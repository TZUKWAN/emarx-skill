# EMARX Material Anchoring Protocol

This protocol stops EMARX from writing paragraphs that float on abstract concepts. It requires every argument paragraph to be tied to something concrete: a case, a policy text, a dataset, a platform mechanism, a specific scholarly finding, or a direct quotation from a local source.

## Core Rule

A **section** without a concrete anchor is a bad section. An individual paragraph can be conceptual, but it must belong to a section that eventually lands on something concrete.

A concrete anchor can be:

- a case or example named in enough detail that the reader can locate it;
- a policy document, law, standard, or regulation cited by name and date;
- a dataset, statistic, survey result, or measurable trend;
- a specific platform mechanism, product feature, or technical process;
- a direct quotation or specific claim from a source, with citation;
- an empirical finding from a paper in the workspace corpus.

What does **not** count as an anchor:

- repeating the paper's own abstract concepts;
- saying "相关研究表明" without naming the study or its finding;
- listing benefits or risks in general terms;
- using policy slogans or common-sense observations.

## Paragraph Functions and Anchors

Different paragraphs do different work. See `references/paragraph-moves-protocol.md` for the full taxonomy. The anchor rule applies by function:

- **Topic-setting paragraphs** name the object or problem. They may be conceptual.
- **Mechanism paragraphs** explain how something works. They should connect to an anchor soon, but may first build the conceptual steps.
- **Evidence paragraphs** must contain an anchor.
- **Boundary paragraphs** often use conceptual distinctions, but should point to a case or source that motivates the boundary.
- **Transition paragraphs** carry the argument forward; they do not need a new anchor if the surrounding paragraphs have one.
- **Judgment paragraphs** return to the thesis; they may summarize the anchor already supplied.

Do not require every paragraph to contain a case. Require that every argumentative cluster has at least one concrete anchor.

## Plain-Language Structure Rule

When restructuring a title or outline, use the ordinary vocabulary of the field. Do not import fancy structural words just to make the outline look more theoretical.

Preferred plain headings:

- 问题的提出
- 研究对象与核心概念
- 技术如何改变传播
- 风险从何而来
- 已有的路径及其局限
- 可以改进的方向

Avoid ornamental structural words unless the argument genuinely needs them:

- 张力
- 治理响应
- 中介结构
- 意义组织系统
- 解释关系

If the user has already used these terms in prior materials, they can stay. Do not invent them to impress.

## Before Drafting: Interactive Diagnosis Card

For every full paper, produce a short diagnosis card and show it to the user before drafting. Wait for user confirmation or revision.

The card must include:

```text
central claim in one sentence:
why this claim is not obvious:
main research object:
key concept and its boundary:
real tension or counter-position:
mechanism chain (2-4 steps):
local source coverage:
  - source file / citation / what it supplies
  - source file / citation / what it supplies
section plan with each section's argumentative job:
known weak spots:
```

Do not draft the full paper until the user has seen and approved this card.

## Source Coverage Table

After scanning local sources, build a table:

| Section | Local Source | What It Provides | How the Paper Uses It |
|---|---|---|---|
|  |  |  |  |

Every major body section must have at least one local source entry. A section that relies only on common knowledge or web search is under-sourced.

## Section Anchor Check

While drafting and revising, check each body section:

1. Does the section contain at least one evidence paragraph with a concrete anchor?
2. Are the conceptual paragraphs leading to or building on that anchor?
3. Does the anchor appear before the section's judgment, not tacked on at the very end as decoration?
4. If the anchor is removed, does the section collapse into empty abstraction?

If the answer to (1) is no, add evidence or rewrite the section.
If the answer to (4) is yes, the anchor is only decorative; rewrite.

## Paragraph Anchor Check

For individual paragraphs, use paragraph-function labeling rather than a mechanical anchor test:

- Label the paragraph as topic-setting, mechanism, evidence, boundary, transition, or judgment.
- Evidence paragraphs must name a concrete object, case, policy, data point, or source.
- Other paragraphs should perform their function clearly and connect to evidence elsewhere in the section.

## What a Good Anchor Looks Like

Weak:

> 生成式人工智能可以帮助中华文化更好地出海，提升传播效能，但也可能带来文化主体性风险。

Stronger:

> 2023 年国家网信办等七部门发布的《生成式人工智能服务管理暂行办法》将生成服务纳入公共治理视野；这意味着中华文化内容若依赖商用模型生成，其训练语料、价值排序和责任归属均需重新评估。

Weak:

> 平台算法可能压缩文化意义。

Stronger:

> TikTok 的推荐逻辑以完播率和互动率为核心指标；在这种机制下，需要背景解释的文化内容往往被切割成 15 秒以内的视觉片段，片段可以获量，却难以回到整体意义。

## Anchor Types by Section

- **Introduction**: anchor in a real policy shift, a visible phenomenon, or a clearly named scholarly gap.
- **Mechanism section**: anchor in a platform rule, a technical process, a law, or an empirical finding.
- **Risk section**: anchor in a concrete case of distortion, misreading, or governance failure.
- **Path section**: anchor in an existing attempt, its limit, and the specific condition under which the proposed path works.
- **Conclusion**: return to the anchor from the introduction, but now with the paper's answer attached.

## Bad-Draft Audit Implications

`scripts/bad_draft_audit.py` flags sections where several consecutive paragraphs appear to lack anchors. A single conceptual paragraph is not automatically wrong. The model must either add an anchor nearby or justify why the paragraph can remain abstract because its function is topic-setting, mechanism, boundary, or transition.

## Interaction with Other Protocols

- `argument-depth-protocol.md`: the mechanism chain must be built from anchors, not from abstract factors.
- `scholarliness-protocol.md`: material-to-theory abstraction starts from material, not from more theory.
- `style-protocol.md`: plain language and concrete anchors work together. A plain sentence with a real case is stronger than a fancy sentence with no case.
- `wording-expression-protocol.md`: anchors satisfy the rule that a paragraph must first give the reader an object, relation, or material before making judgments.
