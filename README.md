# EMARX v7.4

面向中文人文社科期刊语境的学理思辨论文生产技能。覆盖选题、资料读取、结构搭建、正文写作、审稿改稿到 Word 交付的全流程，尤其适合马克思主义理论、思想政治教育、党史党建、文化研究等纯文字性学科学术写作。

## 简介

EMARX 不是论文模板或提示词集合，而是一套带证据门槛的论文生产系统。它要求 AI 先读取用户工作空间的真实资料，锚定 3-5 篇相关论文并回到原文精读，形成期刊体例画像、论证骨架和段落级大纲，再以小节为最小单元逐段生成有推进、有判断、有材料支撑的学术论文。

v7.4 在 v7.x 基础上重点做了三件事：

1. **减少规则过载和模板化**：从固定章节结构转向由题目内部关系生长结构，避免"概念边界—理论基础—现实意义"这类形式主义标题。
2. **吸收 marx-paper-skills 优势**：融合其选题分流方法、结构方法和 Word 交付技术，形成统一入口。
3. **内置 CNKI 文献能力**：把 CNKI Control 的核心检索、摘要、引用功能内置到 EMARX，工作空间文献不足时可自动触发 CNKI 补充。

## 适用场景

- 马克思主义理论一级学科（0305）及思想政治教育、党史党建、文化研究等方向；
- 纯文科、无实证、以概念分析和机制论证为主的课程论文、期刊论文、学位论文；
- 需要 GB/T 7714 参考文献、页下注圈码、Word 直接交付的中文人文社科论文。

## 核心特性

### 1. 先读后写，拒绝凭空综述

不凭空生成"有研究指出""国内外学者普遍认为"等无内容综述。所有事实、政策、数据、案例和文献观点必须回到来源核验，本地工作空间优先。

### 2. 结构由题目生长，而非模板拼装

论文结构根据研究对象内部的真实关系和论证任务生长，避免预设独立章节。一级标题之间必须形成递进关系，能通过"互换测试"和"删除测试"。

### 3. 小节级准入 + 段落级推进

- 每个二级小节先写论证卡，说明要解释的关系、承接问题、材料功能和写作方法；
- 小节内逐段生成，每个自然段只承担一个清楚的论证推进；
- 一节写完、审完、过门后，再进入下一节。

### 4. 三重 subagent 逻辑审查

在大纲完成、小节生成前、小节生成后三个关键节点，调用 15 个定位不同的 subagent 进行多视角逻辑审查，避免机械模板和逻辑跳跃。

### 5. 内置 CNKI 自动补充

工作空间文献不足时，自动调用内置 CNKI 模块检索北大核心/CSSCI 期刊论文，生成研究简报、候选锚定论文和文献池。CNKI 论文不会自动进入正文，必须通过 source-claim 绑定并回原文核实后才能引用。

### 6. 零配置环境

首次使用 EMARX 脚本时，自动创建隔离虚拟环境、安装 Python 依赖、下载 Playwright 浏览器。用户无需手动运行 `pip install` 或 `playwright install`。

### 7. 一键 Word 交付

支持生成符合人文社科期刊习惯的 Word 文档：页下注圈码 ①②③、每页重新编号、标题黑体居中、正文宋体小四、1.5 倍行距、参考文献悬挂缩进。

### 8. 多重审计兜底

初稿后自动运行坏稿审计、学理性审计、引用审计、引用位置审计、AI 痕迹审计和 DOCX 审计，确保交付物有证据、可追溯。

## 技能架构

```text
emarx/
├── SKILL.md                          # 技能总入口与核心规则
├── INSTALL.md                        # AI/用户安装说明
├── README.md                         # 本文件
├── agents/                           # subagent 群
│   ├── openai.yaml                   # agent 配置
│   ├── outline-reviewers/            # 大纲逻辑审查（5 个）
│   ├── section-card-reviewers/       # 小节论证卡审查（5 个）
│   └── paragraph-reviewers/          # 段落逻辑审查（5 个）
├── references/                       # 写作协议与指南
│   ├── production-workflow-v7.md     # 主流程
│   ├── citation-fact-protocol-v7.md  # 引用与事实核查
│   ├── logical-chain-protocol.md     # 逻辑推理链
│   ├── cnki-integration-protocol.md  # CNKI 集成
│   ├── journal-profiles/             # 顶刊画像
│   └── ...                           # 其他 30+ 份协议
├── scripts/                          # 脚本工具
│   ├── cnki/                         # 内置 CNKI Control 模块
│   ├── cnki_cli.py                   # CNKI 命令行入口
│   ├── emarx_literature_gap.py       # 文献缺口诊断与 CNKI 触发
│   ├── emarx_bind_cnki_sources.py    # CNKI 文献功能绑定
│   ├── emarx_build_docx.py           # Word 交付
│   ├── emarx_env.py                  # 自动环境管理
│   ├── scan_workspace_sources.py     # 工作空间扫描
│   ├── select_anchor_papers.py       # 锚定论文选择
│   ├── section_quality_gate.py       # 小节质量门
│   ├── citation_audit.py             # 引用审计
│   ├── ai_trace_audit.py             # AI 痕迹审计
│   └── ...
└── requirements.txt                  # Python 依赖
```

## 工作流程：完整论文六段流程

### 1. 审题选题

明确用户场景（课程论文 / 期刊投稿 / 学位论文）、目标期刊、已有资料和方向明确度。参考 `topic-and-structure-guide.md` 的三层选题法：特征识别 → 情况分流 → 拟题配方。拟题必须符合"大背景 + 小切口""标题无问号"等原则。

确定题目后，优先运行 `scripts/emarx_literature_gap.py` 诊断文献缺口。若本地文献不足，自动触发内置 CNKI 搜索。

### 2. 锚定精读

扫描工作空间真实论文，选择 3-5 篇功能互补的锚定论文（研究对象接近、理论视角有用、结构值得参照、材料支撑充分、表达节奏成熟）。锚定后必须回到原文连续读取，不能只看摘要或拆解报告。

建立概念台账，记录核心概念的定义、来源、区分和使用边界。涉及经典文本时回到原文精读。

### 3. 结构与素材

根据对象内部关系搭建 3-5 个一级标题，每个主体部分配二级标题。建立来源到论点映射，每篇文献只绑定一处正文使用位置。若使用 CNKI 论文，运行 `emarx_bind_cnki_sources.py` 完成功能绑定。

大纲完成后，调用 `agents/outline-reviewers/` 中的 5 个 subagent 进行逻辑审查。

### 4. 小节写作

每个二级小节先写论证卡，再调用 `agents/section-card-reviewers/` 审查。通过后在小节内逐段生成，段落之间建立清晰逻辑关联。

每个小节写完后，调用 `agents/paragraph-reviewers/` 审查段落推进、论据闭环、语言风格、引用位置和收束质量。

### 5. 审稿改稿

初稿完成后依次审逻辑、审语言、审政治合规、审格式。运行 AI 痕迹审计，对高风险段落进行人工改写。形式合格但仍像说明书、综述或套壳稿时，必须回到段落级大纲重写，不能只润色。

### 6. Word 交付

使用新的 Word 交付 pipeline：

```bash
python scripts/emarx_build_docx.py paper.md paper.docx
```

默认生成圈码脚注并每页重新编号。交付前确认：标题黑色、正文引用为上标、脚注格式正确、参考文献悬挂缩进。

## 安装

### 通过 Kimi Code CLI 安装

```bash
kimi skill install https://github.com/TZUKWAN/emarx-skill.git
```

### 手动安装

```bash
git clone https://github.com/TZUKWAN/emarx-skill.git
# 复制到 Kimi Code CLI skills 目录
# Windows: C:\Users\<用户名>\.kimi\skills\emarx
# macOS/Linux: ~/.kimi/skills/emarx
cp -r emarx-skill/* ~/.kimi/skills/emarx/
```

### 首次使用

用户把 EMARX 交给 AI 后，AI 会直接调用脚本。**脚本会自动创建隔离虚拟环境、安装依赖、下载浏览器**，首次运行可能需要 3-10 分钟。用户不需要手动运行任何安装命令。

唯一无法自动安装的外部依赖是 **pandoc**（Word 交付所需）。若系统未安装 pandoc，AI 会提示用户从 https://pandoc.org/installing.html 安装。

## 快速开始

```bash
# 1. 诊断文献缺口，必要时自动触发 CNKI
python scripts/emarx_literature_gap.py \
  --workspace workspace \
  --topic "生成式人工智能 国际传播" \
  --min-local-sources 10 \
  --min-relevant-sources 3 \
  --cnki-pages 3 \
  --top-k 10

# 2. 扫描工作空间来源
python scripts/scan_workspace_sources.py --root workspace --output workspace/sources.json

# 3. 选择锚定论文
python scripts/select_anchor_papers.py \
  --topic "论文题目" \
  --workspace-root workspace \
  --output workspace/anchor-papers.md \
  --top-k 5

# 4. 生成 Word（默认圈码 + 每页重编号）
python scripts/emarx_build_docx.py workspace/paper.md workspace/paper.docx

# 5. 运行审计
python scripts/citation_audit.py --paper workspace/paper.md --output workspace/citation-audit.json
python scripts/ai_trace_audit.py --paper workspace/paper.md --output workspace/ai-trace-audit.json
python scripts/audit_docx.py --docx workspace/paper.docx --output workspace/docx-audit.json
```

## 常用命令

| 命令 | 用途 |
|---|---|
| `python scripts/emarx_literature_gap.py` | 文献缺口诊断 + 自动 CNKI 触发 |
| `python scripts/emarx_bind_cnki_sources.py` | CNKI 论文功能绑定 |
| `python scripts/cnki_cli.py search "关键词"` | 手动 CNKI 检索 |
| `python scripts/scan_workspace_sources.py` | 扫描工作空间来源 |
| `python scripts/select_anchor_papers.py` | 选择锚定论文 |
| `python scripts/section_quality_gate.py` | 小节质量门检查 |
| `python scripts/emarx_build_docx.py` | Word 交付 |
| `python scripts/citation_audit.py` | 引用审计 |
| `python scripts/citation_position_audit.py` | 引用位置审计 |
| `python scripts/ai_trace_audit.py` | AI 痕迹审计 |
| `python scripts/audit_docx.py` | DOCX 审计 |

## 引用规则

- 引用必须贴住被它支撑的那句话，**不集中堆到段落末尾**；
- 一篇文献只引用一次，一个作者只出现一次；
- 禁止"有研究指出""学者认为"等无内容综述引语；
- 文献必须明确论证功能：概念、机制、材料、限制、反例或对话；
- 完整论文默认参考文献不少于 28 条，不足时必须明示真实原因；
- 文末参考文献按正文引用顺序排列，GB/T 7714 格式。

## CNKI 集成

EMARX 内置了 CNKI Control 的核心能力，位于 `scripts/cnki/`。

- 工作空间文献不足时，自动触发 CNKI 检索；
- 输出 `research-brief.md`、`anchor-papers.md` 和 `sources.json`；
- CNKI 论文不会自动进入正文，必须通过 `emarx_bind_cnki_sources.py` 绑定论证功能并回原文核实；
- 只有 `priority=必引` 且 `verified_against_original=true` 的 CNKI 论文才能进入正文。

详见 `references/cnki-integration-protocol.md`。

## 交付标准

完整论文交付必须包含：

- Markdown 工作稿路径；
- DOCX 文件路径；
- 正文字数、标题层级摘要、核心论点摘要；
- 使用的主要本地来源和来源缺口；
- 引用冲突、引用审计状态和引用位置审计状态；
- 参考文献数量及不足 28 条的真实原因；
- 事实核查状态、政治合规自查状态；
- AI 痕迹审计状态、查重预检状态；
- DOCX 审计和渲染检查状态；
- 残余风险说明。

## 注意事项

1. EMARX 生成的是辅助性学术草稿，最终事实、政策、数据和引用仍需作者核验；
2. 涉及党的创新理论、党史、民族、宗教、港澳台、国际关系等敏感议题时，必须回到权威原文；
3. 450 份拆解报告只作索引，不能直接搬入正文；
4. pandoc 需要用户自行安装；
5. 首次运行脚本需要下载依赖和浏览器，请保持网络畅通。

## 主要文件

```text
SKILL.md
references/production-workflow-v7.md
references/citation-fact-protocol-v7.md
references/generative-writing-protocol.md
references/logical-chain-protocol.md
references/section-production-gate-v71.md
references/style-protocol.md
references/cnki-integration-protocol.md
agents/openai.yaml
scripts/emarx_build_docx.py
scripts/emarx_literature_gap.py
scripts/emarx_bind_cnki_sources.py
```

## 版本历史

- **v7.4**（当前）：减少规则过载，吸收 marx-paper-skills 方法，内置 CNKI，新增逻辑链 subagent 群，零配置环境。
- v7.3：标题与参考文献规则优化。
- v7.2：期刊体例与问题链 workflow。
- v7.1：小节质量门。
- v7.0：工作流与 DOCX 处理升级。
- v6.9：中文重写与生成式写作协议。
