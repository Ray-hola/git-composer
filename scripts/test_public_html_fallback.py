#!/usr/bin/env python3
"""Validate the offline public-HTML GitHub fallback report."""

from __future__ import annotations

import copy
import json
import re
from datetime import date, datetime, time, timezone
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError


ROOT = Path(__file__).resolve().parents[1]
REPORT_PATH = ROOT / "fixtures" / "corpus" / "github-public-html-fallback-report.json"
EXPECTED_REPOSITORIES = [
    "cli/cli",
    "vitejs/vite",
    "fastapi/fastapi",
    "astral-sh/ruff",
    "sindresorhus/awesome",
]
ROUNDED_DISPLAY = re.compile(r"^[0-9]+(?:\.[0-9]+)?[kKmM]$")


def validate_snapshot(report: dict[str, Any], as_of: datetime) -> list[str]:
    """Reject a day only when its earliest possible instant is still future.

    The source observations have day precision, so local midnight is a lower
    bound, not an invented capture timestamp. A same-day observation cannot be
    ordered more precisely without additional provenance.
    """
    if not isinstance(as_of, datetime) or as_of.tzinfo is None or as_of.utcoffset() is None:
        return ["as_of must be a timezone-aware datetime"]
    if report.get("snapshot_precision") != "day":
        return ["snapshot_precision must be day"]
    try:
        snapshot_day = date.fromisoformat(report.get("snapshot_date"))
    except (TypeError, ValueError):
        return ["snapshot_date must be an ISO date"]
    try:
        snapshot_zone = ZoneInfo(report.get("snapshot_timezone"))
    except (TypeError, ValueError, ZoneInfoNotFoundError):
        return ["snapshot_timezone must be a valid IANA timezone"]
    earliest_instant = datetime.combine(snapshot_day, time.min, tzinfo=snapshot_zone)
    if earliest_instant.astimezone(timezone.utc) > as_of.astimezone(timezone.utc):
        return ["snapshot_date cannot be in the future in snapshot_timezone"]
    return []


def validate_report(report: dict[str, Any], as_of: datetime) -> list[str]:
    errors: list[str] = []
    if report.get("report_type") != "github_public_html_fallback":
        errors.append("report_type must identify the public HTML fallback")
    if report.get("evidence_kind") != "public_html":
        errors.append("report evidence_kind must be public_html")
    errors.extend(validate_snapshot(report, as_of))

    caveat = f"{report.get('caveat', '')} {report.get('no_claim_rule', '')}".lower()
    if "not api-equivalent" not in caveat:
        errors.append("report must state that HTML is not API-equivalent")
    if "exact" not in caveat or "star" not in caveat:
        errors.append("report must state the exact-star no-claim rule")

    repositories = report.get("repositories")
    if not isinstance(repositories, list):
        return errors + ["repositories must be a list"]
    names = [item.get("repository") for item in repositories if isinstance(item, dict)]
    if names != EXPECTED_REPOSITORIES:
        errors.append("repositories must retain the five-source order")

    for index, item in enumerate(repositories):
        prefix = f"repositories[{index}]"
        if not isinstance(item, dict):
            errors.append(f"{prefix} must be an object")
            continue
        if item.get("evidence_kind") != "public_html":
            errors.append(f"{prefix}.evidence_kind must be public_html")
        source_url = item.get("source_url")
        if not isinstance(source_url, str) or not source_url.startswith("https://github.com/"):
            errors.append(f"{prefix}.source_url must be a public GitHub URL")
        display_value = item.get("display_value")
        if not isinstance(display_value, str) or not ROUNDED_DISPLAY.fullmatch(display_value):
            errors.append(f"{prefix}.display_value must be a rounded display such as 46.5k, not an exact integer")
        if item.get("display_unit") != "stars":
            errors.append(f"{prefix}.display_unit must be stars")
        if not isinstance(item.get("default_branch"), str) or not item["default_branch"]:
            errors.append(f"{prefix}.default_branch must be non-empty")
        evidence = item.get("visible_file_or_resource_evidence")
        if not isinstance(evidence, list) or not evidence:
            errors.append(f"{prefix}.visible_file_or_resource_evidence must be non-empty")
        else:
            for evidence_index, resource in enumerate(evidence):
                if not isinstance(resource, dict) or resource.get("visible") is not True or not resource.get("label"):
                    errors.append(f"{prefix}.visible_file_or_resource_evidence[{evidence_index}] must mark a visible label")
        # A future extension must not silently turn this display-only record into API data.
        if "stars" in item or "exact_stars" in item:
            errors.append(f"{prefix} cannot carry an exact star count")
    return errors


def main() -> int:
    report = json.loads(REPORT_PATH.read_text(encoding="utf-8"))
    failures: list[str] = []
    # Fixed test clock for reproducibility, not a claimed acquisition time.
    as_of = datetime(2026, 9, 30, 16, tzinfo=timezone.utc)

    def check(name: str, candidate: dict[str, Any], clock: datetime = as_of,
              expected_error: str | None = None) -> None:
        actual = validate_report(candidate, clock)
        expected = [expected_error] if expected_error else []
        if actual != expected:
            failures.append(f"{name}: expected {expected}, got {actual}")
        else:
            print(f"PASS: {name}")

    check("public HTML fallback fixture", report)
    for value in (46500, "46500"):
        exact_integer = copy.deepcopy(report)
        exact_integer["repositories"][0]["display_value"] = value
        check(f"exact display_value {value!r} is rejected", exact_integer,
              expected_error="repositories[0].display_value must be a rounded display such as 46.5k, not an exact integer")
    for field in ("stars", "exact_stars"):
        exact_count = copy.deepcopy(report)
        exact_count["repositories"][0][field] = 46500
        check(f"{field} count field is rejected", exact_count,
              expected_error="repositories[0] cannot carry an exact star count")

    next_day = copy.deepcopy(report)
    next_day["snapshot_date"] = "2026-10-01"
    check("future UTC day is rejected", next_day,
          expected_error="snapshot_date cannot be in the future in snapshot_timezone")
    next_day["snapshot_timezone"] = "Asia/Shanghai"
    check("Shanghai next day equals UTC current day", next_day)
    check("comparison clock timezone does not change the result", next_day,
          clock=as_of.astimezone(ZoneInfo("Asia/Shanghai")))
    check("one microsecond before Shanghai midnight is future", next_day,
          clock=datetime(2026, 9, 30, 15, 59, 59, 999999, tzinfo=timezone.utc),
          expected_error="snapshot_date cannot be in the future in snapshot_timezone")
    next_day["snapshot_date"] = "2026-10-02"
    check("future Shanghai day is rejected", next_day,
          expected_error="snapshot_date cannot be in the future in snapshot_timezone")
    check("naive comparison clock is rejected", report, clock=as_of.replace(tzinfo=None),
          expected_error="as_of must be a timezone-aware datetime")
    for value in (None, "Invalid/Timezone"):
        invalid_zone = copy.deepcopy(report)
        invalid_zone["snapshot_timezone"] = value
        check(f"invalid timezone {value!r} is rejected", invalid_zone,
              expected_error="snapshot_timezone must be a valid IANA timezone")

    if failures:
        for failure in failures:
            print(f"FAIL: {failure}")
        return 1
    print("PASS: deterministic public HTML fallback validation")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
