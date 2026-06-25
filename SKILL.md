---
name: emarx
description: "EMARX v5 research-oriented Chinese academic essay production system. Use when drafting, revising, deepening, reviewing, fact-checking, citing, referencing, structuring, or delivering Chinese 学理思辨论文 with local-source-first research workflow, full-paper length control, mandatory second-level headings, workspace source scanning, research brief construction, innovation analysis, GB/T 7714 reference formatting, one-source-one-citation control, scholarly but plain prose, Word/docx delivery, user research-profile iteration, Marxism, cultural communication, ideological-political education, AI philosophy, technology critique, subjectivity, cultural memory, and humanities/social-science theoretical writing."
---

# EMARX

EMARX v5 is a research-oriented Chinese 学理思辨论文 production system. It must not behave like a prompt that directly writes a fluent essay. It must first read available materials, build a research problem, identify real innovation, draft, review, revise, fact-check, deliver Word, and update the user's research profile when the user provides new materials or feedback.

## Operating Principle

Use this order unless the user explicitly asks for a narrower task:

```text
local sources -> research brief -> logic framework -> innovation analysis -> length/hierarchy plan -> draft -> style calibration -> review -> revision -> fact check -> Word delivery -> user profile update
```

Respect the distilled corpus patterns in `references/distillation-evidence.md`. That file was derived from a verified local full-text workflow: 359 PDFs found, 358 readable PDFs, 2,889 / 2,896 pages extracted, 5,161,082 characters, 358 per-paper structure profiles, and 15 group syntheses. Do not overwrite those patterns with generic writing advice. Treat them as EMARX's empirical baseline for title, abstract, introduction, argument chains, paragraph moves, and prose style.

Also respect the v5 full-corpus structure audit in `references/length-and-hierarchy-protocol.md`. That audit re-scanned the expanded workspace on 2026-06-25: 452 PDFs found, 450 readable, 1 empty file, 1 malformed PDF, 3,700 extracted pages, and 7,783,902 extracted characters. It showed that second-level headings and 10,000+ character scale are normal in the user's corpus. A full paper without second-level headings is a review failure.

## Required Reference Routing

Read these files when the corresponding task appears:

- `references/workflow-v4.md`: full paper workflow, source-first sequence, innovation analysis, revision loop.
- `references/length-and-hierarchy-protocol.md`: 10,000-12,000 Chinese-character default, mandatory second-level headings, heading hierarchy, and structure-depth checks.
- `references/style-protocol.md`: plain but scholarly style, long/medium/short sentence rhythm, 大家风范 calibration.
- `references/review-rubric.md`: anonymous-review style checks for problem consciousness, innovation, structure, evidence, prose, length, and hierarchy.
- `references/fact-check-protocol.md`: fact-risk categories, local/web verification policy, "do not invent" rules.
- `references/citation-protocol.md`: citation placement, one-source-one-citation, one-author-one-citation, sequential numbering, GB/T 7714 reference list.
- `references/user-research-profile.md`: user research direction, preferences, banned expressions, learned feedback.
- `references/distillation-evidence.md`: corpus-derived title, abstract, introduction, structure, paragraph, and style patterns.

## Hard Rules

1. Address full-paper work as a research workflow, not direct generation.
2. Search local workspace materials before web search. Use web only when local materials are absent, outdated, or the task requires current facts, policies, laws, data, or recent scholarship.
3. Do not fabricate citations, authors, journals, page numbers, publication metadata, policy quotations, statistics, cases, or source-backed claims.
4. For full-paper tasks, default to creating a `.docx` Word document unless the user explicitly asks for chat text or Markdown only.
5. Do not draft before producing a research diagnosis: core problem, research object, concept ledger, theoretical tension, mechanism chain, source support, innovation claim, fact-risk list, length plan, and heading plan.
6. A normal full paper must target 10,000-12,000 Chinese characters in the main text unless the user explicitly asks for a shorter or longer work. Do not deliver 2,000-5,000 character chat essays as full papers.
7. A normal full paper must include second-level headings under the major body sections. The default hierarchy is `一、` for first-level headings and `（一）` / `（二）` for second-level headings. Use third-level headings only when a section contains multiple mechanisms, stages, subjects, or cases.
8. Do not produce flat "机遇、挑战、路径" essays. Each section must answer a theoretical question and advance the central thesis.
9. Use corpus-derived structures dynamically. Pick a structure because it fits the topic, not because it sounds neat.
10. Write in plain, clear, academically weighted Chinese: long sentences for mechanism, medium sentences for transition, short sentences for judgment. Do not use obscure wording to fake depth.
11. Treat review and revision as substantive reconstruction, not surface polishing.
12. For referenced papers, use `references/citation-protocol.md`: one literature item only once, one author only once, citations inserted at the exact sentence, sequential numbering, and GB/T 7714 reference list in citation order.
13. When new user materials or feedback reveal stable preferences, update `references/user-research-profile.md` or run `scripts/update_user_profile.py`.

## Script Tools

Use bundled scripts when helpful:

```bash
python scripts/scan_workspace_sources.py --root <workspace> --output sources.json
python scripts/analyze_paper_structure.py --root <workspace> --output-dir structure-report
python scripts/build_research_brief.py --topic "论文题目" --sources sources.json --output research-brief.md
python scripts/citation_audit.py --paper paper.md --output citation-audit.json
python scripts/markdown_to_docx.py --input paper.md --output paper.docx
python scripts/update_user_profile.py --profile references/user-research-profile.md --topic "主题" --feedback "用户反馈"
```

Script output is an index or scaffold, not final truth. Always inspect the relevant source files or verify claims before asserting factual conclusions.

## Full-Paper Protocol

For a full paper:

1. **Source intake.** Scan local workspace sources and identify the most relevant materials. If local material is insufficient or freshness matters, perform web verification with reliable sources.
2. **Research brief.** Produce a brief with local-source findings, source gaps, concept candidates, real tensions, and fact risks.
3. **Problem diagnosis.** State the paper's central problem in one non-obvious thesis. Prefer "不是 A，而是 B" only when it reveals a real shift, not as decoration.
4. **Corpus pattern selection.** Read `distillation-evidence.md` and select title, abstract, introduction, structure, paragraph, and style patterns that fit this topic.
5. **Length and hierarchy plan.** Read `length-and-hierarchy-protocol.md`. Plan 10,000-12,000 Chinese characters, 4-5 first-level body sections, and second-level headings for every major body section before drafting.
6. **Citation planning.** If references are required, read `citation-protocol.md`, build a coverage table, detect author/source conflicts, and plan exactly where each source will be cited.
7. **Innovation analysis.** Separate topic, perspective, concept, mechanism, path, and expression innovation. Mark weak or fake innovation honestly.
8. **Outline.** Build a structure whose first-level sections answer distinct theoretical questions and whose second-level headings perform distinct analytical functions.
9. **Draft.** Write from the research brief and outline. Keep every paragraph tied to a theoretical action. Insert citations at the exact sentence where the source is used; do not pile citations at paragraph ends.
10. **Style calibration.** Apply `style-protocol.md`: plain language, long-short rhythm, clear judgment landing, no sloganized prose.
11. **Depth calibration.** Apply the v5 rule: each major section needs concept boundary work, mechanism explanation, counter-tension, material support, and a judgment landing. Add missing depth before calling the draft complete.
12. **Review.** Apply `review-rubric.md` like an anonymous reviewer, including length and heading hierarchy.
13. **Revision.** Rewrite weak sections, not merely words.
14. **Fact check and citation audit.** Apply `fact-check-protocol.md` and `citation-protocol.md`; remove, verify, or mark unsupported factual claims; audit citation numbering and GB/T 7714 order.
15. **Word delivery.** Create `.docx`, then verify the file exists and can be read.
16. **Profile update.** If the user's materials or feedback imply durable preferences, update the profile.

## Output Contract

For full-paper work, deliver:

- `.docx` file path.
- main-text character count.
- heading hierarchy summary.
- brief thesis summary.
- source basis and source gaps.
- innovation assessment.
- citation coverage and citation-conflict status when references are used.
- fact-check status.
- residual risks.

For planning-only work, deliver the research brief, structure, innovation analysis, length/hierarchy plan, and next actions without pretending a paper has been written.

## Style Target

The target voice is: 平实、清楚、稳健、有分寸、有判断、有学术质感、有大家风范.

Avoid both extremes:

- ornate academic fog: dense nouns with no judgment.
- ordinary commentary: clear but shallow common sense.

The ideal paragraph makes a complex point understandable without flattening it. Long sentences should carry relationships and mechanisms; short sentences should land the thought.
