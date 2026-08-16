"""Proof that the node test script accepts ui-full without live API traffic."""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
NODE_TEST = ROOT / ".fractal" / "main.billy_complete" / "scripts" / "test.sh"


def test_node_test_script_defines_ui_full_without_live_api() -> None:
    text = NODE_TEST.read_text(encoding="utf-8")
    assert "ui-full)" in text
    assert 'pytest -m "not live_api"' in text
    assert "--require-complete" in text
    assert "check_repository_policy.py --release" in text
    assert "Unknown BILLY_TEST_MODE" in text


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
