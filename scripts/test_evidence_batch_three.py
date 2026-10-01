#!/usr/bin/env python3
"""Validate the third, 100-document public first-party corpus batch."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any
from urllib.parse import urlparse


ROOT = Path(__file__).resolve().parents[1]
REPORT_PATH = ROOT / "fixtures" / "corpus" / "github-public-doc-evidence-batch-3.json"
FIRST_BATCH = ROOT / "fixtures" / "corpus" / "github-public-doc-evidence-batch.json"
SECOND_BATCH = ROOT / "fixtures" / "corpus" / "github-public-doc-evidence-batch-2.json"
ALLOWED_HOSTS = {"raw.githubusercontent.com"}
SHA256 = re.compile(r"^[0-9a-f]{64}$")
REQUIRED_CATEGORIES = {"architecture", "contribution", "testing", "release"}


def validate(report: dict[str, Any], first: dict[str, Any], second: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if report.get("report_type") != "github_public_document_evidence_batch" or report.get("schema_version") != 3:
        errors.append("wrong third-batch identity")
    if report.get("batch_id") != "phase3c-document-corpus":
        errors.append("wrong batch_id")
    if report.get("snapshot_date") != "2026-09-30" or report.get("snapshot_timezone") != "UTC":
        errors.append("snapshot must be 2026-09-30 UTC")
    source = report.get("source", {})
    if source.get("method") != "webfetch" or source.get("read_only") is not True or source.get("first_party_only") is not True or source.get("api_used") is not False:
        errors.append("source must be first-party read-only webfetch without API use")

    counts = report.get("counts", {})
    expected = {"metadata_records": 25, "documents_read": 100, "unique_documents_read": 100, "full_reads": 54, "partial_reads": 46, "content_hashes_available": 0}
    if counts != expected:
        errors.append(f"counts must equal {expected}")
    documents = report.get("documents", [])
    repositories = report.get("repositories", [])
    if len(documents) != 100 or len(repositories) != 25:
        errors.append("record lengths must be 100 documents and 25 metadata records")

    access = report.get("access_summary", {})
    if access.get("attempted_urls") != 130 or access.get("successful_unique_documents") != 100 or access.get("excluded_failed_fetches") != 30:
        errors.append("access summary must preserve 130 attempts, 100 successes, and 30 excluded failures")
    if access.get("failed_fetches_counted_as_documents") is not False or access.get("repeated_urls_counted_as_documents") is not False or access.get("sections_counted_as_documents") is not False:
        errors.append("failed, repeated, and sectional reads must not count as documents")

    progress = report.get("cumulative_progress", {})
    if progress.get("prior_verified_unique_documents") != 52 or progress.get("this_batch_verified_unique_documents") != 100 or progress.get("cumulative_verified_unique_documents") != 152 or progress.get("target_documents") != 10000 or progress.get("status") != "pending":
        errors.append("cumulative progress must be 52 + 100 = 152 with 10,000 pending")

    urls = [item.get("source_url") for item in documents if isinstance(item, dict)]
    if len(urls) != len(set(urls)):
        errors.append("third-batch source URLs are not unique")
    prior_urls = {item.get("source_url") for source in (first, second) for item in source.get("documents", [])}
    if prior_urls.intersection(urls):
        errors.append("third-batch URL overlaps a prior evidence batch")

    seen_ids: set[str] = set()
    categories: set[str] = set()
    for index, item in enumerate(documents):
        prefix = f"documents[{index}]"
        if not isinstance(item, dict):
            errors.append(f"{prefix} is not an object")
            continue
        doc_id = item.get("document_id")
        if not isinstance(doc_id, str) or not doc_id or doc_id in seen_ids:
            errors.append(f"{prefix}.document_id missing or duplicated")
        seen_ids.add(doc_id)
        categories.add(item.get("category"))
        if item.get("retrieval_status") not in {"full", "partial"}:
            errors.append(f"{prefix} has no full/partial retrieval status")
        lines = item.get("line_count_observed")
        expected_status = "full" if isinstance(lines, int) and lines <= 200 else "partial"
        if item.get("retrieval_status") != expected_status:
            errors.append(f"{prefix} retrieval status does not match observed line count")
        if item.get("content_sha256") is not None or item.get("content_hash_status") != "not_exposed_by_webfetch":
            errors.append(f"{prefix} must state that webfetch did not expose a content hash")
        if item.get("evidence_kind") != "public_raw_text" or not item.get("summary"):
            errors.append(f"{prefix} lacks evidence kind or summary")
        parsed = urlparse(item.get("source_url", ""))
        if parsed.scheme != "https" or parsed.hostname not in ALLOWED_HOSTS:
            errors.append(f"{prefix}.source_url is not a first-party raw GitHub URL")
        if not item.get("source_url", "").startswith("https://raw.githubusercontent.com/"):
            errors.append(f"{prefix}.source_url is not canonical raw URL")
        for forbidden in ("stars", "stargazers_count", "display_value", "exact_stars"):
            if forbidden in item:
                errors.append(f"{prefix} contains forbidden star metadata: {forbidden}")
    if not REQUIRED_CATEGORIES.issubset(categories):
        errors.append("batch must cover architecture, contribution, testing, and release evidence")

    repo_names = {item.get("full_name") for item in repositories if isinstance(item, dict)}
    if len(repo_names) != 25:
        errors.append("repository metadata must be deduplicated")
    for item in repositories:
        if item.get("snapshot_commit_sha") is not None or item.get("snapshot_sha_status") != "not_obtainable_from_public_html":
            errors.append("repository snapshot SHA status must remain explicit and unavailable")
    return errors


def main() -> int:
    report = json.loads(REPORT_PATH.read_text(encoding="utf-8"))
    first = json.loads(FIRST_BATCH.read_text(encoding="utf-8"))
    second = json.loads(SECOND_BATCH.read_text(encoding="utf-8"))
    errors = validate(report, first, second)
    if errors:
        for error in errors:
            print(f"FAIL: {error}")
        return 1
    print("PASS: 100 unique successful first-party document reads are separated from 25 metadata records")
    print("PASS: 54 full and 46 partial reads are explicitly distinguished")
    print("PASS: failed, repeated, and sectional reads are excluded; hashes unavailable is explicit")
    print("PASS: cumulative verified unique count is 152 and 10,000 remains pending")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
