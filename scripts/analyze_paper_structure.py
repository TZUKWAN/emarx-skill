from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Iterable

import pdfplumber


HEADING_PATTERNS = [
    ("level1_cn", re.compile(r"^[一二三四五六七八九十]+[、.．]\s*.{2,80}$")),
    ("level2_cn_paren", re.compile(r"^（[一二三四五六七八九十]+）\s*.{2,80}$")),
    ("level2_arabic", re.compile(r"^\d+[.．、]\s*.{2,80}$")),
    ("level3_cn_paren", re.compile(r"^[（(]\d+[）)]\s*.{2,80}$")),
    ("level3_decimal", re.compile(r"^\d+\.\d+(\.\d+)?\s*.{2,80}$")),
    ("special", re.compile(r"^(摘要|关键词|引言|绪论|前言|结语|结论|参考文献|注释)[:：]?$")),
]

NOISE_PATTERNS = [
    re.compile(r"^\d+$"),
    re.compile(r"^第\s*\d+\s*页$"),
    re.compile(r"^\[\[SOURCE:"),
    re.compile(r"^[\d\s\-—–]+$"),
]

SKIP_DIRS = {".git", ".codex", "node_modules", ".venv", "venv", "__pycache__"}


def clean_line(line: str) -> str:
    return re.sub(r"\s+", " ", (line or "").strip()).strip()


def is_noise(line: str) -> bool:
    if not line or len(line) > 100:
        return True
    return any(pattern.search(line) for pattern in NOISE_PATTERNS)


def heading_type(line: str) -> str | None:
    if is_noise(line):
        return None
    compact = re.sub(r"\s+", "", clean_line(line))
    for name, pattern in HEADING_PATTERNS:
        if pattern.match(compact):
            return name
    return None


def level_from_type(kind: str) -> int:
    if kind == "level1_cn":
        return 1
    if kind in {"level2_cn_paren", "level2_arabic"}:
        return 2
    if kind in {"level3_cn_paren", "level3_decimal"}:
        return 3
    return 0


def iter_pdfs(root: Path) -> Iterable[Path]:
    for path in sorted(root.rglob("*.pdf"), key=lambda item: str(item)):
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        yield path


def extract_pdf(path: Path, text_dir: Path) -> dict:
    record = {
        "file": str(path),
        "name": path.name,
        "size": path.stat().st_size,
        "sha1": "",
        "status": "pending",
        "pages": 0,
        "pages_extracted": 0,
        "chars": 0,
        "text_file": None,
        "headings": [],
        "heading_counts": {},
        "max_heading_level": 0,
        "has_abstract": False,
        "has_keywords": False,
        "has_intro": False,
        "has_conclusion": False,
        "has_references": False,
        "error": None,
    }
    if record["size"] == 0:
        record["status"] = "empty_file"
        return record

    try:
        record["sha1"] = hashlib.sha1(path.read_bytes()).hexdigest()
        all_lines: list[str] = []
        with pdfplumber.open(str(path)) as pdf:
            record["pages"] = len(pdf.pages)
            for page_no, page in enumerate(pdf.pages, 1):
                try:
                    text = page.extract_text() or ""
                except Exception as exc:  # pragma: no cover - depends on malformed PDFs
                    text = f"[page extraction failed: {exc}]"
                if text.strip():
                    record["pages_extracted"] += 1
                for raw in text.splitlines():
                    line = clean_line(raw)
                    if not line:
                        continue
                    all_lines.append(f"[[p{page_no}]] {line}")
                    kind = heading_type(line)
                    if kind:
                        record["headings"].append(
                            {
                                "page": page_no,
                                "type": kind,
                                "level": level_from_type(kind),
                                "text": line,
                            }
                        )

        full_text = "\n".join(all_lines)
        safe_name = hashlib.sha1(str(path).encode("utf-8")).hexdigest()[:12]
        text_path = text_dir / f"{safe_name}.txt"
        text_path.write_text(full_text, encoding="utf-8")
        record["text_file"] = str(text_path)
        record["chars"] = len(full_text)
        record["status"] = "ok" if full_text.strip() else "no_text"
        record["heading_counts"] = dict(Counter(h["type"] for h in record["headings"]))
        record["max_heading_level"] = max([h["level"] for h in record["headings"]] or [0])

        head_text = "\n".join(h["text"] for h in record["headings"])
        probe_start = head_text + "\n" + full_text[:3000]
        probe_end = full_text[-8000:]
        record["has_abstract"] = bool(re.search(r"摘要", probe_start))
        record["has_keywords"] = bool(re.search(r"关键词|关键字", probe_start))
        record["has_intro"] = bool(re.search(r"引言|绪论|前言|问题的提出", probe_start))
        record["has_conclusion"] = bool(re.search(r"结语|结论|结束语", probe_end))
        record["has_references"] = bool(re.search(r"参考文献|注释", probe_end))
        return record
    except Exception as exc:  # pragma: no cover - depends on local PDFs
        record["status"] = "error"
        record["error"] = repr(exc)
        return record


def percentile(values: list[int], p: float) -> int:
    if not values:
        return 0
    index = min(len(values) - 1, max(0, round((len(values) - 1) * p)))
    return values[index]


def summarize(records: list[dict]) -> dict:
    ok = [r for r in records if r.get("status") == "ok"]
    char_values = sorted(r.get("chars", 0) for r in ok)
    page_values = sorted(r.get("pages", 0) for r in ok)
    heading_counts = Counter()
    for record in records:
        heading_counts.update(record.get("heading_counts", {}))

    def pct(count: int) -> float:
        return round(count * 100 / max(1, len(records)), 2)

    return {
        "total": len(records),
        "status": dict(Counter(r.get("status") for r in records)),
        "total_chars": sum(r.get("chars", 0) for r in records),
        "total_pages": sum(r.get("pages", 0) or 0 for r in records),
        "pages_extracted": sum(r.get("pages_extracted", 0) or 0 for r in records),
        "heading_depth_distribution": dict(Counter(str(r.get("max_heading_level", 0)) for r in records)),
        "heading_type_counts": dict(heading_counts),
        "has_abstract": pct(sum(1 for r in records if r.get("has_abstract"))),
        "has_keywords": pct(sum(1 for r in records if r.get("has_keywords"))),
        "has_intro": pct(sum(1 for r in records if r.get("has_intro"))),
        "has_conclusion": pct(sum(1 for r in records if r.get("has_conclusion"))),
        "has_references": pct(sum(1 for r in records if r.get("has_references"))),
        "chars_p25": percentile(char_values, 0.25),
        "chars_p50": percentile(char_values, 0.50),
        "chars_p75": percentile(char_values, 0.75),
        "pages_p25": percentile(page_values, 0.25),
        "pages_p50": percentile(page_values, 0.50),
        "pages_p75": percentile(page_values, 0.75),
        "ok_count": len(ok),
        "chars_ge_10000": sum(1 for r in ok if r.get("chars", 0) >= 10000),
        "chars_ge_12000": sum(1 for r in ok if r.get("chars", 0) >= 12000),
        "pages_ge_8": sum(1 for r in ok if r.get("pages", 0) >= 8),
        "max_heading_level_ge_2": sum(1 for r in ok if r.get("max_heading_level", 0) >= 2),
        "max_heading_level_ge_3": sum(1 for r in ok if r.get("max_heading_level", 0) >= 3),
    }


def write_markdown_report(records: list[dict], summary: dict, report_path: Path) -> None:
    by_depth: dict[int, list[dict]] = defaultdict(list)
    for record in records:
        by_depth[int(record.get("max_heading_level", 0))].append(record)

    lines = [
        "# EMARX Paper Structure Report",
        "",
        "## Summary",
        f"- PDF total: {summary['total']}",
        f"- Status: {summary['status']}",
        f"- Readable PDFs: {summary['ok_count']}",
        f"- Pages extracted: {summary['pages_extracted']} / {summary['total_pages']}",
        f"- Extracted characters: {summary['total_chars']}",
        f"- Characters P25/P50/P75: {summary['chars_p25']} / {summary['chars_p50']} / {summary['chars_p75']}",
        f"- Pages P25/P50/P75: {summary['pages_p25']} / {summary['pages_p50']} / {summary['pages_p75']}",
        f"- Heading depth distribution: {summary['heading_depth_distribution']}",
        f"- Heading type counts: {summary['heading_type_counts']}",
        f"- Papers >= 10,000 chars: {summary['chars_ge_10000']}",
        f"- Papers with heading depth >= 2: {summary['max_heading_level_ge_2']}",
        "",
        "## Caveat",
        "PDF extraction can misread journal headers, DOI strings, page numbers, and reference entries as headings. Use this report as a structural signal and verify important samples manually.",
        "",
        "## Samples By Max Heading Depth",
    ]

    for depth in sorted(by_depth):
        lines.append(f"### Max Heading Level {depth}")
        for record in by_depth[depth][:8]:
            lines.append(
                f"- `{record['name']}` pages={record.get('pages')} chars={record.get('chars')} headings={len(record.get('headings', []))}"
            )
            for heading in record.get("headings", [])[:8]:
                lines.append(f"  - p{heading['page']} L{heading['level']} {heading['text']}")

    lines.append("")
    lines.append("## Low-Depth Risk List")
    for record in [
        item
        for item in records
        if item.get("status") == "ok" and item.get("max_heading_level", 0) < 2
    ][:80]:
        lines.append(
            f"- `{record['name']}` max_level={record.get('max_heading_level')} headings={len(record.get('headings', []))} chars={record.get('chars')}"
        )

    report_path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Analyze PDF paper length and heading hierarchy.")
    parser.add_argument("--root", required=True, help="Workspace or folder containing PDF papers.")
    parser.add_argument("--output-dir", required=True, help="Directory for extracted text and reports.")
    parser.add_argument("--max-files", type=int, default=0, help="Optional limit for smoke tests.")
    parser.add_argument("--resume", action="store_true", help="Reuse records from an existing structure_index.json.")
    args = parser.parse_args()

    root = Path(args.root).expanduser().resolve()
    output_dir = Path(args.output_dir).expanduser().resolve()
    text_dir = output_dir / "texts"
    report_dir = output_dir / "reports"
    text_dir.mkdir(parents=True, exist_ok=True)
    report_dir.mkdir(parents=True, exist_ok=True)

    pdfs = list(iter_pdfs(root))
    if args.max_files:
        pdfs = pdfs[: args.max_files]

    index_path = report_dir / "structure_index.json"
    existing_by_file: dict[str, dict] = {}
    if args.resume and index_path.exists():
        existing = json.loads(index_path.read_text(encoding="utf-8"))
        existing_by_file = {item["file"]: item for item in existing}

    records = []
    for position, pdf in enumerate(pdfs, 1):
        cached = existing_by_file.get(str(pdf))
        if cached and cached.get("status") in {"ok", "empty_file", "no_text", "error"}:
            record = cached
        else:
            record = extract_pdf(pdf, text_dir)
        records.append(record)
        if position % 10 == 0 or position == len(pdfs):
            index_path.write_text(json.dumps(records, ensure_ascii=False, indent=2), encoding="utf-8")
        print(
            json.dumps(
                {
                    "position": position,
                    "total": len(pdfs),
                    "status": record["status"],
                    "pages": record.get("pages"),
                    "headings": len(record.get("headings", [])),
                    "max_heading_level": record.get("max_heading_level"),
                    "name": record["name"],
                },
                ensure_ascii=False,
            ),
            flush=True,
        )

    summary = summarize(records)
    index_path.write_text(json.dumps(records, ensure_ascii=False, indent=2), encoding="utf-8")
    (report_dir / "structure_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    write_markdown_report(records, summary, report_dir / "structure_hierarchy_report.md")
    print(json.dumps(summary, ensure_ascii=False), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
