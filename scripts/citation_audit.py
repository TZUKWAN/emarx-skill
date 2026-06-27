#!/usr/bin/env python
"""Audit EMARX numeric citations and GB/T 7714 reference-list mechanics.

This script proves mechanical consistency only. It cannot prove that a source
supports a claim; the final run manifest must record a source-to-sentence
manual review by the main model.
"""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter, defaultdict
from pathlib import Path


CITE_RE = re.compile(r"(?<!!)\[(\d+)\]")
REF_RE = re.compile(r"^\s*\[(\d+)\]\s*(.+?)\s*$")
DOC_TYPE_RE = re.compile(r"\[(J|M|D|N|C|R|S|P|DB|CP|EB)(?:/[A-Z]+)?\]", re.I)
YEAR_RE = re.compile(r"(?<!\d)(?:19|20)\d{2}(?!\d)")
GENERIC_ATTRIBUTION_RE = re.compile(
    r"(?:有|据|相关|既有|现有|已有)?(?:研究|文献|学者|观点|成果)"
    r"(?:指出|认为|表明|显示|发现|强调|提出|说明)"
)


def split_body_refs(text: str) -> tuple[str, str, bool]:
    marker = re.search(r"(?m)^#{1,6}\s*参考文献\s*$|^参考文献\s*$", text)
    if not marker:
        return text, "", False
    return text[: marker.start()], text[marker.end() :], True


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
    return [part.strip() for part in parts if part.strip()]


def paragraph_end_clusters(body: str) -> list[str]:
    issues: list[str] = []
    for paragraph in re.split(r"\n\s*\n", body):
        stripped = paragraph.strip()
        if re.search(r"(?:\s*\[\d+\]){2,}[。！？.!?]?\s*$", stripped):
            issues.append(stripped[-180:])
    return issues


def stacked_citations(body: str) -> list[str]:
    return sorted(set(re.findall(r"(?:\[\d+\]\s*){2,}", body)))


def citation_contexts(body: str) -> list[dict]:
    contexts: list[dict] = []
    for match in CITE_RE.finditer(body):
        left = body[max(0, match.start() - 100) : match.start()]
        right = body[match.end() : match.end() + 60]
        claim_left = left.rstrip()
        if claim_left.endswith(("。", "！", "？", ".", "!", "?")):
            claim_left = claim_left[:-1].rstrip()
        sentence_left = re.split(r"[。！？!?\n]", claim_left)[-1].strip()
        contexts.append(
            {
                "number": int(match.group(1)),
                "context": (left[-70:] + match.group(0) + right[:40]).replace("\n", " "),
                "generic_attribution": bool(GENERIC_ATTRIBUTION_RE.search(sentence_left)),
                "detached": len(re.findall(r"[\u4e00-\u9fffA-Za-z0-9]", sentence_left)) < 4,
            }
        )
    return contexts


def gbt_issues(reference_lines: list[tuple[int, str]]) -> list[dict]:
    issues: list[dict] = []
    for number, text in reference_lines:
        reasons: list[str] = []
        doc_type = DOC_TYPE_RE.search(text)
        if not doc_type:
            reasons.append("缺少或无法识别文献类型标识")
        if not YEAR_RE.search(text):
            reasons.append("缺少年份")
        author_part = re.split(r"[.．]", text, maxsplit=1)[0].strip()
        if not author_part or len(author_part) > 120:
            reasons.append("作者项缺失或分隔异常")
        if doc_type and doc_type.group(1).upper() == "J":
            remainder = text[doc_type.end() :]
            if not re.search(r"[.．]\s*[^,.，。]{2,}\s*[,，]", remainder):
                reasons.append("期刊名或期刊项分隔不完整")
        if doc_type and doc_type.group(1).upper() == "M":
            remainder = text[doc_type.end() :]
            if not re.search(r"[:：]", remainder):
                reasons.append("专著缺少出版地与出版者分隔")
        if reasons:
            issues.append({"number": number, "reasons": reasons, "reference": text})
    return issues


def normalize_for_match(value: str) -> str:
    return re.sub(r"[^0-9A-Za-z\u4e00-\u9fff]", "", value).lower()


def load_required_sources(path: Path | None) -> list[dict]:
    if path is None:
        return []
    raw = path.read_text(encoding="utf-8").strip()
    if not raw:
        return []
    if path.suffix.lower() == ".json":
        payload = json.loads(raw)
        if isinstance(payload, dict):
            payload = payload.get("sources", [])
        result: list[dict] = []
        for item in payload:
            if isinstance(item, str):
                result.append({"id": item, "match_terms": [item]})
            elif isinstance(item, dict):
                terms = item.get("match_terms") or [item.get("title") or item.get("reference") or item.get("id", "")]
                result.append({"id": str(item.get("id") or item.get("title") or terms[0]), "match_terms": terms})
        return result
    return [
        {"id": line.strip(), "match_terms": [line.strip()]}
        for line in raw.splitlines()
        if line.strip()
    ]


def source_coverage(reference_lines: list[tuple[int, str]], required_sources: list[dict]) -> dict:
    normalized_refs = [normalize_for_match(text) for _, text in reference_lines]
    matched: list[str] = []
    missing: list[str] = []
    ambiguous: list[str] = []
    for source in required_sources:
        terms = [normalize_for_match(str(term)) for term in source["match_terms"] if str(term).strip()]
        hits = [i for i, ref in enumerate(normalized_refs) if any(term and term in ref for term in terms)]
        if len(hits) == 1:
            matched.append(source["id"])
        elif len(hits) == 0:
            missing.append(source["id"])
        else:
            ambiguous.append(source["id"])
    return {
        "required_count": len(required_sources),
        "matched_count": len(matched),
        "matched": matched,
        "missing": missing,
        "ambiguous": ambiguous,
        "ok": bool(required_sources) and not missing and not ambiguous,
    }


def audit(
    text: str,
    expected_count: int | None = None,
    required_sources: list[dict] | None = None,
) -> dict:
    body, refs, has_reference_heading = split_body_refs(text)
    cites = [int(number) for number in CITE_RE.findall(body)]
    counts = Counter(cites)
    first_order: list[int] = []
    for number in cites:
        if number not in first_order:
            first_order.append(number)

    reference_lines = extract_reference_lines(refs)
    reference_numbers = [number for number, _ in reference_lines]
    repeated_authors: dict[str, list[int]] = defaultdict(list)
    for number, ref_text in reference_lines:
        for name in author_names(ref_text):
            repeated_authors[name].append(number)

    contexts = citation_contexts(body)
    coverage = source_coverage(reference_lines, required_sources or [])
    expected_sequence = list(range(1, len(first_order) + 1))
    result = {
        "has_reference_heading": has_reference_heading,
        "inline_citation_count": len(cites),
        "unique_inline_citations": first_order,
        "duplicate_citation_numbers": {str(k): v for k, v in counts.items() if v > 1},
        "first_use_sequence_ok": first_order == expected_sequence,
        "expected_first_use_sequence": expected_sequence,
        "reference_numbers": reference_numbers,
        "reference_order_ok": reference_numbers == first_order,
        "duplicate_reference_numbers": [k for k, v in Counter(reference_numbers).items() if v > 1],
        "duplicate_reference_texts": [text for text, count in Counter(t for _, t in reference_lines).items() if count > 1],
        "missing_reference_entries": [n for n in first_order if n not in reference_numbers],
        "uncited_reference_entries": [n for n in reference_numbers if n not in first_order],
        "duplicate_authors": {name: nums for name, nums in repeated_authors.items() if len(nums) > 1},
        "stacked_citations": stacked_citations(body),
        "paragraph_end_citation_clusters": paragraph_end_clusters(body),
        "detached_citations": [item for item in contexts if item["detached"]],
        "generic_attribution_citations": [item for item in contexts if item["generic_attribution"]],
        "citation_contexts": contexts,
        "gbt_7714_issues": gbt_issues(reference_lines),
        "required_source_coverage": coverage,
        "expected_source_count": expected_count,
        "expected_source_count_ok": None
        if expected_count is None
        else len(reference_numbers) == expected_count == len(first_order),
        "semantic_support_verified": False,
        "semantic_support_note": "必须由主模型逐条对照原文与引文句复核，脚本不能证明语义支持关系。",
    }
    result["ok"] = (
        has_reference_heading
        and bool(cites)
        and not result["duplicate_citation_numbers"]
        and result["first_use_sequence_ok"]
        and result["reference_order_ok"]
        and not result["duplicate_reference_numbers"]
        and not result["duplicate_reference_texts"]
        and not result["missing_reference_entries"]
        and not result["uncited_reference_entries"]
        and not result["duplicate_authors"]
        and not result["stacked_citations"]
        and not result["paragraph_end_citation_clusters"]
        and not result["detached_citations"]
        and not result["generic_attribution_citations"]
        and not result["gbt_7714_issues"]
        and (result["expected_source_count_ok"] is not False)
        and (not required_sources or coverage["ok"])
    )
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--paper", required=True, help="Markdown paper to audit")
    parser.add_argument("--output", help="Optional JSON report path")
    parser.add_argument("--expected-count", type=int, help="Expected number of sources")
    parser.add_argument(
        "--required-sources",
        type=Path,
        help="JSON manifest or UTF-8 text file listing sources that must be covered",
    )
    args = parser.parse_args()

    text = Path(args.paper).read_text(encoding="utf-8")
    required_sources = load_required_sources(args.required_sources)
    result = audit(text, args.expected_count, required_sources)
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
