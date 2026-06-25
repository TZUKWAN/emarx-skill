# EMARX Length And Hierarchy Protocol

Use this file when planning, drafting, reviewing, or revising a full Chinese academic paper.

## Evidence Base

This protocol does not replace `distillation-evidence.md`. It adds a second empirical layer after the user's workspace expanded.

Full-corpus structure audit on 2026-06-25:

- Workspace PDF count: 452.
- Readable PDFs: 450.
- Empty file: `35.论文化记忆与文化自信_左路平.pdf`.
- Malformed PDF: `范式转型与国家文化安全的结构性危机——关于构建中国自主国家文化安全知识体系的思考.pdf`.
- Extracted pages: 3,700.
- Extracted characters: 7,783,902.
- Character count P25/P50/P75: 11,676 / 15,877 / 21,072.
- Page count P25/P50/P75: 6 / 8 / 10.
- Papers with at least 10,000 extracted characters: 379 / 450 readable PDFs.
- Papers with at least 12,000 extracted characters: 328 / 450 readable PDFs.
- Papers with at least 8 pages: 234 / 450 readable PDFs.

Heading-depth distribution from the extraction script:

```text
0 levels: 44 papers
1 level : 91 papers
2 levels: 257 papers
3 levels: 60 papers
```

Heading type counts:

```text
level1_cn        1165
level2_arabic    1205
level2_cn_paren   989
level3_cn_paren   135
level3_decimal      1
special            66
```

Important caveat: the extraction script can misread journal headers, DOI strings, page numbers, and reference entries as headings. It can also miss headings when PDF layout merges title and body text. Treat the statistics as a structural signal, not as publication-grade bibliometrics. The signal is still strong enough for EMARX: full papers need real length and second-level headings.

## Hard Length Rule

For a normal full paper, target 10,000-12,000 Chinese characters in the main text unless the user explicitly asks for another length.

Do not count these as main text:

- title;
- abstract;
- keywords;
- reference list;
- appendices;
- fact-check notes;
- delivery notes.

Failure conditions:

- Less than 8,000 main-text Chinese characters: not a full paper.
- 8,000-9,999 main-text Chinese characters: incomplete unless the user explicitly requested a shorter paper.
- 10,000-12,000 main-text Chinese characters: default target.
- More than 12,000 main-text Chinese characters: allowed only when the topic, source base, or user request requires expansion.

Recommended distribution:

```text
Title: 20-35 Chinese characters
Abstract: 300-450 Chinese characters
Keywords: 3-5 terms
Introduction / problem statement: 1,200-1,600 Chinese characters
Body: 4-5 first-level sections, each 1,600-2,200 Chinese characters
Conclusion: 800-1,200 Chinese characters
```

## Mandatory Heading Hierarchy

A normal full paper must use at least two heading levels.

Default Chinese academic hierarchy:

```text
一、一级标题
（一）二级标题
（二）二级标题

二、一级标题
（一）二级标题
（二）二级标题
```

Acceptable alternative when it fits the user's corpus or target journal:

```text
一、一级标题
1. 二级标题
2. 二级标题
```

Third-level headings are optional and should be used only when the section contains multiple mechanisms, stages, subjects, cases, or sub-arguments:

```text
一、一级标题
（一）二级标题
1. 三级标题
2. 三级标题
```

Do not create a decorative third level. A third-level heading must reduce complexity, not inflate the outline.

## Structure Rules

Each full paper should normally include:

```text
题目
摘要
关键词
引言 / 问题的提出
一、...
（一）...
（二）...
二、...
（一）...
（二）...
三、...
（一）...
（二）...
四、...
（一）...
（二）...
结语 / 结论
参考文献
```

The body should usually have 4-5 first-level sections. Use 3 only for narrow revision tasks or shorter requested papers. Use 6 only for unusually broad source bases.

Every first-level body section must have at least two second-level headings unless it is a short conclusion. No orphan first-level heading is allowed in the body.

Each second-level heading must perform one distinct function:

- concept boundary;
- historical generation;
- theoretical tension;
- mechanism explanation;
- risk diagnosis;
- subject relation;
- material/case analysis;
- path design;
- value return.

Do not repeat the first-level heading in softer words. A second-level heading must narrow the analytical action.

## Depth Rules

Before drafting, write a length and hierarchy plan:

```text
target main-text characters:
first-level sections:
second-level headings per section:
sections requiring third-level headings:
why this structure fits the topic:
which corpus pattern from distillation-evidence.md is being used:
```

During revision, each major section must pass five checks:

```text
concept boundary:
mechanism chain:
source/material support:
counter-tension or risk:
judgment landing:
```

If a section only lists phenomena, rewrite it. If it only offers solutions, add the mechanism that makes the solution necessary. If it only repeats policy vocabulary, translate the vocabulary into a theoretical relation.

## Review Failure Conditions

Mark the draft as failed if any of the following is true:

- main text is below 10,000 Chinese characters without explicit user permission;
- body sections lack second-level headings;
- a first-level section is just a long block of paragraphs;
- headings are generic labels such as "机遇、挑战、路径" without a central thesis;
- conclusion only repeats the outline;
- paragraph development is shallow, slogan-like, or unsupported by sources;
- source citations are piled at the end of paragraphs rather than attached to exact claims.

## Practical Reminder

The user's complaint that an EMARX paper had no second-level headings is valid. Treat this as a regression guard. Before delivery, always report:

```text
main-text character count:
first-level heading count:
second-level heading count:
third-level heading count if any:
sections without second-level headings:
```
