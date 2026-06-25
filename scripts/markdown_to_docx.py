#!/usr/bin/env python
"""Convert a simple Markdown academic paper into a Word .docx file.

This helper intentionally supports a conservative subset of Markdown used by
EMARX outputs: headings, bullet/numbered lists, fenced code blocks, and normal
paragraphs. It is not a full Markdown renderer.
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Pt


def set_run_font(run, size: int | None = None, bold: bool | None = None) -> None:
    run.font.name = "SimSun"
    run._element.rPr.rFonts.set(qn("w:eastAsia"), "SimSun")
    if size is not None:
        run.font.size = Pt(size)
    if bold is not None:
        run.bold = bold


def set_paragraph(paragraph, first_line: bool = False) -> None:
    paragraph.paragraph_format.line_spacing = 1.5
    paragraph.paragraph_format.space_after = Pt(6)
    if first_line:
        paragraph.paragraph_format.first_line_indent = Pt(24)


def add_page_number(section) -> None:
    footer = section.footer
    paragraph = footer.paragraphs[0]
    paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = paragraph.add_run()
    fld_char1 = OxmlElement("w:fldChar")
    fld_char1.set(qn("w:fldCharType"), "begin")
    instr_text = OxmlElement("w:instrText")
    instr_text.set(qn("xml:space"), "preserve")
    instr_text.text = "PAGE"
    fld_char2 = OxmlElement("w:fldChar")
    fld_char2.set(qn("w:fldCharType"), "end")
    run._r.append(fld_char1)
    run._r.append(instr_text)
    run._r.append(fld_char2)


def add_paragraph(document: Document, text: str, style: str | None = None) -> None:
    paragraph = document.add_paragraph(style=style)
    set_paragraph(paragraph, first_line=(style is None))
    run = paragraph.add_run(clean_inline_markdown(text))
    set_run_font(run, 12)


def clean_inline_markdown(text: str) -> str:
    text = text.replace("\ufeff", "")
    text = re.sub(r"\*\*(.+?)\*\*", r"\1", text)
    text = re.sub(r"__(.+?)__", r"\1", text)
    text = re.sub(r"`([^`]+)`", r"\1", text)
    return text


def convert(markdown: str, output: Path) -> None:
    document = Document()
    section = document.sections[0]
    section.top_margin = Pt(72)
    section.bottom_margin = Pt(72)
    section.left_margin = Pt(84)
    section.right_margin = Pt(84)
    add_page_number(section)

    in_code = False
    title_written = False

    for raw_line in markdown.splitlines():
        line = raw_line.rstrip().replace("\ufeff", "")
        if not line.strip():
            continue
        if line.strip().startswith("```"):
            in_code = not in_code
            continue
        if in_code:
            add_paragraph(document, line)
            continue

        heading = re.match(r"^(#{1,4})\s+(.+)$", line)
        if heading:
            level = len(heading.group(1))
            text = heading.group(2).strip()
            if level == 1 and not title_written:
                paragraph = document.add_paragraph()
                paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
                paragraph.paragraph_format.space_after = Pt(12)
                run = paragraph.add_run(clean_inline_markdown(text))
                set_run_font(run, 16, True)
                title_written = True
            else:
                style = "Heading 1" if level <= 2 else "Heading 2"
                paragraph = document.add_paragraph(style=style)
                set_paragraph(paragraph)
                run = paragraph.add_run(clean_inline_markdown(text))
                set_run_font(run, 14 if style == "Heading 1" else 12, True)
            continue

        bullet = re.match(r"^\s*[-*]\s+(.+)$", line)
        if bullet:
            add_paragraph(document, bullet.group(1), style="List Bullet")
            continue

        numbered = re.match(r"^\s*\d+[.)]\s+(.+)$", line)
        if numbered:
            add_paragraph(document, numbered.group(1), style="List Number")
            continue

        add_paragraph(document, line)

    output.parent.mkdir(parents=True, exist_ok=True)
    document.save(output)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="UTF-8 Markdown file")
    parser.add_argument("--output", required=True, help="Output .docx path")
    args = parser.parse_args()

    source = Path(args.input)
    target = Path(args.output)
    convert(source.read_text(encoding="utf-8"), target)
    print(target)


if __name__ == "__main__":
    main()
