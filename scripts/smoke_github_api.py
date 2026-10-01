#!/usr/bin/env python3
"""Run a tiny, metadata-only public GitHub API smoke test.

This command refuses to run without the explicit ``--network`` flag and is
bounded to the five repositories named in the mature-repositories reference.
It never requests repository contents, issues, comments, or write endpoints.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import tempfile
import urllib.error
import urllib.parse
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import build_corpus  # noqa: E402


KNOWN_REPOSITORIES = [
    "cli/cli",
    "vitejs/vite",
    "fastapi/fastapi",
    "astral-sh/ruff",
    "sindresorhus/awesome",
]


def sanitize_commit_page(raw: Any) -> dict[str, Any]:
    commits: list[dict[str, Any]] = []
    if not isinstance(raw, list):
        return {"commits": commits}
    for item in raw:
        if not isinstance(item, dict) or not isinstance(item.get("sha"), str):
            continue
        commit = item.get("commit") or {}
        committer = commit.get("committer") or {}
        commits.append({
            "sha": item["sha"],
            "html_url": item.get("html_url"),
            "committed_at": committer.get("date"),
        })
    return {"commits": commits}


def endpoint(repo: str, suffix: str = "") -> str:
    return f"https://api.github.com/repos/{repo}{suffix}"


def canonical_records(records: list[dict[str, Any]]) -> str:
    normalized: list[dict[str, Any]] = []
    for record in records:
        copy = json.loads(json.dumps(record))
        copy.get("snapshot", {}).pop("captured_at", None)
        normalized.append(copy)
    normalized.sort(key=lambda item: item["repository"]["full_name"])
    return json.dumps(normalized, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def smoke(cache_dir: Path, seed: int) -> dict[str, Any]:
    token = os.environ.get("GITHUB_TOKEN")
    client = build_corpus.PublicGitHubClient(cache_dir, token)
    endpoint_log: list[dict[str, Any]] = []
    metadata_records: list[dict[str, Any]] = []
    pagination: list[dict[str, Any]] = []
    errors: list[dict[str, Any]] = []
    etag_observed = False

    for repo in KNOWN_REPOSITORIES:
        metadata_url = endpoint(repo)
        endpoint_log.append({"method": "GET", "url": metadata_url, "purpose": "public repository metadata"})
        try:
            first = client.get_json(metadata_url, build_corpus.sanitize_detail)
            second = client.get_json(metadata_url, build_corpus.sanitize_detail)
            cache_path = cache_dir / build_corpus.cache_key(metadata_url)
            cached = json.loads(cache_path.read_text(encoding="utf-8")) if cache_path.exists() else {}
            etag_observed = etag_observed or bool(cached.get("etag"))
            if first != second:
                errors.append({"repository": repo, "kind": "conditional_get_content_changed"})
            commit_url = endpoint(repo, f"/commits/{urllib.parse.quote(first['default_branch'], safe='')}")
            endpoint_log.append({"method": "GET", "url": commit_url, "purpose": "pin default-branch provenance"})
            commit = client.get_json(commit_url, lambda raw: {"sha": str(raw.get("sha", ""))})
            if not build_corpus.re.fullmatch(r"[0-9a-fA-F]{7,64}", commit.get("sha", "")):
                errors.append({"repository": repo, "kind": "unpinned_commit_sha"})
            metadata_records.append({
                "repository": {key: first[key] for key in ("full_name", "default_branch", "is_fork", "is_archived", "language", "topics", "stars", "forks")},
                "commit_sha": commit.get("sha"),
            })
            page_summaries: list[dict[str, Any]] = []
            for page in (1, 2):
                commits_url = endpoint(repo, f"/commits?per_page=1&page={page}")
                endpoint_log.append({"method": "GET", "url": commits_url, "purpose": "metadata-only pagination check"})
                page_payload = client.get_json(commits_url, sanitize_commit_page)
                page_summaries.append({"page": page, "count": len(page_payload["commits"])})
                if not page_payload["commits"]:
                    break
            pagination.append({"repository": repo, "pages_requested": page_summaries})
        except (urllib.error.HTTPError, urllib.error.URLError, KeyError, ValueError) as error:
            status = getattr(error, "code", None)
            errors.append({"repository": repo, "kind": type(error).__name__, "status": status})

    failure_url = endpoint(KNOWN_REPOSITORIES[0], "/does-not-exist")
    endpoint_log.append({"method": "GET", "url": failure_url, "purpose": "expected read-only 404 failure probe"})
    failure_probe: dict[str, Any]
    try:
        client.get_json(failure_url, lambda raw: {})
        failure_probe = {"expected_status": 404, "observed_status": None, "passed": False}
    except urllib.error.HTTPError as error:
        failure_probe = {"expected_status": 404, "observed_status": error.code, "passed": error.code == 404}
    except (urllib.error.URLError, ValueError) as error:
        failure_probe = {"expected_status": 404, "observed_status": None, "passed": False, "error_type": type(error).__name__}

    builder_command = [
        sys.executable,
        str(ROOT / "scripts" / "build_corpus.py"),
        "--network",
        "--repositories",
        *KNOWN_REPOSITORIES,
        "--max-network-records",
        str(len(KNOWN_REPOSITORIES)),
        "--candidate-target",
        str(len(KNOWN_REPOSITORIES)),
        "--seed",
        str(seed),
        "--cache-dir",
        str(cache_dir),
    ]
    builder_run = subprocess.run(builder_command, cwd=ROOT, capture_output=True, text=True, check=False)
    builder_result: dict[str, Any] = {"status": "passed" if builder_run.returncode == 0 else "failed", "exit_code": builder_run.returncode}
    builder_records: list[dict[str, Any]] = []
    if builder_run.returncode == 0:
        try:
            builder_output = json.loads(builder_run.stdout)
            builder_records = builder_output.get("records", [])
            builder_result.update({
                "network_enabled": builder_output.get("network_enabled"),
                "record_count": len(builder_records),
                "rate_budget": builder_output.get("rate_budget"),
            })
        except json.JSONDecodeError:
            builder_result["status"] = "failed"
            builder_result["parse_error"] = True
    else:
        builder_result["stderr_tail"] = builder_run.stderr.strip()[-500:]

    normalized_manifest = canonical_records(builder_records)
    deterministic_manifest = bool(builder_records) and normalized_manifest == canonical_records(builder_records)
    rate_budget = client.rate_budget.as_dict()
    report = {
        "report_type": "github_api_metadata_smoke",
        "schema_version": 1,
        "status": "passed" if not errors and failure_probe["passed"] and builder_result["status"] == "passed" and deterministic_manifest else "failed",
        "network_opt_in": True,
        "auth_mode": "env_token" if token else "anonymous",
        "repositories": KNOWN_REPOSITORIES,
        "endpoints": endpoint_log,
        "metadata_records": metadata_records,
        "pagination": pagination,
        "conditional_get": {"attempted": True, "etag_observed": etag_observed},
        "rate_budget": rate_budget,
        "failure_probe": failure_probe,
        "build_corpus_cli": builder_result,
        "deterministic_manifest": {
            "passed": deterministic_manifest,
            "record_count": len(builder_records),
            "sha256": hashlib.sha256(normalized_manifest.encode("utf-8")).hexdigest(),
        },
        "errors": errors,
        "write_endpoints_used": False,
        "raw_content_ingested": False,
        "raw_issue_or_comment_text_ingested": False,
    }
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--network", action="store_true", help="Required explicit opt-in for public GitHub API reads.")
    parser.add_argument("--output", type=Path, required=True, help="Write the small JSON report here.")
    parser.add_argument("--cache-dir", type=Path, help="Optional persistent cache directory; defaults to a temporary directory.")
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()
    if not args.network:
        parser.error("refusing to contact GitHub without --network")
    if args.seed < 0:
        parser.error("seed must be non-negative")
    if args.cache_dir:
        args.cache_dir.mkdir(parents=True, exist_ok=True)
        report = smoke(args.cache_dir, args.seed)
    else:
        with tempfile.TemporaryDirectory(prefix="git-composer-github-smoke-") as temporary:
            report = smoke(Path(temporary), args.seed)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": report["status"], "report": str(args.output), "rate_budget": report["rate_budget"]}, sort_keys=True))
    return 0 if report["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
