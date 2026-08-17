"""Durable CUD parity invariant: open-only chrome cannot green a write row."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from types import ModuleType
from typing import Any

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

GREEN_FIELDS = ("implemented", "live_tested", "vision_verified")


def _load_script_module(name: str) -> ModuleType:
    spec = importlib.util.spec_from_file_location(name, SCRIPTS / f"{name}.py")
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


checker = _load_script_module("check_coverage")


def _tool_is_open_only(tool_name: str) -> bool:
    if not tool_name:
        return True
    return tool_name.endswith(("_open", "_list")) or not tool_name.endswith("_preview")


def _is_green(row: dict[str, Any]) -> bool:
    return all(row.get(field) is True for field in GREEN_FIELDS)


def test_cud_parity_green_requires_preview_and_execute_twin() -> None:
    """Owner EE0A0F1B: green CUD parity needs preview + registered execute twin.

    Open-only status or open/list tool can never set implemented, live_tested,
    or vision_verified. This is the same test that first went red on the 16
    false-green rows. Do not delete it when write tools land.
    """

    ui_manifest = checker.load_document(ROOT / "coverage" / "ui_workflows_manifest.yaml")
    rows = {str(row["id"]): row for row in ui_manifest["workflows"]}
    missing = sorted(CUD_PARITY_IDS - set(rows))
    assert missing == [], f"gate set missing from UI manifest: {missing}"
    registered = checker.registered_domain_tools(ROOT)

    violations: list[str] = []
    for row_id in sorted(CUD_PARITY_IDS):
        row = rows[row_id]
        tool_name = str(row.get("tool_name") or "")
        open_only = row.get("parity_status") in OPEN_ONLY_STATUSES or _tool_is_open_only(tool_name)
        if open_only:
            for field in GREEN_FIELDS:
                if row.get(field) is True:
                    violations.append(f"{row_id}: open-only {field}=true tool={tool_name}")
            continue
        if not _is_green(row):
            continue
        if not tool_name.endswith("_preview"):
            violations.append(f"{row_id}: green without preview tool ({tool_name})")
            continue
        execute_name = f"{tool_name.removesuffix('_preview')}_execute"
        if execute_name not in registered:
            violations.append(f"{row_id}: missing execute twin {execute_name}")
    assert violations == [], "CUD parity invariant failed: " + "; ".join(violations)


def test_contacts_and_bills_update_delete_open_shells_stay_registered() -> None:
    """Preview remap must not drop the update/delete open-shell tools."""

    retained = checker.RETAINED_OPEN_SHELL_TOOLS
    assert retained == frozenset(
        {
            "ui_clients_update_open",
            "ui_clients_delete_open",
            "ui_bills_update_open",
            "ui_bills_delete_open",
        }
    )
    registered = checker.registered_domain_tools(ROOT)
    assert retained <= registered
