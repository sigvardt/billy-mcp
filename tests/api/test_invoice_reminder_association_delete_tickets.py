"""Ticket, route, replay, and no-body tests for association delete."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import cast

import httpx
import pytest

from billy_mcp.confirmations import ConfirmationStore
from billy_mcp.models import StableErrorCode
from tests.api.test_invoice_reminder_association_writes import (
    VALID_ASSOCIATION,
    call_tool,
    make_server,
)

DELETE_PREVIEW = "api_invoice_reminder_associations_delete_preview"
DELETE_EXECUTE = "api_invoice_reminder_associations_delete_execute"
CREATE_PREVIEW = "api_invoice_reminder_associations_create_preview"
CREATE_EXECUTE = "api_invoice_reminder_associations_create_execute"


class Clock:
    """Controllable clock used only by local confirmation-expiry tests."""

    def __init__(self) -> None:
        self.now = datetime(2026, 7, 30, tzinfo=UTC)

    def __call__(self) -> datetime:
        return self.now


def test_delete_execute_sends_encoded_path_with_no_body() -> None:
    deleted_id = "assoc /?"
    server, requests = make_server(
        lambda request: httpx.Response(
            200,
            json={"meta": {"deletedRecords": {"invoiceReminderAssociations": [deleted_id]}}},
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
    assert request.url.raw_path.decode() == "/v2/invoiceReminderAssociations/assoc%20%2F%3F"
    assert request.content == b""
    assert execution["changed_records"] == {}
    assert execution["deleted_records"] == {"invoiceReminderAssociations": [deleted_id]}
    assert "invoiceReminderAssociation" not in execution


def test_tamper_wrong_executor_expiry_and_replay_do_not_make_unexpected_deletes() -> None:
    clock = Clock()
    server, requests = make_server(
        lambda request: httpx.Response(
            200,
            json={"meta": {"deletedRecords": {"invoiceReminderAssociations": ["assoc-1"]}}},
        ),
        confirmations=ConfirmationStore(clock),
    )
    preview = call_tool(server, DELETE_PREVIEW, {"id": "assoc-1"})
    ticket = cast(str, preview["confirmation_ticket"])

    tampered = call_tool(server, DELETE_EXECUTE, {"confirmation_ticket": f"{ticket}x"})
    wrong_executor = call_tool(server, CREATE_EXECUTE, {"confirmation_ticket": ticket})
    assert tampered["code"] == StableErrorCode.CONFIRMATION_INVALID
    assert wrong_executor["code"] == StableErrorCode.CONFIRMATION_MISMATCH
    assert requests == []

    create_preview = call_tool(
        server, CREATE_PREVIEW, {"invoiceReminderAssociation": VALID_ASSOCIATION}
    )
    create_on_delete = call_tool(
        server,
        DELETE_EXECUTE,
        {"confirmation_ticket": create_preview["confirmation_ticket"]},
    )
    assert create_on_delete["code"] == StableErrorCode.CONFIRMATION_MISMATCH
    assert requests == []

    first = call_tool(server, DELETE_EXECUTE, {"confirmation_ticket": ticket})
    replay = call_tool(server, DELETE_EXECUTE, {"confirmation_ticket": ticket})
    assert first["deleted_records"] == {"invoiceReminderAssociations": ["assoc-1"]}
    assert replay["code"] == StableErrorCode.CONFIRMATION_CONSUMED
    assert len(requests) == 1

    expired_preview = call_tool(server, DELETE_PREVIEW, {"id": "assoc-1"})
    clock.now += timedelta(minutes=6)
    expired = call_tool(
        server,
        DELETE_EXECUTE,
        {"confirmation_ticket": expired_preview["confirmation_ticket"]},
    )
    assert expired["code"] == StableErrorCode.CONFIRMATION_EXPIRED
    assert len(requests) == 1


def test_empty_token_returns_typed_auth_required_without_network_activity() -> None:
    server, requests = make_server(
        lambda request: pytest.fail(f"missing token attempted HTTP request: {request.url}"),
        token="",
    )
    preview = call_tool(server, DELETE_PREVIEW, {"id": "assoc-1"})
    error = call_tool(
        server, DELETE_EXECUTE, {"confirmation_ticket": preview["confirmation_ticket"]}
    )

    assert error["code"] == StableErrorCode.AUTH_REQUIRED
    assert requests == []


def test_failed_association_delete_is_not_retried() -> None:
    server, requests = make_server(
        lambda request: httpx.Response(500, json={"errorCode": "INTERNAL_SERVER_ERROR"})
    )
    preview = call_tool(server, DELETE_PREVIEW, {"id": "assoc-1"})
    error = call_tool(
        server, DELETE_EXECUTE, {"confirmation_ticket": preview["confirmation_ticket"]}
    )

    assert error["code"] == StableErrorCode.BILLY_ERROR
    assert len(requests) == 1
