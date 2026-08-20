"""Ticket tamper, expiry, replay, and auth tests for locale writes."""

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
from tests.api.test_locale_writes import PARTIAL_LOCALE, call_tool, make_server


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
            "api_locales_create_preview",
            "api_locales_create_execute",
            {"locale": PARTIAL_LOCALE},
            {"locales": [{"id": "da_DK", **PARTIAL_LOCALE}]},
            "POST",
            "/v2/locales",
            {"locale": PARTIAL_LOCALE},
        ),
        (
            "api_locales_update_preview",
            "api_locales_update_execute",
            {"id": "dk /?", "locale": PARTIAL_LOCALE},
            {"locales": [{"id": "dk /?", **PARTIAL_LOCALE}]},
            "PUT",
            "/v2/locales/dk%20%2F%3F",
            {"locale": PARTIAL_LOCALE},
        ),
    ],
)
def test_execute_sends_exact_singular_locale_write_shapes_once(
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
    assert "locale" not in execution


def test_execute_maps_deleted_records_without_inventing_singular_write_root() -> None:
    response: dict[str, object] = {
        "locales": [{"id": "da_DK", **PARTIAL_LOCALE}],
        "meta": {"deletedRecords": {"locales": []}},
    }
    server, _ = make_server(lambda request: httpx.Response(200, json=response))
    preview = call_tool(server, "api_locales_create_preview", {"locale": PARTIAL_LOCALE})
    execution = call_tool(
        server,
        "api_locales_create_execute",
        {"confirmation_ticket": preview["confirmation_ticket"]},
    )

    assert execution["changed_records"] == {"locales": [{"id": "da_DK", **PARTIAL_LOCALE}]}
    assert execution["deleted_records"] == {"locales": []}
    assert "locale" not in execution


def test_tamper_wrong_executor_expiry_and_replay_do_not_make_unexpected_writes() -> None:
    clock = Clock()
    server, requests = make_server(
        lambda request: httpx.Response(200, json={"locales": [{"id": "da_DK"}]}),
        confirmations=ConfirmationStore(clock),
    )
    preview = call_tool(server, "api_locales_create_preview", {"locale": PARTIAL_LOCALE})
    ticket = cast(str, preview["confirmation_ticket"])

    tampered = call_tool(
        server, "api_locales_create_execute", {"confirmation_ticket": f"{ticket}x"}
    )
    wrong_executor = call_tool(
        server, "api_locales_update_execute", {"confirmation_ticket": ticket}
    )
    assert tampered["code"] == StableErrorCode.CONFIRMATION_INVALID
    assert wrong_executor["code"] == StableErrorCode.CONFIRMATION_MISMATCH
    assert requests == []

    first = call_tool(server, "api_locales_create_execute", {"confirmation_ticket": ticket})
    replay = call_tool(server, "api_locales_create_execute", {"confirmation_ticket": ticket})
    assert first["changed_records"] == {"locales": [{"id": "da_DK"}]}
    assert replay["code"] == StableErrorCode.CONFIRMATION_CONSUMED
    assert len(requests) == 1

    expired_preview = call_tool(server, "api_locales_create_preview", {"locale": PARTIAL_LOCALE})
    clock.now += timedelta(minutes=6)
    expired = call_tool(
        server,
        "api_locales_create_execute",
        {"confirmation_ticket": expired_preview["confirmation_ticket"]},
    )
    assert expired["code"] == StableErrorCode.CONFIRMATION_EXPIRED
    assert len(requests) == 1


def test_ticket_binding_rejects_a_changed_locale_request() -> None:
    store = ConfirmationStore()
    specification = WriteOperationSpec(
        execute_tool_name="api_locales_update_execute",
        method=WriteMethod.PUT,
        collection_path="/locales",
        singular_root="locale",
        plural_root="locales",
        payload={"name": "X"},
        resource_id="da_DK",
        organization_id=None,
        summary="Update one Billy locale.",
        expected_effect_state={"action": "update", "resource": "locale", "id": "da_DK"},
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
    preview = call_tool(server, "api_locales_create_preview", {"locale": PARTIAL_LOCALE})
    error = call_tool(
        server,
        "api_locales_create_execute",
        {"confirmation_ticket": preview["confirmation_ticket"]},
    )

    assert error["code"] == StableErrorCode.AUTH_REQUIRED
    assert requests == []


def test_failed_locale_write_is_not_retried() -> None:
    server, requests = make_server(
        lambda request: httpx.Response(500, json={"errorCode": "INTERNAL_SERVER_ERROR"})
    )
    preview = call_tool(server, "api_locales_create_preview", {"locale": PARTIAL_LOCALE})
    error = call_tool(
        server,
        "api_locales_create_execute",
        {"confirmation_ticket": preview["confirmation_ticket"]},
    )

    assert error["code"] == StableErrorCode.BILLY_ERROR
    assert len(requests) == 1
