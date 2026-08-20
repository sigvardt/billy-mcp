"""Ticket tamper, expiry, replay, and auth tests for zipcode writes."""

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
from tests.api.test_zipcode_writes import PARTIAL_ZIPCODE, call_tool, make_server


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
            "api_zipcodes_create_preview",
            "api_zipcodes_create_execute",
            {"zipcode": PARTIAL_ZIPCODE},
            {"zipcodes": [{"id": "zip-1", **PARTIAL_ZIPCODE}]},
            "POST",
            "/v2/zipcodes",
            {"zipcode": PARTIAL_ZIPCODE},
        ),
        (
            "api_zipcodes_update_preview",
            "api_zipcodes_update_execute",
            {"id": "dk /?", "zipcode": PARTIAL_ZIPCODE},
            {"zipcodes": [{"id": "dk /?", **PARTIAL_ZIPCODE}]},
            "PUT",
            "/v2/zipcodes/dk%20%2F%3F",
            {"zipcode": PARTIAL_ZIPCODE},
        ),
    ],
)
def test_execute_sends_exact_singular_zipcode_write_shapes_once(
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
    assert "zipcode" not in execution


def test_execute_maps_deleted_records_without_inventing_singular_write_root() -> None:
    response: dict[str, object] = {
        "zipcodes": [{"id": "zip-1", **PARTIAL_ZIPCODE}],
        "meta": {"deletedRecords": {"zipcodes": []}},
    }
    server, _ = make_server(lambda request: httpx.Response(200, json=response))
    preview = call_tool(server, "api_zipcodes_create_preview", {"zipcode": PARTIAL_ZIPCODE})
    execution = call_tool(
        server,
        "api_zipcodes_create_execute",
        {"confirmation_ticket": preview["confirmation_ticket"]},
    )

    assert execution["changed_records"] == {"zipcodes": [{"id": "zip-1", **PARTIAL_ZIPCODE}]}
    assert execution["deleted_records"] == {"zipcodes": []}
    assert "zipcode" not in execution


def test_tamper_wrong_executor_expiry_and_replay_do_not_make_unexpected_writes() -> None:
    clock = Clock()
    server, requests = make_server(
        lambda request: httpx.Response(200, json={"zipcodes": [{"id": "zip-1"}]}),
        confirmations=ConfirmationStore(clock),
    )
    preview = call_tool(server, "api_zipcodes_create_preview", {"zipcode": PARTIAL_ZIPCODE})
    ticket = cast(str, preview["confirmation_ticket"])

    tampered = call_tool(
        server, "api_zipcodes_create_execute", {"confirmation_ticket": f"{ticket}x"}
    )
    wrong_executor = call_tool(
        server, "api_zipcodes_update_execute", {"confirmation_ticket": ticket}
    )
    assert tampered["code"] == StableErrorCode.CONFIRMATION_INVALID
    assert wrong_executor["code"] == StableErrorCode.CONFIRMATION_MISMATCH
    assert requests == []

    first = call_tool(server, "api_zipcodes_create_execute", {"confirmation_ticket": ticket})
    replay = call_tool(server, "api_zipcodes_create_execute", {"confirmation_ticket": ticket})
    assert first["changed_records"] == {"zipcodes": [{"id": "zip-1"}]}
    assert replay["code"] == StableErrorCode.CONFIRMATION_CONSUMED
    assert len(requests) == 1

    expired_preview = call_tool(server, "api_zipcodes_create_preview", {"zipcode": PARTIAL_ZIPCODE})
    clock.now += timedelta(minutes=6)
    expired = call_tool(
        server,
        "api_zipcodes_create_execute",
        {"confirmation_ticket": expired_preview["confirmation_ticket"]},
    )
    assert expired["code"] == StableErrorCode.CONFIRMATION_EXPIRED
    assert len(requests) == 1


def test_ticket_binding_rejects_a_changed_zipcode_request() -> None:
    store = ConfirmationStore()
    specification = WriteOperationSpec(
        execute_tool_name="api_zipcodes_update_execute",
        method=WriteMethod.PUT,
        collection_path="/zipcodes",
        singular_root="zipcode",
        plural_root="zipcodes",
        payload={"zipcode": "2100"},
        resource_id="zip-1",
        organization_id=None,
        summary="Update one Billy zipcode.",
        expected_effect_state={"action": "update", "resource": "zipcode", "id": "zip-1"},
    )
    ticket = store.issue(confirmation_binding_for(specification))
    changed_specification = specification.model_copy(update={"payload": {"zipcode": "2200"}})

    with pytest.raises(ConfirmationFailure) as failure:
        store.consume(ticket.value, confirmation_binding_for(changed_specification))

    assert failure.value.error.code is StableErrorCode.CONFIRMATION_MISMATCH


def test_empty_token_returns_typed_auth_required_without_network_activity() -> None:
    server, requests = make_server(
        lambda request: pytest.fail(f"missing token attempted HTTP request: {request.url}"),
        token="",
    )
    preview = call_tool(server, "api_zipcodes_create_preview", {"zipcode": PARTIAL_ZIPCODE})
    error = call_tool(
        server,
        "api_zipcodes_create_execute",
        {"confirmation_ticket": preview["confirmation_ticket"]},
    )

    assert error["code"] == StableErrorCode.AUTH_REQUIRED
    assert requests == []


def test_failed_zipcode_write_is_not_retried() -> None:
    server, requests = make_server(
        lambda request: httpx.Response(500, json={"errorCode": "INTERNAL_SERVER_ERROR"})
    )
    preview = call_tool(server, "api_zipcodes_create_preview", {"zipcode": PARTIAL_ZIPCODE})
    error = call_tool(
        server,
        "api_zipcodes_create_execute",
        {"confirmation_ticket": preview["confirmation_ticket"]},
    )

    assert error["code"] == StableErrorCode.BILLY_ERROR
    assert len(requests) == 1
