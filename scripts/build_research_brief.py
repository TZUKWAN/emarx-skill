#!/usr/bin/env python
"""Build an evidence-only source navigation brief from a workspace index.

The brief deliberately makes no research diagnosis. It identifies files that
the main model must open and read before forming questions or arguments.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


DOMAIN_TERMS = [
    "生成式人工智能", "人工智能", "中华文化", "国际传播", "文化传播",
    "文化主体性", "思想政治教育", "文化记忆", "国家认同", "意识形态",
    "数字文化", "技术", "风险", "机制", "逻辑", "路径",
]


def topic_terms(text: str) -> list[str]:
    terms = [term for term in DOMAIN_TERMS if term in text]
    chunks = re.findall(r"[\u4e00-\u9fff]{2,12}|[A-Za-z][A-Za-z0-9_-]{2,}", text)
    for chunk in chunks:
        if chunk not in terms:
            terms.append(chunk)
        if len(chunk) >= 6 and re.fullmatch(r"[\u4e00-\u9fff]+", chunk):
            for width in (4, 3):
                for index in range(len(chunk) - width + 1):
                    part = chunk[index : index + width]
                    if part not in terms:
                        terms.append(part)
    return terms


def score_record(terms: list[str], record: dict) -> tuple[int, list[str]]:
    name = record.get("relative_path", "")
    sample = record.get("sample", "")
    hits: list[str] = []
    score = 0
    for term in terms:
        if term in name:
            score += 8 + len(term)
            hits.append(term)
        occurrences = sample.count(term)
        if occurrences:
            score += min(8, occurrences) + len(term)
            if term not in hits:
                hits.append(term)
    return score, hits


def build(topic: str, sources: dict, topn: int) -> tuple[str, dict]:
    terms = topic_terms(topic)
    ranked = []
    for record in sources.get("records", []):
        if not record.get("readable") or record.get("category") == "generated_or_internal":
            continue
        score, hits = score_record(terms, record)
        if score > 0:
            ranked.append((score, hits, record))
    ranked.sort(key=lambda item: (-item[0], item[2].get("relative_path", "")))
    selected = ranked[:topn]

    result = {
        "topic": topic,
        "source_index": sources.get("root"),
        "readable_source_count": sum(bool(record.get("readable")) for record in sources.get("records", [])),
        "candidate_count": len(ranked),
        "selected_count": len(selected),
        "selected": [
            {
                "rank": rank,
                "score": score,
                "hits": hits[:16],
                "path": record.get("path"),
                "relative_path": record.get("relative_path"),
                "type": record.get("type"),
                "source_sha256": record.get("source_sha256"),
                "sample": record.get("sample", "")[:500],
            }
            for rank, (score, hits, record) in enumerate(selected, 1)
        ],
        "boundary": "关键词匹配只用于导航，不构成相关性、论点、创新或事实证明。必须打开候选原文后再判断。",
    }

    lines = [
        f"# 题目资料导航：{topic}",
        "",
        f"- 可读资料：{result['readable_source_count']}",
        f"- 有关键词交集的候选：{result['candidate_count']}",
        f"- 当前导航条目：{result['selected_count']}",
        "- 本文件只提供原文入口。不得根据关键词重合直接形成研究问题、结构、创新点或正文。",
        "",
        "## 候选资料",
        "",
    ]
    if not selected:
        lines.append("未发现可读且有关键词交集的本地资料。需要人工复核资料目录，并在必要时联网补充。")
    for item in result["selected"]:
        lines.extend(
            [
                f"### {item['rank']}. {item['relative_path']}",
                "",
                f"- 文件：`{item['path']}`",
                f"- 文件哈希：`{item['source_sha256'] or '未记录'}`",
                f"- 导航分：{item['score']}",
                f"- 命中词：{'、'.join(item['hits'])}",
                f"- 抽取片段：{item['sample']}",
                "- 后续动作：打开原文，核对摘要、引言、标题层级、主体与结论；片段不能替代全文。",
                "",
            ]
        )
    return "\n".join(lines).rstrip() + "\n", result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--topic", required=True)
    parser.add_argument("--sources", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--output-json")
    parser.add_argument("--topn", type=int, default=12)
    args = parser.parse_args()

    sources = json.loads(Path(args.sources).read_text(encoding="utf-8"))
    markdown, result = build(args.topic, sources, args.topn)
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(markdown, encoding="utf-8")
    if args.output_json:
        json_path = Path(args.output_json)
        json_path.parent.mkdir(parents=True, exist_ok=True)
        json_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(output)


if __name__ == "__main__":
    main()
