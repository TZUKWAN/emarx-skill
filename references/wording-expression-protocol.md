# EMARX Wording And Expression Protocol

Use this file when drafting, revising, or reviewing sentence-level expression in Chinese theoretical papers.

## Core Problem

Many weak drafts do not fail because every sentence is grammatically wrong. They fail because sentences start in the wrong place, make claims before naming objects, negate before establishing context, or use abstract nouns to hide an empty relation.

The v6.8 full-corpus language distillation adds one more failure source: prose that talks about the paper instead of making the paper's claim. Phrases such as `本文认为`, `本文的核心观点是`, `本文将`, `文章认为`, and `有研究指出` often make EMARX sound like an assistant explaining an assignment or inserting a review paragraph. The target voice is object-facing and author-invisible.

Good academic expression should make the reader know:

- what object is being discussed;
- what relation is being clarified;
- what evidence or theoretical basis supports the statement;
- what judgment the paragraph has advanced.

## Paragraph Opening

The first sentence of a paragraph should orient the reader. It may open from:

- object: name the concrete object, text, policy, case, concept, or relation;
- field position: name the academic conversation or theoretical issue;
- material: begin with a source, case, data point, or policy fact;
- transition: connect the previous paragraph to the next analytical move;
- concept boundary: clarify how a concept is used in this paper.

Avoid opening a paragraph with a naked negation.

Bad opening patterns:

- `不是...`
- `并非...`
- `不能...`
- `不应...`
- `不要...`
- `没有...`
- `无需...`
- `并不...`
- `绝非...`

These forms are sometimes valid after the object has been established. They are weak when they appear before the reader knows what is being corrected and why the correction matters.

Instead of opening with negation, first name the object or relation:

```text
Weak: 不能把生成式人工智能简单理解为传播工具。
Better: 生成式人工智能进入文化传播后，首先改变的是内容被组织和调用的方式。将其理解为普通传播工具，会遮蔽模型、平台和语料共同塑造意义的过程。
```

The second version still contains a correction, but the correction follows an object and a reason.

## Expression Failure Types

Avoid the whole family of expression failures below. They share the same root: the sentence asks the reader to accept a turn, judgment, or abstraction before the object and relation have been made clear.

### 1. Empty Framing Opening

Weak openings:

- `在……背景下`
- `随着……的发展`
- `当前`
- `近年来`
- `从……来看`
- `在……语境下`

These openings are not automatically wrong, but they often delay the real object. Use them only when the sentence quickly names the concrete relation being analyzed.

### 2. Suspended Pronoun Opening

Weak openings:

- `这种`
- `这一`
- `上述`
- `这说明`
- `这意味着`

These words require a nearby referent. Do not use them to open a new paragraph unless the previous paragraph has clearly prepared the object and the new paragraph immediately names what is being carried forward.

### 3. Premature Judgment

Weak openings:

- `关键在于...`
- `核心是...`
- `根本上...`
- `本质上...`
- `必须...`

Such openings often produce a conclusion before analysis. Use them after the paragraph has shown why the judgment is necessary.

### 4. Concept Stack

Weak sentences pile several abstract terms together:

```text
主体性、解释关系、治理秩序和价值协同构成了智能传播的结构基础。
```

This may sound academic, but it hides relations. Rewrite by explaining which term acts on which object through what mechanism.

### 5. Pseudo Transition

Transitions are common in the corpus and are not automatically bad. They become weak when they make the passage look connected while the reasoning has not moved:

- `因此` used when no inference has been made;
- `由此可见` used when the paragraph only repeats a statement;
- `与此同时` used as a loose connector;
- `值得注意的是` used when the following sentence is not actually notable;
- `进一步看` used when no further analytical step follows.

Use a transition only when it names the actual movement: concept to material, material to mechanism, mechanism to judgment, or literature limit to paper entry.

### 6. Claim-Only Paragraph

A paragraph fails when every sentence asserts and no sentence proves, distinguishes, exemplifies, or interprets. A paragraph needs an argumentative action, not just a topic.

### 7. Slogan Ending

Avoid paragraph endings that only sound positive:

- `具有重要意义`
- `提供有力支撑`
- `形成强大合力`
- `开辟新路径`
- `提升传播效能`

End with what has been clarified, not with how important the issue is.

### 8. Instructional Manual Voice

Path and governance sections often become weak when they sound like a work plan. Watch for repeated use of `应`, `应当`, `需要`, `必须`, `建议`, and similar modal verbs.

These words are not banned. They become a problem when the paragraph only tells actors what to do and no longer explains why that action follows from the paper's analysis.

Better path writing should move:

```text
diagnosed mechanism -> condition that must change -> actor and action -> why this action answers the mechanism
```

Avoid:

- consecutive sentences beginning with `应...`;
- paragraphs made of institutional tasks;
- action lists without theoretical return;
- treating the path section as an implementation manual rather than the conclusion of the argument.

## Sentence Method

Use this default movement when a paragraph feels loose:

```text
object anchor -> relation clarification -> evidence/material -> interpretive judgment
```

Do not use this movement:

```text
paper self-description -> claim announcement -> source parade -> suggestion
```

Examples of sentence functions:

- object anchor: name the thing under discussion;
- relation clarification: explain how A affects B, belongs to B, differs from B, or generates B;
- evidence/material: bring in literature, policy, case, text, data, or historical context;
- interpretive judgment: state what the relation means for the paper's argument.

Avoid paragraphs that only contain:

- claim -> claim -> claim;
- concept -> concept -> concept;
- policy phrase -> slogan -> suggestion;
- negation -> correction -> abstract conclusion.
- `本文认为` -> `有研究指出` -> `因此应当`.

## Author-Invisible Abstract And Body Voice

Abstracts should normally have no visible author subject. They should describe the research object directly through third-person compressed academic prose.

Avoid:

- `本文认为...`
- `本文的核心观点是...`
- `本文从...展开分析`
- `笔者认为...`
- `本研究旨在...`
- `文章认为...`

Better movement:

```text
research object -> problem relation -> mechanism/logic -> value or path
```

The same rule applies to body prose. If a sentence starts by explaining what the paper will do, rewrite it as a sentence about the object.

## Literature Entry Without Review Inserts

Avoid body paragraphs that introduce literature as detached review:

- `有研究指出...`
- `已有研究认为...`
- `相关研究指出...`
- `学者认为...`

When literature is needed, digest it into one of four functions:

- concept source;
- mechanism source;
- problem source;
- limitation source.

The sentence should still belong to the paper's own argument. Citation marks can follow the sentence, but the prose should not read like a literature-review paragraph pasted into the body.

## Negation Discipline

Negation is useful for concept boundary work, but it must not become the engine of prose.

Use negation only when:

- there is a real misconception to correct;
- the positive claim follows quickly;
- the sentence names the object under correction;
- the paper has evidence or reasoning for the correction.

Avoid:

- paragraph opening by negation;
- repeated `不是...而是...`;
- negation that only creates dramatic contrast;
- correcting a view that nobody in the paper has actually held.

Better movement:

```text
先说明对象的实际运行方式，再指出旧理解的不足，最后给出本文的判断。
```

## Verb Choice

Prefer verbs that show intellectual action.

Use:

- distinguishes;
- clarifies;
- explains;
- reveals;
- connects;
- limits;
- transforms;
- supports;
- weakens;
- expands.

In Chinese prose, prefer direct verbs:

- `批判...` over `对...进行批判`;
- `解释...` over `对...作出解释`;
- `限制...` over `形成对...的限制`;
- `支持...` over `为...提供支撑`.

Avoid using `推动`, `促进`, `加强`, `优化`, `提升`, `赋能`, `打造`, and `构建` unless the sentence names the object, mechanism, and condition.

## Subject And Object Clarity

Every important sentence should have a clear subject and object.

Weak signs:

- the subject is an abstract container such as `这一问题`, `这种情况`, or `这一逻辑` without a nearby referent;
- the verb is too general to show relation;
- the object is missing, so the reader cannot tell what has changed;
- the sentence ends with `重要意义`, `现实价值`, or `内在要求` without specifying the value object.

Fix by naming:

```text
actor / mechanism / object / consequence
```

## Transition

Transitions should explain why the next paragraph is necessary.

Good transitions:

- move from concept to material;
- move from material to mechanism;
- move from mechanism to governance implication;
- move from literature limit to this paper's entry point.

The corpus regularly uses `因此`, `由此可见`, `与此同时`, `进一步看`, `在此基础上`, `换言之`, `这意味着`, `然而`, `但是`, `另一方面`. These are acceptable when they name a real movement. They are weak only when they disguise a non-movement as a movement.

Avoid:

- `因此` when no inference has been made;
- `由此可见` when the paragraph only repeats a statement;
- `与此同时` as a loose connector;
- `值得注意的是` when the following sentence is not actually notable.

## Title, Heading, And Body Distinction

Formal first-level and second-level headings remain required for full papers. Body prose should not become a hidden outline.

Inside body paragraphs, sequence words such as `一方面...另一方面...`, `首先...其次...`, and `第一...第二...` are acceptable when they organize real analytical steps. Avoid them only when they replace reasoning with parallel slogans.

Also avoid:

- colon-led mini titles;
- semicolon stacks that merely list concepts;
- paragraph endings that sound like policy bullet points.
- `问题在于：`, `关键在于：`, `核心观点是：`, and similar colon-led prompt-answer structures inside prose.

## Revision Checklist

When revising, check:

```text
naked negative openings:
paragraphs with no object anchor:
paragraphs with only abstract concepts:
sentences with unclear subject:
generic verbs:
unsupported transitions:
claim-only paragraphs:
paragraphs ending in slogans:
visible author subjects:
paper meta-discourse:
review-insert formulas:
colon-led mini titles:
```

If a paragraph opens badly, do not only replace a word. Rebuild the paragraph from object, relation, material, and judgment.
