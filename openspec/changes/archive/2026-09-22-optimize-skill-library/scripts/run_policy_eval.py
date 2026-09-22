"""Compare old and new obsidian-rag policy behavior through Claude CLI.

This evaluates routing and evidence-policy decisions only. It does not provide
an MCP server, so it must not be reported as an end-to-end retrieval test.
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path


def read_old_snapshot(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    start = text.index("```markdown") + len("```markdown")
    end = text.index("```", start)
    return text[start:end].strip()


def run_case(skill_text: str, prompt: str) -> dict:
    instruction = (
        "以下是本次评测要遵循的 Skill 规则：\n\n"
        f"{skill_text}\n\n"
        "根据这些规则分析用户请求，不要执行任何工具。"
        "只输出 JSON：{\"trigger\":\"yes|no\",\"calls\":[\"...\"],"
        "\"evidence_policy\":\"...\",\"answer_policy\":\"...\"}。"
        f"\n用户请求：{prompt}"
    )
    claude_wrapper = shutil.which("claude.cmd") or shutil.which("claude.ps1") or shutil.which("claude")
    if not claude_wrapper:
        return {"error": "Claude CLI wrapper not found on PATH"}
    if claude_wrapper.lower().endswith(".ps1"):
        command = [
            "powershell.exe",
            "-NoProfile",
            "-ExecutionPolicy",
            "Bypass",
            "-File",
            claude_wrapper,
        ]
    else:
        command = [claude_wrapper]
    command += [
        "-p",
        "--bare",
        "--no-session-persistence",
        "--output-format",
        "json",
        "--tools",
        "",
    ]
    completed = subprocess.run(
        command,
        input=instruction,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=120,
    )
    if completed.returncode != 0:
        return {"error": completed.stderr.strip() or completed.stdout.strip()}
    try:
        envelope = json.loads(completed.stdout)
        result = envelope.get("result", "")
        return {"response": json.loads(result), "usage": envelope.get("usage", {})}
    except (json.JSONDecodeError, TypeError) as exc:
        return {"error": f"invalid CLI JSON: {exc}", "raw": completed.stdout}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=Path, default=Path(__file__).parents[4])
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    repo = args.repo.resolve()
    new_skill = (repo / "obsidian-rag" / "SKILL.md").read_text(encoding="utf-8")
    old_skill = read_old_snapshot(
        repo / "openspec" / "changes" / "optimize-skill-library" / "baseline" / "obsidian-rag.SNAPSHOT.md"
    )
    train = json.loads((repo / "obsidian-rag" / "evals" / "evals.json").read_text(encoding="utf-8"))["evals"]
    holdout = json.loads((repo / "obsidian-rag" / "evals" / "holdout.json").read_text(encoding="utf-8"))["evals"]

    results = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "scope": "routing and evidence policy only; no MCP retrieval",
        "cases": [],
    }
    for split, cases in (("train", train), ("holdout", holdout)):
        for case in cases:
            row = {
                "split": split,
                "id": case["id"],
                "expected_trigger": case["expected_trigger"],
                "prompt": case["prompt"],
                "old": run_case(old_skill, case["prompt"]),
                "new": run_case(new_skill, case["prompt"]),
            }
            for version in ("old", "new"):
                response = row[version].get("response", {})
                actual = response.get("trigger") == "yes"
                row[f"{version}_trigger_pass"] = actual == case["expected_trigger"]
            results["cases"].append(row)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {len(results['cases'])} cases to {args.output}")


if __name__ == "__main__":
    main()
