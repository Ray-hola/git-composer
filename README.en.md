<p align="center">
  <img src="assets/git-composer-mark.svg" width="82" alt="Git Composer mark" />
</p>

<h1 align="center">Git Composer</h1>

<p align="center">
  <strong>Make a repository easier to understand, change, verify, and recover.</strong><br />
  A Codex-first companion for Git, README design, and repository maintenance.
</p>

<p align="center">
  <a href="README.md">中文</a> ·
  <a href="https://github.com/Ray-Hola/git-composer">GitHub</a> ·
  <a href="references/codex-onboarding.md">Codex onboarding</a> ·
  <a href="references/README.md">Reference index</a>
</p>

<p align="center">
  <a href="https://github.com/Ray-Hola/git-composer"><img src="https://img.shields.io/github/stars/Ray-Hola/git-composer?style=flat&label=stars" alt="GitHub stars" /></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-2563eb" alt="MIT license" /></a>
</p>

## Start in Codex

You do not need to learn the terminal or Git first. Send this prompt with the repository link:

```text
Please install and enable git-composer from https://github.com/Ray-Hola/git-composer.
Before installing, tell me the target location, files that may change, and decisions I need to make; do not commit or push automatically.
After installation, explain what I can ask it to do and wait for my first task.
```

If your Codex client has a Skill manager, choose “install from GitHub” and enter `Ray-Hola/git-composer`. If that entry is not available, use the natural-language prompt above.

**No terminal or Git knowledge is required.** Maintainer commands and recovery details are kept in the collapsed reference section below.

## The first successful task

After installation, send:

```text
Use $git-composer to inspect this repository read-only first.
Keep my existing changes, tell me the three most valuable improvements, and do not edit, commit, or push yet.
```

You should receive a reviewable report containing:

- the target repository, branch, and worktree state;
- evidence read from actual files rather than guesses;
- completed, unverified, and user-decision items;
- risks, recovery, and one next step.

Until you confirm the scope, the Skill must not overwrite files, create a commit, or push to a remote.

## Prompts you can reuse

| Goal | Tell Codex |
| --- | --- |
| Understand a repository | `Use $git-composer for a read-only review and keep existing changes.` |
| Improve the landing page | `Make the README easier for a beginner; ask me the decisions first.` |
| Commit safely | `Apply the confirmed scope; ask every unresolved question and commit only after checks pass.` |
| Recover from a problem | `Stop writing. List completed checks, unverified items, and the smallest recovery path.` |

## How it works

1. **Find facts first:** the Skill reads the root, branch, diff, history, entry points, and existing conventions.
2. **Ask choices next:** grilling rounds cover decisions that change scope, audience, license, verification, or side effects.
3. **Confirm shared understanding:** Codex restates scope, acceptance, risks, recovery, and exclusions and waits for your confirmation.
4. **Write last:** it edits only after confirmation and reports local commits, pushes, releases, and remote readback separately.

## Documentation

| Need | Start here |
| --- | --- |
| Codex installation and first task | [Codex onboarding](references/codex-onboarding.md) |
| Understand repository shape | [Project structure](references/project-structure.md) |
| Define governance and maintenance | [Governance and docs](references/governance-and-docs.md) |
| Design the README landing page | [README design](references/readme-design.md) |
| Handle branches, commits, sync, and recovery | [Git workflows](references/git-workflows.md) |
| Gate Git writes, remotes, and releases | [Git decision gates](references/decision-gates.md) |
| Turn research into reusable rules | [Research and distillation](references/research-and-distillation.md) |
| Write executable, evidence-backed procedures | [Procedure cards](references/procedure-cards.md) |
| Check license, version, and badge facts | [Metadata and badges](references/metadata-and-badges.md) |
| Write status, evidence, and recovery reports | [Reporting templates](references/reporting-templates.md) |
| Browse the complete map | [references/README.md](references/README.md) |

## Evidence and boundaries

- The verified research material contains **252 deduplicated evidence documents**, with sources, retrieval status, and candidate rules kept in [research and distillation](references/research-and-distillation.md) and its fixtures.
- The fourth evidence fixture is available [here](fixtures/corpus/github-public-doc-evidence-batch-4.json); it remains separate from candidate targets, rule candidates, and user-facing conclusions.
- Candidate research targets are tracked separately from verified documents; a target is not a claim that the Skill has completed that research.
- Research fetching stays read-only, and public HTML fallback preserves provenance and retrieval status.
- The project does not claim unverified licenses, releases, CI, performance, user counts, or screenshots.

## Verification

You can ask Codex to run the checks that match your change:

```text
Use $git-composer to run the checks that match this change.
Report local checks, CI, remote state, and visual preview separately; mark anything not run as unverified.
```

The maintainer suite covers structure, references, UI metadata, schema, fallback behavior, four evidence batches, grilling gates, and offline evaluation. It does not claim target-repository business tests, remote CI, or GitHub page visual approval.

## Safety and recovery

- Local writes, commits, history rewrites, and remote writes are separate actions; read before write.
- Unanswered user questions, unconfirmed shared understanding, or failed checks block commits and pushes.
- Never publish API tokens, private keys, cookies, private configuration, message records, databases, media, or machine state.
- For shared commits, prefer `git revert` instead of force-pushing or rewriting history.

## License

This project is released under the [MIT License](LICENSE), © `Ray-hola`. Third-party materials remain under their own licenses.

<details>
<summary>Maintainer reference: CLI install, checks, and recovery</summary>

### Install and update

After confirming that the target directory has no local changes to keep:

```sh
mkdir -p ~/.codex/skills
git clone https://github.com/Ray-Hola/git-composer.git ~/.codex/skills/git-composer
git -C ~/.codex/skills/git-composer pull --ff-only
```

When local changes exist, ask Codex to inspect them and provide a recovery path before updating.

### Exact maintenance checks

From the Skill root:

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

### Delivery status block

```text
Status: READY / WAITING FOR ANSWER / CONFIRMATION REQUIRED / BLOCKED / COMPLETE
Scope: <files or remote object>
Changed: <one sentence>
Verification: <command> -> passed / failed / unverified
Evidence: <path, line, commit, or page>
Risk and recovery: <risk and recovery path>
Unknowns: <facts still to confirm, or none>
Next: <one most valuable action>
```

</details>
