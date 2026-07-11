"""CNKI search and result parsing."""

import json
import re
from pathlib import Path
from typing import Dict, List, Optional
from urllib.parse import quote

from bs4 import BeautifulSoup
from playwright.sync_api import Page, TimeoutError as PlaywrightTimeoutError

from . import auth, config, utils


def _extract_text(node, default: str = "") -> str:
    if node is None:
        return default
    return re.sub(r"\s+", " ", node.get_text(strip=True))


def _safe_href(node) -> str:
    if node is None:
        return ""
    href = node.get("href", "")
    if href.startswith("http"):
        return href
    return config.CNKI_KNS + href if href else ""


def _parse_result_row(row_html: str) -> Optional[Dict]:
    """Parse a single result row from CNKI result table HTML."""
    soup = BeautifulSoup(row_html, "lxml")
    cells = soup.find_all("td")
    if len(cells) < 6:
        return None

    # Cell indices by observed CNKI classes:
    # 0 seq, 1 name (title), 2 author, 3 source, 4 date, 5 data (db),
    # 6 quote (citations), 7 download (downloads), 8 operat (actions)
    name_cell = soup.select_one("td.name")
    title_node = (
        soup.select_one("td.name a.fz14")
        or soup.select_one("td.name a")
    )
    if not title_node:
        return None

    title = _extract_text(title_node)
    detail_url = _safe_href(title_node)

    author_cell = soup.select_one("td.author")
    if author_cell:
        author_links = author_cell.find_all("a")
        authors = ", ".join(
            a.get_text(strip=True) for a in author_links if a.get_text(strip=True)
        )
    else:
        authors = ""

    source_cell = soup.select_one("td.source")
    source_node = source_cell.select_one("a") if source_cell else None
    source = _extract_text(source_node or source_cell)

    date_cell = soup.select_one("td.date")
    date = _extract_text(date_cell)

    db_cell = soup.select_one("td.data")
    db = _extract_text(db_cell)

    quote_cell = soup.select_one("td.quote")
    quote_text = _extract_text(quote_cell)
    citations = None
    if quote_text and quote_text.isdigit():
        citations = int(quote_text)

    download_cell = soup.select_one("td.download")
    download_count = None
    download_text = _extract_text(download_cell)
    if download_text and download_text.isdigit():
        download_count = int(download_text)

    operat_cell = soup.select_one("td.operat")
    download_node = (
        operat_cell.select_one("a.downloadlink") if operat_cell else None
    )
    download_url = _safe_href(download_node)

    # Checkbox value can be used later for batch operations.
    seq_cell = soup.select_one("td.seq")
    checkbox = seq_cell.select_one("input.cbItem") if seq_cell else None
    file_value = checkbox.get("value", "") if checkbox else ""

    return {
        "title": title,
        "authors": authors,
        "source": source,
        "date": date,
        "year": date.split("-")[0] if date and "-" in date else date,
        "database": db,
        "citations": citations,
        "downloads": download_count,
        "detail_url": detail_url,
        "download_url": download_url,
        "file_value": file_value,
    }


def _get_result_rows(page: Page) -> List[Dict]:
    """Parse rows from the CNKI result table."""
    # Wait until the table has body rows.
    try:
        page.wait_for_selector(".result-table-list tbody tr", timeout=15000)
    except PlaywrightTimeoutError:
        return []

    rows = page.locator(".result-table-list tbody tr").all()
    results = []
    for row in rows:
        try:
            html = row.inner_html()
            item = _parse_result_row(html)
            if item and item.get("title"):
                results.append(item)
        except Exception:
            continue
    return results


def _current_page_number(page: Page) -> int:
    """Extract current page number from active pagination link."""
    try:
        cur = page.locator("#briefBox .countPageMark").first
        if cur.count():
            text = cur.inner_text()
            match = re.search(r"(\d+)\s*/", text)
            if match:
                return int(match.group(1))
    except Exception:
        pass
    return 0


def apply_source_filters(page: Page, core: bool = True, cssci: bool = True) -> None:
    """Apply 北大核心 / CSSCI source filters on CNKI result page.

    Uses ``page.evaluate`` to tick the source-type checkboxes in the
    ``LYBSM`` group and trigger CNKI's ``mutiSelectedGroup`` handler,
    then waits up to 5 seconds for the result count to refresh.
    """
    if not core and not cssci:
        return

    # Capture current pager text so we can wait for the refresh to finish.
    original_total = ""
    try:
        title_cell = page.locator(".pagerTitleCell").first
        if title_cell.count():
            original_total = title_cell.inner_text()
    except Exception:
        pass

    js = f"""
    () => {{
        const dl = document.querySelector("#divGroup dl[groupid='LYBSM']");
        if (!dl) return false;
        let changed = false;
        dl.querySelectorAll("input[type='checkbox']").forEach(cb => {{
            const val = cb.value;
            if (({str(core).lower()} && val === "P01") ||
                ({str(cssci).lower()} && val === "P0209")) {{
                cb.checked = true;
                if (typeof mutiSelectedGroup === "function") {{
                    mutiSelectedGroup(cb);
                }} else if (window.mutiSelectedGroup &&
                           typeof window.mutiSelectedGroup === "function") {{
                    window.mutiSelectedGroup(cb);
                }}
                changed = true;
            }}
        }});
        return changed;
    }}
    """
    try:
        changed = page.evaluate(js)
        if changed:
            if original_total:
                page.wait_for_function(
                    "() => { const el = document.querySelector('.pagerTitleCell'); "
                    "return el && el.innerText !== " + json.dumps(original_total) + "; }",
                    timeout=5000,
                )
            else:
                page.wait_for_selector(".result-table-list tbody tr", timeout=5000)
    except Exception as exc:
        print(f"[search] apply source filters failed: {exc}")


def _search_from_homepage(page: Page, keyword: str) -> None:
    """Enter CNKI through the homepage search box like a real user.

    This lowers machine-like signals compared to opening the one-box search
    URL directly.  The function raises RuntimeError if the homepage search
    box or button cannot be located.
    """
    page.goto(config.CNKI_HOME, wait_until="domcontentloaded", timeout=60000)
    utils.random_delay(2.0, 4.0)

    input_selectors = [
        "textarea#txt_SearchText",
        "textarea.search-input",
        "#txt_SearchText",
        ".search-input",
        "[placeholder*='中文文献']",
        "[placeholder*='请输入']",
    ]
    input_el = None
    for sel in input_selectors:
        try:
            loc = page.locator(sel).first
            if loc.count() > 0 and loc.is_visible():
                input_el = loc
                break
        except Exception:
            continue
    if input_el is None:
        raise RuntimeError("CNKI homepage search input not found")

    input_el.click()
    utils.random_delay(0.3, 0.8)
    input_el.fill(keyword)
    utils.random_delay(0.8, 1.5)

    btn_selectors = ["input.search-btn", ".search-btn", "#searchBtn"]
    btn = None
    for sel in btn_selectors:
        try:
            loc = page.locator(sel).first
            if loc.count() > 0 and loc.is_visible():
                btn = loc
                break
        except Exception:
            continue
    if btn is None:
        raise RuntimeError("CNKI homepage search button not found")

    btn.click()
    page.wait_for_selector(".result-table-list tbody tr", timeout=30000)
    utils.random_delay(2.0, 3.0)


def _search_from_url(page: Page, keyword: str) -> None:
    """Open the one-box search URL directly as a fallback."""
    url = f"{config.CNKI_SEARCH_URL}?kw={quote(keyword)}"
    try:
        page.goto(url, wait_until="networkidle", timeout=60000)
    except PlaywrightTimeoutError:
        page.goto(url, wait_until="domcontentloaded", timeout=60000)
    utils.random_delay(1.5, 3.0)


def search(
    page: Page,
    keyword: str,
    max_pages: int = None,
    max_results: int = None,
) -> List[Dict]:
    """Search CNKI and collect result items across pages.

    Uses ``domcontentloaded`` to avoid network-idle hangs on CNKI's
    tracking/ad scripts, then waits explicitly for the result table.
    """
    if max_pages is None:
        max_pages = config.MAX_PAGES
    if max_results is None:
        max_results = max_pages * config.RESULTS_PER_PAGE

    # Prefer the human-like homepage path; fall back to the direct search URL.
    try:
        _search_from_homepage(page, keyword)
    except Exception as exc:
        print(f"[search] homepage search failed ({exc}), falling back to direct URL")
        _search_from_url(page, keyword)

    if auth.is_security_check(page):
        auth.handle_security_check(page)

    # Ensure the result table is present before applying filters / parsing.
    try:
        page.wait_for_selector(".result-table-list tbody tr", timeout=15000)
    except PlaywrightTimeoutError:
        return []

    apply_source_filters(page, config.CNKI_FILTER_CORE, config.CNKI_FILTER_CSSCI)

    all_results: List[Dict] = []
    for _ in range(max_pages):
        results = _get_result_rows(page)
        if not results:
            break
        all_results.extend(results)

        if len(all_results) >= max_results:
            all_results = all_results[:max_results]
            break

        # Attempt to click the CNKI "next page" button.
        next_loc = page.locator("#PageNext").first
        if next_loc.count() == 0 or not next_loc.is_visible():
            break

        before = _current_page_number(page)
        try:
            next_loc.scroll_into_view_if_needed()
            utils.random_delay(0.5, 1.2)
            next_loc.click()
            # Wait for the page number to change or at least a short settle.
            page.wait_for_function(
                f"() => {{ const m = document.querySelector('.countPageMark'); "
                f"return m && !m.innerText.includes('{before}/'); }}",
                timeout=15000,
            )
        except Exception:
            # If pagination did not advance, stop.
            break

        utils.random_delay(2.0, 4.0)
        if auth.is_security_check(page):
            auth.handle_security_check(page)

    return all_results


def save_results(results: List[Dict], path: Path):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)


def load_results(path: Path) -> List[Dict]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)
