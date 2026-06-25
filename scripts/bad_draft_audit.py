from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from pathlib import Path


CN_RE = re.compile(r"[\u4e00-\u9fff]")
HEADING_RE = re.compile(r"(?m)^(#{1,6})\s*(.+)$")
REF_HEADING_RE = re.compile(r"(?m)^#{0,6}\s*参考文献\s*$")
SENTENCE_RE = re.compile(r"[^。！？!?；;]+[。！？!?；;]?")

DEFAULT_TERMS = [
    "生成式人工智能",
    "中华文化国际传播",
    "文化主体性",
    "技术赋能",
    "价值校准",
    "意义共建",
    "路径",
    "机制",
    "治理",
    "语境",
]

GENERIC_PATTERNS = [
    "重要意义",
    "现实意义",
    "优化路径",
    "提升效能",
    "赋能发展",
    "加强建设",
    "推动传播",
    "提供支撑",
    "形成合力",
]

SOURCE_LABEL_PATTERNS = [
    "研究指出",
    "研究认为",
    "相关研究",
    "有研究指出",
    "已有研究",
]

MECHANICAL_SEQUENCE_PATTERNS = [
    "首先",
    "其次",
    "再次",
    "最后",
]

BINARY_CONTRAST_PATTERNS = [
    r"不是[^。！？；\n]{0,80}而是",
    r"并非[^。！？；\n]{0,80}而是",
    r"不在于[^。！？；\n]{0,80}而在于",
]

INFLATED_NOVELTY_PATTERNS = [
    "重构",
    "重建",
    "填补空白",
]

NAKED_NEGATIVE_OPENING_RE = re.compile(
    r"^(不是|并非|不能|不应|不要|没有|无需|并不|绝非|非但|切忌|避免)"
)

LOOSE_TRANSITION_OPENING_RE = re.compile(
    r"^(因此|由此可见|与此同时|值得注意的是|从这个意义上说|在这一意义上)"
)

GENERIC_VERB_PATTERNS = [
    "推动",
    "促进",
    "加强",
    "优化",
    "提升",
    "赋能",
    "打造",
    "构建",
]


def cn_len(text: str) -> int:
    return len(CN_RE.findall(text))


def split_body_and_refs(text: str) -> tuple[str, str]:
    match = REF_HEADING_RE.search(text)
    if not match:
        return text, ""
    return text[: match.start()], text[match.start() :]


def sentence_bucket(length: int) -> str:
    if length <= 20:
        return "S"
    if length <= 45:
        return "M"
    if length <= 80:
        return "L"
    return "XL"


def analyze_sentences(body: str) -> dict:
    lengths = []
    for match in SENTENCE_RE.finditer(body):
        sentence = match.group(0).strip()
        if not sentence or sentence.startswith("#"):
            continue
        length = cn_len(sentence)
        if length >= 4:
            lengths.append(length)
    buckets = Counter(sentence_bucket(length) for length in lengths)
    transitions = sum(
        1
        for left, right in zip(
            [sentence_bucket(length) for length in lengths],
            [sentence_bucket(length) for length in lengths][1:],
        )
        if left != right
    )
    total = max(1, len(lengths))
    return {
        "sentence_count": len(lengths),
        "avg_sentence_cn": round(sum(lengths) / total, 2),
        "bucket_pct": {key: round(value * 100 / total, 2) for key, value in buckets.items()},
        "alternation_pct": round(transitions * 100 / max(1, total - 1), 2),
        "max_sentence_cn": max(lengths or [0]),
    }


def paragraph_starts(body: str) -> list[str]:
    starts = []
    for para in [item.strip() for item in re.split(r"\n\s*\n", body) if item.strip()]:
        if para.startswith("#"):
            continue
        cleaned = re.sub(r"^[#\s]+", "", para)
        match = re.match(
            r"^(首先|其次|再次|最后|第一|第二|第三|第四|第五|第六|因此|由此|同时|这种|这一|这说明|这意味着|生成式人工智能|中华文化)",
            cleaned,
        )
        starts.append(match.group(1) if match else cleaned[:8])
    return starts


def paragraph_opening_issues(body: str) -> dict:
    naked_negative = []
    loose_transition = []
    for index, para in enumerate([item.strip() for item in re.split(r"\n\s*\n", body) if item.strip()], 1):
        if para.startswith("#"):
            continue
        cleaned = re.sub(r"^[#\s]+", "", para)
        first_sentence = re.split(r"[。！？!?；;]", cleaned, maxsplit=1)[0][:120]
        if NAKED_NEGATIVE_OPENING_RE.match(first_sentence):
            naked_negative.append({"paragraph": index, "opening": first_sentence})
        if LOOSE_TRANSITION_OPENING_RE.match(first_sentence):
            loose_transition.append({"paragraph": index, "opening": first_sentence})
    return {
        "naked_negative_openings": naked_negative,
        "loose_transition_openings": loose_transition,
    }


def audit(path: Path, terms: list[str]) -> dict:
    text = path.read_text(encoding="utf-8-sig", errors="replace")
    body, refs = split_body_and_refs(text)
    headings = HEADING_RE.findall(text)
    second_level = [title for marks, title in headings if "（" in title and "）" in title]
    citations = re.findall(r"\[(\d+)\]", body)
    references = re.findall(r"(?m)^\[(\d+)\]\s*(.+)$", refs)
    starts = Counter(paragraph_starts(body))
    term_counts = {term: body.count(term) for term in terms}
    generic_counts = {term: body.count(term) for term in GENERIC_PATTERNS if body.count(term)}
    source_label_count = sum(body.count(pattern) for pattern in SOURCE_LABEL_PATTERNS)
    mechanical_sequence_counts = {
        term: body.count(term)
        for term in MECHANICAL_SEQUENCE_PATTERNS
        if body.count(term)
    }
    binary_contrast_counts = {
        pattern: len(re.findall(pattern, body))
        for pattern in BINARY_CONTRAST_PATTERNS
        if re.findall(pattern, body)
    }
    inflated_novelty_counts = {
        term: body.count(term)
        for term in INFLATED_NOVELTY_PATTERNS
        if body.count(term)
    }
    generic_verb_counts = {
        term: body.count(term)
        for term in GENERIC_VERB_PATTERNS
        if body.count(term)
    }
    opening_issues = paragraph_opening_issues(body)
    sentence_stats = analyze_sentences(body)
    main_chars = cn_len(body)

    risks = []
    if main_chars < 10000:
        risks.append("main_text_below_10000")
    if len(second_level) == 0:
        risks.append("missing_second_level_headings")
    repeated_terms = {
        term: count
        for term, count in term_counts.items()
        if count >= max(12, main_chars // 250)
    }
    if repeated_terms:
        risks.append("high_concept_repetition")
    repeated_starts = {start: count for start, count in starts.items() if count >= 5}
    if repeated_starts:
        risks.append("repeated_paragraph_openings")
    if source_label_count >= 6:
        risks.append("citations_as_source_labels")
    if generic_counts:
        risks.append("generic_academic_phrases")
    if sum(mechanical_sequence_counts.values()) >= 4:
        risks.append("mechanical_sequence_words")
    if sum(binary_contrast_counts.values()) >= 2:
        risks.append("formulaic_binary_contrasts")
    if inflated_novelty_counts:
        risks.append("inflated_novelty_language")
    if opening_issues["naked_negative_openings"]:
        risks.append("naked_negative_paragraph_openings")
    if len(opening_issues["loose_transition_openings"]) >= 3:
        risks.append("loose_transition_openings")
    if sum(generic_verb_counts.values()) >= max(8, main_chars // 600):
        risks.append("generic_verb_overuse")
    bucket_pct = sentence_stats.get("bucket_pct", {})
    if bucket_pct.get("S", 0) + bucket_pct.get("M", 0) >= 70:
        risks.append("short_medium_heavy_expository_style")

    return {
        "paper": str(path),
        "main_text_cn_chars": main_chars,
        "heading_count": len(headings),
        "second_level_heading_count": len(second_level),
        "body_citation_count": len(citations),
        "unique_body_citations": len(set(citations)),
        "reference_count": len(references),
        "sentence_stats": sentence_stats,
        "term_counts": term_counts,
        "high_repetition_terms": repeated_terms,
        "paragraph_start_top": starts.most_common(15),
        "repeated_paragraph_openings": repeated_starts,
        "source_label_count": source_label_count,
        "generic_phrase_counts": generic_counts,
        "mechanical_sequence_counts": mechanical_sequence_counts,
        "binary_contrast_counts": binary_contrast_counts,
        "inflated_novelty_counts": inflated_novelty_counts,
        "generic_verb_counts": generic_verb_counts,
        "opening_issues": opening_issues,
        "risks": risks,
        "ok": not risks,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit a Chinese academic draft for formal compliance with hollow argument risks.")
    parser.add_argument("--paper", required=True, help="Markdown paper path.")
    parser.add_argument("--output", required=True, help="JSON output path.")
    parser.add_argument("--terms", nargs="*", default=DEFAULT_TERMS, help="Key terms to count for repetition.")
    args = parser.parse_args()

    report = audit(Path(args.paper), args.terms)
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(str(output))
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
