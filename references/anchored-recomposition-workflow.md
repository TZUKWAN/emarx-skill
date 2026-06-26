# EMARX Anchored Recomposition Workflow

Use this file when the user wants EMARX to write a full paper by first learning from local workspace papers.

## Core Idea

The workflow is:

```text
full-corpus deconstruction -> topic-based anchor selection -> shadow recomposition -> logic deconstruction -> detailed outline -> one-paragraph-at-a-time drafting -> paragraph review -> whole-paper revision
```

This is designed to solve the failure where EMARX writes a generic paper from abstract rules. The paper should grow out of a few concrete local models, but it must not become a copied patchwork.

## Full-Corpus Deconstruction

If `article_deconstruction_v1/summary.json` and per-paper reports are missing or stale, run:

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

Treat these reports as a reading index. When a specific claim matters, reopen the original source or extracted text.

## Topic-Based Anchor Selection

For a new user topic, select three to five anchor papers before drafting:

```bash
python scripts/select_anchor_papers.py \
  --topic "<user topic>" \
  --summary <article_deconstruction_dir>/summary.json \
  --output <anchor_report.md> \
  --top-k 5
```

The anchor set should usually include:

- one paper for theoretical starting point;
- one paper for structure or heading movement;
- one paper for mechanism explanation;
- one paper for material/case/policy context;
- one paper for path or conclusion style.

Do not select anchors only by keyword overlap. After script selection, read the reports and adjust if a paper is formally relevant but substantively weak.

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
source paper/report:
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
