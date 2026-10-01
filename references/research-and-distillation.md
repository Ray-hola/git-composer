# 研究语料与规则蒸馏

用于用户要求对标大量 GitHub 仓库、研究结构/协作/发布实践，或把观察沉淀为可安装的代理规则时。此流程是分阶段的研究设计，不声称已经读取某个数量的仓库。

## 目标与分层

将“10k+ 语料”拆成可审计的层次：

1. **候选全集（10,000+）**：只保存公开仓库元数据、分层来源和快照标识。
2. **浅层样本（约 2,000）**：读取 README、贡献/安全/治理说明、Issue/PR 模板、CODEOWNERS、CHANGELOG、工作流与架构/运维文档。
3. **深层样本（约 500）**：补充近期 Issue、PR/评审、提交、发布、标签和自动化运行证据。
4. **金标准与留出集（各约 100–200）**：人工复核规则质量；留出集只用于验证，不参与规则拟合。

候选全集不是深读数量。每一层记录纳入、排除、失败和替换原因，避免把搜索结果数写成已阅读数。

本技能中 **10k+** 的精确定义是至少 10,000 个按 `owner/name` 和 fork lineage 去重的候选项目记录；后续证据文件可以多于项目记录，不能把证据单元数写成项目数。**10k-star stratum** 则专指星标数至少 10,000 的采用/热度分层，它不是 10k+ 语料规模。当前没有已抓取的 10k+ 语料库。

## 候选、证据和规则

使用 [`schemas/research-distillation-records.schema.json`](../schemas/research-distillation-records.schema.json) 记录三类对象：

- `corpus_candidate`：仓库身份、默认分支、分层、查询来源、快照提交和纳入状态。
- `evidence_record`：来源路径/URL/提交、证据类别、观察或声明、内容哈希、许可/隐私审查与置信度。
- `rule_candidate`：触发语句、适用/排除条件、事实收集、允许工具、副作用级别、确认门槛、验证、停止条件和证据引用。

规则只引用已保存的证据记录；“文件声明”“配置存在”和“实际运行结果”分开标注。不要复制仓库原文作为规则正文，使用短释义、固定提交或版本链接和采样日期保留可追溯性。

离线规划由 [`scripts/build_corpus.py`](../scripts/build_corpus.py) 负责，默认只输出确定性的分层计划和 manifest schema 摘要；`--network` 才允许公开 GitHub API 读取。 [`references/ranking-policy.yml`](ranking-policy.yml) 调整权重和分层比例， [`scripts/evaluate_skill.py`](../scripts/evaluate_skill.py) 汇总结构、schema、规划确定性和安全样例检查。

Phase 3A 的 [`scripts/smoke_github_api.py`](../scripts/smoke_github_api.py) 只对成熟仓库案例中的五个公开项目做元数据、默认分支提交、两页提交元数据分页、ETag 重验证和预期 404 失败探针；必须显式传 `--network`，不读取 README/Issue/PR 正文，不写入 GitHub。它生成的是小型 smoke 报告，不是语料库。

## 分层采样

按语言/生态、项目类型、组织与个人、仓库年龄、最近活动、许可证、归档/镜像/分叉状态、星标分位和发布/CI 情况分层。星标只表示采用信号，不等于质量；星标阈值应在语言和年龄层内比较。

GitHub Search API 单个查询最多返回 1,000 条结果，查询最多检索 4,000 个匹配仓库；已认证搜索通常每分钟 30 次，代码搜索每分钟 10 次。普通已认证 REST 请求通常每小时 5,000 次。必须按语言、星标区间、主题和时间区间拆分查询、去重、缓存并保存覆盖率；不要用一次 `sort=stars` 查询声称得到完整全集。

GraphQL 连接使用游标分页，每次 `first`/`last` 为 1–100；每页保存游标和请求时间。仓库内容目录超过 1,000 项时使用 Git Trees API；大于 100 MB 的文件不进入普通内容抓取。工作流、README、模板和治理文件优先于二进制与生成物。

GH Archive 或类似事件数据可补充活动、Issue、PR 和发布时间序列，但它是事件来源，不替代仓库文件快照；活动证据仍要与目标提交关联。

## 质量与规则门槛

对仓库质量和规则强度分开评分。仓库质量可按 0–4 评估文档入口、维护活跃度、治理清晰度、发布/自动化、可复现性、安全/支持和首次使用体验。规则强度评估独立仓库数量、覆盖分层、直接证据、可移植性、维护成本、风险和例外。

只有在多个独立仓库、至少两个分层中重复出现，且有清晰证据时，模式才升级为默认规则。单一大型仓库的做法保留为示例或例外。安全规则可以用较少样本，但必须有明确的风险与停止条件。

## 蒸馏与安装

先用确定性解析器提取路径、标题、链接、命令、YAML 触发器、模板字段、版本和时间，再进行聚类或模型辅助归纳。每条候选规则必须能回答：何时触发、先读什么事实、可用哪些工具、何时需要确认、如何验收、哪些情况停止。人工复核通过后，才把短规则放进 `SKILL.md`，把长证据和案例留在参考文件。

写入或远程动作均记录 `side_effect_level`。`local_destructive`、`history_rewrite` 和 `remote_write` 必须有明确确认门槛；不确定目标、敏感数据或权限时停止并报告缺口。研究抓取阶段只读，不创建 Issue/PR、不推送、不修改仓库设置。

## 研究交付

交付至少包含：覆盖范围和缺失率、样本分层、快照日期、来源提交、质量/规则评分、被拒绝模式及原因、候选规则与证据引用、金标准/留出集结果。将“抓取成功”“文件存在”“规则可移植”“运行通过”分别报告，不合并成一个“全部验证”。

## 第一批一手文档证据

当前第一批使用 webfetch 只读读取 CLI、Python 库、JavaScript monorepo、Rust 工具和 curated list 的 22 个去重公开文档，分别记录在 [`fixtures/corpus/github-public-doc-evidence-batch.json`](../fixtures/corpus/github-public-doc-evidence-batch.json)。报告明确区分 5 条元数据记录和 22 次实际文档读取，并把 10,000 个去重候选项目目标保持为 `pending`。从这些证据提炼出的新手流程卡见 [`references/procedure-cards.md`](procedure-cards.md)；它们仍是候选规则，直到更广泛的分层样本重复验证。

## 第二批成熟项目一手文档证据

2026-09-30 UTC 的第二批通过 webfetch 只读读取 Kubernetes、Rust、Django、Node.js 和 PyTorch 的贡献、治理、安全、发布、CI 及工作流资料，共 5 条元数据记录和 30 个去重文档。机器可读报告在 [`fixtures/corpus/github-public-doc-evidence-batch-2.json`](../fixtures/corpus/github-public-doc-evidence-batch-2.json)，每条记录保存一手 URL、默认分支和内容短释义；本批 GitHub HTML 没有暴露可验证的完整提交 permalink，因此固定 SHA 数为 0，URL 中有 26 条 GitHub 分支路径和 4 条官方非 GitHub 页面，并明确记录 `not_obtainable_from_public_html`。这不是把分支页面误写成快照，也不把网页四舍五入的星标显示当作精确 API 数值。

六张新增流程卡仍标为候选，且分别带有 `claim_kind` 和 `verification_level`：先读项目入口、按所有权和 tracker 路由、保持安全报告私密、追溯 CI source of truth、检查发布授权并演练、把模板和 workflow 当作契约。它们描述的是文档中声明的流程，不等价于远端运行成功；验证和恢复步骤保留在 [`references/procedure-cards.md`](procedure-cards.md)。10,000 个去重候选项目目标继续是 `pending`，30 个文档不能替代项目记录数量。

## 第三批 100 个文档：小型库、CLI 与成熟 monorepo

第三批在 2026-09-30 UTC 通过 public raw GitHub webfetch 读取了 25 个项目的 100 个去重一手文档，覆盖 Python CLI/库、Rust CLI/库、Go 模块、JavaScript monorepo 和 Deno/Clippy 等工具。它们集中补充四类新手可执行事实：manifest 或 workspace 如何划分包边界，贡献入口如何约束改动，测试/Makefile/workflow 如何选择检查，CHANGELOG 或发布工具如何保存版本决定。机器可读记录见 [`fixtures/corpus/github-public-doc-evidence-batch-3.json`](../fixtures/corpus/github-public-doc-evidence-batch-3.json)。

本批不是把探测数当成阅读数：130 个 URL 探测中只有 100 个成功且去重的文档计入，30 个失败或不可用路径被排除；54 个小于等于 200 行的读取标为 `full`，46 个较大文件标为 `partial`。webfetch 没有提供可验证的内容哈希，因此每条记录都写明 `content_hash_status=not_exposed_by_webfetch`；分支 URL 也没有冒充固定提交。累计已验证去重文档为 152（前两批 52 + 本批 100），10,000 个实际文档/项目目标仍为 `pending`，搜索命中、元数据和文档片段均不替代该目标。

第三批支持对已有流程卡作三处具体增强：先从 `pyproject.toml`、`Cargo.toml`、`go.mod` 或 `package.json` 确认 workspace/package 边界；将 workflow、Makefile、tox、pytest 或矩阵配置映射到改动路径并记录未覆盖维度；发布前检查 Towncrier/CHANGELOG 等版本输入和生成链。它也提供反例：根 README 可能明确说明某个 monorepo 不是可复用库，路径过滤可能跳过文档改动，工作流可能只是包装器而非 job 真正来源。长文档的结论保留为 `partial` 观察，不能声称已读完整历史。
