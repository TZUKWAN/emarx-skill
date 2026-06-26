# EMARX

EMARX 是一个面向 Codex 的中文学理思辨论文生产系统。v6.9 的核心转向是：从“坏稿审计驱动”转向“正确论文语言生成驱动”。技能本体、参考文件和入口提示已全面中文化，并新增正向论文语言生成协议，把规则从“写完后检测”前移到“落笔之前规定”。

一句话概括：

> 先读资料，再建问题；先定协议，再写正文；先成体系，再求文采；生成前就把论文语言写对，最后才用审计兜底，并生成 Word 把用户反馈沉淀为下一次写作能力。

## v6.9 核心升级

- **技能本体中文化**：`SKILL.md` 主体改为中文内部操作规范，前置描述、工作原则、硬规则、完整流程、输出要求和风格目标均以中文书写。
- **正向生成协议**：新增 `references/generative-writing-protocol.md`，规定摘要、正文段落、文献、路径、结论的生成运动，把“检测规则”前移为“生成前协议”。
- **摘要无主语生成**：摘要默认按“对象进入 -> 问题关系 -> 机制判断 -> 风险或价值 -> 路径指向”生成，禁止“本文说明 -> 本文认为 -> 本文从几个方面分析 -> 本文提出路径”。
- **段落级生成**：每段先确定对象、关系、材料、判断和句式走向，再按“对象锚定 -> 关系展开 -> 材料或文献进入 -> 机制解释 -> 判断落点”生成。
- **文献消化式写作**：不禁止“有研究指出”，而是规定文献必须先消化为概念来源、机制来源、问题来源或限制来源，再随句引用。
- **路径段回归机制**：路径必须从已证机制推出，避免写成“应当加强/完善/优化”的行动手册。
- **审计降级为兜底**：`bad_draft_audit.py` 等脚本保留，但主流程强调生成协议、段落大纲、逐段生成和即时小修，最后才整体审计。
- **参考文件中文正向化**：`wording-expression-protocol.md`、`style-protocol.md` 改写为中文，并增加正向语体示范；`review-rubric.md` 明确审稿是兜底。
- **入口提示中文化**：`agents/openai.yaml` 默认提示改为中文，并把“先写正确”放在“检测风险”前面。
- 保留此前已验证的本地资料优先、当前工作空间真实论文锚定、即时拆解、影子重组、段落级大纲、逐段写作、结构防火墙、10,000-12,000 字、二级标题、GB/T 7714 引用、Word 交付等规则。

## 完整流程

```text
本地资料优先读取
        ↓
资料索引与研究素材建档
        ↓
当前工作空间真实论文锚定
        ↓
锚定论文即时拆解
        ↓
内部影子重组与逻辑骨架分析
        ↓
必要时联网检索补充
        ↓
研究问题诊断
        ↓
文献/资料观点消化
        ↓
逻辑框架与论证链搭建
        ↓
论证许可与文献消化
        ↓
篇幅与标题层级规划
        ↓
前台论文结构设计与结构防火墙
        ↓
段落级详细大纲
        ↓
创新点真实性分析
        ↓
按生成协议逐段写作与逐段即时小修
        ↓
大家风范语体校准
        ↓
匿名评审式审稿（兜底）
        ↓
改稿深化
        ↓
事实核查
        ↓
引用审计与 GB/T 7714 参考文献整理
        ↓
生成 Word
        ↓
用户研究画像与技能偏好迭代
```

## 生成前协议

v6.9 把最重要的规则写在 `references/generative-writing-protocol.md` 中：

- 摘要必须无主语、报道式、对象导向。
- 每段必须按对象-关系-材料-机制-判断运动。
- 文献必须消化进句内论证。
- 路径必须回应已证机制。
- 审稿和审计只作为最后兜底。

## 文献规律底座

EMARX 继承并尊重此前全文蒸馏形成的写作规律。已验证记录：

- 359 个 PDF 文件
- 358 个可读 PDF
- 2,889 / 2,896 页成功提取文本
- 5,161,082 个字符
- 358 份逐篇全文结构画像
- 15 份分组综合报告

`references/distillation-evidence.md` 保留从真实文献中提炼的标题、摘要、引言、正文结构、段落模板、文风控制和审稿规则。v6.9 的新协议是在这些规律之上搭建，而非替代。

v5 又对扩展后的工作空间做了标题层级与篇幅复核。2026-06-25 的全量结构分析记录为：

- 452 个 PDF 文件
- 450 个可读 PDF
- 3,700 页成功提取文本
- 7,783,902 个字符
- 字符数 P25/P50/P75 为 11,676 / 15,877 / 21,072
- 379 / 450 篇可读论文超过 10,000 字符
- 317 / 450 篇可读论文至少检测到二级标题

因此，EMARX 把“10,000-12,000 字正文”和“正文主体必须有二级标题”写成硬规则。

## 语言表达蒸馏

2026-06-27 对扩展后的工作空间重新运行语言表达蒸馏：

- 450 篇可读论文进入分析
- 114 篇显式摘要被识别
- 显式摘要中 62 篇呈现较明显的无作者主语开篇倾向
- 显式摘要中仅 12 篇检测到可疑作者主语或论文自我说明
- 正文中“本文/文章自我说明”和“有研究指出”式综述插入只作为风险信号处理，不能作为 EMARX 默认写法

蒸馏结果保存在 `references/language-expression-distillation-v68.md`。336 篇推断摘要受 PDF 抽取和元数据干扰，只作为辅助证据；显式摘要和用户反馈才是语言规则的核心依据。

## 大家风范语体

EMARX 的目标语言不是晦涩的“学术腔”，也不是普通评论式白话，而是：

```text
平实、清楚、稳健、有分寸、有判断、有学术质感、有大家风范。
```

基本规则：

- 长句负责解释概念、机制和关系
- 中句负责承接、过渡和限定
- 短句负责收束判断
- 节奏服从论证需要，不机械凑句数、句长或交替比例
- 不用生僻词制造学术感
- 不用口号句代替论证
- 不让“提高效率、扩大影响、加强建设”等泛词停留在抽象层面
- 摘要直接呈现研究对象、问题关系和判断，不用“本文认为”“本文旨在”等主语化叙述
- 正文以对象、关系、材料和机制推进，不用“文章的核心观点是”解释自己的写法
- 文献进入句内论证，不用“有研究指出”单独引出一个综述块
- 冒号、引号、破折号只在必要时使用，不制造报告腔和说明书腔

## 安装方式

使用 Codex skill installer 从本仓库安装：

```bash
python ~/.codex/skills/.system/skill-installer/scripts/install-skill-from-github.py --repo TZUKWAN/emarx-skill --path . --name emarx
```

安装后重启 Codex，使技能被重新发现。

## 调用示例

```text
使用 $emarx，先读取工作空间资料，再围绕“生成式人工智能语境下中华文化国际传播的机遇、挑战与路径”生成研究简报、创新点分析、论文初稿和 Word 文档。
```

```text
使用 $emarx，审稿这篇论文，重点检查问题意识、创新点、概念边界、结构闭环、事实核查和语言是否有大家风范。
```

```text
使用 $emarx，把我刚下载的资料纳入研究画像，之后写中华文化国际传播相关论文时优先参考。
```

## 仓库结构

```text
.
├── SKILL.md
├── README.md
├── agents/
│   └── openai.yaml
├── scripts/
│   ├── scan_workspace_sources.py
│   ├── analyze_paper_structure.py
│   ├── build_research_brief.py
│   ├── bad_draft_audit.py
│   ├── citation_audit.py
│   ├── distill_language_expression.py
│   ├── markdown_to_docx.py
│   └── update_user_profile.py
└── references/
    ├── generative-writing-protocol.md
    ├── distillation-evidence.md
    ├── argument-depth-protocol.md
    ├── length-and-hierarchy-protocol.md
    ├── writing-rhythm-protocol.md
    ├── language-expression-distillation-v68.md
    ├── workflow-v4.md
    ├── style-protocol.md
    ├── wording-expression-protocol.md
    ├── review-rubric.md
    ├── fact-check-protocol.md
    ├── citation-protocol.md
    └── user-research-profile.md
```

## 脚本工具

扫描工作空间资料：

```bash
python scripts/scan_workspace_sources.py --root D:\BAOXUE --output sources.json
```

生成研究简报：

```bash
python scripts/build_research_brief.py --topic "论文题目" --sources sources.json --output research-brief.md
```

审计格式合规但论证空转的烂稿风险：

```bash
python scripts/bad_draft_audit.py --paper paper.md --output bad-draft-audit.json
```

分析工作空间论文篇幅与标题层级：

```bash
python scripts/analyze_paper_structure.py --root D:\BAOXUE --output-dir structure-report
```

重新蒸馏工作空间论文语言表达：

```bash
python scripts/distill_language_expression.py --index structure_index.json --output-json language-expression-distillation.json --output-md language-expression-distillation.md
```

审计引用顺序和参考文献列表：

```bash
python scripts/citation_audit.py --paper paper.md --output citation-audit.json
```

Markdown 转 Word：

```bash
python scripts/markdown_to_docx.py --input paper.md --output paper.docx
```

沉淀用户反馈：

```bash
python scripts/update_user_profile.py --profile references/user-research-profile.md --topic "主题" --feedback "反馈"
```

脚本输出只是索引或脚手架，不等于最终事实。事实、引文、数据和政策原文仍需核验。

## 使用边界

EMARX 可以生成研究逻辑、论文结构、论证路径、审稿意见、改稿方案和 Word 文档，但不能自动保证所有现实事实为真。

不要用 EMARX 虚构：

- 引文
- 作者
- 期刊信息
- 页码
- 政策原文
- 统计数据
- 真实案例
- 需要来源支撑的事实判断

当论文涉及最新政策、近期研究、法律法规、机构事实、真实引文或统计数据时，必须使用可靠来源核验后再写入正文。

## 许可

本仓库用于个人 Codex 技能管理与论文写作辅助。若公开传播或复用，请保留来源说明，并自行核验其中涉及的事实、引文和政策材料。
