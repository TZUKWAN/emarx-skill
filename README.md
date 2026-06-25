# EMARX

EMARX 是一个面向 Codex 的中文学理思辨论文生产系统。v5 版本的重点不再只是“把论文写得更像论文”，而是建立一套完整流程：本地资料优先读取、资料建档、研究逻辑梳理、创新点分析、篇幅与标题层级规划、初稿写作、大家风范语体校准、匿名评审式审稿、改稿深化、事实核查、Word 交付，以及用户研究画像迭代。

一句话概括：

> 先读资料，再建问题；先有判断，再写正文；先成体系，再求文采；最后生成 Word，并把用户反馈沉淀为下一次写作能力。

## v5 核心升级

- 本地资料优先，不再凭空写作
- 必要时再联网检索，补充最新政策、数据、法规、文献和事实
- 写作前必须形成研究简报与问题诊断
- 完整论文默认正文 10,000-12,000 字，不再把短篇聊天文本伪装成论文
- 正文主体必须有二级标题，默认使用“一、”“（一）”的中文学术层级
- 写作节奏按论证需要校准，不用句长比例或交替配额控制文风
- 新增论证许可、文献消化和烂稿反审，防止“格式合规但思想空转”
- 强制分析选题、视角、概念、机制、路径、表达六类创新
- 尊重既有文献蒸馏规律，不用通用写作建议覆盖真实文献规律
- 正文写作后必须进行大家风范语体校准
- 审稿不只是润色，而是检查问题意识、概念、结构、证据和创新
- 事实核查与写作生成分离，不虚构引文、数据、政策原文和来源
- 完整论文默认生成 Word `.docx`
- 用户新资料和反馈可以沉淀进本地研究画像
- 引用按“一篇文献只引一次、一个作者只引一次、随句插入、顺序编号、GB/T 7714 文末列表”执行

## 完整流程

```text
本地资料优先读取
        ↓
资料索引与研究素材建档
        ↓
必要时联网检索补充
        ↓
研究问题诊断
        ↓
文献/资料观点梳理
        ↓
逻辑框架与论证链搭建
        ↓
论证许可与文献消化
        ↓
篇幅与标题层级规划
        ↓
创新点真实性分析
        ↓
初稿写作
        ↓
大家风范语体校准
        ↓
匿名评审式审稿
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

## 文献规律底座

EMARX v5 继承并尊重此前全文蒸馏形成的写作规律。该批材料的已验证记录为：

- 359 个 PDF 文件
- 358 个可读 PDF
- 2,889 / 2,896 页成功提取文本
- 5,161,082 个字符
- 358 份逐篇全文结构画像
- 15 份分组综合报告

`references/distillation-evidence.md` 中保留了标题、摘要、引言、正文结构、段落模板、文风控制、审稿规则等从真实文献中提炼出的规律。v5 的新流程是在这些规律之上搭建，而不是替代它们。

v5 又对扩展后的工作空间做了标题层级与篇幅复核。2026-06-25 的全量结构分析记录为：

- 452 个 PDF 文件
- 450 个可读 PDF
- 3,700 页成功提取文本
- 7,783,902 个字符
- 字符数 P25/P50/P75 为 11,676 / 15,877 / 21,072
- 379 / 450 篇可读论文超过 10,000 字符
- 317 / 450 篇可读论文至少检测到二级标题

因此，EMARX v5 把“10,000-12,000 字正文”和“正文主体必须有二级标题”写成硬规则。此前没有二级标题、篇幅过短的输出，按 v5 标准视为不合格。

## 大家风范语体

EMARX v5 的目标语言不是晦涩的“学术腔”，也不是普通评论式白话，而是：

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
│   ├── markdown_to_docx.py
│   └── update_user_profile.py
└── references/
    ├── distillation-evidence.md
    ├── argument-depth-protocol.md
    ├── length-and-hierarchy-protocol.md
    ├── writing-rhythm-protocol.md
    ├── workflow-v4.md
    ├── style-protocol.md
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
