# EMARX User Research Profile

This file stores durable user preferences and research direction. Update it only when the user provides materials, feedback, or standards that should influence future work.

## Research Themes

- Chinese academic-theoretical essay writing.
- Marxism, ideological-political education, Chinese culture, cultural communication, subjectivity, AI philosophy, technology critique, cultural memory.

## Preferred Workflow

- Read local workspace materials before web search.
- Build research logic before drafting.
- Analyze real innovation before writing.
- Produce Word `.docx` for full papers.
- Review and revise substantively.
- Fact-check source-backed claims.

## Style Preferences

- Plain and clear language.
- Strong academic texture.
- Long, medium, and short sentence rhythm.
- Rhythm should be qualitative and argument-driven, not controlled by sentence-length quotas.
- Mature, steady, "大家风范" voice.
- Conceptually precise but not obscure.
- Deep insight over formulaic completeness.

## Disliked Output

- Shallow "机遇、挑战、路径" listing.
- Generic policy commentary.
- Empty slogans.
- Heavy terminology without mechanism.
- Chat-only paper delivery when Word is expected.
- Fabricated citations or unsupported factual claims.

## Confirmed Lessons

- v3 improved Word delivery and anti-shallow rules but still needs a full research-production workflow.
- EMARX must preserve corpus-derived writing patterns from `distillation-evidence.md`.
- EMARX must become a personal research and knowledge-deposition system, not just a writing prompt.
- Full papers must not be short chat essays. The default target is 10,000-12,000 Chinese characters in the main text.
- Full papers must include second-level headings under major body sections. Missing second-level headings is a visible quality failure.
- The expanded workspace audit on 2026-06-25 found 452 PDFs, 450 readable PDFs, and a strong structural signal for two-level headings and 10,000+ character papers.

## Updating Notes

Append future user feedback here with date, topic, preference, and action taken.

## Feedback 2026-06-25 13:42

- Topic: 论文引用规范
- Feedback: 引用必须一篇文献只引用一次，一个作者只引用一次；工作空间文献需要覆盖使用；引用随句插入为[X]，不能堆在段落末尾；文末按引用顺序使用GB/T 7714格式。
- Action: 后续完整论文任务必须先做引用覆盖表和冲突检查，再写作、审稿和引用审计。

## Feedback 2026-06-25 14:30

- Topic: 篇幅、标题层级与学理深度
- Feedback: EMARX 生成论文没有二级标题，结构显得诡异；篇幅太短，完整论文应在 10,000-12,000 字之间；新增论文后需要重新分析全部论文的标题层级；行文仍需更深入、更有学理性。
- Action: v5 增加 `length-and-hierarchy-protocol.md`，把 10,000-12,000 字、二级标题、结构深度校准和交付前标题层级报告写成硬规则。

## Feedback 2026-06-25 15:05

- Topic: 写作节奏
- Feedback: 节奏比例可以作为语料分析结果，但不能作为技能硬性要求；节奏不是通过定量要求得出来的，不能让 EMARX 机械凑句长和交替比例。
- Action: 新增 `writing-rhythm-protocol.md`，把全量节奏分析转化为质性原则：节奏服从论证需要，长句展开关系，中句承接推进，短句落定判断；比例只作为后台诊断证据，不进入生成配额。

## Feedback 2026-06-25 16:25

- Topic: 形式合规但思想空转
- Feedback: v5 重写稿虽然补齐字数、二级标题、引用和 Word，但行文风格仍然很差，像规则套壳，缺少真正的学理推进。
- Action: 新增 `argument-depth-protocol.md` 和 `scripts/bad_draft_audit.py`。后续完整论文必须先通过论证许可、文献消化和烂稿反审；形式合规不等于可交付。

## Feedback 2026-06-25 17:05

- Topic: 日常写作提示词与反机器腔语体
- Feedback: 写作要谨慎思考、深入研究、多角度推进；语言要平实但有学术质感，逻辑严谨，层层递进；少用引号，不自造新词，不夸张；禁止机械使用“首先、其次、再次、最后”；禁止“重构、重建、填补空白”等夸张表达；禁止“不是……而是……”和“并非……而是……”等公式化对照；避免一眼像 AI 的冒号、破折号和过度标点；正文段落应自然展开，不用小标题和分点替代论证。
- Action: 将该提示词转化为 `style-protocol.md` 的 Daily Prose Constraints，并加入坏稿审计和审稿清单。完整论文仍保留正式标题层级要求，但正文段落内部禁止机械分点和清单腔。
