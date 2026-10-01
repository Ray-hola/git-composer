#!/usr/bin/env python3
"""Build a deterministic, offline-first GitHub corpus sampling plan.

The default mode never opens a network connection. ``--network`` is an
explicit opt-in for a small public-API pilot and stores only sanitized,
provenance-pinned repository records.
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import os
import random
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_POLICY = ROOT / "references" / "ranking-policy.yml"
PLAN_SCHEMA = ROOT / "schemas" / "corpus-plan.schema.json"


def parse_scalar(raw: str) -> Any:
    value = raw.strip()
    if not value:
        return None
    if value in {"null", "~"}:
        return None
    if value.lower() in {"true", "false"}:
        return value.lower() == "true"
    if value.startswith("["):
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            return ast.literal_eval(value)
    if value.startswith(('"', "'")):
        try:
            return ast.literal_eval(value)
        except (SyntaxError, ValueError):
            return value.strip('"\'')
    try:
        return int(value)
    except ValueError:
        try:
            return float(value)
        except ValueError:
            return value


def load_policy(path: Path) -> dict[str, Any]:
    """Parse the deliberately small YAML subset used by ranking-policy.yml."""

    result: dict[str, Any] = {"weights": {}, "partitions": []}
    section: str | None = None
    current_partition: dict[str, Any] | None = None
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        if not raw_line.strip() or raw_line.lstrip().startswith("#"):
            continue
        indent = len(raw_line) - len(raw_line.lstrip(" "))
        line = raw_line.strip()
        if indent == 0:
            if ":" not in line:
                raise ValueError(f"invalid policy line: {raw_line}")
            key, raw_value = line.split(":", 1)
            section = key
            current_partition = None
            if raw_value.strip():
                result[key] = parse_scalar(raw_value)
            elif key == "weights":
                result[key] = {}
            elif key == "partitions":
                result[key] = []
            continue
        if section == "weights" and indent >= 2:
            key, raw_value = line.split(":", 1)
            result["weights"][key.strip()] = parse_scalar(raw_value)
            continue
        if section == "partitions" and line.startswith("- "):
            current_partition = {}
            result["partitions"].append(current_partition)
            remainder = line[2:].strip()
            if remainder:
                key, raw_value = remainder.split(":", 1)
                current_partition[key.strip()] = parse_scalar(raw_value)
            continue
        if section == "partitions" and current_partition is not None and indent >= 4:
            key, raw_value = line.split(":", 1)
            current_partition[key.strip()] = parse_scalar(raw_value)
            continue
        raise ValueError(f"unsupported policy structure: {raw_line}")
    partitions = result.get("partitions", [])
    if not partitions:
        raise ValueError("policy must define partitions")
    if any(not item.get("id") for item in partitions):
        raise ValueError("every partition needs an id")
    share_total = sum(float(item.get("share", 0)) for item in partitions)
    if abs(share_total - 1.0) > 1e-9:
        raise ValueError(f"partition shares must sum to 1.0, got {share_total}")
    weight_total = sum(float(value) for value in result.get("weights", {}).values())
    if abs(weight_total - 1.0) > 1e-9:
        raise ValueError(f"ranking weights must sum to 1.0, got {weight_total}")
    return result


def allocate_counts(total: int, partitions: list[dict[str, Any]]) -> list[int]:
    raw = [total * float(item["share"]) for item in partitions]
    counts = [int(value) for value in raw]
    remaining = total - sum(counts)
    order = sorted(range(len(raw)), key=lambda index: (-(raw[index] - counts[index]), index))
    for index in order[:remaining]:
        counts[index] += 1
    return counts


def build_plan(policy: dict[str, Any], seed: int, candidate_target: int, network: bool) -> dict[str, Any]:
    partitions = policy["partitions"]
    counts = allocate_counts(candidate_target, partitions)
    return {
        "plan_type": "corpus_sampling_plan",
        "schema_version": 1,
        "mode": "network" if network else "dry-run",
        "network_enabled": network,
        "seed": seed,
        "candidate_target": candidate_target,
        "target_meaning": "At least this many unique candidate project records after owner/name and fork-lineage dedupe; it is not a 10k-star threshold and does not mean the records have been harvested.",
        "partitions": [
            {
                "id": item["id"],
                "share": float(item["share"]),
                "target_count": count,
                "qualifiers": list(item.get("qualifiers", [])),
            }
            for item, count in zip(partitions, counts)
        ],
        "manifest_schema": {
            "path": str(PLAN_SCHEMA.parent / "research-distillation-records.schema.json"),
            "record_type": "corpus_candidate",
            "required_fields": ["record_type", "repository", "snapshot", "sampling", "eligibility"],
        },
        "constraints": {
            "search_results_per_query_max": 1000,
            "search_scope_per_query_max": 4000,
            "authenticated_search_requests_per_minute": 30,
            "authenticated_code_search_requests_per_minute": 10,
            "authenticated_rest_requests_per_hour": 5000,
            "graphql_connection_page_max": 100,
            "content_directory_file_limit": 1000,
            "content_file_size_limit_bytes": 100 * 1024 * 1024,
        },
        "dedupe": ["owner/name", "fork_lineage_key"],
        "provenance": ["source_query", "captured_at", "default_branch", "commit_sha", "source"],
        "privacy": {
            "raw_content_ingested": False,
            "raw_issue_or_comment_text_ingested": False,
            "excluded_fields": ["description", "owner_profile", "issue_bodies", "comment_bodies", "tokens"],
        },
    }


def cache_key(url: str) -> str:
    return hashlib.sha256(url.encode("utf-8")).hexdigest() + ".json"


class RateBudget:
    def __init__(self) -> None:
        self.requests = 0
        self.search_requests = 0
        self.limit: int | None = None
        self.remaining: int | None = None
        self.reset_epoch: int | None = None

    def update(self, headers: Any, is_search: bool) -> None:
        self.requests += 1
        if is_search:
            self.search_requests += 1
        try:
            self.limit = int(headers.get("X-RateLimit-Limit", self.limit or 0)) or self.limit
            self.remaining = int(headers.get("X-RateLimit-Remaining", self.remaining or 0))
            self.reset_epoch = int(headers.get("X-RateLimit-Reset", self.reset_epoch or 0)) or self.reset_epoch
        except (TypeError, ValueError):
            pass

    def as_dict(self) -> dict[str, Any]:
        return {
            "requests": self.requests,
            "search_requests": self.search_requests,
            "limit": self.limit,
            "remaining": self.remaining,
            "reset_epoch": self.reset_epoch,
        }


class PublicGitHubClient:
    def __init__(self, cache_dir: Path, token: str | None, max_retries: int = 4) -> None:
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.token = token
        self.max_retries = max_retries
        self.rate_budget = RateBudget()

    def _wait_for_budget(self) -> None:
        if self.rate_budget.remaining == 0 and self.rate_budget.reset_epoch:
            delay = max(0, self.rate_budget.reset_epoch - int(time.time())) + 1
            time.sleep(delay)

    def get_json(self, url: str, sanitizer: Callable[[dict[str, Any]], dict[str, Any]], is_search: bool = False) -> dict[str, Any]:
        cache_path = self.cache_dir / cache_key(url)
        cached: dict[str, Any] | None = None
        if cache_path.exists():
            cached = json.loads(cache_path.read_text(encoding="utf-8"))
        for attempt in range(self.max_retries + 1):
            self._wait_for_budget()
            headers = {
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28",
                "User-Agent": "git-composer-corpus-planner/phase2",
            }
            if self.token:
                headers["Authorization"] = f"Bearer {self.token}"
            if cached and cached.get("etag"):
                headers["If-None-Match"] = cached["etag"]
            request = urllib.request.Request(url, headers=headers)
            try:
                with urllib.request.urlopen(request, timeout=30) as response:
                    self.rate_budget.update(response.headers, is_search)
                    raw = json.loads(response.read().decode("utf-8"))
                    sanitized = sanitizer(raw)
                    cache_path.write_text(json.dumps({"etag": response.headers.get("ETag"), "payload": sanitized}, sort_keys=True), encoding="utf-8")
                    return sanitized
            except urllib.error.HTTPError as error:
                self.rate_budget.update(error.headers, is_search)
                if error.code == 304 and cached:
                    return cached["payload"]
                if error.code not in {403, 429} or attempt >= self.max_retries:
                    raise
                retry_after = error.headers.get("Retry-After")
                if retry_after:
                    delay = max(1, int(retry_after))
                elif self.rate_budget.reset_epoch and self.rate_budget.remaining == 0:
                    delay = max(1, self.rate_budget.reset_epoch - int(time.time()) + 1)
                else:
                    delay = min(60, 2**attempt)
                time.sleep(delay)
        raise RuntimeError("unreachable retry state")


def sanitize_repository(item: dict[str, Any]) -> dict[str, Any]:
    full_name = str(item.get("full_name", ""))
    if not re.fullmatch(r"[^/\s]+/[^/\s]+", full_name):
        raise ValueError("repository response is missing a safe owner/name")
    topics = item.get("topics") or []
    return {
        "full_name": full_name,
        "html_url": f"https://github.com/{full_name}",
        "visibility": "public",
        "default_branch": str(item.get("default_branch") or "main"),
        "is_fork": bool(item.get("fork", False)),
        "is_archived": bool(item.get("archived", False)),
        "language": item.get("language") if isinstance(item.get("language"), str) else None,
        "topics": sorted(str(topic) for topic in topics if isinstance(topic, str)),
        "stars": int(item.get("stargazers_count", 0) or 0),
        "forks": int(item.get("forks_count", 0) or 0),
    }


def sanitize_search(raw: dict[str, Any]) -> dict[str, Any]:
    items: list[dict[str, Any]] = []
    for item in raw.get("items", []):
        try:
            items.append(sanitize_repository(item))
        except (TypeError, ValueError):
            continue
    return {
        "total_count": int(raw.get("total_count", 0) or 0),
        "incomplete_results": bool(raw.get("incomplete_results", False)),
        "items": items,
    }


def sanitize_detail(raw: dict[str, Any]) -> dict[str, Any]:
    result = sanitize_repository(raw)
    parent = raw.get("parent") or {}
    source = raw.get("source") or {}
    result["parent_full_name"] = parent.get("full_name") if isinstance(parent, dict) else None
    result["source_full_name"] = source.get("full_name") if isinstance(source, dict) else None
    return result


def search_url(query: str, page: int) -> str:
    params = urllib.parse.urlencode({"q": query, "sort": "stars", "order": "desc", "per_page": 100, "page": page})
    return f"https://api.github.com/search/repositories?{params}"


def collect_network(plan: dict[str, Any], client: PublicGitHubClient, max_records: int, seed: int) -> dict[str, Any]:
    records: list[dict[str, Any]] = []
    seen_names: set[str] = set()
    seen_lineages: set[str] = set()
    rng = random.Random(seed)
    partitions = list(plan["partitions"])
    rng.shuffle(partitions)
    for partition in partitions:
        if len(records) >= max_records:
            break
        query = " ".join([*partition["qualifiers"], "is:public"])
        page = 1
        while page <= 10 and len(records) < max_records and page <= max(1, (partition["target_count"] + 99) // 100):
            payload = client.get_json(search_url(query, page), sanitize_search, is_search=True)
            for candidate in payload["items"]:
                full_name = candidate["full_name"]
                if full_name in seen_names:
                    continue
                lineage = full_name
                if candidate["is_fork"]:
                    detail_url = f"https://api.github.com/repos/{full_name}"
                    detail = client.get_json(detail_url, sanitize_detail)
                    lineage = detail.get("source_full_name") or detail.get("parent_full_name") or full_name
                    candidate.update({key: detail[key] for key in ("default_branch", "is_fork", "is_archived") if key in detail})
                if lineage in seen_lineages:
                    continue
                commit_url = f"https://api.github.com/repos/{full_name}/commits/{urllib.parse.quote(candidate['default_branch'], safe='')}"
                commit = client.get_json(commit_url, lambda raw: {"sha": str(raw.get("sha", ""))})
                if not re.fullmatch(r"[0-9a-fA-F]{7,64}", commit.get("sha", "")):
                    continue
                seen_names.add(full_name)
                seen_lineages.add(lineage)
                records.append({
                    "record_type": "corpus_candidate",
                    "repository": candidate,
                    "snapshot": {
                        "captured_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
                        "commit_sha": commit["sha"],
                        "source": "github_rest",
                    },
                    "sampling": {"strata": [partition["id"]], "source_query": query, "seed": seed},
                    "eligibility": {"status": "included", "reasons": ["public", "deduped by owner/name and fork lineage"]},
                })
                if len(records) >= max_records:
                    break
            if len(payload["items"]) < 100:
                break
            page += 1
    return {"records": records, "rate_budget": client.rate_budget.as_dict(), "incomplete_search_results": False}


def collect_known_repositories(plan: dict[str, Any], client: PublicGitHubClient, repositories: list[str], max_records: int, seed: int) -> dict[str, Any]:
    """Collect metadata for an explicit, small, public repository allowlist."""

    records: list[dict[str, Any]] = []
    seen_names: set[str] = set()
    seen_lineages: set[str] = set()
    for full_name in sorted(set(repositories)):
        if len(records) >= max_records:
            break
        if not re.fullmatch(r"[^/\s]+/[^/\s]+", full_name):
            raise ValueError(f"invalid repository allowlist entry: {full_name}")
        detail_url = f"https://api.github.com/repos/{full_name}"
        detail = client.get_json(detail_url, sanitize_detail)
        lineage = detail.get("source_full_name") or detail.get("parent_full_name") or full_name
        if full_name in seen_names or lineage in seen_lineages:
            continue
        commit_url = f"https://api.github.com/repos/{full_name}/commits/{urllib.parse.quote(detail['default_branch'], safe='')}"
        commit = client.get_json(commit_url, lambda raw: {"sha": str(raw.get("sha", ""))})
        if not re.fullmatch(r"[0-9a-fA-F]{7,64}", commit.get("sha", "")):
            continue
        seen_names.add(full_name)
        seen_lineages.add(lineage)
        records.append({
            "record_type": "corpus_candidate",
            "repository": {key: detail[key] for key in ("full_name", "html_url", "visibility", "default_branch", "is_fork", "is_archived", "language", "topics", "stars", "forks")},
            "snapshot": {
                "captured_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
                "commit_sha": commit["sha"],
                "source": "github_rest",
            },
            "sampling": {"strata": ["smoke_known_public"], "source_query": f"repo:{full_name}", "seed": seed},
            "eligibility": {"status": "included", "reasons": ["explicit public smoke allowlist", "deduped by owner/name and fork lineage"]},
        })
    return {"records": records, "rate_budget": client.rate_budget.as_dict(), "incomplete_search_results": False}


def write_or_print(document: dict[str, Any], output: Path | None) -> None:
    encoded = json.dumps(document, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    if output:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(encoded, encoding="utf-8")
    else:
        sys.stdout.write(encoded)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--policy", type=Path, default=DEFAULT_POLICY)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--candidate-target", type=int, default=None)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--network", action="store_true", help="Explicitly opt into public GitHub API reads.")
    parser.add_argument("--repositories", nargs="+", help="Explicit public owner/name allowlist for a bounded pilot.")
    parser.add_argument("--max-network-records", type=int, default=100, help="Safety cap for --network pilots.")
    parser.add_argument("--cache-dir", type=Path, default=ROOT / ".cache" / "corpus")
    args = parser.parse_args()
    if args.seed < 0 or args.max_network_records < 1:
        parser.error("seed must be non-negative and max-network-records must be positive")
    if args.repositories and not args.network:
        parser.error("--repositories requires --network")
    policy = load_policy(args.policy)
    target = args.candidate_target or int(policy.get("candidate_target_default", 10000))
    if target < 1:
        parser.error("candidate-target must be positive")
    plan = build_plan(policy, args.seed, target, args.network)
    if not args.network:
        write_or_print(plan, args.output)
        return 0
    token = os.environ.get("GITHUB_TOKEN")
    client = PublicGitHubClient(args.cache_dir, token)
    if args.repositories:
        network_result = collect_known_repositories(plan, client, args.repositories, min(args.max_network_records, target), args.seed)
    else:
        network_result = collect_network(plan, client, min(args.max_network_records, target), args.seed)
    plan.update(network_result)
    write_or_print(plan, args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
