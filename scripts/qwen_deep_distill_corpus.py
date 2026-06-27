#!/usr/bin/env python
"""Use Qwen to produce evidence-based, per-paper deep-reading reports.

The script is resumable. It reads the verified full-text extraction referenced by
the structure index, sends every page to Qwen, and stores one report plus one
machine-readable metadata record per paper. Qwen performs read-only extraction
and compression; the reports remain evidence that the main model must verify.
"""

from __future__ import annotations

import argparse
import concurrent.futures
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import threading
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Iterable


PAGE_RE = re.compile(r"(?m)^\[\[p(\d+)(?::L\d+)?\]\]")
LOCATION_RE = re.compile(r"\[\[p(\d+):L(\d+)(?:-L(\d+))?\]\]")
CHINESE_RE = re.compile(r"[\u4e00-\u9fff]")
OLD_TEMPLATE_PHRASES = (
    "围绕标题展开解释、判断与材料支撑",
    "中等长度句子为主，兼顾解释与推进",
    "以背景或语境打开论述；用问题/风险推动论证转入",
    "主体单元一",
    "主体单元二",
)

STRUCTURE_SECTION_RE = re.compile(
    r"(?:真实结构地图|原文结构地图|主体逐节(?:精读|拆解))(.*?)(?:\n##\s+\d+\.?\s*(?:摘要|引言|文章特有|写作节奏|语言|可迁移|结论)|\Z)",
    re.S,
)
CLAIMED_TITLE_LINE_RE = re.compile(
    r"^\s*(?:[-*]\s*)?(?:#{2,6}\s*)?(?:\*\*)?"
    r"(?:(?:第[一二三四五六七八九十]+(?:部分|章|节)|[一二三四五六七八九十]+、|\(?[一二三四五六七八九十]+\)?|[0-9]+(?:\.[0-9]+)*[.、])\s*)?"
    r"([^：:\[\]\n]{4,36}(?:[：:][^：:\[\]\n]{4,60})?)"
)

SYSTEM_PROMPT = """你是中文人文社会科学论文的全文精读助手。你的任务只有读取、定位、还原和压缩，不负责设计写作技能，也不负责形成跨论文总体结论。

必须遵守：
1. 只依据给出的论文全文，不依据题名猜测，不补造缺失内容。
2. 每项分析附带 [[pN:LNNNN]] 页码行号；连续证据可写 [[pN:LNNNN-LNNNN]]。
3. 保留论文自身的结构和差异，不套用固定五步逻辑，不使用预设风格标签。
4. 明确区分摘要、引言、正文、结论、参考文献和PDF提取噪声。
5. 若双栏抽取导致错序，指出错序，不自行编造顺序。
6. 禁止输出“主体单元一/二”“中等长度句子为主，兼顾解释与推进”“围绕标题展开解释、判断与材料支撑”等万能话术。
7. 不提出EMARX修改方案，不做最终质量判决。报告是供主模型复核的证据层。
8. 不要手抄或改写原文充当直接引语。只返回证据位置和你的分析，程序会从原始全文自动回填逐字证据。
9. 不使用外部知识判断当前年份、作者身份、案例真伪或文献真伪。只记录文本明确呈现的内容和提取层面的不确定性。
10. 不报告未经逐项计数的词频，不用“出现若干次”制造精确感。
11. 页码行号必须真实存在。连续范围只能写同一页内的行号，例如 [[p3:L0100-L0112]]；跨页内容必须拆成多个定位，例如 [[p3:L0100-L0120]][[p4:L0121-L0130]]，不得写成单个跨页范围。
12. 禁止使用“段落群1/2/3”“段落群<N>”“摘要与引言”这类占位式小标题来替代原文结构。若原文没有标题，应直接用该段实际讨论对象命名，例如“从改革开放记忆进入思想政治教育问题”。
"""

REPORT_REQUEST = """请对下面这篇论文进行逐页、全文、非模板化精读，形成一份文章专属的中文Markdown证据报告。

报告必须包含但不限于以下内容；可以根据论文实际结构调整小节名称和顺序，不得为了齐整虚构内容：

1. 文献身份与提取边界：核对真实题名、作者、文献形态，列出刊头、双栏错序、断行、基金信息、参考文献混入等噪声，并给出页码行号。
2. 原文结构地图：逐项列出真实一级、二级、三级标题及页码；没有标题时，按真实语义转折还原段落群，但明确注明“原文无标题”。
3. 摘要精读：识别摘要的每个语义单元，说明其前后关系、主语安排、动词和收束方式；逐项附原文证据。若没有显式摘要，明确写无，不得把第一段冒充摘要。
4. 引言精读：按实际段落或论证转折解释问题怎样进入、材料怎样出现、已有讨论怎样被处理、正文入口怎样形成。不得只写“背景—问题—意义”。
5. 主体逐节精读：沿真实标题逐节说明每一节内部的段落推进、论点与根据、概念变化、材料进入、转折和判断落点。每节至少给出两处页码证据；短文可按实际情况减少。
6. 结论或收束精读：说明它怎样回收前文、提升或限制判断。没有独立结论时，指出实际收束位置。
7. 文章特有的论证链：用这篇论文自己的概念和材料还原论证，不得套用通用五步框架。
8. 写作节奏：选择至少8个有代表性的句子或相邻句组，逐例说明句长变化、停顿、递进、转折和收束在该处承担的论证作用。证据不足时按实际数量。
9. 语言与表达：分别分析段首、主语、动词、概念复现、过渡、引用进入、判断落点和标点使用；每一类都要有具体例句，不能只给标签。
10. 可迁移方法与不可照搬之处：只总结有原文证据的具体方法，并说明适用条件。不得输出适用于所有论文的空泛建议。
11. 证据定位台账：最后列出至少20条“页码行号—它证明了什么”。短文按证据实际数量，但不得用同一位置重复凑数。不要手抄原文。
12. 不确定项：列出因提取错序、缺页或元数据不全而不能确认的内容。

证据定位要求：所有页码行号必须来自下方论文全文中已经出现的定位标记。连续范围只能在同一页内部使用；如果一个内容跨越两页或更多页，必须拆成多个定位，不能把不同页的行号合并到一个 `[[pN:L起-L止]]` 中。

覆盖要求：报告至少引用论文中10个不同页码；若论文不足10页，则覆盖全部页码。每个连续页块都必须在综合报告中留下证据，不能在合并时丢页。短文确实无法满足时，必须在“不确定项”中说明原因。

结构命名要求：不得使用“段落群1/2/3”“段落群<N>”“摘要与引言”等占位式标题。没有原文标题时，用该段实际对象或论证动作命名，标题必须随文章而变。

论文元数据：
{metadata}

论文全文：
{text}
"""

CHUNK_REQUEST = """下面是同一篇超长论文的第 {chunk_no}/{chunk_total} 个连续页块，覆盖 {page_range}。只做本页块的细读证据提取，不形成全篇结论。

请沿原文顺序完成以下工作：
1. 列出本页块出现的每一个真实标题，不得遗漏二级、三级标题。
2. 按自然段或受双栏错序影响的段落组合依次说明每一组具体写了什么、怎样承接前文、提出了什么根据或判断。不要使用“段落群1/2/3”作小标题，不要把整页压成一句通用概括。
3. 记录概念的引入、复现、转义和限定，材料、政策、案例与文献在何处进入。
4. 选择本页块最有代表性的句子或相邻句组，分析句式、节奏、主语、动词、过渡、引用和判断落点。
5. 每项附 [[pN:LNNNN]] 页码行号；连续证据可写成同页行号范围。跨页证据必须拆成多个定位，不能写成单个跨页范围。不要手抄原文，程序会自动回填。
6. 标明双栏错序、断行、页眉页脚、脚注或参考文献污染。

不得套用固定段落类型或万能总结，不得跳过看似次要的段落。

论文元数据：
{metadata}

本页块全文：
{text}
"""

MERGE_REQUEST = """下面是同一篇论文全部页块的逐页证据。请在不丢失页码证据的前提下，合并为一份文章专属的完整精读报告。

必须覆盖文献身份与提取边界、真实结构地图、摘要、引言、主体逐节、结论、文章特有论证链、至少8组写作节奏实例、语言表达实例、可迁移方法及其适用条件、证据定位台账、不确定项。原文存在的每个一级、二级和三级标题都必须在主体拆解中出现；不能只挑代表性小节。所有判断继续保留 [[pN:LNNNN]] 定位，不要复制原文。页码行号必须真实存在，连续范围只能在同一页内部使用，跨页内容必须拆成多个定位。合并报告必须保留每个页块的证据，至少引用10个不同页码；论文不足10页则覆盖全部页码。不得使用“段落群1/2/3”“段落群<N>”“摘要与引言”这类占位式标题。不得把不同页块压缩成通用五步框架，不得使用万能标签，不得补充页块证据以外的时间判断或事实判断。

论文元数据：
{metadata}

全部页块证据：
{chunk_reports}
"""


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def normalize_for_title_match(text: str) -> str:
    return "".join(re.findall(r"[\u4e00-\u9fffA-Za-z0-9]", text))


def strip_report_markup(text: str) -> str:
    text = re.sub(r"\[\[p\d+:L\d+(?:-L\d+)?\]\]", "", text)
    text = re.sub(r"[`*_#>]", "", text)
    text = re.sub(r"（.*?）|\(.*?\)", "", text)
    return text.strip(" -—:：。；;，,")


def likely_claimed_source_titles(report: str) -> list[str]:
    """Extract phrases that the report presents as source headings.

    This deliberately avoids the whole report. Analytical labels in later
    sections may be useful but are not original headings. The validator only
    checks sections where the report claims to map or deconstruct the source
    structure.
    """
    candidates: list[str] = []
    seen: set[str] = set()
    for section_match in STRUCTURE_SECTION_RE.finditer(report):
        section = section_match.group(1)
        for raw_line in section.splitlines():
            raw_stripped = raw_line.lstrip()
            heading_like = raw_stripped.startswith("#") or "**" in raw_stripped[:80]
            if not heading_like:
                continue
            line = strip_report_markup(raw_line)
            if not line:
                continue
            if any(
                word in line
                for word in (
                    "核心逻辑",
                    "关键判断",
                    "理论支撑",
                    "子点",
                    "定位",
                    "注：",
                    "噪声",
                    "证据",
                    "总述",
                    "必要性",
                    "操作",
                    "适用条件",
                    "功能层",
                    "价值层",
                    "路径层",
                )
            ):
                continue
            match = CLAIMED_TITLE_LINE_RE.match(line)
            if not match:
                continue
            candidate = strip_report_markup(match.group(1))
            if "：" in candidate or ":" in candidate:
                left, right = re.split(r"[：:]", candidate, maxsplit=1)
                if len(normalize_for_title_match(right)) >= 6:
                    candidate = right
                elif len(normalize_for_title_match(left)) >= 6:
                    candidate = left
            candidate = re.sub(r"^(?:第一部分|第二部分|第三部分|第四部分|第五部分)[：:、]?", "", candidate)
            candidate = strip_report_markup(candidate)
            normalized = normalize_for_title_match(candidate)
            if len(CHINESE_RE.findall(candidate)) < 6:
                continue
            if candidate in ("摘要与引言", "参考文献", "结论", "引言", "摘要"):
                continue
            if normalized and normalized not in seen:
                seen.add(normalized)
                candidates.append(candidate)
    return candidates


def has_unnegated_phrase(text: str, phrase: str) -> bool:
    for match in re.finditer(re.escape(phrase), text):
        context = text[max(0, match.start() - 20) : match.end() + 20]
        if any(marker in context for marker in ("无明显", "未检测到", "没有", "不得", "禁止", "避免", "不使用", "不要")):
            continue
        return True
    return False


def safe_name(index: int, name: str) -> str:
    stem = Path(name).stem
    stem = re.sub(r"[<>:\"/\\|?*\x00-\x1f]", "_", stem).strip(" ._")
    digest = hashlib.sha1(name.encode("utf-8")).hexdigest()[:8]
    return f"{index:03d}_{stem[:88]}_{digest}"


def page_chunks(text: str, max_chars: int) -> list[tuple[str, str]]:
    starts = list(PAGE_RE.finditer(text))
    if not starts:
        return [("全文（无可靠页码标记）", text)]

    pages: list[tuple[int, str]] = []
    for pos, match in enumerate(starts):
        end = starts[pos + 1].start() if pos + 1 < len(starts) else len(text)
        pages.append((int(match.group(1)), text[match.start() : end]))

    chunks: list[tuple[str, str]] = []
    current: list[tuple[int, str]] = []
    size = 0
    for page_no, page_text in pages:
        if current and size + len(page_text) > max_chars:
            chunks.append((f"p{current[0][0]}-p{current[-1][0]}", "".join(p[1] for p in current)))
            current = []
            size = 0
        current.append((page_no, page_text))
        size += len(page_text)
    if current:
        chunks.append((f"p{current[0][0]}-p{current[-1][0]}", "".join(p[1] for p in current)))
    return chunks


def number_source_lines(text: str) -> tuple[str, dict[int, dict]]:
    numbered: list[str] = []
    mapping: dict[int, dict] = {}
    current_page = 0
    for line_number, raw in enumerate(text.splitlines(), 1):
        match = re.match(r"^\[\[p(\d+)\]\]\s?(.*)$", raw)
        if match:
            current_page = int(match.group(1))
            body = match.group(2)
        else:
            body = raw
        location = f"[[p{current_page}:L{line_number:04d}]]"
        numbered.append(f"{location} {body}")
        mapping[line_number] = {"page": current_page, "text": body}
    return "\n".join(numbered), mapping


def normalize_report_locations(report: str, mapping: dict[int, dict]) -> tuple[str, list[dict]]:
    corrections: list[dict] = []

    def replace(match: re.Match) -> str:
        stated_page = int(match.group(1))
        start = int(match.group(2))
        end_text = match.group(3)
        end = int(end_text) if end_text else start
        if end < start and start in mapping and end in mapping:
            corrections.append(
                {
                    "original": match.group(0),
                    "corrected_range": [end, start],
                }
            )
            start, end = end, start
        if start not in mapping:
            return match.group(0)
        actual_page = int(mapping[start]["page"])
        if (
            end not in mapping
            or end < start
            or int(mapping[end]["page"]) != actual_page
        ):
            corrections.append(
                {
                    "original": match.group(0),
                    "corrected_to_single_line": start,
                    "reason": "invalid_or_cross_page_range_end",
                }
            )
            end = start
        if actual_page != stated_page:
            corrections.append(
                {
                    "original": match.group(0),
                    "corrected_page": actual_page,
                    "line": start,
                }
            )
        suffix = f"-L{end:04d}" if end != start else ""
        return f"[[p{actual_page}:L{start:04d}{suffix}]]"

    return LOCATION_RE.sub(replace, report), corrections


def evidence_from_locations(report: str, mapping: dict[int, dict]) -> tuple[str, dict]:
    found: list[dict] = []
    invalid: list[str] = []
    broad: list[str] = []
    seen = set()
    for page_text, start_text, end_text in LOCATION_RE.findall(report):
        page = int(page_text)
        start = int(start_text)
        end = int(end_text) if end_text else start
        key = (page, start, end)
        if key in seen:
            continue
        seen.add(key)
        if start not in mapping or end not in mapping or end < start:
            invalid.append(f"p{page}:L{start:04d}-L{end:04d}")
            continue
        if end - start > 20:
            broad.append(f"p{page}:L{start:04d}-L{end:04d}")
            continue
        lines = [mapping[number] for number in range(start, end + 1) if number in mapping]
        if not lines or lines[0]["page"] != page:
            invalid.append(f"p{page}:L{start:04d}-L{end:04d}")
            continue
        exact = " ".join(
            str(line["text"]).strip() for line in lines if str(line["text"]).strip()
        )
        found.append(
            {
                "location": f"[[p{page}:L{start:04d}"
                + (f"-L{end:04d}" if end != start else "")
                + "]]",
                "page": page,
                "start": start,
                "end": end,
                "exact": exact,
            }
        )

    appendix = [
        "# 程序回填的逐字证据",
        "",
        "以下原文由程序依据千问返回的页码行号直接回填，未经过模型改写。",
        "",
    ]
    for index, item in enumerate(found, 1):
        appendix.extend(
            [
                f"## 证据 {index} {item['location']}",
                "",
                item["exact"] or "（该行为空）",
                "",
            ]
        )
    return "\n".join(appendix), {
        "locations": found,
        "invalid_locations": invalid,
        "broad_locations": broad,
    }


def response_content(payload: dict) -> str:
    choices = payload.get("choices") or []
    if not choices:
        raise ValueError(f"API response has no choices: {str(payload)[:500]}")
    content = (choices[0].get("message") or {}).get("content", "")
    if isinstance(content, str):
        value = content.strip()
        if not value or value.lower() == "none":
            raise ValueError("API returned empty content")
        return value
    if isinstance(content, list):
        parts = []
        for item in content:
            if isinstance(item, dict) and item.get("type") == "text":
                parts.append(str(item.get("text", "")))
        value = "\n".join(parts).strip()
        if not value:
            raise ValueError("API returned empty content")
        return value
    value = str(content).strip()
    if not value or value.lower() == "none":
        raise ValueError("API returned empty content")
    return value


def call_qwen(
    *,
    base_url: str,
    api_key: str,
    model: str,
    prompt: str,
    timeout: int,
    retries: int,
    max_tokens: int,
    transport: str,
) -> tuple[str, dict]:
    if transport == "cli-yolo":
        return call_qwen_cli_yolo(
            base_url=base_url,
            api_key=api_key,
            model=model,
            prompt=prompt,
            timeout=timeout,
            retries=retries,
            max_tokens=max_tokens,
        )
    url = base_url.rstrip("/") + "/chat/completions"
    body = {
        "model": model,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.15,
        "max_tokens": max_tokens,
        # The OpenAI-compatible Qwen endpoint used in this workspace defaults to
        # emitting reasoning tokens. For extraction jobs we need report text, not
        # hidden reasoning, and the endpoint honors this nested flag.
        "chat_template_kwargs": {"enable_thinking": False},
    }
    encoded = json.dumps(body, ensure_ascii=False).encode("utf-8")
    last_error: Exception | None = None
    for attempt in range(1, retries + 1):
        request = urllib.request.Request(
            url,
            data=encoded,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                payload = json.loads(response.read().decode("utf-8"))
            return response_content(payload), payload.get("usage") or {}
        except (urllib.error.URLError, TimeoutError, ValueError, json.JSONDecodeError) as exc:
            last_error = exc
            if attempt < retries:
                delay = min(20, 2**attempt)
                print(
                    f"Qwen request attempt {attempt}/{retries} failed: "
                    f"{type(exc).__name__}: {exc}; retrying in {delay}s",
                    file=sys.stderr,
                    flush=True,
                )
                time.sleep(delay)
    raise RuntimeError(f"Qwen request failed after {retries} attempts: {last_error}")


def call_qwen_cli_yolo(
    *,
    base_url: str,
    api_key: str,
    model: str,
    prompt: str,
    timeout: int,
    retries: int,
    max_tokens: int,
) -> tuple[str, dict]:
    executable = shutil.which("qwen.cmd") or shutil.which("qwen")
    if not executable:
        raise FileNotFoundError("Qwen Code CLI was not found on PATH.")
    command = [
        executable,
        "--yolo",
        "--bare",
        "--max-tool-calls",
        "0",
        "--max-wall-time",
        f"{timeout}s",
        "--auth-type",
        "openai",
        "--model",
        model,
        "--system-prompt",
        SYSTEM_PROMPT,
        "--output-format",
        "json",
    ]
    environment = os.environ.copy()
    environment["OPENAI_BASE_URL"] = base_url
    environment["OPENAI_API_KEY"] = api_key
    environment["QWEN_CODE_SUPPRESS_YOLO_WARNING"] = "1"
    environment["QWEN_CODE_MAX_OUTPUT_TOKENS"] = str(max_tokens)
    combined_prompt = prompt
    last_error: Exception | None = None
    for attempt in range(1, retries + 1):
        try:
            completed = subprocess.run(
                command,
                input=combined_prompt,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=timeout + 60,
                env=environment,
                check=False,
            )
            if completed.returncode != 0:
                detail = (completed.stderr or completed.stdout)[-2000:]
                raise RuntimeError(f"Qwen CLI exit {completed.returncode}: {detail}")
            raw_output = completed.stdout.strip()
            plain_content: str | None = None
            try:
                decoded_output = json.loads(raw_output)
                if isinstance(decoded_output, str):
                    plain_content = decoded_output.strip()
                    events = []
                else:
                    events = decoded_output
            except json.JSONDecodeError:
                events = None
                string_candidates: list[str] = []
                decoder = json.JSONDecoder()
                for match in re.finditer(r"[\[\"]", raw_output):
                    try:
                        candidate, _ = decoder.raw_decode(raw_output, match.start())
                    except json.JSONDecodeError:
                        continue
                    if isinstance(candidate, list) and candidate and isinstance(candidate[0], dict):
                        events = candidate
                        break
                    if isinstance(candidate, str) and len(candidate.strip()) >= 100:
                        string_candidates.append(candidate.strip())
                if events is None and string_candidates:
                    plain_content = max(string_candidates, key=len)
                    events = []
                if (
                    events is None
                    and len(raw_output) >= 1000
                    and "##" in raw_output
                    and re.search(r"\[\[p\d+:L\d+", raw_output)
                ):
                    plain_content = raw_output
                    events = []
                if events is None:
                    raise ValueError(
                        f"Qwen CLI output contains no JSON event array: {raw_output[-1200:]}"
                    )
            if plain_content:
                return plain_content, {
                    "transport": "cli-yolo",
                    "permission_mode": "yolo",
                    "tool_calls": 0,
                    "max_output_tokens": max_tokens,
                    "cli_output_shape": "plain_text_or_json_string",
                    "usage_unavailable": True,
                }
            if not isinstance(events, list):
                raise ValueError("Qwen CLI JSON output is not an event list.")
            result_event = next(
                (
                    event
                    for event in reversed(events)
                    if event.get("type") == "result" and event.get("subtype") == "success"
                ),
                None,
            )
            if result_event is None:
                raise ValueError("Qwen CLI did not return a success result event.")
            tool_calls = ((result_event.get("stats") or {}).get("tools") or {}).get("totalCalls", 0)
            if tool_calls:
                raise RuntimeError(f"Qwen CLI unexpectedly used {tool_calls} tools.")
            content = str(result_event.get("result") or "").strip()
            if not content:
                assistant_parts: list[str] = []
                for event in events:
                    if event.get("type") != "assistant":
                        continue
                    message = event.get("message") or {}
                    for part in message.get("content") or []:
                        if part.get("type") == "text" and str(part.get("text") or "").strip():
                            assistant_parts.append(str(part["text"]).strip())
                content = "\n\n".join(assistant_parts).strip()
            if not content:
                event_summary = [
                    {
                        "type": event.get("type"),
                        "subtype": event.get("subtype"),
                        "stop_reason": (event.get("message") or {}).get("stop_reason"),
                        "usage": event.get("usage") or (event.get("message") or {}).get("usage"),
                        "content_parts": [
                            {
                                "type": part.get("type"),
                                "characters": len(str(part.get("text") or part.get("thinking") or "")),
                            }
                            for part in ((event.get("message") or {}).get("content") or [])
                        ],
                    }
                    for event in events[-8:]
                ]
                raise ValueError(f"Qwen CLI returned empty content; events={event_summary}")
            usage = dict(result_event.get("usage") or {})
            usage.update(
                {
                    "transport": "cli-yolo",
                    "permission_mode": "yolo",
                    "tool_calls": tool_calls,
                    "duration_ms": result_event.get("duration_ms"),
                    "max_output_tokens": max_tokens,
                }
            )
            return content, usage
        except (subprocess.TimeoutExpired, RuntimeError, ValueError, json.JSONDecodeError) as exc:
            last_error = exc
            if attempt < retries:
                delay = min(20, 2**attempt)
                print(
                    f"Qwen CLI yolo attempt {attempt}/{retries} failed: "
                    f"{type(exc).__name__}: {exc}; retrying in {delay}s",
                    file=sys.stderr,
                    flush=True,
                )
                time.sleep(delay)
    raise RuntimeError(f"Qwen CLI yolo failed after {retries} attempts: {last_error}")


def quality_check(
    report: str, item: dict, source_text: str, location_data: dict
) -> tuple[list[str], dict]:
    problems: list[str] = []
    normalized_source = normalize_for_title_match(source_text)
    text_chars = int(item.get("chars") or 0)
    pages = int(item.get("pages") or 0)
    minimum_chars = min(5000, max(1200, text_chars // 3))
    if len(report) < minimum_chars:
        problems.append(f"report_too_short:{len(report)}<{minimum_chars}")
    source_pages = set(PAGE_RE.findall(source_text))
    effective_pages = len(source_pages) or pages
    page_refs = {page for page, _, _ in LOCATION_RE.findall(report)}
    minimum_pages = min(10, max(1, effective_pages))
    if len(page_refs) < minimum_pages:
        problems.append(f"insufficient_page_evidence:{len(page_refs)}<{minimum_pages}")
    for phrase in OLD_TEMPLATE_PHRASES:
        if has_unnegated_phrase(report, phrase):
            problems.append(f"old_template_phrase:{phrase}")
    if "不确定" not in report and "噪声" not in report:
        problems.append("missing_uncertainty_or_noise_section")
    invalid_locations = location_data.get("invalid_locations") or []
    if invalid_locations:
        problems.append(f"invalid_evidence_locations:{len(invalid_locations)}")
    location_count = len(location_data.get("locations") or [])
    minimum_locations = min(20, max(3, pages * 2))
    if location_count < minimum_locations:
        problems.append(f"insufficient_evidence_locations:{location_count}<{minimum_locations}")
    missing_pages = sorted(source_pages - page_refs, key=int)
    if missing_pages:
        problems.append(f"missing_page_coverage:{','.join(missing_pages[:20])}")
    claimed_titles = likely_claimed_source_titles(report)
    unmatched_titles: list[str] = []
    for title in claimed_titles:
        normalized_title = normalize_for_title_match(title)
        if normalized_title and normalized_title not in normalized_source:
            unmatched_titles.append(title)
    evidence = {
        "evidence_locations": location_count,
        "invalid_locations": invalid_locations[:20],
        "source_pages": len(source_pages),
        "report_pages": len(page_refs),
        "missing_pages": missing_pages,
        "claimed_source_titles_checked": claimed_titles,
        "unmatched_claimed_source_titles": unmatched_titles,
        "title_validation_note": (
            "Title matching is a warning signal. PDF extraction noise and report "
            "analysis labels can create false positives; the main model must review "
            "warnings before synthesizing corpus rules."
        ),
    }
    return problems, evidence


def metadata_text(item: dict) -> str:
    headings = item.get("headings") or []
    compact_headings = [
        {"page": h.get("page"), "level": h.get("level"), "text": h.get("text")}
        for h in headings
    ]
    return json.dumps(
        {
            "name": item.get("name"),
            "source_file": item.get("file"),
            "pages": item.get("pages"),
            "characters": item.get("chars"),
            "extractor_headings_for_reference_only": compact_headings,
        },
        ensure_ascii=False,
        indent=2,
    )


def distill_one(
    *,
    position: int,
    item: dict,
    output_dir: Path,
    base_url: str,
    api_key: str,
    model: str,
    max_input_chars: int,
    chunk_chars: int,
    timeout: int,
    retries: int,
    max_tokens: int,
    transport: str,
    force: bool,
    single_pass: bool,
) -> dict:
    started = time.time()
    stem = safe_name(position, str(item.get("name") or "paper"))
    report_path = output_dir / "reports" / f"{stem}.md"
    metadata_path = output_dir / "metadata" / f"{stem}.json"
    if report_path.exists() and metadata_path.exists() and not force:
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        if metadata.get("status") == "ok":
            metadata["resume_status"] = "skipped_existing"
            return metadata

    text_path = Path(str(item.get("text_file") or ""))
    if not text_path.exists():
        raise FileNotFoundError(f"Missing extracted text: {text_path}")
    text = text_path.read_text(encoding="utf-8", errors="replace")
    numbered_text, line_mapping = number_source_lines(text)
    metadata = metadata_text(item)
    usage_records: list[dict] = []

    if single_pass and len(numbered_text) <= max_input_chars:
        prompt = REPORT_REQUEST.format(metadata=metadata, text=numbered_text)
        report, usage = call_qwen(
            base_url=base_url,
            api_key=api_key,
            model=model,
            prompt=prompt,
            timeout=timeout,
            retries=retries,
            max_tokens=max_tokens,
            transport=transport,
        )
        usage_records.append({"stage": "full_paper", "usage": usage})
        chunks_used = 1
        report, location_corrections = normalize_report_locations(report, line_mapping)
        evidence_appendix, location_data = evidence_from_locations(report, line_mapping)
        report = report + "\n\n---\n\n" + evidence_appendix
    else:
        chunks = page_chunks(numbered_text, chunk_chars)
        chunk_reports: list[str] = []
        chunk_dir = output_dir / "evidence" / stem
        chunk_dir.mkdir(parents=True, exist_ok=True)
        for chunk_index, (page_range, chunk_text) in enumerate(chunks, 1):
            prompt = CHUNK_REQUEST.format(
                chunk_no=chunk_index,
                chunk_total=len(chunks),
                page_range=page_range,
                metadata=metadata,
                text=chunk_text,
            )
            chunk_report, usage = call_qwen(
                base_url=base_url,
                api_key=api_key,
                model=model,
                prompt=prompt,
                timeout=timeout,
                retries=retries,
                max_tokens=max_tokens,
                transport=transport,
            )
            chunk_reports.append(f"\n## 页块 {chunk_index}: {page_range}\n\n{chunk_report}")
            (chunk_dir / f"chunk-{chunk_index:02d}-{page_range}.md").write_text(
                chunk_report.rstrip() + "\n", encoding="utf-8"
            )
            usage_records.append({"stage": f"chunk_{chunk_index}", "usage": usage})
        merge_prompt = MERGE_REQUEST.format(
            metadata=metadata,
            chunk_reports="\n".join(chunk_reports),
        )
        synthesis, usage = call_qwen(
            base_url=base_url,
            api_key=api_key,
            model=model,
            prompt=merge_prompt,
            timeout=timeout,
            retries=retries,
            max_tokens=max_tokens,
            transport=transport,
        )
        usage_records.append({"stage": "merge", "usage": usage})
        chunks_used = len(chunks)
        report_without_evidence = (
            synthesis.rstrip()
            + "\n\n---\n\n# 逐页精读原始证据\n"
            + "\n".join(chunk_reports)
        )
        report_without_evidence, location_corrections = normalize_report_locations(
            report_without_evidence, line_mapping
        )
        evidence_appendix, location_data = evidence_from_locations(
            report_without_evidence, line_mapping
        )
        report = report_without_evidence + "\n\n---\n\n" + evidence_appendix

    problems, evidence_validation = quality_check(
        report, item, text, location_data
    )
    report_path.parent.mkdir(parents=True, exist_ok=True)
    metadata_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(report.rstrip() + "\n", encoding="utf-8")
    record = {
        "index": position,
        "name": item.get("name"),
        "source_file": item.get("file"),
        "text_file": str(text_path),
        "source_sha256": sha256_text(text),
        "source_chars": len(text),
        "source_pages": item.get("pages"),
        "model": model,
        "transport": transport,
        "chunks": chunks_used,
        "report": str(report_path),
        "report_chars": len(report),
        "quality_problems": problems,
        "evidence_validation": evidence_validation,
        "location_corrections": location_corrections,
        "status": "ok" if not problems else "quality_failed",
        "usage": usage_records,
        "elapsed_seconds": round(time.time() - started, 2),
    }
    metadata_path.write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8")
    return record


def selected_items(index: list[dict], names_file: str | None, start: int, limit: int | None) -> list[tuple[int, dict]]:
    rows = [(i, item) for i, item in enumerate(index, 1) if item.get("status") == "ok"]
    if names_file:
        requested = {
            line.strip()
            for line in Path(names_file).read_text(encoding="utf-8").splitlines()
            if line.strip() and not line.lstrip().startswith("#")
        }
        rows = [row for row in rows if str(row[1].get("name")) in requested or str(row[1].get("file")) in requested]
    rows = rows[max(0, start - 1) :]
    if limit is not None:
        rows = rows[:limit]
    return rows


def append_manifest(path: Path, record: dict, lock: threading.Lock) -> None:
    with lock:
        with path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")


def summarize(output_dir: Path, records: Iterable[dict]) -> dict:
    rows = list(records)
    summary = {
        "paper_count": len(rows),
        "ok": sum(1 for row in rows if row.get("status") == "ok"),
        "quality_failed": sum(1 for row in rows if row.get("status") == "quality_failed"),
        "errors": sum(1 for row in rows if row.get("status") == "error"),
        "skipped_existing": sum(1 for row in rows if row.get("resume_status") == "skipped_existing"),
        "records": rows,
    }
    (output_dir / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    return summary


def reaudit_one(position: int, item: dict, output_dir: Path) -> dict:
    stem = safe_name(position, str(item.get("name") or "paper"))
    report_path = output_dir / "reports" / f"{stem}.md"
    metadata_path = output_dir / "metadata" / f"{stem}.json"
    if not report_path.exists() or not metadata_path.exists():
        raise FileNotFoundError(f"Missing existing report or metadata for {item.get('name')}")

    text_path = Path(str(item.get("text_file") or ""))
    source_text = text_path.read_text(encoding="utf-8", errors="replace")
    _, line_mapping = number_source_lines(source_text)
    report = report_path.read_text(encoding="utf-8")
    report = report.split("\n\n---\n\n# 程序回填的逐字证据", 1)[0].rstrip()
    report, corrections = normalize_report_locations(report, line_mapping)
    appendix, location_data = evidence_from_locations(report, line_mapping)
    report = report + "\n\n---\n\n" + appendix
    problems, evidence_validation = quality_check(
        report, item, source_text, location_data
    )
    report_path.write_text(report.rstrip() + "\n", encoding="utf-8")
    record = json.loads(metadata_path.read_text(encoding="utf-8"))
    record.update(
        {
            "report_chars": len(report),
            "quality_problems": problems,
            "evidence_validation": evidence_validation,
            "location_corrections": corrections,
            "status": "ok" if not problems else "quality_failed",
            "reaudited": True,
        }
    )
    metadata_path.write_text(
        json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return record


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--index", required=True, help="structure_index.json")
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--names-file", help="Optional UTF-8 list of exact paper names or paths")
    parser.add_argument("--start", type=int, default=1)
    parser.add_argument("--limit", type=int)
    parser.add_argument("--workers", type=int, default=1)
    parser.add_argument("--model", default=os.environ.get("QWEN_MODEL", "Qwen3.5-122B-A10B"))
    parser.add_argument("--max-input-chars", type=int, default=70000)
    parser.add_argument("--chunk-chars", type=int, default=9000)
    parser.add_argument("--timeout", type=int, default=240)
    parser.add_argument("--retries", type=int, default=3)
    parser.add_argument("--max-tokens", type=int, default=12000)
    parser.add_argument("--transport", choices=("cli-yolo", "api"), default="cli-yolo")
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--single-pass", action="store_true", help="Use one request for short papers; default is page-block deep reading for every paper")
    parser.add_argument("--reaudit-only", action="store_true", help="Rebuild deterministic evidence appendices and quality metadata without API calls")
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    index = json.loads(Path(args.index).read_text(encoding="utf-8"))
    rows = selected_items(index, args.names_file, args.start, args.limit)
    if not rows:
        raise SystemExit("No matching readable papers.")

    if args.reaudit_only:
        manifest = output_dir / "run.jsonl"
        lock = threading.Lock()
        records = []
        for position, item in rows:
            try:
                record = reaudit_one(position, item, output_dir)
            except Exception as exc:
                record = {
                    "index": position,
                    "name": item.get("name"),
                    "status": "error",
                    "error": repr(exc),
                }
            records.append(record)
            append_manifest(manifest, record, lock)
            print(json.dumps({"index": position, "name": item.get("name"), "status": record.get("status")}, ensure_ascii=False), flush=True)
        summary = summarize(output_dir, records)
        print(json.dumps({key: summary[key] for key in ("paper_count", "ok", "quality_failed", "errors", "skipped_existing")}, ensure_ascii=False))
        return 0 if summary["quality_failed"] == 0 and summary["errors"] == 0 else 1

    base_url = os.environ.get("QWEN_API_BASE_URL")
    api_key = os.environ.get("QWEN_API_KEY")
    if not base_url or not api_key:
        raise SystemExit("Set QWEN_API_BASE_URL and QWEN_API_KEY in the environment.")

    manifest = output_dir / "run.jsonl"
    lock = threading.Lock()
    records: list[dict] = []

    def run(row: tuple[int, dict]) -> dict:
        position, item = row
        try:
            record = distill_one(
                position=position,
                item=item,
                output_dir=output_dir,
                base_url=base_url,
                api_key=api_key,
                model=args.model,
                max_input_chars=args.max_input_chars,
                chunk_chars=args.chunk_chars,
                timeout=args.timeout,
                retries=args.retries,
                max_tokens=args.max_tokens,
                transport=args.transport,
                force=args.force,
                single_pass=args.single_pass,
            )
        except Exception as exc:  # Preserve failures for resumable corpus runs.
            record = {
                "index": position,
                "name": item.get("name"),
                "source_file": item.get("file"),
                "status": "error",
                "error": repr(exc),
            }
        append_manifest(manifest, record, lock)
        print(json.dumps({"index": position, "name": item.get("name"), "status": record.get("status")}, ensure_ascii=False), flush=True)
        return record

    with concurrent.futures.ThreadPoolExecutor(max_workers=max(1, args.workers)) as pool:
        for record in pool.map(run, rows):
            records.append(record)

    summary = summarize(output_dir, records)
    print(json.dumps({key: summary[key] for key in ("paper_count", "ok", "quality_failed", "errors", "skipped_existing")}, ensure_ascii=False))
    return 0 if summary["quality_failed"] == 0 and summary["errors"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
