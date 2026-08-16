"""Offline FastMCP ticket tests for UI contact create, update, and delete."""

from __future__ import annotations

import asyncio
from datetime import UTC, datetime, timedelta
from typing import cast

import pytest
from fastmcp import FastMCP
from pydantic import JsonValue, ValidationError

from billy_mcp.confirmations import MAX_TICKET_TTL, ConfirmationStore
from billy_mcp.models import StableErrorCode
from billy_mcp.ui_writes.contacts import (
    ClientsCreatePreviewInput,
    ClientsDeletePreviewInput,
    ClientsUpdatePreviewInput,
    register_ui_contact_write_tools,
)
from billy_mcp.ui_writes.protocol import UiWriteExecuteInput, UiWriteProtocol


class Clock:
    def __init__(self) -> None:
        self.now = datetime(2026, 8, 16, tzinfo=UTC)

    def __call__(self) -> datetime:
        return self.now


class FakeActor:
    def __init__(self) -> None:
        self.calls: list[tuple[str, dict[str, JsonValue]]] = []

    async def submit_create(self, request: dict[str, JsonValue]) -> dict[str, JsonValue]:
        self.calls.append(("create", request))
        return {"ok": True}

    async def submit_update(self, request: dict[str, JsonValue]) -> dict[str, JsonValue]:
        self.calls.append(("update", request))
        return {"ok": True}

    async def submit_delete(self, request: dict[str, JsonValue]) -> dict[str, JsonValue]:
        self.calls.append(("delete", request))
        return {"ok": True}


def make_server(
    actor: FakeActor | None = None,
    *,
    clock: Clock | None = None,
) -> tuple[FastMCP, FakeActor]:
    fake = actor or FakeActor()
    server = FastMCP("ui-contacts-write-contract-test")
    register_ui_contact_write_tools(
        server,
        UiWriteProtocol(ConfirmationStore(clock=clock or Clock())),
        actor=fake,
    )
    return server, fake


def call_tool(server: FastMCP, tool_name: str, arguments: dict[str, object]) -> dict[str, object]:
    result = asyncio.run(server.call_tool(tool_name, arguments))
    structured = result.structured_content
    assert isinstance(structured, dict)
    payload = structured.get("result", structured)
    assert isinstance(payload, dict)
    return cast(dict[str, object], payload)


def test_registers_exactly_six_flat_typed_contact_ui_write_tools() -> None:
    server, _ = make_server()
    by_name = {tool.name: tool for tool in asyncio.run(server.list_tools())}
    expected = {
        "ui_clients_create_preview": {"name"},
        "ui_clients_create_execute": {"confirmation_ticket"},
        "ui_clients_update_preview": {"name", "new_name"},
        "ui_clients_update_execute": {"confirmation_ticket"},
        "ui_clients_delete_preview": {"name"},
        "ui_clients_delete_execute": {"confirmation_ticket"},
    }
    assert set(by_name) == set(expected)
    for name, fields in expected.items():
        schema = by_name[name].parameters
        properties = cast(dict[str, dict[str, object]], schema["properties"])
        assert schema["additionalProperties"] is False
        assert set(properties) == fields
        assert "input" not in properties
        for field in fields:
            assert properties[field]["minLength"] == 1


@pytest.mark.parametrize(
    ("model", "payload"),
    [
        (ClientsCreatePreviewInput, {"name": "x", "extra": True}),
        (ClientsCreatePreviewInput, {"name": ""}),
        (ClientsUpdatePreviewInput, {"name": "a", "new_name": "b", "extra": True}),
        (ClientsUpdatePreviewInput, {"name": "", "new_name": "b"}),
        (ClientsUpdatePreviewInput, {"name": "a", "new_name": ""}),
        (ClientsDeletePreviewInput, {"name": "x", "extra": True}),
        (ClientsDeletePreviewInput, {"name": ""}),
        (UiWriteExecuteInput, {"confirmation_ticket": "t", "name": "x"}),
        (UiWriteExecuteInput, {"confirmation_ticket": ""}),
    ],
)
def test_outer_inputs_forbid_extras_and_empty_values(
    model: type[ClientsCreatePreviewInput]
    | type[ClientsUpdatePreviewInput]
    | type[ClientsDeletePreviewInput]
    | type[UiWriteExecuteInput],
    payload: dict[str, object],
) -> None:
    with pytest.raises(ValidationError):
        model.model_validate(payload)


@pytest.mark.parametrize(
    ("preview_name", "arguments", "canonical", "effect"),
    [
        (
            "ui_clients_create_preview",
            {"name": "MCP-UI-C-AAAA"},
            {"action": "create", "name": "MCP-UI-C-AAAA"},
            {"action": "create", "resource": "contact"},
        ),
        (
            "ui_clients_update_preview",
            {"name": "MCP-UI-C-AAAA", "new_name": "MCP-UI-C-AAAA-U"},
            {"action": "update", "name": "MCP-UI-C-AAAA", "new_name": "MCP-UI-C-AAAA-U"},
            {
                "action": "update",
                "resource": "contact",
                "name": "MCP-UI-C-AAAA",
                "new_name": "MCP-UI-C-AAAA-U",
            },
        ),
        (
            "ui_clients_delete_preview",
            {"name": "MCP-UI-C-AAAA-U"},
            {"action": "delete", "name": "MCP-UI-C-AAAA-U"},
            {"action": "delete", "resource": "contact", "name": "MCP-UI-C-AAAA-U"},
        ),
    ],
)
def test_preview_does_not_submit(
    preview_name: str,
    arguments: dict[str, object],
    canonical: dict[str, object],
    effect: dict[str, object],
) -> None:
    server, actor = make_server()
    preview = call_tool(server, preview_name, arguments)
    assert actor.calls == []
    assert preview["canonical_request"] == canonical
    assert preview["expected_effect_state"] == effect
    assert isinstance(preview["confirmation_ticket"], str)
    assert preview["confirmation_ticket"]


@pytest.mark.parametrize(
    ("preview_name", "execute_name", "arguments", "op"),
    [
        (
            "ui_clients_create_preview",
            "ui_clients_create_execute",
            {"name": "MCP-UI-C-BBBB"},
            "create",
        ),
        (
            "ui_clients_update_preview",
            "ui_clients_update_execute",
            {"name": "MCP-UI-C-BBBB", "new_name": "MCP-UI-C-BBBB-U"},
            "update",
        ),
        (
            "ui_clients_delete_preview",
            "ui_clients_delete_execute",
            {"name": "MCP-UI-C-BBBB-U"},
            "delete",
        ),
    ],
)
def test_execute_submits_once_then_replay_is_consumed(
    preview_name: str,
    execute_name: str,
    arguments: dict[str, object],
    op: str,
) -> None:
    server, actor = make_server()
    preview = call_tool(server, preview_name, arguments)
    ticket = cast(str, preview["confirmation_ticket"])
    first = call_tool(server, execute_name, {"confirmation_ticket": ticket})
    assert first["submitted"] is True
    assert first["canonical_request"] == preview["canonical_request"]
    assert actor.calls == [(op, preview["canonical_request"])]
    replay = call_tool(server, execute_name, {"confirmation_ticket": ticket})
    assert replay["code"] == StableErrorCode.CONFIRMATION_CONSUMED
    assert actor.calls == [(op, preview["canonical_request"])]


def test_execute_rejects_wrong_tool_and_does_not_submit() -> None:
    server, actor = make_server()
    preview = call_tool(server, "ui_clients_create_preview", {"name": "MCP-UI-C-CCCC"})
    ticket = cast(str, preview["confirmation_ticket"])
    for execute_name in ("ui_clients_update_execute", "ui_clients_delete_execute"):
        mismatch = call_tool(server, execute_name, {"confirmation_ticket": ticket})
        assert mismatch["code"] == StableErrorCode.CONFIRMATION_MISMATCH
    assert actor.calls == []


def test_execute_rejects_expired_ticket_and_does_not_submit() -> None:
    clock = Clock()
    server, actor = make_server(clock=clock)
    preview = call_tool(server, "ui_clients_create_preview", {"name": "MCP-UI-C-DDDD"})
    clock.now = clock.now + MAX_TICKET_TTL + timedelta(seconds=1)
    expired = call_tool(
        server,
        "ui_clients_create_execute",
        {"confirmation_ticket": preview["confirmation_ticket"]},
    )
    assert expired["code"] == StableErrorCode.CONFIRMATION_EXPIRED
    assert actor.calls == []
