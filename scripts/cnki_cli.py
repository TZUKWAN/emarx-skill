# -*- coding: utf-8 -*-
r"""
cnki_cli.py — EMARX 内置的 CNKI 集成命令入口。

直接调用 scripts/cnki/ 下的 CNKI Control 核心模块，无需依赖外部 D:\CNKICONTROL 项目。

用法：
  # 搜索并保存为 EMARX 格式
  python scripts/cnki_cli.py search "生成式人工智能 国际传播" --pages 3 --output workspace/cnki_results.json

  # 批量采集摘要
  python scripts/cnki_cli.py read-batch --results workspace/cnki_results.json --output-dir workspace/summaries --limit 10

  # 导入 EMARX 工作空间
  python scripts/cnki_cli.py import --results workspace/cnki_results.json --summaries-dir workspace/summaries --output-dir workspace --top-k 10
"""
import argparse
import json
import sys
from pathlib import Path

# 把 scripts/ 加入路径，使 import cnki 可工作
sys.path.insert(0, str(Path(__file__).resolve().parent))

from cnki import config, reader, search, summarizer, utils
from cnki.browser import managed_browser
from cnki.citation import format_gb7714


def normalize_paper(raw: dict) -> dict:
    """把 CNKI Control 单条结果转换为 EMARX 标准格式。"""
    authors = raw.get("authors", [])
    if isinstance(authors, list):
        authors_str = ", ".join(authors)
    else:
        authors_str = str(authors)

    return {
        "index": raw.get("index", 0),
        "title": raw.get("title", "").strip(),
        "authors": authors_str,
        "source": raw.get("source", "").strip(),
        "year": str(raw.get("year", "")).strip(),
        "issue": str(raw.get("issue", "")).strip(),
        "pages": raw.get("pages", "").strip(),
        "cited_count": str(raw.get("cited_count", "")).strip(),
        "abstract": raw.get("abstract", "").strip(),
        "abstract_url": raw.get("detail_url", raw.get("url", "")).strip(),
        "download_url": raw.get("download_url", "").strip(),
        "gb_reference": format_gb7714(raw) if raw.get("title") else "",
        "core": raw.get("core", True),
        "cssci": raw.get("cssci", True),
    }


def cmd_search(args):
    """搜索 CNKI 并输出 EMARX 格式。"""
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    delay_min = config.DELAY_MIN
    delay_max = config.DELAY_MAX
    if args.slow:
        delay_min, delay_max = 5.0, 12.0

    with managed_browser(headless=not args.no_headless) as bm:
        results = search.search(
            bm.page,
            args.query,
            max_pages=args.pages,
            max_results=args.max_results,
        )

    emarx_results = {
        "query": args.query,
        "total": len(results),
        "source": "cnki",
        "filters": {"core": config.CNKI_FILTER_CORE, "cssci": config.CNKI_FILTER_CSSCI},
        "papers": [normalize_paper(r) for r in results],
    }

    output_path.write_text(json.dumps(emarx_results, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"搜索完成，共 {len(results)} 条结果，保存到 {output_path}")

    if args.slow:
        utils.random_delay(delay_min, delay_max)


def _derive_output_name(article: dict) -> str:
    """生成安全的摘要文件名。"""
    title = utils.sanitize_filename(article.get("title", "article"))
    authors = article.get("authors", [])
    author_part = utils.sanitize_filename(authors[0]) if authors else ""
    if author_part:
        return f"{title}_{author_part}.txt"
    return f"{title}.txt"


def _build_summary_text(article: dict) -> str:
    """组合 GB/T 7714 引用和结构化摘要。"""
    citation = format_gb7714(article)
    summary = summarizer.summarize(
        article.get("text", ""),
        is_abstract_only=article.get("text_type") == "abstract",
    )
    lines = [
        f"标题：{article.get('title', '')}",
        f"作者：{', '.join(article.get('authors', []))}",
        f"来源：{article.get('source', '')}",
        f"年/期：{article.get('year', '')}({article.get('issue', '')})",
        f"页码：{article.get('pages', '')}",
        f"URL：{article.get('url', '')}",
        "",
        "【GB/T 7714 引用】",
        citation,
        "",
        summary,
    ]
    return "\n".join(lines)


def cmd_read_batch(args):
    """批量读取 CNKI 详情页并保存摘要。"""
    results_path = Path(args.results)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    results = search.load_results(results_path)
    if not results:
        print("没有搜索结果。", file=sys.stderr)
        sys.exit(1)

    start = args.start
    end = args.end if args.end is not None else len(results)
    batch = results[start:end]
    if args.limit is not None:
        batch = batch[:args.limit]

    delay_min = config.DELAY_MIN
    delay_max = config.DELAY_MAX
    if args.slow:
        delay_min, delay_max = 5.0, 12.0

    with managed_browser(headless=not args.no_headless) as bm:
        for idx, item in enumerate(batch, start=start):
            detail_url = item.get("detail_url")
            if not detail_url:
                print(f"[{idx}] 跳过：无详情页 URL", file=sys.stderr)
                continue
            print(f"[{idx}] 读取：{item.get('title', detail_url)}")
            try:
                article = reader.read_article(
                    bm.page,
                    detail_url,
                    expected_title=item.get("title", ""),
                    expected_source=item.get("source", ""),
                    expected_year=item.get("year", ""),
                )
                out_name = _derive_output_name(article)
                out_path = output_dir / out_name
                if out_path.exists():
                    out_path = output_dir / f"{out_path.stem}_{idx}{out_path.suffix}"
                out_path.write_text(_build_summary_text(article), encoding="utf-8")
                print(f"[{idx}] 已保存：{out_path}")
                if article.get("warnings"):
                    for warning in article["warnings"]:
                        print(f"[{idx}] 警告：{warning}", file=sys.stderr)
                if args.slow:
                    utils.random_delay(delay_min, delay_max)
            except Exception as exc:
                print(f"[{idx}] 失败：{exc}", file=sys.stderr)
                continue

    print(f"批量读取完成，摘要保存到 {output_dir}")


def cmd_import(args):
    """把 CNKI 搜索结果导入 EMARX 工作空间。"""
    results_path = Path(args.results)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    summaries_dir = Path(args.summaries_dir) if args.summaries_dir else None

    data = json.loads(results_path.read_text(encoding="utf-8"))
    papers = data.get("papers", [])

    if summaries_dir and summaries_dir.exists():
        for p in papers:
            safe_title = utils.sanitize_filename(p["title"])[:40]
            for f in summaries_dir.iterdir():
                if safe_title in f.name or p["title"][:20] in f.name:
                    p["summary_text"] = f.read_text(encoding="utf-8")
                    break

    selected = papers[:args.top_k]

    # 生成研究简报
    brief_lines = [
        "# CNKI 研究简报",
        "",
        f"检索来源：中国知网（北大核心 + CSSCI）",
        f"结果总数：{len(papers)}",
        f"入选精读：{len(selected)}",
        "",
        "## 一、现有研究主题分布",
        "",
        "（主模型应根据标题和摘要进行主题聚类，此处仅列出候选论文）",
        "",
    ]
    for i, p in enumerate(selected, 1):
        brief_lines.extend([
            f"### {i}. {p['title']}",
            "",
            f"- 作者：{p['authors']}",
            f"- 来源：{p['source']} {p['year']}年第{p['issue']}期" if p["issue"] else f"- 来源：{p['source']} {p['year']}",
            f"- 被引：{p['cited_count']}",
            f"- 详情页：{p['abstract_url']}",
            "",
            "**摘要**：",
            "",
            p["abstract"] or "（未采集到摘要）",
            "",
        ])
    brief_lines.extend([
        "## 二、研究缺口与选题方向",
        "",
        "（主模型根据以上文献提炼：已有研究能解释什么、不能解释什么、本文入口在哪里）",
        "",
    ])

    # 生成候选锚定论文
    anchor_lines = [
        "# 候选锚定论文",
        "",
        "以下论文根据 CNKI 搜索结果按相关性、被引量、期刊级别初步筛选。正式锚定前需回原文精读。",
        "",
    ]
    for i, p in enumerate(selected, 1):
        anchor_lines.extend([
            f"## {i}. {p['title']}",
            "",
            f"- 作者：{p['authors']}",
            f"- 来源：{p['source']} {p['year']}年第{p['issue']}期" if p["issue"] else f"- 来源：{p['source']} {p['year']}",
            f"- 被引：{p['cited_count']}",
            f"- 详情页：{p['abstract_url']}",
            f"- GB/T 7714：{p.get('gb_reference', '待补充')}",
            "",
        ])

    # 生成文献池
    sources = [
        {
            "id": i,
            "title": p["title"],
            "authors": p["authors"],
            "source": p["source"],
            "year": p["year"],
            "issue": p["issue"],
            "abstract_url": p["abstract_url"],
            "gb_reference": p.get("gb_reference", ""),
            "origin": "cnki",
        }
        for i, p in enumerate(papers, 1)
    ]

    brief_path = output_dir / "research-brief.md"
    anchor_path = output_dir / "anchor-papers.md"
    sources_path = output_dir / "sources.json"

    brief_path.write_text("\n".join(brief_lines), encoding="utf-8")
    anchor_path.write_text("\n".join(anchor_lines), encoding="utf-8")
    sources_path.write_text(json.dumps(sources, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"研究简报：{brief_path}")
    print(f"候选锚定论文：{anchor_path}")
    print(f"文献池：{sources_path}")


def main():
    parser = argparse.ArgumentParser(description="EMARX 内置 CNKI 工具")
    parser.add_argument("--slow", action="store_true", help="降低操作频率（5-12s），减少反爬风险")
    parser.add_argument("--no-headless", action="store_true", help="非无头模式，便于人工处理验证")

    subparsers = parser.add_subparsers(dest="command", required=True)

    # search
    search_parser = subparsers.add_parser("search", help="搜索 CNKI 并输出 EMARX 格式")
    search_parser.add_argument("query", help="检索关键词")
    search_parser.add_argument("--pages", type=int, default=config.MAX_PAGES, help="最多翻页数")
    search_parser.add_argument("--max-results", type=int, default=None, help="最多采集结果数")
    search_parser.add_argument("--output", required=True, help="输出 JSON 路径")

    # read-batch
    read_parser = subparsers.add_parser("read-batch", help="批量读取 CNKI 详情页摘要")
    read_parser.add_argument("--results", required=True, help="搜索结果 JSON 路径")
    read_parser.add_argument("--output-dir", required=True, help="摘要保存目录")
    read_parser.add_argument("--limit", type=int, default=None, help="最多读取篇数")
    read_parser.add_argument("--start", type=int, default=0, help="起始索引（含）")
    read_parser.add_argument("--end", type=int, default=None, help="结束索引（不含）")

    # import
    import_parser = subparsers.add_parser("import", help="导入 CNKI 结果到 EMARX 工作空间")
    import_parser.add_argument("--results", required=True, help="搜索结果 JSON 路径")
    import_parser.add_argument("--summaries-dir", default=None, help="批量摘要目录")
    import_parser.add_argument("--output-dir", required=True, help="EMARX 工作空间输出目录")
    import_parser.add_argument("--top-k", type=int, default=10, help="入选精读数量")

    args = parser.parse_args()

    if args.command == "search":
        cmd_search(args)
    elif args.command == "read-batch":
        cmd_read_batch(args)
    elif args.command == "import":
        cmd_import(args)


if __name__ == "__main__":
    main()
