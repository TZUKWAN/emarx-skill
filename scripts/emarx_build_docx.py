# -*- coding: utf-8 -*-
"""
emarx_build_docx.py — EMARX 一键 Word 交付脚本。

先把 EMARX 论文 markdown（正文使用 [n] 行内引用）转成 format pipeline 可接受的
pandoc 脚注格式，再调用 scripts/format/build_docx.py 完成 Word 渲染。

用法：
  python scripts/emarx_build_docx.py input.md output.docx [--no-circle]

默认生成圈码 ①②③ 并每页重新编号。Word COM 调用会优先复用已运行的 Word/WPS 实例，
没有已运行实例时才新建隐藏实例，尽量不影响前台工作。若不希望调用 COM，加 --no-circle。
"""
import argparse
import subprocess
import sys
import tempfile
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent.resolve()
PROJECT_ROOT = SCRIPT_DIR.parent
ADAPTER = SCRIPT_DIR / "format_adapter.py"
BUILD_DOCX = SCRIPT_DIR / "format" / "build_docx.py"


def run(cmd, cwd=None):
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=cwd)
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)
    if result.returncode != 0:
        raise RuntimeError(f"命令失败: {' '.join(cmd)}")


def main():
    ap = argparse.ArgumentParser(description="EMARX 一键生成规范 Word 文档")
    ap.add_argument("md", help="输入 EMARX markdown 文件路径")
    ap.add_argument("docx", help="输出 docx 文件路径")
    ap.add_argument("--no-circle", action="store_true",
                    help="不生成圈码、不做每页重编号（不调用 Word/WPS COM）")
    ap.add_argument("--keep-references", action="store_true",
                    help="保留文末参考文献表（默认删除，避免与页下注重复）")
    args = ap.parse_args()

    input_md = Path(args.md).resolve()
    output_docx = Path(args.docx).resolve()

    if not input_md.exists():
        raise FileNotFoundError(f"找不到输入文件: {input_md}")

    # 第一步：用 adapter 转换格式
    with tempfile.NamedTemporaryFile(mode='w', suffix='.md',
                                     delete=False, encoding='utf-8') as tmp:
        adapted_md = Path(tmp.name)

    print(f"步骤1: 适配 EMARX 引用格式 -> {adapted_md.name}")
    adapter_cmd = [sys.executable, str(ADAPTER), str(input_md), str(adapted_md)]
    if args.keep_references:
        adapter_cmd.append("--keep-references")
    run(adapter_cmd)

    # 第二步：调用 format pipeline
    print(f"\n步骤2: 生成 Word -> {output_docx}")
    cmd = [sys.executable, str(BUILD_DOCX), str(adapted_md), str(output_docx)]
    if args.no_circle:
        cmd.append("--no-circle")
    run(cmd)

    # 清理临时文件
    adapted_md.unlink(missing_ok=True)
    print(f"\n✅ 完成: {output_docx}")


if __name__ == "__main__":
    main()
