# -*- coding: utf-8 -*-
"""
clean_deconstruction_reports.py — 清洗 450 份逐篇拆解报告中的模板化套话。

策略：
  1. 把原始报告复制到 reports_archive/ 备份；
  2. 删除已知的模板化句子、空字段和无信息段落；
  3. 保留真实提取信息（基本信息、短引片段、统计数据）；
  4. 添加模板化警告，避免当作写作范文；
  5. 输出清洗后的报告到 reports_cleaned/。

用法：
  python scripts/clean_deconstruction_reports.py
"""
import re
import shutil
from pathlib import Path

# 模板化句子/短语列表。这些是从 deconstruct_corpus_articles.py 中写入的固定话术。
TEMPLATES = [
    "中等长度句子为主，兼顾解释与推进。",
    "围绕标题展开解释、判断与材料支撑",
    "以背景或语境打开论述；用问题/风险推动论证转入；通过视角限定或材料入口组织分析；以机制、结构或生成逻辑连接现象与判断；把分析推进到路径或实践安排。",
    "使用递进、并列和因果连接词维持段内推进。",
    "引用或注释标记较多，依靠文献/材料增强支撑。",
    "存在较多无主语介词结构，适合压缩背景，但容易削弱判断主体。",
    "可重点借鉴其段落推进方式，但仍需核对材料支撑和概念一致性。",
    "可借鉴其概念密度，但仿写时必须保持术语一致。",
    "可借鉴其段内转折、递进和因果连接方式。",
    "可借鉴其段落推进方式，但仍需核对材料支撑和概念一致性。",
]

WARNING = (
    "> ⚠️ 模板化提示：本报告由脚本批量生成，包含大量模板化字段。"
    "清洗后仅保留基本信息、短引片段和统计指标，供索引与粗略参考，"
    "不宜直接作为写作模板或范文使用。如需深入仿写，请结合原文自行精读。\n\n"
)


def remove_empty_bullet_paragraphs(text: str) -> str:
    """删除空字段行和空列表项。"""
    # 删除以 '- ' 开头且后面没有实质内容的行（字段名后为空，或纯 '-'）
    pattern = re.compile(r"^-\s*$", re.MULTILINE)
    text = pattern.sub("", text)
    pattern = re.compile(r"^- [^\n]*[：:]\s*$", re.MULTILINE)
    text = pattern.sub("", text)
    return text


def remove_empty_sections(text: str) -> str:
    """删除只有标题没有实质内容的节，并清理标题后的多余空行。"""
    # 匹配 ## 或 ### 标题，后面紧跟着下一个 ## 标题或文件末尾
    pattern = re.compile(r"^(#{2,3} [^\n]+)\n+(?=\s*^(#{2,3} |\Z))", re.MULTILINE)
    text = pattern.sub("", text)
    # 清理标题后的多余空行：保证标题后只有一条空行
    text = re.sub(r"^(#{1,3} [^\n]+)\n{2,}", r"\1\n\n", text, flags=re.MULTILINE)
    return text


def clean_text(text: str) -> str:
    """删除模板化句子，清理空字段和无信息段落。"""
    # 1. 删除模板化句子
    for t in TEMPLATES:
        text = text.replace(t, "")

    # 2. 删除 "主体单元一/二/三" 这种无真实标题的占位
    text = re.sub(
        r"### 主体单元[\d一二三四五六七八九十]+：主体单元[\d一二三四五六七八九十]+",
        "### 主体部分（原报告未提取真实小标题）",
        text
    )
    # 同时处理只有一个 "主体单元三" 标题的情况
    text = re.sub(
        r"### 主体单元[\d一二三四五六七八九十]+(?=\n\n- )",
        "### 主体部分（原报告未提取真实小标题）",
        text
    )

    # 3. 删除空字段
    text = remove_empty_bullet_paragraphs(text)
    text = re.sub(r"\n{3,}", "\n\n", text)

    # 4. 删除空节
    text = remove_empty_sections(text)

    # 5. 清理多余空行
    text = re.sub(r"\n{3,}", "\n\n", text)

    # 6. 如果摘要逻辑/风格等字段为空，删除该字段
    text = re.sub(r"- 摘要逻辑：\s*\n", "", text)
    text = re.sub(r"- 摘要风格：\s*\n", "", text)
    text = re.sub(r"- 写作手法：\s*\n", "", text)
    text = re.sub(r"- 行文功能：\s*\n", "", text)
    text = re.sub(r"- 论证逻辑：\s*\n", "", text)
    text = re.sub(r"- 写作风格：\s*\n", "", text)
    text = re.sub(r"- 表达手法：\s*\n", "", text)
    text = re.sub(r"- 主要动作：\s*\n", "", text)

    # 7. 删除内容完全为空的 '可借鉴之处' 和 '需要注意的问题' 节
    text = re.sub(r"## 可借鉴之处\s*\n(?:-?\s*\n)*", "", text)
    text = re.sub(r"## 需要注意的问题\s*\n(?:-?\s*\n)*", "", text)

    # 8. 再次清理空节和空行
    text = remove_empty_sections(text)
    text = re.sub(r"\n{3,}", "\n\n", text)

    # 9. 把同一节内的列表项之间的空行去掉，使其成为紧凑列表
    text = re.sub(r"\n\n- ", r"\n- ", text)

    # 10. 添加警告到文件开头（标题之后）
    lines = text.split("\n")
    if lines and lines[0].startswith("# "):
        text = lines[0] + "\n\n" + WARNING + "\n".join(lines[1:]).lstrip()
    else:
        text = WARNING + text

    return text.strip() + "\n"


def main():
    # 脚本位于 .codex/emarx/github-export/scripts/，工作空间根目录是脚本的上三级目录
    script_dir = Path(__file__).parent.resolve()
    workspace_root = script_dir.parent.parent.parent.parent
    base_dir = workspace_root / ".codex" / "emarx" / "article_deconstruction_v1"
    reports_dir = base_dir / "reports"
    archive_dir = base_dir / "reports_archive"
    cleaned_dir = base_dir / "reports_cleaned"

    if not reports_dir.exists():
        raise FileNotFoundError(f"找不到报告目录: {reports_dir}")

    # 备份原始报告
    if not archive_dir.exists():
        print(f"备份原始报告到 {archive_dir}")
        shutil.copytree(reports_dir, archive_dir)

    # 创建清洗后目录
    cleaned_dir.mkdir(exist_ok=True)

    files = sorted(reports_dir.glob("*.md"))
    print(f"开始清洗 {len(files)} 份报告...")

    removed_total = 0
    for f in files:
        text = f.read_text(encoding="utf-8")
        removed = sum(text.count(t) for t in TEMPLATES)
        removed_total += removed

        cleaned = clean_text(text)
        out_path = cleaned_dir / f.name
        out_path.write_text(cleaned, encoding="utf-8")

    print(f"完成。共删除 {removed_total} 处模板化句子，并清理空字段/空节。")
    print(f"原始报告备份: {archive_dir}")
    print(f"清洗后报告: {cleaned_dir}")


if __name__ == "__main__":
    main()
