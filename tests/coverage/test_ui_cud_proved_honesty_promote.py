"""Owner 58D7D0E1: accepted CUD rows leave honesty red only until proved."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from types import ModuleType
from typing import Any, Final

from billy_mcp.vision_evidence import (
    VisionEvidenceRecord,
    qualifies_for_coverage_vision,
)

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

GREEN_FIELDS: Final[tuple[str, ...]] = ("implemented", "live_tested", "vision_verified")
PROVED_STATUS: Final[str] = "preview_execute"

PROVED_ROWS: Final[dict[str, tuple[str, str]]] = {
    "ui.parity.contacts.create": (
        "ui_clients_create_preview",
        "tmp/vision-records/ui_contacts_writes.json",
    ),
    "ui.parity.contacts.update": (
        "ui_clients_update_preview",
        "tmp/vision-records/ui_contacts_writes.json",
    ),
    "ui.parity.contacts.delete": (
        "ui_clients_delete_preview",
        "tmp/vision-records/ui_contacts_writes.json",
    ),
    "ui.parity.bills.create": (
        "ui_bills_create_preview",
        "tmp/vision-records/ui_bills_writes.json",
    ),
    "ui.parity.bills.update": (
        "ui_bills_update_preview",
        "tmp/vision-records/ui_bills_writes.json",
    ),
    "ui.parity.bills.delete": (
        "ui_bills_delete_preview",
        "tmp/vision-records/ui_bills_writes.json",
    ),
    "ui.parity.organizations.update": (
        "ui_organizations_update_preview",
        "tmp/vision-records/ui_organizations_writes.json",
    ),
    "ui.parity.invoices.create": (
        "ui_invoices_create_preview",
        "tmp/vision-records/ui_invoices_writes.json",
    ),
    "ui.parity.invoices.update": (
        "ui_invoices_update_preview",
        "tmp/vision-records/ui_invoices_writes.json",
    ),
    "ui.parity.invoices.delete": (
        "ui_invoices_delete_preview",
        "tmp/vision-records/ui_invoices_writes.json",
    ),
    "ui.parity.products.create": (
        "ui_products_create_preview",
        "tmp/vision-records/ui_products_writes.json",
    ),
}

REMAINING_HONESTY_IDS: Final[frozenset[str]] = frozenset(
    {
        "ui.parity.files.create",
        "ui.parity.daybooks.create",
        "ui.parity.daybooks.delete",
        "ui.parity.daybookTransactions.create",
        "ui.parity.transactions.create",
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


def _rows() -> dict[str, dict[str, Any]]:
    document = checker.load_document(ROOT / "coverage" / "ui_workflows_manifest.yaml")
    return {str(row["id"]): row for row in document["workflows"]}


def test_proved_honesty_rows_are_preview_execute_and_green() -> None:
    """Given accepted CUD vision, When reading coverage, Then the 11 rows are green."""

    rows = _rows()
    registered = checker.registered_domain_tools(ROOT)
    missing = sorted(set(PROVED_ROWS) - set(rows))
    assert missing == [], f"proved set missing from UI manifest: {missing}"

    for row_id, (preview, record_rel) in PROVED_ROWS.items():
        row = rows[row_id]
        record = VisionEvidenceRecord.model_validate_json(
            (ROOT / record_rel).read_text(encoding="utf-8")
        )
        assert qualifies_for_coverage_vision(record) is True
        assert row["tool_name"] == preview
        execute_name = f"{preview.removesuffix('_preview')}_execute"
        assert execute_name in registered, f"{row_id}: missing {execute_name}"
        assert row["parity_status"] == PROVED_STATUS
        for field in GREEN_FIELDS:
            assert row[field] is True, f"{row_id}: {field} is {row[field]!r}"
        assert row["vision_evidence"] is None


def test_remaining_honesty_set_is_empty_after_owner_scope() -> None:
    """Given FE6FA4B1, When reading the honesty set, Then the five moved to owner scope."""

    generator = _load_script_module("generate_coverage_report")
    assert generator.UI_CUD_PARITY_OPEN_ONLY_HONESTY_IDS == frozenset()
    assert set(generator.UI_RESIDUAL_WRITE_OWNER_SCOPE) == set(REMAINING_HONESTY_IDS)
    rows = _rows()
    for row_id in sorted(REMAINING_HONESTY_IDS):
        row = rows[row_id]
        assert row["parity_status"] == "out_of_scope_by_user"
        for field in GREEN_FIELDS:
            assert row[field] is False, f"{row_id}: {field} greened"


def test_promoted_coverage_is_complete_under_owner_scope() -> None:
    """Given the 11-row promote plus owner skips, When reading status, Then complete is true."""

    status = checker.load_document(ROOT / "coverage" / "status.json")
    assert status["complete"] is True
