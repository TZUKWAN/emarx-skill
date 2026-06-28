# EMARX

EMARX 是一个面向 Codex 的中文学理思辨论文生产技能。v7.2 的目标不是增加更多模板，而是把论文生产还原为真实研究流程：先读资料，锚定论文，精读结构和语言，再建立期刊体例画像、论证骨架、小节论证卡、问题链和文献功能绑定，以小节为准入单元逐段写作，最后做事实、引用、格式和 Word 交付审计。

一句话概括：

> 先读本次工作空间，再吸收语料规律；先判断期刊体例，再建立论证骨架、章下小序和问题链；先让语言在首稿中写对，再用小节质量门和全文审计兜底。

## v7.2 核心变化

- **入口重写为中文 v7 流程**：`SKILL.md` 不再把 v4/英文流程作为主路由，完整论文优先读取 `production-workflow-v7.md` 和 `citation-fact-protocol-v7.md`。
- **当前工作空间优先**：锚定论文必须来自用户本次工作空间的真实文件，旧拆解报告只可作索引。
- **反模板化精读**：每篇锚定论文回到原文连续读取，拆解摘要、引言、标题层级、主体推进、结论、句式节奏和文献进入方式。若报告大段相同，判为模板化失败。
- **期刊体例画像**：落笔前先判断目标期刊或锚定论文体例，区分短引言、标准引言和“政策阐释—文献对话—问题引出”，不默认长引言。
- **人文社科摘要**：摘要采用无作者主语的报道式、思辨式压缩论证，不写成理科式“目的—方法—结果—结论”，也不逐章播报。
- **章下小序**：正文一级标题下、第一个二级标题前通常设置短小小序，用于承接上一层问题并引出本章内部问题链。
- **问题链写作**：每个二级小节先建立“小问题—关系问题—机制问题—限度问题—大判断—转出问题”，正文尽量以小见大，避免宏大判断倒扣材料。
- **小节生产控制**：先形成小节论证卡和文献功能绑定，再在小节内逐段写作；每个二级小节写完必须通过 `section_quality_gate.py`，未通过不得并入全文。
- **结构防火墙**：正文标题不能暴露后台流程。默认禁止把“研究对象与概念边界”“理论框架”“材料锚定”“创新点分析”等诊断动作写成章节。
- **引用与事实合并协议**：新增 `references/citation-fact-protocol-v7.md`，要求来源到论点映射、一文献一次、一作者一次、引用随句插入、文末按 GB/T 7714 顺序排列。
- **Word 交付硬化**：完整论文默认生成 DOCX，并通过独立 DOCX 审计和渲染检查。

## 语料底座

EMARX 继承此前对本地论文的结构、篇幅、标题层级、语言表达和写作节奏分析。已经验证过的关键事实包括：

- 扩展工作空间中有 452 个 PDF；
- 450 个可读 PDF；
- 提取 3,700 页、7,783,902 字符；
- 379 / 450 篇可读论文超过 10,000 字符；
- 317 / 450 篇可读论文检测到二级标题。

因此，完整论文默认要求正文约 10,000-12,000 字，主体部分应有二级标题。

v7 正在进一步进行逐篇全文精读蒸馏：辅助模型只做页块阅读、行号定位和证据压缩，主模型负责复核和综合。未完成全量审计前，不把任何新统计结论写成已验证规律。

## 写作目标

目标语体是：

```text
平实、清楚、稳健、有分寸、有判断、有学术质感。
```

避免：

- “本文认为”“本文指出”“本文的核心观点是”；
- “有研究指出”“相关研究表明”“学者认为”；
- “首先、其次、再次、最后”；
- “不是……而是……”“并非……而是……”；
- 空泛背景、口号式结尾、冒号小标题腔、密集引号和破折号式 AI 腔；
- 把后台诊断、审稿、来源覆盖表和流程语言写进正文。

摘要默认采用无作者主语的中文人文社科报道式表达。正文让文献进入论证，不把文献写成综述插入块；每个小节优先从具体对象或小问题进入，经由问题链推出更大的学理判断。

## 安装方式

```bash
python ~/.codex/skills/.system/skill-installer/scripts/install-skill-from-github.py --repo TZUKWAN/emarx-skill --path . --name emarx
```

安装后重启 Codex。

## 调用示例

```text
使用 $emarx，先读取工作空间资料，再围绕“生成式人工智能语境下中华文化国际传播的机遇、挑战与路径”生成期刊体例画像、研究简报、论文结构、问题链、完整论文和 Word 文档。
```

```text
使用 $emarx，审稿这篇论文，重点检查学理性、结构推进、引用、事实核查、语言是否像论文而不是说明书。
```

## 主要文件

```text
.
├── SKILL.md
├── README.md
├── agents/
│   └── openai.yaml
├── scripts/
│   ├── scan_workspace_sources.py
│   ├── build_research_brief.py
│   ├── select_anchor_papers.py
│   ├── prepare_anchor_reading.py
│   ├── qwen_deep_distill_corpus.py
│   ├── audit_deep_reading_reports.py
│   ├── section_quality_gate.py
│   ├── bad_draft_audit.py
│   ├── citation_audit.py
│   ├── markdown_to_docx.py
│   ├── audit_docx.py
│   └── update_user_profile.py
└── references/
    ├── production-workflow-v7.md
    ├── citation-fact-protocol-v7.md
    ├── qwen-deep-reading-protocol.md
    ├── generative-writing-protocol.md
    ├── journal-genre-and-question-chain-v72.md
    ├── section-production-gate-v71.md
    ├── wording-expression-protocol.md
    ├── style-protocol.md
    ├── structure-design-protocol.md
    ├── length-and-hierarchy-protocol.md
    ├── scholarliness-protocol.md
    ├── review-rubric.md
    └── user-research-profile.md
```

## 常用脚本

```bash
python scripts/scan_workspace_sources.py --root D:\BAOXUE --output sources.json
python scripts/build_research_brief.py --topic "论文题目" --sources sources.json --output research-brief.md
python scripts/select_anchor_papers.py --topic "论文题目" --workspace-root D:\BAOXUE --output anchor-papers.md --top-k 5
python scripts/prepare_anchor_reading.py --anchors anchor-papers.md --output-dir anchor-reading
python scripts/qwen_deep_distill_corpus.py --index structure_index.json --output-dir qwen_deep_reading --transport api
python scripts/audit_deep_reading_reports.py --run-manifest qwen_deep_reading/run.jsonl --expected-count 450
python scripts/section_quality_gate.py --paper paper.md --section-title "（一）小节标题" --output section-gate.json --require-citation
python scripts/bad_draft_audit.py --paper paper.md --output bad-draft-audit.json
python scripts/citation_audit.py --paper paper.md --output citation-audit.json
python scripts/markdown_to_docx.py --input paper.md --output paper.docx
python scripts/audit_docx.py --docx paper.docx --output docx-audit.json
```

脚本输出只是索引、审计或交付辅助。事实、引文、数据、政策和最终质量判断必须回到来源复核。

## 使用边界

EMARX 可以帮助生成研究逻辑、论文结构、论证路径、审稿意见、改稿方案和 Word 文档，但不能自动保证所有现实事实为真。涉及最新政策、法律法规、统计数据、真实案例、直接引语、期刊信息和页码时，必须核验。

不得用 EMARX 虚构作者、引文、刊物、页码、数据、政策原文或案例。
