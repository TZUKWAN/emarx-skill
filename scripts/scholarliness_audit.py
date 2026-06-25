from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from pathlib import Path


CN_RE = re.compile(r"[\u4e00-\u9fff]")
REF_HEADING_RE = re.compile(r"(?m)^#{0,6}\s*参考文献\s*$")
PARA_SPLIT_RE = re.compile(r"\n\s*\n")

THEORY_MARKERS = [
    "理论",
    "学科",
    "领域",
    "视角",
    "范式",
    "框架",
    "问题意识",
    "研究脉络",
    "学术",
]

CONCEPT_MARKERS = [
    "概念",
    "范畴",
    "边界",
    "内涵",
    "外延",
    "区别",
    "区分",
    "限定",
    "指向",
]

LITERATURE_DIALOGUE_MARKERS = [
    "已有研究",
    "现有研究",
    "学界",
    "研究指出",
    "研究认为",
    "研究表明",
    "文献",
    "观点",
    "讨论",
]

CRITIQUE_MARKERS = [
    "忽视",
    "不足",
    "局限",
    "偏重",
    "缺乏",
    "尚未",
    "有待",
    "未能",
]

ABSTRACTION_MARKERS = [
    "机制",
    "关系",
    "结构",
    "逻辑",
    "生成",
    "转化",
    "抽象",
    "一般",
    "普遍",
]

MATERIAL_MARKERS = [
    "例如",
    "案例",
    "数据显示",
    "报告",
    "政策",
    "文本",
    "实践",
    "平台",
    "机构",
    "调查",
    "历史",
]

EMPTY_ACADEMIC_PHRASES = [
    "众所周知",
    "不言而喻",
    "笔者认为",
    "具有重要意义",
    "理论意义和现实意义",
    "随着时代的发展",
]


def cn_len(text: str) -> int:
    return len(CN_RE.findall(text))


def split_body_and_refs(text: str) -> tuple[str, str]:
    match = REF_HEADING_RE.search(text)
    if not match:
        return text, ""
    return text[: match.start()], text[match.start() :]


def count_markers(text: str, markers: list[str]) -> dict[str, int]:
    return {marker: text.count(marker) for marker in markers if text.count(marker)}


def paragraph_actions(body: str) -> dict[str, int]:
    actions: Counter[str] = Counter()
    for para in [p.strip() for p in PARA_SPLIT_RE.split(body) if p.strip()]:
        if para.startswith("#"):
            continue
        if any(marker in para for marker in CONCEPT_MARKERS):
            actions["concept_work"] += 1
        if any(marker in para for marker in LITERATURE_DIALOGUE_MARKERS) or re.search(r"\[\d+\]", para):
            actions["literature_or_citation"] += 1
        if any(marker in para for marker in CRITIQUE_MARKERS):
            actions["critique"] += 1
        if any(marker in para for marker in MATERIAL_MARKERS):
            actions["material_anchor"] += 1
        if any(marker in para for marker in ABSTRACTION_MARKERS):
            actions["abstraction"] += 1
    return dict(actions)


def audit(path: Path) -> dict:
    text = path.read_text(encoding="utf-8-sig", errors="replace")
    body, _refs = split_body_and_refs(text)
    main_chars = cn_len(body)
    paras = [p.strip() for p in PARA_SPLIT_RE.split(body) if p.strip() and not p.strip().startswith("#")]

    marker_groups = {
        "theory_positioning": count_markers(body, THEORY_MARKERS),
        "concept_work": count_markers(body, CONCEPT_MARKERS),
        "literature_dialogue": count_markers(body, LITERATURE_DIALOGUE_MARKERS),
        "critique": count_markers(body, CRITIQUE_MARKERS),
        "abstraction": count_markers(body, ABSTRACTION_MARKERS),
        "material_anchor": count_markers(body, MATERIAL_MARKERS),
        "empty_academic_phrases": count_markers(body, EMPTY_ACADEMIC_PHRASES),
    }

    action_counts = paragraph_actions(body)
    risks = []
    if sum(marker_groups["theory_positioning"].values()) < 5:
        risks.append("weak_academic_map_signal")
    if sum(marker_groups["concept_work"].values()) < 8:
        risks.append("weak_concept_boundary_signal")
    if sum(marker_groups["literature_dialogue"].values()) < 6:
        risks.append("weak_literature_dialogue_signal")
    if sum(marker_groups["critique"].values()) < 3:
        risks.append("weak_measured_critique_signal")
    if sum(marker_groups["abstraction"].values()) < 10:
        risks.append("weak_abstraction_signal")
    if sum(marker_groups["material_anchor"].values()) < 8:
        risks.append("weak_material_anchor_signal")
    if marker_groups["empty_academic_phrases"]:
        risks.append("empty_academic_phrase_risk")
    if action_counts.get("concept_work", 0) < max(2, len(paras) // 10):
        risks.append("few_paragraphs_with_concept_work")
    if action_counts.get("material_anchor", 0) < max(2, len(paras) // 12):
        risks.append("few_paragraphs_with_material_anchor")

    return {
        "paper": str(path),
        "main_text_cn_chars": main_chars,
        "paragraph_count": len(paras),
        "marker_groups": marker_groups,
        "paragraph_action_counts": action_counts,
        "risks": risks,
        "ok": not risks,
        "note": "Diagnostic evidence only. Main model must read the paper and judge scholarliness from argument, sources, and prose.",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Diagnose visible scholarliness signals in a Chinese academic draft.")
    parser.add_argument("--paper", required=True, help="Markdown paper path.")
    parser.add_argument("--output", required=True, help="JSON output path.")
    args = parser.parse_args()

    report = audit(Path(args.paper))
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(str(output))
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
