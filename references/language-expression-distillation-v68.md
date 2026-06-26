# EMARX v6.8 Language Expression Distillation

Use this file when drafting, revising, or reviewing abstract and body prose.

## Evidence Base

Full workspace language-expression distillation on 2026-06-27:

- 450 extracted workspace articles analyzed.
- 114 explicit abstracts detected.
- 336 first-paragraph abstract candidates detected, but these are weaker evidence because PDF extraction often merges title, author, metadata, and opening text.

Key measured signals:

- Explicit abstracts with visible author subjects such as `本文`, `笔者`, `本研究`, or `文章认为`: 12 / 114, or 10.53%.
- Explicit abstracts with subjectless or prepositional compressed openings: 62 / 114, or 54.39%.
- Articles containing paper meta-discourse such as `本文的核心观点`, `本文认为`, `本文将`, or `文章认为`: 70 / 450, or 15.56%.
- Articles containing review-insert patterns such as `有研究指出`, `已有研究认为`, or `相关研究指出`: 65 / 450, or 14.44%.

Interpretation:

- Some corpus papers do use author-visible phrases, but they are not the target style for EMARX because the user explicitly rejects self-narrating prose.
- The target abstract voice is impersonal, object-facing, compressed, and third-person reporting-like.
- Literature may enter the paper, but not as a detached mini-review sentence.

## Abstract Voice

The abstract should not narrate what the paper, author, or researcher is doing.

Do not write:

- `本文认为...`
- `本文的核心观点是...`
- `本文从...展开分析`
- `笔者认为...`
- `本研究旨在...`
- `文章认为...`
- `文章指出...`

Write the object, relation, mechanism, and value directly:

```text
生成式人工智能改变中华文化国际传播的内容组织、语义转译和平台分发方式，使文化意义进入国际语境的过程呈现出更强的生成性、协商性和不确定性。
```

The abstract can use compressed, subjectless, or prepositional starts when they serve academic compression:

```text
基于生成式人工智能介入文化生产与跨语境传播的现实进程，中华文化国际传播的关键问题不再停留于内容输出规模，而集中于语义解释、主体呈现和接受反馈之间的关系调整。
```

This style differs from chat prose. It does not say `本文要讨论什么`; it directly presents the academic object.

## Body Prose

Do not use paper self-description as a substitute for argument.

Avoid:

- `本文的核心观点是...`
- `本文认为...`
- `本文将从以下几个方面...`
- `文章首先分析...`
- `本文通过...得出...`

Replacement method:

```text
self-description -> object/relation claim
```

Examples:

```text
Bad: 本文认为，生成式人工智能为中华文化国际传播带来了机遇和挑战。
Better: 生成式人工智能使中华文化国际传播同时面对表达扩展和意义失控两种后果。
```

```text
Bad: 本文的核心观点是，中华文化国际传播需要重视语料建设。
Better: 语料建设决定了模型能够以何种方式识别、调用和解释中华文化资源。
```

## Literature Entry

Do not insert literature with detached review formulas:

- `有研究指出...`
- `已有研究认为...`
- `相关研究指出...`
- `学者认为...`

These forms make the paragraph sound like a literature review pasted into an argument.

Instead, digest the source into one of four functions:

```text
concept source:
mechanism source:
problem source:
limitation source:
```

Then place the citation at the exact sentence where the source works. The sentence should still belong to the paper's own argument.

## Punctuation

Use commas and periods as the normal base.

Use colons only when they perform a real academic function:

- title or subtitle;
- quoted source title;
- necessary concept explanation;
- table/list outside body prose.

Avoid colon-led mini titles inside paragraphs:

```text
Bad: 关键问题在于：文化主体性容易被模型逻辑遮蔽。
Better: 文化主体性容易被模型逻辑遮蔽，这是智能传播中最需要警惕的前端问题。
```

Avoid decorative quotation marks and dash-heavy turns unless required by source titles or cited terms.

## Generation Rules

For EMARX drafting:

1. Abstracts must be author-invisible by default.
2. Never start the abstract with `本文`, `笔者`, `本研究`, or `文章`.
3. Do not write `本文认为`, `本文的核心观点`, `本文将`, or `文章认为` anywhere in final paper prose.
4. Do not use `有研究指出`, `已有研究认为`, or `相关研究指出` as a body paragraph opening.
5. If literature is needed, digest it into the paper's mechanism, concept, problem, or limitation.
6. Replace colon-led explanation with ordinary sentence movement unless a colon is structurally necessary.
7. Every paragraph should sound like a paper making an argument, not like an assistant explaining what the paper will do.
