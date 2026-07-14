# -*- coding: utf-8 -*-
"""
emarx_literature_gap.py — EMARX 文献缺口诊断与 CNKI 自动触发脚本。

扫描工作空间已有文献，评估其与论文题目的相关度；若文献不足，自动调用内置 CNKI 模块搜索并生成 EMARX 可用产物。

用法：
  python scripts/emarx_literature_gap.py \
    --workspace workspace \
    --topic "生成式人工智能 国际传播" \
    --min-local-sources 10 \
    --cnki-pages 3 \
    --top-k 10

输出：
  - workspace/literature-gap-report.json
  - workspace/cnki_results.json（如触发 CNKI）
  - workspace/research-brief.md（如触发 CNKI）
  - workspace/anchor-papers.md（如触发 CNKI）
  - workspace/sources.json（如触发 CNKI）
"""
import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

# 在脚本目录中查找 cnki 模块
sys.path.insert(0, str(Path(__file__).resolve().parent))
from emarx_env import ensure_venv_and_reexec
ensure_venv_and_reexec()
from cnki.env_check import ensure_ready


def collect_local_sources(workspace: Path) -> list[dict]:
    """扫描工作空间中的潜在文献文件（PDF、MD、TXT）。"""
    sources = []
    for ext in ("*.pdf", "*.md", "*.txt"):
        for f in workspace.rglob(ext):
            # 排除技能文件和报告文件
            if ".codex" in str(f) or "reports_archive" in str(f) or "reports_cleaned" in str(f):
                continue
            if f.name in ("SKILL.md", "README.md", "research-brief.md", "anchor-papers.md"):
                continue
            sources.append({
                "path": str(f.relative_to(workspace)),
                "filename": f.name,
                "type": f.suffix.lower(),
            })
    return sources


def estimate_relevance(sources: list[dict], topic: str) -> list[dict]:
    """用简单关键词匹配估算文献与题目的相关度。"""
    topic_keywords = set(re.findall(r"[\u4e00-\u9fa5a-zA-Z0-9]+", topic.lower()))
    # 过滤掉过短或无意义词
    topic_keywords = {k for k in topic_keywords if len(k) >= 2}

    for s in sources:
        filename_lower = s["filename"].lower()
        matched = [k for k in topic_keywords if k in filename_lower]
        s["matched_keywords"] = matched
        s["relevance_score"] = len(matched)

    return sorted(sources, key=lambda x: x["relevance_score"], reverse=True)


def evaluate_gap(sources: list[dict], min_local_sources: int, min_relevant_sources: int) -> dict:
    """评估文献缺口。"""
    total = len(sources)
    relevant = [s for s in sources if s["relevance_score"] > 0]
    high_relevant = [s for s in sources if s["relevance_score"] >= 2]

    needs_cnki = False
    reasons = []

    if total < min_local_sources:
        needs_cnki = True
        reasons.append(f"本地文献总数 {total} 少于阈值 {min_local_sources}")

    if len(relevant) < min_relevant_sources:
        needs_cnki = True
        reasons.append(f"相关文献数 {len(relevant)} 少于阈值 {min_relevant_sources}")

    if len(high_relevant) < 3:
        needs_cnki = True
        reasons.append(f"高度相关文献数 {len(high_relevant)} 不足 3 篇")

    return {
        "total_local_sources": total,
        "relevant_sources": len(relevant),
        "high_relevant_sources": len(high_relevant),
        "needs_cnki": needs_cnki,
        "reasons": reasons,
    }


def trigger_cnki_search(workspace: Path, topic: str, pages: int, top_k: int) -> Path:
    """调用内置 CNKI CLI 搜索。"""
    cli = Path(__file__).resolve().parent / "cnki_cli.py"
    results_path = workspace / "cnki_results.json"

    cmd = [
        sys.executable,
        str(cli),
        "search",
        topic,
        "--pages", str(pages),
        "--output", str(results_path),
    ]

    print(f"触发 CNKI 搜索: {' '.join(cmd)}")
    result = subprocess.run(cmd)
    if result.returncode != 0:
        raise RuntimeError("CNKI 搜索失败")

    return results_path


def trigger_cnki_import(workspace: Path, results_path: Path, top_k: int) -> None:
    """调用内置 CNKI CLI 导入。"""
    cli = Path(__file__).resolve().parent / "cnki_cli.py"
    summaries_dir = workspace / "summaries"

    cmd = [
        sys.executable,
        str(cli),
        "import",
        "--results", str(results_path),
        "--output-dir", str(workspace),
        "--top-k", str(top_k),
    ]
    if summaries_dir.exists():
        cmd.extend(["--summaries-dir", str(summaries_dir)])

    print(f"触发 CNKI 导入: {' '.join(cmd)}")
    result = subprocess.run(cmd)
    if result.returncode != 0:
        raise RuntimeError("CNKI 导入失败")


def generate_gap_report(gap: dict, topic: str, top_sources: list[dict]) -> dict:
    """生成文献缺口诊断报告。"""
    return {
        "topic": topic,
        "evaluation": gap,
        "top_local_sources": top_sources[:10],
        "recommendation": "建议调用 CNKI 补充文献" if gap["needs_cnki"] else "本地文献充足，可直接进入锚定精读",
    }


def main():
    parser = argparse.ArgumentParser(description="EMARX 文献缺口诊断与 CNKI 自动触发")
    parser.add_argument("--workspace", required=True, help="EMARX 工作空间目录")
    parser.add_argument("--topic", required=True, help="论文题目或核心主题")
    parser.add_argument("--min-local-sources", type=int, default=10, help="本地文献数量阈值")
    parser.add_argument("--min-relevant-sources", type=int, default=3, help="相关文献数量阈值")
    parser.add_argument("--cnki-pages", type=int, default=3, help="触发 CNKI 时的翻页数")
    parser.add_argument("--top-k", type=int, default=10, help="CNKI 入选精读数量")
    parser.add_argument("--skip-cnki", action="store_true", help="只诊断缺口，不触发 CNKI")
    args = parser.parse_args()

    workspace = Path(args.workspace)
    workspace.mkdir(parents=True, exist_ok=True)

    sources = collect_local_sources(workspace)
    sources = estimate_relevance(sources, args.topic)
    gap = evaluate_gap(sources, args.min_local_sources, args.min_relevant_sources)

    report = generate_gap_report(gap, args.topic, sources)
    report_path = workspace / "literature-gap-report.json"
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"文献缺口诊断完成：{report_path}")
    print(f"  本地文献总数：{gap['total_local_sources']}")
    print(f"  相关文献数：{gap['relevant_sources']}")
    print(f"  高度相关文献数：{gap['high_relevant_sources']}")
    print(f"  是否需要 CNKI：{'是' if gap['needs_cnki'] else '否'}")
    if gap["reasons"]:
        for r in gap["reasons"]:
            print(f"  - {r}")

    if gap["needs_cnki"] and not args.skip_cnki:
        # 自动确保 CNKI 环境就绪
        if not ensure_ready(auto=True):
            print("CNKI 环境准备失败，请运行：python scripts/setup_emarx.py", file=sys.stderr)
            sys.exit(1)
        try:
            results_path = trigger_cnki_search(workspace, args.topic, args.cnki_pages, args.top_k)
            trigger_cnki_import(workspace, results_path, args.top_k)
            print("CNKI 补充完成，已生成 research-brief.md、anchor-papers.md、sources.json")
        except Exception as exc:
            print(f"CNKI 调用失败：{exc}", file=sys.stderr)
            print("请检查是否已安装依赖：pip install -r scripts/cnki/requirements.txt && playwright install chromium", file=sys.stderr)
            sys.exit(1)


if __name__ == "__main__":
    main()
