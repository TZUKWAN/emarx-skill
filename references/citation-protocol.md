# EMARX Citation Protocol

Use this protocol whenever EMARX writes, revises, audits, or exports a paper with references.

## Core Rules

1. **Coverage is not an argument.** Do not treat workspace literature as a checklist to be cited. Only cite a source when it performs a specific argumentative function for this paper.
2. Cite one literature item only once in the body.
3. Cite one author only once in the body and reference list.
4. Insert the citation immediately after the sentence or clause that uses that source, like `……具体论断。[3]`
5. Do not pile references at the end of a paragraph, such as `……。[1][2][3]`
6. Citation numbers must follow first-use order: `[1]`, `[2]`, `[3]`...
7. The reference list must follow the same order as first body citation.
8. Format references using GB/T 7714 numeric style as far as verified metadata allows.
9. Do not invent missing authors, titles, journals, years, issue numbers, pages, publishers, DOI, or URLs.

## Argument-First Citation Principle

A source is not a section topic. A source is not a paragraph topic. A source is material used to advance a claim.

Before citing, answer:

- What claim in this paper needs this source?
- Does the source supply a concept, a mechanism, a case, a limitation, or a scholarly position?
- If the citation were removed, would the paragraph's argument collapse?

If the answer is no, do not cite the source just because it is in the workspace.

Default behavior: select sources that genuinely support the argument. Full workspace coverage is an exception, not the default. If the user explicitly requires full coverage, still subordinate each source to a specific argumentative move; do not let the source list dictate the paper's structure.

## Corpus-Driven Citation Rules

Based on the nuwa distillation of the workspace corpus:

1. **Policy texts must be problematized.** A policy quotation is valid only when it is turned into a research question, boundary condition, or concrete contradiction. Do not use policy texts as authoritative conclusions.
2. **Every case or datum needs a verifiable detail.** Include at least one of: source institution, release date, platform name, sample size, access volume, or research design. Avoid "如……等" lists without evidence.
3. **Literature review must end with a gap.** The last move of any review paragraph must state what existing research has not solved and how this paper addresses it.
4. **Interdisciplinary concepts must be translated.** When importing concepts from outside the field, redefine them with this paper's object. Do not transport original disciplinary definitions unchanged.
5. **Citations must not parade authors.** Avoid paragraphs that consist of "A 指出… B 认为… C 区分了…" sequences. Use sources to build your claim, not to summarize the field.

## Conflict Check

Before drafting, build a citation coverage table:

```text
source_id:
file:
verified metadata:
first author:
all visible authors:
usable claim:
planned sentence/section:
GB/T 7714 draft:
status:
```

Stop and report a conflict if:

- the workspace contains two or more usable sources by the same author and the user also requires "one author only once";
- a source lacks enough metadata to create a reliable GB/T 7714 entry;
- a source is unrelated to the paper topic and citing it would be dishonest;
- the number of required workspace sources exceeds the paper's reasonable citation capacity.

Do not solve these conflicts by fake citations or irrelevant citations. Instead, report the conflict and ask whether to prioritize full-source coverage, author uniqueness, or relevance.

## Full Workspace Literature Use

When the user says the paper must use all workspace literature:

1. Identify literature sources separately from drafts, notes, scripts, images, and generated files.
2. Create a one-source-one-claim map.
3. Assign each source to exactly one sentence.
4. Do not cite the same source again later.
5. If a source can only support background rather than argument, cite it in the sentence where that background is stated.
6. If a source cannot honestly support any sentence, list it in `未使用及原因`.

## In-Text Citation Placement

Correct:

```text
生成式人工智能改变的不只是文化内容的生产速度，更改变了意义进入跨文化语境的组织方式。[1] 这一变化使国际传播从单向输出转向解释关系的再建构。
```

Incorrect:

```text
生成式人工智能改变了文化传播方式，也带来了新的风险，需要完善治理机制。[1][2][3]
```

The citation should be attached to the specific sentence whose claim depends on the source. It should not function as a general paragraph decoration.

## GB/T 7714 Numeric Reference Examples

Use verified metadata only.

Journal article:

```text
[1] 作者. 题名[J]. 刊名, 年, 卷(期): 起止页码.
```

Book:

```text
[2] 作者. 书名[M]. 出版地: 出版者, 年.
```

Dissertation:

```text
[3] 作者. 题名[D]. 学位授予单位所在地: 学位授予单位, 年.
```

Newspaper:

```text
[4] 作者. 题名[N]. 报纸名, 年-月-日(版次).
```

Online source:

```text
[5] 作者或机构. 题名[EB/OL]. (发布日期)[引用日期]. URL.
```

If metadata is incomplete, use only verified fields and mark missing fields in a note outside the formal reference list.

## Citation Audit

Before delivery:

1. Run `scripts/citation_audit.py` on the final Markdown draft when available.
2. Check that inline citations appear exactly once each.
3. Check first-use order and reference list order.
4. Check repeated authors.
5. Check paragraph-end citation piles.
6. Manually review whether each citation sentence really uses the cited source.

Script checks are necessary but not sufficient. They cannot prove that a source supports a claim.
