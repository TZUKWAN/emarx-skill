"""Simple Chinese academic paper summarizer.

The summarizer segments a paper by recognizing common section headings and
maps each section to one of six fixed output slots. When headings cannot be
reliably identified, it falls back to a percentage-based heuristic split.
"""

from __future__ import annotations

import re

_MAX_LEN = 4000

# Output bucket -> heading keywords that belong there.
_TARGET_KEYWORDS: dict[str, tuple[str, ...]] = {
    "摘要": ("摘要", "Abstract"),
    "论证逻辑": (
        "引言",
        "绪论",
        "问题提出",
        "研究背景",
        "文献综述",
        "理论基础",
        "理论框架",
        "概念界定",
        "研究缘起",
    ),
    "研究方法": (
        "研究方法",
        "研究设计",
        "研究设计与方法",
        "数据来源",
        "实证设计",
        "研究对象",
        "变量测量",
        "模型构建",
        "数据分析",
        "数据采集",
        "案例采样",
        "访谈采样",
        "采样",
    ),
    "主要观点": (
        "研究结果",
        "实证结果",
        "研究发现",
        "结果分析",
        "讨论",
        "结论",
        "结语",
        "总结",
        "结果与讨论",
        "结论与讨论",
    ),
    "主要贡献": ("贡献", "启示", "建议", "研究启示", "政策建议", "治理", "策略", "路径", "对策", "展望", "局限", "不足"),
}

# Headings whose content should be ignored.
_SKIP_KEYWORDS = ("关键词", "Keywords", "Key words", "参考文献", "References", "注释", "Notes")

# Every keyword that can introduce a heading line.
_ALL_KEYWORDS = _SKIP_KEYWORDS + tuple(
    kw for kws in _TARGET_KEYWORDS.values() for kw in kws
)

_OUTPUT_ORDER = ["摘要", "主要内容", "论证逻辑", "主要观点", "研究方法", "主要贡献"]

# Regex alternation of all heading keywords, longest first so composite terms
# such as "研究设计与方法" are preferred over shorter matches.
_KEYWORD_RE_ALTS = "|".join(
    re.escape(kw) for kw in sorted(_ALL_KEYWORDS, key=len, reverse=True)
)

# Numbering prefixes commonly used in Chinese academic papers.
_NUMBERING_PREFIX_RE = re.compile(
    r"^(?:"
    r"[一二三四五六七八九十]+[、.．）)]\s*"
    r"|\d+(?:\.\d+)*[\s.．、）)]\s*"
    r"|（[一二三四五六七八九十]+）\s*"
    r"|\([一二三四五六七八九十]+\)\s*"
    r"|\(\d+\)\s*"
    r")"
)

# Heading patterns that appear inline inside CNKI article text (which is
# sometimes returned as a single long line). We insert line breaks so the section
# splitter can recognize the structure.
# The captured segment must contain at least one known heading keyword; this
# prevents numbers such as "15 university" or years like "2025" from being
# mistaken for section headings.
_NUMBERED_HEADING_RE = re.compile(
    r"(\s|^)("
    r"(?:"
    r"[一二三四五六七八九十]+[、.．）)]\s*|"
    r"\d+(?:\.\d+)*[\s.．、）)]\s*|"
    r"（[一二三四五六七八九十]+）\s*|"
    r"\([一二三四五六七八九十]+\)\s*|"
    r"\(\d+\)\s*"
    r")"
    r"(?=[^\s]{0,35}(?:" + _KEYWORD_RE_ALTS + r")\b)[^\s]{1,35}"
    r")(?=\s|$)"
)

_UNNUMBERED_HEADING_RE = re.compile(
    r"(\s|^)(引言|绪论|研究设计|研究方法|数据来源|研究结果|研究发现|结果分析|讨论|结论|结语|总结|贡献|启示|政策建议)(?=\s|$)"
)

_REF_SPLIT_RE = re.compile(
    r"(\s|^)(参考文献|References|注释|Notes)(?=\s|$)", re.IGNORECASE
)

_METADATA_BOUNDARY_RE = re.compile(
    r"(^|\s)("
    r"关键词|Keywords|Keyword|Key words|"
    r"基金项目|基金|作者简介|收稿日期|Received|"
    r"DOI|中图分类号|文献标识码|文章编号"
    r")[：:]\s*.*?(?=\s+(?:"
    r"[一二三四五六七八九十]+[、.．）)]|"
    r"\d+(?:\.\d+)*[\s.．、）)]|"
    r"（[一二三四五六七八九十]+）|"
    r"\(\d+\)|"
    r"摘要|Abstract|引言|绪论|结论|结语|总结|研究方法|研究结果|研究发现|结果分析|讨论|"
    r"贡献|启示|政策建议|参考文献|References|注释|Notes"
    r")|$)",
    re.IGNORECASE | re.DOTALL,
)


class _SectionSplitter:
    """Split paper text into sections based on recognized heading lines."""

    def __init__(self, text: str) -> None:
        self.text = text
        # (heading, content, content_start_in_text, content_end_in_text)
        self.sections: list[tuple[str, str, int, int]] = []
        self.first_heading_pos: int = -1

    def split(self) -> "_SectionSplitter":
        lines = self.text.splitlines(keepends=True)
        current_heading: str | None = None
        current_content: list[str] = []
        content_start: int = 0
        pos = 0

        for line in lines:
            stripped = line.strip()
            if self._is_heading_line(stripped):
                if self.first_heading_pos < 0:
                    self.first_heading_pos = pos
                if current_heading is not None:
                    self.sections.append(
                        (
                            current_heading,
                            "".join(current_content).strip(),
                            content_start,
                            pos,
                        )
                    )
                current_heading = stripped
                current_content = []
                content_start = pos + len(line)
            else:
                current_content.append(line)
            pos += len(line)

        if current_heading is not None:
            self.sections.append(
                (
                    current_heading,
                    "".join(current_content).strip(),
                    content_start,
                    pos,
                )
            )

        return self

    @staticmethod
    def _is_heading_line(line: str) -> bool:
        """Return True if ``line`` is a standalone section heading."""
        if not line or len(line) > 40:
            return False
        rest = _NUMBERING_PREFIX_RE.sub("", line).rstrip("：:；;")
        if not rest:
            return False
        parts = re.split(r"\s*(?:与|和|及|、)\s*", rest)

        # Recognize explicit section keywords (abstract, methods, references, etc.).
        has_keyword = any(part in _ALL_KEYWORDS for part in parts)
        if has_keyword:
            return True

        # Also treat short, numbered/structured lines without sentence endings as
        # generic section headings. This catches first-level chapter headings such
        # as "二、具身智能的特征..." or "（一）数据来源" that do not contain any
        # of the explicit keywords above, but still mark a structural boundary.
        # Require Chinese characters so that bare numbers/years in English text are
        # not mistaken for headings.
        if (
            _NUMBERING_PREFIX_RE.match(line)
            and len(rest) <= 35
            and not rest.endswith("。！？;；,，")
            and re.search(r"[一-鿿]", rest)
        ):
            return True

        return False


def _classify_heading(title: str) -> list[str]:
    """Return the output bucket(s) a heading maps to."""
    rest = _NUMBERING_PREFIX_RE.sub("", title).rstrip("：:；;")
    parts = re.split(r"\s*(?:与|和|及|、)\s*", rest)
    targets: set[str] = set()
    for part in parts:
        for target, keywords in _TARGET_KEYWORDS.items():
            if part in keywords:
                targets.add(target)
    return list(targets)


def _is_skip_heading(title: str) -> bool:
    """Return True if the heading's content should be ignored."""
    rest = _NUMBERING_PREFIX_RE.sub("", title).rstrip("：:；;")
    parts = re.split(r"\s*(?:与|和|及|、)\s*", rest)
    return any(part in _SKIP_KEYWORDS for part in parts)


def _heuristic_split(text: str) -> dict[str, str]:
    """Split text by percentages when headings cannot be identified.

    Boundaries snap to the nearest line break so sections do not start in the
    middle of a sentence.

    - First 15% -> abstract
    - Next 25% -> evenly split between logic and method
    - Middle 40% -> main content
    - Last 20% -> evenly split between viewpoints and contributions
    """
    total = len(text)
    abstract_end = int(total * 0.15)
    logic_method_end = int(total * 0.40)
    main_end = int(total * 0.80)

    # Snap each boundary to the next line break to avoid splitting mid-sentence.
    lines = text.splitlines(keepends=True)
    cumulative = [0]
    for line in lines:
        cumulative.append(cumulative[-1] + len(line))

    def snap(pos: int) -> int:
        # If the text is essentially one line, keep the original index.
        if len(lines) <= 1:
            return pos
        for c in cumulative:
            if c >= pos:
                return c
        return total

    abstract_end = snap(abstract_end)
    logic_method_end = snap(logic_method_end)
    main_end = snap(main_end)

    abstract = text[:abstract_end].strip()
    logic_method = text[abstract_end:logic_method_end].strip()
    main = text[logic_method_end:main_end].strip()
    view_contrib = text[main_end:].strip()

    lm_mid = len(logic_method) // 2
    vc_mid = len(view_contrib) // 2

    return {
        "摘要": abstract,
        "论证逻辑": logic_method[:lm_mid].strip(),
        "研究方法": logic_method[lm_mid:].strip(),
        "主要内容": main,
        "主要观点": view_contrib[:vc_mid].strip(),
        "主要贡献": view_contrib[vc_mid:].strip(),
    }


def _unused_text(text: str, used_ranges: list[tuple[int, int]]) -> str:
    """Return the parts of ``text`` not covered by ``used_ranges``.

    Ranges are merged and interpreted as half-open ``[start, end)`` intervals.
    """
    if not used_ranges:
        return text.strip()

    merged: list[tuple[int, int]] = []
    for start, end in sorted(used_ranges):
        if start >= end:
            continue
        if merged and start <= merged[-1][1]:
            merged[-1] = (merged[-1][0], max(merged[-1][1], end))
        else:
            merged.append((start, end))

    out: list[str] = []
    last = 0
    for start, end in merged:
        if start > len(text):
            break
        if start > last:
            out.append(text[last:start])
        last = max(last, end)
    if last < len(text):
        out.append(text[last:])

    return "".join(out).strip()


def _truncate(text: str, max_len: int = _MAX_LEN) -> str:
    """Return text truncated to ``max_len``, preferring whole lines."""
    if len(text) <= max_len:
        return text
    return text[:max_len].rsplit("\n", 1)[0].rstrip()


def _format_output(parts: dict[str, str]) -> str:
    """Build the fixed six-part plain-text output."""
    lines: list[str] = []
    for key in _OUTPUT_ORDER:
        lines.append(f"【{key}】")
        lines.append(parts.get(key, ""))
        lines.append("")
    return "\n".join(lines).strip() + "\n"


def _collapse(text: str | None) -> str:
    if not text:
        return ""
    return re.sub(r"\s+", " ", text).strip()


def _normalize_text(text: str) -> str:
    """Insert line breaks around inline headings and reference markers.

    CNKI's HTML reader often returns the entire article as one long line of text.
    Without normalization the section splitter cannot find headings because they
    are not on separate lines.
    """
    text = _NUMBERED_HEADING_RE.sub(r"\1\n\2\n", text)
    text = _UNNUMBERED_HEADING_RE.sub(r"\1\n\2\n", text)
    text = _REF_SPLIT_RE.sub(r"\1\n\2\n", text)
    return text


def _strip_inline_metadata(text: str) -> str:
    """Remove inline metadata blocks (keywords, funding, bios, etc.).

    These blocks may appear before the first heading or between sections even
    when the text is not line-wrapped. The regex stops at the next structural
    boundary so it does not swallow paper content.
    """
    return _METADATA_BOUNDARY_RE.sub(r"\1", text)


def _extract_abstracts(text: str) -> tuple[str, str, str]:
    """Isolate Chinese and English abstracts and return (cn, en, remaining_text).

    Each abstract is capped so a missing delimiter does not swallow the whole
    paper.  The captured block is removed from ``text`` so it does not pollute
    the other buckets.
    """
    # Metadata markers that normally terminate an abstract block.
    stop_markers = (
        r"关键词|Keywords|Keyword|Key words|Abstract|"
        r"Received|收稿日期|基金项目|作者简介|DOI|"
        r"中图分类号|文献标识码|文章编号"
    )

    chinese = ""
    m = re.search(
        r"摘要\s*[：:]?\s*(.{0,2500}?)\s*(?:" + stop_markers + r")",
        text,
        re.DOTALL | re.IGNORECASE,
    )
    if m:
        chinese = _collapse(m.group(1))
        text = text[: m.start()] + text[m.end() :]

    english = ""
    m2 = re.search(
        r"(?<!\w)Abstract\s*[：:]?\s*(.{0,2500}?)\s*(?:"
        r"Key words|Keywords|Keyword|Received|收稿日期|基金项目|作者简介|DOI|"
        r"中图分类号|文献标识码|文章编号|"
        r"\Z)",
        text,
        re.DOTALL | re.IGNORECASE,
    )
    if m2:
        english = _collapse(m2.group(1))
        text = text[: m2.start()] + text[m2.end() :]

    # Drop leftover metadata lines that look like headings but are not paper
    # sections (keywords, author bios, funding, DOI, classification codes).
    text = re.sub(
        r"(?:^|\n)\s*(?:"
        r"关键词|Keyword|Keywords|Key words|"
        r"基金|作者简介|收稿日期|Received|DOI|"
        r"中图分类号|文献标识码|文章编号"
        r")[：:]\s*[^\n]*",
        "",
        text,
        flags=re.IGNORECASE,
    )

    text = text.strip()
    return chinese, english, text


def summarize(text: str, metadata: dict | None = None, *, is_abstract_only: bool = False) -> str:
    """Generate a fixed six-part summary of a Chinese academic paper.

    Args:
        text: The full paper text (or the article abstract when
            ``is_abstract_only`` is True).
        metadata: Optional metadata dict (currently reserved for future use).
        is_abstract_only: When True, ``text`` is treated as an article abstract
            rather than full paper text. The abstract is placed in both the
            ``摘要`` and ``主要内容`` slots; the remaining slots are filled with
            a short note indicating that the information is not available from
            the abstract alone.

    Returns:
        A plain-text string with sections prefixed by ``【摘要】``,
        ``【主要内容】``, ``【论证逻辑】``, ``【主要观点】``,
        ``【研究方法】`` and ``【主要贡献】``.
    """
    if not text or not text.strip():
        return _format_output({k: "" for k in _OUTPUT_ORDER})

    text = text.strip()

    if is_abstract_only:
        return _format_output(
            {
                "摘要": text,
                "主要内容": text,
                "论证逻辑": "（仅采集到摘要，未明确说明研究背景与问题提出）",
                "研究方法": "（仅采集到摘要，未明确说明研究方法）",
                "主要观点": "（仅采集到摘要，未明确说明研究结果与观点）",
                "主要贡献": "（仅采集到摘要，未明确说明贡献与启示）",
            }
        )

    chinese, english, working_text = _extract_abstracts(text)
    working_text = _strip_inline_metadata(working_text)
    working_text = _normalize_text(working_text)

    # Drop reference/footnote sections before splitting so they never leak into
    # other buckets.
    for marker in ("参考文献", "References", "注释", "Notes"):
        working_text = re.split(
            rf"(?:^|\n)\s*{re.escape(marker)}\b", working_text, maxsplit=1, flags=re.IGNORECASE
        )[0]

    # Strip leading metadata (English title, author pinyin, keywords, received
    # date, etc.) so the first recognized section heading becomes the split
    # boundary. Without this the pre-heading block pollutes the 主要内容 bucket.
    first_heading_offset = 0
    pos = 0
    for line in working_text.splitlines(keepends=True):
        if _SectionSplitter._is_heading_line(line.strip()):
            first_heading_offset = pos
            break
        pos += len(line)
    working_text = working_text[first_heading_offset:]

    buckets: dict[str, list[str]] = {k: [] for k in _OUTPUT_ORDER}
    abstract_parts = [p for p in (chinese, english) if p]
    if abstract_parts:
        buckets["摘要"].append("\n".join(abstract_parts))

    splitter = _SectionSplitter(working_text).split()
    recognized = [s for s in splitter.sections if _classify_heading(s[0])]

    if not recognized:
        # Fallback: pure heuristic split on the remaining text.
        heuristic = _heuristic_split(working_text)
        for key in _OUTPUT_ORDER:
            if not buckets[key]:
                buckets[key].append(heuristic[key])
    else:
        used_ranges: list[tuple[int, int]] = []

        # Any substantial text before the first heading is treated as body,
        # unless it looks like leftover metadata (abstract/keywords/author info).
        if splitter.first_heading_pos > 50:
            pre = working_text[: splitter.first_heading_pos].strip()
            metadata_markers = ("摘要", "关键词", "作者简介", "基金项目", "收稿日期", "Received")
            is_metadata = any(marker in pre for marker in metadata_markers)
            if len(pre) > 50 and not is_metadata:
                buckets["主要内容"].append(pre)
                used_ranges.append((0, splitter.first_heading_pos))

        # Distribute each section's content to the appropriate bucket(s).
        for title, content, start, end in splitter.sections:
            if _is_skip_heading(title):
                continue
            if not content:
                continue
            targets = _classify_heading(title)
            if not targets:
                buckets["主要内容"].append(content)
            else:
                for target in targets:
                    buckets[target].append(content)
            used_ranges.append((start, end))

    parts = {k: _truncate("\n\n".join(v).strip()) for k, v in buckets.items()}
    return _format_output(parts)
