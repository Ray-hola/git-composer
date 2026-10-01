#!/usr/bin/env python3
"""Deterministic, dependency-free checks for research record fixtures."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "schemas" / "research-distillation-records.schema.json"
FIXTURE_DIR = ROOT / "fixtures" / "research"


class ValidationError(Exception):
    pass


def resolve_ref(schema: dict[str, Any], ref: str) -> dict[str, Any]:
    if not ref.startswith("#/"):
        raise ValidationError(f"unsupported external ref: {ref}")
    node: Any = schema
    for part in ref[2:].split("/"):
        node = node[part]
    return node


def type_matches(value: Any, expected: str | list[str]) -> bool:
    expected_types = [expected] if isinstance(expected, str) else expected
    for item in expected_types:
        if item == "null" and value is None:
            return True
        if item == "object" and isinstance(value, dict):
            return True
        if item == "array" and isinstance(value, list):
            return True
        if item == "string" and isinstance(value, str):
            return True
        if item == "boolean" and isinstance(value, bool):
            return True
        if item == "integer" and isinstance(value, int) and not isinstance(value, bool):
            return True
        if item == "number" and isinstance(value, (int, float)) and not isinstance(value, bool):
            return True
    return False


def validate(value: Any, schema: dict[str, Any], root_schema: dict[str, Any], path: str = "$") -> None:
    if "$ref" in schema:
        validate(value, resolve_ref(root_schema, schema["$ref"]), root_schema, path)
        return
    if "oneOf" in schema:
        for option in schema["oneOf"]:
            try:
                validate(value, option, root_schema, path)
                return
            except ValidationError:
                pass
        raise ValidationError(f"{path}: no oneOf branch matched")
    if "const" in schema and value != schema["const"]:
        raise ValidationError(f"{path}: expected {schema['const']!r}")
    if "type" in schema and not type_matches(value, schema["type"]):
        raise ValidationError(f"{path}: wrong type")
    if "enum" in schema and value not in schema["enum"]:
        raise ValidationError(f"{path}: value is not in enum")
    if isinstance(value, str):
        if len(value) < schema.get("minLength", 0):
            raise ValidationError(f"{path}: string is too short")
        if "pattern" in schema and not re.search(schema["pattern"], value):
            raise ValidationError(f"{path}: string does not match pattern")
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        if value < schema.get("minimum", value) or value > schema.get("maximum", value):
            raise ValidationError(f"{path}: number is out of range")
    if isinstance(value, list):
        if len(value) < schema.get("minItems", 0):
            raise ValidationError(f"{path}: too few items")
        if "items" in schema:
            for index, item in enumerate(value):
                validate(item, schema["items"], root_schema, f"{path}[{index}]")
    if isinstance(value, dict):
        required = schema.get("required", [])
        missing = [key for key in required if key not in value]
        if missing:
            raise ValidationError(f"{path}: missing {', '.join(missing)}")
        properties = schema.get("properties", {})
        if schema.get("additionalProperties") is False:
            unknown = sorted(set(value) - set(properties))
            if unknown:
                raise ValidationError(f"{path}: unknown fields {', '.join(unknown)}")
        for key, child_schema in properties.items():
            if key in value:
                validate(value[key], child_schema, root_schema, f"{path}.{key}")


def validate_domain_invariants(record: dict[str, Any]) -> None:
    if record["record_type"] != "rule_candidate":
        return
    safety = record["safety"]
    gate = record["confirmation_gate"]
    if safety["side_effect_level"] in {"local_destructive", "history_rewrite", "remote_write"}:
        if not safety["confirmation_required"] or not gate["required"]:
            raise ValidationError("destructive or remote rules require an explicit confirmation gate")
        if gate["when"] == "never" or not gate.get("question"):
            raise ValidationError("destructive or remote rules require a concrete confirmation question")
    if gate["required"] and gate["when"] == "never":
        raise ValidationError("a required gate cannot have when=never")


def main() -> int:
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    failures: list[str] = []
    fixtures = sorted(FIXTURE_DIR.glob("*.json"))
    if not fixtures:
        print("FAIL: no research fixtures found")
        return 1
    for fixture in fixtures:
        record = json.loads(fixture.read_text(encoding="utf-8"))
        expected_valid = fixture.name.startswith("valid-")
        try:
            validate(record, schema, schema)
            validate_domain_invariants(record)
            actual_valid = True
        except (ValidationError, KeyError, TypeError) as exc:
            actual_valid = False
            if expected_valid:
                failures.append(f"{fixture.name}: unexpected failure: {exc}")
        if actual_valid != expected_valid:
            failures.append(f"{fixture.name}: expected valid={expected_valid}, got {actual_valid}")
        else:
            print(f"PASS: {fixture.name}")
    if failures:
        for failure in failures:
            print(f"FAIL: {failure}")
        return 1
    print(f"PASS: {len(fixtures)} deterministic research fixtures")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
