#!/usr/bin/env python
"""Append durable user feedback to the EMARX user research profile."""

from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--profile", required=True)
    parser.add_argument("--topic", required=True)
    parser.add_argument("--feedback", required=True)
    parser.add_argument("--action", default="待后续写作时遵循")
    args = parser.parse_args()

    profile = Path(args.profile)
    if not profile.exists():
        profile.parent.mkdir(parents=True, exist_ok=True)
        profile.write_text("# EMARX User Research Profile\n\n", encoding="utf-8")

    stamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    entry = (
        "\n"
        f"## Feedback {stamp}\n\n"
        f"- Topic: {args.topic}\n"
        f"- Feedback: {args.feedback}\n"
        f"- Action: {args.action}\n"
    )
    with profile.open("a", encoding="utf-8") as handle:
        handle.write(entry)
    print(profile)


if __name__ == "__main__":
    main()
