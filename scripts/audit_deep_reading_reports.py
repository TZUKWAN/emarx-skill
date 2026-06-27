#!/usr/bin/env python
"""Audit a Qwen deep-reading corpus for coverage, evidence, and templating risk."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path


LOCATION_RE = re.compile(r"\[\[p(\d+):L(\d+)(?:-L(\d+))?\]\]")
OLD_TEMPLATE_PHRASES = [
    "界定对象、描述现象、解释原因、提出路径",
    "概念界定—问题呈现—机制分析—路径回应",
    "先界定、再分析、后提出对策",
]


def has_unnegated_phrase(text: str, phrase: str) -> bool:
    for match in re.finditer(re.escape(phrase), text):
        context = text[max(0, match.start() - 20) : match.end() + 20]
        if any(marker in context for marker in ("无明显", "未检测到", "没有", "不得", "禁止", "避免", "不使用", "不要")):
            continue
        return True
    return False


def read_jsonl(path: Path) -> list[dict]:
    rows: list[dict] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return rows


def latest_by_index(rows: list[dict]) -> list[dict]:
    latest: dict[int, dict] = {}
    for row in rows:
        if "index" in row:
            latest[int(row["index"])] = row
    return [latest[index] for index in sorted(latest)]


def normalize_line(line: str) -> str:
    line = LOCATION_RE.sub("<LOC>", line.strip())
    line = re.sub(r"\d+", "<N>", line)
    line = re.sub(r"\s+", " ", line)
    return line


def content_lines(text: str) -> set[str]:
    result: set[str] = set()
    in_exact_evidence = False
    for line in text.splitlines():
        stripped = line.strip()
        if stripped == "# 程序回填的逐字证据":
            in_exact_evidence = True
            continue
        if in_exact_evidence or stripped.startswith("#") or stripped.startswith("|"):
            continue
        normalized = normalize_line(stripped)
        if len(normalized) >= 36 and normalized != "以下原文由程序依据千问返回的页码行号直接回填，未经过模型改写。":
            result.add(normalized)
    return result


def report_record(row: dict) -> dict:
    report_path = Path(str(row.get("report", "")))
    if not report_path.exists():
        return {
            "index": row.get("index"),
            "name": row.get("name"),
            "status": "missing_report",
            "report": str(report_path),
        }
    text = report_path.read_text(encoding="utf-8", errors="replace")
    pages = sorted({int(match.group(1)) for match in LOCATION_RE.finditer(text)})
    quality = row.get("quality") or {}
    evidence = row.get("evidence_validation") or {}
    quality_problems = row.get("quality_problems", quality.get("issues", [])) or []
    invalid_locations = evidence.get("invalid_locations")
    if invalid_locations is None:
        invalid_locations = quality.get("invalid_evidence_locations")
    missing_pages = evidence.get("missing_pages", []) or []
    unmatched_titles = evidence.get("unmatched_claimed_source_titles", []) or []
    quality_ok = quality.get("ok")
    if quality_ok is None:
        quality_ok = not quality_problems and not invalid_locations and not missing_pages
    old_hits = [phrase for phrase in OLD_TEMPLATE_PHRASES if has_unnegated_phrase(text, phrase)]
    return {
        "index": row.get("index"),
        "name": row.get("name"),
        "status": row.get("status"),
        "transport": row.get("transport", "api_legacy_or_unspecified"),
        "report": str(report_path),
        "report_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
        "characters": len(text),
        "location_count": len(LOCATION_RE.findall(text)),
        "located_pages": pages,
        "located_page_count": len(pages),
        "valid_evidence_locations": evidence.get("evidence_locations", quality.get("valid_evidence_locations")),
        "invalid_evidence_locations": invalid_locations,
        "missing_pages": missing_pages,
        "title_warning_count": len(unmatched_titles),
        "title_warnings": unmatched_titles[:20],
        "quality_ok": quality_ok,
        "quality_issues": quality_problems,
        "old_template_hits": old_hits,
        "content_lines": content_lines(text),
    }


def build_audit(
    run_manifest: Path,
    expected_count: int | None,
    repeat_threshold: int,
    required_transport: str | None,
) -> dict:
    latest = latest_by_index(read_jsonl(run_manifest))
    records = [report_record(row) for row in latest if row.get("status") == "ok"]
    errors = [row for row in latest if row.get("status") != "ok"]

    hash_groups: dict[str, list[dict]] = defaultdict(list)
    line_groups: dict[str, list[int]] = defaultdict(list)
    for record in records:
        hash_groups[record["report_sha256"]].append(record)
        for line in record.pop("content_lines"):
            line_groups[line].append(int(record["index"]))

    duplicate_reports = [
        {"sha256": digest, "indices": [item["index"] for item in group]}
        for digest, group in hash_groups.items()
        if len(group) > 1
    ]
    repeated_lines = [
        {"report_count": len(indices), "indices": indices, "line": line}
        for line, indices in line_groups.items()
        if len(indices) >= repeat_threshold
    ]
    repeated_lines.sort(key=lambda item: (-item["report_count"], item["line"]))
    title_warning_records = [
        {
            "index": record["index"],
            "name": record["name"],
            "title_warning_count": record.get("title_warning_count", 0),
            "title_warnings": record.get("title_warnings", []),
        }
        for record in records
        if record.get("title_warning_count", 0)
    ]

    abnormal = []
    for record in records:
        reasons = []
        if record["quality_ok"] is not True:
            reasons.append("quality_not_ok")
        if record["invalid_evidence_locations"] not in (None, 0, []):
            reasons.append("invalid_evidence_locations")
        if record["location_count"] < 6:
            reasons.append("too_few_locations")
        if record["old_template_hits"]:
            reasons.append("old_template_phrase")
        if required_transport and record["transport"] != required_transport:
            reasons.append(f"transport_mismatch:{record['transport']}")
        if reasons:
            abnormal.append({"index": record["index"], "name": record["name"], "reasons": reasons})

    expected_ok = expected_count is None or len(records) == expected_count
    audit = {
        "run_manifest": str(run_manifest.resolve()),
        "latest_record_count": len(latest),
        "ok_report_count": len(records),
        "error_count": len(errors),
        "expected_count": expected_count,
        "required_transport": required_transport,
        "expected_count_ok": expected_ok,
        "errors": errors,
        "duplicate_report_hashes": duplicate_reports,
        "repeated_content_line_threshold": repeat_threshold,
        "repeated_content_lines": repeated_lines,
        "old_template_report_count": sum(bool(record["old_template_hits"]) for record in records),
        "title_warning_report_count": len(title_warning_records),
        "title_warning_records": title_warning_records,
        "abnormal_reports": abnormal,
        "reports": records,
    }
    audit["ok"] = (
        expected_ok
        and not errors
        and not duplicate_reports
        and not abnormal
        and not repeated_lines
    )
    return audit


def markdown_summary(audit: dict) -> str:
    lines = [
        "# EMARX 逐篇精读全量审计",
        "",
        f"- 最新记录：{audit['latest_record_count']}",
        f"- 合格报告：{audit['ok_report_count']}",
        f"- 失败记录：{audit['error_count']}",
        f"- 预期数量：{audit['expected_count']}",
        f"- 要求调用通道：{audit['required_transport']}",
        f"- 报告哈希重复组：{len(audit['duplicate_report_hashes'])}",
        f"- 重复长句：{len(audit['repeated_content_lines'])}",
        f"- 旧版套话报告：{audit['old_template_report_count']}",
        f"- 标题一致性警告报告：{audit.get('title_warning_report_count', 0)}",
        f"- 异常报告：{len(audit['abnormal_reports'])}",
        f"- 机械审计结论：{'通过' if audit['ok'] else '未通过'}",
        "",
        "> 机械审计不能替代主模型对原文、报告和最终写作规律的语义复核。",
    ]
    if audit["errors"]:
        lines.extend(["", "## 失败记录", ""])
        lines.extend(f"- {row.get('index')}: {row.get('name')} - {row.get('error', row.get('status'))}" for row in audit["errors"])
    if audit["abnormal_reports"]:
        lines.extend(["", "## 异常报告", ""])
        lines.extend(f"- {row['index']}: {row['name']} - {', '.join(row['reasons'])}" for row in audit["abnormal_reports"])
    if audit.get("title_warning_records"):
        lines.extend(["", "## 标题一致性警告", ""])
        for row in audit["title_warning_records"][:100]:
            samples = "；".join(row.get("title_warnings", [])[:3])
            lines.append(f"- {row['index']}: {row['name']} - {row['title_warning_count']} 项；{samples}")
    if audit["repeated_content_lines"]:
        lines.extend(["", "## 跨报告重复长句", ""])
        for item in audit["repeated_content_lines"][:100]:
            lines.append(f"- {item['report_count']} 篇：{item['line']}")
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-manifest", required=True, type=Path)
    parser.add_argument("--output-json", required=True, type=Path)
    parser.add_argument("--output-md", required=True, type=Path)
    parser.add_argument("--expected-count", type=int)
    parser.add_argument("--repeat-threshold", type=int, default=8)
    parser.add_argument("--required-transport", choices=("cli-yolo", "api"))
    args = parser.parse_args()

    audit = build_audit(
        args.run_manifest,
        args.expected_count,
        args.repeat_threshold,
        args.required_transport,
    )
    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_md.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(json.dumps(audit, ensure_ascii=False, indent=2), encoding="utf-8")
    args.output_md.write_text(markdown_summary(audit), encoding="utf-8")
    print(json.dumps({"ok": audit["ok"], "json": str(args.output_json), "md": str(args.output_md)}, ensure_ascii=False))
    return 0 if audit["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
