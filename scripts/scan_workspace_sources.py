#!/usr/bin/env python
"""Scan a workspace for research sources and produce a JSON index.

This script is intentionally conservative. It extracts lightweight metadata and
short text samples so EMARX can decide what to inspect next. The index is not a
substitute for reading and verifying the original files.
"""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter
import hashlib
from pathlib import Path
from typing import Iterable


SUPPORTED = {".pdf", ".docx", ".md", ".markdown", ".txt", ".html", ".htm"}
SKIP_DIRS = {
    ".git", ".codex", ".sophia", "node_modules", "__pycache__", ".venv",
    "venv", ".idea", ".vscode", "generated_documents",
}
GENERATED_PATTERNS = [
    "EMARX", "重写版", "最新版", "最新", "审计", "audit", "anchor-test",
    "research-brief", "source-inventory", "anchors.md", "anchor-reading-manifest",
    "reading-packets", "reading_packet", "逐篇精读报告", "拆解报告",
]


def iter_files(root: Path) -> Iterable[Path]:
    for path in sorted(root.rglob("*"), key=lambda item: str(item).lower()):
        if any(part.lower() in SKIP_DIRS or part.startswith(".") for part in path.parts):
            continue
        if path.is_file() and path.suffix.lower() in SUPPORTED:
            yield path


def clean_text(text: str, limit: int = 6000) -> str:
    text = re.sub(r"\s+", " ", text.replace("\ufeff", " ")).strip()
    return text[:limit]


def read_text_file(path: Path) -> str:
    for encoding in ("utf-8", "utf-8-sig", "gb18030", "latin-1"):
        try:
            return path.read_text(encoding=encoding, errors="ignore")
        except Exception:
            continue
    return ""


def read_docx(path: Path) -> str:
    try:
        from docx import Document

        doc = Document(str(path))
        return "\n".join(p.text for p in doc.paragraphs)
    except Exception:
        return ""


def read_pdf(path: Path, pages: int) -> str:
    try:
        import pdfplumber

        chunks: list[str] = []
        with pdfplumber.open(str(path)) as pdf:
            for page in pdf.pages[:pages]:
                chunks.append(page.extract_text() or "")
        return "\n".join(chunks)
    except Exception:
        return ""


def keywords(text: str, topn: int = 12) -> list[str]:
    chinese_terms = re.findall(r"[\u4e00-\u9fff]{2,8}", text)
    latin_terms = re.findall(r"[A-Za-z][A-Za-z0-9_-]{2,}", text.lower())
    stop = {
        "的", "和", "以及", "通过", "进行", "研究", "问题", "本文", "认为", "可以",
        "this", "that", "with", "from", "the", "and", "for", "are", "was",
    }
    counts = Counter(t for t in chinese_terms + latin_terms if t not in stop)
    return [term for term, _ in counts.most_common(topn)]


def make_record(path: Path, root: Path, sample_pages: int) -> dict:
    suffix = path.suffix.lower()
    if suffix == ".pdf":
        text = read_pdf(path, sample_pages)
    elif suffix == ".docx":
        text = read_docx(path)
    else:
        text = read_text_file(path)
    sample = clean_text(text)
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    path_text = str(path).lower()
    generated = any(pattern.lower() in path_text for pattern in GENERATED_PATTERNS)
    return {
        "path": str(path),
        "relative_path": str(path.relative_to(root)),
        "type": suffix.lstrip("."),
        "size": path.stat().st_size,
        "source_sha256": digest.hexdigest(),
        "category": "generated_or_internal" if generated else "candidate_source",
        "keywords": keywords(sample),
        "sample": sample[:1200],
        "char_count_sampled": len(sample),
        "readable": bool(sample),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", required=True, help="Workspace root to scan")
    parser.add_argument("--output", required=True, help="Output JSON path")
    parser.add_argument("--max-files", type=int, default=2000, help="Maximum files to index")
    parser.add_argument("--pdf-pages", type=int, default=3, help="PDF pages to sample per file")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    records: list[dict] = []
    all_paths = list(iter_files(root))
    for path in all_paths:
        records.append(make_record(path, root, args.pdf_pages))
        if len(records) >= args.max_files:
            break

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "root": str(root),
        "count": len(records),
        "available_count": len(all_paths),
        "truncated": len(records) < len(all_paths),
        "supported_types": sorted(SUPPORTED),
        "records": records,
    }
    output.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(output)


if __name__ == "__main__":
    main()
