# EMARX Review Agent Protocol

## Purpose

EMARX 必须在交付前通过一支专业化审稿 agent 团队。审稿不是形式检查，而是模拟真实期刊审稿流程，从学理性、逻辑、遣词造句、格式四个维度提出可执行的修改意见。

## When to Use

- 任何 full-paper 任务在生成 `.docx` 之前。
- 用户明确要求审稿或深度修订时。
- 主 agent 自己判断草稿可能还有隐性质量问题，需要外部视角时。

## Agent Team

| Agent | 角色文件 | 审查重点 | 对应协议 |
|---|---|---|---|
| ScholarlyReviewer | `references/review-agents/scholarly-reviewer.md` | 问题意识、概念、理论框架、文献对话、批判判断、材料抽象 | `scholarliness-protocol.md` |
| LogicReviewer | `references/review-agents/logic-reviewer.md` | 中心论点、机制链、段落功能、证据-判断、反综述、对策可执行性 | `argument-depth-protocol.md`, `paragraph-moves-protocol.md`, `material-anchoring-protocol.md` |
| ProseReviewer | `references/review-agents/prose-reviewer.md` | 段首、过渡、动词、节奏、机器腔、术语、口号化 | `style-protocol.md`, `wording-expression-protocol.md`, `writing-rhythm-protocol.md` |
| FormatReviewer | `references/review-agents/format-reviewer.md` | 标题层级、字数、引用、参考文献、事实风险、Word 输出 | `length-and-hierarchy-protocol.md`, `citation-protocol.md`, `fact-check-protocol.md` |

## Workflow

1. **Pre-review audit.** 主 agent 先运行 `scripts/bad_draft_audit.py`、`scripts/citation_audit.py`（如需要引用）和 `scripts/scholarliness_audit.py`，拿到基础数据。
2. **Spawn review agents.** 并行启动四个审稿 agent，向每个 agent 传递：
   - 论文 Markdown 路径；
   - 该 agent 对应的协议文件路径；
   - 基础审计数据（可选）。
3. **Collect reports.** 每个 agent 返回结构化的 markdown 审稿报告。
4. **Consolidate.** 主 agent 合并四份报告：
   - 按优先级排序；
   - 标记冲突（如学理性要求增加概念，遣词造句要求删除术语）；
   - 给出统一修订计划。
5. **Revise.** 主 agent 根据修订计划重写相关 section，而不是只改词语。
6. **Re-review.** 对修改后的部分重新运行相关 agent，直到没有高优先级问题，或用户明确接受剩余问题。

## Auto-Optimization Loop

审稿不是一次性检查，而是迭代优化。规则如下：

- **最少审稿轮次：3 轮。** 即使第一轮没有 fail，也必须跑满 3 轮，确保 weak 问题被逐步消除。
- **终止条件（满足任意一条即可）：**
  - 连续两轮没有出现任何 fail，且 weak 问题数量不再减少；
  - 已达到 5 轮上限；
  - 用户明确要求停止并接受当前版本。
- **每轮必须做的事：**
  - 主 agent 根据上轮报告修订论文；
  - 保存新版本为 `paper_vX_roundN.md`；
  - 生成或更新审稿报告 `review-report-roundN-[role].md`；
  - 在下一轮中重点检查上一轮标记为 fail/weak 的维度。
- **冲突处理：** 当不同审稿 agent 意见冲突时，以“是否服务于核心论点”为最终标准。若无法判断，把冲突写入报告并交由用户决定。

## Final Review Report

最后一轮结束后，主 agent 输出一份汇总报告：

```markdown
## EMARX 审稿与修订汇总

### 审稿轮次：N

### 每轮关键改动
- 第 1 轮：...
- 第 2 轮：...
- 第 3 轮：...

### 最终评级
- 学理性：pass / weak / fail
- 逻辑：pass / weak / fail
- 遣词造句：pass / weak / fail
- 格式：pass / weak / fail

### 已解决的核心问题
- ...

### 残留的 weak 问题及接受理由
- ...

### 最终文件
- Markdown: ...
- Word: ...
```

## Output Contract

最终交付时，向用户说明：

- 四个审稿 agent 的评级汇总；
- 已采纳的关键修改；
- 未采纳的意见及原因；
- 仍存在的 residual risks。

## Rules

- 审稿 agent 必须给出可执行的修改建议，不能只说“这里不好”。
- 任何维度出现 fail，论文不得交付，必须先修订。
- 主 agent 不能机械地接受所有意见；出现冲突时以“服务于核心论点”为最终判断标准。
- 审稿报告应作为交付物的一部分保存，路径建议为 `.codex/tmp_session/review-report-[topic].md`。
