# -*- coding: utf-8 -*-
r"""
emarx_search_cnki.py — EMARX 内置 CNKI 搜索入口的兼容包装。

本脚本直接调用同目录下的 scripts/cnki_cli.py，不再依赖外部 D:\CNKICONTROL 项目。

用法：
  python scripts/emarx_search_cnki.py \
    --query "生成式人工智能 国际传播" \
    --pages 3 \
    --max-results 30 \
    --output workspace/cnki_results.json

注意：--cnki-root 参数已保留但不再使用，仅用于兼容旧命令。
"""
import argparse
import subprocess
import sys
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description="EMARX 内置 CNKI 搜索（兼容包装）")
    parser.add_argument("--cnki-root", default=None, help="已废弃，保留兼容")
    parser.add_argument("--query", required=True, help="检索关键词")
    parser.add_argument("--pages", type=int, default=3, help="最多翻页数")
    parser.add_argument("--max-results", type=int, default=None, help="最多采集结果数")
    parser.add_argument("--slow", action="store_true", help="降低操作频率")
    parser.add_argument("--output", required=True, help="输出 JSON 文件路径")
    args = parser.parse_args()

    cli = Path(__file__).resolve().parent / "cnki_cli.py"
    cmd = [
        sys.executable,
        str(cli),
        "--slow" if args.slow else "",
        "search",
        args.query,
        "--pages", str(args.pages),
        "--output", args.output,
    ]
    if args.max_results is not None:
        cmd.extend(["--max-results", str(args.max_results)])

    # 过滤空字符串
    cmd = [c for c in cmd if c]

    result = subprocess.run(cmd)
    sys.exit(result.returncode)


if __name__ == "__main__":
    main()
