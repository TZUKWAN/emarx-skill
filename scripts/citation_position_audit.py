# -*- coding: utf-8 -*-
"""
citation_position_audit.py — 检查论文中引用是否紧随使用句、是否堆在段落末尾。

规则：
  1. 引用编号 `[n]` 应紧随使用它的句子，而不是集中在段落末尾；
  2. 一个段落中出现多个引用编号时，它们应分布在段落的不同位置；
  3. 直接引用或转述他人观点的句子必须有引用标注；
  4. 输出可疑位置和统计信息。

用法：
  python scripts/citation_position_audit.py --paper paper.md --output citation-position-audit.json
"""
import argparse
import json
import re
from pathlib import Path

# 引用编号模式
CITATION_RE = re.compile(r"\[(\d+)\]")

# 句子切分（粗略按中文句号、问号、感叹号切分，保留引号内内容）
SENTENCE_RE = re.compile(r"([^。！？\n]+[。！？]?)")

# 可能包含他人观点/转述的指示词（需要引用）
ATTRIBUTION_MARKERS = [
    "指出",
    "认为",
    "强调",
    "提出",
    "主张",
    "表示",
    "说明",
    "论述",
    "阐释",
    "认为",
    "看来",
    "称",
    "所说",
]

# 直接引用标记
DIRECT_QUOTE_MARKERS = ["\u201c", "\u201d", "\u2018", "\u2019"]


def split_paragraphs(text: str) -> list[str]:
    """按空行切分段落。"""
    paragraphs = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
    return paragraphs


def split_sentences(paragraph: str) -> list[str]:
    """把段落切分成句子列表。"""
    sentences = SENTENCE_RE.findall(paragraph)
    return [s.strip() for s in sentences if s.strip()]


def analyze_paragraph(idx: int, paragraph: str) -> dict:
    """分析单个段落的引用分布。"""
    sentences = split_sentences(paragraph)
    total_sentences = len(sentences)

    cited_sentence_indices = []
    citation_counts = []
    for i, sent in enumerate(sentences):
        matches = CITATION_RE.findall(sent)
        count = len(matches)
        citation_counts.append(count)
        if count > 0:
            cited_sentence_indices.append(i)

    total_citations = sum(citation_counts)

    # 判断引用是否集中在段落末尾
    # 规则：如果 70% 以上的引用出现在最后 30% 的句子中，视为集中
    clustered_at_end = False
    if total_citations >= 2 and total_sentences >= 3:
        last_30_percent_start = max(0, int(total_sentences * 0.7))
        citations_in_last_30_percent = sum(
            citation_counts[i] for i in range(last_30_percent_start, total_sentences)
        )
        if citations_in_last_30_percent / total_citations >= 0.7:
            clustered_at_end = True

    # 判断是否存在应该引用但未引用的句子
    missing_citation_sentences = []
    for i, sent in enumerate(sentences):
        if CITATION_RE.search(sent):
            continue
        # 如果句子包含直接引号或转述标记，但没有引用，标记为可疑
        has_direct_quote = any(m in sent for m in DIRECT_QUOTE_MARKERS)
        has_attribution = any(marker in sent for marker in ATTRIBUTION_MARKERS)
        if has_direct_quote or has_attribution:
            # 排除一些常见的不需要引用的情况
            if not re.search(r"马克思|恩格斯|列宁|毛泽东|习近平|党中央|党的二十大", sent):
                missing_citation_sentences.append({
                    "sentence_index": i,
                    "text": sent[:120],
                    "reason": "direct_quote" if has_direct_quote else "attribution",
                })

    # 找出所有引用编号的位置（句子索引）
    citation_positions = []
    for i, sent in enumerate(sentences):
        for m in CITATION_RE.finditer(sent):
            citation_positions.append({
                "sentence_index": i,
                "citation": m.group(0),
                "sentence_preview": sent[:80],
            })

    return {
        "paragraph_index": idx,
        "paragraph_preview": paragraph[:120].replace("\n", " "),
        "total_sentences": total_sentences,
        "total_citations": total_citations,
        "cited_sentence_indices": cited_sentence_indices,
        "clustered_at_end": clustered_at_end,
        "missing_citation_sentences": missing_citation_sentences,
        "citation_positions": citation_positions,
    }


def analyze(text: str) -> dict:
    paragraphs = split_paragraphs(text)
    paragraph_results = []

    clustered_count = 0
    missing_count = 0

    for idx, para in enumerate(paragraphs):
        # 跳过标题、摘要、关键词、参考文献等非正文段落
        if para.startswith("#") or para.startswith("【") or para.startswith("["):
            continue
        # 跳过过短的段落
        if len(para) < 30:
            continue

        result = analyze_paragraph(idx, para)
        paragraph_results.append(result)
        if result["clustered_at_end"]:
            clustered_count += 1
        missing_count += len(result["missing_citation_sentences"])

    # 计算总体风险评分
    risk_score = clustered_count * 5 + missing_count * 3
    risk_level = "low"
    if risk_score > 20:
        risk_level = "high"
    elif risk_score > 10:
        risk_level = "medium"

    return {
        "total_paragraphs_analyzed": len(paragraph_results),
        "clustered_at_end_paragraphs": clustered_count,
        "missing_citation_sentences": missing_count,
        "risk_score": risk_score,
        "risk_level": risk_level,
        "paragraphs": paragraph_results,
    }


def main():
    parser = argparse.ArgumentParser(description="检查论文引用位置是否合规")
    parser.add_argument("--paper", required=True, help="输入论文 Markdown 文件路径")
    parser.add_argument("--output", required=True, help="输出 JSON 报告路径")
    args = parser.parse_args()

    paper_path = Path(args.paper)
    if not paper_path.exists():
        raise FileNotFoundError(f"找不到论文文件: {paper_path}")

    text = paper_path.read_text(encoding="utf-8")
    result = analyze(text)
    result["paper"] = str(paper_path)

    output_path = Path(args.output)
    output_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"引用位置审计完成。")
    print(f"风险等级: {result['risk_level']} (score={result['risk_score']})")
    print(f"分析段落数: {result['total_paragraphs_analyzed']}")
    print(f"引用堆在段尾的段落: {result['clustered_at_end_paragraphs']}")
    print(f"可能缺引用的句子: {result['missing_citation_sentences']}")
    print(f"报告保存: {output_path}")


if __name__ == "__main__":
    main()
