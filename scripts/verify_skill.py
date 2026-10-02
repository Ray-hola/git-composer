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
    readme = root / "README.md"
    english_readme = root / "README.en.md"
    license_file = root / "LICENSE"
    ui_yaml = root / "agents" / "openai.yaml"
    references = root / "references"
    reporting = references / "reporting-templates.md"

    for path in (skill_md, readme, english_readme, license_file, ui_yaml, references, reporting):
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

    if readme.exists():
        readme_text = readme.read_text(encoding="utf-8")
        required_sections = ("在 Codex 中开始", "第一次成功的判据", "你可以直接这样说", "安全与恢复", "证据与边界", "维护者参考")
        for section in required_sections:
            if section not in readme_text:
                fail(f"README.md is missing required novice section: {section}", failures)
        for phrase in ("252 个去重证据文档", "--ff-only", "未验证", "不需要终端或 Git", "READY / WAITING FOR ANSWER / CONFIRMATION REQUIRED / BLOCKED / COMPLETE", "references/codex-onboarding.md"):
            if phrase not in readme_text:
                fail(f"README.md is missing evidence or safety phrase: {phrase}", failures)
        for link in (
            "references/git-workflows.md",
            "references/readme-design.md",
            "references/research-and-distillation.md",
            "references/reporting-templates.md",
            "fixtures/corpus/github-public-doc-evidence-batch-4.json",
        ):
            if link not in readme_text:
                fail(f"README.md is missing deep link: {link}", failures)
        public_readme = readme_text.split("<details>", 1)[0]
        if re.search(r"(?m)^git\s+(clone|status|pull|commit|push)\b", public_readme):
            fail("README.md public onboarding contains a command-line Git step", failures)

    if english_readme.exists():
        english_text = english_readme.read_text(encoding="utf-8")
        for phrase in ("Start in Codex", "The first successful task", "No terminal or Git knowledge is required", "Codex onboarding", "MIT License"):
            if phrase not in english_text:
                fail(f"README.en.md is missing onboarding phrase: {phrase}", failures)
        public_english = english_text.split("<details>", 1)[0]
        if re.search(r"(?m)^git\s+(clone|status|pull|commit|push)\b", public_english):
            fail("README.en.md public onboarding contains a command-line Git step", failures)

    if license_file.exists() and not license_file.read_text(encoding="utf-8").startswith("MIT License\n"):
        fail("LICENSE is not the selected MIT license", failures)

    if reporting.exists():
        reporting_text = reporting.read_text(encoding="utf-8")
        for field in ("状态", "范围", "改动", "验证", "证据", "风险与恢复", "未知", "下一步", "进度消息", "最终交付块"):
            if field not in reporting_text:
                fail(f"reporting-templates.md is missing field or section: {field}", failures)

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
