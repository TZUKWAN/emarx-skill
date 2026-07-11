---
name: emarx
description: "EMARX v7.4 中文学理思辨论文生产技能。用于中文人文社科论文的选题、资料读取、结构搭建、正文写作、审稿改稿与 Word 交付。核心要求：先读用户当前工作空间真实资料，锚定三至五篇相关论文并精读，形成期刊体例画像、论证骨架和段落级大纲，再以小节为最小单元写成 10000-12000 字左右、有二级标题、学理性强、语言平实成熟的论文。v7.4 重点减少规则过载和模板化，吸收 marx-paper-skills 的 Word 交付技术和选题结构方法。"
---

# EMARX v7.4

EMARX 是中文学理思辨论文生产技能，不是论文说明书、流程展示器或提示词集合。所有扫描、锚定、诊断、审稿和引用审计都属于后台工作，不能写进论文正文。

目标是生成能进入中文人文社科期刊语境的论文：问题意识明确，结构有推进，概念稳定，论证有材料和机制支撑，语言平实、稳健、有学术质感。完整论文默认生成 Markdown 工作稿和 Word 文档。

## 一、总原则

1. **先读本次工作空间，再使用既有语料规律**。旧报告、旧画像和旧蒸馏结论只能作索引，不能替代当次原文读取。
2. **论文结构由题目内部的真实关系生长出来**，不把“研究对象与概念边界”“理论框架”“材料锚定”“创新点分析”等后台动作做成正文标题。
3. **写作之前必须形成期刊体例画像、论证骨架和段落级大纲**。小节是最小准入单元，小节内每个自然段只承担一个清楚的论证推进；一节写完、审完、过门后，再进入下一节。
4. **正文必须围绕问题逐段推进**。每个小节先以小问题进入，再推出中层机制和较大判断，尽量以小见大，避免从宏大判断倒扣材料。
5. **正确表达要在首稿生成时形成**，不能依赖后期检测批量修补。审计脚本只作最后兜底。
6. **引用、事实和 Word 交付都必须有证据**。没有核验，不得宣称完成。
7. **千问、脚本和辅助模型只能做低风险的读取、提取、定位、压缩和分类**；主模型必须亲自复核关键来源、判断、结论和交付物。
8. **标题不得使用问句或题目化提问腔**。一级、二级和必要的三级标题中不得出现问号，也不得使用“如何、何以、为何、为什么、怎样、怎么、是否、能否、吗”。
9. **完整论文默认参考文献不少于 28 条**。若用户明确要求更少、目标期刊有明确更少体例、或工作空间真实可用文献不足 28 条，必须在交付说明中明示原因；不得用无关文献、重复作者、假文献或未读文献凑数。
10. **450 份拆解报告只作索引，不是写作模板**。其中大量包含固定套话，已完成清洗并备份；使用时应读取 `.codex/emarx/article_deconstruction_v1/reports_cleaned/` 中的版本，并仍以当次工作空间真实论文的精读为准，不得把报告中的固定话术直接搬进正文。
11. **政治合规是顶刊第一关**。涉及党的创新理论、党史、民族、宗教、港澳台、国际关系等敏感议题时，必须回到权威原文，禁止出现政治方向性错误和敏感表述。
12. **主动降低 AI 痕迹并预检查重**。顶刊已普遍引入 AI 检测和查重审查，交付前必须控制总体 AI 率在 10% 以下、局部在 20% 以下，查重率符合目标期刊要求。

## 二、优先读取文件

### 必读（完整论文任务）

- `references/production-workflow-v7.md`：从资料建档到 Word 交付的主流程。
- `references/citation-fact-protocol-v7.md`：引用、事实核查和 GB/T 7714。
- `references/generative-writing-protocol.md`：摘要、正文、文献进入、路径段和结论的生成规则。
- `references/section-production-gate-v71.md`：小节论证卡、小节级生成和质量准入门槛。
- `references/style-protocol.md`：平实学术语言和语体要求。
- `references/wording-expression-protocol.md`：段首、否定、动词、过渡和标点纪律。
- `references/ten-writing-methods.md`：马理论论文常用的十种论证方法。
- `references/writing-method-selector.md`：根据题目类型和段落任务选择合适的方法组合。
- `references/logical-chain-protocol.md`：标题之间、段落之间、句子之间的逻辑推理链策略。
- `references/theoretical-problem-checklist.md`：动笔前必须回答的五个理论问题。
- `references/theoretical-increment-protocol.md`：判断论文比已有研究多解释了什么。
- `references/concept-ledger-protocol.md`：核心概念定义、来源、区分和稳定性管理。
- `references/classic-text-reading-protocol.md`：经典文本何时精读、怎么进入正文。
- `references/marxist-classics-index.md`：马克思主义经典文本主题索引和常见误读。
- `references/political-compliance-protocol.md`：马理论论文政治方向、政策引用和敏感表述把关。
- `references/ai-trace-mitigation-protocol.md`：降低 AI 痕迹、查重与 AI 检测预检。

### 按需读取

- `references/topic-and-structure-guide.md`：选题与结构轻量指南（吸收 marx-paper-skills 方法）。
- `references/journal-genre-and-question-chain-v72.md`：期刊体例画像、引言模式、章下小序和问题链写法。
- `references/journal-profiles/`：马理论顶刊精准画像，用于目标期刊匹配。
- `references/structure-design-protocol.md`：标题结构与诊断性标题防火墙。
- `references/length-and-hierarchy-protocol.md`：10000-12000 字、标题层级和结构深度。
- `references/scholarliness-protocol.md`：学理性、概念、理论框架、批判和抽象。
- `references/policy-to-problem-mapping.md`：把重大政策精神转化为学术命题。
- `references/methodology-selection-guide.md`：根据题目类型选择方法论进路。
- `references/case-material-protocol.md`：案例材料选择、使用与写作规范。
- `references/peer-review-response-protocol.md`：外审意见修改与回应策略。
- `references/review-rubric.md`：匿名审稿式质量检查。
- `references/user-research-profile.md`：用户稳定偏好和历史失败教训。
- `references/cnki-integration-protocol.md`：EMARX 与 CNKI Control 的集成方式（按需读取，工作空间本地文献不足时使用）。

旧版文件已移入 `references/archive/`，若其内容与 v7.4 协议冲突，以 v7.4 协议为准。

## 三、完整论文六段流程

### 1. 审题选题

- 明确用户场景（课程论文 / 期刊投稿 / 学位论文）、目标期刊、已有资料和方向明确度。
- 若用户有目标期刊，读取 `references/journal-profiles/` 中对应画像，按该刊选题偏好、篇幅体例和风格组织论文。
- 参考 `references/topic-and-structure-guide.md` 的三层选题法：特征识别 → 情况分流 → 拟题配方。
- 拟出的候选题目应符合“大背景 + 小切口”“问题意识鲜明”“标题无问号”等原则。
- **动笔前必须回答 `references/theoretical-problem-checklist.md` 中的五个问题**，并进一步用 `references/theoretical-increment-protocol.md` 判断理论增量。
- 若题目涉及重大政策精神，参考 `references/policy-to-problem-mapping.md` 把政策语言转化为学术命题。
- 若工作空间本地文献不足，可调用 `scripts/emarx_search_cnki.py` 搜索 CNKI（北大核心 + CSSCI），并用 `scripts/emarx_import_cnki.py` 生成研究简报，辅助判断研究现状与选题缺口。详见 `references/cnki-integration-protocol.md`。
- 参考 `references/methodology-selection-guide.md` 初步确定方法论进路。

### 2. 锚定精读

- 扫描本次工作空间中的真实论文，区分正式论文、政策资料、用户草稿和技能文件。
- 根据题目选择 3-5 篇功能互补的锚定论文：研究对象接近、理论视角有用、结构值得参照、材料支撑充分、表达节奏成熟。
- 工作空间本地文献不足时，可用 `scripts/emarx_search_cnki.py` 搜索 CNKI（北大核心 + CSSCI），批量采集摘要后用 `scripts/emarx_import_cnki.py` 生成候选锚定论文列表。
- 锚定后必须回到原文连续读取，不能只看拆解报告或 CNKI 摘要。重点看摘要、引言、标题关系、段落运动和文献进入方式。
- **建立概念台账**：参考 `references/concept-ledger-protocol.md`，记录题目核心概念的定义、来源、与相近概念的区分、论证功能和使用边界。
- **经典文本精读**：如果题目涉及马克思主义经典概念或文本，参考 `references/classic-text-reading-protocol.md` 和 `references/marxist-classics-index.md`，回到原文精读，并按“论证参与式”进入正文。

### 3. 结构与素材

- 参考 `references/topic-and-structure-guide.md` 的结构方法，根据对象内部关系搭建 3-5 个一级标题，每个主体部分配二级标题。
- 一级标题之间必须形成递进关系，前一部分产生后一部分的论证必要性。任意两节互换顺序后仍然成立，说明结构只是并列罗列。详见 `references/logical-chain-protocol.md`。
- 一级标题下、第一个二级标题前，原则上安排一段短小章下小序。
- 建立来源到论点映射，每篇文献只绑定一处正文使用位置，一个作者只出现一次。
- 整理直接引用（按来源分类）和间接引用（按结构部分分类，每篇最多 1 条）。
- 根据题目需要选择和使用案例材料，参考 `references/case-material-protocol.md`。
- 写作过程中持续对照概念台账，确保核心概念内涵外延一致；出现新概念时补录台账。
- 涉及政策、党史、民族、宗教、港澳台、国际关系等敏感议题时，按 `references/political-compliance-protocol.md` 进行政治合规自查。
- **大纲完成后，调用 `agents/outline-reviewers/` 中的 5 个 subagent 进行逻辑审查**，综合其报告后再进入正文写作。

### 4. 小节写作

- 每个二级小节先写论证卡（解释的关系、承接问题、材料功能、推荐写作方法及选择理由、最终判断、下一节必要性）。方法选择参考 `references/writing-method-selector.md`，根据题目类型和段落任务确定 1-2 种主导方法。
- **论证卡写完后，调用 `agents/section-card-reviewers/` 中的 5 个 subagent 进行审查**，确认承接关系、问题链、方法匹配、文献功能和转出必要性都无问题后，再开始生成正文。
- 小节内逐段生成，段落之间必须建立逻辑关联：前一段的判断应为后一段的展开前提或未尽问题。参考 `references/logical-chain-protocol.md`。
- 当前段写完后立即检查：对象是否清楚、文献是否消化、引用是否进入句子、段首是否悬空或裸否定、方法是否匹配任务、与上下段逻辑是否连贯、结尾是否口号化。
- 段落运动是生成前检查项，不是固定五步模板。不同段落可选择不同进入方式（见 `generative-writing-protocol.md` 和 `references/ten-writing-methods.md`）。
- 涉及经典文本的段落，按 `references/classic-text-reading-protocol.md` 的“论证参与式”进入，避免语录式引用。
- 涉及矛盾分析、批判建构、概念界定、历史条件分析等，可参考 `references/ten-writing-methods.md` 和 `references/writing-method-selector.md` 选择合适方法。
- **禁止所有小节使用同一种方法，禁止为使用方法而硬造对立或虚假矛盾**。
- **每个小节写完后，调用 `agents/paragraph-reviewers/` 中的 5 个 subagent 进行审查**，检查段落推进、论-据-证闭环、语言风格、引用位置和收束质量。
- 失败的小节不得进入全文草稿；同一小节连续出现同类硬性问题，应缩小粒度或更换策略。

### 5. 审稿改稿

- 初稿完成后先审逻辑（中心判断是否贯穿、标题链是否递进、材料是否支撑判断），再审语言（禁用表达、AI 腔、公式化对照），然后审政治合规（`references/political-compliance-protocol.md`），最后审格式。
- 运行 `scripts/ai_trace_audit.py` 检查 AI 痕迹，对高风险段落进行人工改写。
- 形式合格但仍像说明书、综述或套壳稿时，必须重写结构或段落，不能只润色。
- 失败稿回炉不得全文润色。应保留中心判断、标题链、来源映射和有效材料，回到干净段落级大纲按小节重写。
- 收到外审意见后，参考 `references/peer-review-response-protocol.md` 进行修改和回应。

### 6. Word 交付

- 使用新的 Word 交付 pipeline：

```bash
python scripts/emarx_build_docx.py paper.md paper.docx
```

- **默认生成圈码 ①②③ 并每页重新编号**。Word COM 调用会优先复用你已打开的 Word/WPS 实例，没有已运行实例时才新建隐藏实例，尽量不影响前台工作。
- 若不希望调用 Word/WPS COM，加 `--no-circle`：

```bash
python scripts/emarx_build_docx.py paper.md paper.docx --no-circle
```

- 默认删除文末参考文献表中的具体条目，避免与页下注重复。如需保留文末参考文献表（会与页下注重复），加 `--keep-references`：

```bash
python scripts/emarx_build_docx.py paper.md paper.docx --keep-references
```

- 交付前必须确认：标题黑色、正文引用为上标、脚注格式正确、参考文献悬挂缩进、摘要和关键词格式正确。

## 四、语言规则

目标语体是平实、清楚、稳健、有分寸、有判断、有学术质感。

禁止或强烈避免：

- 论文元话语：“本文认为”“本文指出”“本文旨在”“本文从……展开”“本文的核心观点是”“笔者认为”“本研究认为”“文章认为”；
- 无内容综述引语：“有研究指出”“相关研究表明”“已有研究认为”“学者认为”“国内外学者普遍认为”“学术界认为”；
- 结构预告与自我指涉：“本文将从以下几个方面展开”“下文将”“前文指出”“前文已经说明”“上文认为”“如前文所述”“综上所述”（正文内部）；
- “首先、其次、再次、最后”的机械序列；
- “不是……而是……”“并非……而是……”等公式化对照；
- “重构、重建、填补空白”等夸张自我拔高；
- 段首裸否定；
- 冒号小标题腔（“问题在于：”“核心观点是：”）；
- 装饰性引号、破折号和过度标点；
- 标题中的“何以、为何、如何、为什么、怎样、怎么、是否、能否、吗”。

概念要稳定，动词要承担推进。能用清楚动词表达的地方，不用抽象名词堆叠。

## 五、脚本工具

脚本用于索引、审计和交付，不等于最终事实判断。

```bash
# 资料与锚定
python scripts/scan_workspace_sources.py --root <workspace> --output sources.json
python scripts/select_anchor_papers.py --topic "论文题目" --workspace-root <workspace> --output anchor-papers.md --top-k 5
python scripts/build_research_brief.py --topic "论文题目" --sources sources.json --output research-brief.md

# CNKI 检索（本地文献不足时使用，需先安装 scripts/cnki/requirements.txt）
python scripts/cnki_cli.py search "生成式人工智能 国际传播" --pages 3 --output workspace/cnki_results.json
python scripts/cnki_cli.py read-batch --results workspace/cnki_results.json --output-dir workspace/summaries --limit 10
python scripts/cnki_cli.py import --results workspace/cnki_results.json --summaries-dir workspace/summaries --output-dir workspace --top-k 10

# 小节与质量
python scripts/section_quality_gate.py --paper paper.md --section-title "（一）小节标题" --output section-gate.json --require-citation

# 审计
python scripts/bad_draft_audit.py --paper paper.md --output bad-draft-audit.json
python scripts/scholarliness_audit.py --paper paper.md --output scholarliness-audit.json
python scripts/citation_audit.py --paper paper.md --output citation-audit.json --min-count 28
python scripts/citation_position_audit.py --paper paper.md --output citation-position-audit.json
python scripts/ai_trace_audit.py --paper paper.md --output ai-trace-audit.json

# Word 交付（新 pipeline）
python scripts/emarx_build_docx.py paper.md paper.docx                   # 默认圈码 + 每页重编号（静默 COM）
python scripts/emarx_build_docx.py paper.md paper.docx --no-circle       # 不调用 COM
python scripts/emarx_build_docx.py paper.md paper.docx --keep-references # 保留文末参考文献表
python scripts/audit_docx.py --docx paper.docx --output docx-audit.json
```

## 六、逻辑审查 subagent 群

为加强文章逻辑链路控制，EMARX 在三个关键节点引入 subagent 群进行多视角讨论和梳理。每个群由 3-5 个定位不同的 agent 组成，输出审查报告供主模型参考。subagent 只负责挑问题和给建议，**不直接改写正文**。

### 1. 大纲逻辑审查 agent 群

在大纲完成后、正文写作前运行，位于 `agents/outline-reviewers/`：

| Agent | 定位 |
|---|---|
| `structure-progression-reviewer.md` | 检查一级标题递进关系，做互换测试和删除测试 |
| `problem-consciousness-reviewer.md` | 检查问题意识尖锐度和理论增量是否明确 |
| `concept-consistency-reviewer.md` | 检查概念台账稳定性和标题概念关系 |
| `material-feasibility-reviewer.md` | 检查材料是否支撑大纲中的每个判断 |
| `journal-fit-reviewer.md` | 检查结构是否符合目标期刊体例画像 |

### 2. 小节论证卡审查 agent 群

在每个二级小节生成前运行，位于 `agents/section-card-reviewers/`：

| Agent | 定位 |
|---|---|
| `continuity-reviewer.md` | 检查本节与上一节的承接关系是否真实 |
| `question-chain-reviewer.md` | 检查小问题链是否完整并能推到大判断 |
| `method-fit-reviewer.md` | 检查推荐写作方法是否匹配本节任务 |
| `source-function-reviewer.md` | 检查文献功能绑定和支撑有效性 |
| `transition-necessity-reviewer.md` | 检查本节是否为下一节留下必要问题 |

### 3. 段落逻辑审查 agent 群

在每个小节写完后运行，位于 `agents/paragraph-reviewers/`：

| Agent | 定位 |
|---|---|
| `paragraph-progression-reviewer.md` | 检查段落之间是否存在逻辑跳跃 |
| `evidence-argument-reviewer.md` | 检查每个段落的论-据-证闭环 |
| `language-style-reviewer.md` | 检查 AI 腔、元话语、口号化等语言问题 |
| `citation-position-reviewer.md` | 检查引用是否紧随使用句、是否堆在段尾 |
| `closure-quality-reviewer.md` | 检查段落和小节收束是否落到具体判断 |

### 使用原则

- subagent 群在大纲、小节生成前、小节生成后三个节点运行；
- 每个 agent 只从自己的定位出发审查，避免面面俱到导致模糊；
- 主模型综合各 agent 报告后决定是否调整，并负责最终判断；
- subagent 不替代审计脚本，而是与脚本互补：脚本做机械扫描，subagent 做逻辑诊断；
- 不引入多层嵌套 subagent，避免上下文传递失真。

## 七、交付标准

完整论文交付必须包含：

- Markdown 工作稿路径；
- DOCX 文件路径；
- 正文字数；
- 标题层级摘要；
- 核心论点摘要；
- 使用的主要本地来源和来源缺口；
- 引用冲突、引用审计状态和引用位置审计状态；
- 参考文献数量，若少于 28 条必须说明真实原因；
- 事实核查状态；
- 政治合规自查状态；
- AI 痕迹审计状态；
- 查重预检与 AI 检测预检状态；
- DOCX 审计和渲染检查状态；
- 残余风险。

交付前必须至少运行语言风险审计、引用审计、引用位置审计和 DOCX 审计；其中任何一项未通过时，只能说明正在回炉或存在风险，不能宣称稿件合格。

没有生成 Word 不能说已生成 Word；没有审计不能说已审计；没有核验来源不能说事实可靠。EMARX 的质量以真实产物和证据为准。
