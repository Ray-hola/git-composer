#!/usr/bin/env python3
"""Validate the second substantive, read-only GitHub document evidence batch."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any
from urllib.parse import urlparse


ROOT = Path(__file__).resolve().parents[1]
REPORT_PATH = ROOT / "fixtures" / "corpus" / "github-public-doc-evidence-batch-2.json"
SHA = re.compile(r"^[0-9a-f]{40}$")
REQUIRED_REPOSITORIES = {
    "kubernetes/kubernetes",
    "rust-lang/rust",
    "django/django",
    "nodejs/node",
    "pytorch/pytorch",
}
REQUIRED_CATEGORIES = {"contribution", "governance", "security", "release", "ci", "workflow"}
CARD_FIELDS = {
    "card_id",
    "title",
    "claim_kind",
    "verification_level",
    "applies_when",
    "counterexamples",
    "procedure",
    "verification",
    "recovery",
    "evidence_refs",
    "status",
}
ALLOWED_HOSTS = {
    "github.com",
    "raw.githubusercontent.com",
    "rust-lang.org",
    "www.rust-lang.org",
    "docs.djangoproject.com",
    "pytorch.org",
}


def validate(report: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if report.get("report_type") != "github_public_document_evidence_batch":
        errors.append("wrong report_type")
    if report.get("schema_version") != 2 or report.get("batch_id") != "phase3b-mature-docs":
        errors.append("wrong second-batch identity")
    if report.get("snapshot_date") != "2026-09-30" or report.get("snapshot_timezone") != "UTC":
        errors.append("snapshot must be 2026-09-30 UTC")

    source = report.get("source", {})
    if (
        source.get("method") != "webfetch"
        or source.get("read_only") is not True
        or source.get("first_party_only") is not True
        or source.get("network_scope") != "public_html"
        or source.get("api_used") is not False
    ):
        errors.append("source must be read-only first-party public-html webfetch without API use")

    provenance = report.get("provenance", {})
    if provenance.get("fixed_sha_documents") != 0:
        errors.append("this HTML batch must not claim fixed-SHA documents")
    if provenance.get("branch_url_documents") != 26 or provenance.get("official_url_documents") != 4:
        errors.append("HTML URL provenance must count 26 GitHub branch URLs and 4 official non-GitHub URLs")
    if provenance.get("sha_status") != "not_obtainable_from_public_html":
        errors.append("SHA blocker must be explicit")
    if provenance.get("html_rounded_values_not_used") is not True:
        errors.append("rounded HTML values must not be used")

    counts = report.get("counts", {})
    repositories = report.get("repositories", [])
    documents = report.get("documents", [])
    cards = report.get("procedure_cards", [])
    if counts != {
        "metadata_records": 5,
        "documents_read": 30,
        "unique_documents_read": 30,
        "fixed_sha_documents": 0,
        "branch_url_documents": 26,
        "official_url_documents": 4,
        "procedure_cards": 6,
    }:
        errors.append("counts must record five metadata records, thirty unique reads, zero fixed SHAs, and six cards")
    if len(repositories) != 5 or len(documents) != 30 or len(cards) != 6:
        errors.append("record lengths do not match the bounded batch")
    canonical_urls = [item.get("source_url") for item in documents if isinstance(item, dict)]
    if len(canonical_urls) != len(set(canonical_urls)):
        errors.append("source URLs are not deduplicated")

    target = report.get("target", {})
    if target.get("candidate_projects") != 10000 or target.get("status") != "pending":
        errors.append("10k candidate target must remain explicitly pending")

    repo_names = {item.get("full_name") for item in repositories if isinstance(item, dict)}
    if repo_names != REQUIRED_REPOSITORIES:
        errors.append("repository set does not cover Kubernetes, Rust, Django, Node.js, and PyTorch")
    for index, item in enumerate(repositories):
        prefix = f"repositories[{index}]"
        if not isinstance(item, dict):
            errors.append(f"{prefix} is not an object")
            continue
        if item.get("snapshot_commit_sha") is not None:
            errors.append(f"{prefix}.snapshot_commit_sha must remain null without a fixed HTML SHA")
        if item.get("snapshot_sha_status") != "not_obtainable_from_public_html":
            errors.append(f"{prefix}.snapshot_sha_status must explain the HTML limitation")

    seen_ids: set[str] = set()
    categories_by_repo: dict[str, set[str]] = {name: set() for name in REQUIRED_REPOSITORIES}
    for index, item in enumerate(documents):
        prefix = f"documents[{index}]"
        if not isinstance(item, dict):
            errors.append(f"{prefix} is not an object")
            continue
        doc_id = item.get("document_id")
        if not isinstance(doc_id, str) or not doc_id or doc_id in seen_ids:
            errors.append(f"{prefix}.document_id is missing or duplicated")
        seen_ids.add(doc_id)
        repo = item.get("repository")
        if repo not in REQUIRED_REPOSITORIES:
            errors.append(f"{prefix} has an unknown repository")
        else:
            categories_by_repo[repo].add(item.get("category"))
        if item.get("category") not in REQUIRED_CATEGORIES:
            errors.append(f"{prefix} has an unknown category")
        if item.get("commit_sha") is not None or item.get("sha_status") != "not_obtainable_from_public_html":
            errors.append(f"{prefix} must preserve the unavailable-SHA status")
        if item.get("evidence_kind") != "public_html_declared" or not item.get("summary"):
            errors.append(f"{prefix} lacks a public HTML evidence summary")
        source_url = item.get("source_url", "")
        parsed = urlparse(source_url)
        if parsed.scheme != "https" or parsed.hostname not in ALLOWED_HOSTS:
            errors.append(f"{prefix}.source_url is not an allowed first-party HTTPS URL")
        if "/blob/" in source_url and re.search(r"/blob/[0-9a-f]{40}/", source_url):
            errors.append(f"{prefix}.source_url falsely claims a fixed commit SHA")
        raw_url = item.get("raw_url")
        if parsed.hostname in {"github.com", "raw.githubusercontent.com"} and "/blob/" in source_url:
            if not isinstance(raw_url, str) or not raw_url.startswith("https://raw.githubusercontent.com/"):
                errors.append(f"{prefix}.raw_url must preserve the branch raw URL")
        elif raw_url is not None:
            errors.append(f"{prefix}.raw_url must be null for non-GitHub HTML sources")
        for forbidden in ("stars", "stargazers_count", "display_value"):
            if forbidden in item:
                errors.append(f"{prefix} contains forbidden star metadata: {forbidden}")

    for repo, categories in categories_by_repo.items():
        if categories != REQUIRED_CATEGORIES:
            errors.append(f"{repo} must have one contribution, governance, security, release, CI, and workflow document")

    seen_card_ids: set[str] = set()
    for index, card in enumerate(cards):
        prefix = f"procedure_cards[{index}]"
        if not isinstance(card, dict) or set(card) != CARD_FIELDS:
            errors.append(f"{prefix} does not have the complete procedure-card shape")
            continue
        if card.get("card_id") in seen_card_ids:
            errors.append(f"{prefix}.card_id is duplicated")
        seen_card_ids.add(card.get("card_id"))
        if card.get("status") != "candidate":
            errors.append(f"{prefix} must remain a candidate until broader sampling")
        if not card.get("claim_kind") or not card.get("verification_level"):
            errors.append(f"{prefix} needs claim_kind and verification_level")
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
    print("PASS: five metadata records are separated from thirty unique public-HTML document reads")
    print("PASS: fixed-SHA absence and HTML provenance blocker are explicit")
    print("PASS: each project covers contribution, governance, security, release, CI, and workflow evidence")
    print("PASS: six cards include claim_kind, verification_level, applicability, counterexamples, verification, and recovery")
    print("PASS: 10,000-project target remains pending and star values are absent")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
