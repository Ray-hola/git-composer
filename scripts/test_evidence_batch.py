#!/usr/bin/env python3
"""Validate the first substantive, read-only GitHub document evidence batch."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
REPORT_PATH = ROOT / "fixtures" / "corpus" / "github-public-doc-evidence-batch.json"
SHA = re.compile(r"^[0-9a-f]{40}$")
REQUIRED_CATEGORIES = {"contribution", "structure", "ci", "release"}
REQUIRED_REPOSITORIES = {
    "cli/cli",
    "fastapi/fastapi",
    "vitejs/vite",
    "astral-sh/ruff",
    "sindresorhus/awesome",
}
CARD_FIELDS = {
    "card_id",
    "title",
    "applies_when",
    "counterexamples",
    "procedure",
    "verification",
    "recovery",
    "evidence_refs",
    "status",
}


def validate(report: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if report.get("report_type") != "github_public_document_evidence_batch":
        errors.append("wrong report_type")
    source = report.get("source", {})
    if source.get("method") != "webfetch" or source.get("read_only") is not True or source.get("first_party_only") is not True:
        errors.append("source must be read-only first-party webfetch")
    counts = report.get("counts", {})
    repositories = report.get("repositories", [])
    documents = report.get("documents", [])
    cards = report.get("procedure_cards", [])
    if counts.get("metadata_records") != len(repositories):
        errors.append("metadata_records does not match repository records")
    if counts.get("documents_read") != len(documents):
        errors.append("documents_read does not match document records")
    canonical_urls = [item.get("source_url") for item in documents if isinstance(item, dict)]
    if counts.get("unique_documents_read") != len(set(canonical_urls)) or len(canonical_urls) != len(set(canonical_urls)):
        errors.append("document count or canonical URLs are not deduplicated")
    if counts.get("documents_read", 0) <= counts.get("metadata_records", 0):
        errors.append("document reads must be counted separately from metadata records")
    if counts.get("procedure_cards") != len(cards):
        errors.append("procedure_cards does not match card records")

    target = report.get("target", {})
    if target.get("candidate_projects") != 10000 or target.get("status") != "pending":
        errors.append("10k candidate target must remain explicitly pending")

    repo_names = {item.get("full_name") for item in repositories if isinstance(item, dict)}
    if repo_names != REQUIRED_REPOSITORIES:
        errors.append("repository set does not cover the required five project types")
    repo_shas = {
        item.get("full_name"): item.get("snapshot_commit_sha")
        for item in repositories
        if isinstance(item, dict)
    }
    for item in repositories:
        if not isinstance(item, dict) or not SHA.fullmatch(item.get("snapshot_commit_sha", "")):
            errors.append("repository snapshot commit is not a full SHA")

    seen_ids: set[str] = set()
    seen_categories: set[str] = set()
    for index, item in enumerate(documents):
        prefix = f"documents[{index}]"
        if not isinstance(item, dict):
            errors.append(f"{prefix} is not an object")
            continue
        doc_id = item.get("document_id")
        if not isinstance(doc_id, str) or doc_id in seen_ids:
            errors.append(f"{prefix}.document_id is missing or duplicated")
        seen_ids.add(doc_id)
        if item.get("repository") not in REQUIRED_REPOSITORIES:
            errors.append(f"{prefix} has an unknown repository")
        category = item.get("category")
        seen_categories.add(category)
        if category not in REQUIRED_CATEGORIES:
            errors.append(f"{prefix} has an unknown category")
        sha = item.get("commit_sha", "")
        if not SHA.fullmatch(sha):
            errors.append(f"{prefix}.commit_sha is not a full SHA")
        url = item.get("source_url", "")
        if not isinstance(url, str) or not re.search(r"/blob/[0-9a-f]{40}/", url):
            errors.append(f"{prefix}.source_url is not a fixed GitHub blob URL")
        if f"/blob/{sha}/" not in url:
            errors.append(f"{prefix}.source_url does not pin its commit_sha")
        fetch_url = item.get("fetch_url", "")
        if not isinstance(fetch_url, str) or not fetch_url.startswith("https://raw.githubusercontent.com/") or f"/{sha}/" not in fetch_url:
            errors.append(f"{prefix}.fetch_url is not a matching raw fixed-SHA URL")
        if sha != repo_shas.get(item.get("repository")):
            errors.append(f"{prefix}.commit_sha does not match the repository snapshot")
        if item.get("evidence_kind") != "declared" or not item.get("summary"):
            errors.append(f"{prefix} lacks declared evidence summary")
        if "stars" in item or "stargazers_count" in item:
            errors.append(f"{prefix} contains forbidden star metadata")
    if not REQUIRED_CATEGORIES.issubset(seen_categories):
        errors.append("batch does not cover contribution, structure, CI, and release evidence")

    for index, card in enumerate(cards):
        prefix = f"procedure_cards[{index}]"
        if not isinstance(card, dict) or set(card) != CARD_FIELDS:
            errors.append(f"{prefix} does not have the complete procedure-card shape")
            continue
        if card.get("status") != "candidate":
            errors.append(f"{prefix} must remain a candidate until broader sampling")
        for field in ("applies_when", "counterexamples", "procedure", "verification", "recovery", "evidence_refs"):
            if not isinstance(card.get(field), list) or not card[field]:
                errors.append(f"{prefix}.{field} must be non-empty")
        for ref in card.get("evidence_refs", []):
            if ref not in seen_ids:
                errors.append(f"{prefix} references unknown document {ref}")
    return errors


def main() -> int:
    report = json.loads(REPORT_PATH.read_text(encoding="utf-8"))
    errors = validate(report)
    if errors:
        for error in errors:
            print(f"FAIL: {error}")
        return 1
    print("PASS: 5 metadata records are separated from 22 unique document reads")
    print("PASS: fixed-SHA first-party provenance and required categories")
    print("PASS: six evidence-backed novice procedure cards")
    print("PASS: 10,000-project target remains pending")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
