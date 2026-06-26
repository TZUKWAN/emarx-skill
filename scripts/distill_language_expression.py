from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from pathlib import Path


CN_RE = re.compile(r"[\u4e00-\u9fff]")
PAGE_RE = re.compile(r"\[\[p\d+\]\]\s*")
SENTENCE_RE = re.compile(r"[^。！？!?；;]+[。！？!?；;]?")
REF_START_RE = re.compile(r"(参考文献|注释|References)\s*[:：]?", re.IGNORECASE)
ABSTRACT_RE = re.compile(r"[［\[]?摘要[］\]]?\s*[:：]?\s*(.{80,1200}?)(?=[［\[]?关键词|关键字|Abstract|中图分类号|一、|1[.．、]|$)", re.S)

AUTHOR_VISIBLE_PATTERNS = [
    "本文",
    "笔者",
    "本研究",
    "本论文",
    "本文认为",
    "本文指出",
    "笔者认为",
    "文章认为",
    "文章指出",
]

META_DISCOURSE_PATTERNS = [
    "本文的核心观点",
    "核心观点是",
    "本文认为",
    "本文指出",
    "本文旨在",
    "本文试图",
    "本文将",
    "本文从",
    "文章认为",
    "文章指出",
    "本文通过",
]

REVIEW_INSERT_PATTERNS = [
    "有研究指出",
    "有研究认为",
    "相关研究指出",
    "相关研究认为",
    "已有研究指出",
    "已有研究认为",
    "学者指出",
    "学者认为",
]

REPORTING_VERBS = ["指出", "认为", "提出", "强调", "阐明", "揭示", "表明", "显示", "分析"]
SUBJECTLESS_OPENING_RE = re.compile(r"^(基于|通过|从|以|围绕|针对|立足|结合|借助|依托|在)")
COLON_RE = re.compile(r"[:：]")
DASH_RE = re.compile(r"[—-]{2,}|——")
QUOTE_RE = re.compile(r"[“”\"']")
FIRST_PERSON_RE = re.compile(r"(本文|笔者|作者|本研究|本论文|文章)")


def cn_len(text: str) -> int:
    return len(CN_RE.findall(text))


def clean_text(text: str) -> str:
    text = PAGE_RE.sub("", text)
    text = text.replace("\u3000", " ")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def split_refs(text: str) -> tuple[str, str]:
    match = REF_START_RE.search(text)
    if not match:
        return text, ""
    return text[: match.start()].strip(), text[match.start() :].strip()


def sentences(text: str) -> list[str]:
    out = []
    for match in SENTENCE_RE.finditer(text):
        s = match.group(0).strip()
        if cn_len(s) >= 6:
            out.append(s)
    return out


def detect_abstract(body: str) -> tuple[str, str]:
    match = ABSTRACT_RE.search(body[:5000])
    if match:
        return match.group(1).strip(), "explicit"
    paras = [p.strip() for p in re.split(r"\n\s*\n", body[:4000]) if cn_len(p) >= 100]
    if paras:
        return paras[0][:900].strip(), "inferred_first_paragraph"
    return "", "missing"


def count_any(text: str, patterns: list[str]) -> int:
    return sum(text.count(pattern) for pattern in patterns)


def strip_metadata_noise(text: str) -> str:
    text = re.sub(r"作者简介.{0,120}", "", text)
    text = re.sub(r"文章编号.{0,80}", "", text)
    text = re.sub(r"中图分类号.{0,80}", "", text)
    text = re.sub(r"文献标识码.{0,80}", "", text)
    return text


def sample_hits(text: str, patterns: list[str], limit: int = 5) -> list[str]:
    hits = []
    for pattern in patterns:
        index = text.find(pattern)
        if index >= 0:
            start = max(0, index - 22)
            end = min(len(text), index + len(pattern) + 42)
            snippet = re.sub(r"\s+", "", text[start:end])
            hits.append(snippet[:90])
        if len(hits) >= limit:
            break
    return hits


def paragraph_openings(body: str) -> Counter:
    counter: Counter[str] = Counter()
    for para in [p.strip() for p in re.split(r"\n\s*\n", body) if cn_len(p) >= 60]:
        first = re.split(r"[。！？!?；;]", para, maxsplit=1)[0].strip()
        match = SUBJECTLESS_OPENING_RE.match(first)
        if match:
            counter[match.group(1)] += 1
    return counter


def analyze_item(item: dict) -> dict:
    path = Path(item.get("text_file", ""))
    text = clean_text(path.read_text(encoding="utf-8", errors="replace")) if path.exists() else ""
    body, refs = split_refs(text)
    abstract, abstract_status = detect_abstract(body)
    abstract_for_style = strip_metadata_noise(abstract)
    body_sentences = sentences(body)
    abstract_sentences = sentences(abstract_for_style)
    author_visible_abstract = count_any(abstract_for_style, AUTHOR_VISIBLE_PATTERNS)
    meta_body = count_any(body, META_DISCOURSE_PATTERNS)
    review_body = count_any(body, REVIEW_INSERT_PATTERNS)
    reporting_body = count_any(body, REPORTING_VERBS)
    subjectless_abstract = sum(1 for s in abstract_sentences if SUBJECTLESS_OPENING_RE.match(s))
    colon_count = len(COLON_RE.findall(body))
    dash_count = len(DASH_RE.findall(body))
    quote_count = len(QUOTE_RE.findall(body))
    return {
        "name": item.get("name"),
        "file": item.get("file"),
        "status": item.get("status"),
        "chars": item.get("chars", 0),
        "abstract_status": abstract_status,
        "abstract_cn_chars": cn_len(abstract_for_style),
        "abstract_sentence_count": len(abstract_sentences),
        "abstract_author_visible_count": author_visible_abstract,
        "abstract_subjectless_opening_count": subjectless_abstract,
        "abstract_author_visible_samples": sample_hits(abstract_for_style, AUTHOR_VISIBLE_PATTERNS, 3),
        "body_sentence_count": len(body_sentences),
        "body_meta_discourse_count": meta_body,
        "body_review_insert_count": review_body,
        "body_reporting_verb_count": reporting_body,
        "body_meta_samples": sample_hits(body, META_DISCOURSE_PATTERNS, 3),
        "body_review_samples": sample_hits(body, REVIEW_INSERT_PATTERNS, 3),
        "colon_count": colon_count,
        "dash_count": dash_count,
        "quote_count": quote_count,
        "subjectless_openings": dict(paragraph_openings(body).most_common()),
    }


def pct(num: int, den: int) -> float:
    return round(num * 100 / max(den, 1), 2)


def aggregate(rows: list[dict]) -> dict:
    total = len(rows)
    explicit = [r for r in rows if r["abstract_status"] == "explicit"]
    inferred = [r for r in rows if r["abstract_status"] == "inferred_first_paragraph"]
    author_visible_explicit = [r for r in explicit if r["abstract_author_visible_count"] > 0]
    author_visible_all = [r for r in rows if r["abstract_author_visible_count"] > 0]
    subjectless_explicit = [
        r for r in explicit
        if r["abstract_subjectless_opening_count"] > 0 and r["abstract_sentence_count"] > 0
    ]
    meta_rows = [r for r in rows if r["body_meta_discourse_count"] > 0]
    review_rows = [r for r in rows if r["body_review_insert_count"] > 0]
    colon_heavy = [r for r in rows if r["colon_count"] >= 20]
    opening_counter: Counter[str] = Counter()
    for r in rows:
        opening_counter.update(r["subjectless_openings"])
    return {
        "article_count": total,
        "explicit_abstract_count": len(explicit),
        "inferred_abstract_count": len(inferred),
        "explicit_abstract_author_visible_count": len(author_visible_explicit),
        "explicit_abstract_author_visible_pct": pct(len(author_visible_explicit), len(explicit)),
        "explicit_abstract_subjectless_opening_count": len(subjectless_explicit),
        "explicit_abstract_subjectless_opening_pct": pct(len(subjectless_explicit), len(explicit)),
        "all_abstract_author_visible_count": len(author_visible_all),
        "all_abstract_author_visible_pct": pct(len(author_visible_all), total),
        "body_meta_discourse_article_count": len(meta_rows),
        "body_meta_discourse_article_pct": pct(len(meta_rows), total),
        "body_review_insert_article_count": len(review_rows),
        "body_review_insert_article_pct": pct(len(review_rows), total),
        "colon_heavy_article_count": len(colon_heavy),
        "colon_heavy_article_pct": pct(len(colon_heavy), total),
        "subjectless_openings_top": opening_counter.most_common(12),
        "top_meta_samples": [sample for r in meta_rows[:8] for sample in r["body_meta_samples"][:1]],
        "top_review_samples": [sample for r in review_rows[:8] for sample in r["body_review_samples"][:1]],
        "top_abstract_author_samples": [sample for r in author_visible_all[:8] for sample in r["abstract_author_visible_samples"][:1]],
    }


def markdown_report(summary: dict, rows: list[dict]) -> str:
    lines = [
        "# EMARX v6.8 Language Expression Distillation",
        "",
        "## Evidence Base",
        "",
        f"- Articles analyzed: {summary['article_count']}",
        f"- Explicit abstracts detected: {summary['explicit_abstract_count']}",
        f"- Inferred first-paragraph abstracts: {summary['inferred_abstract_count']}",
        "",
        "## Findings",
        "",
        f"- Explicit abstracts with visible author subjects (`本文`/`笔者`/`本研究`/`文章认为`): {summary['explicit_abstract_author_visible_count']} / {summary['explicit_abstract_count']} ({summary['explicit_abstract_author_visible_pct']}%).",
        f"- Explicit abstracts with subjectless or prepositional compressed openings: {summary['explicit_abstract_subjectless_opening_count']} / {summary['explicit_abstract_count']} ({summary['explicit_abstract_subjectless_opening_pct']}%).",
        f"- All detected abstract candidates with visible author subjects: {summary['all_abstract_author_visible_count']} / {summary['article_count']} ({summary['all_abstract_author_visible_pct']}%).",
        f"- Articles containing meta-discourse such as `本文的核心观点`, `本文认为`, or `文章认为`: {summary['body_meta_discourse_article_count']} / {summary['article_count']} ({summary['body_meta_discourse_article_pct']}%).",
        f"- Articles containing review-insert patterns such as `有研究指出` or `已有研究认为`: {summary['body_review_insert_article_count']} / {summary['article_count']} ({summary['body_review_insert_article_pct']}%).",
        f"- Articles with 20 or more colons in body text: {summary['colon_heavy_article_count']} / {summary['article_count']} ({summary['colon_heavy_article_pct']}%).",
        "",
        "## Subjectless Openings In Corpus",
        "",
    ]
    for token, count in summary["subjectless_openings_top"]:
        lines.append(f"- `{token}`: {count}")
    lines.extend([
        "",
        "## Style Rules Derived",
        "",
        "- Abstracts should normally use impersonal third-person reporting and compressed object-description. Do not write `本文认为`, `本文的核心观点是`, `笔者认为`, or `文章认为` in abstracts.",
        "- The abstract should describe the object, problem, mechanism, value, and path directly. It should not narrate what the author or article is going to do.",
        "- Body prose must not insert mini literature reviews with `有研究指出`, `已有研究认为`, or `相关研究指出`. If literature is used, digest the source into the argument or cite the exact claim where it functions.",
        "- Avoid meta-discourse about the paper itself, such as `本文的核心观点`, `本文将从`, or `文章通过`. Turn the statement into a direct academic claim.",
        "- Use colon, quotation marks, and dash only when required by title, citation, or concept explanation. Do not use colon-led mini titles inside paragraphs.",
        "- Prefer object-led and relation-led prose over self-referential prose. Let the paper sound like scholarship, not a plan, report, or prompt answer.",
        "",
        "## Negative Rewrite Rules",
        "",
        "| Bad | Better movement |",
        "| --- | --- |",
        "| `本文的核心观点是……` | State the claim directly. |",
        "| `本文认为……` | Name the object and relation, then make the judgment. |",
        "| `有研究指出……` | Digest the source into a problem, concept, mechanism, or limitation. |",
        "| `文章从……展开分析` | Remove paper self-description and start from the research object. |",
        "| `问题在于：……` | Use a sentence with subject, relation, and consequence. |",
        "",
        "## Caveats",
        "",
        "- PDF extraction noise can affect abstract detection. Explicit abstracts are stronger evidence than inferred first paragraphs.",
        "- Some genuine papers may use `本文` in methodological or historical contexts. EMARX still bans it by default because the user's target style rejects visible author subjects and self-narration.",
        "",
    ])
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Distill language-expression patterns from EMARX workspace papers.")
    parser.add_argument("--index", required=True, help="structure_index.json path")
    parser.add_argument("--output-json", required=True)
    parser.add_argument("--output-md", required=True)
    args = parser.parse_args()

    items = json.loads(Path(args.index).read_text(encoding="utf-8"))
    ok_items = [item for item in items if item.get("status") == "ok" and item.get("text_file")]
    rows = [analyze_item(item) for item in ok_items]
    summary = aggregate(rows)
    out = {
        "source_index": args.index,
        "summary": summary,
        "articles": rows,
    }
    json_path = Path(args.output_json)
    md_path = Path(args.output_md)
    json_path.parent.mkdir(parents=True, exist_ok=True)
    md_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    md_path.write_text(markdown_report(summary, rows), encoding="utf-8")
    print(json.dumps({"articles": len(rows), "json": str(json_path), "md": str(md_path)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
