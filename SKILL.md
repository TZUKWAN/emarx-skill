---
name: emarx
description: "EMARX v6.9 研究型中文学理思辨论文生产技能。用于中文学术论文的构思、结构、写作、审稿、修改、引用、事实核查与 Word 交付。核心流程：先读用户当前工作空间真实论文，锚定三至五篇相关论文并即时拆解，形成内部影子重组、逻辑骨架与段落级大纲，再按大纲逐段生成中文论文。强调生成前协议、无主语摘要、文献消化式写作、段落级对象-关系-材料-机制-判断运动、结构防火墙、大家风范语体、GB/T 7714 引用与 Word 输出。适用领域包括马克思主义理论、思想政治教育、中华文化与国际传播、文化记忆、人工智能哲学、技术批判、主体性研究和人文社科理论写作。"
---

# EMARX

EMARX v6.9 是面向中文学理思辨论文的研究型生产技能。它不是普通写作提示词，也不是论文流程管理器。诊断、锚定、拆解、影子重组、审稿、审计等动作都是后台质量控制，不得写入论文正文或标题。

v6.9 的核心转向是：从“坏稿审计驱动”转向“正确论文语言生成驱动”。规则不再主要靠后期拦截，而要在落笔之前就规定论文语言、段落运动、摘要写法和文献进入方式。

## 核心工作原则

默认顺序如下，除非用户明确要求只完成其中某一步：

```text
工作空间扫描 -> 锚定三至五篇真实论文 -> 即时拆解锚定论文 -> 内部影子重组 -> 逻辑骨架 -> 段落级大纲 -> 按生成协议逐段写作 -> 即时小修 -> 风格校准 -> 审稿 -> 改稿 -> 事实核查 -> Word 交付 -> 简要交付说明
```

前台论文的标题层级必须是论证骨架，不能暴露后台流程。研究对象诊断、概念边界、机制梳理、材料锚定、路径设计等内部工作必须转化为实质性论文章节。

## 生成前协议优先

写作之前，必须先读 `references/generative-writing-protocol.md`。该文件规定：

- 摘要按“对象进入 -> 问题关系 -> 机制判断 -> 风险或价值 -> 路径指向”生成，禁止“本文说明 -> 本文认为 -> 本文从几个方面分析 -> 本文提出路径”。
- 正文段落按“对象锚定 -> 关系展开 -> 材料或文献进入 -> 机制解释 -> 判断落点”生成，禁止“本文认为 -> 有研究指出 -> 因此应该”。
- 每段落笔前先在内部确认：本段对象、关系、材料、判断、如何承接上一段、如何引出下一段；这些信息不得写入正文。
- 文献必须消化为概念来源、机制来源、问题来源或限制来源，再以 `[X]` 随句引用。
- 路径段必须对应已论证的机制，不能写成行动手册。
- 结论回到理论判断，不得复述结构。

生成协议是质量控制的第一道关口。`bad_draft_audit.py` 等脚本只作为最后兜底。

## 必须遵守的语料规律

尊重 `references/distillation-evidence.md` 中的真实论文规律。该文件来自已验证的本地全文流程：359 个 PDF、358 个可读、2,889 / 2,896 页提取、5,161,082 字符、358 份逐篇结构画像、15 份分组综合。不要用通用写作建议覆盖这些真实样本规律。

同时尊重 v5 全量结构复核：`references/length-and-hierarchy-protocol.md` 记录 2026-06-25 对 452 个 PDF、450 个可读、3,700 页、7,783,902 字符的分析。正文 10,000-12,000 字、主体必须有二级标题，是语料支持的硬规则。

## 参考文件路由

按任务读取对应文件：

- `references/generative-writing-protocol.md`：v6.9 核心，摘要、段落、文献、路径、结论的正向生成规则。
- `references/workflow-v4.md`：完整论文流程、资料优先顺序、创新分析、改稿循环。
- `references/anchored-recomposition-workflow.md`：当前工作空间论文锚定、影子重组、段落级大纲、逐段写作。
- `references/length-and-hierarchy-protocol.md`：10,000-12,000 字默认、二级标题、标题层级与结构深度。
- `references/argument-depth-protocol.md`：论证许可、文献消化、段落论证单元、烂稿拒稿规则。
- `references/structure-design-protocol.md`：前台论文结构、诊断性标题防火墙、标题转换、语料对齐的章节设计。
- `references/scholarliness-protocol.md`：学术地图、现象问题化、概念台账、理论框架、温和批判、文献对话、理论抽象。
- `references/style-protocol.md`：平实学体、大家风范、非机械节奏。
- `references/wording-expression-protocol.md`：句级表达、段首规则、否定纪律、动词选择、主宾清晰、过渡方法。
- `references/language-expression-distillation-v68.md`：全量语言表达语料、无主语摘要、反元话语、反综述插入、标点克制。
- `references/material-anchoring-protocol.md`：章节与证据段锚定、内部诊断卡、论断-来源映射、平实结构。
- `references/paragraph-moves-protocol.md`：语料驱动的段落功能与章节节奏。
- `references/writing-rhythm-protocol.md`：质性写作节奏、段落呼吸、判断落点。
- `references/review-rubric.md`：匿名审稿式检查，但审稿是兜底。
- `references/fact-check-protocol.md`：事实风险类别、本地/网络核验、禁止虚构。
- `references/citation-protocol.md`：引用位置、一文献一引、一作者一引、顺序编号、GB/T 7714 文末列表。
- `references/user-research-profile.md`：用户研究方向、偏好、禁用表达、已学习反馈。
- `references/distillation-evidence.md`：语料提炼的标题、摘要、引言、结构、段落、文风规律。
- `references/nuwa-distill/README.md` 及 `references/nuwa-distill/research/*.md`：语料驱动的论证、引用、段落、概念与失败模式。
- `references/review-agent-protocol.md`：四审稿人团队何时运行。
- `references/review-agents/*.md`：ScholarlyReviewer、LogicReviewer、ProseReviewer、FormatReviewer 的角色提示。

## 硬规则

1. 把完整论文当作研究生产流程，不是直接生成聊天文本。
2. 先搜本地工作空间资料，再考虑网络检索。仅在本地资料不足、过时或需要最新政策、数据、法规、文献和事实时使用网络。
3. 不虚构引文、作者、期刊、页码、政策原文、统计数据、案例或来源支撑的判断。
4. 完整论文默认输出 `.docx` Word 文档，除非用户明确要求聊天文本或 Markdown。
5. 正式起草前完成内部研究诊断：核心问题、研究对象、概念台账、理论张力、机制链、来源支撑、创新主张、事实风险、篇幅计划、标题计划。诊断不写入正文。
6. 必须通过 `references/argument-depth-protocol.md` 的论证许可：论文必须有非显而易见的论点、真实张力、机制链与章节论证义务。
7. 诊断卡按 `references/material-anchoring-protocol.md` 作为内部规划文件。仅在用户要求规划、核心论断不确定或起草风险较大时展示。
8. 每个正文主体章节必须至少有一个来自本地来源、案例、政策、数据集、平台机制或经验发现的具体锚点。浮在抽象概念上的段落是坏稿。
9. 必须通过 `references/scholarliness-protocol.md` 的学理诊断：学术地图、现象问题化、概念台账、框架一致性、文献对话计划、批判判断、材料-理论抽象路径。
10. 引用不是支撑标签。来源必须先消化：它回答什么问题、贡献什么概念、有何局限、本文如何使用它。
11. **不能围绕来源覆盖表组织论文。论证选择来源，而不是来源选择论证。** 从一篇工作空间论文移到下一篇的写法是综述，不是论文。
12. 正常完整论文正文默认 10,000-12,000 字，除非用户明确要求更短或更长。不要把 2,000-5,000 字的聊天文本当完整论文交付。
13. 正常完整论文正文主体必须有二级标题。默认一级标题用“一、”，二级标题用“（一）”“（二）”。仅在章节包含多个机制、阶段、主体或案例时使用三级标题。
14. 不写扁平的“机遇、挑战、路径”论文。每个章节必须回答一个理论问题并推进中心论点。
15. 动态使用语料结构。选择某种结构是因为适合题目，而不是因为它听起来整齐。
16. 用平实、清楚、稳健、有分寸、有判断、有学术质感、有大家风范的中文写作。节奏服务推理：长句展开关系，中句承接限定，短句落定判断。不强制句数、句长或交替比例。
17. 审稿和改稿是实质性重构，不是表面润色。
18. 交付前运行坏稿审稿。如果稿件仅在长度、标题、引用上合规却仍像套壳、重复或论证薄弱，应拒稿并重写。
19. 仅在用户要求深度审稿、内部审计发现严重风险或稿件用于高 stakes 交付时，使用 `references/review-agent-protocol.md` 的四审稿人协议。不默认强制多轮审稿，且审稿报告语言不得进入正文。
20. 引用遵循 `references/citation-protocol.md`：一篇文献只引一次、一个作者只引一次、引用紧随使用它的句子、顺序编号、文末按引用顺序以 GB/T 7714 格式排列。
21. 日常表达约束来自 `references/style-protocol.md`：不硬造概念、不使用夸张新奇语言、非必要不用引号和冒号式 AI 标点、避免机械序列词如“首先/其次/再次/最后”。
22. 不依赖“不是……而是……”“并非……而是……”等二元对照公式。直接陈述论断，让证据和机制承担区分。
23. 段首不裸否定。按 `references/wording-expression-protocol.md`：先以对象、关系、材料或学术位置定位读者，再进入限定、批判或判断。
24. 论文语言防火墙：最终文章不得包含诊断卡、机制链、论证任务、审稿轮次、审稿人、通过/不通过、审计、来源覆盖表或其他内部流程语言。
25. 结构防火墙：最终文章不得使用“研究对象与概念边界”“概念界定”“理论框架”“材料锚定”“问题诊断”“学理性诊断”“机制链”“论证任务”“创新点分析”“路径建设与可执行条件”等诊断性或清单式标题，除非用户明确要求研究设计、方法章节或教学大纲。这些工作必须嵌入实质性论证章节。
26. 一级标题必须命名题目内部的真实关系、功能、机制、矛盾、风险、转化或路径。如果标题只是在说作者要做什么，就先重写再起草。
27. 高质量完整论文任务使用 `references/anchored-recomposition-workflow.md`：扫描用户当前工作空间，根据题目选择三至五篇真实本地论文，在任何重组或起草前即时拆解这些论文。
28. 不要从旧拆解报告库锚定。旧报告仅在匹配到当前工作空间文件后作为缓存或阅读索引，不能替代当前文件的扫描、打开与判断。
29. 不要把影子重组稿当最终论文。它只是段落功能、来源角色与逻辑运动的内部地图。最终正文必须逐段重写，带引用、转化与事实核查。
30. 使用锚定工作流时逐段起草。不要一次生成多段再指望后期润色修复逻辑。
31. 应用 `references/language-expression-distillation-v68.md`：摘要默认作者隐身。摘要和正文中不要写“本文”“笔者”“本研究”“本文认为”“本文的核心观点”“文章认为”“文章指出”，除非在引用来源标题或原文。
32. 不要用“有研究指出”“已有研究认为”“相关研究指出”“学者认为”等句式 detached 地插入文献。先把文献消化进论文自己的概念、机制、问题或限制，再引用。
33. 避免正文中的冒号小标题、装饰性引号和破折号式 AI 腔。仅在结构上必要时使用标点。
34. 当新资料或反馈揭示稳定偏好时，更新 `references/user-research-profile.md` 或运行 `scripts/update_user_profile.py`。

## 脚本工具

按需使用自带脚本：

```bash
python scripts/scan_workspace_sources.py --root <workspace> --output sources.json
python scripts/analyze_paper_structure.py --root <workspace> --output-dir structure-report
python scripts/build_research_brief.py --topic "论文题目" --sources sources.json --output research-brief.md
python scripts/scholarliness_audit.py --paper paper.md --output scholarliness-audit.json
python scripts/bad_draft_audit.py --paper paper.md --output bad-draft-audit.json
python scripts/citation_audit.py --paper paper.md --output citation-audit.json
python scripts/deconstruct_corpus_articles.py --index structure_index.json --output-dir article_deconstruction/reports --summary article_deconstruction/summary.json
python scripts/select_anchor_papers.py --topic "论文题目" --workspace-root <current_workspace> --summary article_deconstruction/summary.json --output anchor-papers.md --top-k 5
python scripts/distill_language_expression.py --index structure_index.json --output-json language-expression-distillation.json --output-md language-expression-distillation.md
python scripts/markdown_to_docx.py --input paper.md --output paper.docx
python scripts/update_user_profile.py --profile references/user-research-profile.md --topic "主题" --feedback "用户反馈"
```

脚本输出只是索引或脚手架，不等于最终事实。作出事实性结论前必须检查相关来源文件或核验主张。

## 完整论文流程

1. **资料摄入。** 扫描本地工作空间来源，识别最相关材料。本地材料不足或需要最新信息时进行网络核验。
2. **当前工作空间锚定扫描。** 读取 `anchored-recomposition-workflow.md`。扫描用户当前工作空间并选择三至五篇真实论文。旧拆解报告仅在匹配当前文件后作为可选缓存。
3. **即时拆解锚定论文。** 打开或提取所选论文，分析其摘要逻辑、风格、写作手法、引言、正文运动、结论、标题结构、论证逻辑、文风、表达方法与风险。不要仅从缓存报告出发。
4. **研究简报。** 产出本地来源发现、来源缺口、概念候选、真实张力与事实风险。
5. **学理诊断。** 读取 `scholarliness-protocol.md`。产出学术地图、理论起点、现象问题化、概念台账、框架一致性检查、文献对话计划、批判判断、材料-理论抽象路径。
6. **问题诊断。** 用一句非显而易见的论点陈述论文中心问题。避免“不是 A，而是 B”的套式；直接写出论断，通过概念边界、证据和机制分析完成区分。
7. **论证许可。** 读取 `argument-depth-protocol.md`。在论点、张力、机制链、文献位置和章节义务足够强之前不起草。
8. **内部影子重组。** 如需要，从锚定论文创建段落功能图，保留来源标记。不要把它当最终正文交付。
9. **逻辑骨架。** 把影子重组和用户题目分解为中心论点、一级运动、二级运动与段落序列。
10. **内部材料锚定说明。** 读取 `material-anchoring-protocol.md`。在内部用中心论断、非显而易见性、机制链、来源-论断映射和每章论证义务建立诊断卡。仅在用户要求规划或核心论断需要确认时展示。
11. **语料模式选择。** 读取 `distillation-evidence.md` 和所选论文拆解报告；选择适合本题的标题、摘要、引言、结构、段落和风格模式。
12. **篇幅与标题层级计划。** 读取 `length-and-hierarchy-protocol.md`。计划 10,000-12,000 字、4-5 个一级主体章节、每个主要主体章节都有二级标题。
13. **结构设计。** 读取 `structure-design-protocol.md`。把内部诊断转化为前台论文结构。拒绝把研究工作流程当标题。
14. **引用与文献消化。** 如需引用，读取 `citation-protocol.md`、`argument-depth-protocol.md` 和 `scholarliness-protocol.md`；建立覆盖表，检测作者/来源冲突，说明每份来源如何被消化进论证。
15. **创新分析。** 区分选题、视角、概念、机制、路径和表达创新。如实标记薄弱或虚假创新。
16. **段落级大纲。** 为每个段落建立详细大纲：功能、目标论断、来源锚点、材料、概念、转入、转出、风格参考、事实/引用风险、完成标准。
17. **逐段起草。** 按段落级大纲一段一段写。每段写完后检查论断、来源使用、转化、过渡、引用、节奏和判断落点，再进入下一段。优先遵守 `generative-writing-protocol.md` 的段落运动与文献消化规则。
18. **风格与段落运动校准。** 应用 `style-protocol.md`、`wording-expression-protocol.md`、`language-expression-distillation-v68.md`、`material-anchoring-protocol.md`、`paragraph-moves-protocol.md` 和 `writing-rhythm-protocol.md`：平实语言、自然节奏、作者隐身摘要、清晰判断落点、无论文元话语、无 detached 综述插入、无口号化、无机械句长控制、无裸否定段首、无 AI 式对照套式。
19. **学理校准。** 应用 `scholarliness-protocol.md`：核验领域位置、概念边界、文献对话、批判判断、材料-理论抽象、标题逻辑和段落级理论动作。
20. **深度校准。** 应用 `argument-depth-protocol.md`：每个主要章节都需要概念边界工作、机制解释、反张力、材料支撑和判断落点。在称之为完成前补足缺失的深度。
21. **结构防火墙复核。** 起草后再次应用 `structure-design-protocol.md`。删除或重写每个诊断/清单式标题，确保概念边界工作嵌入实质性章节而非孤立成章。
22. **坏稿审稿。** 应用 `review-rubric.md` 并尽可能运行 `scripts/scholarliness_audit.py` 和 `scripts/bad_draft_audit.py`。形式合规但套壳的稿件必须拒稿。
23. **定向审稿。** 如需要，把 `references/review-agent-protocol.md` 作为内部审稿清单或审稿轮次。报告保存在论文之外。修改薄弱章节，而非只改字词。
24. **事实核查与引用审计。** 应用 `fact-check-protocol.md` 和 `citation-protocol.md`；删除、核验或标记无来源的事实主张；审计引用编号与 GB/T 7714 顺序。
25. **论文语言防火墙。** 从文章中删除所有内部流程词汇、清单式措辞、审稿标签、诊断标题和指令式句子。
26. **Word 交付。** 创建 `.docx`，然后核验文件存在且可读。
27. **画像更新。** 如用户材料或反馈意味着持久偏好，更新画像。

## 交付约定

完整论文交付：

- `.docx` 文件路径；
- 正文字数；
- 标题层级摘要；
- 简要论点摘要；
- 来源基础与来源缺口；
- 创新评估；
- 简要内部质量摘要（仅在交付说明中，不在论文中）；
- 引用覆盖与引用冲突状态（使用引用时）；
- 坏稿审计状态；
- 事实核查状态；
- 残余风险。

规划性任务只交付研究简报、结构、创新分析、篇幅/标题层级计划和下一步动作，不假装已经写成论文。

## 风格目标

目标语体：平实、清楚、稳健、有分寸、有判断、有学术质感、有大家风范。

避免两个极端：

- 晦涩学术迷雾：只有密集名词而无判断。
- 普通评论：清楚但浅薄的常识。

理想段落让复杂论点可被理解而不被扁平化。长句承载关系与机制，短句落定思想。
