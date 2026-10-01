# Git Composer

面向新手的仓库整理与维护助手：先看清项目，再做小而可回退的改动，并把每一步的证据、验证和恢复方式说清楚。

## 5 分钟只读快速开始

以下步骤只读，不会改文件、提交、推送或修改远端设置。

```sh
git rev-parse --show-toplevel
git status --short --branch
git diff --stat
git log -1 --format='%h %s%n%b'
```

在干净仓库上，通常会看到项目根目录、类似 `## main...origin/main` 的分支行、空的 diff 统计，以及一条短提交哈希和标题：

```text
/你的项目根目录
## main...origin/main
<没有输出，或一行 diff 统计>
<短提交哈希> <最近提交标题>
```

分支名、上游和输出都以实际仓库为准；没有上游、存在改动或没有提交时，技能会原样说明，不把空输出解释成“检查通过”。看到不认识的文件或分支时，先停在只读检查。

然后把仓库交给 `$git-composer`，例如：

> 先只读检查这个仓库，告诉我最值得处理的 3 项，并给出证据、影响和验证命令。

如果需要 GitHub 页面或远端状态，再明确给出仓库 URL、分支和动作；技能会先确认目标，不把当前目录或默认分支当成目标。

## 5 分钟安装与第一次改动

在确认目标目录没有要保留的本地改动后安装：

```sh
mkdir -p ~/.codex/skills
git clone https://github.com/Ray-Hola/git-composer.git ~/.codex/skills/git-composer
```

已经安装过时，先检查再快进同步：

```sh
git -C ~/.codex/skills/git-composer status --short --branch
git -C ~/.codex/skills/git-composer pull --ff-only
```

`pull --ff-only` 遇到本地改动会停止，不会覆盖文件；如果目录不是 Git checkout，请重新执行 `git clone` 到一个新目录，再按宿主的 Skill 目录约定安装。安装完成后在 Codex 中直接说：

```text
帮我整理这个仓库：先保留现有改动，改善 README 和验证入口，再报告变更、证据、测试、风险和回滚。
```

预期结果是一个可审查的状态块：写明范围、实际文件、命令和退出结果、未验证维度、恢复路径以及下一步；没有运行的测试必须标为“未验证”。

## 任务菜单

| 你想做什么 | 可以这样说 | 主要入口 |
| --- | --- | --- |
| 体检 | “先只读检查仓库” | [仓库结构](references/project-structure.md)、[标准](references/repository-standards.md) |
| 整理 | “按优先级直接整理并验证” | [治理与说明](references/governance-and-docs.md) |
| 设计 README | “把首页改得更清楚、更好看” | [README 设计](references/readme-design.md) |
| 日常 Git | “帮我开分支/提交/同步/恢复” | [Git 工作流](references/git-workflows.md) |
| 研究规则 | “研究仓库实践并沉淀规则” | [研究与蒸馏](references/research-and-distillation.md) |
| 带练 | “教我完成这次修改” | [流程卡](references/procedure-cards.md) |

## 你会看到的结果

每次交付都尽量包含下面这个状态块。它让你一眼知道改了什么、检查到哪里、还缺什么。

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

### 证据标签

- **已核实**：由本地文件、命令输出或固定链接直接支持。
- **已修正**：本轮改动后重新检查通过。
- **待决定**：需要用户选择，例如许可证、发布范围或风格偏好。
- **未验证**：缺少运行环境、权限、网络或实际预览；不能写成“通过”。
- **不适用**：说明为什么不适用，不留空白。

## 安全边界

- 默认先读后写；本地写入、历史改写、远程写入分别说明影响。
- 不猜仓库、分支、远程、许可证或支持版本；目标不明确就停在可审查的准备结果。
- 保留已有未提交和暂存意图；不 stash、覆盖、批量格式化或清理无关文件。
- 推送前检查实际文件和历史中的密钥、凭据、私人配置及本地数据；忽略规则不能替代检查。
- 不 force-push、不重写共享历史、不改远端配置或分支保护，除非用户明确授权。
- 研究任务只读；“10k+”表示至少 10,000 个去重候选项目记录，不表示已阅读 10,000 个项目。
- 对已经写入的改动，交付中同时给出起始基线、实际差异、检查结果和恢复路径；没有远端回执就写“未验证”，不把本地提交当成已推送。

## 验证与回退

文档或规则改动至少运行与范围对应的结构、引用和 diff 检查。若命令失败，保留失败输出的摘要和缺口；不要用“命令已执行”代替“结果通过”。

```sh
git diff --check
git status --short --branch
git diff --stat
```

未提交的改动只在确认路径和内容后回退。已提交的共享改动使用 `git revert`，先核对目标提交、分支和远端状态；回退提交本身也要重新验证。README 的链接和排版检查通过，不等于目标项目的业务测试、远端 CI 或实际视觉预览通过。

## 研究计数（当前事实）

本地已核实语料是 **252 个去重文档**（见 [`batch 1`](fixtures/corpus/github-public-doc-evidence-batch.json)、[`batch 2`](fixtures/corpus/github-public-doc-evidence-batch-2.json)、[`batch 3`](fixtures/corpus/github-public-doc-evidence-batch-3.json) 和 [`batch 4`](fixtures/corpus/github-public-doc-evidence-batch-4.json)）。第四批记录 147 次尝试、100 个成功文档和 47 个排除路径；52 次 `full`、48 次 `partial`，且固定 SHA/内容哈希均未暴露。**10,000 个候选项目目标仍为 pending**；候选项目数、文档数和 10k-star 分层不能互换。当前材料没有证据支持“已读取 10k 项目”的说法。

## 精确维护检查

在修改技能本身后，从技能根目录运行：

```sh
python3 scripts/verify_skill.py
python3 scripts/test_research_schema.py
python3 scripts/test_public_html_fallback.py
python3 scripts/test_evidence_batch.py
python3 scripts/test_evidence_batch_two.py
python3 scripts/test_evidence_batch_three.py
python3 scripts/test_evidence_batch_four.py
python3 scripts/evaluate_skill.py
```

这些检查覆盖结构、引用、UI 元数据、schema、回退路径、四批证据、离线计划确定性、分层样例、留出集溯源和安全门槛。它们不证明任意目标仓库的业务测试、远端工作流或 README 的实际视觉效果；README 改动还要按 [设计指南](references/readme-design.md) 做宽屏、窄屏、明暗背景预览。

## 常见提示

- “只读体检，先不要改文件。”
- “按问题—证据—影响—处理—验证报告。”
- “保留我的未提交改动，只改 README 和维护说明。”
- “准备提交并推送到这个明确的远程和分支，先做隐私门禁。”
- “如果无法验证，请标为未验证并说明缺口。”
- “把这套做法整理成可复用流程卡。”

## 深入阅读

- [项目结构](references/project-structure.md)
- [治理与说明文件](references/governance-and-docs.md)
- [Git 工作流](references/git-workflows.md)
- [README 设计](references/readme-design.md)
- [研究与规则蒸馏](references/research-and-distillation.md)
- [流程卡](references/procedure-cards.md)
- [状态与变更报告模板](references/reporting-templates.md)
- [元数据、许可证与徽章检查](references/metadata-and-badges.md)

维护建议：每次改规则后，先更新对应参考文件，再运行上面的整套检查，并把“已核实 / 未验证 / 待决定”写进交付状态块。
