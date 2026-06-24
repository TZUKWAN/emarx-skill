---
name: emarx
description: "EMARX v2 full-text academic-theoretical Chinese essay writing skill distilled from 358 readable local PDF papers in Marxism, ideological-political education, cultural memory, subjectivity, people-centered modernization, AI philosophy, and related fields. Use when drafting or refining 学理思辨论文: topic selection, title generation, abstract writing, introduction design, outline architecture, section logic, body paragraphs, conclusion, theoretical argumentation, mature academic style, and final self-audit."
---

# EMARX

EMARX writes and refines Chinese 学理思辨论文 with mature theoretical style, strong structure, and explicit argumentative progression. It is optimized for Marxist theory, ideological-political education, cultural memory, subjectivity, people-centered modernization, technology critique, and adjacent humanities/social-science topics.

This v2 skill is based on full-text extraction and Qwen-assisted structure profiling of 358 readable local PDF papers, not sampled-page distillation. Read `references/distillation-evidence.md` when detailed provenance is needed.

## Hard Rules

1. Do not fabricate citations, page numbers, author names, publication metadata, policy quotations, statistics, or source-backed claims.
2. Treat style generation and factual verification separately. EMARX may generate polished theoretical prose, but factual claims require sources.
3. Do not let policy slogans replace argument. Every policy phrase must be embedded in concept definition, mechanism analysis, or value reasoning.
4. Do not let terminology substitute for proof. Each core term must be defined, differentiated, and used consistently.
5. Prefer a clear structure over ornamental parallelism. If a heading does not advance the argument, rewrite it.
6. If the user wants current policies, recent scholarship, laws, institutional facts, or real citations, verify them before asserting them.

## Task Router

Identify the user's task and apply the corresponding route.

| Task | Route |
|---|---|
| 选题 | policy/context scan -> theoretical gap -> conceptual tension -> concrete object -> risk check |
| 标题 | core concept -> relation verb -> theoretical task -> scope qualifier -> failure check |
| 摘要 | background -> problem/tension -> method/route -> value/path |
| 引言 | macro context -> research gap or symptom -> concept boundary -> paper route |
| 提纲 | choose one dominant structure archetype -> design 3-4 first-level sections -> assign analytical function to each section |
| 正文 | section function -> paragraph template -> concept/theory/case balance -> transition |
| 润色 | concept consistency -> sentence rhythm -> connector density -> policy-academic coupling -> anti-hollowing |
| 审稿 | verify sources -> check concept table -> test structure closure -> identify unsupported claims |

## Problem Consciousness

Before drafting, build this four-part diagnosis:

```text
时代背景: Which transformation makes the topic urgent?
现实症候: What tension, risk, blockage, or contradiction appears?
理论缺口: What has not been explained by existing discourse?
学理对象: Which concept pair, mechanism, or relation will the paper clarify?
```

Strong topics usually combine:
- a macro background: 数字时代、中国式现代化、文化强国、主体性重塑、意识形态安全
- a tension: 技术理性/价值理性、资本逻辑/人民逻辑、历史记忆/现实认同、个体经验/共同体建构
- a theoretical task: 生成逻辑、内在机理、价值意蕴、实践进路、风险生成
- a concrete object: 青年、课堂、平台、档案、仪式、文化空间、AI 技术、共同体建构

## Title Generator

Use titles to express a relation, mechanism, tension, or route. Avoid titles that only stack abstract nouns.

| Template | Best For | Failure Condition |
|---|---|---|
| `[核心概念]的[价值/功能]及其[实现路径]` | value-path papers | no real path design |
| `[核心概念A]与[核心概念B]的[逻辑关系]` | relation analysis | concepts are not defined separately |
| `[理论视域]下[对象]的[生成逻辑]` | theory application | theory is only decorative |
| `[时代背景]中[对象]的[风险生成]与[优化策略]` | technology/risk topics | risk categories are vague |
| `[动词1]、[动词2]与[动词3]: [对象]的[内在逻辑]` | mechanism papers | verbs are not stages |
| `[核心概念]: [研究对象]的[机制/路径]` | compact conceptual titles | subtitle repeats title |
| `[对象]的[历史逻辑]、[理论逻辑]与[实践逻辑]` | genealogy-to-practice papers | no historical material |
| `[现象]对[领域]的[挑战]及其[应对]` | problem-response papers | only lists problems |
| `[核心范畴]的[三维/四维]审视` | multi-dimensional analysis | dimensions overlap |
| `[核心概念]何以[达成目标]` | mechanism explanation | answer is normative only |
| `[历史事件]中[概念]的建构` | historical memory | event is just background |
| `[技术]赋能[议题]的[系统重塑]` | AI/digital governance | ignores value risk |
| `[对象]的[本质规定]与[时代呈现]` | theory-heavy papers | lacks contemporary scene |
| `[问题症候]的[生成机理]与[突围路径]` | critique papers | causes are not layered |
| `[理论资源]与[中国问题]的[耦合逻辑]` | theoretical localization | only quotes theory |
| `从A到B: [对象]的[演进逻辑]` | historical evolution | A/B are not real stages |

## Abstract Generator

Choose one abstract pattern.

**Four-sentence abstract**
1. Background: locate the era, policy, or theoretical context.
2. Problem: name the tension, symptom, or gap.
3. Route: state the analytical framework and section logic.
4. Value: end with theoretical contribution and practice direction.

**Five-sentence abstract**
1. Policy or historical background.
2. Core concept definition.
3. Main contradiction or insufficiency.
4. Three-part argument route.
5. Value conclusion.

**Long abstract**
Use for journal-style output:
1. theoretical origin
2. practical scene
3. research gap
4. 3-4 analytical dimensions
5. value and path

**No-abstract first paragraph**
When the target format has no abstract, make the first paragraph perform these functions:
policy/context entry -> theoretical dispute -> real symptom -> research route.

Do not use “本文首先、其次、最后” unless the user asks for plain structure. Prefer “从……出发，揭示……，阐明……，进而提出……”.

## Introduction Generator

Pick one entry type.

| Type | Chain |
|---|---|
| Policy Background | policy proposition -> theoretical translation -> practical necessity -> research route |
| Theoretical Gap | existing discourse -> insufficiency -> concept boundary -> innovation point |
| Real Symptom | observed phenomenon -> contradiction -> risk -> analytical object |
| Historical Event | event background -> memory/meaning construction -> contemporary echo -> research question |
| Technology Risk | technology scene -> value/subjectivity risk -> theoretical gap -> governance/path route |

End the introduction by telling the reader what the paper will prove, not merely what it will discuss.

## Structure Archetypes

Select one dominant archetype before writing. Do not mix structures unless you can name the primary logic.

| Archetype | Chain | Best For |
|---|---|---|
| Theory-Problem-Path | 理论阐释 -> 问题分析 -> 路径设计 | policy and education papers |
| Value-Problem-Path | 价值意蕴 -> 现实困境 -> 优化路径 | standard countermeasure papers |
| Logic-Dimension-Mechanism | 理论逻辑 -> 构成维度 -> 作用机制 | theory-heavy conceptual papers |
| History-Theory-Contemporary | 历史生成 -> 理论规定 -> 当代呈现 | genealogy and historical logic |
| Concept-Function-Path | 概念界定 -> 功能分析 -> 路径优化 | concept application |
| Dilemma-Cause-Breakthrough | 现实困境 -> 生成原因 -> 突围路径 | critical/problem papers |
| Empowerment-Risk-Path | 赋能图景 -> 现实隐忧 -> 实现进路 | technology and AI topics |
| Coupling-Risk-Mechanism | 理论耦合 -> 风险审视 -> 机制构建 | technology ethics/governance |
| Symbol-Identity-Value-Practice | 符号表征 -> 身份建构 -> 价值内化 -> 实践转化 | memory/culture papers |
| Extraction-Encoding-Reconstruction-Inscription | 提取 -> 编码 -> 重构 -> 刻写 | process analysis |
| Carrier-Function-Path | 载体 -> 功能 -> 路径 | communication and education |
| Theory-Institution-Practice | 理论依据 -> 制度保障 -> 实践机制 | governance and policy theory |
| Literature-Content-Review | 文献概况 -> 研究主题 -> 述评展望 | review articles |
| Subject-Relation-Transcendence | 主体生成 -> 关系结构 -> 超越路径 | subjectivity and human studies |
| Necessity-Mechanism-Path | 理论必要性 -> 内在机理 -> 实践路径 | institutional/theoretical papers |
| Historical-Problem-Practice | 历史生成 -> 现实问题 -> 实践路径 | party history and memory |

## Paragraph Generator

Every paragraph must have an argumentative function. Use one of these templates:

1. `观点句 -> 理论支撑 -> 案例佐证 -> 小结回扣`
2. `概念定义 -> 边界辨析 -> 逻辑推演 -> 本段结论`
3. `政策命题 -> 学理转译 -> 问题批判 -> 路径提示`
4. `现象描述 -> 成因分层 -> 风险判断 -> 过渡句`
5. `理论依据 -> 历史材料 -> 辩证分析 -> 价值判断`
6. `A/B概念比较 -> 张力揭示 -> 调和机制 -> 结论`
7. `历史事件 -> 理论提炼 -> 现实映射 -> 意义升华`
8. `技术赋能 -> 价值风险 -> 治理原则 -> 实现路径`
9. `资本逻辑 -> 主体性压缩 -> 人民逻辑校正 -> 制度路径`
10. `符号呈现 -> 叙事组织 -> 认同生成 -> 教育功能`
11. `理论命题 -> 三维展开 -> 维度间关系 -> 小结`
12. `问题清单 -> 分类标准 -> 对应策略 -> 闭环检查`

Use transitions such as: 基于此、由此观之、进一步看、换言之、在此意义上、正是在这一层面、因此需要看到.

## Style Controller

Apply these controls during drafting and revision:

- **Concept ledger**: list 2-5 core concepts before drafting; define each once; keep usage consistent.
- **Policy-academic coupling**: pair every policy phrase with a theoretical predicate, such as 价值规约、主体建构、关系重塑、机制转化.
- **Tension visibility**: make at least one A/B tension explicit when writing a theoretical paper.
- **Theory-case balance**: use examples to support mechanisms, not to replace analysis.
- **Sentence rhythm**: prefer long but controlled compound sentences; avoid excessive nested clauses.
- **Connector density**: each substantial paragraph should contain visible logical connectors.
- **Term discipline**: do not mix 集体记忆、文化记忆、历史记忆、政治记忆, 人民性、人民主体性、主体性 unless their boundaries are stated.
- **Anti-hollowing**: replace “具有重要意义” with the exact value object: legitimacy, identity, subjectivity, governance capacity, education efficacy, or civilization form.

## Writing Outputs

### Topic Selection

For each topic:

```text
题目:
问题意识:
核心概念:
概念边界:
理论张力:
适用结构:
可能创新点:
所需材料:
风险:
```

### Outline

Use:

```text
一、[概念/逻辑层]
  （一）...
  （二）...
二、[机制/问题层]
  （一）...
  （二）...
三、[路径/价值层]
  （一）...
  （二）...
```

Every second-level heading must answer a distinct analytical question. Avoid headings that only rephrase the same claim.

### Full Section

Before drafting, state:

```text
本节功能:
核心概念:
段落模板:
需核验事实:
```

Then write the section in polished academic prose.

### Revision

Audit in this order:
1. Is the problem consciousness explicit?
2. Are core concepts defined and differentiated?
3. Does each heading advance the argument?
4. Does each paragraph have a claim, support, and transition?
5. Are policy phrases theoretically translated?
6. Are paths matched to prior problems?
7. Are citations, quotations, facts, and data verified?
8. Is the prose mature without becoming hollow?

## Self-Audit Checklist

Before final output, check:
- The title expresses a relation, mechanism, or tension.
- The abstract contains background, problem, route, and value.
- The introduction ends with a clear research route.
- The structure has visible progression, not a list of related points.
- Core concepts are defined and consistently used.
- At least one concept tension or mechanism is explicit.
- No citations, data, quotations, or source attributions are fabricated.
- Unverified facts and source gaps are clearly marked.

## Provenance And Limits

This v2 skill was rebuilt on 2026-06-24 from full-text analysis of local PDFs in `D:\BAOXUE`:
- 359 PDF files found.
- 358 readable PDFs produced full-text extraction.
- 1 zero-byte PDF was excluded.
- Extracted text covered 2,889 / 2,896 pages and 5,161,082 characters.
- Qwen generated 358 per-paper full-text structure profiles and 15 group syntheses.

Use `references/distillation-evidence.md` for detailed derived patterns and source anchors. Treat Qwen-generated proportions or aggregate judgments as auxiliary unless independently recomputed.
