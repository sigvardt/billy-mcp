"""Keep unit bills dumps off the live owner-only inspect paths."""

from __future__ import annotations

from pathlib import Path

import pytest


@pytest.fixture(autouse=True)
def isolate_bills_inspect_dumps(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from billy_mcp.ui_writes import bills_form, bills_vendor

    monkeypatch.setattr(bills_form, "CREATE_PRE_SUBMIT_DUMP", tmp_path / "create.json")
    monkeypatch.setattr(bills_form, "PRE_SUBMIT_DUMP", tmp_path / "update.json")
    monkeypatch.setattr(bills_form, "_PERSIST_DUMP", tmp_path / "persist.json")
    monkeypatch.setattr(bills_vendor, "VENDOR_CHROME_DUMP", tmp_path / "vendor.json")
    monkeypatch.setattr(bills_vendor, "VENDOR_WRAPPER_DUMP", tmp_path / "wrapper.json")
    monkeypatch.setattr(bills_vendor, "DATE_CHROME_DUMP", tmp_path / "date.json")
