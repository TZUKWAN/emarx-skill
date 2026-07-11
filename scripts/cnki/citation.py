"""GB/T 7714-2015 citation formatter."""

from __future__ import annotations

import re


def parse_authors(text: str) -> list[str]:
    """Parse author names separated by Chinese/English commas, semicolons or spaces.

    Empty segments are removed and each name is stripped of surrounding whitespace.
    """
    if not text or not text.strip():
        return []
    # Split on common separators: Chinese comma, English comma,
    # Chinese semicolon, English semicolon, whitespace
    parts = re.split(r"[，,；;\s]+", text.strip())
    return [name.strip() for name in parts if name.strip()]


def _format_authors(authors: list[str], is_english: bool) -> str:
    """Format author list according to GB/T 7714-2015.

    For English lists ending in ``et al.`` no extra period is inserted before
    the title; for Chinese lists a period separates authors from title.
    """
    if not authors:
        return ""

    if len(authors) > 3:
        display = authors[:3]
        suffix = "et al." if is_english else "等"
        separator = " " if is_english else ". "
        return ", ".join(display) + ", " + suffix + separator

    return ", ".join(authors) + ". "


def format_gb7714(item: dict) -> str:
    """Format a journal article citation in GB/T 7714-2015 style.

    Expected ``item`` fields:
        - title
        - authors (list of str)
        - source (journal name)
        - year
        - issue
        - pages
        - doi (optional)
        - is_english (optional bool)
    """
    title = item.get("title", "")
    authors = item.get("authors", [])
    source = item.get("source", "")
    year = item.get("year", "")
    issue = item.get("issue", "")
    pages = item.get("pages", "")
    doi = item.get("doi")
    is_english = bool(item.get("is_english", False))

    # Normalize issue: remove leading zeros while keeping "0" as "0"
    if isinstance(issue, str) and issue.strip():
        issue = issue.lstrip("0")
        if issue == "":
            issue = "0"
    elif isinstance(issue, int):
        issue = str(int(issue))
    else:
        issue = ""

    author_str = _format_authors(authors, is_english)

    parts: list[str] = []
    if source:
        parts.append(f"{source}")
    if year:
        if issue:
            parts.append(f"{year}({issue})")
        else:
            parts.append(f"{year}")
    journal_part = ", ".join(parts)

    citation = f"{author_str}{title}[J]."
    if journal_part:
        citation += f" {journal_part}"
    if pages:
        citation += f": {pages}"
    citation += "."

    if doi:
        citation += f" DOI: {doi}"

    return citation
