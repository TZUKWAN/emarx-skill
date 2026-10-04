# -*- coding: utf-8 -*-
"""
footnote_audit.py — EMARX 脚注工程化审计脚本。

依据 references/footnote-engineering-protocol.md，检查：

  1. 闭环对账：脚注定义数、正文引用数、缺号、重号；
  2. 复合脚注候选：一个注号内塞多条文献（分号连排、"。又"、多个类型码）；
  3. 禁用词：参见 / 前引 / 同上 / 同前 / 另见；
  4. 著录变体重复组候选：同一文献的带日期/不带日期、全半角、有无析出篇名等写法；
  5. 同段同文献同页码的完全重复引用候选；
  6. 短引先于完整著录的顺序问题候选。

支持两种稿式：
  - EMARX 工作稿：正文 [n] 行内引用 + 文末"参考文献"节 [n] 条目；
  - pandoc 脚注稿：正文 [^n] 引用 + [^n]: 定义。

用法：
  python scripts/footnote_audit.py --paper paper.md --output footnote-audit.json

注意：本脚本只发现候选问题，不自动修改。合并与删除必须由主模型逐组确认。
"""
import argparse
import json
import re
from pathlib import Path

# ---------- 模式识别 ----------

PANDOC_DEF_RE = re.compile(r"^\[\^(\d+)\]:\s*(.+?)\s*$", re.MULTILINE)
PANDOC_CITE_RE = re.compile(r"\[\^(\d+)\]")
INLINE_CITE_RE = re.compile(r"(?<!!)(?<!\^)\[(\d+)\]")
REF_HEADING_RE = re.compile(r"^(#+)\s*参考文献\s*$", re.MULTILINE)
REF_ENTRY_RE = re.compile(r"^\[(\d+)\]\s*(.+?)\s*$", re.MULTILINE)

# ---------- 检查规则 ----------

BANNED_WORDS = ["参见", "前引", "同上", "同前", "另见"]
TYPE_CODE_RE = re.compile(r"\[[MJDRCP]\]")
PAGE_TAIL_RE = re.compile(r"[:：,，]\s*(?:第)?(\d+(?:[-—–]\d+)?(?:[,、]\d+(?:[-—–]\d+)?)*)\s*页?$")
CN_DATE_RE = re.compile(
    r"[(（]?\d{4}年\d{1,2}月\d{1,2}日[)）]?"
    r"|[(（]?[〇零一二三四五六七八九十]{4}年[一二三四五六七八九十]{1,3}月[一二三四五六七八九十]{1,3}日[)）]?"
)
NORMALIZE_STRIP_RE = re.compile(r"[\s，。,.；;：:、（）()《》〈〉\"'“”‘’\-—–]")


def normalize_work_key(entry: str) -> str:
    """把著录文本规范化为'同一文献'识别键：去日期、去标点、去页码、去类型码。"""
    s = entry
    s = CN_DATE_RE.sub("", s)
    s = PAGE_TAIL_RE.sub("", s)
    s = TYPE_CODE_RE.sub("", s)
    s = NORMALIZE_STRIP_RE.sub("", s)
    return s


def extract_pages(entry: str) -> str:
    """提取著录尾部页码，用于同页码判断。没有页码返回空串。"""
    m = PAGE_TAIL_RE.search(entry)
    return m.group(1) if m else ""


def has_type_code(entry: str) -> bool:
    return bool(TYPE_CODE_RE.search(entry))


def detect_composite(entry: str) -> list[str]:
    """检测一个注号内是否塞了多条文献。返回命中的特征列表。"""
    hits = []
    if "。又" in entry or "；又" in entry or ";又" in entry:
        hits.append("又字连接")
    # 多个类型码：一条著录正常只有一个 [M]/[J]/[D]
    codes = TYPE_CODE_RE.findall(entry)
    if len(codes) >= 2:
        hits.append(f"多个类型码{len(codes)}个")
    # 分号后紧跟'作者.'著录形态（中文作者名+点号）
    if re.search(r"[；;]\s*[^；;。]{1,12}[.]\s*[^；;]", entry):
        hits.append("分号后接新著录")
    return hits


def parse_paper(text: str) -> dict:
    """解析论文，返回 {'mode': 'pandoc'|'emarx', 'defs': {n: entry}, 'cites': [(n, para_idx)], 'paragraphs': [...]}"""
    pandoc_defs = {int(n): e for n, e in PANDOC_DEF_RE.findall(text)}
    if pandoc_defs:
        # pandoc 模式：定义行不算正文引用
        body_lines = []
        for line in text.split("\n"):
            if not PANDOC_DEF_RE.match(line):
                body_lines.append(line)
        body = "\n".join(body_lines)
        cites = [(int(n), None) for n in PANDOC_CITE_RE.findall(body)]
        defs = pandoc_defs
        mode = "pandoc"
    else:
        # EMARX 工作稿模式：正文 [n] + 文末参考文献节
        m = REF_HEADING_RE.search(text)
        if m:
            body = text[:m.start()]
            ref_section = text[m.end():]
            defs = {int(n): e for n, e in REF_ENTRY_RE.findall(ref_section)}
        else:
            body = text
            defs = {}
        cites = [(int(n), None) for n in INLINE_CITE_RE.findall(body)]
        mode = "emarx"

    # 正文段落：记录每个引用落在第几段
    paragraphs = [p for p in re.split(r"\n\s*\n", body) if p.strip()]
    cites_with_para = []
    for pidx, para in enumerate(paragraphs):
        cite_re = PANDOC_CITE_RE if mode == "pandoc" else INLINE_CITE_RE
        for n in cite_re.findall(para):
            cites_with_para.append({"n": int(n), "paragraph_index": pidx})

    return {"mode": mode, "defs": defs, "cites": cites_with_para, "paragraphs": paragraphs}


def audit(text: str) -> dict:
    parsed = parse_paper(text)
    defs = parsed["defs"]
    cites = parsed["cites"]
    paragraphs = parsed["paragraphs"]

    def_nums = sorted(defs.keys())
    cite_nums = [c["n"] for c in cites]
    def_set = set(def_nums)
    cite_set = set(cite_nums)

    # 1. 闭环对账
    missing_defs = sorted(cite_set - def_set)   # 正文引用了但没有定义
    orphan_defs = sorted(def_set - cite_set)    # 定义了但正文没引用
    missing_numbers = []
    if def_nums:
        full_range = set(range(min(def_nums), max(def_nums) + 1))
        missing_numbers = sorted(full_range - def_set)

    reconciliation = {
        "mode": parsed["mode"],
        "definition_count": len(def_nums),
        "citation_count": len(cite_nums),
        "unique_cited_numbers": len(cite_set),
        "cited_but_undefined": missing_defs,
        "defined_but_uncited": orphan_defs,
        "number_gaps": missing_numbers,
        "balanced": (not missing_defs and not orphan_defs and not missing_numbers),
    }

    # 2. 复合脚注候选
    composite_candidates = []
    for n in def_nums:
        hits = detect_composite(defs[n])
        if hits:
            composite_candidates.append({"footnote": n, "signals": hits, "entry": defs[n][:200]})

    # 3. 禁用词
    banned_hits = []
    for n in def_nums:
        for w in BANNED_WORDS:
            if w in defs[n]:
                banned_hits.append({"footnote": n, "word": w, "entry": defs[n][:200]})

    # 4. 著录变体重复组候选（规范键相同、原文不同）
    key_groups = {}
    for n in def_nums:
        key = normalize_work_key(defs[n])
        if not key:
            continue
        key_groups.setdefault(key, []).append(n)
    variant_groups = []
    for key, nums in key_groups.items():
        if len(nums) < 2:
            continue
        texts = {defs[n] for n in nums}
        if len(texts) > 1:  # 原文完全相同不算变体问题（同段重复在第5项查）
            variant_groups.append({
                "work_key_preview": defs[nums[0]][:80],
                "footnotes": nums,
                "variants": [defs[n][:160] for n in nums],
            })

    # 5. 同段同文献同页码完全重复候选
    same_para_dupes = []
    para_cite_map = {}
    for c in cites:
        if c["n"] in def_set:
            para_cite_map.setdefault(c["paragraph_index"], []).append(c["n"])
    for pidx, nums in para_cite_map.items():
        seen = {}
        for n in nums:
            sig = (normalize_work_key(defs[n]), extract_pages(defs[n]))
            if not sig[0]:
                continue
            if sig in seen:
                same_para_dupes.append({
                    "paragraph_index": pidx,
                    "footnotes": [seen[sig], n],
                    "entry": defs[n][:160],
                    "paragraph_preview": paragraphs[pidx][:100].replace("\n", " "),
                })
            else:
                seen[sig] = n

    # 6. 短引先于完整著录候选：同规范键组内，短引（无类型码）编号 < 完整著录（有类型码）编号
    order_candidates = []
    for key, nums in key_groups.items():
        if len(nums) < 2:
            continue
        ordered = sorted(nums)
        first = ordered[0]
        if not has_type_code(defs[first]):
            later_full = [n for n in ordered[1:] if has_type_code(defs[n])]
            if later_full:
                order_candidates.append({
                    "short_cite_footnote": first,
                    "full_cite_footnotes": later_full,
                    "short_entry": defs[first][:160],
                })

    issues = (len(composite_candidates) + len(banned_hits) + len(variant_groups)
              + len(same_para_dupes) + len(order_candidates)
              + len(missing_defs) + len(orphan_defs) + len(missing_numbers))

    return {
        "reconciliation": reconciliation,
        "composite_footnote_candidates": composite_candidates,
        "banned_word_hits": banned_hits,
        "variant_duplicate_groups": variant_groups,
        "same_paragraph_duplicate_candidates": same_para_dupes,
        "short_before_full_candidates": order_candidates,
        "issue_count": issues,
        "note": "脚本只发现候选问题；合并与删除必须由主模型逐组确认，不得自动执行。",
    }


def main():
    ap = argparse.ArgumentParser(description="EMARX 脚注工程化审计")
    ap.add_argument("--paper", required=True, help="论文 Markdown 文件路径")
    ap.add_argument("--output", required=True, help="输出 JSON 报告路径")
    args = ap.parse_args()

    paper_path = Path(args.paper)
    if not paper_path.exists():
        raise FileNotFoundError(f"找不到论文文件: {paper_path}")

    text = paper_path.read_text(encoding="utf-8")
    result = audit(text)
    result["paper"] = str(paper_path)

    output_path = Path(args.output)
    output_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")

    rec = result["reconciliation"]
    print("脚注审计完成。")
    print(f"稿式: {rec['mode']}")
    print(f"脚注定义: {rec['definition_count']} | 正文引用: {rec['citation_count']} | "
          f"对账: {'平衡' if rec['balanced'] else '不平衡'}")
    if not rec["balanced"]:
        print(f"  引而未定义: {rec['cited_but_undefined'][:20]}")
        print(f"  定义未引用: {rec['defined_but_uncited'][:20]}")
        print(f"  编号缺号: {rec['number_gaps'][:20]}")
    print(f"复合脚注候选: {len(result['composite_footnote_candidates'])}")
    print(f"禁用词命中: {len(result['banned_word_hits'])}")
    print(f"著录变体重复组候选: {len(result['variant_duplicate_groups'])}")
    print(f"同段同页重复候选: {len(result['same_paragraph_duplicate_candidates'])}")
    print(f"短引先于完整著录候选: {len(result['short_before_full_candidates'])}")
    print(f"报告保存: {output_path}")


if __name__ == "__main__":
    main()
