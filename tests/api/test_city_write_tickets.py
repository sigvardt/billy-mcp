"""Ticket tamper, expiry, replay, and auth tests for city writes."""

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
from tests.api.test_city_writes import PARTIAL_CITY, call_tool, make_server


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
            "api_cities_create_preview",
            "api_cities_create_execute",
            {"city": PARTIAL_CITY},
            {"cities": [{"id": "city-1", **PARTIAL_CITY}]},
            "POST",
            "/v2/cities",
            {"city": PARTIAL_CITY},
        ),
        (
            "api_cities_update_preview",
            "api_cities_update_execute",
            {"id": "city /?", "city": PARTIAL_CITY},
            {"cities": [{"id": "city /?", **PARTIAL_CITY}]},
            "PUT",
            "/v2/cities/city%20%2F%3F",
            {"city": PARTIAL_CITY},
        ),
    ],
)
def test_execute_sends_exact_singular_city_write_shapes_once(
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
    assert "city" not in execution


def test_execute_maps_deleted_records_without_inventing_singular_write_root() -> None:
    response: dict[str, object] = {
        "cities": [{"id": "city-1", **PARTIAL_CITY}],
        "meta": {"deletedRecords": {"cities": []}},
    }
    server, _ = make_server(lambda request: httpx.Response(200, json=response))
    preview = call_tool(server, "api_cities_create_preview", {"city": PARTIAL_CITY})
    execution = call_tool(
        server,
        "api_cities_create_execute",
        {"confirmation_ticket": preview["confirmation_ticket"]},
    )

    assert execution["changed_records"] == {"cities": [{"id": "city-1", **PARTIAL_CITY}]}
    assert execution["deleted_records"] == {"cities": []}
    assert "city" not in execution


def test_tamper_wrong_executor_expiry_and_replay_do_not_make_unexpected_writes() -> None:
    clock = Clock()
    server, requests = make_server(
        lambda request: httpx.Response(200, json={"cities": [{"id": "city-1"}]}),
        confirmations=ConfirmationStore(clock),
    )
    preview = call_tool(server, "api_cities_create_preview", {"city": PARTIAL_CITY})
    ticket = cast(str, preview["confirmation_ticket"])

    tampered = call_tool(server, "api_cities_create_execute", {"confirmation_ticket": f"{ticket}x"})
    wrong_executor = call_tool(server, "api_cities_update_execute", {"confirmation_ticket": ticket})
    assert tampered["code"] == StableErrorCode.CONFIRMATION_INVALID
    assert wrong_executor["code"] == StableErrorCode.CONFIRMATION_MISMATCH
    assert requests == []

    first = call_tool(server, "api_cities_create_execute", {"confirmation_ticket": ticket})
    replay = call_tool(server, "api_cities_create_execute", {"confirmation_ticket": ticket})
    assert first["changed_records"] == {"cities": [{"id": "city-1"}]}
    assert replay["code"] == StableErrorCode.CONFIRMATION_CONSUMED
    assert len(requests) == 1

    expired_preview = call_tool(server, "api_cities_create_preview", {"city": PARTIAL_CITY})
    clock.now += timedelta(minutes=6)
    expired = call_tool(
        server,
        "api_cities_create_execute",
        {"confirmation_ticket": expired_preview["confirmation_ticket"]},
    )
    assert expired["code"] == StableErrorCode.CONFIRMATION_EXPIRED
    assert len(requests) == 1


def test_ticket_binding_rejects_a_changed_city_request() -> None:
    store = ConfirmationStore()
    specification = WriteOperationSpec(
        execute_tool_name="api_cities_update_execute",
        method=WriteMethod.PUT,
        collection_path="/cities",
        singular_root="city",
        plural_root="cities",
        payload={"name": "Helsingor"},
        resource_id="city-1",
        organization_id=None,
        summary="Update one Billy city.",
        expected_effect_state={"action": "update", "resource": "city", "id": "city-1"},
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
    preview = call_tool(server, "api_cities_create_preview", {"city": PARTIAL_CITY})
    error = call_tool(
        server,
        "api_cities_create_execute",
        {"confirmation_ticket": preview["confirmation_ticket"]},
    )

    assert error["code"] == StableErrorCode.AUTH_REQUIRED
    assert requests == []


def test_failed_city_write_is_not_retried() -> None:
    server, requests = make_server(
        lambda request: httpx.Response(500, json={"errorCode": "INTERNAL_SERVER_ERROR"})
    )
    preview = call_tool(server, "api_cities_create_preview", {"city": PARTIAL_CITY})
    error = call_tool(
        server,
        "api_cities_create_execute",
        {"confirmation_ticket": preview["confirmation_ticket"]},
    )

    assert error["code"] == StableErrorCode.BILLY_ERROR
    assert len(requests) == 1
