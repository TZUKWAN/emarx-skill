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
section plan with each section's argumentative job:
  - section: central claim this section proves
  - section: central claim this section proves
known weak spots:
```

Do **not** include a "local source coverage" list that mirrors the workspace file list. The diagnosis card is an argument plan, not a bibliography preview.

## Source-to-Argument Table

If sources are needed, build a small table that maps each candidate source to a claim, not to a section:

| Claim This Paper Makes | Source | What the Source Supplies | How It Is Used |
|---|---|---|---|
|  |  |  |  |

Rules:

- Every source must attach to a paper claim, not to a topic area.
- Do not assign one source per section by default.
- A section may use zero, one, or multiple sources depending on its argumentative job.
- If a source does not support a specific claim, leave it out.

## Warning: Do Not Write a Review

A paper structured around sources is a review, not a thesis. Watch for these signs:

- each major section is named after a source or a school;
- paragraphs begin with author names and end with citations;
- the paper's flow is "A 指出… B 认为… C 区分了…";
- removing the citations leaves a list of other people's claims rather than your own argument.

If these signs appear, discard the outline and rebuild it around the paper's own claim structure.

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

## Corpus-Driven Anchor Rules

Based on the nuwa distillation of the workspace corpus:

1. **Policy texts must be anchored as problems, not as conclusions.** A policy quotation is valid only when it is immediately followed by a research question, boundary condition, or concrete contradiction.
2. **Theories must be anchored as operational variables.** After a theory is named, show the 2-4 observable dimensions or analytical layers it produces for this paper.
3. **Cases must be anchored as mechanism tests.** Every case paragraph must state which link of the mechanism chain it supports and why removing it would weaken the claim.
4. **Countermeasures must be anchored as executable actions.** Vague verbs such as "完善/加强/深化/优化/构建" are not anchors unless they specify who does what, to what, by what standard, and by when.
5. **Data and platforms must be anchored with verifiable details.** Prefer named platforms, dates, access numbers, sample sizes, or research designs over slogan-like lists.

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
