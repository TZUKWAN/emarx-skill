# EMARX

EMARX 是面向 Codex 的中文学理思辨论文生产技能，用于中文人文社科论文的资料读取、论文选题、结构设计、摘要、引言、正文写作、引用、事实核查、审稿、改稿和 Word 交付。

当前版本：v7.3。

## 核心要求

- 先读用户当前工作空间中的真实资料，再写论文。
- 锚定三至五篇相关论文并回到原文精读，不能用旧报告替代本次读取。
- 写作前形成期刊体例画像、研究诊断、来源到论点映射、论证骨架、小节论证卡、问题链和段落级大纲。
- 完整论文默认正文 10000-12000 字，主体必须有二级标题。
- 标题不能用问句。论文题目、一级标题、二级标题和三级标题不得出现问号，也不得使用“如何、何以、为何、为什么、怎样、怎么、是否、能否、吗”等题目化提问腔。
- 正常完整中文人文社科期刊论文参考文献不少于 28 条。少于 28 条必须说明真实材料限制，不能用未读、无关、重复作者或不可核验文献凑数。
- 每篇文献只引用一次，每个作者只出现一次，引用随真正使用来源的句子插入，文末按 GB/T 7714 顺序排列。
- 默认生成 Markdown 工作稿和 Word 文档，并运行引用审计、坏稿审计、学理性审计和 DOCX 审计。

## 安装

```bash
python ~/.codex/skills/.system/skill-installer/scripts/install-skill-from-github.py --repo TZUKWAN/emarx-skill --path . --name emarx
```

安装后重启 Codex。

## 常用命令

```bash
python scripts/scan_workspace_sources.py --root D:\BAOXUE --output sources.json
python scripts/build_research_brief.py --topic "论文题目" --sources sources.json --output research-brief.md
python scripts/select_anchor_papers.py --topic "论文题目" --workspace-root D:\BAOXUE --output anchor-papers.md --top-k 5
python scripts/prepare_anchor_reading.py --anchors anchor-papers.md --output-dir anchor-reading
python scripts/section_quality_gate.py --paper paper.md --section-title "（一）小节标题" --output section-gate.json --require-citation
python scripts/bad_draft_audit.py --paper paper.md --output bad-draft-audit.json
python scripts/scholarliness_audit.py --paper paper.md --output scholarliness-audit.json
python scripts/citation_audit.py --paper paper.md --output citation-audit.json --min-count 28
python scripts/markdown_to_docx.py --input paper.md --output paper.docx
python scripts/audit_docx.py --docx paper.docx --output docx-audit.json --min-reference-count 28
```

小样本测试可以显式使用 `--min-count 0` 或 `--min-reference-count 0`，但完整论文不得绕过 28 条参考文献下限。

## 主要文件

```text
SKILL.md
agents/openai.yaml
references/production-workflow-v7.md
references/citation-fact-protocol-v7.md
references/journal-genre-and-question-chain-v72.md
references/generative-writing-protocol.md
references/structure-design-protocol.md
references/length-and-hierarchy-protocol.md
references/style-protocol.md
references/review-rubric.md
scripts/bad_draft_audit.py
scripts/citation_audit.py
scripts/audit_docx.py
```

## 使用边界

EMARX 可以帮助组织研究逻辑、写作论文、生成 Word 和进行格式审计，但不能自动保证所有现实事实、最新政策、真实案例和文献页码为真。涉及最新事实、政策法规、数据、直接引语、案例细节和期刊信息时，必须回到来源核验。
