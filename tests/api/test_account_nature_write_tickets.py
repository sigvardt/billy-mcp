"""Ticket tamper, expiry, replay, and bind tests for account-nature writes."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

import httpx
import pytest

from billy_mcp.api.write_protocol import (
    WriteMethod,
    WriteOperationSpec,
    confirmation_binding_for,
)
from billy_mcp.confirmations import ConfirmationFailure, ConfirmationStore
from billy_mcp.models import StableErrorCode
from tests.api.test_account_nature_writes import call_tool, make_server


class Clock:
    """Controllable confirmation clock used only by local ticket-expiry tests."""

    def __init__(self) -> None:
        self.now = datetime(2026, 7, 29, tzinfo=UTC)

    def __call__(self) -> datetime:
        return self.now


def test_tampered_expired_replayed_and_wrong_executor_tickets_fail_closed() -> None:
    clock = Clock()
    server, requests = make_server(
        lambda request: httpx.Response(200, json={"accountNatures": [{"id": "nature-1"}]}),
        confirmations=ConfirmationStore(clock),
    )

    preview = call_tool(
        server,
        "api_account_natures_create_preview",
        {"accountNature": {"name": "Asset"}},
    )
    ticket = preview["confirmation_ticket"]
    assert isinstance(ticket, str)
    tampered = call_tool(
        server,
        "api_account_natures_create_execute",
        {"confirmation_ticket": f"{ticket}x"},
    )
    assert tampered["code"] == StableErrorCode.CONFIRMATION_INVALID
    assert requests == []

    clock.now += timedelta(minutes=6)
    expired = call_tool(
        server,
        "api_account_natures_create_execute",
        {"confirmation_ticket": ticket},
    )
    assert expired["code"] == StableErrorCode.CONFIRMATION_EXPIRED
    assert requests == []

    replay_preview = call_tool(
        server,
        "api_account_natures_create_preview",
        {"accountNature": {"name": "Asset"}},
    )
    replay_ticket = replay_preview["confirmation_ticket"]
    assert isinstance(replay_ticket, str)
    wrong_executor = call_tool(
        server,
        "api_account_natures_update_execute",
        {"confirmation_ticket": replay_ticket},
    )
    assert wrong_executor["code"] == StableErrorCode.CONFIRMATION_MISMATCH
    assert requests == []

    first = call_tool(
        server,
        "api_account_natures_create_execute",
        {"confirmation_ticket": replay_ticket},
    )
    replayed = call_tool(
        server,
        "api_account_natures_create_execute",
        {"confirmation_ticket": replay_ticket},
    )

    assert first["changed_records"] == {"accountNatures": [{"id": "nature-1"}]}
    assert replayed["code"] == StableErrorCode.CONFIRMATION_CONSUMED
    assert len(requests) == 1


def test_ticket_binding_rejects_a_changed_account_nature_request() -> None:
    store = ConfirmationStore()
    specification = WriteOperationSpec(
        execute_tool_name="api_account_natures_update_execute",
        method=WriteMethod.PUT,
        collection_path="/accountNatures",
        singular_root="accountNature",
        plural_root="accountNatures",
        payload={"name": "Asset"},
        resource_id="nature-1",
        organization_id=None,
        summary="Update one Billy account nature.",
        expected_effect_state={
            "action": "update",
            "resource": "accountNature",
            "id": "nature-1",
        },
    )
    ticket = store.issue(confirmation_binding_for(specification))
    changed_specification = specification.model_copy(update={"payload": {"name": "Changed"}})

    with pytest.raises(ConfirmationFailure) as failure:
        store.consume(ticket.value, confirmation_binding_for(changed_specification))

    assert failure.value.error.code is StableErrorCode.CONFIRMATION_MISMATCH


def test_empty_token_returns_typed_auth_error_without_network_activity() -> None:
    server, requests = make_server(
        lambda request: pytest.fail(f"missing token attempted HTTP request: {request.url}"),
        token="",
    )

    preview = call_tool(
        server,
        "api_account_natures_create_preview",
        {"accountNature": {"name": "Asset"}},
    )
    error = call_tool(
        server,
        "api_account_natures_create_execute",
        {"confirmation_ticket": preview["confirmation_ticket"]},
    )

    assert error["code"] == StableErrorCode.AUTH_REQUIRED
    assert requests == []
