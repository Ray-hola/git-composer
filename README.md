<p align="center">
  <img src="assets/git-composer-mark.svg" width="88" alt="Git Composer mark" />
</p>

<h1 align="center">Git Composer</h1>

<p align="center"><strong>Make a repository easier to understand, change, verify, and recover.</strong><br />
让仓库更容易看懂、修改、验证与恢复。</p>

<p align="center">
  <a href="https://github.com/Ray-Hola/git-composer"><img src="https://img.shields.io/badge/GitHub-view%20repository-181717?logo=github&logoColor=white" alt="View the GitHub repository" /></a>
  <a href="https://github.com/Ray-Hola/git-composer"><img src="https://img.shields.io/github/stars/Ray-Hola/git-composer?style=flat&label=stars" alt="GitHub stars" /></a>
  <a href="#verification"><img src="https://img.shields.io/badge/status-local%20checks%20documented-2563eb" alt="Status: local checks documented" /></a>
</p>

> **A beginner-friendly Git and README companion.** Start with evidence, make the smallest useful change, and leave a clear path back.
> **面向新手的 Git 与 README 助手。** 先看证据，再做小而有用的改动，并留下清楚的恢复路径。

<p align="center"><a href="#60-second-first-check">60-second first check</a> · <a href="#capabilities">Capabilities</a> · <a href="#docs">Docs</a> · <a href="#safety-and-evidence">Safety & evidence</a></p>

## 60-second first check

Read-only commands; they do not edit files, commit, push, or change remotes.

```sh
git rev-parse --show-toplevel
git status --short --branch
git diff --stat
git log -1 --format='%h %s%n%b'
```

Then ask for a focused pass:

```text
Use $git-composer to inspect this repository first. Keep existing changes, improve the README and verification entry points, then report changes, evidence, checks, risks, and recovery.
```

Expected output: a status block with scope, files, commands and exit results, evidence, recovery, unknowns, and one next step. Unrun checks stay marked **unverified**.

## Capabilities

- **Read before write** — establish the root, branch, diff, history, runtime, and current conventions before proposing edits.
- **Small, reversible improvements** — shape a useful README, project structure, contribution notes, or Git workflow without inventing releases, licenses, CI, or support promises.
- **Evidence-led handoff** — report what was verified, what was changed, what remains unknown, and how to recover; keep research counts separate from sampled evidence.

## Docs

| Need | Start here |
| --- | --- |
| Understand the repository shape | [Project structure](references/project-structure.md) |
| Define maintainable rules and docs | [Governance & docs](references/governance-and-docs.md) |
| Design a useful README | [README design](references/readme-design.md) |
| Handle branches, commits, sync, and recovery | [Git workflows](references/git-workflows.md) |
| Gate Git writes, remotes, releases, and research | [Decision gates](references/decision-gates.md) |
| Turn research into reusable rules | [Research & distillation](references/research-and-distillation.md) |
| Convert evidence into a procedure | [Procedure cards](references/procedure-cards.md) |
| Check metadata, badges, and license facts | [Metadata & badges](references/metadata-and-badges.md) |
| Use the complete reference map | [References index](references/README.md) |

## Safety and evidence

- Local writes, history changes, and remote writes are separate actions; default work is local and reviewable.
- Existing uncommitted or staged intent is preserved. No stash, force-push, shared-history rewrite, remote configuration change, or branch protection change is assumed.
- Research work is read-only. **252 verified evidence documents** are present across the four recorded batches; **10,000 candidate projects remain pending**. A candidate count, document count, and 10k-star tier are different facts.
- The current materials do not establish a license, published releases, CI, user count, performance result, or screenshot. License status is **undecided** until the project owner chooses one.
- Public HTML fallback and batch fixtures preserve retrieval status, exclusions, and provenance instead of turning partial reads into claims.

## Verification

From the skill root, run the checks that match the change:

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

These checks cover structure, references, UI metadata, schema, fallback behavior, four evidence batches, offline evaluation, and safety gates. A passing local check does not claim remote CI or target-repository business tests.

## Contributing

Start with a read-only inspection, make a focused change, and include the exact verification command and result. Use the [procedure cards](references/procedure-cards.md) when turning a proven pattern into a reusable workflow. The [GitHub repository](https://github.com/Ray-Hola/git-composer) is the public discussion and contribution entry point.

## Security

Do not paste credentials, private configuration, or local user data into issues or examples. For a suspected secret exposure, stop sharing the material and use the repository's private GitHub contact path before opening a public report. The safety rules and recovery gates live in [SKILL.md](SKILL.md).

## Releases and status

No published release or CI status is asserted here. The status badge above means the documented local checks are the current source of truth. Watch the [GitHub repository](https://github.com/Ray-Hola/git-composer) for owner-confirmed releases and changes; the project license remains undecided.

## Restore and maintain

For an uncommitted change, review the path and diff, then restore only the intended file with your normal Git tooling. For a shared committed change, identify the exact commit and use `git revert`; re-run the relevant checks afterward. Keep this README, the reference index, and the linked reference pages aligned when rules change.

<details>
<summary>维护者速查 / Maintainer reference</summary>

## 5 分钟只读快速开始

同上面的 **60-second first check**；这组命令只读。

## 5 分钟安装与第一次改动

```sh
mkdir -p ~/.codex/skills
git clone https://github.com/Ray-Hola/git-composer.git ~/.codex/skills/git-composer
git -C ~/.codex/skills/git-composer status --short --branch
git -C ~/.codex/skills/git-composer pull --ff-only
```

已有本地改动时，`pull --ff-only` 会停止而不会覆盖文件；先检查再决定如何恢复。

## 任务菜单

- 体检：先读 [project structure](references/project-structure.md) 与 [repository standards](references/repository-standards.md)。
- 整理：按 [governance & docs](references/governance-and-docs.md) 做最小可回退改动。
- 设计 README：按 [README design](references/readme-design.md) 检查首屏、窄屏、明暗背景与链接。
- 日常 Git：按 [Git workflows](references/git-workflows.md) 处理分支、提交、同步或恢复。
- 研究规则：按 [research & distillation](references/research-and-distillation.md) 保持候选、证据和规则分层。

## 安全边界

默认先读后写；本地写入、历史改写、远程写入分别说明影响。不会猜仓库、分支、远程、许可证或支持版本；没有证据就写 **未验证** 或 **待决定**。研究抓取只读，不创建 Issue/PR、不推送、不修改仓库设置。

## 研究计数

本地已核实语料是 **252 个去重文档**；**10,000 个候选项目目标仍为 pending**。第四批及其累计结果见 [`fixtures/corpus/github-public-doc-evidence-batch-4.json`](fixtures/corpus/github-public-doc-evidence-batch-4.json)。候选项目数、文档数和 10k-star 分层不能互换。

## 精确维护检查

从技能根目录运行：

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

`references/reporting-templates.md` 定义交付状态块；没有运行的命令必须标为 **未验证**。

</details>

### 交付状态块

**预期结果**是一个可审查的状态块：

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

### 验证与回退

文档或规则改动至少运行与范围对应的结构、引用和 diff 检查。未提交的改动只在确认路径和内容后回退；已提交的共享改动使用 `git revert`，然后重新运行相关检查。
