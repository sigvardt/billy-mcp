"""Owner FE6FA4B1: residual files/ledger writes are out_of_scope_by_user."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from types import ModuleType
from typing import Any, Final

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

GREEN_FIELDS: Final[tuple[str, ...]] = ("implemented", "live_tested", "vision_verified")

SCOPED_ROWS: Final[dict[str, str]] = {
    "ui.parity.daybookTransactions.create": "GODKEND_HIGH_IMPACT_PROHIBITED",
    "ui.parity.transactions.create": "GODKEND_HIGH_IMPACT_PROHIBITED",
    "ui.parity.files.create": "FILES_NO_UI_DELETE",
    "ui.parity.daybooks.create": "DAYBOOKS_UNIQUE_PERSIST_ABSENT",
    "ui.parity.daybooks.delete": "DAYBOOKS_UNIQUE_PERSIST_ABSENT",
}
UNIMPLEMENTED_UI_OWNER_SCOPE: Final[frozenset[str]] = frozenset(
    {
        "ui.discovery.annual_reports",
        *SCOPED_ROWS,
    }
)


def _load_script_module(name: str) -> ModuleType:
    spec = importlib.util.spec_from_file_location(name, SCRIPTS / f"{name}.py")
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


checker = _load_script_module("check_coverage")
generator = _load_script_module("generate_coverage_report")


def _rows() -> dict[str, dict[str, Any]]:
    document = checker.load_document(ROOT / "coverage" / "ui_workflows_manifest.yaml")
    return {str(row["id"]): row for row in document["workflows"]}


def test_residual_write_rows_are_owner_out_of_scope() -> None:
    """Given residual files and ledger writes, When reading coverage, Then they are owner-scoped."""

    rows = _rows()
    missing = sorted(set(SCOPED_ROWS) - set(rows))
    assert missing == [], f"residual scope set missing from UI manifest: {missing}"

    for row_id, scope_code in SCOPED_ROWS.items():
        row = rows[row_id]
        qual: dict[str, Any] = dict(row.get("qualification") or {})
        assert qual.get("kind") == "out_of_scope_by_user", f"{row_id}: missing qualification"
        assert qual.get("scope_code") == scope_code
        assert qual.get("tools_allowed") is False
        assert qual.get("not_applicable_decision") == "rejected"
        assert qual.get("owner_decision_ref") == "radio:FE6FA4B1"
        assert row["parity_status"] == "out_of_scope_by_user"
        assert row["parity_status"] != "not_applicable"
        assert row["vision_evidence"] is None
        for field in GREEN_FIELDS:
            assert row[field] is False, f"{row_id}: {field} is {row[field]!r}"
        evidence = str(row.get("evidence") or "")
        assert "radio:FE6FA4B1" in evidence
        assert generator.is_owner_out_of_scope(row) is True


def test_residual_owner_scope_does_not_block_complete() -> None:
    """Given residual owner scope, When reading status, Then complete is true."""

    status = checker.load_document(ROOT / "coverage" / "status.json")
    assert status["complete"] is True
    assert status["qualification"]["blocker"] == "No manifest qualification blockers remain."


def test_unimplemented_ui_rows_are_exactly_owner_scoped() -> None:
    """Unimplemented UI rows are exactly the six owner-scoped rows."""

    document = checker.load_document(ROOT / "coverage" / "ui_workflows_manifest.yaml")
    workflows = list(document["workflows"])
    unimplemented = [row for row in workflows if row.get("implemented") is not True]
    ids = {str(row["id"]) for row in unimplemented}
    assert ids == set(UNIMPLEMENTED_UI_OWNER_SCOPE)
    assert len(unimplemented) == 6
    for row in unimplemented:
        assert generator.is_owner_out_of_scope(row) is True
        assert generator.row_is_qualified(row, generator.UI_QUALIFICATION_FIELDS) is True
    unqualified = [
        str(row["id"])
        for row in workflows
        if not generator.row_is_qualified(row, generator.UI_QUALIFICATION_FIELDS)
    ]
    assert unqualified == []
