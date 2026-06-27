#!/usr/bin/env python
"""Build full-text, page-addressable reading packets for selected anchor papers."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path


PATH_RE = re.compile(r"^- 原文件：`(.+?)`\s*$", re.MULTILINE)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def safe_stem(position: int, path: Path) -> str:
    name = re.sub(r"[<>:\"/\\|?*\x00-\x1f]", "_", path.stem).strip(" ._")
    digest = hashlib.sha256(str(path.resolve()).encode("utf-8")).hexdigest()[:8]
    return f"{position:02d}_{name[:90]}_{digest}"


def clean_text(text: str) -> str:
    text = text.replace("\ufeff", "")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def extract_pdf(path: Path) -> tuple[list[str], list[int]]:
    import pdfplumber

    pages: list[str] = []
    empty_pages: list[int] = []
    with pdfplumber.open(str(path)) as document:
        for index, page in enumerate(document.pages, 1):
            text = clean_text(page.extract_text() or "")
            pages.append(text)
            if not text:
                empty_pages.append(index)
    return pages, empty_pages


def extract_docx(path: Path) -> tuple[list[str], list[int]]:
    from docx import Document

    document = Document(str(path))
    paragraphs = [paragraph.text for paragraph in document.paragraphs]
    return [clean_text("\n".join(paragraphs))], []


def extract_text(path: Path) -> tuple[list[str], list[int]]:
    text = path.read_text(encoding="utf-8", errors="replace")
    if path.suffix.lower() in {".html", ".htm"}:
        text = re.sub(r"<script\b[^>]*>.*?</script>", " ", text, flags=re.I | re.S)
        text = re.sub(r"<style\b[^>]*>.*?</style>", " ", text, flags=re.I | re.S)
        text = re.sub(r"<[^>]+>", " ", text)
    return [clean_text(text)], []


def extract_pages(path: Path) -> tuple[list[str], list[int], str]:
    suffix = path.suffix.lower()
    if suffix == ".pdf":
        pages, empty = extract_pdf(path)
        return pages, empty, "pdfplumber_full_pages"
    if suffix == ".docx":
        pages, empty = extract_docx(path)
        return pages, empty, "python_docx_paragraphs"
    if suffix in {".md", ".txt", ".html", ".htm"}:
        pages, empty = extract_text(path)
        return pages, empty, "utf8_text"
    raise ValueError(f"Unsupported anchor format: {suffix}")


def number_packet(pages: list[str]) -> tuple[str, int]:
    output: list[str] = []
    line_number = 1
    for page_number, text in enumerate(pages, 1):
        output.append(f"[[PAGE {page_number}]]")
        lines = text.splitlines() or [""]
        for line in lines:
            output.append(f"[[p{page_number}:L{line_number:05d}]] {line}")
            line_number += 1
        output.append("")
    return "\n".join(output).rstrip() + "\n", line_number - 1


def parse_anchor_paths(selection: Path) -> list[Path]:
    text = selection.read_text(encoding="utf-8")
    paths: list[Path] = []
    seen: set[str] = set()
    for match in PATH_RE.finditer(text):
        path = Path(match.group(1)).expanduser().resolve()
        key = str(path).lower()
        if key not in seen:
            paths.append(path)
            seen.add(key)
    return paths


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--selection", required=True, type=Path, help="Markdown produced by select_anchor_papers.py")
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--minimum", type=int, default=3)
    parser.add_argument("--maximum", type=int, default=5)
    args = parser.parse_args()

    paths = parse_anchor_paths(args.selection)
    if len(paths) < args.minimum or len(paths) > args.maximum:
        raise SystemExit(f"Anchor count {len(paths)} is outside required range {args.minimum}-{args.maximum}.")

    args.output_dir.mkdir(parents=True, exist_ok=True)
    records: list[dict] = []
    failures: list[dict] = []
    for position, path in enumerate(paths, 1):
        try:
            if not path.is_file():
                raise FileNotFoundError(path)
            pages, empty_pages, method = extract_pages(path)
            packet, line_count = number_packet(pages)
            output = args.output_dir / f"{safe_stem(position, path)}.txt"
            output.write_text(packet, encoding="utf-8")
            record = {
                "position": position,
                "source_file": str(path),
                "source_sha256": sha256_file(path),
                "format": path.suffix.lower(),
                "extraction_method": method,
                "page_count": len(pages),
                "empty_pages": empty_pages,
                "extracted_characters": sum(len(page) for page in pages),
                "numbered_lines": line_count,
                "packet": str(output),
                "packet_sha256": hashlib.sha256(packet.encode("utf-8")).hexdigest(),
                "status": "ok" if any(pages) else "empty",
            }
            records.append(record)
        except Exception as exc:
            failures.append({"position": position, "source_file": str(path), "error": repr(exc)})

    manifest = {
        "selection": str(args.selection.resolve()),
        "anchor_count": len(paths),
        "ok_count": sum(record["status"] == "ok" for record in records),
        "records": records,
        "failures": failures,
    }
    manifest["ok"] = not failures and manifest["ok_count"] == len(paths)
    manifest_path = args.output_dir / "anchor-reading-manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"ok": manifest["ok"], "manifest": str(manifest_path)}, ensure_ascii=False))
    return 0 if manifest["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
