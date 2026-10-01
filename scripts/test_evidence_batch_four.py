#!/usr/bin/env python3
"""Validate the fourth 100-document first-party evidence batch."""

from __future__ import annotations

import json
import re
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "fixtures/corpus/github-public-doc-evidence-batch-4.json"
PRIOR = [
    ROOT / "fixtures/corpus/github-public-doc-evidence-batch.json",
    ROOT / "fixtures/corpus/github-public-doc-evidence-batch-2.json",
    ROOT / "fixtures/corpus/github-public-doc-evidence-batch-3.json",
]
SHA256 = re.compile(r"^[0-9a-f]{64}$")


def validate(report: dict) -> list[str]:
    errors: list[str] = []
    if report.get("report_type") != "github_public_document_evidence_batch" or report.get("schema_version") != 4:
        errors.append("wrong fourth-batch identity")
    if report.get("batch_id") != "phase4-smaller-libraries-monorepos":
        errors.append("wrong batch_id")
    if report.get("snapshot_date") != "2026-10-01" or report.get("snapshot_timezone") != "UTC":
        errors.append("snapshot must be 2026-10-01 UTC")
    source = report.get("source", {})
    if source.get("method") != "webfetch" or source.get("read_only") is not True or source.get("first_party_only") is not True or source.get("api_used") is not False:
        errors.append("source must be first-party read-only webfetch without API use")
    if source.get("retrieved_at") != "2026-10-01T04:46:00Z":
        errors.append("retrieval timestamp must be recorded")

    counts = report.get("counts", {})
    expected = {
        "metadata_records": 28,
        "documents_read": 100,
        "unique_documents_read": 100,
        "full_reads": 52,
        "partial_reads": 48,
        "fixed_sha_documents": 0,
        "branch_url_documents": 100,
        "content_hashes_available": 0,
        "procedure_cards_added": 4,
    }
    if counts != expected:
        errors.append(f"counts must equal {expected}")
    docs = report.get("documents", [])
    repos = report.get("repositories", [])
    if len(docs) != 100 or len(repos) != 28:
        errors.append("record lengths must be 100 documents and 28 metadata records")

    access = report.get("access_summary", {})
    if access.get("attempted_urls") != 147 or access.get("successful_unique_documents") != 100 or access.get("excluded_failed_fetches") != 47:
        errors.append("access summary must preserve 147 attempts, 100 successes, and 47 excluded failures")
    if access.get("failed_fetches_counted_as_documents") is not False or access.get("repeated_urls_counted_as_documents") is not False or access.get("sections_counted_as_documents") is not False:
        errors.append("failed, repeated, and sectional reads must not count as documents")
    failed_urls = [item.get("url") for item in access.get("failed_urls", []) if isinstance(item, dict)]
    if len(failed_urls) != 47 or len(set(failed_urls)) != 47:
        errors.append("failed URL ledger must contain 47 unique URLs")

    progress = report.get("cumulative_progress", {})
    if progress.get("prior_verified_unique_documents") != 152 or progress.get("this_batch_verified_unique_documents") != 100 or progress.get("cumulative_verified_unique_documents") != 252 or progress.get("target_documents") != 10000 or progress.get("status") != "pending":
        errors.append("cumulative progress must be 152 + 100 = 252 with 10,000 pending")
    target = report.get("target", {})
    if target.get("candidate_projects") != 10000 or target.get("status") != "pending":
        errors.append("10,000 candidate target must remain pending")

    urls = [item.get("source_url") for item in docs if isinstance(item, dict)]
    if len(urls) != len(set(urls)):
        errors.append("document URLs are not unique")
    if set(urls) & set(failed_urls):
        errors.append("failed URLs must not appear in successful documents")

    prior_urls: set[str] = set()
    for path in PRIOR:
        prior_urls.update(item.get("source_url") for item in json.loads(path.read_text(encoding="utf-8")).get("documents", []) if isinstance(item, dict))
    if prior_urls.intersection(urls):
        errors.append("fourth-batch URLs overlap an earlier evidence batch")

    seen_ids: set[str] = set()
    categories: set[str] = set()
    for index, item in enumerate(docs):
        prefix = f"documents[{index}]"
        if not isinstance(item, dict):
            errors.append(f"{prefix} is not an object")
            continue
        doc_id = item.get("document_id")
        if not isinstance(doc_id, str) or not doc_id or doc_id in seen_ids:
            errors.append(f"{prefix}.document_id missing or duplicated")
        seen_ids.add(doc_id)
        categories.add(item.get("category"))
        parsed = urlparse(item.get("source_url", ""))
        if parsed.scheme != "https" or parsed.hostname != "raw.githubusercontent.com":
            errors.append(f"{prefix}.source_url is not a first-party raw GitHub URL")
        if item.get("fetch_url") != item.get("source_url"):
            errors.append(f"{prefix}.fetch_url must retain the direct URL")
        if item.get("retrieved_at") != "2026-10-01T04:46:00Z":
            errors.append(f"{prefix}.retrieved_at is missing or inconsistent")
        lines = item.get("line_count_observed")
        expected_status = "full" if isinstance(lines, int) and lines <= 200 else "partial"
        if item.get("retrieval_status") != expected_status:
            errors.append(f"{prefix} retrieval status does not match observed line count")
        if item.get("commit_sha") is not None or item.get("sha_status") != "not_obtainable_from_public_html":
            errors.append(f"{prefix} must preserve unavailable fixed-SHA status")
        if item.get("content_sha256") is not None or item.get("content_hash_status") != "not_exposed_by_webfetch":
            errors.append(f"{prefix} must preserve unavailable content-hash status")
        if item.get("evidence_kind") != "public_raw_text" or not item.get("summary"):
            errors.append(f"{prefix} lacks evidence kind or summary")
    if not {"architecture", "structure", "contribution", "release", "automation"}.issubset(categories):
        errors.append("batch must cover architecture, structure, contribution, release, and automation evidence")

    for index, item in enumerate(repos):
        prefix = f"repositories[{index}]"
        if item.get("snapshot_commit_sha") is not None or item.get("snapshot_sha_status") != "not_obtainable_from_public_html":
            errors.append(f"{prefix} must state that fixed snapshot SHA was unavailable")
    cards = report.get("procedure_cards", [])
    if len(cards) != 4:
        errors.append("four procedure cards must be added")
    known_ids = seen_ids
    for index, card in enumerate(cards):
        prefix = f"procedure_cards[{index}]"
        required = {"card_id", "title", "claim_kind", "verification_level", "applies_when", "counterexamples", "procedure", "verification", "recovery", "evidence_refs", "status"}
        if not isinstance(card, dict) or set(card) != required:
            errors.append(f"{prefix} does not have the complete procedure-card shape")
            continue
        if card.get("status") != "candidate":
            errors.append(f"{prefix} must remain candidate pending broader sampling")
        for field in ("applies_when", "counterexamples", "procedure", "verification", "recovery", "evidence_refs"):
            if not isinstance(card.get(field), list) or not card[field]:
                errors.append(f"{prefix}.{field} must be non-empty")
        for ref in card.get("evidence_refs", []):
            if ref not in known_ids:
                errors.append(f"{prefix} references unknown document {ref}")
    if report.get("provenance", {}).get("fixed_sha_documents") != 0 or report.get("provenance", {}).get("content_hashes_available") != 0:
        errors.append("provenance must report zero fixed SHAs and zero content hashes")
    if "not_exposed" not in report.get("provenance", {}).get("content_hash_blocker", ""):
        errors.append("missing content-hash reason must be explicit")
    return errors


def main() -> int:
    report = json.loads(REPORT.read_text(encoding="utf-8"))
    errors = validate(report)
    if errors:
        for error in errors:
            print(f"FAIL: {error}")
        return 1
    print("PASS: 147 attempted URLs are separated into 100 successful documents and 47 excluded failures")
    print("PASS: 52 full and 48 partial reads preserve line-count evidence")
    print("PASS: direct URLs, timestamps, missing SHA/hash reasons, and cross-batch dedupe are explicit")
    print("PASS: four new procedure cards cite only this batch and 10,000 remains pending")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
