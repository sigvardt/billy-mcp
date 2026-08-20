"""Ticket, route, replay, and no-body tests for transactions delete."""

from __future__ import annotations

from collections.abc import Callable
from datetime import UTC, datetime, timedelta
from typing import cast

import httpx
import pytest
from fastmcp import FastMCP

from billy_mcp.api.bank_payment_writes import register_bank_payment_write_tools
from billy_mcp.api.transaction_writes import register_transaction_write_tools
from billy_mcp.api.write_protocol import WriteProtocolService
from billy_mcp.client import BillyHttpClient
from billy_mcp.confirmations import ConfirmationStore
from billy_mcp.models import StableErrorCode
from tests.api.test_transaction_delete import call_tool

DELETE_PREVIEW = "api_transactions_delete_preview"
DELETE_EXECUTE = "api_transactions_delete_execute"
BANK_DELETE_PREVIEW = "api_bank_payments_delete_preview"
BANK_DELETE_EXECUTE = "api_bank_payments_delete_execute"


class Clock:
    """Controllable clock used only by local confirmation-expiry tests."""

    def __init__(self) -> None:
        self.now = datetime(2026, 7, 30, tzinfo=UTC)

    def __call__(self) -> datetime:
        return self.now


def make_ticket_server(
    handler: Callable[[httpx.Request], httpx.Response],
    *,
    token: str | None = "transaction-delete-ticket-test-token",
    confirmations: ConfirmationStore | None = None,
) -> tuple[FastMCP, list[httpx.Request]]:
    """Register transaction delete plus bank-payment delete for wrong-executor tests."""

    requests: list[httpx.Request] = []

    def recording_handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return handler(request)

    client = BillyHttpClient(lambda: token, transport=httpx.MockTransport(recording_handler))
    protocol = WriteProtocolService(client, confirmations or ConfirmationStore())
    server = FastMCP("transaction-delete-ticket-contract-test")
    register_transaction_write_tools(server, client, protocol)
    register_bank_payment_write_tools(server, client, protocol)
    return server, requests


def test_delete_execute_sends_encoded_path_with_no_body() -> None:
    deleted_id = "txn /?"
    server, requests = make_ticket_server(
        lambda request: httpx.Response(
            200,
            json={"meta": {"deletedRecords": {"transactions": [deleted_id]}}},
        )
    )

    preview = call_tool(server, DELETE_PREVIEW, {"id": deleted_id})
    execution = call_tool(
        server, DELETE_EXECUTE, {"confirmation_ticket": preview["confirmation_ticket"]}
    )

    assert len(requests) == 1
    request = requests[0]
    assert request.method == "DELETE"
    assert request.url.scheme == "https"
    assert request.url.host == "api.billysbilling.com"
    assert request.url.raw_path.decode() == "/v2/transactions/txn%20%2F%3F"
    assert request.content == b""
    assert execution["changed_records"] == {}
    assert execution["deleted_records"] == {"transactions": [deleted_id]}
    assert "transaction" not in execution


def test_tamper_wrong_executor_expiry_and_replay_do_not_make_unexpected_deletes() -> None:
    clock = Clock()
    server, requests = make_ticket_server(
        lambda request: httpx.Response(
            200,
            json={"meta": {"deletedRecords": {"transactions": ["txn-1"]}}},
        ),
        confirmations=ConfirmationStore(clock),
    )
    preview = call_tool(server, DELETE_PREVIEW, {"id": "txn-1"})
    ticket = cast(str, preview["confirmation_ticket"])

    tampered = call_tool(server, DELETE_EXECUTE, {"confirmation_ticket": f"{ticket}x"})
    wrong_executor = call_tool(server, BANK_DELETE_EXECUTE, {"confirmation_ticket": ticket})
    assert tampered["code"] == StableErrorCode.CONFIRMATION_INVALID
    assert wrong_executor["code"] == StableErrorCode.CONFIRMATION_MISMATCH
    assert requests == []

    bank_preview = call_tool(server, BANK_DELETE_PREVIEW, {"id": "pay-1"})
    bank_on_transaction = call_tool(
        server,
        DELETE_EXECUTE,
        {"confirmation_ticket": bank_preview["confirmation_ticket"]},
    )
    assert bank_on_transaction["code"] == StableErrorCode.CONFIRMATION_MISMATCH
    assert requests == []

    first = call_tool(server, DELETE_EXECUTE, {"confirmation_ticket": ticket})
    replay = call_tool(server, DELETE_EXECUTE, {"confirmation_ticket": ticket})
    assert first["deleted_records"] == {"transactions": ["txn-1"]}
    assert replay["code"] == StableErrorCode.CONFIRMATION_CONSUMED
    assert len(requests) == 1

    expired_preview = call_tool(server, DELETE_PREVIEW, {"id": "txn-1"})
    clock.now += timedelta(minutes=6)
    expired = call_tool(
        server,
        DELETE_EXECUTE,
        {"confirmation_ticket": expired_preview["confirmation_ticket"]},
    )
    assert expired["code"] == StableErrorCode.CONFIRMATION_EXPIRED
    assert len(requests) == 1


def test_empty_token_returns_typed_auth_required_without_network_activity() -> None:
    server, requests = make_ticket_server(
        lambda request: pytest.fail(f"missing token attempted HTTP request: {request.url}"),
        token="",
    )
    preview = call_tool(server, DELETE_PREVIEW, {"id": "txn-1"})
    error = call_tool(
        server, DELETE_EXECUTE, {"confirmation_ticket": preview["confirmation_ticket"]}
    )

    assert error["code"] == StableErrorCode.AUTH_REQUIRED
    assert requests == []


def test_failed_transaction_delete_is_not_retried() -> None:
    server, requests = make_ticket_server(
        lambda request: httpx.Response(500, json={"errorCode": "INTERNAL_SERVER_ERROR"})
    )
    preview = call_tool(server, DELETE_PREVIEW, {"id": "txn-1"})
    error = call_tool(
        server, DELETE_EXECUTE, {"confirmation_ticket": preview["confirmation_ticket"]}
    )

    assert error["code"] == StableErrorCode.BILLY_ERROR
    assert len(requests) == 1
