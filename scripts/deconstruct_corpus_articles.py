from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import Counter
from pathlib import Path


CN_RE = re.compile(r"[\u4e00-\u9fff]")
PAGE_RE = re.compile(r"\[\[p\d+\]\]\s*")
SENTENCE_RE = re.compile(r"[^。！？!?；;]+[。！？!?；;]?")
REF_START_RE = re.compile(r"(参考文献|注释|References)\s*[:：]?", re.IGNORECASE)
ABSTRACT_RE = re.compile(r"[［\[]?摘要[］\]]?\s*[:：]?\s*(.{80,1200}?)(?=[［\[]?关键词|关键字|Abstract|中图分类号|一、|1[.．、]|$)", re.S)
KEYWORDS_RE = re.compile(r"(?:关键词|关键字)\s*[:：]?\s*(.{3,160}?)(?=\n|中图分类号|Abstract|$)", re.S)
FORMAL_HEADING_RE = re.compile(
    r"^(?P<prefix>[一二三四五六七八九十]+、|（[一二三四五六七八九十]+）|\d+[.．、])\s*(?P<title>\S.{0,80})$"
)

BACKGROUND_CUES = ["背景", "语境", "时代", "现实", "随着", "当前", "近年来", "新时代"]
PROBLEM_CUES = ["问题", "困境", "不足", "风险", "挑战", "缺乏", "忽视", "矛盾", "危机"]
METHOD_CUES = ["基于", "从", "视角", "视域", "以", "通过", "运用", "分析", "考察"]
CONCLUSION_CUES = ["提出", "认为", "指出", "表明", "应", "需要", "有助于", "路径", "策略", "进路"]
REPORTING_CUES = ["指出", "认为", "提出", "强调", "显示", "表明", "揭示", "阐释", "分析"]
POLICY_CUES = ["习近平", "二十大", "党中央", "新时代", "中国式现代化", "文化强国", "中华民族共同体"]
THEORY_CUES = ["马克思", "理论", "概念", "主体性", "现代性", "意识形态", "文化记忆", "集体记忆", "认同"]
MECHANISM_CUES = ["机制", "机理", "逻辑", "结构", "过程", "生成", "建构", "转化", "形塑"]
PATH_CUES = ["路径", "策略", "进路", "对策", "实践", "优化", "完善", "提升", "推进", "构建"]
RHETORIC_CUES = ["一方面", "另一方面", "不仅", "而且", "同时", "因此", "由此", "可见", "进而", "具体而言"]
NOISE_HEADING_RE = re.compile(
    r"^(?:\d{4}[.．]\d{1,2}|20\d{2}年第?\d*期|第\d+期|DOI|doi|CNKI|思想理论教育|学校党建与思想教育|马克思主义研究)"
)


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


def sentence_list(text: str) -> list[str]:
    sentences = []
    for match in SENTENCE_RE.finditer(text):
        sentence = match.group(0).strip()
        if cn_len(sentence) >= 6:
            sentences.append(sentence)
    return sentences


def pct(value: int, total: int) -> float:
    return round(value * 100 / max(total, 1), 2)


def short_excerpt(text: str, limit: int = 55) -> str:
    text = re.sub(r"\s+", "", text)
    if len(text) <= limit:
        return text
    return text[:limit] + "..."


def detect_abstract(body: str) -> tuple[str, str]:
    match = ABSTRACT_RE.search(body[:5000])
    if match:
        return match.group(1).strip(), "explicit"
    paras = [p.strip() for p in re.split(r"\n\s*\n", body[:4000]) if cn_len(p) >= 80]
    if paras:
        return paras[0][:900].strip(), "inferred_first_paragraph"
    return "", "missing"


def detect_keywords(body: str) -> list[str]:
    match = KEYWORDS_RE.search(body[:4000])
    if not match:
        return []
    raw = re.sub(r"\s+", "", match.group(1))
    raw = re.sub(r"^[\]］】):：,，;；]+", "", raw)
    items = re.split(r"[；;，,、\s]+", raw)
    cleaned = []
    for item in items:
        item = re.sub(r"^[^\u4e00-\u9fffA-Za-z0-9]+|[^\u4e00-\u9fffA-Za-z0-9]+$", "", item)
        if 2 <= cn_len(item) <= 18:
            cleaned.append(item)
    return cleaned[:8]


def is_noise_heading(title: str) -> bool:
    title = title.strip()
    if not title:
        return True
    if NOISE_HEADING_RE.search(title):
        return True
    if re.search(r"(cnki|doi|issn|[JＭM]\.|思想理论教育|学校党建与思想教育)", title, re.I):
        return True
    if re.fullmatch(r"[\d\s.．,，:：;；()（）\-—]+", title):
        return True
    if cn_len(title) < 3:
        return True
    return False


def extract_headings(body: str, index_headings: list[dict]) -> list[dict]:
    headings = []
    for line_no, line in enumerate(body.splitlines(), 1):
        stripped = line.strip()
        match = FORMAL_HEADING_RE.match(stripped)
        if match and not is_noise_heading(stripped):
            prefix = match.group("prefix")
            level = 1 if prefix.endswith("、") and not prefix[0].isdigit() else 2
            headings.append({"line": line_no, "level": level, "title": stripped, "source": "text"})
    if headings:
        return headings
    cleaned = []
    for item in index_headings:
        title = str(item.get("text", "")).strip()
        if is_noise_heading(title):
            continue
        cleaned.append({
            "line": None,
            "level": item.get("level", 0),
            "title": title[:90],
            "source": "index",
        })
    return cleaned[:30]


def split_sections(body: str, headings: list[dict]) -> list[dict]:
    lines = body.splitlines()
    line_headings = [h for h in headings if h.get("source") == "text" and h.get("line")]
    if line_headings and not (len(line_headings) < 3 and cn_len(body) > 6000):
        sections = []
        for idx, heading in enumerate(line_headings):
            start = int(heading["line"])
            end = int(line_headings[idx + 1]["line"]) if idx + 1 < len(line_headings) else len(lines) + 1
            content = "\n".join(lines[start:end - 1]).strip()
            if cn_len(content) >= 40:
                sections.append({
                    "title": heading["title"],
                    "level": heading["level"],
                    "content": content,
                })
        return sections

    paras = [p.strip() for p in re.split(r"\n\s*\n", body) if cn_len(p) >= 80]
    if len(paras) < 6:
        sentences = sentence_list(body)
        paras = ["".join(sentences[i:i + 8]) for i in range(0, len(sentences), 8) if cn_len("".join(sentences[i:i + 8])) >= 80]
    if not paras:
        return []
    chunks = []
    chunk_size = max(1, len(paras) // 4)
    labels = ["引入/问题段", "主体单元一", "主体单元二", "主体单元三", "结尾单元"]
    for i in range(0, len(paras), chunk_size):
        content = "\n\n".join(paras[i:i + chunk_size])
        if cn_len(content) >= 80:
            chunks.append({
                "title": labels[min(len(chunks), len(labels) - 1)],
                "level": 0,
                "content": content,
            })
        if len(chunks) >= 5:
            break
    return chunks


def classify_sentence_role(sentence: str) -> str:
    if any(cue in sentence for cue in BACKGROUND_CUES):
        return "背景铺陈"
    if any(cue in sentence for cue in PROBLEM_CUES):
        return "问题提出"
    if any(cue in sentence for cue in METHOD_CUES):
        return "视角/方法"
    if any(cue in sentence for cue in CONCLUSION_CUES):
        return "结论/路径"
    return "判断陈述"


def analyze_style(text: str) -> dict:
    sentences = sentence_list(text)
    lengths = [cn_len(s) for s in sentences]
    total = len(sentences)
    starts_no_subject = sum(1 for s in sentences if re.match(r"^(通过|基于|从|在|以|围绕|针对|结合|立足)", s))
    reporting = sum(1 for s in sentences if any(cue in s for cue in REPORTING_CUES))
    policy = sum(1 for s in sentences if any(cue in s for cue in POLICY_CUES))
    theory = sum(1 for s in sentences if any(cue in s for cue in THEORY_CUES))
    mechanism = sum(1 for s in sentences if any(cue in s for cue in MECHANISM_CUES))
    path = sum(1 for s in sentences if any(cue in s for cue in PATH_CUES))
    rhetoric = sum(1 for s in sentences if any(cue in s for cue in RHETORIC_CUES))
    citations = len(re.findall(r"[①②③④⑤⑥⑦⑧⑨⑩]|\[\d+\]|\(\d+\)", text))
    return {
        "sentences": total,
        "avg_sentence_cn": round(sum(lengths) / max(total, 1), 2),
        "max_sentence_cn": max(lengths or [0]),
        "subjectless_opening_pct": pct(starts_no_subject, total),
        "reporting_style_pct": pct(reporting, total),
        "policy_discourse_pct": pct(policy, total),
        "theoretical_density_pct": pct(theory, total),
        "mechanism_terms_pct": pct(mechanism, total),
        "path_terms_pct": pct(path, total),
        "rhetorical_link_pct": pct(rhetoric, total),
        "citation_markers": citations,
    }


def style_label(stats: dict) -> str:
    labels = []
    if stats["subjectless_opening_pct"] >= 20:
        labels.append("多用无主语介词开头")
    if stats["reporting_style_pct"] >= 18:
        labels.append("报道式/转述式较强")
    if stats["policy_discourse_pct"] >= 12:
        labels.append("政策话语嵌入明显")
    if stats["theoretical_density_pct"] >= 18:
        labels.append("理论概念密度较高")
    if stats["mechanism_terms_pct"] >= 15:
        labels.append("机制解释倾向明显")
    if stats["path_terms_pct"] >= 15:
        labels.append("对策/路径导向明显")
    if not labels:
        labels.append("平铺判断与解释为主")
    return "；".join(labels)


def analyze_abstract(abstract: str, source: str) -> dict:
    sentences = sentence_list(abstract)
    roles = [classify_sentence_role(s) for s in sentences[:8]]
    role_counts = Counter(roles)
    stats = analyze_style(abstract)
    if not abstract:
        return {
            "status": "missing",
            "logic": "未检测到可稳定识别的摘要。",
            "style": "无",
            "methods": [],
            "snippet": "",
        }
    logic_parts = []
    if role_counts["背景铺陈"]:
        logic_parts.append("先交代背景或研究语境")
    if role_counts["问题提出"]:
        logic_parts.append("再提出问题、困境或不足")
    if role_counts["视角/方法"]:
        logic_parts.append("随后给出研究视角或分析方法")
    if role_counts["结论/路径"]:
        logic_parts.append("最后落到判断、路径或价值")
    if not logic_parts:
        logic_parts.append("以连续判断陈述推进")
    methods = []
    if stats["subjectless_opening_pct"] >= 15:
        methods.append("常用无主语介词结构起句，如“基于、通过、从、以”。")
    if stats["reporting_style_pct"] >= 15:
        methods.append("采用报道式写法，靠“指出、认为、提出、阐释”等动词组织观点。")
    if stats["policy_discourse_pct"] >= 10:
        methods.append("把政策语汇作为摘要的合法性入口。")
    if stats["theoretical_density_pct"] >= 15:
        methods.append("用核心概念提高摘要的理论密度。")
    return {
        "status": source,
        "logic": "，".join(logic_parts) + "。",
        "style": style_label(stats),
        "methods": methods or ["以概括性陈述压缩研究对象、问题和结论。"],
        "snippet": short_excerpt(abstract),
    }


def section_logic(section: dict) -> dict:
    content = section["content"]
    sentences = sentence_list(content)
    role_counts = Counter(classify_sentence_role(s) for s in sentences)
    stats = analyze_style(content)
    dominant = role_counts.most_common(3)
    if any(cue in section["title"] for cue in ["引言", "问题", "提出"]):
        function = "提出问题并建立研究必要性"
    elif any(cue in section["title"] for cue in ["概念", "内涵", "意蕴", "理论", "前提"]):
        function = "进行概念辨析或理论铺垫"
    elif any(cue in section["title"] for cue in ["机制", "机理", "逻辑", "生成", "建构"]):
        function = "解释机制或生成逻辑"
    elif any(cue in section["title"] for cue in ["困境", "风险", "挑战", "问题"]):
        function = "诊断现实问题或结构性风险"
    elif any(cue in section["title"] for cue in ["路径", "进路", "策略", "对策", "路向"]):
        function = "提出实践路径或改进方向"
    elif any(cue in section["title"] for cue in ["结语", "结论"]):
        function = "收束全文并作价值回归"
    else:
        function = "围绕标题展开解释、判断与材料支撑"
    return {
        "title": section["title"],
        "function": function,
        "cn_chars": cn_len(content),
        "dominant_moves": [f"{name}:{count}" for name, count in dominant],
        "style": style_label(stats),
        "argument_logic": infer_argument_logic(content, role_counts),
        "expression_methods": infer_expression_methods(content, stats),
        "snippet": short_excerpt(content),
    }


def infer_argument_logic(content: str, role_counts: Counter) -> str:
    pieces = []
    if role_counts["背景铺陈"]:
        pieces.append("以背景或语境打开论述")
    if role_counts["问题提出"]:
        pieces.append("用问题/风险推动论证转入")
    if role_counts["视角/方法"]:
        pieces.append("通过视角限定或材料入口组织分析")
    if any(cue in content for cue in MECHANISM_CUES):
        pieces.append("以机制、结构或生成逻辑连接现象与判断")
    if any(cue in content for cue in PATH_CUES):
        pieces.append("把分析推进到路径或实践安排")
    if not pieces:
        pieces.append("以连续解释和判断完成段落推进")
    return "；".join(pieces) + "。"


def infer_expression_methods(content: str, stats: dict) -> list[str]:
    methods = []
    if stats["avg_sentence_cn"] >= 55:
        methods.append("长句承担限定、因果和层次展开。")
    elif stats["avg_sentence_cn"] <= 28:
        methods.append("短中句较多，表达偏直接。")
    else:
        methods.append("中等长度句子为主，兼顾解释与推进。")
    if stats["rhetorical_link_pct"] >= 15:
        methods.append("使用递进、并列和因果连接词维持段内推进。")
    if stats["citation_markers"] >= 3:
        methods.append("引用或注释标记较多，依靠文献/材料增强支撑。")
    if stats["subjectless_opening_pct"] >= 15:
        methods.append("存在较多无主语介词结构，适合压缩背景，但容易削弱判断主体。")
    if stats["reporting_style_pct"] >= 15:
        methods.append("报道式动词较多，适合综述，但过多会削弱作者自己的论证声音。")
    return methods


def attention_points(report: dict) -> list[str]:
    points = []
    stats = report["whole_style_stats"]
    if stats["reporting_style_pct"] >= 22:
        points.append("注意避免把文献转述当成论文论证，需要把“他人认为”转化为自己的问题线索。")
    if stats["path_terms_pct"] >= 22:
        points.append("路径词密度较高，写作时要补足前置机制，避免直接进入对策。")
    if stats["policy_discourse_pct"] >= 18:
        points.append("政策话语较强，借鉴时要转译为学术关系，避免文件语言覆盖论证。")
    if stats["subjectless_opening_pct"] >= 25:
        points.append("无主语开头较多，仿写时要防止句子悬空，重要判断要补出对象和主体。")
    if report["heading_count"] == 0:
        points.append("未检测到稳定标题层级，借鉴时不能直接学习其结构，需要从段落功能反推逻辑。")
    if not points:
        points.append("可重点借鉴其段落推进方式，但仍需核对材料支撑和概念一致性。")
    return points


def markdown_report(report: dict) -> str:
    lines = [
        f"# {report['title']}",
        "",
        "## 基本信息",
        "",
        f"- 原文件：`{report['file']}`",
        f"- 提取状态：{report['status']}",
        f"- 页数：{report['pages']}",
        f"- 提取字符数：{report['chars']}",
        f"- 标题数量：{report['heading_count']}",
        f"- 摘要识别：{report['abstract']['status']}",
        f"- 关键词：{'、'.join(report['keywords']) if report['keywords'] else '未稳定识别'}",
        "",
        "## 摘要拆解",
        "",
        f"- 摘要逻辑：{report['abstract']['logic']}",
        f"- 摘要风格：{report['abstract']['style']}",
        f"- 写作手法：{' '.join(report['abstract']['methods'])}",
        f"- 短引片段：{report['abstract']['snippet'] or '无'}",
        "",
        "## 引言/开篇拆解",
        "",
    ]
    for item in report["opening_sections"]:
        lines.extend([
            f"### {item['title']}",
            "",
            f"- 行文功能：{item['function']}",
            f"- 论证逻辑：{item['argument_logic']}",
            f"- 写作风格：{item['style']}",
            f"- 表达手法：{' '.join(item['expression_methods'])}",
            f"- 短引片段：{item['snippet']}",
            "",
        ])
    lines.extend(["## 主体部分拆解", ""])
    for idx, item in enumerate(report["body_sections"], 1):
        lines.extend([
            f"### 主体单元{idx}：{item['title']}",
            "",
            f"- 行文功能：{item['function']}",
            f"- 论证逻辑：{item['argument_logic']}",
            f"- 主要动作：{'；'.join(item['dominant_moves'])}",
            f"- 写作风格：{item['style']}",
            f"- 表达手法：{' '.join(item['expression_methods'])}",
            f"- 短引片段：{item['snippet']}",
            "",
        ])
    lines.extend(["## 结论/收束拆解", ""])
    for item in report["closing_sections"]:
        lines.extend([
            f"### {item['title']}",
            "",
            f"- 行文功能：{item['function']}",
            f"- 论证逻辑：{item['argument_logic']}",
            f"- 写作风格：{item['style']}",
            f"- 表达手法：{' '.join(item['expression_methods'])}",
            f"- 短引片段：{item['snippet']}",
            "",
        ])
    lines.extend([
        "## 整体文风与论证方式",
        "",
        f"- 整体文风：{report['whole_style_label']}",
        f"- 句均中文字符：{report['whole_style_stats']['avg_sentence_cn']}",
        f"- 报道式写法占比：{report['whole_style_stats']['reporting_style_pct']}%",
        f"- 无主语介词开头占比：{report['whole_style_stats']['subjectless_opening_pct']}%",
        f"- 理论概念密度：{report['whole_style_stats']['theoretical_density_pct']}%",
        f"- 机制词占比：{report['whole_style_stats']['mechanism_terms_pct']}%",
        f"- 路径词占比：{report['whole_style_stats']['path_terms_pct']}%",
        "",
        "## 可借鉴之处",
        "",
    ])
    for item in report["borrowable_patterns"]:
        lines.append(f"- {item}")
    lines.extend(["", "## 需要注意的问题", ""])
    for item in report["attention_points"]:
        lines.append(f"- {item}")
    lines.append("")
    return "\n".join(lines)


def build_report(item: dict) -> dict:
    text_path = Path(item.get("text_file", ""))
    text = clean_text(text_path.read_text(encoding="utf-8", errors="replace")) if text_path.exists() else ""
    body, refs = split_refs(text)
    abstract, abstract_source = detect_abstract(body)
    keywords = detect_keywords(body)
    headings = extract_headings(body, item.get("headings", []))
    sections = split_sections(body, headings)
    opening_sections = [section_logic(s) for s in sections[:1]]
    closing_candidates = [s for s in sections if any(cue in s["title"] for cue in ["结语", "结论"])]
    if not closing_candidates and sections:
        closing_candidates = [sections[-1]]
    closing_sections = [section_logic(s) for s in closing_candidates[:1]]
    body_pool = sections[1:-1] if len(sections) >= 3 else sections[1:4]
    body_sections = [section_logic(s) for s in body_pool[:6]]
    whole_stats = analyze_style(body)
    report = {
        "title": item.get("name", "unknown"),
        "file": item.get("file", ""),
        "status": item.get("status", ""),
        "pages": item.get("pages", 0),
        "chars": item.get("chars", 0),
        "heading_count": len(headings),
        "keywords": keywords,
        "abstract": analyze_abstract(abstract, abstract_source),
        "opening_sections": opening_sections,
        "body_sections": body_sections,
        "closing_sections": closing_sections,
        "whole_style_stats": whole_stats,
        "whole_style_label": style_label(whole_stats),
        "borrowable_patterns": infer_borrowable_patterns(headings, sections, whole_stats),
        "attention_points": [],
        "refs_chars": cn_len(refs),
    }
    report["attention_points"] = attention_points(report)
    return report


def infer_borrowable_patterns(headings: list[dict], sections: list[dict], stats: dict) -> list[str]:
    patterns = []
    level1 = [h["title"] for h in headings if h.get("level") == 1]
    if len(level1) >= 3:
        patterns.append("可借鉴其一级标题之间的递进关系，但需判断是否真有问题推进。")
    if stats["mechanism_terms_pct"] >= 15:
        patterns.append("可借鉴其用机制、结构、生成逻辑连接现象与判断的方式。")
    if stats["theoretical_density_pct"] >= 18:
        patterns.append("可借鉴其概念密度，但仿写时必须保持术语一致。")
    if stats["rhetorical_link_pct"] >= 15:
        patterns.append("可借鉴其段内转折、递进和因果连接方式。")
    if stats["policy_discourse_pct"] >= 12:
        patterns.append("可借鉴其政策话语嵌入方式，但要避免把政策表述直接当结论。")
    if not patterns:
        patterns.append("可作为普通结构样本，重点观察其开篇、段落承接和结尾收束。")
    return patterns


def safe_name(name: str, index: int) -> str:
    stem = Path(name).stem
    stem = re.sub(r"[<>:\"/\\|?*\s]+", "_", stem).strip("_")
    digest = hashlib.sha1(name.encode("utf-8", errors="ignore")).hexdigest()[:8]
    return f"{index:03d}_{stem[:80]}_{digest}.md"


def main() -> int:
    parser = argparse.ArgumentParser(description="Create per-article deconstruction reports from EMARX structure index.")
    parser.add_argument("--index", required=True, help="structure_index.json path")
    parser.add_argument("--output-dir", required=True, help="directory for markdown reports")
    parser.add_argument("--summary", required=True, help="summary JSON path")
    parser.add_argument("--limit", type=int, default=0, help="optional max number of ok articles")
    args = parser.parse_args()

    index_path = Path(args.index)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    items = json.loads(index_path.read_text(encoding="utf-8"))
    ok_items = [item for item in items if item.get("status") == "ok" and item.get("text_file")]
    if args.limit:
        ok_items = ok_items[: args.limit]

    summary = []
    for idx, item in enumerate(ok_items, 1):
        report = build_report(item)
        out_path = output_dir / safe_name(item.get("name", "unknown"), idx)
        out_path.write_text(markdown_report(report), encoding="utf-8")
        summary.append({
            "index": idx,
            "name": item.get("name"),
            "file": item.get("file"),
            "report": str(out_path),
            "chars": item.get("chars"),
            "pages": item.get("pages"),
            "heading_count": report["heading_count"],
            "abstract_status": report["abstract"]["status"],
            "whole_style_label": report["whole_style_label"],
            "attention_points": report["attention_points"],
        })

    summary_path = Path(args.summary)
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    summary_path.write_text(json.dumps({
        "source_index": str(index_path),
        "article_count": len(summary),
        "output_dir": str(output_dir),
        "reports": summary,
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"article_count": len(summary), "summary": str(summary_path), "output_dir": str(output_dir)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
