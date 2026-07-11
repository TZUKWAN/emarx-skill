# -*- coding: utf-8 -*-
"""
format_adapter.py — 把 EMARX 论文 markdown 转成 marx-paper-skills format pipeline 可接受的格式。

EMARX 使用行内 [n] 引用标记，文末列参考文献。format pipeline 需要 pandoc 脚注语法 [^n]。
本脚本：
  1. 识别正文中的 [n] 引用，替换为 [^n]；
  2. 从文末“参考文献”部分提取条目，生成 pandoc 脚注定义 [^n]: 条目；
  3. 默认删除文末参考文献表中的具体条目，避免与页下注重复；
  4. 保留原 frontmatter、摘要、关键词。

用法：
  python scripts/format_adapter.py input.md output.md
  python scripts/format_adapter.py input.md output.md --keep-references

--keep-references：保留文末参考文献表（会与页下注内容重复，仅作过渡兼容）。
"""
import argparse
import re
import sys
from pathlib import Path

CITATION_RE = re.compile(r'(?<!!)\[(\d+)\]')
REF_HEADING_RE = re.compile(r'^(#+)\s*参考文献\s*$', re.MULTILINE)
REF_ENTRY_RE = re.compile(r'^\[(\d+)\]\s*(.+?)\s*$', re.MULTILINE)


def extract_references(text: str):
    """从文末参考文献部分提取编号到条目的映射，并返回正文和参考文献部分。"""
    m = REF_HEADING_RE.search(text)
    if not m:
        return {}, text, None

    ref_start = m.start()
    body = text[:ref_start]
    heading = m.group(0)
    ref_section = text[ref_start + len(heading):]

    refs = {}
    for num, entry in REF_ENTRY_RE.findall(ref_section):
        refs[int(num)] = entry.strip()

    return refs, body, heading


def adapt(input_md: str, output_md: str, keep_references: bool = False):
    input_path = Path(input_md)
    output_path = Path(output_md)
    if not input_path.exists():
        raise FileNotFoundError(f'找不到 {input_path}')

    text = input_path.read_text(encoding='utf-8')

    refs, body, heading = extract_references(text)
    if not refs:
        print('警告：未找到文末参考文献部分，仅做引用标记替换')

    # 只在正文部分替换 [n] -> [^n]
    body = CITATION_RE.sub(lambda m: f'[^{m.group(1)}]', body)

    if heading is None:
        output_path.write_text(body, encoding='utf-8')
        print(f'已生成: {output_path}')
        return

    # 按编号顺序生成脚注定义
    footnote_defs = []
    for num in sorted(refs.keys()):
        footnote_defs.append(f'[^{num}]: {refs[num]}')
    footnote_block = '\n\n'.join(footnote_defs)

    if keep_references:
        # 保留文末参考文献表：在标题前插入脚注定义，保留原参考文献部分
        ref_section = text[text.find(heading) + len(heading):]
        new_text = body + '\n\n' + footnote_block + '\n\n' + heading + ref_section
    else:
        # 默认：删除文末参考文献条目，只保留标题（避免与页下注重复）
        new_text = body + '\n\n' + footnote_block + '\n\n' + heading + '\n'

    output_path.write_text(new_text, encoding='utf-8')
    print(f'已生成: {output_path}')
    if refs:
        print(f'  转换 {len(refs)} 条引用为 pandoc 脚注')
    if not keep_references:
        print('  已删除文末参考文献条目，避免与页下注重复')


def main():
    ap = argparse.ArgumentParser(description='把 EMARX markdown 转成 format pipeline 可接受格式')
    ap.add_argument('input', help='输入 EMARX markdown 文件路径')
    ap.add_argument('output', help='输出 markdown 文件路径')
    ap.add_argument('--keep-references', action='store_true',
                    help='保留文末参考文献表（会与页下注重复）')
    args = ap.parse_args()
    adapt(args.input, args.output, keep_references=args.keep_references)


if __name__ == '__main__':
    main()
