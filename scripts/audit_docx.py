#!/usr/bin/env python
"""Independently audit an EMARX DOCX after generation."""

from __future__ import annotations

import argparse
import json
import re
import zipfile
from pathlib import Path

from docx import Document


CITE_RE = re.compile(r"^\[(\d+)\]$")
REF_RE = re.compile(r"^\[(\d+)\]\s+")


def points(value) -> float | None:
    return None if value is None else round(value.pt, 2)


def style_color(style) -> str | None:
    color = style.font.color
    return str(color.rgb) if color is not None and color.rgb is not None else None


def audit(path: Path) -> dict:
    zip_error = None
    with zipfile.ZipFile(path) as archive:
        zip_error = archive.testzip()

    document = Document(str(path))
    paragraphs = document.paragraphs
    sections = document.sections
    section = sections[0]
    titles = [p for p in paragraphs if p.style.name == "EMARX Title"]
    headings = [p for p in paragraphs if p.style.name.startswith("Heading ")]
    abstracts = [p for p in paragraphs if p.style.name == "EMARX Abstract"]
    keywords = [p for p in paragraphs if p.style.name == "EMARX Keywords"]
    references = [p for p in paragraphs if p.style.name == "EMARX Reference"]
    body = [p for p in paragraphs if p.style.name == "Normal" and p.text.strip()]

    body_citations = []
    baseline_citations = []
    for paragraph in body + abstracts + keywords:
        for run in paragraph.runs:
            if CITE_RE.match(run.text.strip()):
                body_citations.append(int(CITE_RE.match(run.text.strip()).group(1)))
                if run.font.superscript is not True:
                    baseline_citations.append(run.text)

    reference_numbers = []
    for paragraph in references:
        match = REF_RE.match(paragraph.text.strip())
        if match:
            reference_numbers.append(int(match.group(1)))

    relevant_styles = ["EMARX Title", "Heading 1", "Heading 2", "Heading 3", "Normal", "EMARX Abstract", "EMARX Keywords", "EMARX Reference"]
    nonblack_styles = {}
    for name in relevant_styles:
        if name in document.styles:
            color = style_color(document.styles[name])
            if color not in (None, "000000"):
                nonblack_styles[name] = color

    reference_style = document.styles["EMARX Reference"].paragraph_format if "EMARX Reference" in document.styles else None
    footer_xml = "".join(section.footer._element.xml for section in sections)
    page_width_mm = round(section.page_width.mm, 2)
    page_height_mm = round(section.page_height.mm, 2)
    result = {
        "file": str(path.resolve()),
        "file_bytes": path.stat().st_size,
        "zip_integrity_ok": zip_error is None,
        "zip_bad_member": zip_error,
        "section_count": len(sections),
        "page_width_mm": page_width_mm,
        "page_height_mm": page_height_mm,
        "a4_ok": abs(page_width_mm - 210) < 0.5 and abs(page_height_mm - 297) < 0.5,
        "margins_mm": {
            "top": round(section.top_margin.mm, 2),
            "bottom": round(section.bottom_margin.mm, 2),
            "left": round(section.left_margin.mm, 2),
            "right": round(section.right_margin.mm, 2),
        },
        "title_count": len(titles),
        "heading_count": len(headings),
        "heading_styles": {name: sum(p.style.name == name for p in headings) for name in ("Heading 1", "Heading 2", "Heading 3")},
        "abstract_count": len(abstracts),
        "keywords_count": len(keywords),
        "body_paragraph_count": len(body),
        "reference_count": len(references),
        "body_citation_numbers": body_citations,
        "reference_numbers": reference_numbers,
        "baseline_citations": baseline_citations,
        "citation_reference_count_ok": len(body_citations) == len(references),
        "nonblack_relevant_styles": nonblack_styles,
        "reference_style_left_indent_pt": points(reference_style.left_indent) if reference_style else None,
        "reference_style_first_line_indent_pt": points(reference_style.first_line_indent) if reference_style else None,
        "reference_hanging_indent_ok": bool(
            reference_style
            and reference_style.left_indent
            and reference_style.first_line_indent
            and reference_style.left_indent.pt > 0
            and reference_style.first_line_indent.pt < 0
        ),
        "page_number_field_ok": "PAGE" in footer_xml and "w:fldChar" in footer_xml,
    }
    result["ok"] = (
        result["zip_integrity_ok"]
        and result["a4_ok"]
        and result["title_count"] == 1
        and result["heading_count"] > 0
        and result["abstract_count"] == 1
        and result["keywords_count"] == 1
        and result["body_paragraph_count"] > 0
        and not result["baseline_citations"]
        and result["citation_reference_count_ok"]
        and not result["nonblack_relevant_styles"]
        and result["reference_hanging_indent_ok"]
        and result["page_number_field_ok"]
    )
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--docx", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    result = audit(args.docx)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"ok": result["ok"], "output": str(args.output)}, ensure_ascii=False))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
