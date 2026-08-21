"""Execute must bind the ticket org and read back on a second session."""

from __future__ import annotations

import asyncio
from typing import cast

import pytest
from fastmcp import FastMCP

from billy_mcp.browser import BrowserRuntime
from billy_mcp.models import StableErrorCode
from billy_mcp.server import create_server
from tests.unit.fake_billy_page import FakeBillySession


def _arm_pair(
    monkeypatch: pytest.MonkeyPatch,
    *,
    write_slug: str = "org-test",
    readback_slug: str | None = None,
) -> tuple[FakeBillySession, FakeBillySession]:
    write = FakeBillySession(live_slug=write_slug)
    readback = FakeBillySession(live_slug=readback_slug or write_slug)

    async def _start(self: BrowserRuntime) -> object:
        profile_name = self.profile_path.name
        if profile_name.endswith("-readback"):
            return await readback.start()
        return await write.start()

    monkeypatch.setattr(BrowserRuntime, "start", _start)
    return write, readback


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
    *,
    organization_id: str,
) -> dict[str, object]:
    preview = _call(server, preview_name, {**arguments, "organization_id": organization_id})
    ticket = preview.get("confirmation_ticket")
    assert isinstance(ticket, str) and ticket
    return _call(server, execute_name, {"confirmation_ticket": ticket})


def test_bills_create_execute_refuses_wrong_live_org(monkeypatch: pytest.MonkeyPatch) -> None:
    write, readback = _arm_pair(monkeypatch, write_slug="org-b")
    executed = _preview_and_execute(
        create_server(),
        "ui_bills_create_preview",
        "ui_bills_create_execute",
        {"unique_tag": "MCP-BILL-WRONG-ORG"},
        organization_id="org-a",
    )
    assert executed.get("code") == StableErrorCode.CONFIRMATION_MISMATCH
    assert executed.get("submitted") is not True
    assert write.fills == []
    assert write.clicks == []
    assert readback.starts == 0


def test_products_create_execute_refuses_wrong_live_org(monkeypatch: pytest.MonkeyPatch) -> None:
    write, readback = _arm_pair(monkeypatch, write_slug="org-b")
    executed = _preview_and_execute(
        create_server(),
        "ui_products_create_preview",
        "ui_products_create_execute",
        {"name": "MCP-PROD-WRONG-ORG", "unitPrice": 1.0},
        organization_id="org-a",
    )
    assert executed.get("code") == StableErrorCode.CONFIRMATION_MISMATCH
    assert executed.get("submitted") is not True
    assert write.fills == []
    assert write.clicks == []
    assert readback.starts == 0


def test_products_delete_execute_refuses_wrong_live_org(monkeypatch: pytest.MonkeyPatch) -> None:
    write, readback = _arm_pair(monkeypatch, write_slug="org-b")
    executed = _preview_and_execute(
        create_server(),
        "ui_products_delete_preview",
        "ui_products_delete_execute",
        {"unique_tag": "MCP-PROD-DEL-WRONG-ORG"},
        organization_id="org-a",
    )
    assert executed.get("code") == StableErrorCode.CONFIRMATION_MISMATCH
    assert executed.get("submitted") is not True
    assert write.fills == []
    assert write.clicks == []
    assert readback.starts == 0


def test_clients_create_execute_refuses_wrong_live_org(monkeypatch: pytest.MonkeyPatch) -> None:
    write, readback = _arm_pair(monkeypatch, write_slug="org-b")
    executed = _preview_and_execute(
        create_server(),
        "ui_clients_create_preview",
        "ui_clients_create_execute",
        {"name": "MCP-UI-C-WRONG-ORG"},
        organization_id="org-a",
    )
    assert executed.get("code") == StableErrorCode.CONFIRMATION_MISMATCH
    assert executed.get("submitted") is not True
    assert write.fills == []
    assert write.clicks == []
    assert readback.starts == 0


def test_bills_create_execute_starts_second_session_without_shared_store(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    write, readback = _arm_pair(monkeypatch, write_slug="org-test")
    executed = _preview_and_execute(
        create_server(),
        "ui_bills_create_preview",
        "ui_bills_create_execute",
        {"unique_tag": "MCP-BILL-INDEP"},
        organization_id="org-test",
    )
    assert write.has_route("/bills/new")
    assert write.has_fill_value("MCP-BILL-INDEP")
    assert write.has_click("Gem som kladde")
    assert write.readback_page_count() == 0
    assert readback.starts >= 1
    assert readback.has_route("/bills")
    assert executed.get("submitted") is not True
    assert executed.get("code") == StableErrorCode.NOT_FOUND
    assert "MCP-BILL-INDEP" not in readback.records


def test_clients_create_execute_starts_second_session_without_shared_store(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    write, readback = _arm_pair(monkeypatch, write_slug="org-test")
    executed = _preview_and_execute(
        create_server(),
        "ui_clients_create_preview",
        "ui_clients_create_execute",
        {"name": "MCP-UI-C-INDEP"},
        organization_id="org-test",
    )
    assert write.has_route("/clients")
    assert write.has_fill_value("MCP-UI-C-INDEP")
    assert write.has_click("Opret kontakt")
    assert write.has_click("Gem")
    assert write.readback_page_count() == 0
    assert readback.starts >= 1
    assert readback.has_route("/clients")
    assert executed.get("submitted") is not True
    assert executed.get("code") == StableErrorCode.NOT_FOUND
    assert "MCP-UI-C-INDEP" not in readback.records


def test_clients_create_ignores_identity_file_when_live_url_has_no_slug(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    write, readback = _arm_pair(monkeypatch, write_slug="login")
    executed = _preview_and_execute(
        create_server(),
        "ui_clients_create_preview",
        "ui_clients_create_execute",
        {"name": "MCP-UI-C-LOGIN"},
        organization_id="org-a",
    )
    assert executed.get("code") == StableErrorCode.ORGANIZATION_REQUIRED
    assert executed.get("submitted") is not True
    assert write.fills == []
    assert write.clicks == []
    assert readback.starts == 0


def test_blank_readback_session_cannot_prove_submit(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    write, readback = _arm_pair(monkeypatch, write_slug="org-test", readback_slug="login")
    executed = _preview_and_execute(
        create_server(),
        "ui_bills_create_preview",
        "ui_bills_create_execute",
        {"unique_tag": "MCP-BILL-BLANK-RB"},
        organization_id="org-test",
    )
    assert write.has_click("Gem som kladde")
    assert readback.starts >= 1
    assert executed.get("submitted") is not True
    assert executed.get("code") == StableErrorCode.ORGANIZATION_REQUIRED
