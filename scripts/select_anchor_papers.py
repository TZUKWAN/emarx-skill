from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


CN_RE = re.compile(r"[\u4e00-\u9fff]")
DOMAIN_TERMS = [
    "生成式人工智能",
    "人工智能",
    "中华文化",
    "国际传播",
    "文化国际传播",
    "文化主体性",
    "习近平文化思想",
    "中国哲学社会科学",
    "自主知识体系",
    "微短剧",
    "数字文化",
    "文化出海",
    "机遇",
    "挑战",
    "风险",
    "路径",
    "机制",
    "机理",
    "语境",
]


def cn_terms(text: str) -> list[str]:
    terms = [term for term in DOMAIN_TERMS if term in text]
    words = re.findall(r"[\u4e00-\u9fffA-Za-z0-9]{2,}", text)
    for word in words:
        if len(CN_RE.findall(word)) >= 2:
            terms.append(word)
            if len(word) >= 6:
                terms.extend(word[i:i + 3] for i in range(len(word) - 2) if len(CN_RE.findall(word[i:i + 3])) == 3)
    seen = []
    for term in terms:
        if term not in seen:
            seen.append(term)
    return seen


def role_guess(name: str, text: str) -> str:
    if any(term in name for term in ["风险", "困境", "挑战", "安全", "危机"]):
        return "问题诊断/风险分析"
    if any(term in name for term in ["路径", "策略", "进路", "对策", "范式"]):
        return "路径回应/实践转化"
    if any(term in name for term in ["机制", "机理", "逻辑", "结构", "生成"]):
        return "机制解释/结构推进"
    if any(term in name for term in ["传播", "出海", "国际", "叙事", "平台"]):
        return "传播对象/案例语境"
    if any(term in name for term in ["理论", "马克思", "主体性", "现代性", "概念"]):
        return "理论起点/概念资源"
    if any(term in text for term in ["风险", "困境", "挑战", "安全", "危机"]):
        return "问题诊断/风险分析"
    if any(term in text for term in ["路径", "策略", "进路", "对策", "实践"]):
        return "路径回应/实践转化"
    if any(term in text for term in ["机制", "机理", "逻辑", "结构", "生成"]):
        return "机制解释/结构推进"
    if any(term in text for term in ["传播", "出海", "国际", "叙事", "平台"]):
        return "传播对象/案例语境"
    if any(term in text for term in ["理论", "马克思", "主体性", "现代性", "概念"]):
        return "理论起点/概念资源"
    return "结构与文风参照"


def score_text(topic_terms: list[str], name: str, extra_text: str = "") -> tuple[int, list[str]]:
    haystack_title = name
    haystack = name + "\n" + extra_text[:6000]
    hits = []
    score = 0
    for term in topic_terms:
        if term in haystack_title:
            score += 8 + len(term)
            hits.append(term)
        count = haystack.count(term)
        if count:
            score += min(10, count) + len(term)
            if term not in hits:
                hits.append(term)
    display_hits = [
        term for term in hits
        if term in DOMAIN_TERMS or len(term) >= 4
    ]
    return score, display_hits[:12]


def load_summary_cache(summary_path: str | None) -> dict[str, dict]:
    if not summary_path:
        return {}
    path = Path(summary_path)
    if not path.exists():
        return {}
    data = json.loads(path.read_text(encoding="utf-8"))
    cache = {}
    for item in data.get("reports", []):
        source = item.get("file")
        if source:
            cache[str(Path(source).resolve()).lower()] = item
    return cache


def normalized_text(text: str) -> str:
    return re.sub(r"[^\u4e00-\u9fffA-Za-z0-9]+", "", text).lower()


def workspace_candidates(root: Path, cache: dict[str, dict], topic: str) -> list[dict]:
    exts = {".pdf", ".docx", ".doc", ".md", ".txt", ".html", ".htm"}
    generated_name_patterns = [
        "EMARX",
        "重写版",
        "最新版",
        "最新",
        "给我写",
        "基于工作空间",
        "anchor-test",
        "bad-draft-audit",
        "scholarliness-audit",
    ]
    normalized_topic = normalized_text(topic)
    candidates = []
    for path in root.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in exts:
            continue
        lower_parts = [part.lower() for part in path.parts]
        if any(part.startswith(".") for part in path.parts):
            continue
        if any(part in {".codex", ".sophia", "generated_documents", "__pycache__"} for part in lower_parts):
            continue
        if any(pattern.lower() in path.name.lower() for pattern in generated_name_patterns):
            continue
        normalized_name = normalized_text(path.stem)
        if path.suffix.lower() != ".pdf" and normalized_topic and normalized_topic in normalized_name:
            continue
        resolved = str(path.resolve()).lower()
        cached = cache.get(resolved)
        candidates.append({
            "name": path.name,
            "file": str(path),
            "report": cached.get("report") if cached else "",
            "whole_style_label": cached.get("whole_style_label", "") if cached else "",
            "attention_points": cached.get("attention_points", []) if cached else [],
            "cache_status": "matched_report_cache" if cached else "live_workspace_file",
        })
    return candidates


def main() -> int:
    parser = argparse.ArgumentParser(description="Select 3-5 anchor papers from the user's current workspace, optionally using deconstruction reports only as cache.")
    parser.add_argument("--topic", required=True)
    parser.add_argument("--workspace-root", help="current user workspace to scan for real paper files")
    parser.add_argument("--summary", help="optional article_deconstruction summary.json cache")
    parser.add_argument("--output", required=True, help="markdown output path")
    parser.add_argument("--top-k", type=int, default=5)
    args = parser.parse_args()

    topic_terms = cn_terms(args.topic)
    cache = load_summary_cache(args.summary)
    if args.workspace_root:
        candidates = workspace_candidates(Path(args.workspace_root), cache, args.topic)
        source_mode = "current_workspace"
    elif args.summary:
        data = json.loads(Path(args.summary).read_text(encoding="utf-8"))
        candidates = []
        for item in data["reports"]:
            candidates.append({
                "name": item["name"],
                "file": item["file"],
                "report": item["report"],
                "whole_style_label": item.get("whole_style_label", ""),
                "attention_points": item.get("attention_points", []),
                "cache_status": "report_only_legacy_mode",
            })
        source_mode = "report_cache_only"
    else:
        raise SystemExit("Either --workspace-root or --summary is required.")

    ranked = []
    for item in candidates:
        text = ""
        report_path = Path(item["report"]) if item.get("report") else None
        if report_path and report_path.exists():
            text = report_path.read_text(encoding="utf-8", errors="replace")
        score, hits = score_text(topic_terms, item["name"], text)
        if score > 0:
            ranked.append((score, hits, item, text))
    ranked.sort(key=lambda row: row[0], reverse=True)
    selected = ranked[: max(1, args.top_k)]

    lines = [
        f"# 主题锚定论文选择：{args.topic}",
        "",
        "## 使用说明",
        "",
        f"- 选择来源：{source_mode}",
        "- 本报告用于写作前的三至五篇锚定。锚定对象必须是用户当次工作空间中的真实论文文件。",
        "- 既有拆解报告只能作为缓存和索引，不能替代对锚定论文原文的即时读取与拆解。",
        "- 锚定论文只能作为结构、逻辑、材料和文风参照，不能把原文拼贴为最终论文。若后续生成影子重组稿，必须保留来源标记，并在正式写作阶段逐段重写、改造和引用。",
        "",
        "## 锚定结果",
        "",
    ]
    for idx, (score, hits, item, text) in enumerate(selected, 1):
        role = role_guess(item["name"], text[:2000])
        lines.extend([
            f"### {idx}. {item['name']}",
            "",
            f"- 匹配分：{score}",
            f"- 命中词：{'、'.join(hits) if hits else '无'}",
            f"- 建议角色：{role}",
            f"- 缓存状态：{item.get('cache_status', '')}",
            f"- 拆解报告缓存：`{item['report']}`" if item.get("report") else "- 拆解报告缓存：无，需对该工作空间文件即时拆解",
            f"- 原文件：`{item['file']}`",
            f"- 文风标签：{item.get('whole_style_label', '')}",
            f"- 注意问题：{'；'.join(item.get('attention_points', []))}",
            "",
        ])
    lines.extend([
        "## 下一步",
        "",
        "1. 打开上述原文件，逐篇读取锚定论文的摘要、引言、主体、结论和标题层级。",
        "2. 对锚定论文做即时拆解，确认每篇可借鉴的逻辑、文风、写作手法和论证方式。",
        "3. 建立影子重组稿，只记录段落功能、材料来源和论证动作，不作为最终正文交付。",
        "4. 对影子重组稿做逻辑拆解，形成新论文的详细大纲。",
        "5. 按大纲逐段写作、逐段审查、逐段改写，不能一次生成多个段落后再泛泛润色。",
        "",
    ])
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("\n".join(lines), encoding="utf-8")
    print(json.dumps({"selected": len(selected), "output": str(output)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
