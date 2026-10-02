#!/usr/bin/env python3
"""Deterministic structural checks for the Git-only decision gates."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REFERENCE = ROOT / "references" / "decision-gates.md"
FIXTURES = ROOT / "fixtures" / "decision-gates"


def main() -> int:
    errors: list[str] = []
    text = REFERENCE.read_text(encoding="utf-8") if REFERENCE.is_file() else ""
    required = (
        "git rev-parse --show-toplevel", "git status --short --branch", "git remote -v",
        "observe", "plan", "local_write", "commit", "remote_write", "release", "research",
        "user", "repo_fact", "inference", "bounded_default", "unverified",
        "P0", "P1", "1–3", "READY", "WAITING FOR ANSWER", "CONFIRMATION REQUIRED",
        "BLOCKED", "COMPLETE", "Status", "Changed", "Why / evidence", "Risk & rollback",
        "Unknowns / blocked choice", "Next question", "252 verified documents",
        "10,000 candidate projects still pending", "Cleanup", "GitHub upload",
        "Release prep", "Mature-repository research",
    )
    for fragment in required:
        if fragment not in text:
            errors.append(f"reference missing {fragment!r}")
    files = sorted(FIXTURES.glob("*.json"))
    if {p.stem for p in files} != {"cleanup", "github-upload", "release-prep", "mature-research"}:
        errors.append("decision-gate fixtures are incomplete")
    for path in files:
        try:
            record = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            errors.append(f"{path.name}: invalid JSON ({exc})")
            continue
        if not record.get("classification"):
            errors.append(f"{path.name}: classification is empty")
        if record.get("name") == "mature-repository-research":
            if record.get("verified_documents") != 252 or record.get("candidate_projects_status") != "pending":
                errors.append("research fixture changed preserved counts")
            if record.get("remote_writes") is not False:
                errors.append("research fixture must remain read-only")
        if record.get("name") == "github-upload" and set(record.get("forbidden_inferences", [])) != {"origin", "main", "public"}:
            errors.append("upload fixture must forbid origin/main/public inference")
    if errors:
        for error in errors:
            print(f"FAIL: {error}")
        return 1
    print(f"PASS: decision-gate reference and {len(files)} fixtures")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
