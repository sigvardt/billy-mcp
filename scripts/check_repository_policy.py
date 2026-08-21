#!/usr/bin/env python3
"""Reject committed credentials and browser evidence before CI or release."""

from __future__ import annotations

import argparse
import re
import subprocess
from pathlib import Path

FORBIDDEN_SUFFIXES = (".har", ".trace.zip", ".pem", ".key")
FORBIDDEN_PARTS = {
    "chrome-profile",
    "downloads",
    "playwright-report",
    "rendered-frames",
    "screenshots",
    "test-results",
    "vision-evidence",
}
SECRET_ASSIGNMENT = re.compile(
    r"(?i)(?:billy_api_token|password|totp|cookie|authorization)\s*[:=]\s*['\"]?(?!\$\{|os\.environ|env\[)[A-Za-z0-9_./+=-]{12,}"
)
TEXT_SUFFIXES = {".md", ".py", ".toml", ".yaml", ".yml", ".json", ".txt"}


def tracked_paths(root: Path) -> list[Path]:
    """Return repository-managed files without walking ignored local state."""

    result = subprocess.run(
        ["git", "-C", str(root), "ls-files", "-z"],
        check=True,
        capture_output=True,
    )
    return [root / item for item in result.stdout.decode().split("\0") if item]


def violations(root: Path) -> list[str]:
    """Return every committed artifact that violates the public repository policy."""

    findings: list[str] = []
    for path in tracked_paths(root):
        relative = path.relative_to(root)
        # The index retains a path during a safe working-tree rename or deletion;
        # only files currently present can leak from the project tree.
        if not path.is_file():
            continue
        if path.suffix in FORBIDDEN_SUFFIXES or any(
            part in FORBIDDEN_PARTS for part in relative.parts
        ):
            findings.append(f"forbidden artifact: {relative}")
            continue
        if path.suffix not in TEXT_SUFFIXES:
            continue
        try:
            content = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            findings.append(f"non-UTF-8 text artifact: {relative}")
            continue
        if SECRET_ASSIGNMENT.search(content):
            findings.append(f"possible committed secret: {relative}")
    return findings


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--release", action="store_true", help="reserved for release-only checks")
    parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    findings = violations(root)
    if findings:
        print("Repository policy violations:")
        print("\n".join(f"- {finding}" for finding in findings))
        return 1
    print("Repository policy checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
