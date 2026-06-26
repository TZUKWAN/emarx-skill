# EMARX Anchored Recomposition Workflow

Use this file when the user wants EMARX to write a full paper by first learning from local workspace papers.

## Core Idea

The workflow is:

```text
current workspace scan -> topic-based anchor selection from real papers -> immediate anchor-paper deconstruction -> shadow recomposition -> logic deconstruction -> detailed outline -> one-paragraph-at-a-time drafting -> paragraph review -> whole-paper revision
```

This is designed to solve the failure where EMARX writes a generic paper from abstract rules. The paper should grow out of a few concrete local models, but it must not become a copied patchwork.

## Current Workspace First

Anchor papers must be selected from the user's current workspace at the time of use. Do not start from an old deconstruction report library. A report library may help as a cache, but it cannot replace scanning, opening, and judging the real files that are currently available to the user.

Minimum current-workspace actions:

- scan the current workspace for PDF, Word, Markdown, TXT, HTML, and other readable papers;
- rank candidate papers against the user's topic;
- verify that selected anchors are real current files;
- open or extract the selected anchor papers;
- deconstruct the selected papers' abstract, introduction, body, conclusion, style, writing methods, and argument logic before drafting.

Old reports are allowed only when they match a current workspace file path and are treated as cache. If a cached report exists, still reopen the original file or extracted text for the selected anchors when the writing decision depends on the source.

## Optional Cache: Full-Corpus Deconstruction

If the current workspace has an existing structure index and extracted texts, a report cache can be built or refreshed:

```bash
python scripts/deconstruct_corpus_articles.py \
  --index <structure_index.json> \
  --output-dir <article_deconstruction_dir>/reports \
  --summary <article_deconstruction_dir>/summary.json
```

Each report should record:

- abstract logic, style, and expression methods;
- opening/introduction logic;
- body section movement;
- conclusion/closing method;
- whole-paper prose style;
- argumentative logic;
- usable patterns;
- risks to avoid.

Treat these reports as a reading index and acceleration layer only. They are not the source of anchoring.

## Topic-Based Anchor Selection

For a new user topic, select three to five anchor papers from the current workspace before drafting:

```bash
python scripts/select_anchor_papers.py \
  --topic "<user topic>" \
  --workspace-root <current_workspace> \
  --summary <optional_article_deconstruction_cache.json> \
  --output <anchor_report.md> \
  --top-k 5
```

The anchor set should usually include:

- one paper for theoretical starting point;
- one paper for structure or heading movement;
- one paper for mechanism explanation;
- one paper for material/case/policy context;
- one paper for path or conclusion style.

Do not select anchors only by keyword overlap. After script selection, open the selected current workspace files, read the abstract/introduction/body/conclusion or their extracted text, and adjust if a paper is formally relevant but substantively weak.

## Immediate Anchor-Paper Deconstruction

After selecting the three to five anchors, deconstruct those anchors for the current topic. Do not skip this step just because a report cache exists.

For each selected anchor paper, produce an internal note:

```text
file:
why selected:
abstract logic:
abstract style and writing methods:
introduction logic:
body section movement:
conclusion movement:
heading structure:
argument logic:
prose style:
expression methods:
usable structure moves:
usable paragraph moves:
what must not be copied:
what must be transformed for the user's topic:
```

Only after this immediate deconstruction can the workflow move to shadow recomposition.

## Shadow Recomposition

The user may ask to "first recombine three to five papers with little change." This is allowed only as an internal shadow draft.

Rules:

- The shadow recomposition is not a deliverable paper.
- Keep source marks for every borrowed paragraph or logic move.
- Use the shadow draft to expose the target paper's possible skeleton.
- Do not hide borrowed wording.
- Do not treat light editing as original writing.
- The final paper must be rewritten paragraph by paragraph with its own thesis, source integration, citations, and fact checks.

The shadow recomposition should be a paragraph-function map, not a polished article:

```text
paragraph_id:
source paper:
borrowed function:
borrowed material:
why it fits the user topic:
what must change:
target paragraph claim:
```

## Logic Deconstruction Of The Shadow Draft

After shadow recomposition, deconstruct it before writing:

```text
central thesis:
real problem:
first-level section movement:
second-level section movement:
paragraph sequence:
which parts are inherited:
which parts must be transformed:
where original argument is still missing:
where material support is thin:
where citation/fact risks exist:
```

The output of this step is not prose. It is the paper's logic skeleton.

## Detailed Outline

The outline must be detailed enough to control paragraph-by-paragraph writing.

For every paragraph, specify:

```text
paragraph number:
section:
paragraph function:
target claim:
source anchor:
required material:
concepts used:
transition from previous paragraph:
transition to next paragraph:
style reference:
fact/citation risk:
completion standard:
```

Do not begin drafting until every planned paragraph has a function and target claim.

## One-Paragraph-At-A-Time Drafting

Write one paragraph at a time.

For each paragraph:

1. Read the paragraph plan.
2. Read the relevant anchor report or source excerpt.
3. Draft only that paragraph.
4. Check subject, claim, mechanism, evidence, citation, transition, rhythm, and style.
5. Revise that paragraph before moving on.

Do not draft several paragraphs at once and then rely on later polishing. That recreates the generic EMARX failure.

Each paragraph must pass:

```text
has a clear claim:
fits the detailed outline:
uses source/material correctly:
does not copy anchor wording:
connects to previous paragraph:
prepares the next paragraph:
contains no diagnostic workflow language:
has a judgment landing:
```

## Whole-Paper Revision

After all paragraphs are drafted:

- check whether the central thesis is still stable;
- check whether headings form an argument skeleton;
- remove any shadow-draft residue;
- run citation audit and fact check;
- run bad-draft audit;
- revise weak paragraphs substantively;
- generate Word only after the paper passes review.

## Failure Conditions

Reject the draft if:

- anchor papers are selected but not actually read;
- the shadow recomposition becomes the final paper;
- paragraphs preserve borrowed wording without citation and transformation;
- the outline is only a heading list, not a paragraph-level logic plan;
- the draft writes multiple paragraphs at once and loses local control;
- the final paper sounds like a manual, source parade, or stitched review.
