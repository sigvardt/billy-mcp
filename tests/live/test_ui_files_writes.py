"""Live UI files create gate. Submit stays held until root radios a live slot."""

from __future__ import annotations

from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
_WIKI = _REPO_ROOT / "wiki" / "ui_files_writes.md"


def test_records_live_slot_hold_without_submit() -> None:
    """Given parent radio 5D46AAC4, record the hold and do not execute submit."""

    page = " ".join(_WIKI.read_text(encoding="utf-8").split())

    assert "5D46AAC4" in page
    assert "contacts has the current live slot" in page
    assert "must not run a live execute submit" in page
    assert "not an unsafe skipped submit" in page
    assert "ui_files_create_preview" in page
    assert "ui_files_create_execute" in page
