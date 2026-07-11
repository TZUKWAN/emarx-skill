# -*- coding: utf-8 -*-
"""
ai_trace_audit.py — 扫描论文中的 AI 痕迹特征。

本脚本只做机械扫描，输出统计信息和可疑位置，最终判断需由主模型阅读完成。

用法：
  python scripts/ai_trace_audit.py --paper paper.md --output ai-trace-audit.json
"""
import argparse
import json
import re
from pathlib import Path

# AI 腔高频词/短语
AI_PHRASES = [
    "不是",
    "而是",
    "并非",
    "既",
    "又",
    "一方面",
    "另一方面",
    "首先",
    "其次",
    "再次",
    "最后",
    "第一",
    "第二",
    "第三",
    "综上所述",
    "由此可见",
    "总而言之",
    "本文认为",
    "笔者认为",
    "文章认为",
    "有研究指出",
    "相关研究表明",
    "已有研究认为",
    "国内外学者普遍认为",
    "具有重要意义",
    "不容忽视",
    "值得深思",
    "不可或缺",
]

# 抽象名词（过度使用易被识别为 AI 腔）
ABSTRACT_NOUNS = [
    "维度",
    "视域",
    "场域",
    "逻辑",
    "机制",
    "路径",
    "意蕴",
    "范式",
    "理路",
    "向度",
    "进路",
    "图景",
]

# 夸张动词
HYPE_VERBS = [
    "重构",
    "重建",
    "重塑",
    "填补空白",
    "开创性",
    "颠覆",
    "彻底",
]

# 对称结构模式
SYMMETRIC_PATTERNS = [
    re.compile(r"不是[^，。；]+而是"),
    re.compile(r"并非[^，。；]+而是"),
    re.compile(r"既[^，。；]+又"),
    re.compile(r"一方面[^，。；]+另一方面"),
]

# 元话语模式（句子在解释论文自身而非论述对象）
METADISCOURSE_PATTERNS = [
    re.compile(r"本文认为"),
    re.compile(r"本文指出"),
    re.compile(r"本文旨在"),
    re.compile(r"本文试图"),
    re.compile(r"本文从.*展开分析"),
    re.compile(r"本文的核心观点是"),
    re.compile(r"本文的研究对象是"),
    re.compile(r"笔者认为"),
    re.compile(r"本研究认为"),
    re.compile(r"本研究旨在"),
    re.compile(r"文章认为"),
    re.compile(r"文章指出"),
    re.compile(r"有研究指出"),
    re.compile(r"已有研究认为"),
    re.compile(r"相关研究指出"),
    re.compile(r"相关研究表明"),
    re.compile(r"学者认为"),
    re.compile(r"国内外学者普遍认为"),
    re.compile(r"学术界认为"),
    re.compile(r"本文将从.*?(方面|角度|维度|层面).*?(展开|分析|论述|探讨|研究)"),
    re.compile(r"下文将"),
    re.compile(r"前文指出"),
    re.compile(r"前文已经说明"),
    re.compile(r"上文认为"),
    re.compile(r"如前文所述"),
    re.compile(r"综上所述[，。；]?"),
]


def count_occurrences(text: str, items: list[str]) -> dict:
    result = {}
    for item in items:
        count = text.count(item)
        if count > 0:
            result[item] = count
    return result


def find_pattern_lines(text: str, patterns: list[re.Pattern]) -> list[dict]:
    findings = []
    for i, line in enumerate(text.splitlines(), 1):
        for pat in patterns:
            for m in pat.finditer(line):
                findings.append({"line": i, "match": m.group(0)})
    return findings


def analyze(text: str) -> dict:
    total_chars = len(text)
    total_lines = text.count("\n") + 1

    ai_phrase_counts = count_occurrences(text, AI_PHRASES)
    abstract_noun_counts = count_occurrences(text, ABSTRACT_NOUNS)
    hype_verb_counts = count_occurrences(text, HYPE_VERBS)
    symmetric_findings = find_pattern_lines(text, SYMMETRIC_PATTERNS)
    metadiscourse_findings = find_pattern_lines(text, METADISCOURSE_PATTERNS)

    # 估算抽象名词密度（每千字出现次数）
    abstract_noun_total = sum(abstract_noun_counts.values())
    abstract_noun_density = (abstract_noun_total / (total_chars / 1000)) if total_chars else 0

    # 简单风险评分
    risk_score = 0
    risk_score += len(ai_phrase_counts) * 2
    risk_score += abstract_noun_density * 5
    risk_score += len(hype_verb_counts) * 3
    risk_score += len(symmetric_findings) * 2
    risk_score += len(metadiscourse_findings) * 4  # 元话语是硬性违规，权重较高

    risk_level = "low"
    if risk_score > 50:
        risk_level = "high"
    elif risk_score > 25:
        risk_level = "medium"

    return {
        "total_chars": total_chars,
        "total_lines": total_lines,
        "ai_phrase_counts": ai_phrase_counts,
        "abstract_noun_counts": abstract_noun_counts,
        "abstract_noun_density_per_1k": round(abstract_noun_density, 2),
        "hype_verb_counts": hype_verb_counts,
        "symmetric_structures": symmetric_findings,
        "metadiscourse": metadiscourse_findings,
        "risk_score": risk_score,
        "risk_level": risk_level,
    }


def main():
    parser = argparse.ArgumentParser(description="扫描论文中的 AI 痕迹特征")
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

    print(f"AI 痕迹审计完成。")
    print(f"风险等级: {result['risk_level']} (score={result['risk_score']})")
    print(f"元话语违规: {len(result['metadiscourse'])}")
    print(f"报告保存: {output_path}")


if __name__ == "__main__":
    main()
