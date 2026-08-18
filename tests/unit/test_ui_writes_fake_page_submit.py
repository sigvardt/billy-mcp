"""Default create_server execute must drive route, fields, CTA, and read-back."""

from __future__ import annotations

import asyncio
from pathlib import Path
from typing import cast

import pytest
from fastmcp import FastMCP

from billy_mcp.browser import BrowserRuntime
from billy_mcp.server import create_server
from billy_mcp.ui_writes.invoices import DRAFT_SAVE_CTA
from tests.unit.fake_billy_page import FakeBillySession


@pytest.fixture
def upload_file(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    root = tmp_path / "uploads"
    root.mkdir()
    path = root / "gate.txt"
    path.write_bytes(b"mcp-ui-file-gate")
    monkeypatch.setenv("BILLY_UPLOAD_ROOTS", str(root))
    return path


def _arm(monkeypatch: pytest.MonkeyPatch) -> FakeBillySession:
    session = FakeBillySession()

    async def _start(self: BrowserRuntime) -> object:
        del self
        return await session.start()

    monkeypatch.setattr(BrowserRuntime, "start", _start)
    return session


def _call(server: FastMCP, tool_name: str, arguments: dict[str, object]) -> dict[str, object]:
    result = asyncio.run(server.call_tool(tool_name, arguments))
    assert isinstance(result.structured_content, dict)
    structured = cast(dict[str, object], result.structured_content)
    payload = structured.get("result", structured)
    assert isinstance(payload, dict)
    return cast(dict[str, object], payload)


def _preview_and_execute(
    server: FastMCP,
    preview_name: str,
    execute_name: str,
    arguments: dict[str, object],
) -> dict[str, object]:
    preview = _call(server, preview_name, {**arguments, "organization_id": "org-test"})
    ticket = preview.get("confirmation_ticket")
    assert isinstance(ticket, str) and ticket
    return _call(server, execute_name, {"confirmation_ticket": ticket})


def test_bills_create_execute_uses_route_fields_cta_and_readback(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    from billy_mcp.ui_writes import bills_form, bills_vendor

    monkeypatch.setattr(bills_form, "CREATE_PRE_SUBMIT_DUMP", tmp_path / "create.json")
    monkeypatch.setattr(bills_form, "PRE_SUBMIT_DUMP", tmp_path / "update.json")
    monkeypatch.setattr(bills_form, "_PERSIST_DUMP", tmp_path / "persist.json")
    monkeypatch.setattr(bills_form, "SAVE_DUMP", tmp_path / "save.json")
    monkeypatch.setattr(bills_vendor, "VENDOR_CHROME_DUMP", tmp_path / "vendor.json")
    session = _arm(monkeypatch)
    executed = _preview_and_execute(
        create_server(),
        "ui_bills_create_preview",
        "ui_bills_create_execute",
        {"unique_tag": "MCP-BILL-ACT"},
    )
    assert executed.get("submitted") is True
    assert session.has_route("/bills/new")
    assert session.has_fill_value("MCP-BILL-ACT")
    assert session.has_click("Gem som kladde")
    assert session.readback_page_count() >= 1
    assert session.has_route("/bills")


def test_invoices_create_execute_uses_route_fields_cta_and_readback(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    from billy_mcp.ui_writes import invoices_form, invoices_form_observe

    monkeypatch.setattr(invoices_form, "CREATE_PRE_SUBMIT_DUMP", tmp_path / "create.json")
    monkeypatch.setattr(invoices_form_observe, "KUNDE_CHROME_DUMP", tmp_path / "kunde.json")
    monkeypatch.setattr(invoices_form_observe, "KUNDE_OPENER_DUMP", tmp_path / "opener.json")
    session = _arm(monkeypatch)
    executed = _preview_and_execute(
        create_server(),
        "ui_invoices_create_preview",
        "ui_invoices_create_execute",
        {
            "contact_name": "MCP-UI-INV-ACT",
            "line_description": "MCP-UI-INV line",
            "unit_price": 1.0,
            "action": "draft_create",
            "save_cta": DRAFT_SAVE_CTA,
        },
    )
    assert executed.get("submitted") is True
    assert session.has_route("/invoices/new")
    assert session.has_fill_value("MCP-UI-INV-ACT")
    assert session.has_fill_value("MCP-UI-INV line")
    assert session.has_click(DRAFT_SAVE_CTA)
    assert session.readback_page_count() >= 1


def test_products_create_execute_uses_route_fields_cta_and_readback(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from billy_mcp.ui_writes import products

    def _allow_persist(path: Path | None = None) -> bool:
        del path
        return True

    monkeypatch.setattr(products, "product_persist_allowed", _allow_persist)
    session = _arm(monkeypatch)
    executed = _preview_and_execute(
        create_server(),
        "ui_products_create_preview",
        "ui_products_create_execute",
        {"name": "MCP-PROD-ACT"},
    )
    assert executed.get("submitted") is True
    assert session.has_route("/inventory")
    assert session.has_click("Opret produkt")
    assert session.has_fill_value("MCP-PROD-ACT")
    assert session.has_click("Gem produkt")
    assert session.readback_page_count() >= 1


def test_organizations_update_execute_uses_route_fields_cta_and_readback(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    session = _arm(monkeypatch)
    executed = _preview_and_execute(
        create_server(),
        "ui_organizations_update_preview",
        "ui_organizations_update_execute",
        {"phone": "87654321"},
    )
    assert executed.get("submitted") is True
    assert session.has_route("/settings")
    assert session.has_fill_value("87654321")
    assert session.has_click("Gem ændringer")
    assert session.readback_page_count() >= 1


def test_files_create_execute_uses_route_file_cta_and_readback(
    monkeypatch: pytest.MonkeyPatch,
    upload_file: Path,
) -> None:
    session = _arm(monkeypatch)
    executed = _preview_and_execute(
        create_server(),
        "ui_files_create_preview",
        "ui_files_create_execute",
        {"path": str(upload_file), "filename": upload_file.name},
    )
    assert executed.get("submitted") is True or executed.get("filename") == upload_file.name
    assert session.has_route("/uploads")
    assert session.files and Path(session.files[0]).name == upload_file.name
    assert session.has_click("Upload filer")
    assert session.readback_page_count() >= 1


def test_daybooks_create_execute_uses_route_fields_cta_and_readback(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    session = _arm(monkeypatch)
    executed = _preview_and_execute(
        create_server(),
        "ui_daybooks_create_preview",
        "ui_daybooks_create_execute",
        {"name": "MCP-DB-ACT"},
    )
    assert executed.get("submitted") is True
    assert session.has_route("/daybooks/new")
    assert session.has_fill_value("MCP-DB-ACT")
    assert session.has_click("Opret ny kassekladde")
    assert session.readback_page_count() >= 1


def test_daybooks_delete_execute_clicks_slet_and_reads_back(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    session = _arm(monkeypatch)
    executed = _preview_and_execute(
        create_server(),
        "ui_daybooks_delete_preview",
        "ui_daybooks_delete_execute",
        {"id": "daybook-1"},
    )
    assert executed.get("submitted") is True
    assert session.has_route("/daybooks")
    assert session.has_click("Slet")
    assert session.readback_page_count() >= 1
    assert executed.get("submitted") is not True or "Bogfør" not in session.clicks


def test_transactions_create_execute_refuses_without_false_submit(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    session = _arm(monkeypatch)
    executed = _preview_and_execute(
        create_server(),
        "ui_transactions_create_preview",
        "ui_transactions_create_execute",
        {"text": "MCP-TX-ACT"},
    )
    assert executed.get("submitted") is not True
    assert "Bogfør" not in session.clicks


def test_contacts_create_execute_uses_route_fields_cta_and_readback(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    session = _arm(monkeypatch)
    executed = _preview_and_execute(
        create_server(),
        "ui_clients_create_preview",
        "ui_clients_create_execute",
        {"name": "MCP-UI-C-ACT"},
    )
    assert executed.get("submitted") is True
    assert session.has_route("/clients")
    assert session.has_fill_value("MCP-UI-C-ACT")
    assert session.has_click("Opret kontakt")
    assert session.has_click("Gem")
    assert session.readback_page_count() >= 1


def test_start_only_is_not_enough_for_bills_create(monkeypatch: pytest.MonkeyPatch) -> None:
    started: list[str] = []

    class _EmptyContext:
        async def new_page(self) -> object:
            raise AssertionError("start-only context must not count as a submit")

    async def _start(self: BrowserRuntime) -> object:
        del self
        started.append("start")
        return _EmptyContext()

    monkeypatch.setattr(BrowserRuntime, "start", _start)
    executed = _preview_and_execute(
        create_server(),
        "ui_bills_create_preview",
        "ui_bills_create_execute",
        {"unique_tag": "MCP-BILL-START-ONLY"},
    )
    assert started
    assert executed.get("submitted") is not True
