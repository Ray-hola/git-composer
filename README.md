<p align="center">
  <img src="assets/git-composer-mark.svg" width="82" alt="Git Composer 标志" />
</p>

<h1 align="center">Git Composer</h1>

<p align="center">
  <strong>让仓库更容易看懂、修改、验证与恢复。</strong><br />
  面向 Codex 新手的 Git、README 与仓库维护助手。
</p>

<p align="center">
  <a href="README.en.md">English</a> ·
  <a href="https://github.com/Ray-Hola/git-composer">GitHub</a> ·
  <a href="references/codex-onboarding.md">Codex 上手指南</a> ·
  <a href="references/README.md">完整文档索引</a>
</p>

<p align="center">
  <a href="https://github.com/Ray-Hola/git-composer"><img src="https://img.shields.io/github/stars/Ray-Hola/git-composer?style=flat&label=stars" alt="GitHub stars" /></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-2563eb" alt="MIT license" /></a>
</p>

## 在 Codex 中开始

你不需要先学习终端或 Git。把下面的提示和仓库链接一起交给 Codex：

```text
请从 https://github.com/Ray-Hola/git-composer 安装并启用 git-composer。
安装前先告诉我目标位置、会改哪些文件和需要我确认的事项；不要自动提交或推送。
安装后用一句话说明我可以让它做什么，并等待我的第一个任务。
```

如果当前 Codex 客户端有 Skill 管理界面，也可以选择“从 GitHub 仓库安装”，填入 `Ray-Hola/git-composer`。找不到这个入口时，继续使用上面的自然语言方式即可。

**不需要终端或 Git。** 维护者命令和故障排查命令放在页面底部的“维护者参考”中，不会阻挡第一次使用。

## 第一次成功的判据

安装后发送：

```text
使用 $git-composer 先只读检查这个仓库。
保留我现有的改动，告诉我最值得先修的 3 个问题；先不要修改、提交或推送。
```

你应该看到一份可审查的报告，至少包含：

- 目标仓库、分支和工作区状态；
- 实际读到的文件证据，而不是猜测；
- 已完成、未验证和仍需你决定的事项；
- 风险、恢复方式和下一步。

没有得到确认时，Skill 不应覆盖文件、创建提交或推送远程。

## 你可以直接这样说

| 你的目标 | 可以发送给 Codex 的话 |
| --- | --- |
| 先了解仓库 | `使用 $git-composer 先只读体检，保留现有改动。` |
| 改善首页 | `让 README 更容易让新手上手，先给我方案和需要确认的问题。` |
| 安全提交 | `按已确认范围修改；全部问题回答完、检查通过后再创建一个提交。` |
| 出现问题 | `停止写入，列出已经运行的检查、未验证项和最小恢复步骤。` |

## 它会怎么工作

1. **先查事实**：根目录、分支、差异、历史、入口和已有约定由 Skill 自行读取。
2. **再问选择**：用 grilling 的设计树逐轮询问会改变范围、受众、许可证、验证或副作用的决定。
3. **共同确认**：把最终范围、验收、风险、恢复和排除项复述给你，等你确认。
4. **最后写入**：验证通过后才修改；提交、推送和发布在各自的最后一步分别确认并回读。

## 文档入口

| 你要做什么 | 从这里开始 |
| --- | --- |
| Codex 安装和第一次任务 | [Codex 新手入口](references/codex-onboarding.md) |
| 了解目录和职责 | [项目结构](references/project-structure.md) |
| 建立治理与维护规则 | [治理与说明文件](references/governance-and-docs.md) |
| 设计 README 首页 | [README 设计](references/readme-design.md) |
| 处理分支、提交、同步与恢复 | [Git 工作流](references/git-workflows.md) |
| 判断 Git 写入、远程和发布门禁 | [Git 决策门禁](references/decision-gates.md) |
| 把研究转成可执行规则 | [研究与规则蒸馏](references/research-and-distillation.md) |
| 编写带验证和恢复条件的流程 | [流程卡](references/procedure-cards.md) |
| 检查许可证、版本和徽章事实 | [元数据与徽章](references/metadata-and-badges.md) |
| 编写状态、证据与恢复报告 | [状态与变更报告](references/reporting-templates.md) |
| 查看完整索引 | [references/README.md](references/README.md) |

## 证据与边界

- 已核实的研究材料包含 **252 个去重证据文档**，来源、读取状态和规则候选保存在[研究与规则蒸馏](references/research-and-distillation.md)及其 fixture 中。
- 第四批证据 fixture 可在[这里](fixtures/corpus/github-public-doc-evidence-batch-4.json)复核；它与候选目标、规则候选和用户可见结论分开保存。
- 候选研究目标与已核实文档分开记录；候选目标是未来研究范围，不是 Skill 已完成能力的数量承诺。
- 研究抓取保持只读；公开 HTML fallback 会保留来源和读取状态，方便继续复核。
- 不把许可证、发布、CI、性能、用户数或截图写成没有证据的成功状态。

## 验证

普通使用者可以直接让 Codex 运行：

```text
使用 $git-composer 运行与本次改动匹配的验证。
请分别报告本地检查、CI、远端和视觉预览；没有运行的项目标为“未验证”。
```

维护者检查覆盖结构、引用、UI 元数据、schema、fallback、四批 evidence、grilling 门禁和离线评估。它们不冒充目标仓库业务测试、远端 CI 或 GitHub 页面视觉验收。

## 安全与恢复

- 本地写入、提交、历史改写和远程写入是不同动作，默认先读后写。
- 未闭合的用户问题、未确认的共同理解或失败的验证会阻止 commit/push。
- 不把 API token、私钥、cookie、私人配置、消息记录、数据库、媒体文件或本机状态放进公开仓库。
- 已共享的提交优先用 `git revert` 恢复；不要为了“整洁”强推或重写共享历史。

## 许可证

本项目使用 [MIT License](LICENSE)，署名为 `Ray-hola`。它只说明本 Skill 仓库的代码和文档授权；第三方材料仍以各自许可证为准。

<details>
<summary>维护者参考：命令行安装、检查与恢复</summary>

### 安装与更新

在确认目标目录没有要保留的本地改动后：

```sh
mkdir -p ~/.codex/skills
git clone https://github.com/Ray-Hola/git-composer.git ~/.codex/skills/git-composer
git -C ~/.codex/skills/git-composer pull --ff-only
```

已有本地改动时，先让 Codex 检查并给出恢复方案，不要直接覆盖。

### 精确维护检查

从 Skill 根目录运行：

```sh
python3 scripts/verify_skill.py
python3 scripts/test_research_schema.py
python3 scripts/test_public_html_fallback.py
python3 scripts/test_evidence_batch.py
python3 scripts/test_evidence_batch_two.py
python3 scripts/test_evidence_batch_three.py
python3 scripts/test_evidence_batch_four.py
python3 scripts/test_decision_gates.py
python3 scripts/evaluate_skill.py
```

### 交付状态块

```text
状态：READY / WAITING FOR ANSWER / CONFIRMATION REQUIRED / BLOCKED / COMPLETE
范围：<文件或远端对象>
改动：<一句话>
验证：<命令> → 通过 / 失败 / 未验证
证据：<路径、行号、提交或页面链接>
风险与恢复：<风险；如何回退或恢复>
未知：<仍待确认的事实；没有则写“无”>
下一步：<一条最有价值的动作>
```

</details>
