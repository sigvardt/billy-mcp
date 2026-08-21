"""Proof that the node test script accepts ui-full without live API traffic."""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
NODE_TEST = ROOT / "scripts" / "test.sh"


def test_ui_full_runs_ui_without_live_api_and_release_gates(tmp_path: Path) -> None:
    call_log = tmp_path / "uv-calls.txt"
    fake_bin = tmp_path / "bin"
    fake_bin.mkdir()
    fake_uv = fake_bin / "uv"
    fake_uv.write_text(
        '#!/usr/bin/env bash\nprintf "%s\\n" "$*" >> "$BILLY_TEST_CALL_LOG"\n',
        encoding="utf-8",
    )
    fake_uv.chmod(0o755)

    result = subprocess.run(
        ["bash", str(NODE_TEST)],
        cwd=ROOT,
        env={
            **os.environ,
            "BILLY_TEST_MODE": "ui-full",
            "BILLY_TEST_CALL_LOG": str(call_log),
            "PATH": f"{fake_bin}{os.pathsep}{os.environ['PATH']}",
        },
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    assert call_log.read_text(encoding="utf-8").splitlines() == [
        "run pytest -m not live_api",
        "run python scripts/check_coverage.py --require-complete",
        "run python scripts/check_repository_policy.py --release",
    ]


def test_unknown_billy_test_mode_exits_2() -> None:
    result = subprocess.run(
        ["bash", str(NODE_TEST)],
        cwd=ROOT,
        env={**os.environ, "BILLY_TEST_MODE": "not-a-mode"},
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 2
    assert "Unknown BILLY_TEST_MODE: not-a-mode" in result.stderr
