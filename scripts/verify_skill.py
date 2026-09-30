#!/usr/bin/env python3
"""Run side-effect-free checks for the git-composer skill package.

This checks package invariants only. It does not run Git mutations, publish a
repository, or claim that a model followed the instructions correctly.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path


def fail(message: str, failures: list[str]) -> None:
    failures.append(message)
    print(f"FAIL: {message}")


def main() -> int:
    root = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path(__file__).resolve().parents[1]
    failures: list[str] = []

    skill_md = root / "SKILL.md"
    ui_yaml = root / "agents" / "openai.yaml"
    references = root / "references"

    for path in (skill_md, ui_yaml, references):
        if not path.exists():
            fail(f"missing required path: {path.relative_to(root)}", failures)

    if not failures:
        content = skill_md.read_text(encoding="utf-8")
        frontmatter = re.match(r"^---\n(.*?)\n---", content, re.DOTALL)
        if not frontmatter:
            fail("SKILL.md has no valid YAML frontmatter block", failures)
        else:
            header = frontmatter.group(1)
            name_match = re.search(r"^name:\s*([^\n]+)$", header, re.MULTILINE)
            description_match = re.search(r"^description:\s*(.+)$", header, re.MULTILINE)
            if not name_match:
                fail("frontmatter is missing name", failures)
            elif name_match.group(1).strip().strip('"\'') != root.name:
                fail("frontmatter name does not match the skill directory", failures)
            if not description_match or not description_match.group(1).strip():
                fail("frontmatter is missing a non-empty description", failures)

        for reference in sorted(set(re.findall(r"references/[A-Za-z0-9_.-]+\.md", content))):
            if not (root / reference).is_file():
                fail(f"broken SKILL.md reference: {reference}", failures)

    if ui_yaml.exists():
        ui = ui_yaml.read_text(encoding="utf-8")
        for key in ("display_name", "short_description", "default_prompt"):
            if not re.search(rf"^\s+{key}:\s*['\"].+['\"]\s*$", ui, re.MULTILINE):
                fail(f"agents/openai.yaml is missing a quoted interface.{key}", failures)
        name = root.name
        if f"${name}" not in ui:
            fail(f"agents/openai.yaml default_prompt must mention ${name}", failures)

    if failures:
        print(f"{len(failures)} check(s) failed.")
        return 1

    print("PASS: skill package structure, references, and UI metadata are consistent.")
    print("REVIEW: manually exercise representative Chinese and English requests; static checks cannot prove model behavior or repository tests.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
