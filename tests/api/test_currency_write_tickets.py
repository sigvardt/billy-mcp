"""Ticket tamper, expiry, replay, and auth tests for currency writes."""

from __future__ import annotations

import json
from datetime import UTC, datetime, timedelta
from typing import cast

import httpx
import pytest

from billy_mcp.api.write_protocol import (
    WriteMethod,
    WriteOperationSpec,
    confirmation_binding_for,
)
from billy_mcp.confirmations import ConfirmationFailure, ConfirmationStore
from billy_mcp.models import StableErrorCode
from tests.api.test_currency_writes import PARTIAL_CURRENCY, call_tool, make_server


class Clock:
    """Controllable confirmation clock used only by local ticket-expiry tests."""

    def __init__(self) -> None:
        self.now = datetime(2026, 8, 20, tzinfo=UTC)

    def __call__(self) -> datetime:
        return self.now


@pytest.mark.parametrize(
    ("preview_name", "execute_name", "arguments", "response", "method", "path", "body"),
    [
        (
            "api_currencies_create_preview",
            "api_currencies_create_execute",
            {"currency": PARTIAL_CURRENCY},
            {"currencies": [{"id": "dkk", **PARTIAL_CURRENCY}]},
            "POST",
            "/v2/currencies",
            {"currency": PARTIAL_CURRENCY},
        ),
        (
            "api_currencies_update_preview",
            "api_currencies_update_execute",
            {"id": "dk /?", "currency": PARTIAL_CURRENCY},
            {"currencies": [{"id": "dk /?", **PARTIAL_CURRENCY}]},
            "PUT",
            "/v2/currencies/dk%20%2F%3F",
            {"currency": PARTIAL_CURRENCY},
        ),
    ],
)
def test_execute_sends_exact_singular_currency_write_shapes_once(
    preview_name: str,
    execute_name: str,
    arguments: dict[str, object],
    response: dict[str, object],
    method: str,
    path: str,
    body: dict[str, object],
) -> None:
    server, requests = make_server(lambda request: httpx.Response(200, json=response))

    preview = call_tool(server, preview_name, arguments)
    execution = call_tool(
        server,
        execute_name,
        {"confirmation_ticket": preview["confirmation_ticket"]},
    )

    assert len(requests) == 1
    request = requests[0]
    assert request.method == method
    assert request.url.scheme == "https"
    assert request.url.host == "api.billysbilling.com"
    assert request.url.raw_path.decode() == path
    assert json.loads(request.content) == body
    assert execution["changed_records"] == response
    assert execution["deleted_records"] is None
    assert "currency" not in execution


def test_execute_maps_deleted_records_without_inventing_singular_write_root() -> None:
    response: dict[str, object] = {
        "currencies": [{"id": "dkk", **PARTIAL_CURRENCY}],
        "meta": {"deletedRecords": {"currencies": []}},
    }
    server, _ = make_server(lambda request: httpx.Response(200, json=response))
    preview = call_tool(server, "api_currencies_create_preview", {"currency": PARTIAL_CURRENCY})
    execution = call_tool(
        server,
        "api_currencies_create_execute",
        {"confirmation_ticket": preview["confirmation_ticket"]},
    )

    assert execution["changed_records"] == {"currencies": [{"id": "dkk", **PARTIAL_CURRENCY}]}
    assert execution["deleted_records"] == {"currencies": []}
    assert "currency" not in execution


def test_tamper_wrong_executor_expiry_and_replay_do_not_make_unexpected_writes() -> None:
    clock = Clock()
    server, requests = make_server(
        lambda request: httpx.Response(200, json={"currencies": [{"id": "dkk"}]}),
        confirmations=ConfirmationStore(clock),
    )
    preview = call_tool(server, "api_currencies_create_preview", {"currency": PARTIAL_CURRENCY})
    ticket = cast(str, preview["confirmation_ticket"])

    tampered = call_tool(
        server, "api_currencies_create_execute", {"confirmation_ticket": f"{ticket}x"}
    )
    wrong_executor = call_tool(
        server, "api_currencies_update_execute", {"confirmation_ticket": ticket}
    )
    assert tampered["code"] == StableErrorCode.CONFIRMATION_INVALID
    assert wrong_executor["code"] == StableErrorCode.CONFIRMATION_MISMATCH
    assert requests == []

    first = call_tool(server, "api_currencies_create_execute", {"confirmation_ticket": ticket})
    replay = call_tool(server, "api_currencies_create_execute", {"confirmation_ticket": ticket})
    assert first["changed_records"] == {"currencies": [{"id": "dkk"}]}
    assert replay["code"] == StableErrorCode.CONFIRMATION_CONSUMED
    assert len(requests) == 1

    expired_preview = call_tool(
        server, "api_currencies_create_preview", {"currency": PARTIAL_CURRENCY}
    )
    clock.now += timedelta(minutes=6)
    expired = call_tool(
        server,
        "api_currencies_create_execute",
        {"confirmation_ticket": expired_preview["confirmation_ticket"]},
    )
    assert expired["code"] == StableErrorCode.CONFIRMATION_EXPIRED
    assert len(requests) == 1


def test_ticket_binding_rejects_a_changed_currency_request() -> None:
    store = ConfirmationStore()
    specification = WriteOperationSpec(
        execute_tool_name="api_currencies_update_execute",
        method=WriteMethod.PUT,
        collection_path="/currencies",
        singular_root="currency",
        plural_root="currencies",
        payload={"name": "X"},
        resource_id="dkk",
        organization_id=None,
        summary="Update one Billy currency.",
        expected_effect_state={"action": "update", "resource": "currency", "id": "dkk"},
    )
    ticket = store.issue(confirmation_binding_for(specification))
    changed_specification = specification.model_copy(update={"payload": {"name": "Changed"}})

    with pytest.raises(ConfirmationFailure) as failure:
        store.consume(ticket.value, confirmation_binding_for(changed_specification))

    assert failure.value.error.code is StableErrorCode.CONFIRMATION_MISMATCH


def test_empty_token_returns_typed_auth_required_without_network_activity() -> None:
    server, requests = make_server(
        lambda request: pytest.fail(f"missing token attempted HTTP request: {request.url}"),
        token="",
    )
    preview = call_tool(server, "api_currencies_create_preview", {"currency": PARTIAL_CURRENCY})
    error = call_tool(
        server,
        "api_currencies_create_execute",
        {"confirmation_ticket": preview["confirmation_ticket"]},
    )

    assert error["code"] == StableErrorCode.AUTH_REQUIRED
    assert requests == []


def test_failed_currency_write_is_not_retried() -> None:
    server, requests = make_server(
        lambda request: httpx.Response(500, json={"errorCode": "INTERNAL_SERVER_ERROR"})
    )
    preview = call_tool(server, "api_currencies_create_preview", {"currency": PARTIAL_CURRENCY})
    error = call_tool(
        server,
        "api_currencies_create_execute",
        {"confirmation_ticket": preview["confirmation_ticket"]},
    )

    assert error["code"] == StableErrorCode.BILLY_ERROR
    assert len(requests) == 1
