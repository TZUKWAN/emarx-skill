#!/usr/bin/env python
"""Gate a single EMARX section before it is admitted into a full paper."""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from pathlib import Path


CN_RE = re.compile(r"[\u4e00-\u9fff]")
HEADING_RE = re.compile(r"(?m)^(#{1,6})\s*(.+?)\s*$")
CITE_RE = re.compile(r"(?<!!)\[(\d+)\]")
SENTENCE_RE = re.compile(r"[^。！？!?；;\n]+[。！？!?；;]?")

BANNED_PATTERNS = {
    "author_visible": r"本文|笔者|本研究|文章认为|本文认为|核心观点",
    "review_insert": r"有研究指出|相关研究表明|相关研究指出|已有研究认为|已有研究指出|学者认为|学者指出",
    "mechanical_sequence": r"首先|其次|再次|最后",
    "formulaic_contrast": r"不是[^。！？；\n]{0,80}而是|并非[^。！？；\n]{0,80}而是|不在于[^。！？；\n]{0,80}而在于",
    "inflated_language": r"填补空白|首次|开创性|重构|重建",
    "colon_mini_title": r"问题在于[:：]|关键在于[:：]|核心观点是[:：]|具体而言[:：]",
}

OPENING_PATTERNS = {
    "naked_negative": r"^(不是|并非|不能|不应|不要|没有|无需|并不|绝非)",
    "suspended_pronoun": r"^(这种|这一|上述|这说明|这意味着|由此)",
    "loose_transition": r"^(因此|由此可见|与此同时|值得注意的是|进一步看|进一步而言)",
    "empty_framing": r"^(在.{0,18}(背景|语境|视域|视角|时代|格局)下|随着.{0,18}(发展|推进|演进)|当前|近年来)",
    "premature_judgment": r"^(关键在于|核心是|本质上|根本上|必须|应当|需要)",
}

GENERIC_VERBS = ["推动", "促进", "加强", "优化", "提升", "赋能", "打造", "构建"]
MODALS = ["应", "应当", "需要", "必须", "建议", "不得"]
SLOGAN_ENDINGS = [
    "具有重要意义",
    "提供有力支撑",
    "形成合力",
    "形成强大合力",
    "开辟新路径",
    "提升传播效能",
    "现实价值",
    "内在要求",
]


def strip_references(text: str) -> str:
    return re.split(r"(?m)^#{1,6}\s*参考文献\s*$|^参考文献\s*$", text, maxsplit=1)[0]


def extract_section(text: str, section_title: str | None) -> str:
    if not section_title:
        return strip_references(text)
    matches = list(HEADING_RE.finditer(text))
    for index, match in enumerate(matches):
        level = len(match.group(1))
        title = match.group(2).strip()
        if section_title in title:
            start = match.start()
            end = len(text)
            for nxt in matches[index + 1 :]:
                if len(nxt.group(1)) <= level:
                    end = nxt.start()
                    break
            return strip_references(text[start:end])
    raise SystemExit(f"Section title not found: {section_title}")


def paragraphs(text: str) -> list[str]:
    result: list[str] = []
    for block in re.split(r"\n\s*\n", text):
        cleaned = block.strip()
        if not cleaned or cleaned.startswith("#"):
            continue
        result.append(cleaned)
    return result


def sentence_count(text: str) -> int:
    return len([item for item in SENTENCE_RE.findall(text) if CN_RE.search(item)])


def count_matches(pattern: str, text: str) -> int:
    return len(re.findall(pattern, text))


def opening_issues(paras: list[str]) -> dict[str, list[dict]]:
    issues: dict[str, list[dict]] = {name: [] for name in OPENING_PATTERNS}
    for index, para in enumerate(paras, 1):
        opening = re.sub(r"\s+", "", para)[:40]
        for name, pattern in OPENING_PATTERNS.items():
            if re.search(pattern, opening):
                issues[name].append({"paragraph": index, "opening": opening})
    return {name: items for name, items in issues.items() if items}


def generic_verb_contexts(text: str) -> dict[str, int]:
    return {verb: text.count(verb) for verb in GENERIC_VERBS if text.count(verb)}


def modal_count(text: str) -> dict[str, int]:
    return {word: text.count(word) for word in MODALS if text.count(word)}


def repeated_openings(paras: list[str]) -> dict[str, int]:
    starts = []
    for para in paras:
        normalized = re.sub(r"\s+", "", para)
        if normalized:
            starts.append(normalized[:8])
    return {key: value for key, value in Counter(starts).items() if value >= 2}


def citation_contexts(text: str) -> list[dict]:
    contexts: list[dict] = []
    generic_attr = re.compile(r"(研究|文献|学者|观点|成果)(指出|认为|表明|显示|提出)")
    for match in CITE_RE.finditer(text):
        left = text[max(0, match.start() - 120) : match.start()]
        sentence_left = re.split(r"[。！？!?\n]", left.rstrip())[-1].strip()
        contexts.append(
            {
                "number": int(match.group(1)),
                "context": (left[-70:] + match.group(0)).replace("\n", " "),
                "generic_attribution": bool(generic_attr.search(sentence_left)),
                "detached": len(CN_RE.findall(sentence_left)) < 6,
            }
        )
    return contexts


def audit(text: str, section_title: str | None, require_citation: bool, terms: list[str]) -> dict:
    section = extract_section(text, section_title)
    paras = paragraphs(section)
    cn_chars = len(CN_RE.findall(section))
    citations = [int(num) for num in CITE_RE.findall(section)]
    contexts = citation_contexts(section)
    banned = {name: count_matches(pattern, section) for name, pattern in BANNED_PATTERNS.items()}
    banned = {name: count for name, count in banned.items() if count}
    openings = opening_issues(paras)
    generic_verbs = generic_verb_contexts(section)
    modals = modal_count(section)
    term_counts = {term: section.count(term) for term in terms if term and section.count(term)}
    slogan_endings = [
        {"paragraph": index, "ending": para[-80:]}
        for index, para in enumerate(paras, 1)
        if any(phrase in para[-40:] for phrase in SLOGAN_ENDINGS)
    ]
    only_assertion_paras = [
        {"paragraph": index, "snippet": para[:120]}
        for index, para in enumerate(paras, 1)
        if sentence_count(para) >= 3
        and not CITE_RE.search(para)
        and not re.search(r"例如|比如|材料|数据|案例|政策|报告|显示|意味着|因为|由于|从而|使得|导致|源于|取决于", para)
    ]
    issues: list[str] = []
    if len(paras) < 2:
        issues.append("too_few_paragraphs")
    if cn_chars < 500:
        issues.append("section_too_short")
    if banned:
        issues.append("banned_patterns")
    if openings:
        issues.append("bad_paragraph_openings")
    if repeated_openings(paras):
        issues.append("repeated_openings")
    if require_citation and not citations:
        issues.append("missing_required_citation")
    if any(item["generic_attribution"] or item["detached"] for item in contexts):
        issues.append("weak_citation_context")
    if sum(generic_verbs.values()) > max(6, len(paras) * 2):
        issues.append("generic_verb_overuse")
    if sum(modals.values()) > max(5, len(paras) * 2):
        issues.append("instructional_modal_overuse")
    if slogan_endings:
        issues.append("slogan_endings")
    if len(only_assertion_paras) >= max(2, len(paras) // 2):
        issues.append("assertion_only_paragraphs")
    result = {
        "section_title_filter": section_title,
        "cn_chars": cn_chars,
        "paragraph_count": len(paras),
        "sentence_count": sentence_count(section),
        "citations": citations,
        "unique_citations": sorted(set(citations), key=citations.index),
        "citation_contexts": contexts,
        "banned_counts": banned,
        "opening_issues": openings,
        "repeated_openings": repeated_openings(paras),
        "generic_verb_counts": generic_verbs,
        "modal_counts": modals,
        "term_counts": term_counts,
        "slogan_endings": slogan_endings,
        "assertion_only_paragraphs": only_assertion_paras,
        "issues": issues,
        "ok": not issues,
    }
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--paper", required=True, help="Markdown paper or section path")
    parser.add_argument("--output", required=True, help="JSON output path")
    parser.add_argument("--section-title", help="Extract and audit the first heading containing this text")
    parser.add_argument("--require-citation", action="store_true", help="Require at least one citation in this section")
    parser.add_argument("--terms", nargs="*", default=[], help="Terms to count for repetition")
    args = parser.parse_args()

    text = Path(args.paper).read_text(encoding="utf-8")
    result = audit(text, args.section_title, args.require_citation, args.terms)
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(out)
    raise SystemExit(0 if result["ok"] else 1)


if __name__ == "__main__":
    main()
