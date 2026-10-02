# Git-only decision gates

This reference governs Git requests that can change a repository, its history, a remote, or a release. It does not authorize Git initialization, remote configuration, pushes, releases, or unrelated product work.

## Snapshot before classification

Run these read-only commands first:

```sh
git rev-parse --show-toplevel
git symbolic-ref --short -q HEAD || printf '%s\\n' '(detached HEAD)'
git rev-parse --verify HEAD 2>/dev/null || printf '%s\\n' '(no commit)'
git status --short --branch
git diff --stat
git diff --cached --stat
git remote -v
```

Record root, branch or detached state, `HEAD` (or no commit), worktree status, staged/unstaged summaries, and remotes. Mask credentials in remote URLs. Never infer `origin`, `main`, default-branch names, visibility, upstreams, or permissions.

## Classify the request

Use exactly one or more of these classes, in dependency order: `observe` (read facts), `plan` (bounded plan), `local_write` (worktree edits), `commit` (local history), `remote_write` (push/remote branch/tag/PR/settings), `release` (tag/package/publish), and `research` (bounded public or local evidence reads). Stop at the first unresolved gate. Keep Git work separate from product implementation, deployment, account administration, or unrelated cleanup.

## Evidence labels

Label each material fact as `user` (explicitly supplied), `repo_fact` (observed in the snapshot/files), `inference` (drawn from labeled facts), `bounded_default` (narrow and reversible, such as inspect before edit), or `unverified` (not observed). Missing remotes, branches, visibility, licenses, versions, and permissions stay `unverified`; ask when they change the action.

## Questions and statuses

Ask only unresolved action-changing questions, in dependency order, with at most 1–3 in the initial round. **P0 before any write:** target and scope (repository, branch/path, files) plus side effect (worktree only, commit, remote write, or release). **P0 before legal/release:** license, version, and publish target. **P1 after P0:** language/audience when it changes files or wording, then verification commands and rollback/recovery. A remote or release action needs confirmation immediately before its irreversible step.

Use exactly one status: `READY`, `WAITING FOR ANSWER`, `CONFIRMATION REQUIRED`, `BLOCKED`, or `COMPLETE`. Local edits can be READY after P0; commit, remote, and release actions remain CONFIRMATION REQUIRED at the final step unless the user explicitly authorized that exact side effect.

## Grilling closure before a write

For any request that can change files, history, a remote, or a release, use a small design tree rather than silently choosing defaults:

1. Record the settled goal and the facts that can be read from the repository; facts are the agent's job, not a user questionnaire.
2. Ask the whole current frontier (the decisions whose prerequisites are settled) in one round, with a recommended answer and the consequence of each choice. Do not ask downstream questions before their prerequisites are answered.
3. Keep asking rounds until every action-changing branch is `settled`, `not applicable`, or explicitly deferred by the user. A vague “looks good” does not settle a missing license, audience, target, version, scope, or side effect.
4. Summarize the final scope, user-facing behavior, verification plan, rollback, and excluded work in plain language. This is the shared-understanding checkpoint.
5. Wait for the user's confirmation of that summary. Until it arrives, status is `WAITING FOR ANSWER` or `CONFIRMATION REQUIRED`; do not edit, commit, push, tag, or release.

After confirmation, facts may still fail validation. Keep the worktree reviewable, report the exact failed gate, and return to the affected frontier instead of converting a failed or unverified item into a completion claim. The same closure applies again immediately before a commit or any remote/release action when the final diff, target, or side effect differs from the confirmed summary.

## Report order

Reports must be ordered: **Status → Changed → Why / evidence → Verification (local, CI, remote, release) → Risk & rollback → Unknowns / blocked choice → Next question**. Mark unrun surfaces `unverified`; a local command does not verify CI, remote, or release state.

## Stop conditions

Report `BLOCKED` for out-of-scope product work, an unidentified target, requests to guess a remote/branch/visibility/license/version, suspected secrets, or an unauthorized/unconfirmed remote or release operation. Preserve local work and give a concrete recovery path. Do not initialize Git or alter remotes to make a request fit.

## Examples

- **Cleanup:** classify `local_write`; ask paths and whether to remain uncommitted; show the diff, run the named local check, and give file-level `git restore` recovery. Do not delete user data from a filename pattern alone.
- **GitHub upload:** classify `remote_write`; ask exact repository, branch, visibility, paths/history, and commit authorization; inspect tracked files and history for credentials; confirm immediately before push; verify remote branch/commit separately. Never infer `origin`, `main`, or public visibility.
- **Release prep:** classify preparation as `plan`/`local_write` and publication as `release`; ask license, version, and publish target; read release instructions; stage notes and run checks; confirm tag/package/publish; verify tag, artifact, registry/release page, and CI independently.
- **Mature-repository research:** classify `research`; keep reads public and bounded; distinguish candidate metadata, documents read, and the `10k-star` stratum. Preserve the verified-document count and any candidate target as separate evidence fields; a candidate target is not a completion claim. Do not create issues/PRs, push, or change settings; label conclusions `inference` or `bounded_default`.
