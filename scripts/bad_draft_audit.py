from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from pathlib import Path


CN_RE = re.compile(r"[\u4e00-\u9fff]")
HEADING_RE = re.compile(r"(?m)^(#{1,6})\s*(.+)$")
FORMAL_HEADING_RE = re.compile(
    r"^(?:[一二三四五六七八九十]+、|（[一二三四五六七八九十]+）|\d+[.．、])\s*\S+"
)
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

SOURCE_PARADE_RE = re.compile(
    r"^[\u4e00-\u9fff]{2,4}(?:等|和[\u4e00-\u9fff]{2,4})?(?:指出|认为|提出|强调|分析|概括|区分|总结)"
)

POLICY_PILE_RE = re.compile(
    r"^(党的|习近平|二十大|三中全会|全国宣传思想|《中共中央|《决定》|《办法》)"
)

EMPTY_COUNTER_PATTERNS = [
    r"(?:完善|加强|深化|优化|构建|推动|提升).{0,15}(?:完善|加强|深化|优化|构建|推动|提升)",
    r"以\s*.+?\s*为\s*(?:核心|重点|基点|支撑|驱动|抓手)",
]
EMPTY_COUNTER_RE = re.compile("|".join(EMPTY_COUNTER_PATTERNS))

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
    r"^(因此|由此可见|与此同时|值得注意的是|从这个意义上说|在这一意义上|进一步看|进一步而言)"
)

EMPTY_FRAMING_OPENING_RE = re.compile(
    r"^(在.{0,18}(背景|语境|视域|视角|时代|格局)下|随着.{0,18}(发展|推进|演进)|当前|近年来|从.{0,18}来看)"
)

SUSPENDED_PRONOUN_OPENING_RE = re.compile(
    r"^(这种|这一|上述|这说明|这意味着|由此)"
)

PREMATURE_JUDGMENT_OPENING_RE = re.compile(
    r"^(关键在于|核心是|根本上|本质上|必须|应当|需要)"
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

SLOGAN_ENDING_PATTERNS = [
    "具有重要意义",
    "提供有力支撑",
    "形成强大合力",
    "开辟新路径",
    "提升传播效能",
    "现实价值",
    "内在要求",
]

PROCESS_LEAK_PATTERNS = [
    "诊断卡",
    "机制链",
    "论证任务",
    "argumentative job",
    "source coverage",
    "coverage table",
    "审稿轮次",
    "review round",
    "ScholarlyReviewer",
    "LogicReviewer",
    "ProseReviewer",
    "FormatReviewer",
    "pass/fail",
    "audit",
]

DIAGNOSTIC_HEADING_PATTERNS = [
    "研究对象与概念边界",
    "概念界定",
    "概念边界",
    "理论框架",
    "研究设计",
    "材料锚定",
    "问题诊断",
    "学理性诊断",
    "机制链",
    "论证任务",
    "创新点分析",
    "事实核查",
    "审稿意见",
]

WORKFLOW_HEADING_PATTERNS = [
    "可执行条件",
    "路径建设与",
    "建设与可执行",
    "质量控制",
    "写作思路",
    "论文结构",
    "资料梳理",
]

GENERIC_STRUCTURE_HEADINGS = [
    "机遇",
    "挑战",
    "路径",
    "对策",
    "意义",
    "价值",
]

INSTRUCTIONAL_MODAL_PATTERNS = [
    "应",
    "应当",
    "需要",
    "必须",
    "不得",
    "建议",
]

YEAR_RE = re.compile(r"(?:19|20)\d{2}")
NUMBER_RE = re.compile(r"\d+(?:\.\d+)?%?|\d+\.\d+")
QUOTE_RE = re.compile(r"[\u2018\u2019\u201c\u201d\"']")
ANCHOR_TERMS = [
    "案例",
    "实例",
    "数据",
    "统计",
    "调查",
    "问卷",
    "访谈",
    "实验",
    "平台",
    "算法",
    "模型",
    "产品",
    "政策",
    "法规",
    "办法",
    "报告",
    "研究显示",
    "研究表明",
    "学者",
    "提出",
    "发现",
    "指出",
    "认为",
    "观测",
    "测量",
]


def cn_len(text: str) -> int:
    return len(CN_RE.findall(text))


def split_body_and_refs(text: str) -> tuple[str, str]:
    match = REF_HEADING_RE.search(text)
    if not match:
        return text, ""
    return text[: match.start()], text[match.start() :]


def extract_heading_titles(text: str) -> list[dict]:
    headings = []
    seen = set()
    for match in HEADING_RE.finditer(text):
        title = match.group(2).strip()
        key = (match.start(), title)
        seen.add(key)
        headings.append({
            "line": text.count("\n", 0, match.start()) + 1,
            "level": len(match.group(1)),
            "title": title,
            "source": "markdown",
        })
    for offset, line in enumerate(text.splitlines(), 1):
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if FORMAL_HEADING_RE.match(stripped) or stripped in {"摘要", "关键词", "引言", "结语", "结论", "参考文献"}:
            key = (offset, stripped)
            if key not in seen:
                headings.append({
                    "line": offset,
                    "level": 0,
                    "title": stripped,
                    "source": "formal",
                })
    return headings


def structure_heading_issues(text: str) -> dict:
    headings = extract_heading_titles(text)
    diagnostic = []
    workflow = []
    generic = []
    for heading in headings:
        title = heading["title"]
        clean_title = re.sub(r"^[#\s一二三四五六七八九十、（）()0-9.．]+", "", title).strip()
        if any(pattern in title for pattern in DIAGNOSTIC_HEADING_PATTERNS):
            diagnostic.append(heading)
        if any(pattern in title for pattern in WORKFLOW_HEADING_PATTERNS):
            workflow.append(heading)
        if clean_title in GENERIC_STRUCTURE_HEADINGS or re.fullmatch(
            r"(?:结构性)?(?:机遇|挑战|路径|对策|意义|价值)(?:分析|研究|阐释|审视|探析)?",
            clean_title,
        ):
            generic.append(heading)
    return {
        "headings": headings,
        "diagnostic_heading_leaks": diagnostic,
        "workflow_heading_leaks": workflow,
        "generic_structure_headings": generic,
    }


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
    empty_framing = []
    suspended_pronoun = []
    premature_judgment = []
    slogan_ending = []
    for index, para in enumerate([item.strip() for item in re.split(r"\n\s*\n", body) if item.strip()], 1):
        if para.startswith("#"):
            continue
        cleaned = re.sub(r"^[#\s]+", "", para)
        first_sentence = re.split(r"[。！？!?；;]", cleaned, maxsplit=1)[0][:120]
        last_sentence_candidates = [item.strip() for item in re.split(r"[。！？!?；;]", cleaned) if item.strip()]
        last_sentence = (last_sentence_candidates[-1] if last_sentence_candidates else "")[-120:]
        if NAKED_NEGATIVE_OPENING_RE.match(first_sentence):
            naked_negative.append({"paragraph": index, "opening": first_sentence})
        if LOOSE_TRANSITION_OPENING_RE.match(first_sentence):
            loose_transition.append({"paragraph": index, "opening": first_sentence})
        if EMPTY_FRAMING_OPENING_RE.match(first_sentence):
            empty_framing.append({"paragraph": index, "opening": first_sentence})
        if SUSPENDED_PRONOUN_OPENING_RE.match(first_sentence):
            suspended_pronoun.append({"paragraph": index, "opening": first_sentence})
        if PREMATURE_JUDGMENT_OPENING_RE.match(first_sentence):
            premature_judgment.append({"paragraph": index, "opening": first_sentence})
        if any(pattern in last_sentence for pattern in SLOGAN_ENDING_PATTERNS):
            slogan_ending.append({"paragraph": index, "ending": last_sentence})
    return {
        "naked_negative_openings": naked_negative,
        "loose_transition_openings": loose_transition,
        "empty_framing_openings": empty_framing,
        "suspended_pronoun_openings": suspended_pronoun,
        "premature_judgment_openings": premature_judgment,
        "slogan_endings": slogan_ending,
    }


def review_like_patterns(body: str) -> dict:
    source_parade = []
    policy_pile = []
    empty_counter = []
    for index, para in enumerate([item.strip() for item in re.split(r"\n\s*\n", body) if item.strip()], 1):
        if para.startswith("#"):
            continue
        cleaned = re.sub(r"^[#\s]+", "", para)
        first_sentence = re.split(r"[。！？!?；;]", cleaned, maxsplit=1)[0][:120]
        if SOURCE_PARADE_RE.match(first_sentence) and "[" in first_sentence and "]" in first_sentence:
            source_parade.append({"paragraph": index, "opening": first_sentence})
        if POLICY_PILE_RE.match(first_sentence):
            policy_pile.append({"paragraph": index, "opening": first_sentence})
        if EMPTY_COUNTER_RE.search(cleaned):
            empty_counter.append({"paragraph": index, "snippet": cleaned[:120]})
    return {
        "source_parade_paragraphs": source_parade,
        "policy_pile_paragraphs": policy_pile,
        "empty_countermeasure_sentences": empty_counter,
    }


def paragraph_has_anchor(para: str) -> bool:
    cleaned = re.sub(r"^[#\s]+", "", para)
    if cn_len(cleaned) < 30:
        return True  # skip very short fragments
    if para.startswith("#"):
        return True
    has_citation = "[" in cleaned and "]" in cleaned
    has_year = YEAR_RE.search(cleaned) is not None
    has_number = NUMBER_RE.search(cleaned) is not None
    has_quote = QUOTE_RE.search(cleaned) is not None
    has_anchor_term = any(term in cleaned for term in ANCHOR_TERMS)
    return has_citation or has_year or has_number or has_quote or has_anchor_term


def floating_paragraphs(body: str) -> list[dict]:
    paras = [item.strip() for item in re.split(r"\n\s*\n", body) if item.strip()]
    flagged = []
    run_start = None
    run_openings = []
    for index, para in enumerate(paras, 1):
        if para.startswith("#"):
            continue
        if paragraph_has_anchor(para):
            if run_start is not None and len(run_openings) >= 3:
                flagged.append({
                    "start_paragraph": run_start,
                    "end_paragraph": index - 1,
                    "count": len(run_openings),
                    "openings": run_openings,
                })
            run_start = None
            run_openings = []
        else:
            if run_start is None:
                run_start = index
            cleaned = re.sub(r"^[#\s]+", "", para)
            first_sentence = re.split(r"[。！？!?；;]", cleaned, maxsplit=1)[0][:120]
            run_openings.append(first_sentence)
    if run_start is not None and len(run_openings) >= 3:
        flagged.append({
            "start_paragraph": run_start,
            "end_paragraph": len(paras),
            "count": len(run_openings),
            "openings": run_openings,
        })
    return flagged


def audit(path: Path, terms: list[str]) -> dict:
    text = path.read_text(encoding="utf-8-sig", errors="replace")
    body, refs = split_body_and_refs(text)
    headings = HEADING_RE.findall(text)
    structure_issues = structure_heading_issues(text)
    heading_titles = [item["title"] for item in structure_issues["headings"]]
    second_level = [title for title in heading_titles if "（" in title and "）" in title]
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
    process_leak_counts = {
        term: body.count(term)
        for term in PROCESS_LEAK_PATTERNS
        if body.count(term)
    }
    instructional_modal_counts = {
        term: body.count(term)
        for term in INSTRUCTIONAL_MODAL_PATTERNS
        if body.count(term)
    }
    opening_issues = paragraph_opening_issues(body)
    review_like = review_like_patterns(body)
    floating = floating_paragraphs(body)
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
        if count >= max(10, main_chars // 350)
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
    if sum(mechanical_sequence_counts.values()) >= 8:
        risks.append("mechanical_sequence_words")
    if sum(binary_contrast_counts.values()) >= 3:
        risks.append("formulaic_binary_contrasts")
    if inflated_novelty_counts:
        risks.append("inflated_novelty_language")
    if opening_issues["naked_negative_openings"]:
        risks.append("naked_negative_paragraph_openings")
    if len(opening_issues["loose_transition_openings"]) >= 5:
        risks.append("loose_transition_openings")
    if len(opening_issues["empty_framing_openings"]) >= 5:
        risks.append("empty_framing_openings")
    if len(opening_issues["suspended_pronoun_openings"]) >= 5:
        risks.append("suspended_pronoun_openings")
    if len(opening_issues["premature_judgment_openings"]) >= 5:
        risks.append("premature_judgment_openings")
    if opening_issues["slogan_endings"]:
        risks.append("slogan_paragraph_endings")
    if floating:
        risks.append("floating_sections")
    if len(review_like["source_parade_paragraphs"]) >= 4:
        risks.append("review_like_source_parade")
    if len(review_like["policy_pile_paragraphs"]) >= 3:
        risks.append("policy_pile_openings")
    if len(review_like["empty_countermeasure_sentences"]) >= 5:
        risks.append("empty_countermeasure_sentences")
    if sum(generic_verb_counts.values()) >= max(10, main_chars // 500):
        risks.append("generic_verb_overuse")
    if process_leak_counts:
        risks.append("internal_process_language_leak")
    if structure_issues["diagnostic_heading_leaks"]:
        risks.append("diagnostic_heading_leak")
    if structure_issues["workflow_heading_leaks"]:
        risks.append("workflow_heading_leak")
    if structure_issues["generic_structure_headings"]:
        risks.append("generic_structure_heading")
    if any("研究对象" in item["title"] for item in structure_issues["headings"]) and any(
        "概念" in item["title"] for item in structure_issues["headings"]
    ):
        risks.append("concept_section_overexposure")
    if sum(instructional_modal_counts.values()) >= max(18, main_chars // 550):
        risks.append("instructional_modal_overuse")
    bucket_pct = sentence_stats.get("bucket_pct", {})
    if bucket_pct.get("S", 0) + bucket_pct.get("M", 0) >= 75:
        risks.append("short_medium_heavy_expository_style")

    return {
        "paper": str(path),
        "main_text_cn_chars": main_chars,
        "heading_count": len(structure_issues["headings"]),
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
        "process_leak_counts": process_leak_counts,
        "instructional_modal_counts": instructional_modal_counts,
        "structure_heading_issues": structure_issues,
        "opening_issues": opening_issues,
        "review_like_patterns": review_like,
        "floating_paragraphs": floating,
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
