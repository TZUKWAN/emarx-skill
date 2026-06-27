"""Synthesize EMARX deep-reading reports into corpus-level writing guidance.

The script reads every per-paper report, extracts relevant sections, asks an
OpenAI-compatible Qwen endpoint for batch syntheses, then combines those batch
outputs into a final Chinese corpus synthesis. API credentials are read only
from environment variables.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import time
import urllib.error
import urllib.request
from pathlib import Path


SECTION_PATTERNS = [
    "真实结构地图",
    "原文结构地图",
    "摘要",
    "引言",
    "主体",
    "结论",
    "收束",
    "文章特有的论证链",
    "写作节奏",
    "语言与表达",
    "可迁移方法",
    "不可照搬",
    "不确定项",
]


SYSTEM_PROMPT = """你是中文人文社科学术论文写作规律的语料综合助手。

你只能基于给出的逐篇精读报告摘录做归纳，不能编造语料之外的结论。
你的任务不是写论文，也不是设计模板，而是把真实论文中反复出现的结构、论证、语言和节奏规律压缩成可供 EMARX 主模型复核的证据层总结。

必须遵守：
1. 不输出固定段落模板、句长比例、标题公式或万能流程。
2. 区分“语料中常见的倾向”和“可以写入技能的生成原则”。
3. 把摘要、引言、主体结构、二级标题、段落推进、语言表达、写作节奏、文献进入、结论收束分别总结。
4. 特别指出哪些写法会让文章变成说明书、综述、政策清单、AI腔或空洞口号。
5. 语言使用中文，平实、准确、有学术判断。
"""


def call_api(base_url: str, api_key: str, model: str, prompt: str, timeout: int, max_tokens: int) -> str:
    endpoint = base_url.rstrip("/") + "/chat/completions"
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.2,
        "max_tokens": max_tokens,
        "chat_template_kwargs": {"enable_thinking": False},
    }
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    request = urllib.request.Request(
        endpoint,
        data=data,
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        result = json.loads(response.read().decode("utf-8"))
    return str(result["choices"][0]["message"]["content"]).strip()


def split_sections(text: str) -> list[tuple[str, str]]:
    matches = list(re.finditer(r"^#{1,4}\s+(.+?)\s*$", text, flags=re.M))
    sections: list[tuple[str, str]] = []
    if not matches:
        return [("全文", text)]
    for i, match in enumerate(matches):
        start = match.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        sections.append((match.group(1).strip(), text[start:end].strip()))
    return sections


def relevant_excerpt(path: Path, per_report_chars: int) -> str:
    text = path.read_text(encoding="utf-8", errors="replace")
    text = text.split("\n\n---\n\n# 程序回填的逐字证据", 1)[0]
    selected: list[str] = []
    for title, body in split_sections(text):
        if any(pattern in title for pattern in SECTION_PATTERNS):
            compact = re.sub(r"\n{3,}", "\n\n", body).strip()
            if compact:
                selected.append(f"### {title}\n{compact}")
    if not selected:
        selected = [text[:per_report_chars]]
    excerpt = "\n\n".join(selected)
    if len(excerpt) > per_report_chars:
        excerpt = excerpt[:per_report_chars] + "\n...[单篇摘录截断]"
    return f"## {path.name}\n{excerpt}"


def batches(items: list[str], max_chars: int) -> list[list[str]]:
    result: list[list[str]] = []
    current: list[str] = []
    size = 0
    for item in items:
        if current and size + len(item) > max_chars:
            result.append(current)
            current = []
            size = 0
        current.append(item)
        size += len(item)
    if current:
        result.append(current)
    return result


def batch_prompt(batch_no: int, total: int, batch: list[str]) -> str:
    return f"""下面是 EMARX 对 450 篇工作空间论文逐篇精读报告的第 {batch_no}/{total} 批摘录。

请做本批综合。不要写成模板，不要给句长比例，不要把规律变成固定公式。请输出：

1. 本批论文的结构推进方式，特别是一级标题和二级标题如何服务论证。
2. 摘要的常见写法，尤其主语、对象进入、问题收束和判断落点。
3. 引言如何把材料、政策、文献或现实语境转化为学术问题。
4. 主体部分怎样逐节推进，而不是并列罗列。
5. 段落如何起笔、承接、转折、用材料、落判断。
6. 语言和节奏的可迁移原则，注意不要量化成比例。
7. 最应该写进 EMARX 的正向生成原则。
8. 必须避免的坏稿信号。

本批摘录：

{chr(10).join(batch)}
"""


def final_prompt(batch_summaries: list[str]) -> str:
    return f"""下面是 450 篇论文精读报告分批综合的结果。请合成为一份 EMARX v7 全量语料综合报告。

要求：
1. 必须用中文。
2. 不要输出论文模板。
3. 明确区分可写入技能的原则、只可作为后台判断的观察、必须避免的失败模式。
4. 特别服务于中文学理思辨论文写作：选题、标题层级、摘要、引言、主体三到五章、二级标题、段落推进、文献进入、结论、语言质感、节奏。
5. 语言要平实、准确、有学术判断，不要自造新词。

分批综合如下：

{chr(10).join(batch_summaries)}
"""


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--reports-dir", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--model", default=os.environ.get("QWEN_MODEL", "Qwen3.5-122B-A10B"))
    parser.add_argument("--batch-chars", type=int, default=50000)
    parser.add_argument("--per-report-chars", type=int, default=2200)
    parser.add_argument("--timeout", type=int, default=900)
    parser.add_argument("--max-tokens", type=int, default=10000)
    args = parser.parse_args()

    base_url = os.environ.get("QWEN_API_BASE_URL") or os.environ.get("OPENAI_BASE_URL")
    api_key = os.environ.get("QWEN_API_KEY") or os.environ.get("OPENAI_API_KEY")
    if not base_url or not api_key:
        raise SystemExit("Set QWEN_API_BASE_URL and QWEN_API_KEY in the environment.")

    args.output_dir.mkdir(parents=True, exist_ok=True)
    reports = sorted(args.reports_dir.glob("*.md"))
    excerpts = [relevant_excerpt(path, args.per_report_chars) for path in reports]
    grouped = batches(excerpts, args.batch_chars)

    batch_summaries: list[str] = []
    for i, group in enumerate(grouped, 1):
        out_path = args.output_dir / f"batch-{i:02d}-of-{len(grouped):02d}.md"
        if out_path.exists():
            summary = out_path.read_text(encoding="utf-8")
        else:
            summary = call_api(
                base_url=base_url,
                api_key=api_key,
                model=args.model,
                prompt=batch_prompt(i, len(grouped), group),
                timeout=args.timeout,
                max_tokens=args.max_tokens,
            )
            out_path.write_text(summary + "\n", encoding="utf-8")
            time.sleep(0.5)
        batch_summaries.append(f"# 批次 {i}\n\n{summary}")
        print(json.dumps({"batch": i, "total": len(grouped), "output": str(out_path)}, ensure_ascii=False), flush=True)

    final = call_api(
        base_url=base_url,
        api_key=api_key,
        model=args.model,
        prompt=final_prompt(batch_summaries),
        timeout=args.timeout,
        max_tokens=args.max_tokens,
    )
    final_path = args.output_dir / "corpus-synthesis-v7.md"
    final_path.write_text(final + "\n", encoding="utf-8")
    manifest = {
        "reports": len(reports),
        "batches": len(grouped),
        "batch_chars": args.batch_chars,
        "per_report_chars": args.per_report_chars,
        "model": args.model,
        "final": str(final_path),
    }
    (args.output_dir / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(manifest, ensure_ascii=False), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
