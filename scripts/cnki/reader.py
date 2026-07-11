"""CNKI article detail page reader.

Extracts metadata (title, authors, source, year, issue, pages, DOI) and the
article abstract from a CNKI detail page.  This module no longer opens the
HTML reader popup or extracts full-text body content, because CNKI's HTML
reader serves a slider captcha in automated contexts and many articles do not
provide an HTML reader entry at all.
"""

import re
from typing import Dict, List, Optional

from playwright.sync_api import Page, TimeoutError as PlaywrightTimeoutError

from . import auth, config, utils


def _collapse(text: Optional[str]) -> str:
    if not text:
        return ""
    return re.sub(r"\s+", " ", text).strip()


def _normalize_article_text(raw: Optional[str]) -> str:
    """Preserve paragraph breaks while collapsing intra-line whitespace."""
    if not raw:
        return ""
    lines = [re.sub(r"\s+", " ", line).strip() for line in raw.splitlines()]
    cleaned = []
    last_empty = False
    for line in lines:
        if not line:
            if not last_empty:
                cleaned.append("")
            last_empty = True
        else:
            cleaned.append(line)
            last_empty = False
    return "\n".join(cleaned).strip()


def _extract_title(page: Page) -> str:
    """Return the first non-empty title candidate found on the page."""
    selectors = ["h1", ".wx_title", ".doc-title", ".brief"]
    for sel in selectors:
        try:
            el = page.locator(sel).first
            if el.count():
                text = _collapse(el.inner_text())
                if text:
                    return text
        except Exception:
            continue
    # Fallback to the browser document title, stripped of common CNKI suffixes.
    try:
        title = _collapse(page.title())
        title = re.sub(r"-?\s*中国知网\s*$", "", title)
        title = re.sub(r"-?\s*CNKI\s*$", "", title)
        return title.strip("- ")
    except Exception:
        return ""


def _extract_authors(page: Page) -> List[str]:
    """Return author names as a list.

    Prefer individual author links inside ``.author``; otherwise fall back
    to splitting the element text on common delimiters.
    """
    try:
        links = page.locator(".author a").all()
        names = []
        for a in links:
            try:
                href = (a.get_attribute("href") or "").lower()
                # Skip affiliation/organisation links.
                if "/organ/" in href:
                    continue
                text = _collapse(a.inner_text())
                if text:
                    names.append(text)
            except Exception:
                continue
        if names:
            return names
    except Exception:
        pass

    raw = ""
    try:
        el = page.locator(".author").first
        if el.count():
            raw = _collapse(el.inner_text())
    except Exception:
        raw = ""
    if not raw:
        return []
    parts = re.split(r"[;；,，\s]+", raw)
    return [p.strip() for p in parts if p.strip()]


def _extract_pub_info(page: Page) -> Dict[str, str]:
    """Parse source/year/issue/pages from the detail page header."""
    text = ""
    for sel in (".doc-top", ".top-tip"):
        try:
            el = page.locator(sel).first
            if el.count():
                text = _collapse(el.inner_text())
                if text:
                    break
        except Exception:
            continue

    info = {"source": "", "year": "", "issue": "", "pages": ""}
    if not text:
        return info

    patterns = [
        r"(?P<source>.+?)\s*\.\s*(?P<year>\d{4})\s*\((?P<issue>[^)]+)\)\s*[:：]\s*(?P<pages>[\d\-–—]+)",
        r"(?P<source>.+?)\s*,\s*(?P<year>\d{4})\s*\((?P<issue>[^)]+)\)\s*[:：]\s*(?P<pages>[\d\-–—]+)",
        r"(?P<source>.+?)\s+(?P<year>\d{4})\s*年\s*(?P<issue>\d+)\s*期\s*[:：]?\s*(?P<pages>[\d\-–—]+)",
    ]
    for pat in patterns:
        m = re.search(pat, text)
        if m:
            info.update({k: _collapse(v) for k, v in m.groupdict().items()})
            break
    return info


def _extract_doi(page: Page) -> Optional[str]:
    """Best-effort DOI extraction from page text."""
    try:
        text = page.inner_text("body", timeout=5000)
    except Exception:
        text = ""
    if not text:
        return None
    m = re.search(r"\b(10\.\d{4,9}/[-._;()/:\w]+)\b", text)
    return m.group(1) if m else None


def _extract_abstract(page: Page) -> str:
    """Extract the article abstract from the detail page.

    CNKI uses several selectors across different layouts; try them in order
    and return the first non-empty result.
    """
    selectors = [
        ".abstract-text",
        "#ChDivSummary",
        "#abstract_text",
        ".abstract",
    ]
    for sel in selectors:
        try:
            loc = page.locator(sel).first
            if loc.count() > 0:
                text = _normalize_article_text(loc.inner_text())
                if text:
                    return text
        except Exception:
            continue
    return ""


_LOGIN_TITLES = {"自动登录", "登录", "login", "Login"}


def _looks_like_login(item: Dict[str, str]) -> bool:
    """Return True when the detail page redirected to a login/transfer page."""
    title = item.get("title", "")
    if title in _LOGIN_TITLES or title.startswith("自动登录"):
        return True
    return not item.get("source") and not item.get("year") and not item.get("pages")


def _open_detail_via_home_search(page: Page, title: str) -> Page:
    """Fall back to homepage search when a direct detail URL hits clickWord.

    CNKI is less likely to serve the ``clickWord`` verification when the user
    enters through the homepage search box.  This function searches for the
    article title and clicks the matching result, returning the newly opened
    detail page.
    """
    from . import search as search_module

    search_module._search_from_homepage(page, title)

    links = page.locator(".result-table-list tbody tr td.name a").all()
    for link in links:
        try:
            link_title = (link.inner_text() or "").strip()
            if not link_title:
                continue
            if title in link_title or link_title in title:
                with page.context.expect_event("page", timeout=15000) as new_page_info:
                    link.click()
                detail_page = new_page_info.value
                detail_page.wait_for_load_state("domcontentloaded", timeout=30000)
                return detail_page
        except Exception:
            continue
    raise RuntimeError(f"Could not find '{title}' via homepage search")


def read_article(
    page: Page,
    detail_url: str,
    expected_title: str = "",
    expected_source: str = "",
    expected_year: str = "",
) -> Dict:
    """Open a CNKI detail page and extract metadata plus the article abstract.

    Args:
        page: The active Playwright page (the detail page will be loaded here).
        detail_url: URL of the CNKI article detail page.
        expected_title: Optional title from the search result, used as a fallback
            when the detail page redirects to a login/transfer page.
        expected_source: Optional journal name from the search result.
        expected_year: Optional publication year from the search result.

    Returns:
        A dict with title, authors, source, year, issue, pages, doi (optional),
        url, and the article abstract in ``text``.
    """
    # CNKI is very sensitive to direct detail-page URLs, especially in headless
    # or automated contexts, and often serves a clickWord verification.  When we
    # know the article title we use the lower-machine-signal homepage-search
    # path first, then click the matching result.
    if expected_title:
        try:
            page = _open_detail_via_home_search(page, expected_title)
        except Exception as exc:
            print(f"[reader] homepage search path failed: {exc}; falling back to direct URL")
            page.goto(detail_url, wait_until="domcontentloaded", timeout=60000)
            if auth.is_security_check(page):
                auth.handle_security_check(page)
    else:
        page.goto(detail_url, wait_until="domcontentloaded", timeout=60000)
        if auth.is_security_check(page):
            auth.handle_security_check(page)

    try:
        page.wait_for_selector(".brief, .doc, h1", state="visible", timeout=15000)
    except PlaywrightTimeoutError:
        pass

    title = _extract_title(page)
    authors = _extract_authors(page)
    pub_info = _extract_pub_info(page)
    doi = _extract_doi(page)
    abstract = _extract_abstract(page)

    warnings: List[str] = []

    # If the detail page metadata is missing because CNKI asked for login,
    # recover what we can from the expected search result values.
    if _looks_like_login(
        {
            "title": title,
            "source": pub_info.get("source"),
            "year": pub_info.get("year"),
            "pages": pub_info.get("pages"),
        }
    ):
        title = expected_title or title
        if expected_source and not pub_info.get("source"):
            pub_info["source"] = expected_source
        if expected_year and not pub_info.get("year"):
            pub_info["year"] = expected_year

    if not abstract:
        warnings.append("Could not extract article abstract from the detail page.")

    utils.random_delay(0.5, 1.0)

    result = {
        "title": title,
        "authors": authors,
        "source": pub_info.get("source", ""),
        "year": pub_info.get("year", ""),
        "issue": pub_info.get("issue", ""),
        "pages": pub_info.get("pages", ""),
        "url": detail_url,
        "text": abstract,
        "text_type": "abstract",
    }
    if doi:
        result["doi"] = doi
    if warnings:
        result["warnings"] = warnings
    return result
