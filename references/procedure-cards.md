# 新手仓库管理流程卡

这组流程卡来自 2026-09-30 UTC 的第一批公开一手文档证据：5 个项目元数据记录、22 个实际读取且去重的文档。它们是候选规则，不是所有仓库都必须采用的流程；当前 10,000 个候选项目目标仍处于 pending，不能用文档数代替项目数。机器可读来源和计数见 [`fixtures/corpus/github-public-doc-evidence-batch.json`](../fixtures/corpus/github-public-doc-evidence-batch.json)。

## 改文件前先画出项目地图

适用于包含多个包、crate、playground 或生成产物的项目。先读根目录 manifest/workspace 文件和结构说明，找到公开入口、最近的测试以及生成文件的来源，再把改动放进拥有该行为的最小包或 crate。CLI、Vite、Ruff 的材料都把职责边界写进结构或 manifest；FastAPI 的 `pyproject.toml` 还明确了构建后端、可选依赖和 console entry point。

验证时确认改动路径被结构说明或 manifest 解释，并从文档所示根目录运行聚焦检查。若目录和说明冲突，暂停搬动文件，记录差异，依照正在使用的 manifest，并请维护者确认哪个来源有效。只有一个入口的小脚本不需要先搭 monorepo。

证据：[CLI project layout](https://github.com/cli/cli/blob/fc4b137cdef0a6bd28fd461b7cf9c84a5812a8cd/docs/project-layout.md)、[Vite workspace](https://github.com/vitejs/vite/blob/cf5c0288d526824aead1b24e977400f13c527927/pnpm-workspace.yaml)、[Ruff workspace](https://github.com/astral-sh/ruff/blob/a4e7c20ca0d42f5cb41485210193548b98ee39c2/Cargo.toml)、[FastAPI packaging](https://github.com/fastapi/fastapi/blob/33d411dbc3236275dd64d200bfe18d5d60a49b2e/pyproject.toml)。

第三批补充：先检查 `pyproject.toml`、`Cargo.toml`、`go.mod` 或 `package.json` 的 workspace/package 边界和生成入口；它们常比目录名更准确。反例是 Prometheus README 明确说明主仓库是独立程序而非稳定库，不能因为能 import 就把内部包当公共 API。若结构文档很长而只完成部分读取，把结论标为未完整验证并先限定改动范围。

## 写代码前检查贡献入口

适用于外部 issue、feature 或 pull request。先查重复 issue 和关联 PR，再读标签与 acceptance criteria。CLI 只接受带 `help wanted` 和明确验收标准的外部 PR；Ruff 将 `good first issue`、`help wanted`、`needs-design` 和 `needs-decision` 区分处理；Vite 要求新功能配测试并控制 PR 范围。

验证时让 PR 链接 issue、保持在验收范围内，并包含要求的测试。没有标准、标记为核心范围或需要设计共识时，停止实现路径，改为讨论或询问维护者。内部已分配的私有任务可以遵循自己的授权流程。

证据：[CLI contributing](https://github.com/cli/cli/blob/fc4b137cdef0a6bd28fd461b7cf9c84a5812a8cd/.github/CONTRIBUTING.md)、[Vite contributing](https://github.com/vitejs/vite/blob/cf5c0288d526824aead1b24e977400f13c527927/CONTRIBUTING.md)、[Ruff contributing](https://github.com/astral-sh/ruff/blob/a4e7c20ca0d42f5cb41485210193548b98ee39c2/CONTRIBUTING.md)。

## 从 CI 推导本地检查

适用于 workflow 写出了路径过滤、运行时矩阵或组件任务的项目。先读触发条件和过滤路径，再运行覆盖改动范围的最小本地矩阵，补齐仓库命名的 formatter、typecheck、test 和 build 命令，并记录环境版本。CLI、FastAPI、Vite、Ruff 和 Awesome 都把不同的检查入口或触发范围写在配置中。

验证时逐项对应改动组件和本地命令；跳过的操作系统或依赖组合要明确写成未验证。缺少某个本地环境时保留失败输出，运行最接近的支持检查，并报告缺失维度。CI 配置本身不能证明远端分支保护、部署或秘密凭据任务已经成功。

证据：[CLI CI](https://github.com/cli/cli/blob/fc4b137cdef0a6bd28fd461b7cf9c84a5812a8cd/.github/workflows/go.yml)、[FastAPI CI](https://github.com/fastapi/fastapi/blob/33d411dbc3236275dd64d200bfe18d5d60a49b2e/.github/workflows/test.yml)、[Vite CI](https://github.com/vitejs/vite/blob/cf5c0288d526824aead1b24e977400f13c527927/.github/workflows/ci.yml)、[Ruff CI](https://github.com/astral-sh/ruff/blob/a4e7c20ca0d42f5cb41485210193548b98ee39c2/.github/workflows/ci.yaml)、[Awesome workflow](https://github.com/sindresorhus/awesome/blob/bc98e517ddca672f55f9857d714fc3ea3c3540b2/.github/workflows/main.yml)。

第三批补充：将 workflow 的路径过滤、Makefile/tox/pytest 命令、workspace 矩阵和可复用 job 一起读，才能知道本地检查覆盖什么。反例是一个只负责调用生成配置的薄 workflow，不能据它推断完整矩阵；文档路径被 filter 排除时也不要声称 CI 会验证它。若只能部分读取大 workflow，记录未覆盖的 job，再请求一次受控 CI 结果或维护者确认。

## 发布前先演练

适用于准备打包、打 tag 或发布的改动。先读 release 文档并找出 approval/environment gate，再分开准备版本、changelog、生成文件和 lockfile，最后使用项目提供的 staging 或 local 模式。CLI 有 staging/local release，Vite 先生成 release PR 再等待检查和环境批准，Ruff 先更新版本、changelog、crate README 和 lockfile，FastAPI 由 published release 事件触发 build/publish。

验证时检查产物、版本、changelog 和目标提交一致；发布成功后再核对包、tag 和 release。准备阶段失败可以修复后重跑；如果不可变包已发布但 tag 或 release 创建失败，先确认包状态再重试。演练本身不是创建远程发布的授权。

证据：[CLI releasing](https://github.com/cli/cli/blob/fc4b137cdef0a6bd28fd461b7cf9c84a5812a8cd/docs/releasing.md)、[Vite release guidance](https://github.com/vitejs/vite/blob/cf5c0288d526824aead1b24e977400f13c527927/CONTRIBUTING.md)、[Ruff release script](https://github.com/astral-sh/ruff/blob/a4e7c20ca0d42f5cb41485210193548b98ee39c2/scripts/release.sh)、[FastAPI publish workflow](https://github.com/fastapi/fastapi/blob/33d411dbc3236275dd64d200bfe18d5d60a49b2e/.github/workflows/publish.yml)。

第三批补充：在 release 文档旁检查 CHANGELOG、Towncrier 片段或生成脚本，确认版本输入、生成文件和目标提交如何关联。attrs 的 `pyproject.toml` 将 `changelog.d` 片段接入发布文档，说明“改完代码再补发布记录”可能是不完整流程。反例是只做本地版本号或 changelog 草稿，不应触发 publish；若已有不可变包而后续 tag 失败，先盘点现状再按项目恢复说明重试。

## 从源文件重新生成输出

适用于手册、schema、changelog、snapshot 或 package/crate 元数据由工具生成的项目。找到贡献或 release 文档中的生成命令，先改源文件，再运行生成器并检查 diff，最后运行聚焦测试。CLI 从命令源码生成手册；Ruff 要求更新生成文档和代码，并用 mdtest/snapshot 验证规则。

如果只改了生成文件或 snapshot 漂移，先撤销生成物的孤立改动，重新运行记录的生成器，再审查结果，不要一键接受全部 snapshot。手写 README 或一次性文本不自动属于生成产物。

证据：[CLI layout](https://github.com/cli/cli/blob/fc4b137cdef0a6bd28fd461b7cf9c84a5812a8cd/docs/project-layout.md)、[CLI release](https://github.com/cli/cli/blob/fc4b137cdef0a6bd28fd461b7cf9c84a5812a8cd/docs/releasing.md)、[Ruff contributing](https://github.com/astral-sh/ruff/blob/a4e7c20ca0d42f5cb41485210193548b98ee39c2/CONTRIBUTING.md)。

## 把 curated list 当作内容贡献

适用于资源清单或 Markdown 索引。Awesome 的 checklist 要求准备好的 PR、复核其他开放 PR、标题和描述格式、分类位置、lowercase slug、`#readme` 链接以及 `awesome-lint`。workflow 只在 `readme.md` 变化时触发，并由脚本提取新链接、clone 目标仓库后运行 linter。

验证时逐项完成 checklist、确认分类和链接，再运行 linter。若链接无法 clone 或内容不合规，修复链接/条目并重跑；不要借机扩展无关清理。这套规则不代表普通代码库的 release 或测试流程。

证据：[Awesome contributing](https://github.com/sindresorhus/awesome/blob/bc98e517ddca672f55f9857d714fc3ea3c3540b2/contributing.md)、[PR template](https://github.com/sindresorhus/awesome/blob/bc98e517ddca672f55f9857d714fc3ea3c3540b2/pull_request_template.md)、[workflow](https://github.com/sindresorhus/awesome/blob/bc98e517ddca672f55f9857d714fc3ea3c3540b2/.github/workflows/main.yml)、[repo linter](https://github.com/sindresorhus/awesome/blob/bc98e517ddca672f55f9857d714fc3ea3c3540b2/.github/workflows/repo_linter.sh)。

## 第二批候选流程卡

以下六张卡来自第二批 2026-09-30 UTC 的 30 个公开一手文档。机器可读字段、精确计数和 URL 在 [`fixtures/corpus/github-public-doc-evidence-batch-2.json`](../fixtures/corpus/github-public-doc-evidence-batch-2.json)；第二批没有可从 HTML 验证的固定 SHA，不能把分支 URL 当作提交快照。

### 先读项目入口再实现

`claim_kind`: `cross_project_procedure`；`verification_level`: `observed_public_html`。适用于外部改动和有贡献协议的成熟项目。先读 CONTRIBUTING 及其链接的 community/developer guide，确认协议、tracker、标签、测试和范围；验证 PR 或 issue 已进入文档规定的路径并运行入口要求的检查。已有维护者明确分配流程或只做本地一次性实验时不套用。若入口转到另一个 tracker 或社区指南，停止编辑，记录转向并询问维护者。

### 按所有权和 tracker 路由

`claim_kind`: `cross_project_procedure`；`verification_level`: `cross_project_public_policy`。适用于 SIG、team、triager 或独立 tracker 管理的子系统。把改动映射到 owner，检查标签和设计门槛，并链接 canonical record；验证 owner、标签或 tracker 与改动路径相符。文档小修可以不走子系统路由；所有权含糊或需要设计决策时，暂停并请 owner/triager 指派。

### 保持漏洞报告在安全通道

`claim_kind`: `safety_gate`；`verification_level`: `cross_project_public_policy`。怀疑可利用漏洞、危险模型、凭据或敏感复现时，先读项目安全政策并使用私密渠道，不在公开 issue 放 exploit 细节；验证 acknowledgement 和升级路径，不把策略声明当成运行结果。普通且明确排除在安全范围外的 bug 可走公开 tracker。若信息已泄露，停止扩散，按政策升级并轮换暴露凭据；若政策排除该报告，转到指定公共路径。

### 追溯 CI 的 source of truth

`claim_kind`: `cross_project_procedure`；`verification_level`: `observed_public_html`。适用于矩阵、路径过滤、生成 job、Prow、可复用 workflow 或 label 触发的项目。读 trigger/filter，继续追到生成配置或 reusable workflow，再运行覆盖改动组件的最小本地命令并记录跳过维度。验证每个改动路径对应命名 job，区分“配置声明”和“远端运行成功”。若矩阵源不可用，报告未验证维度并请求 CI/维护者；项目规定需要 rebase 或重新生成时按其流程恢复。

### 检查发布授权并演练门槛

`claim_kind`: `release_safety_gate`；`verification_level`: `cross_project_public_policy`。准备版本、tag、包或 release 时，先读 release process，找 authorized role、staging、签名和 Go-No-Go 门槛，在 dry-run/staging 中准备版本、changelog 和产物，审批后才 tag、签名、推广或 publish。只改本地版本或 changelog 不触发发布卡。验证 staged artifact、版本、changelog 和目标提交一致；若已有部分不可变发布，先盘点包、tag、release 状态，再由 owner 确认恢复路径。

### 把模板和 workflow 当作契约

`claim_kind`: `repository_contract`；`verification_level`: `observed_public_html`。提交 issue/PR 或依赖特定 workflow 时，检查模板字段、事件、路径过滤、权限和 action pin，确保改动路径真的触发目标检查，再运行聚焦本地检查。自由格式 issue、手动 dispatch 或被过滤的文档路径是反例。验证字段完整、触发条件匹配并记录配置 pin；未触发时先查 event/path filter，必要时修正范围或请维护者重跑。

## 第四批候选流程卡

以下四张卡来自第四批 2026-10-01 UTC 的 100 个去重一手文档，覆盖较小的成熟库、CLI 和成熟 monorepo。固定提交 SHA 与内容摘要均未由本次 raw webfetch 暴露，因此不能把分支 URL 当成提交快照；机器可读计数、失败清单和缺失哈希原因见 [`fixtures/corpus/github-public-doc-evidence-batch-4.json`](../fixtures/corpus/github-public-doc-evidence-batch-4.json)。它们仍是候选规则，10,000 个候选项目目标保持 pending。

### 先按根 manifest 选择工具链

适用于多包仓库，或根目录存在 `package.json`、`pyproject.toml`、`go.mod`、`Cargo.toml` 的 CLI/库。先读根 manifest，使用其中声明的包管理器、workspace 过滤器和脚本，再把修改和检查限制在 manifest 定义的包边界。pnpm、Yarn、Svelte、React、pip 和 Nushell 的材料都把脚本、workspace、依赖组或包边界写入根文件。单文件脚本没有 manifest 时不套用；manifest 与目录冲突时暂停移动文件，记录差异并确认哪个来源有效。

验证时记录 manifest 路径，并运行覆盖改动包的最小声明检查。证据：[pip metadata](https://raw.githubusercontent.com/pypa/pip/main/pyproject.toml)、[pnpm root package](https://raw.githubusercontent.com/pnpm/pnpm/main/package.json)、[Svelte root package](https://raw.githubusercontent.com/sveltejs/svelte/main/package.json)、[React root package](https://raw.githubusercontent.com/facebook/react/main/package.json)、[Nushell workspace](https://raw.githubusercontent.com/nushell/nushell/main/Cargo.toml)。

### 发布记录与版本输入一起准备

适用于将要打包、打 tag 或发布的改动。先读 changelog、news 或 release-fragment 约定，在项目规定的源格式中写入记录，再运行声明的检查并审查生成或 staged diff；准备阶段不等于获得 publish 授权。pip、Packaging、Task、Yarn 和 Vue 都把版本变更留在可追溯的发布记录中。没有发布动作的本地实验不触发这张卡；已有不可变产物时，先盘点包、tag、release 状态再重试。

验证时确认记录覆盖改动包，并与目标提交和待发布版本一致。证据：[pip NEWS](https://raw.githubusercontent.com/pypa/pip/main/NEWS.rst)、[Packaging changelog](https://raw.githubusercontent.com/pypa/packaging/main/CHANGELOG.rst)、[Task changelog](https://raw.githubusercontent.com/go-task/task/main/CHANGELOG.md)、[Yarn changelog](https://raw.githubusercontent.com/yarnpkg/berry/master/CHANGELOG.md)、[Vue changelog](https://raw.githubusercontent.com/vuejs/core/main/CHANGELOG.md)。

### 大范围功能先走 triage 或 RFC

适用于跨包、面向用户或需要设计共识的功能。先读项目贡献指南中的 issue 标签、roadmap、RFC 和测试计划，搜索现有讨论，再在 canonical issue/RFC 中确认范围后实现。Nushell、Starship、Svelte、Storybook 和 TypeScript 都将 triage、设计讨论或贡献入口写入一手指南。已经分配的窄范围维护修复不套用；如果提案不在当前优先级或没有 owner，停止实现并请求维护者指派。

验证时让 PR 链接 issue/RFC，并满足贡献指南要求的检查。证据：[Nushell contributing](https://raw.githubusercontent.com/nushell/nushell/main/CONTRIBUTING.md)、[Starship contributing](https://raw.githubusercontent.com/starship/starship/master/CONTRIBUTING.md)、[Svelte contributing](https://raw.githubusercontent.com/sveltejs/svelte/main/CONTRIBUTING.md)、[Storybook contributing](https://raw.githubusercontent.com/storybookjs/storybook/next/CONTRIBUTING.md)、[TypeScript contributing](https://raw.githubusercontent.com/microsoft/TypeScript/main/CONTRIBUTING.md)。

### 涉及漏洞时使用私密通道

适用于可能暴露可利用漏洞、凭据或敏感复现的报告。先读 `SECURITY.md`，使用项目指定的私密渠道，避免把 exploit 细节放入公开 issue 或 PR；记录政策和 acknowledgement 路径，不把政策声明当成修复已上线。普通且明确不在安全范围内的 bug 可按公开 tracker 流程处理；信息已公开时停止扩散，按政策升级并轮换暴露凭据。

验证时保留安全政策 URL 和升级路径。证据：[Storybook security](https://raw.githubusercontent.com/storybookjs/storybook/next/SECURITY.md)、[TypeScript security](https://raw.githubusercontent.com/microsoft/TypeScript/main/SECURITY.md)。
