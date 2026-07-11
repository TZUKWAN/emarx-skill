"""Authentication and security-check handling."""

import io
import re
from pathlib import Path
from typing import Optional

from PIL import Image
from playwright.sync_api import Page

from . import captcha, config, utils


SECURITY_KEYWORDS = ["安全验证", "验证码", "滑块验证", "人机验证", "security check", "captcha"]


class AuthError(Exception):
    pass


class SecurityCheckError(AuthError):
    pass


def is_security_check(page: Page) -> bool:
    """Detect if current page is a CNKI security verification page.

    We rely on the URL or visible captcha elements, because CNKI may leave
    hidden verification text in the body after a successful solve.
    """
    url = page.url
    if "verify" in url or "starter" in url:
        return True
    try:
        if (
            page.locator(".verify-img-panel img").count() > 0
            or page.locator(".verify-move-block").count() > 0
            or page.locator(".verify-jigsaw").count() > 0
        ):
            return True
    except Exception:
        pass
    return False


def is_logged_in(page: Page) -> bool:
    """Best-effort detection of CNKI login state."""
    indicators = [
        "我的CNKI",
        "退出",
        "个人中心",
        "欢迎",
        "usercenter",
    ]
    text = ""
    try:
        text = page.inner_text("body", timeout=5000)[:2000]
    except Exception:
        pass
    return any(ind in text for ind in indicators)


def _find_captcha_image(page: Page):
    """Heuristic selectors for common captcha images."""
    selectors = [
        "img.captcha",
        "img#captcha",
        ".captcha img",
        ".verify-img",
        ".yidun_bgimg",
        "img[src*='captcha']",
        "img[alt*='验证码']",
    ]
    for sel in selectors:
        loc = page.locator(sel).first
        if loc.count() > 0 and loc.is_visible():
            return loc
    return None


def _find_captcha_input(page: Page):
    selectors = [
        "input#captcha",
        "input.captcha",
        "input[name*='captcha']",
        "input[placeholder*='验证码']",
    ]
    for sel in selectors:
        loc = page.locator(sel).first
        if loc.count() > 0 and loc.is_visible():
            return loc
    return None


def _find_slider_elements(page: Page):
    """Try to locate slider handle and background."""
    handle_selectors = [
        ".slider",
        ".yidun_slider",
        ".verify-move-block",
        ".nc_iconfont",
    ]
    bg_selectors = [
        ".yidun_bgimg",
        ".verify-img",
        ".slider-bg",
    ]
    handle = None
    bg = None
    for sel in handle_selectors:
        loc = page.locator(sel).first
        if loc.count() > 0 and loc.is_visible():
            handle = loc
            break
    for sel in bg_selectors:
        loc = page.locator(sel).first
        if loc.count() > 0 and loc.is_visible():
            bg = loc
            break
    return handle, bg


def _is_block_puzzle(page: Page) -> bool:
    """Detect CNKI block-puzzle captcha page/element."""
    if "blockPuzzle" in page.url:
        return True
    try:
        if (
            page.locator(".verify-img-panel img").count() > 0
            and page.locator(".verify-sub-block img").count() > 0
        ):
            return True
    except Exception:
        pass
    return False


def _is_click_word(page: Page) -> bool:
    """Detect CNKI click-word captcha page/element."""
    if "clickWord" in page.url:
        return True
    try:
        if (
            page.locator(".verify-img-panel img").count() > 0
            and page.locator(".verify-click-word").count() > 0
        ):
            return True
    except Exception:
        pass
    return False


def _handle_block_puzzle(page: Page, max_retries: int = 2):
    """Solve CNKI block-puzzle captcha by image matching and Vue component control."""
    for attempt in range(1, max_retries + 1):
        try:
            page.wait_for_selector(".verify-img-panel img", timeout=10000)
            page.wait_for_selector(".verify-sub-block img", timeout=10000)

            data = page.evaluate(
                """() => {
                    const panel = document.querySelector('.verify-img-panel img');
                    const sub = document.querySelector('.verify-sub-block img');
                    const move = document.querySelector('.verify-move-block');
                    let vue = null, el = move;
                    while (el) {
                        if (el.__vue__) { vue = el.__vue__; break; }
                        el = el.parentElement;
                    }
                    return {
                        original: panel ? panel.src : null,
                        jigsaw: sub ? sub.src : null,
                        secretKey: vue ? vue.secretKey : null,
                        backToken: vue ? vue.backToken : null,
                        ident: vue ? vue.ident : null,
                        returnUrl: vue ? vue.returnUrl : null,
                        imgWidth: vue && vue.setSize ? parseInt(vue.setSize.imgWidth) : 310,
                        passFlag: vue ? vue.passFlag : null,
                    };
                }"""
            )

            if not data.get("original") or not data.get("jigsaw"):
                raise RuntimeError("Could not locate block-puzzle images")

            original_b64 = (
                data["original"].split(",", 1)[1]
                if "," in data["original"]
                else data["original"]
            )
            jigsaw_b64 = (
                data["jigsaw"].split(",", 1)[1]
                if "," in data["jigsaw"]
                else data["jigsaw"]
            )

            target_x = captcha.solve_block_puzzle(original_b64, jigsaw_b64)

            # We skip visual mouse dragging here because CNKI's Vue captcha
            # resets the token on stray mouse events. We set the slider state
            # directly and invoke the component's end() to submit.
            with page.expect_response("**/verify-api/web/check") as response_info:
                page.evaluate(
                    """(target_x) => {
                        const move = document.querySelector('.verify-move-block');
                        let vue = null, el = move;
                        while (el) {
                            if (el.__vue__) { vue = el.__vue__; break; }
                            el = el.parentElement;
                        }
                        if (!vue) throw new Error('Vue captcha component not found');
                        const left = Math.round(target_x) + 'px';
                        vue.moveBlockLeft = left;
                        vue.leftBarWidth = left;
                        vue.status = true;
                        vue.isEnd = false;
                        const now = +new Date;
                        vue.startMoveTime = now - 600;
                        vue.endMovetime = now;
                        vue.end();
                    }""",
                    target_x,
                )
                resp = response_info.value
            check_data = resp.json()
            print('[block-puzzle] check_data', check_data)
            if not check_data.get("data", {}).get("result"):
                raise RuntimeError(f"Verification rejected: {check_data}")

            # CNKI's Vue captcha schedules an automatic redirect to the
            # original URL after a successful verification. Wait for that
            # navigation instead of forcing one, because a forced goto will
            # abort the in-flight redirect and lose the verification token.
            try:
                page.wait_for_url(lambda url: "verify" not in url, timeout=20000)
                print('[block-puzzle] auto-redirected to', page.url)
            except Exception as exc:
                print('[block-puzzle] no auto-redirect observed', type(exc).__name__, exc)
            return

        except Exception as exc:
            print('[block-puzzle] attempt', attempt, 'error', type(exc).__name__, exc)
            if attempt >= max_retries:
                raise SecurityCheckError(
                    f"Failed to solve block-puzzle captcha after {max_retries} attempts: {exc}"
                )
            utils.random_delay(1.0, 2.0)
            try:
                page.evaluate(
                    """() => {
                        const move = document.querySelector('.verify-move-block');
                        let vue = null, el = move;
                        while (el) {
                            if (el.__vue__) { vue = el.__vue__; break; }
                            el = el.parentElement;
                        }
                        if (vue && typeof vue.refresh === 'function') vue.refresh();
                    }"""
                )
                utils.random_delay(1.5, 2.5)
            except Exception:
                pass

    raise SecurityCheckError("Failed to solve block-puzzle captcha")


def _wait_for_manual_click_word(page: Page, timeout: float = 120.0):
    """Pause and wait for a user to complete a click-word captcha manually.

    This is used when headless is disabled and CNKI serves a verification type
    that the project cannot solve automatically yet.
    """
    print(f"[click-word] 检测到文字点击验证码，请在浏览器窗口中按提示点击文字。最长等待 {int(timeout)} 秒...")
    import time as _time

    start = _time.time()
    while _time.time() - start < timeout:
        _time.sleep(2.0)
        if not is_security_check(page):
            print("[click-word] 验证码已通过，继续执行。")
            return
        remaining = int(timeout - (_time.time() - start))
        print(f"[click-word] 仍在等待... 剩余 {remaining} 秒")
    raise SecurityCheckError("click-word 验证码手动处理超时。")


def handle_security_check(page: Page, max_retries: int = 2):
    """Attempt to pass a CNKI security check automatically.

    Raises SecurityCheckError if it cannot be solved automatically.
    """
    if not is_security_check(page):
        return

    solver = captcha.create_solver(config.CAPTCHA_SOLVER, config.TWOCAPTCHA_API_KEY)
    debug_dir = Path("logs/captcha")
    debug_dir.mkdir(parents=True, exist_ok=True)

    for attempt in range(1, max_retries + 1):
        # Always screenshot for debugging
        shot_path = debug_dir / f"security_{attempt}.png"
        page.screenshot(path=str(shot_path))

        # CNKI block-puzzle captcha
        if _is_block_puzzle(page):
            try:
                _handle_block_puzzle(page, max_retries=1)
            except SecurityCheckError:
                if attempt >= max_retries:
                    raise
                utils.random_delay(1.5, 2.5)
                continue
            if not is_security_check(page):
                return
            continue

        # Try image captcha
        img_loc = _find_captcha_image(page)
        input_loc = _find_captcha_input(page)
        if img_loc and input_loc:
            img = Image.open(io.BytesIO(img_loc.screenshot()))
            code = solver.solve_image(img)
            utils.random_delay(0.5, 1.5)
            input_loc.fill(code)
            utils.random_delay(0.3, 0.8)
            # Try pressing Enter or clicking submit
            input_loc.press("Enter")
            page.wait_for_timeout(2000)
            if not is_security_check(page):
                return
            continue

        # Try slider captcha
        handle, bg = _find_slider_elements(page)
        if handle and bg:
            bg_img = Image.open(io.BytesIO(bg.screenshot()))
            handle_img = Image.open(io.BytesIO(handle.screenshot()))
            captcha.save_captcha_debug(bg_img, handle_img, debug_dir / f"slider_{attempt}.png")
            offset = solver.solve_slider(bg_img, handle_img)
            captcha.human_like_drag(page, handle, offset)
            page.wait_for_timeout(2500)
            if not is_security_check(page):
                return
            continue

        # CNKI click-word captcha: cannot be solved automatically yet.
        if _is_click_word(page):
            if config.HEADLESS:
                raise SecurityCheckError(
                    f"CNKI click-word captcha detected at {page.url}. "
                    "Automatic solving is not supported. Run with --no-headless "
                    "or connect to an already-logged-in Chrome via CDP to continue."
                )
            _wait_for_manual_click_word(page, timeout=120.0)
            if not is_security_check(page):
                return
            continue

        # Unknown verification type
        raise SecurityCheckError(
            f"Unknown security check at {page.url}. Screenshot saved to {shot_path}. "
            "Automatic solving is not supported for this verification type."
        )

    raise SecurityCheckError(f"Failed to pass security check after {max_retries} attempts.")


def ensure_session(page: Page, login_url: Optional[str] = None):
    """If not logged in, navigate to login page and let user complete login manually.

    This function does NOT automate credentials because we should not handle passwords.
    """
    if is_logged_in(page):
        return
    # For CDP / persistent context we expect the user to already be logged in.
    if config.CDP_CONNECT or config.USER_DATA_DIR:
        raise AuthError(
            "Not logged into CNKI in the connected Chrome. "
            "Please log in manually in that Chrome window first."
        )
    # Otherwise we could open the login page. We leave it to the caller/cli to handle.
    raise AuthError("CNKI login required. Use 'login' command or connect to an already logged-in Chrome.")
