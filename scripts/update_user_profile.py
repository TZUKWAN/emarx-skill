#!/usr/bin/env python
"""Record EMARX feedback without silently promoting it to a global rule."""

from __future__ import annotations

import argparse
import hashlib
from datetime import datetime
from pathlib import Path


VALID_STATUS = {"待复核", "已验证", "已驳回"}
VALID_SCOPE = {"本篇", "同类题目", "候选通则"}


def evidence_record(path_text: str | None) -> tuple[str, str]:
    if not path_text:
        return "未提供", ""
    path = Path(path_text).expanduser().resolve()
    if not path.is_file():
        raise FileNotFoundError(f"反馈证据不存在: {path}")
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    return str(path), digest


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--profile", required=True)
    parser.add_argument("--topic", required=True)
    parser.add_argument("--feedback", required=True)
    parser.add_argument("--scope", choices=sorted(VALID_SCOPE), default="本篇")
    parser.add_argument("--status", choices=sorted(VALID_STATUS), default="待复核")
    parser.add_argument("--evidence", help="可选的论文、批注或审稿文件")
    parser.add_argument("--proposed-action", default="分析形成原因，并在复核后决定是否修改生成协议")
    parser.add_argument("--review-note", default="尚未完成主模型复核")
    args = parser.parse_args()

    evidence_path, evidence_hash = evidence_record(args.evidence)
    profile = Path(args.profile)
    if not profile.exists():
        profile.parent.mkdir(parents=True, exist_ok=True)
        profile.write_text("# EMARX 用户研究画像与反馈记录\n\n", encoding="utf-8")

    stamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = (
        "\n"
        f"## 反馈记录 {stamp}\n\n"
        f"- 题目：{args.topic}\n"
        f"- 用户反馈：{args.feedback}\n"
        f"- 当前状态：{args.status}\n"
        f"- 暂定范围：{args.scope}\n"
        f"- 证据文件：{evidence_path}\n"
        f"- 证据 SHA-256：{evidence_hash or '无'}\n"
        f"- 拟采取动作：{args.proposed_action}\n"
        f"- 复核说明：{args.review_note}\n"
        "- 晋升限制：处于“待复核”状态时不得写入通用生成规则；候选通则须经多篇原文或多次成文验证。\n"
    )
    with profile.open("a", encoding="utf-8") as handle:
        handle.write(entry)
    print(profile)


if __name__ == "__main__":
    main()
