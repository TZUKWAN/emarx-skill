# EMARX Skill 安装说明（给 AI 与最终用户）

## 一、技能信息

- **技能名称**：`emarx`
- **仓库地址**：`https://github.com/TZUKWAN/emarx-skill.git`
- **适用场景**：中文人文社科论文（尤其是马克思主义理论、思想政治教育、党史党建等）的选题、写作、审稿与 Word 交付。
- **默认输出**：Markdown 工作稿 + DOCX 文档。

## 二、安装方式

### 方式 1：通过 Kimi Code CLI 命令安装（推荐）

在 Kimi Code CLI 中执行：

```bash
kimi skill install https://github.com/TZUKWAN/emarx-skill.git
```

安装完成后，EMARX 会出现在可用技能列表中。

### 方式 2：手动克隆并放置到 skills 目录

如果当前 CLI 不支持 `kimi skill install`，可手动操作：

```bash
# 克隆仓库到本地任意位置
git clone https://github.com/TZUKWAN/emarx-skill.git /tmp/emarx-skill

# 复制到 Kimi Code CLI 的 skills 目录
# Windows 默认路径：C:\Users\<用户名>\.kimi\skills\emarx
# macOS/Linux 默认路径：~/.kimi/skills/emarx

cp -r /tmp/emarx-skill/* ~/.kimi/skills/emarx/
```

### 方式 3：在当前工作空间使用 Project scope

如果不想安装为 User scope skill，可以把仓库内容放到当前项目的 `.codex/emarx/github-export/` 目录下，Kimi Code CLI 会自动识别为 Project scope skill。

## 三、安装后验证

安装完成后，让 AI 读取 `SKILL.md` 确认加载成功：

```bash
# AI 应能直接引用以下文件
SKILL.md
references/production-workflow-v7.md
references/cnki-integration-protocol.md
```

可以让 AI 执行一次快速自检：

```bash
python scripts/cnki/env_check.py
```

如果输出"环境已就绪"，说明 Python 依赖和浏览器都已准备好。

## 四、首次使用：零配置

EMARX 设计为**首次使用时自动配置环境**。用户不需要手动运行 `pip install` 或 `playwright install`。

AI 首次调用以下任意脚本时，脚本会自动：

1. 在技能目录下创建隔离的虚拟环境 `.venv/`；
2. 安装所有 Python 依赖（python-docx、pdfplumber、playwright、ddddocr 等）；
3. 下载 Playwright Chromium 浏览器；
4. 切换到虚拟环境继续执行原命令。

示例：

```bash
python scripts/cnki_cli.py search "生成式人工智能 国际传播" --pages 3 --output workspace/cnki_results.json
```

首次运行可能需要 3-10 分钟下载浏览器和依赖，AI 应提前告知用户。

## 五、AI 使用 EMARX 的标准流程

1. **确认用户意图**：完整论文、大纲、某一部分修改、审稿等；
2. **读取 SKILL.md**：了解当前版本的总原则和流程；
3. **扫描工作空间**：区分正式论文、政策资料、用户草稿和技能文件；
4. **按需调用 CNKI**：工作空间文献不足时，运行 `scripts/emarx_literature_gap.py`；
5. **按六段流程执行**：审题选题 → 锚定精读 → 结构与素材 → 小节写作 → 审稿改稿 → Word 交付；
6. **交付前审计**：运行 AI 痕迹审计、引用审计、引用位置审计、DOCX 审计等。

## 六、注意事项

1. **Pandoc 无法自动安装**：Word 交付需要 pandoc，它不是 Python 包。若系统未安装 pandoc，AI 应提示用户从 https://pandoc.org/installing.html 安装。
2. **网络要求**：首次自动配置需要下载 Python 包和 Chromium 浏览器，需保持网络畅通。
3. **Windows 推荐**：EMARX 的 Word 交付和 pywin32 依赖在 Windows 上最稳定。
4. **不要提交 .venv**：`.venv/` 已被 `.gitignore` 排除，不应提交到仓库。

## 七、故障排查

| 现象 | 可能原因 | 解决方式 |
|---|---|---|
| 提示缺少 Python 依赖 | 自动安装失败 | 手动运行 `python scripts/setup_emarx.py`，或检查网络 |
| 提示缺少 Chromium | Playwright 浏览器未下载成功 | 运行 `python scripts/setup_emarx.py` 重新安装 |
| Word 生成失败 | 未安装 pandoc | 安装 pandoc 并加入系统 PATH |
| CNKI 搜索被拦截 | 反爬验证 | 使用 `--no-headless` 或连接已登录的 Chrome CDP |

## 八、技能更新

当仓库更新后，AI 应重新安装 skill：

```bash
kimi skill update emarx
```

或手动拉取仓库并覆盖 `~/.kimi/skills/emarx/` 目录。
"