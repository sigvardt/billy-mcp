"""Offline ticket contract for the shared UI write protocol."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

from billy_mcp.confirmations import MAX_TICKET_TTL, ConfirmationStore
from billy_mcp.models import StableErrorCode, ToolError
from billy_mcp.ui_writes.protocol import UiWriteExecuteInput, UiWriteProtocol


class Clock:
    def __init__(self) -> None:
        self.now = datetime(2026, 8, 16, tzinfo=UTC)

    def __call__(self) -> datetime:
        return self.now


def _protocol(clock: Clock | None = None) -> UiWriteProtocol:
    return UiWriteProtocol(ConfirmationStore(clock=clock or Clock()))


def test_preview_does_not_submit_and_execute_consumes_once() -> None:
    protocol = _protocol()
    preview = protocol.preview(
        execute_tool_name="ui_clients_create_execute",
        organization_id="org-1",
        target="clients",
        canonical_request={"name": "MCP-TEST-1"},
        expected_effect_state={"action": "create", "resource": "contact"},
        summary="Create one Billy customer in the interface.",
    )
    first = protocol.consume(
        UiWriteExecuteInput(confirmation_ticket=preview.confirmation_ticket),
        execute_tool_name="ui_clients_create_execute",
    )
    assert not isinstance(first, ToolError)
    assert first.canonical_request == {"name": "MCP-TEST-1"}
    replay = protocol.consume(
        UiWriteExecuteInput(confirmation_ticket=preview.confirmation_ticket),
        execute_tool_name="ui_clients_create_execute",
    )
    assert isinstance(replay, ToolError)
    assert replay.code is StableErrorCode.CONFIRMATION_CONSUMED


def test_execute_rejects_wrong_tool_and_expired_ticket() -> None:
    clock = Clock()
    protocol = _protocol(clock)
    preview = protocol.preview(
        execute_tool_name="ui_clients_create_execute",
        organization_id="org-1",
        target="clients",
        canonical_request={"name": "MCP-TEST-2"},
        expected_effect_state={"action": "create"},
        summary="Create one Billy customer in the interface.",
    )
    wrong_tool = protocol.consume(
        UiWriteExecuteInput(confirmation_ticket=preview.confirmation_ticket),
        execute_tool_name="ui_clients_delete_execute",
    )
    assert isinstance(wrong_tool, ToolError)
    assert wrong_tool.code is StableErrorCode.CONFIRMATION_MISMATCH

    clock.now = clock.now + MAX_TICKET_TTL + timedelta(seconds=1)
    expired = protocol.consume(
        UiWriteExecuteInput(confirmation_ticket=preview.confirmation_ticket),
        execute_tool_name="ui_clients_create_execute",
    )
    assert isinstance(expired, ToolError)
    assert expired.code is StableErrorCode.CONFIRMATION_EXPIRED
