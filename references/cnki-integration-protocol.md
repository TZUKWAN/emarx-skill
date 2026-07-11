# EMARX × CNKI Control 集成协议

## 一、集成目标

把 CNKI Control 的核心代码内置到 EMARX 中（位于 `scripts/cnki/`），使 EMARX 在选题、锚定精读、文献整理、引用核查四个阶段能够直接调用 CNKI 的北大核心/CSSCI 期刊数据，弥补工作空间本地文献不足的短板。

集成原则：

1. **内置化**：CNKI Control 核心模块复制到 `scripts/cnki/`，EMARX 通过 `scripts/cnki_cli.py` 直接调用，不再依赖外部 `D:\CNKICONTROL` 项目；
2. **自动触发**：EMARX 自动诊断工作空间文献是否充足，不足时主动建议或触发 CNKI 搜索；
3. **格式统一**：搜索结果自动转换为 EMARX 标准 JSON 格式，可直接生成研究简报、候选锚定论文和文献池；
4. **功能绑定**：CNKI 论文不会自动进正文，必须通过 `source-claim-map` 绑定论证功能后才能引用；
5. **用户授权优先**：CNKI 搜索和下载必须在用户已拥有合法访问权限的前提下进行；
6. **结果只作索引**：CNKI 摘要和引用格式只用于索引、选题和引用核查，真正精读仍需回到原文。

## 二、CNKI Control 能向 EMARX 提供什么

| 输出 | 内容 | EMARX 用途 |
|---|---|---|
| `results.json` | 检索结果列表：标题、作者、来源、年/期、被引、详情页 URL | 选题现状扫描、锚定论文候选 |
| `summary.txt` | 单篇结构化摘要：摘要、主要内容、论证逻辑、主要观点、研究方法、主要贡献 | 锚定精读、判断论文是否值得细读 |
| GB/T 7714 引用 | 标准参考文献格式 | 直接导入 EMARX 参考文献池 |
| 批量 summaries 目录 | 多篇摘要文件 | 快速建立研究简报 |

## 三、自动触发机制

### 什么时候自动触发 CNKI

EMARX 在以下节点检查文献缺口：

1. **审题选题阶段**：确定题目后，立即扫描工作空间文献；
2. **锚定精读阶段**：选择锚定论文前，确认候选论文数量；
3. **结构与素材阶段**：大纲完成后，检查每个论证点是否有材料支撑。

触发条件（可配置）：

- 工作空间可用文献总数少于 10 篇；
- 与题目高度相关的文献少于 3 篇；
- 某个核心概念或判断在本地文献中没有支撑。

满足任一条件，EMARX 提示用户运行 CNKI 补充文献。

### 自动触发脚本

`scripts/emarx_literature_gap.py`：

```bash
python scripts/emarx_literature_gap.py \
  --workspace workspace \
  --topic "生成式人工智能 国际传播" \
  --min-local-sources 10 \
  --min-relevant-sources 3 \
  --cnki-pages 3 \
  --top-k 10
```

功能：

- 扫描工作空间 PDF/MD/TXT 文件；
- 按题目关键词匹配计算相关度；
- 输出 `literature-gap-report.json`；
- 若文献不足，自动调用 `cnki_cli.py search` 和 `cnki_cli.py import`；
- 生成 `research-brief.md`、`anchor-papers.md`、`sources.json`。

## 四、文献功能绑定：CNKI 论文如何进入正文

CNKI 搜索到的论文**不会自动插入正文**。它们必须先经过功能绑定。

### 绑定工具

`scripts/emarx_bind_cnki_sources.py`：

```bash
python scripts/emarx_bind_cnki_sources.py \
  --sources workspace/sources.json \
  --outline workspace/outline.md \
  --output workspace/source-claim-map.json
```

输出模板要求每篇候选文献填写：

| 字段 | 说明 |
|---|---|
| `function` | 概念 / 机制 / 问题 / 材料 / 限制 / 反例 |
| `claim_supported` | 该文献支撑正文中的哪个具体判断 |
| `section` | 使用位置：第几节第几段 |
| `verified_against_original` | 是否已回原文核实，不能只看 CNKI 摘要 |
| `priority` | 必引 / 候选 / 弃用 |

### 进入正文的规则

- `priority` 为"必引"的文献必须在正文中出现；
- `priority` 为"候选"的文献可选，根据论证需要决定；
- `priority` 为"弃用"的文献不进入正文；
- `verified_against_original` 为 false 的文献不能直接引用，必须先回原文核实；
- 同一篇 CNKI 论文在正文中最多出现一次（间接引用不超过 1 条）。

## 五、集成使用场景

### 场景 1：选题阶段扫描研究现状

当用户只给了一个大致方向，工作空间又没有足够文献时：

1. 运行 `emarx_literature_gap.py` 诊断文献缺口；
2. 若触发 CNKI，自动生成 `research-brief.md`；
3. 主模型阅读简报后判断：现有研究集中在哪些问题、还有哪些缺口、本文可以从哪里切入。

### 场景 2：锚定论文选择

当需要为 EMARX 选择 3-5 篇锚定论文时：

1. `emarx_literature_gap.py` 输出 `anchor-papers.md`；
2. 主模型按被引量、来源期刊、发表时间筛选 top 论文；
3. 批量采集摘要，判断哪些论文与本次写作最相关；
4. 最终选定的锚定论文回到原文精读。

### 场景 3：文献补充与引用核查

当 EMARX 写作中发现某个判断需要补充文献支撑，或对某个引用来源存疑时：

1. 用 `cnki_cli.py search` 搜索该判断涉及的核心概念或作者；
2. 查看详情页摘要，确认该文献是否真正支撑该判断；
3. 用 `emarx_bind_cnki_sources.py` 绑定功能；
4. 若确认，把 GB/T 7714 引用加入参考文献池。

## 六、内置命令

### 1. `scripts/cnki_cli.py`（主入口）

EMARX 内置的 CNKI 命令入口，直接调用 `scripts/cnki/` 下的核心模块。

```bash
# 搜索并保存为 EMARX 格式
python scripts/cnki_cli.py search "生成式人工智能 国际传播" --pages 3 --output workspace/cnki_results.json

# 批量采集摘要
python scripts/cnki_cli.py read-batch --results workspace/cnki_results.json --output-dir workspace/summaries --limit 10

# 导入 EMARX 工作空间
python scripts/cnki_cli.py import --results workspace/cnki_results.json --summaries-dir workspace/summaries --output-dir workspace --top-k 10
```

### 2. `scripts/emarx_search_cnki.py`（兼容包装）

保留原命令形式，内部调用 `cnki_cli.py search`。`--cnki-root` 参数已废弃，可省略。

```bash
python scripts/emarx_search_cnki.py \
  --query "生成式人工智能 国际传播" \
  --pages 3 \
  --max-results 30 \
  --output workspace/cnki_results.json
```

### 3. `scripts/emarx_import_cnki.py`（兼容包装）

保留原命令形式，内部调用 `cnki_cli.py import`。

```bash
python scripts/emarx_import_cnki.py \
  --results workspace/cnki_results.json \
  --summaries-dir workspace/summaries \
  --output-dir workspace \
  --top-k 10
```

### 4. `scripts/emarx_literature_gap.py`（缺口诊断 + 自动触发）

见第三节。

### 5. `scripts/emarx_bind_cnki_sources.py`（功能绑定）

见第四节。

## 七、与 EMARX 六段流程的对接

| EMARX 阶段 | CNKI 集成动作 | 输出产物 |
|---|---|---|
| 审题选题 | 运行 `emarx_literature_gap.py` 诊断缺口并触发搜索 | `literature-gap-report.json`、`research-brief.md` |
| 锚定精读 | 从 `anchor-papers.md` 选择 top 论文，批量采集摘要 | `anchor-papers.md`、`summaries/` |
| 结构与素材 | 用 `emarx_bind_cnki_sources.py` 绑定文献功能 | `source-claim-map.json` |
| 小节写作 | 根据 `source-claim-map.json` 插入经过功能绑定的引用 | 新增引用 |
| 审稿改稿 | 核查关键引用的 GB/T 7714 格式和摘要 | 引用修正 |
| Word 交付 | 把 CNKI 提供的 GB/T 7714 引用合并入参考文献 | 最终参考文献表 |

## 八、政治合规与学术伦理

1. **合法授权**：CNKI 搜索和引用采集必须在用户已拥有合法访问权限的前提下进行；
2. **不绕过付费墙**：CNKI Control 本身不破解付费墙，EMARX 也不应利用它获取无权限全文；
3. **引用准确性**：CNKI 提供的 GB/T 7714 格式需人工核对，不能直接信任；
4. **不替代精读**：CNKI 摘要只用于筛选和索引，真正写作必须回到原文或可靠 PDF；
5. **查重风险**：从 CNKI 复制摘要或引用格式不会导致查重问题，但直接复制论文原文会。

## 九、依赖安装

CNKI 模块需要单独安装依赖。在 EMARX 根目录执行：

```bash
python -m pip install -r scripts/cnki/requirements.txt
python -m playwright install chromium
```

建议在虚拟环境中安装，避免污染全局 Python 环境。

## 十、使用限制

1. CNKI 页面结构变化可能导致内置 CNKI 模块失效，需要定期维护；
2. 反爬机制可能触发安全验证，需要用户人工处理；
3. 大规模批量下载可能触发账号限制，建议控制频率；
4. 内置 CNKI 模块目前主要针对期刊论文，学位论文、会议论文等类型支持有限。

## 十一、失败处理

当 CNKI 集成失败时：

1. 优先使用工作空间已有本地文献；
2. 使用 WebSearch 或 FetchURL 获取公开论文信息；
3. 在交付说明中明确标注哪些引用来自 CNKI、哪些来自本地文献、哪些需要进一步核实。
