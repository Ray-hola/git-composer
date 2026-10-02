<p align="center">
  <img src="assets/git-composer-mark.svg" width="82" alt="Git Composer 标志" />
</p>

<h1 align="center">Git Composer</h1>

<p align="center">
  <strong>让仓库更容易看懂、修改、验证与恢复。</strong><br />
  面向新手的 Git、README 与仓库维护助手。
</p>

<p align="center">
  <a href="README.en.md">English</a> ·
  <a href="https://github.com/Ray-Hola/git-composer">GitHub</a> ·
  <a href="references/README.md">文档索引</a>
</p>

<p align="center">
  <a href="https://github.com/Ray-Hola/git-composer"><img src="https://img.shields.io/badge/GitHub-查看仓库-181717?logo=github&logoColor=white" alt="查看 GitHub 仓库" /></a>
  <a href="https://github.com/Ray-Hola/git-composer"><img src="https://img.shields.io/github/stars/Ray-Hola/git-composer?style=flat&label=stars" alt="GitHub stars" /></a>
  <a href="#验证"><img src="https://img.shields.io/badge/status-本地检查已记录-2563eb" alt="状态：本地检查已记录" /></a>
</p>

## 60 秒开始

先做一次只读检查。下面的命令不会改文件、提交、推送或修改远程配置：

```sh
git rev-parse --show-toplevel
git status --short --branch
git diff --stat
git log -1 --format='%h %s%n%b'
```

然后把仓库交给 Git Composer：

```text
使用 $git-composer 先只读检查这个仓库。保留现有改动，改善 README 和验证入口，并报告变更、证据、检查、风险与恢复方式。
```

你应该得到一份可审查的状态报告：范围、实际文件、命令结果、证据、未验证项、恢复路径和下一步。没有运行的检查会明确标为“未验证”。

## 它解决什么问题

### 先看清，再动手

先确认根目录、分支、差异、历史、运行入口和已有约定，避免把猜测当成项目事实。

### 做小而可回退的改动

改善 README、目录说明、贡献流程或 Git 操作时，优先复用现有结构，不凭空添加许可证、发布、CI 或性能承诺。

### 交付可追溯的结果

把“改了什么、为什么、怎么验证、哪里还未知、怎样恢复”写清楚，并区分候选项目、证据文档和研究结论。

## 文档入口

| 你要做什么 | 从这里开始 |
| --- | --- |
| 了解目录和职责 | [项目结构](references/project-structure.md) |
| 建立治理与维护规则 | [治理与说明文件](references/governance-and-docs.md) |
| 设计 README 首页 | [README 设计](references/readme-design.md) |
| 处理分支、提交、同步与恢复 | [Git 工作流](references/git-workflows.md) |
| 判断 Git 写入、远程和发布门禁 | [Git 决策门禁](references/decision-gates.md) |
| 把研究转成可执行规则 | [研究与规则蒸馏](references/research-and-distillation.md) |
| 编写带验证和恢复条件的流程 | [流程卡](references/procedure-cards.md) |
| 检查许可证、版本和徽章事实 | [元数据与徽章](references/metadata-and-badges.md) |
| 查看完整索引 | [references/README.md](references/README.md) |

## 证据驱动的工作方式

- 已核实的研究材料包含 **252 个去重证据文档**，来源、读取状态和规则候选都保存在[研究与规则蒸馏](references/research-and-distillation.md)及其 fixture 中。
- Git Composer 把证据、规则和用户可见结论分开保存；主页只展示已经成立的使用路径。
- 研究抓取保持只读，公开 HTML fallback 会保留来源和读取状态，方便继续复核。

## 验证

在 skill 根目录运行与本轮改动匹配的检查：

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

这些检查覆盖结构、引用、UI 元数据、schema、fallback、四批 evidence、Git 决策门禁和离线评估。它们不等同于目标仓库的业务测试、远端 CI 或 GitHub 页面视觉验收。

## 安全与恢复

- 本地写入、提交、历史改写和远程写入是不同动作，默认先读后写。
- 不把 API token、私钥、cookie、私人配置、消息记录、数据库、媒体文件或本机状态放进公开仓库。
- 已共享的提交优先用 `git revert` 恢复；不要为了“整洁”强推或重写共享历史。
- 怀疑泄露凭据时先停止分享并轮换凭据，再处理仓库历史。

## 参与维护

先只读检查，再做一个范围清楚的改动，并附上准确的验证命令和结果。将成熟做法沉淀为流程时，使用[流程卡](references/procedure-cards.md)。

欢迎通过 [GitHub 仓库](https://github.com/Ray-Hola/git-composer)查看和讨论。

<details>
<summary>维护者参考</summary>

## 5 分钟只读快速开始

上面的 **60 秒开始**只读命令是最小入口；它不会改文件、提交或推送。

## 5 分钟安装与第一次改动

在确认目标目录没有要保留的本地改动后：

```sh
mkdir -p ~/.codex/skills
git clone https://github.com/Ray-Hola/git-composer.git ~/.codex/skills/git-composer
git -C ~/.codex/skills/git-composer status --short --branch
git -C ~/.codex/skills/git-composer pull --ff-only
```

已有本地改动时，`pull --ff-only` 会停止而不会覆盖文件；先检查再决定如何恢复。

## 任务菜单

- 体检：从[项目结构](references/project-structure.md)和仓库标准开始。
- 整理：按[治理与说明文件](references/governance-and-docs.md)做最小可回退改动。
- README：按[README 设计](references/readme-design.md)检查首屏、窄屏、明暗背景与链接。
- Git：按[Git 工作流](references/git-workflows.md)处理分支、提交、同步或恢复。
- 研究：按[研究与规则蒸馏](references/research-and-distillation.md)保持候选、证据和规则分层。

## 安全边界

默认先读后写；本地写入、历史改写、远程写入分别说明影响。不会猜仓库、分支、远程、许可证或支持版本；没有证据就写“未验证”或“待决定”。研究抓取只读，不创建 Issue/PR、不推送、不修改仓库设置。

## 研究计数

本地已核实语料是 **252 个去重文档**。候选范围、采样口径和第四批记录见 [`references/research-and-distillation.md`](references/research-and-distillation.md) 与 [`fixtures/corpus/github-public-doc-evidence-batch-4.json`](fixtures/corpus/github-public-doc-evidence-batch-4.json)。

## 精确维护检查

从 skill 根目录运行：

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

交付时使用[状态与变更报告模板](references/reporting-templates.md)；没有运行的命令必须标为“未验证”。

## 交付状态块

**预期结果**是一份可审查的状态报告：

```text
状态：已完成 / 部分完成 / 被阻塞
范围：<文件或远端对象>
改动：<一句话>
验证：<命令> → 通过 / 失败 / 未验证
证据：<路径、行号、提交或页面链接>
风险与恢复：<风险；如何回退或恢复>
未知：<仍待确认的事实；没有则写“无”>
下一步：<一条最有价值的动作>
```

## 验证与回退

文档或规则改动至少运行与范围对应的结构、引用和 diff 检查。未提交的改动只在确认路径和内容后回退；已提交的共享改动使用 `git revert`，然后重新运行相关检查。

</details>
