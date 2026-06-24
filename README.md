# EMARX

EMARX is a Codex skill for writing and refining Chinese 学理思辨论文 with mature theoretical style, strong structure, and explicit argumentative progression.

It is optimized for topics in Marxist theory, ideological-political education, cultural memory, subjectivity, people-centered modernization, AI philosophy, technology critique, and adjacent humanities or social-science fields.

## What It Does

EMARX helps with:

- 论文选题 and problem consciousness
- title generation
- abstract writing
- introduction design
- outline architecture
- section logic
- body paragraph drafting
- conclusion design
- theoretical argumentation
- mature academic style refinement
- final self-audit

## Core Features

- Full task routing for 选题、标题、摘要、引言、提纲、正文、润色、审稿
- 16 title templates with use cases and failure conditions
- abstract generator for 4-sentence, 5-sentence, long abstract, and no-abstract formats
- introduction generator for policy-background, theoretical-gap, real-symptom, historical-event, and technology-risk entries
- 16 structure archetypes for 学理思辨论文
- 12 paragraph templates for concept analysis, contradiction analysis, policy translation, technology critique, and value reasoning
- style controller for concept consistency, policy-academic coupling, tension visibility, connector density, and anti-hollowing revision
- hard rules against fabricated citations, data, page numbers, policy quotes, and source-backed claims

## Installation

Install from this repository with the Codex skill installer:

```bash
python ~/.codex/skills/.system/skill-installer/scripts/install-skill-from-github.py --repo TZUKWAN/emarx-skill --path . --name emarx
```

After installation, restart Codex so the skill can be discovered.

You can then ask Codex to use `$emarx`, for example:

```text
Use $emarx to draft a Chinese theoretical essay topic, title, abstract, and three-level outline on generative AI and human subjectivity.
```

## Repository Layout

```text
.
├── SKILL.md
├── README.md
├── agents/
│   └── openai.yaml
└── references/
    └── distillation-evidence.md
```

## Provenance

This v2 skill was rebuilt on 2026-06-24 from full-text analysis of local PDF papers:

- 359 PDF files found
- 358 readable PDFs produced full-text extraction
- 1 zero-byte PDF was excluded
- extracted text covered 2,889 / 2,896 pages
- extracted text size was 5,161,082 characters
- Qwen generated 358 per-paper full-text structure profiles
- Qwen generated 15 group syntheses

The bundled `references/distillation-evidence.md` records the derived patterns and source-anchor style evidence used to update EMARX.

## Important Limits

EMARX generates academic-style writing patterns. It does not verify real-world facts by itself.

Do not use EMARX to fabricate:

- citations
- author names
- journal metadata
- page numbers
- policy quotations
- statistics
- source-backed claims

When current policies, recent scholarship, laws, institutional facts, or real citations matter, verify them with reliable sources before asserting them.

Qwen-generated proportions or aggregate judgments in the evidence material should be treated as auxiliary observations unless independently recomputed.
