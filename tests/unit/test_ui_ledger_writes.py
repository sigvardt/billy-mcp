"""Offline FastMCP ticket contract for UI ledger preview and execute tools."""

from __future__ import annotations

import asyncio
from datetime import UTC, datetime, timedelta

import pytest
from fastmcp import FastMCP
from pydantic import ValidationError

from billy_mcp.confirmations import MAX_TICKET_TTL, ConfirmationStore
from billy_mcp.models import StableErrorCode
from billy_mcp.ui_writes.ledger import (
    LEDGER_SUBMIT_BLOCKER,
    DaybookCreatePreviewInput,
    DaybookDeletePreviewInput,
    DaybookTransactionCreatePreviewInput,
    TransactionCreatePreviewInput,
    register_ui_ledger_write_tools,
)
from billy_mcp.ui_writes.protocol import UiWriteExecuteInput, UiWriteProtocol

PREVIEW_EXECUTE = {
    "ui_daybooks_create_preview": "ui_daybooks_create_execute",
    "ui_daybooks_delete_preview": "ui_daybooks_delete_execute",
    "ui_daybook_transactions_create_preview": "ui_daybook_transactions_create_execute",
    "ui_transactions_create_preview": "ui_transactions_create_execute",
}

PREVIEW_ARGUMENTS: dict[str, dict[str, str]] = {
    "ui_daybooks_create_preview": {"name": "MCP-LEDGER-UNIT-DAYBOOK"},
    "ui_daybooks_delete_preview": {"id": "daybook-1"},
    "ui_daybook_transactions_create_preview": {
        "daybook_id": "daybook-1",
        "text": "MCP-LEDGER-UNIT-LINE",
    },
    "ui_transactions_create_preview": {"text": "MCP-LEDGER-UNIT-POSTING"},
}


class Clock:
    """Controllable confirmation clock used only by local ticket-expiry tests."""

    def __init__(self) -> None:
        self.now = datetime(2026, 8, 16, tzinfo=UTC)

    def __call__(self) -> datetime:
        return self.now


def make_server(*, clock: Clock | None = None) -> FastMCP:
    """Register the ledger family on a local FastMCP server."""

    server = FastMCP("ui-ledger-write-contract-test")
    register_ui_ledger_write_tools(
        server,
        UiWriteProtocol(ConfirmationStore(clock=clock or Clock())),
    )
    return server


def call_tool(
    server: FastMCP, tool_name: str, arguments: dict[str, object]
) -> dict[str, object]:
    """Call one typed tool with its direct MCP argument object."""

    result = asyncio.run(server.call_tool(tool_name, arguments))
    structured_content = result.structured_content
    assert isinstance(structured_content, dict)
    structured_result = structured_content.get("result", structured_content)
    assert isinstance(structured_result, dict)
    return structured_result


def test_registers_exactly_eight_flat_typed_ledger_write_tools() -> None:
    server = make_server()
    by_name = {tool.name: tool for tool in asyncio.run(server.list_tools())}

    assert set(by_name) == set(PREVIEW_EXECUTE) | set(PREVIEW_EXECUTE.values())
    expected_properties = {
        "ui_daybooks_create_preview": {"name"},
        "ui_daybooks_create_execute": {"confirmation_ticket"},
        "ui_daybooks_delete_preview": {"id"},
        "ui_daybooks_delete_execute": {"confirmation_ticket"},
        "ui_daybook_transactions_create_preview": {"daybook_id", "text"},
        "ui_daybook_transactions_create_execute": {"confirmation_ticket"},
        "ui_transactions_create_preview": {"text"},
        "ui_transactions_create_execute": {"confirmation_ticket"},
    }
    for name, fields in expected_properties.items():
        schema = by_name[name].parameters
        properties = schema["properties"]
        assert schema["additionalProperties"] is False
        assert set(properties) == fields
        assert "input" not in properties


@pytest.mark.parametrize(
    ("input_model", "payload"),
    [
        (DaybookCreatePreviewInput, {"name": ""}),
        (DaybookCreatePreviewInput, {"name": "MCP-LEDGER-X", "extra": "no"}),
        (DaybookDeletePreviewInput, {"id": ""}),
        (DaybookDeletePreviewInput, {"id": "daybook-1", "name": "no"}),
        (DaybookTransactionCreatePreviewInput, {"daybook_id": "d1"}),
        (DaybookTransactionCreatePreviewInput, {"daybook_id": "", "text": "line"}),
        (TransactionCreatePreviewInput, {"text": ""}),
        (TransactionCreatePreviewInput, {"text": "post", "amount": "1"}),
        (UiWriteExecuteInput, {"confirmation_ticket": "ticket", "name": "no"}),
    ],
)
def test_outer_inputs_forbid_extra_fields_and_empty_values(
    input_model: type[DaybookCreatePreviewInput]
    | type[DaybookDeletePreviewInput]
    | type[DaybookTransactionCreatePreviewInput]
    | type[TransactionCreatePreviewInput]
    | type[UiWriteExecuteInput],
    payload: dict[str, object],
) -> None:
    with pytest.raises(ValidationError):
        input_model.model_validate(payload)


@pytest.mark.parametrize("preview_name", list(PREVIEW_EXECUTE))
def test_preview_issues_ticket_and_does_not_submit(
    preview_name: str,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    constructed: list[str] = []

    def refuse_client(*_args: object, **_kwargs: object) -> None:
        constructed.append("BillyHttpClient")
        raise AssertionError("BillyHttpClient must not be constructed")

    monkeypatch.setattr("billy_mcp.client.BillyHttpClient.__init__", refuse_client)
    server = make_server()
    preview = call_tool(server, preview_name, PREVIEW_ARGUMENTS[preview_name])

    assert constructed == []
    ticket = preview["confirmation_ticket"]
    assert isinstance(ticket, str)
    assert ticket
    assert preview["expires_at"]
    assert preview["canonical_request"] == PREVIEW_ARGUMENTS[preview_name]
    assert preview["expected_effect_state"]["action"] in {"create", "delete"}


@pytest.mark.parametrize("preview_name", list(PREVIEW_EXECUTE))
def test_execute_consumes_once_without_submitting(preview_name: str) -> None:
    server = make_server()
    preview = call_tool(server, preview_name, PREVIEW_ARGUMENTS[preview_name])
    execute_name = PREVIEW_EXECUTE[preview_name]
    first = call_tool(
        server,
        execute_name,
        {"confirmation_ticket": preview["confirmation_ticket"]},
    )
    replay = call_tool(
        server,
        execute_name,
        {"confirmation_ticket": preview["confirmation_ticket"]},
    )

    assert first["submitted"] is False
    assert first["blocker"] == LEDGER_SUBMIT_BLOCKER
    assert first["canonical_request"] == PREVIEW_ARGUMENTS[preview_name]
    assert replay["code"] == StableErrorCode.CONFIRMATION_CONSUMED


def test_expired_ticket_fails_closed() -> None:
    clock = Clock()
    server = make_server(clock=clock)
    preview = call_tool(
        server,
        "ui_daybooks_create_preview",
        {"name": "MCP-LEDGER-UNIT-EXPIRE"},
    )
    clock.now = clock.now + MAX_TICKET_TTL + timedelta(seconds=1)
    expired = call_tool(
        server,
        "ui_daybooks_create_execute",
        {"confirmation_ticket": preview["confirmation_ticket"]},
    )

    assert expired["code"] == StableErrorCode.CONFIRMATION_EXPIRED


def test_wrong_tool_rejects_ticket() -> None:
    server = make_server()
    preview = call_tool(
        server,
        "ui_daybooks_create_preview",
        {"name": "MCP-LEDGER-UNIT-MISMATCH"},
    )
    wrong = call_tool(
        server,
        "ui_daybooks_delete_execute",
        {"confirmation_ticket": preview["confirmation_ticket"]},
    )
    correct = call_tool(
        server,
        "ui_daybooks_create_execute",
        {"confirmation_ticket": preview["confirmation_ticket"]},
    )

    assert wrong["code"] == StableErrorCode.CONFIRMATION_MISMATCH
    assert correct["submitted"] is False
    assert correct["blocker"] == LEDGER_SUBMIT_BLOCKER
