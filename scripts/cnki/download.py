"""CNKI article download helpers."""

import re
import uuid
from pathlib import Path
from typing import Dict, Optional, Union
from urllib.parse import urljoin

from playwright.sync_api import Page, TimeoutError as PlaywrightTimeoutError

from . import auth, config, utils


def _ensure_abs(base: str, href: str) -> str:
    if not href:
        return ""
    if href.startswith("http"):
        return href
    return urljoin(base, href)


def _extract_title(page: Page) -> str:
    title = page.title()
    # CNKI detail title often like "题名-..."
    title = re.split(r"[-_—]", title)[0].strip()
    return title


def extract_download_links(
    page: Page,
    detail_url: str,
    timeout: int = 60000,
) -> Dict[str, str]:
    """Open a CNKI detail page and extract PDF/CAJ download URLs.

    Returns a dict with ``pdf_url``, ``caj_url`` and ``title``.
    """
    try:
        page.goto(detail_url, wait_until="networkidle", timeout=timeout)
    except PlaywrightTimeoutError:
        page.goto(detail_url, wait_until="domcontentloaded", timeout=timeout)

    utils.random_delay(1.0, 2.5)

    if auth.is_security_check(page):
        auth.handle_security_check(page)

    # Wait for the download anchors to appear.
    page.wait_for_selector("#pdfDown, #cajDown", state="visible", timeout=15000)

    pdf_href = ""
    caj_href = ""
    try:
        pdf_el = page.locator("#pdfDown").first
        if pdf_el.count():
            pdf_href = pdf_el.get_attribute("href") or ""
    except Exception:
        pass
    try:
        caj_el = page.locator("#cajDown").first
        if caj_el.count():
            caj_href = caj_el.get_attribute("href") or ""
    except Exception:
        pass

    return {
        "title": _extract_title(page),
        "pdf_url": _ensure_abs(config.CNKI_KNS, pdf_href),
        "caj_url": _ensure_abs(config.CNKI_KNS, caj_href),
        "detail_url": detail_url,
    }


def download_item(
    page: Page,
    item_or_detail_url: Union[Dict[str, str], str],
    output_dir: Optional[Path] = None,
    prefer: str = "pdf",
    timeout: int = 120000,
) -> Path:
    """Download a single article from its detail page or direct order URL.

    ``item_or_detail_url`` can be a result dict containing ``detail_url`` or a
    direct ``bar.cnki.net`` order URL. ``prefer`` chooses between ``pdf`` and
    ``caj`` when a detail dict is supplied.

    Note: CNKI order URLs require the correct referer/session context. For
    result dicts we therefore click the real detail-page anchor instead of
    navigating to the bare ``bar.cnki.net`` URL.
    """
    output_dir = Path(output_dir or config.DOWNLOAD_DIR)
    output_dir.mkdir(parents=True, exist_ok=True)

    if isinstance(item_or_detail_url, dict):
        links = extract_download_links(page, item_or_detail_url["detail_url"])
        selector = "#pdfDown" if prefer == "pdf" and links.get("pdf_url") else "#cajDown"
    else:
        # Bare order URL: navigate directly. This may fail if referer is
        # missing, but we keep the option available for pre-signed URLs.
        selector = None
        url = item_or_detail_url

    if selector:
        # Remove target="_blank" so the download fires in the same page context
        # and Playwright can capture it.
        page.evaluate(f"""() => {{
            document.querySelectorAll('{selector}').forEach(a => a.removeAttribute('target'));
        }}""")
        anchor = page.locator(f"{selector}:visible").first
        anchor.scroll_into_view_if_needed()
        utils.random_delay(0.5, 1.2)
        with page.expect_download(timeout=timeout) as download_info:
            anchor.click()
        download = download_info.value
    else:
        with page.expect_download(timeout=timeout) as download_info:
            page.goto(url, wait_until="domcontentloaded", timeout=timeout)
        download = download_info.value

    suggested = download.suggested_filename
    if not suggested:
        ext = ".pdf" if (selector == "#pdfDown") else ".caj"
        suggested = f"cnki_{uuid.uuid4().hex[:8]}{ext}"
    dest = output_dir / suggested
    download.save_as(dest)
    return dest


def download_from_result(
    page: Page,
    result: Dict[str, str],
    output_dir: Optional[Path] = None,
    prefer: str = "pdf",
    timeout: int = 120000,
) -> Path:
    """Convenience wrapper to download from a search result dict."""
    return download_item(page, result, output_dir=output_dir, prefer=prefer, timeout=timeout)
