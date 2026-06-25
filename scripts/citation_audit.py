#!/usr/bin/env python
"""Audit EMARX numeric citations in a Markdown paper.

The script checks mechanical rules only: citation sequence, duplicate citation
numbers, reference-list order, repeated authors, and paragraph-end citation
clusters. It cannot verify whether a source truly supports a sentence.
"""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter, defaultdict
from pathlib import Path


CITE_RE = re.compile(r"(?<!!)\[(\d+)\]")
REF_RE = re.compile(r"^\s*\[(\d+)\]\s*(.+?)\s*$")


def split_body_refs(text: str) -> tuple[str, str]:
    marker = re.search(r"(?m)^#{1,6}\s*参考文献\s*$|^参考文献\s*$", text)
    if not marker:
        return text, ""
    return text[: marker.start()], text[marker.end() :]


def extract_reference_lines(refs: str) -> list[tuple[int, str]]:
    lines: list[tuple[int, str]] = []
    for line in refs.splitlines():
        match = REF_RE.match(line)
        if match:
            lines.append((int(match.group(1)), match.group(2).strip()))
    return lines


def author_names(ref_text: str) -> list[str]:
    author_part = re.split(r"[.．]", ref_text, maxsplit=1)[0].strip()
    author_part = re.sub(r"\s*(等|et al)\.?\s*$", "", author_part, flags=re.I)
    parts = re.split(r"[,，、;；]\s*", author_part)
    return [p.strip() for p in parts if p.strip()]


def paragraph_end_clusters(body: str) -> list[str]:
    issues: list[str] = []
    for para in re.split(r"\n\s*\n", body):
        stripped = para.strip()
        if not stripped:
            continue
        if re.search(r"(?:\[\d+\]){2,}\s*$", stripped):
            issues.append(stripped[-160:])
    return issues


def audit(text: str, expected_count: int | None = None) -> dict:
    body, refs = split_body_refs(text)
    cites = [int(n) for n in CITE_RE.findall(body)]
    counts = Counter(cites)
    first_order: list[int] = []
    for n in cites:
        if n not in first_order:
            first_order.append(n)

    reference_lines = extract_reference_lines(refs)
    reference_numbers = [n for n, _ in reference_lines]

    repeated_authors: dict[str, list[int]] = defaultdict(list)
    for number, ref_text in reference_lines:
        for name in author_names(ref_text):
            repeated_authors[name].append(number)

    duplicate_authors = {
        name: nums for name, nums in repeated_authors.items() if len(nums) > 1
    }

    expected_sequence = list(range(1, len(first_order) + 1))
    result = {
        "inline_citation_count": len(cites),
        "unique_inline_citations": first_order,
        "duplicate_citation_numbers": {str(k): v for k, v in counts.items() if v > 1},
        "first_use_sequence_ok": first_order == expected_sequence,
        "expected_first_use_sequence": expected_sequence,
        "reference_numbers": reference_numbers,
        "reference_order_ok": reference_numbers == first_order,
        "missing_reference_entries": [n for n in first_order if n not in reference_numbers],
        "uncited_reference_entries": [n for n in reference_numbers if n not in first_order],
        "duplicate_authors": duplicate_authors,
        "paragraph_end_citation_clusters": paragraph_end_clusters(body),
        "expected_source_count": expected_count,
        "expected_source_count_ok": None
        if expected_count is None
        else len(reference_numbers) == expected_count == len(first_order),
    }
    result["ok"] = (
        bool(cites)
        and not result["duplicate_citation_numbers"]
        and result["first_use_sequence_ok"]
        and result["reference_order_ok"]
        and not result["missing_reference_entries"]
        and not result["uncited_reference_entries"]
        and not result["duplicate_authors"]
        and not result["paragraph_end_citation_clusters"]
        and (result["expected_source_count_ok"] is not False)
    )
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--paper", required=True, help="Markdown paper to audit")
    parser.add_argument("--output", help="Optional JSON report path")
    parser.add_argument("--expected-count", type=int, help="Expected number of sources")
    args = parser.parse_args()

    text = Path(args.paper).read_text(encoding="utf-8")
    result = audit(text, args.expected_count)
    payload = json.dumps(result, ensure_ascii=False, indent=2)
    if args.output:
        out = Path(args.output)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(payload, encoding="utf-8")
        print(out)
    else:
        print(payload)
    raise SystemExit(0 if result["ok"] else 1)


if __name__ == "__main__":
    main()
