<p align="center">
  <img src="assets/git-composer-mark.svg" width="82" alt="Git Composer mark" />
</p>

<h1 align="center">Git Composer</h1>

<p align="center">
  <strong>Make a repository easier to understand, change, verify, and recover.</strong><br />
  A beginner-friendly companion for Git, README design, and repository maintenance.
</p>

<p align="center">
  <a href="README.md">中文</a> ·
  <a href="https://github.com/Ray-Hola/git-composer">GitHub</a> ·
  <a href="references/README.md">Reference index</a>
</p>

<p align="center">
  <a href="https://github.com/Ray-Hola/git-composer"><img src="https://img.shields.io/badge/GitHub-view%20repository-181717?logo=github&logoColor=white" alt="View the GitHub repository" /></a>
  <a href="https://github.com/Ray-Hola/git-composer"><img src="https://img.shields.io/github/stars/Ray-Hola/git-composer?style=flat&label=stars" alt="GitHub stars" /></a>
  <a href="#verification"><img src="https://img.shields.io/badge/status-local%20checks%20documented-2563eb" alt="Status: local checks documented" /></a>
</p>

## Start in 60 seconds

Run a read-only inspection first. These commands do not edit files, commit, push, or change remotes:

```sh
git rev-parse --show-toplevel
git status --short --branch
git diff --stat
git log -1 --format='%h %s%n%b'
```

Then ask Git Composer for a focused pass:

```text
Use $git-composer to inspect this repository first. Keep existing changes, improve the README and verification entry points, then report changes, evidence, checks, risks, and recovery.
```

The result should be a reviewable status report with scope, actual files, command results, evidence, unknowns, recovery, and one next step. Unrun checks stay marked **unverified**.

## What it helps with

### Read before write

Establish the root, branch, diff, history, runtime entry point, and current conventions before treating anything as a project fact.

### Make small, reversible improvements

Improve a README, folder guide, contribution note, or Git workflow without inventing licenses, releases, CI, or performance promises.

### Leave an evidence-led handoff

Record what changed, why, how it was checked, what remains unknown, and how to recover. Keep candidate projects, evidence documents, and research conclusions separate.

## Documentation

| Need | Start here |
| --- | --- |
| Understand the repository shape | [Project structure](references/project-structure.md) |
| Define governance and maintenance rules | [Governance and docs](references/governance-and-docs.md) |
| Design the README landing page | [README design](references/readme-design.md) |
| Handle branches, commits, sync, and recovery | [Git workflows](references/git-workflows.md) |
| Gate Git writes, remotes, and releases | [Git decision gates](references/decision-gates.md) |
| Turn research into reusable rules | [Research and distillation](references/research-and-distillation.md) |
| Write executable, evidence-backed procedures | [Procedure cards](references/procedure-cards.md) |
| Check license, version, and badge facts | [Metadata and badges](references/metadata-and-badges.md) |
| Browse the complete map | [references/README.md](references/README.md) |

## Evidence-led workflow

- The verified research material contains **252 deduplicated evidence documents**. Sources, retrieval status, and candidate rules live in [research and distillation](references/research-and-distillation.md) and its fixtures.
- Git Composer keeps evidence, rules, and user-facing conclusions separate; this landing page focuses on the capabilities that are ready to use.
- Research fetching stays read-only, and public HTML fallback keeps provenance and retrieval status available for review.

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

These checks cover structure, references, UI metadata, schema, fallback behavior, four evidence batches, Git decision gates, and offline evaluation. They do not claim target-repository business tests, remote CI, or GitHub page visual approval.

## Safety and recovery

- Local writes, commits, history rewrites, and remote writes are separate actions; default to read before write.
- Do not publish API tokens, private keys, cookies, private configuration, message records, databases, media, or machine state.
- For shared commits, prefer `git revert` instead of force-pushing or rewriting shared history.
- If a credential may be exposed, stop sharing it and rotate it before repairing repository history.

## Contributing

Start with a read-only inspection, make one focused change, and include the exact verification command and result. Use the [procedure cards](references/procedure-cards.md) when turning a proven pattern into a reusable workflow.

See and discuss the project on [GitHub](https://github.com/Ray-Hola/git-composer).
