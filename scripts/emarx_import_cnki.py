# -*- coding: utf-8 -*-
r"""
emarx_import_cnki.py — EMARX 内置 CNKI 导入入口的兼容包装。

本脚本直接调用同目录下的 scripts/cnki_cli.py import，不再依赖外部 D:\CNKICONTROL 项目。

用法：
  python scripts/emarx_import_cnki.py \
    --results workspace/cnki_results.json \
    --summaries-dir workspace/summaries \
    --output-dir workspace \
    --top-k 10
"""
import argparse
import subprocess
import sys
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description="EMARX 内置 CNKI 导入（兼容包装）")
    parser.add_argument("--results", required=True, help="CNKI 搜索结果 JSON 路径")
    parser.add_argument("--summaries-dir", default=None, help="批量摘要目录")
    parser.add_argument("--output-dir", required=True, help="EMARX 工作空间输出目录")
    parser.add_argument("--top-k", type=int, default=10, help="入选精读数量")
    args = parser.parse_args()

    cli = Path(__file__).resolve().parent / "cnki_cli.py"
    cmd = [
        sys.executable,
        str(cli),
        "import",
        "--results", args.results,
        "--output-dir", args.output_dir,
        "--top-k", str(args.top_k),
    ]
    if args.summaries_dir:
        cmd.extend(["--summaries-dir", args.summaries_dir])

    result = subprocess.run(cmd)
    sys.exit(result.returncode)


if __name__ == "__main__":
    main()
