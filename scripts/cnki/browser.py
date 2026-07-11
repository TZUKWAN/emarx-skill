"""Human-like browser automation wrapper."""

import random
import time
from contextlib import contextmanager
from pathlib import Path
from typing import Optional

from playwright.sync_api import (
    Browser,
    BrowserContext,
    Page,
    Playwright,
    expect,
    sync_playwright,
)
from playwright_stealth import Stealth

from . import config
from .utils import random_delay

_stealth = Stealth()


STEALTH_SCRIPT = """
// Remove webdriver flag
Object.defineProperty(navigator, 'webdriver', {
    get: () => undefined
});
// Pretend to have plugins
Object.defineProperty(navigator, 'plugins', {
    get: () => [1, 2, 3, 4, 5]
});
// Languages
Object.defineProperty(navigator, 'languages', {
    get: () => ['zh-CN', 'zh', 'en-US', 'en']
});
// Chrome runtime
window.chrome = window.chrome || {};
window.chrome.runtime = window.chrome.runtime || {};
// Hide headless from common detection snippets
window.navigator.__proto__.getUserMedia = window.navigator.__proto__.getUserMedia || function() {};
"""

# Launch flags that make headless Chromium less detectable.
_STEALTH_ARGS = [
    "--disable-blink-features=AutomationControlled",
    "--disable-infobars",
    "--disable-features=IsolateOrigins,site-per-process",
    "--disable-web-security",
    "--disable-dev-shm-usage",
]

# A recent Windows Chrome user-agent; used mainly for headless contexts.
_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
)


class BrowserManager:
    """Manages a Playwright browser/context/page with human-like behavior."""

    def __init__(
        self,
        headless: Optional[bool] = None,
        cdp_url: Optional[str] = None,
        user_data_dir: Optional[str] = None,
        storage_state: Optional[Path] = None,
    ):
        self.headless = headless if headless is not None else config.HEADLESS
        # Keep the global config in sync so downstream helpers (e.g. auth)
        # know whether the current session is headless.
        config.HEADLESS = self.headless
        self.cdp_url = cdp_url or config.REMOTE_DEBUGGING_URL
        self.user_data_dir = user_data_dir or (config.USER_DATA_DIR if config.USER_DATA_DIR else None)
        self.storage_state = storage_state or config.STORAGE_STATE_PATH
        self.playwright: Optional[Playwright] = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None

    def start(self) -> Page:
        self.playwright = sync_playwright().start()

        if config.CDP_CONNECT:
            self.browser = self.playwright.chromium.connect_over_cdp(self.cdp_url)
            contexts = self.browser.contexts
            if contexts:
                self.context = contexts[0]
            else:
                self.context = self.browser.new_context(
                    viewport={"width": 1366, "height": 768},
                    locale="zh-CN",
                    timezone_id="Asia/Shanghai",
                    accept_downloads=True,
                )
            pages = self.context.pages
            self.page = pages[0] if pages else self.context.new_page()
        elif self.user_data_dir:
            # Persistent context reuses real Chrome profile
            self.context = self.playwright.chromium.launch_persistent_context(
                user_data_dir=self.user_data_dir,
                headless=self.headless,
                viewport={"width": 1366, "height": 768},
                locale="zh-CN",
                timezone_id="Asia/Shanghai",
                accept_downloads=True,
                args=_STEALTH_ARGS,
            )
            self.browser = self.context.browser
            pages = self.context.pages
            self.page = pages[0] if pages else self.context.new_page()
        else:
            self.browser = self.playwright.chromium.launch(
                headless=self.headless,
                args=_STEALTH_ARGS,
            )
            context_kwargs = {
                "viewport": {"width": 1366, "height": 768},
                "locale": "zh-CN",
                "timezone_id": "Asia/Shanghai",
                "accept_downloads": True,
                "user_agent": _USER_AGENT,
            }
            if self.storage_state and self.storage_state.exists():
                context_kwargs["storage_state"] = str(self.storage_state)
            self.context = self.browser.new_context(**context_kwargs)
            self.page = self.context.new_page()

        self.page.add_init_script(STEALTH_SCRIPT)
        _stealth.apply_stealth_sync(self.page)
        # Random small delay after page creation
        random_delay(0.5, 1.5)
        return self.page

    def stop(self):
        if self.context and not config.CDP_CONNECT and not self.user_data_dir:
            try:
                self.context.storage_state(path=str(self.storage_state))
            except Exception as exc:
                print(f"[warn] failed to save storage state: {exc}")
        if self.context:
            try:
                self.context.close()
            except Exception:
                pass
        if self.browser:
            try:
                self.browser.close()
            except Exception:
                pass
        if self.playwright:
            try:
                self.playwright.stop()
            except Exception:
                pass

    def save_storage_state(self):
        if self.context and not config.CDP_CONNECT and not self.user_data_dir:
            config.STORAGE_STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
            self.context.storage_state(path=str(config.STORAGE_STATE_PATH))

    def human_scroll(self, amount: Optional[int] = None, steps: int = 5):
        """Scroll in multiple small random steps like a human."""
        if not self.page:
            return
        if amount is None:
            amount = random.randint(200, 600)
        step = amount // steps
        for _ in range(steps):
            self.page.mouse.wheel(0, step)
            random_delay(0.05, 0.2)

    def human_move_to(self, x: int, y: int, duration: float = 0.3):
        """Move mouse with intermediate random points."""
        if not self.page:
            return
        start = self.page.evaluate("() => ({x: window.lastMouseX || 0, y: window.lastMouseY || 0})")
        sx, sy = start.get("x", 0), start.get("y", 0)
        steps = max(10, int(duration * 30))
        for i in range(1, steps + 1):
            t = i / steps
            # Add small random jitter
            jx = random.randint(-5, 5)
            jy = random.randint(-5, 5)
            cx = int(sx + (x - sx) * t) + jx
            cy = int(sy + (y - sy) * t) + jy
            self.page.mouse.move(cx, cy)
            time.sleep(duration / steps)
        self.page.evaluate(f"window.lastMouseX = {x}; window.lastMouseY = {y};")

    def human_click(self, selector: Optional[str] = None, element=None, x: Optional[int] = None, y: Optional[int] = None):
        """Hover, hesitate, then click."""
        if not self.page:
            raise RuntimeError("Browser not started")

        if element is None and selector:
            element = self.page.locator(selector).first

        if element is not None:
            box = element.bounding_box()
            if box:
                x = int(box["x"] + box["width"] / 2) + random.randint(-3, 3)
                y = int(box["y"] + box["height"] / 2) + random.randint(-3, 3)
            element.scroll_into_view_if_needed()
            random_delay(0.2, 0.6)
            element.hover()
            random_delay(0.2, 0.5)
            element.click()
        elif x is not None and y is not None:
            self.human_move_to(x, y)
            random_delay(0.2, 0.5)
            self.page.mouse.click(x, y)
        else:
            raise ValueError("Must provide selector, element, or x/y")

        random_delay(0.3, 0.8)

    def human_type(self, selector: str, text: str, clear: bool = True):
        """Type text character by character with random delays."""
        if not self.page:
            raise RuntimeError("Browser not started")
        locator = self.page.locator(selector).first
        locator.scroll_into_view_if_needed()
        random_delay(0.2, 0.5)
        locator.click()
        if clear:
            locator.fill("")
            random_delay(0.1, 0.3)
        for char in text:
            locator.press(char)
            random_delay(0.05, 0.25)
            if random.random() < 0.05:
                random_delay(0.2, 0.5)
        random_delay(0.3, 0.7)

    def goto(self, url: str, wait_until: str = "networkidle", timeout: int = 30000):
        """Navigate to URL and wait.

        Falls back to ``domcontentloaded`` if the requested wait strategy
        times out, which often happens on CNKI because tracking/ad scripts
        keep the network busy.
        """
        if not self.page:
            raise RuntimeError("Browser not started")
        try:
            self.page.goto(url, wait_until=wait_until, timeout=timeout)
        except Exception as exc:
            if wait_until != "domcontentloaded":
                print(f"[browser] goto networkidle timed out ({type(exc).__name__}), retrying with domcontentloaded")
                self.page.goto(url, wait_until="domcontentloaded", timeout=timeout)
            else:
                raise
        random_delay(1.0, 2.5)

    def wait_for_selector(self, selector: str, timeout: int = 10000, state: str = "visible"):
        return self.page.wait_for_selector(selector, timeout=timeout, state=state)

    def screenshot(self, path: Path):
        if self.page:
            self.page.screenshot(path=str(path))


@contextmanager
def managed_browser(**kwargs):
    """Context manager that saves storage state on exit."""
    bm = BrowserManager(**kwargs)
    try:
        bm.start()
        yield bm
        bm.save_storage_state()
    finally:
        bm.stop()
