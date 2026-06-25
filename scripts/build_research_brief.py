#!/usr/bin/env python
"""Build a lightweight EMARX research brief from a source index."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


def terms(text: str) -> set[str]:
    found = set(re.findall(r"[\u4e00-\u9fff]{2,8}", text))
    found.update(re.findall(r"[A-Za-z][A-Za-z0-9_-]{2,}", text.lower()))
    return found


def score_record(topic_terms: set[str], record: dict) -> int:
    haystack = " ".join(
        [
            record.get("relative_path", ""),
            " ".join(record.get("keywords", [])),
            record.get("sample", ""),
        ]
    )
    source_terms = terms(haystack)
    return len(topic_terms & source_terms)


def brief(topic: str, sources: dict, topn: int) -> str:
    topic_terms = terms(topic)
    records = sources.get("records", [])
    ranked = sorted(
        ((score_record(topic_terms, r), r) for r in records if r.get("readable")),
        key=lambda item: item[0],
        reverse=True,
    )
    selected = [(score, r) for score, r in ranked if score > 0][:topn]

    lines: list[str] = []
    lines.append(f"# EMARX 研究简报")
    lines.append("")
    lines.append(f"## 题目")
    lines.append(topic)
    lines.append("")
    lines.append("## 本地资料匹配")
    if not selected:
        lines.append("未发现与题目有明显关键词重合的本地资料。需要人工指定资料，或进行联网检索补充。")
    else:
        for idx, (score, record) in enumerate(selected, 1):
            lines.append(f"{idx}. `{record['relative_path']}`")
            lines.append(f"   - 类型: {record['type']}")
            lines.append(f"   - 相关度分: {score}")
            lines.append(f"   - 关键词: {', '.join(record.get('keywords', [])[:10])}")
            sample = record.get("sample", "")[:220]
            if sample:
                lines.append(f"   - 样本文本: {sample}")
    lines.append("")
    lines.append("## 初步研究诊断")
    lines.append("- 核心问题: 待根据上述资料与用户目标进一步压缩为一个可论证问题。")
    lines.append("- 研究对象: 待界定为现象、机制、主体关系、传播结构或制度路径。")
    lines.append("- 概念边界: 至少需要界定 3-5 个核心概念，避免概念漂移。")
    lines.append("- 理论张力: 从资料中提取 A/B 张力，不要凭空套用。")
    lines.append("- 论证链条: 建议从材料共识、理论缺口、机制解释、路径闭环展开。")
    lines.append("")
    lines.append("## 可能创新点")
    lines.append("- 选题创新: 待判断是否只是旧题新词。")
    lines.append("- 视角创新: 待判断是否有新的观察角度。")
    lines.append("- 概念创新: 待判断是否有清晰概念边界。")
    lines.append("- 机制创新: 待判断是否解释了既有研究未说清的运行逻辑。")
    lines.append("- 路径创新: 待判断是否与前文问题逐项对应。")
    lines.append("- 表达创新: 待在不牺牲学术准确性的前提下形成大家风范。")
    lines.append("")
    lines.append("## 资料缺口与事实核查")
    lines.append("- 若涉及最新政策、数据、法规、机构事实、真实案例或文献出处，需要联网或原文核验。")
    lines.append("- 不得把本简报中的关键词重合当成事实证明。")
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--topic", required=True)
    parser.add_argument("--sources", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--topn", type=int, default=8)
    args = parser.parse_args()

    sources = json.loads(Path(args.sources).read_text(encoding="utf-8"))
    text = brief(args.topic, sources, args.topn)
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(text, encoding="utf-8")
    print(output)


if __name__ == "__main__":
    main()
