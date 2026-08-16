"""Open-only UI chrome cannot complete create/update/delete parity rows."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from types import ModuleType

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

OPEN_ONLY_STATUSES = frozenset(
    {
        "form_open_only",
        "create_chrome_open_only",
        "delete_chrome_open_only",
    }
)

CUD_PARITY_IDS = frozenset(
    {
        "ui.parity.bills.create",
        "ui.parity.bills.update",
        "ui.parity.bills.delete",
        "ui.parity.contacts.create",
        "ui.parity.contacts.update",
        "ui.parity.contacts.delete",
        "ui.parity.daybooks.create",
        "ui.parity.daybooks.delete",
        "ui.parity.daybookTransactions.create",
        "ui.parity.files.create",
        "ui.parity.invoices.create",
        "ui.parity.invoices.update",
        "ui.parity.invoices.delete",
        "ui.parity.organizations.update",
        "ui.parity.products.create",
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


def test_open_only_tools_cannot_complete_cud_parity_rows() -> None:
    """Owner 96908DC6 / E004E7D5: open-only chrome is not a finished write."""

    ui_manifest = checker.load_document(ROOT / "coverage" / "ui_workflows_manifest.yaml")
    rows = {str(row["id"]): row for row in ui_manifest["workflows"]}
    missing = sorted(CUD_PARITY_IDS - set(rows))
    assert missing == [], f"gate set missing from UI manifest: {missing}"

    false_complete: list[str] = []
    for row_id in sorted(CUD_PARITY_IDS):
        row = rows[row_id]
        if row.get("parity_status") not in OPEN_ONLY_STATUSES:
            continue
        if row.get("implemented") is True and row.get("live_tested") is True:
            false_complete.append(row_id)
    assert false_complete == [], (
        "open-only CUD parity rows must not be implemented and live_tested: "
        + ", ".join(false_complete)
    )


def test_no_ui_preview_or_execute_tools_are_registered() -> None:
    """The 52 ui_* tools are open/list/shell only until write children land."""

    registered = checker.registered_domain_tools(ROOT)
    ui_write_tools = sorted(
        name
        for name in registered
        if name.startswith("ui_") and name.endswith(("_preview", "_execute"))
    )
    assert ui_write_tools == []
