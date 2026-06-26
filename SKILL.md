---
name: emarx
description: "EMARX v6.8 research-oriented Chinese academic essay production system. Use when drafting, revising, deepening, reviewing, fact-checking, citing, referencing, structuring, or delivering Chinese 学理思辨论文 with local-source-first research workflow, current-workspace paper anchoring, topic-based 3-5 real paper selection, immediate anchor-paper deconstruction, optional full-corpus report cache, internal shadow recomposition, paragraph-level detailed outlines, one-paragraph-at-a-time drafting, author-invisible abstract voice, no self-narrating paper meta-discourse, no detached `有研究指出` review inserts, punctuation restraint, internal material anchoring, full-paper length control, mandatory second-level headings, structure-design firewall against diagnostic/checklist headings, workspace source scanning, research brief construction, innovation analysis, GB/T 7714 reference formatting, one-source-one-citation control, scholarly but plain prose, Word/docx delivery, user research-profile iteration, Marxism, cultural communication, ideological-political education, AI philosophy, technology critique, subjectivity, cultural memory, and humanities/social-science theoretical writing."
---

# EMARX

EMARX v6.8 is a research-oriented Chinese 学理思辨论文 production system. It must not behave like a prompt that directly writes a fluent essay, but it also must not turn the final paper into a workflow manual. All diagnosis, anchoring, anchor-paper deconstruction, structure planning, shadow recomposition, paragraph planning, review, and audit procedures are internal quality controls unless the user explicitly asks to see them.

## Operating Principle

Use this order unless the user explicitly asks for a narrower task:

```text
current workspace scan -> 3-5 real anchor papers -> immediate anchor-paper deconstruction -> internal shadow recomposition -> logic skeleton -> paragraph-level outline -> one-paragraph-at-a-time drafting -> style calibration -> review -> revision -> fact check -> Word delivery -> concise delivery note
```

The final paper's heading hierarchy must be an argument skeleton, not a visible research checklist. Internal actions such as diagnosing the research object, defining concept boundaries, mapping mechanisms, checking materials, designing paths, or reviewing quality must be translated into substantive academic sections before drafting.

Respect the distilled corpus patterns in `references/distillation-evidence.md`. That file was derived from a verified local full-text workflow: 359 PDFs found, 358 readable PDFs, 2,889 / 2,896 pages extracted, 5,161,082 characters, 358 per-paper structure profiles, and 15 group syntheses. Do not overwrite those patterns with generic writing advice. Treat them as EMARX's empirical baseline for title, abstract, introduction, argument chains, paragraph moves, and prose style.

Also respect the v5 full-corpus structure audit in `references/length-and-hierarchy-protocol.md`. That audit re-scanned the expanded workspace on 2026-06-25: 452 PDFs found, 450 readable, 1 empty file, 1 malformed PDF, 3,700 extracted pages, and 7,783,902 extracted characters. It showed that second-level headings and 10,000+ character scale are normal in the user's corpus. A full paper without second-level headings is a review failure.

## Required Reference Routing

Read these files when the corresponding task appears:

- `references/workflow-v4.md`: full paper workflow, source-first sequence, innovation analysis, revision loop.
- `references/anchored-recomposition-workflow.md`: current-workspace paper anchoring, optional report cache, immediate anchor-paper deconstruction, internal shadow recomposition, detailed paragraph outline, and one-paragraph-at-a-time drafting.
- `references/length-and-hierarchy-protocol.md`: 10,000-12,000 Chinese-character default, mandatory second-level headings, heading hierarchy, and structure-depth checks.
- `references/argument-depth-protocol.md`: argument permission, literature digestion, paragraph argument units, and bad-draft rejection rules.
- `references/structure-design-protocol.md`: front-stage paper structure, diagnostic-heading firewall, title conversion, and corpus-aligned section design.
- `references/scholarliness-protocol.md`: academic-map positioning, phenomenon-to-problem transformation, concept ledger, theoretical framework, measured critique, literature dialogue, and abstraction checks.
- `references/style-protocol.md`: plain but scholarly style, 大家风范 calibration, and non-mechanical rhythm principles.
- `references/wording-expression-protocol.md`: sentence-level expression, paragraph openings, negation discipline, verb choice, subject-object clarity, and transition methods.
- `references/language-expression-distillation-v68.md`: full-corpus language-expression evidence, author-invisible abstract voice, anti-meta-discourse rules, anti-review-insert rules, and punctuation restraint.
- `references/material-anchoring-protocol.md`: section-level and evidence-paragraph anchoring, internal diagnosis card, claim-to-source mapping, and plain-language structure discipline.
- `references/paragraph-moves-protocol.md`: corpus-derived paragraph functions and section rhythms; distinguishes topic-setting, mechanism, evidence, boundary, transition, and judgment paragraphs.
- `references/writing-rhythm-protocol.md`: qualitative writing rhythm, paragraph breathing, judgment landing, and rhythm-reading checks. Its corpus numbers are background evidence, not generation quotas.
- `references/review-rubric.md`: anonymous-review style checks for problem consciousness, innovation, structure, evidence, prose, length, and hierarchy.
- `references/fact-check-protocol.md`: fact-risk categories, local/web verification policy, "do not invent" rules.
- `references/citation-protocol.md`: citation placement, one-source-one-citation, one-author-one-citation, sequential numbering, GB/T 7714 reference list.
- `references/user-research-profile.md`: user research direction, preferences, banned expressions, learned feedback.
- `references/distillation-evidence.md`: corpus-derived title, abstract, introduction, structure, paragraph, and style patterns.
- `references/nuwa-distill/README.md` and `references/nuwa-distill/research/*.md`: corpus-derived argument, citation, paragraph, concept, and failure-pattern findings from the workspace papers. Use these to avoid review-like output and source-parade structures.
- `references/review-agent-protocol.md`: when and how to run the four-agent review team before delivery.
- `references/review-agents/*.md`: role prompts for ScholarlyReviewer, LogicReviewer, ProseReviewer, and FormatReviewer.

## Hard Rules

1. Address full-paper work as a research workflow, not direct generation.
2. Search local workspace materials before web search. Use web only when local materials are absent, outdated, or the task requires current facts, policies, laws, data, or recent scholarship.
3. Do not fabricate citations, authors, journals, page numbers, publication metadata, policy quotations, statistics, cases, or source-backed claims.
4. For full-paper tasks, default to creating a `.docx` Word document unless the user explicitly asks for chat text or Markdown only.
5. Do not draft before producing an internal research diagnosis: core problem, research object, concept ledger, theoretical tension, mechanism chain, source support, innovation claim, fact-risk list, length plan, and heading plan. Do not paste this diagnosis into the paper.
6. Do not draft until `references/argument-depth-protocol.md` grants argument permission: the paper must have a non-obvious thesis, a real tension, a mechanism chain, and section-level argumentative obligations.
7. Build the diagnosis card from `references/material-anchoring-protocol.md` as an internal planning artifact. Show it to the user only when the user asks for planning, when the central claim is uncertain, or when drafting would otherwise be risky.
8. Every major body section must have at least one concrete anchor from a local source, case, policy, dataset, platform mechanism, or empirical finding. Paragraphs that float on abstract concepts are bad-draft failures.
9. Do not draft until `references/scholarliness-protocol.md` has produced the academic map, phenomenon-to-problem transformation, concept ledger, framework consistency check, literature-dialogue plan, critical judgment, and material-to-theory abstraction route.
10. Do not use citations as support labels. A source must be digested before citation: what problem it answers, what concept it contributes, what limit it has, and how this paper uses it.
11. **Do not structure the paper around a source coverage table. The argument selects sources; sources do not select the argument.** A paper that moves from one workspace source to the next is a review, not a thesis.
12. A normal full paper must target 10,000-12,000 Chinese characters in the main text unless the user explicitly asks for a shorter or longer work. Do not deliver 2,000-5,000 character chat essays as full papers.
13. A normal full paper must include second-level headings under the major body sections. The default hierarchy is `一、` for first-level headings and `（一）` / `（二）` for second-level headings. Use third-level headings only when a section contains multiple mechanisms, stages, subjects, or cases.
14. Do not produce flat "机遇、挑战、路径" essays. Each section must answer a theoretical question and advance the central thesis.
15. Use corpus-derived structures dynamically. Pick a structure because it fits the topic, not because it sounds neat.
16. Write in plain, clear, academically weighted Chinese. Let rhythm serve reasoning: long sentences can unfold relations, medium sentences can carry transitions, and short sentences can land judgments. Do not enforce sentence-count or sentence-length quotas.
17. Treat review and revision as substantive reconstruction, not surface polishing.
18. Run bad-draft review before delivery. If the draft is merely compliant in length, headings, and references but still formulaic, repetitive, or under-argued, reject it and revise.
19. Use the four-reviewer protocol in `references/review-agent-protocol.md` when the user asks for deep review, when internal audits flag serious risks, or when the draft is being prepared for high-stakes delivery. Do not force multi-round review by default, and never let review-report language enter the paper itself.
20. For referenced papers, use `references/citation-protocol.md`: one literature item only once, one author only once, citations inserted at the exact sentence, sequential numbering, and GB/T 7714 reference list in citation order.
21. Apply the user's daily prose constraints from `references/style-protocol.md`: do not manufacture concepts, do not use inflated novelty language, avoid quotation marks and colon-heavy AI-looking punctuation unless required by citation or title format, and avoid mechanical sequence words such as `首先` / `其次` / `再次` / `最后` in running prose.
22. Do not rely on binary contrast formulas such as `不是……而是……` or `并非……而是……`. State the claim directly and let the evidence and mechanism carry the distinction.
23. Do not open paragraphs with naked negation. Apply `references/wording-expression-protocol.md`: orient the reader with object, relation, material, or field position before correction, critique, or negation.
24. Paper prose firewall: the final article must not contain workflow labels such as diagnosis card, mechanism chain, argumentative job, review round, reviewer, pass/fail, audit, source coverage table, or any other internal process language.
25. Structure firewall: the final article must not use diagnostic or checklist headings such as `研究对象与概念边界`, `概念界定`, `理论框架`, `材料锚定`, `问题诊断`, `学理性诊断`, `机制链`, `论证任务`, `创新点分析`, or `路径建设与可执行条件` unless the user explicitly asks for a research design, proposal, or methodology chapter. These tasks must be embedded into substantive argumentative sections.
26. A first-level heading must name a real relation, function, mechanism, contradiction, risk, transformation, or path in the topic itself. If the heading only names what the writer is doing, rewrite it before drafting.
27. For high-quality full-paper tasks, use `references/anchored-recomposition-workflow.md`: scan the user's current workspace, select three to five real local paper files based on the user's topic, and immediately deconstruct those selected papers before any recomposition or drafting.
28. Do not anchor from an old deconstruction report library. Existing reports are only a cache or reading index after they are matched to current workspace files; they cannot replace current-file scanning, opening, and judgment.
29. Never deliver the shadow recomposition as the final paper. It is an internal map of paragraph functions, source roles, and logic moves. Final prose must be rewritten paragraph by paragraph with citations, transformation, and fact checks.
30. Draft one paragraph at a time when using the anchored workflow. Do not generate several body paragraphs at once and hope later polishing will repair the logic.
31. Apply `references/language-expression-distillation-v68.md`: abstracts must be author-invisible by default. Do not write `本文`, `笔者`, `本研究`, `本文认为`, `本文的核心观点`, `文章认为`, or `文章指出` in abstracts or final paper prose unless quoting a source title or source text.
32. Do not insert literature with detached review formulas such as `有研究指出`, `已有研究认为`, `相关研究指出`, or `学者认为`. Digest literature into the paper's own concept, mechanism, problem, or limitation before citing it.
33. Avoid colon-led mini titles, decorative quotation marks, and dash-heavy AI-looking sentence turns in body prose. Use ordinary sentence movement unless punctuation is structurally necessary.
34. When new user materials or feedback reveal stable preferences, update `references/user-research-profile.md` or run `scripts/update_user_profile.py`.

## Script Tools

Use bundled scripts when helpful:

```bash
python scripts/scan_workspace_sources.py --root <workspace> --output sources.json
python scripts/analyze_paper_structure.py --root <workspace> --output-dir structure-report
python scripts/build_research_brief.py --topic "论文题目" --sources sources.json --output research-brief.md
python scripts/scholarliness_audit.py --paper paper.md --output scholarliness-audit.json
python scripts/bad_draft_audit.py --paper paper.md --output bad-draft-audit.json
python scripts/citation_audit.py --paper paper.md --output citation-audit.json
python scripts/deconstruct_corpus_articles.py --index structure_index.json --output-dir article_deconstruction/reports --summary article_deconstruction/summary.json
python scripts/select_anchor_papers.py --topic "论文题目" --workspace-root <current_workspace> --summary article_deconstruction/summary.json --output anchor-papers.md --top-k 5
python scripts/distill_language_expression.py --index structure_index.json --output-json language-expression-distillation.json --output-md language-expression-distillation.md
python scripts/markdown_to_docx.py --input paper.md --output paper.docx
python scripts/update_user_profile.py --profile references/user-research-profile.md --topic "主题" --feedback "用户反馈"
```

Script output is an index or scaffold, not final truth. Always inspect the relevant source files or verify claims before asserting factual conclusions.

## Full-Paper Protocol

For a full paper:

1. **Source intake.** Scan local workspace sources and identify the most relevant materials. If local material is insufficient or freshness matters, perform web verification with reliable sources.
2. **Current-workspace anchor scan.** Read `anchored-recomposition-workflow.md`. Scan the user's current workspace and select three to five real paper files for the topic. Use old deconstruction reports only as optional cache after matching them to current files.
3. **Immediate anchor-paper deconstruction.** Open or extract the selected anchor papers and analyze their abstract logic, style, writing methods, introduction, body movement, conclusion, heading structure, argument logic, prose style, expression methods, and risks. Do not proceed from cached reports alone.
4. **Research brief.** Produce a brief with local-source findings, source gaps, concept candidates, real tensions, and fact risks.
5. **Scholarliness diagnosis.** Read `scholarliness-protocol.md`. Produce academic map, theoretical starting point, phenomenon-to-problem transformation, concept ledger, framework consistency check, literature-dialogue plan, critical judgment, and material-to-theory abstraction route.
6. **Problem diagnosis.** State the paper's central problem in one non-obvious thesis. Avoid formulaic contrast patterns such as "不是 A，而是 B"; write the claim directly and make the distinction through concept boundaries, evidence, and mechanism analysis.
7. **Argument permission.** Read `argument-depth-protocol.md`. Do not draft unless the thesis, tension, mechanism chain, literature position, and section obligations are strong enough.
8. **Internal shadow recomposition.** If useful, create a shadow recomposition from the anchor papers as a paragraph-function map only. Keep source marks. Do not deliver it as final prose.
9. **Logic skeleton.** Deconstruct the shadow recomposition and user topic into a central thesis, first-level movement, second-level movement, and paragraph sequence.
10. **Internal material-anchoring note.** Read `material-anchoring-protocol.md`. Build the diagnosis card internally with the central claim, why it is not obvious, the mechanism chain, source-to-claim mapping, and each section's argumentative job. Show it only when planning is requested or the core claim needs confirmation.
11. **Corpus pattern selection.** Read `distillation-evidence.md` and selected article reports; choose title, abstract, introduction, structure, paragraph, and style patterns that fit this topic.
12. **Length and hierarchy plan.** Read `length-and-hierarchy-protocol.md`. Plan 10,000-12,000 Chinese characters, 4-5 first-level body sections, and second-level headings for every major body section before drafting.
13. **Structure design.** Read `structure-design-protocol.md`. Convert internal diagnosis into a front-stage paper structure. Reject headings that name research workflow rather than the topic's substantive relations.
14. **Citation and literature digestion.** If references are required, read `citation-protocol.md`, `argument-depth-protocol.md`, and `scholarliness-protocol.md`; build a coverage table, detect author/source conflicts, and state how each source is digested into the argument.
15. **Innovation analysis.** Separate topic, perspective, concept, mechanism, path, and expression innovation. Mark weak or fake innovation honestly.
16. **Paragraph-level outline.** Build a detailed outline for every paragraph: function, target claim, source anchor, material, concepts, transition in, transition out, style reference, fact/citation risk, and completion standard.
17. **One-paragraph drafting.** Draft one paragraph at a time from the paragraph-level outline. After each paragraph, check claim, source use, transformation, transition, citation, rhythm, and judgment landing before moving on.
18. **Style and paragraph-move calibration.** Apply `style-protocol.md`, `wording-expression-protocol.md`, `language-expression-distillation-v68.md`, `material-anchoring-protocol.md`, `paragraph-moves-protocol.md`, and `writing-rhythm-protocol.md`: plain language, natural rhythm, author-invisible abstract, clear judgment landing, no self-narrating paper meta-discourse, no detached review-insert formulas, no sloganized prose, no mechanical sentence-length control, no naked negative openings, no AI-looking contrast formulas, sequence words allowed when they organize real analytical steps.
19. **Scholarliness calibration.** Apply `scholarliness-protocol.md`: verify field position, concept boundary, literature dialogue, critical judgment, material-to-theory abstraction, title logic, and paragraph-level theoretical action.
20. **Depth calibration.** Apply `argument-depth-protocol.md`: each major section needs concept boundary work, mechanism explanation, counter-tension, material support, and a judgment landing. Add missing depth before calling the draft complete.
21. **Structure firewall review.** Apply `structure-design-protocol.md` again after drafting. Remove or rewrite every diagnostic/checklist heading, and ensure concept boundary work is embedded in substantive sections rather than isolated as a workflow chapter.
22. **Bad-draft review.** Apply `review-rubric.md` and run `scripts/scholarliness_audit.py` plus `scripts/bad_draft_audit.py` when possible. A formally compliant but formulaic draft must be rejected.
23. **Targeted review.** If needed, apply `references/review-agent-protocol.md` as an internal reviewer checklist or reviewer pass. Save reports outside the paper. Revise weak sections, not merely words.
24. **Fact check and citation audit.** Apply `fact-check-protocol.md` and `citation-protocol.md`; remove, verify, or mark unsupported factual claims; audit citation numbering and GB/T 7714 order.
25. **Paper-prose firewall.** Remove all internal workflow vocabulary, checklist phrasing, review labels, diagnostic headings, and instruction-like sentences from the article.
26. **Word delivery.** Create `.docx`, then verify the file exists and can be read.
27. **Profile update.** If the user's materials or feedback imply durable preferences, update the profile.

## Output Contract

For full-paper work, deliver:

- `.docx` file path.
- main-text character count.
- heading hierarchy summary.
- brief thesis summary.
- source basis and source gaps.
- innovation assessment.
- brief internal-quality summary, only in the delivery note, not in the paper.
- citation coverage and citation-conflict status when references are used.
- bad-draft audit status.
- fact-check status.
- residual risks.

For planning-only work, deliver the research brief, structure, innovation analysis, length/hierarchy plan, and next actions without pretending a paper has been written.

## Style Target

The target voice is: 平实、清楚、稳健、有分寸、有判断、有学术质感、有大家风范.

Avoid both extremes:

- ornate academic fog: dense nouns with no judgment.
- ordinary commentary: clear but shallow common sense.

The ideal paragraph makes a complex point understandable without flattening it. Long sentences should carry relationships and mechanisms; short sentences should land the thought.
