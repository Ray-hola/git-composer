#!/usr/bin/env python3
"""Run offline structural, schema, planner, and safety checks."""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
FIXTURE_DIR = ROOT / "fixtures" / "corpus"


def run_check(command: list[str]) -> dict[str, Any]:
    completed = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, check=False)
    output = (completed.stdout + completed.stderr).strip()
    return {
        "command": command,
        "status": "passed" if completed.returncode == 0 else "failed",
        "exit_code": completed.returncode,
        "output_tail": output[-1000:],
    }


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def validate_plan(plan: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if plan.get("plan_type") != "corpus_sampling_plan":
        errors.append("plan_type is wrong")
    if plan.get("mode") != "dry-run" or plan.get("network_enabled") is not False:
        errors.append("evaluation plan must be offline dry-run")
    if plan.get("candidate_target") != 10000:
        errors.append("evaluation plan must use candidate target 10000")
    if sum(item.get("target_count", 0) for item in plan.get("partitions", [])) != plan.get("candidate_target"):
        errors.append("partition target counts do not sum to candidate target")
    if "10k-star" not in plan.get("target_meaning", ""):
        errors.append("plan must distinguish candidate count from 10k-star stratum")
    if plan.get("privacy", {}).get("raw_content_ingested") is not False:
        errors.append("plan must prohibit raw content ingestion")
    return errors


def validate_partition_fixture(plan_builder: Path) -> list[str]:
    fixture = load_json(FIXTURE_DIR / "partition-plan.json")
    command = [sys.executable, str(plan_builder), "--candidate-target", str(fixture["candidate_target"]), "--seed", str(fixture["seed"])]
    completed = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, check=False)
    if completed.returncode != 0:
        return [f"partition fixture command failed: {completed.stderr.strip()}"]
    plan = json.loads(completed.stdout)
    errors: list[str] = []
    actual_counts = {item["id"]: item["target_count"] for item in plan["partitions"]}
    if actual_counts != fixture["expected_counts"]:
        errors.append(f"partition counts differ: {actual_counts}")
    if [item["id"] for item in plan["partitions"]] != fixture["expected_partition_ids"]:
        errors.append("partition ordering differs")
    return errors


def validate_readme_contract() -> list[str]:
    readme = ROOT / "README.md"
    errors: list[str] = []
    if not readme.is_file():
        return ["README.md is missing"]
    text = readme.read_text(encoding="utf-8")
    required_fragments = {
        "codex_entry": "在 Codex 中开始",
        "expected_output": "第一次成功的判据",
        "status_block": "状态：READY / WAITING FOR ANSWER / CONFIRMATION REQUIRED / BLOCKED / COMPLETE",
        "evidence_labels": "未验证",
        "rollback": "安全与恢复",
        "reporting_templates": "references/reporting-templates.md",
        "maintenance_check": "scripts/evaluate_skill.py",
        "remote_target": "https://github.com/Ray-Hola/git-composer.git",
        "verified_count": "252 个去重证据文档",
        "no_cli": "不需要终端或 Git",
        "license": "MIT License",
    }
    for label, fragment in required_fragments.items():
        if fragment not in text:
            errors.append(f"README contract missing {label}: {fragment}")
    public_text = text.split("<details>", 1)[0]
    for forbidden in ("10,000 个候选项目目标仍为 pending", "许可证尚未决定", "No release", "no release"):
        if forbidden in public_text:
            errors.append(f"public README still exposes unresolved status: {forbidden}")
    research_reference = ROOT / "references" / "research-and-distillation.md"
    if not research_reference.is_file():
        errors.append("research reference is missing")
    else:
        research_text = research_reference.read_text(encoding="utf-8")
        for fragment in ("target.candidate_projects=10000", "target.status=pending"):
            if fragment not in research_text:
                errors.append(f"research reference missing internal fact: {fragment}")
    batch4 = load_json(FIXTURE_DIR / "github-public-doc-evidence-batch-4.json")
    cumulative = batch4.get("cumulative_progress", {}).get("cumulative_verified_unique_documents")
    if cumulative != 252:
        errors.append(f"batch-4 cumulative verified count changed: {cumulative!r}")
    return errors


def validate_holdout_fixture() -> list[str]:
    fixture = load_json(FIXTURE_DIR / "provenance-holdout.json")
    errors: list[str] = []
    if fixture.get("fixture_type") != "provenance_holdout":
        errors.append("wrong holdout fixture type")
    if fixture.get("holdout", {}).get("excluded_from_rule_fit") is not True:
        errors.append("holdout must be excluded from rule fitting")
    provenance = fixture.get("provenance", {})
    if not re.fullmatch(r"[0-9a-fA-F]{7,64}", provenance.get("commit_sha", "")):
        errors.append("holdout commit SHA is not pinned")
    if not re.fullmatch(r"[0-9a-fA-F]{64}", provenance.get("content_sha256", "")):
        errors.append("holdout content hash is not SHA-256")
    if fixture.get("raw_content_ingested") is not False:
        errors.append("holdout fixture must not ingest raw content")
    return errors


def main() -> int:
    checks: list[dict[str, Any]] = []
    checks.append(run_check([sys.executable, str(SCRIPTS / "verify_skill.py"), str(ROOT)]))
    checks.append(run_check([sys.executable, str(SCRIPTS / "test_research_schema.py")]))
    checks.append(run_check([sys.executable, str(SCRIPTS / "test_public_html_fallback.py")]))
    checks.append(run_check([sys.executable, str(SCRIPTS / "test_evidence_batch.py")]))
    checks.append(run_check([sys.executable, str(SCRIPTS / "test_evidence_batch_two.py")]))
    checks.append(run_check([sys.executable, str(SCRIPTS / "test_evidence_batch_three.py")]))
    checks.append(run_check([sys.executable, str(SCRIPTS / "test_evidence_batch_four.py")]))
    checks.append(run_check([sys.executable, str(SCRIPTS / "test_decision_gates.py")]))

    plan_command = [sys.executable, str(SCRIPTS / "build_corpus.py"), "--candidate-target", "10000", "--seed", "42"]
    first = subprocess.run(plan_command, cwd=ROOT, capture_output=True, text=True, check=False)
    second = subprocess.run(plan_command, cwd=ROOT, capture_output=True, text=True, check=False)
    plan_errors: list[str] = []
    if first.returncode or second.returncode:
        plan_errors.append("offline planner failed")
    else:
        first_plan = json.loads(first.stdout)
        second_plan = json.loads(second.stdout)
        if first_plan != second_plan:
            plan_errors.append("offline planner is not deterministic")
        plan_errors.extend(validate_plan(first_plan))
    checks.append({"name": "offline_plan", "status": "passed" if not plan_errors else "failed", "errors": plan_errors})

    partition_errors = validate_partition_fixture(SCRIPTS / "build_corpus.py")
    checks.append({"name": "partition_fixture", "status": "passed" if not partition_errors else "failed", "errors": partition_errors})
    holdout_errors = validate_holdout_fixture()
    checks.append({"name": "provenance_holdout_fixture", "status": "passed" if not holdout_errors else "failed", "errors": holdout_errors})
    readme_errors = validate_readme_contract()
    checks.append({"name": "readme_contract", "status": "passed" if not readme_errors else "failed", "errors": readme_errors})

    failed = [check for check in checks if check.get("status") == "failed"]
    report = {
        "report_type": "git-composer.skill-evaluation",
        "schema_version": 1,
        "status": "failed" if failed else "passed",
        "network_used": False,
        "raw_content_ingested": False,
        "checks": checks,
        "report_sha256": hashlib.sha256(json.dumps(checks, sort_keys=True).encode("utf-8")).hexdigest(),
    }
    output = json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    print(output, end="")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
