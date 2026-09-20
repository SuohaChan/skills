"""Validate the repository shape and metadata of every Skill."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


SKILL_NAME = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


def parse_frontmatter(path: Path) -> tuple[dict[str, str], list[str]]:
    errors: list[str] = []
    lines = path.read_text(encoding="utf-8").splitlines()
    if not lines or lines[0].strip() != "---":
        return {}, [f"{path}: missing YAML frontmatter"]

    metadata: dict[str, str] = {}
    closing = None
    for index, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            closing = index
            break
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if ":" not in line:
            errors.append(f"{path}:{index + 1}: invalid frontmatter line")
            continue
        key, value = line.split(":", 1)
        metadata[key.strip()] = value.strip().strip("'\"")

    if closing is None:
        errors.append(f"{path}: frontmatter is not closed")
    return metadata, errors


def validate_skill(skill_dir: Path) -> list[str]:
    skill_file = skill_dir / "SKILL.md"
    metadata, errors = parse_frontmatter(skill_file)

    name = metadata.get("name", "")
    description = metadata.get("description", "")
    if not name:
        errors.append(f"{skill_file}: missing name")
    elif not SKILL_NAME.fullmatch(name):
        errors.append(f"{skill_file}: name must be lowercase kebab-case: {name}")
    elif name != skill_dir.name:
        errors.append(f"{skill_file}: name {name!r} differs from directory {skill_dir.name!r}")
    if not description:
        errors.append(f"{skill_file}: missing description")

    evals = skill_dir / "evals" / "evals.json"
    if evals.exists():
        try:
            payload = json.loads(evals.read_text(encoding="utf-8"))
        except json.JSONDecodeError as error:
            errors.append(f"{evals}: invalid JSON: {error}")
        else:
            if not isinstance(payload, dict) or payload.get("skill_name") != name:
                errors.append(f"{evals}: skill_name must match {name!r}")
            if not isinstance(payload.get("evals"), list):
                errors.append(f"{evals}: evals must be a list")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "root", nargs="?", type=Path, default=Path(__file__).resolve().parents[1]
    )
    args = parser.parse_args()
    root = args.root.resolve()

    skill_dirs = sorted(path.parent for path in root.glob("*/SKILL.md"))
    if not skill_dirs:
        print(f"No Skills found under {root}", file=sys.stderr)
        return 1

    errors: list[str] = []
    names: dict[str, Path] = {}
    for skill_dir in skill_dirs:
        errors.extend(validate_skill(skill_dir))
        metadata, _ = parse_frontmatter(skill_dir / "SKILL.md")
        name = metadata.get("name")
        if name:
            previous = names.get(name)
            if previous:
                errors.append(f"duplicate Skill name {name!r}: {previous} and {skill_dir}")
            names[name] = skill_dir

    if errors:
        print("Skill validation failed:")
        print("\n".join(f"- {error}" for error in errors))
        return 1

    print(f"Validated {len(skill_dirs)} Skills: {', '.join(sorted(names))}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

