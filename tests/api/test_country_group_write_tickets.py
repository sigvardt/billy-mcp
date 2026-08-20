"""Ticket tamper, expiry, replay, and auth tests for country-group writes."""

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
from tests.api.test_country_group_writes import PARTIAL_COUNTRY_GROUP, call_tool, make_server


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
            "api_country_groups_create_preview",
            "api_country_groups_create_execute",
            {"countryGroup": PARTIAL_COUNTRY_GROUP},
            {"countryGroups": [{"id": "group-1", **PARTIAL_COUNTRY_GROUP}]},
            "POST",
            "/v2/countryGroups",
            {"countryGroup": PARTIAL_COUNTRY_GROUP},
        ),
        (
            "api_country_groups_update_preview",
            "api_country_groups_update_execute",
            {"id": "group /?", "countryGroup": PARTIAL_COUNTRY_GROUP},
            {"countryGroups": [{"id": "group /?", **PARTIAL_COUNTRY_GROUP}]},
            "PUT",
            "/v2/countryGroups/group%20%2F%3F",
            {"countryGroup": PARTIAL_COUNTRY_GROUP},
        ),
    ],
)
def test_execute_sends_exact_singular_country_group_write_shapes_once(
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
    assert "countryGroup" not in execution


def test_execute_maps_deleted_records_without_inventing_singular_write_root() -> None:
    response: dict[str, object] = {
        "countryGroups": [{"id": "group-1", **PARTIAL_COUNTRY_GROUP}],
        "meta": {"deletedRecords": {"countryGroups": []}},
    }
    server, _ = make_server(lambda request: httpx.Response(200, json=response))
    preview = call_tool(
        server, "api_country_groups_create_preview", {"countryGroup": PARTIAL_COUNTRY_GROUP}
    )
    execution = call_tool(
        server,
        "api_country_groups_create_execute",
        {"confirmation_ticket": preview["confirmation_ticket"]},
    )

    assert execution["changed_records"] == {
        "countryGroups": [{"id": "group-1", **PARTIAL_COUNTRY_GROUP}]
    }
    assert execution["deleted_records"] == {"countryGroups": []}
    assert "countryGroup" not in execution


def test_tamper_wrong_executor_expiry_and_replay_do_not_make_unexpected_writes() -> None:
    clock = Clock()
    server, requests = make_server(
        lambda request: httpx.Response(200, json={"countryGroups": [{"id": "group-1"}]}),
        confirmations=ConfirmationStore(clock),
    )
    preview = call_tool(
        server, "api_country_groups_create_preview", {"countryGroup": PARTIAL_COUNTRY_GROUP}
    )
    ticket = cast(str, preview["confirmation_ticket"])

    tampered = call_tool(
        server, "api_country_groups_create_execute", {"confirmation_ticket": f"{ticket}x"}
    )
    wrong_executor = call_tool(
        server, "api_country_groups_update_execute", {"confirmation_ticket": ticket}
    )
    assert tampered["code"] == StableErrorCode.CONFIRMATION_INVALID
    assert wrong_executor["code"] == StableErrorCode.CONFIRMATION_MISMATCH
    assert requests == []

    first = call_tool(server, "api_country_groups_create_execute", {"confirmation_ticket": ticket})
    replay = call_tool(server, "api_country_groups_create_execute", {"confirmation_ticket": ticket})
    assert first["changed_records"] == {"countryGroups": [{"id": "group-1"}]}
    assert replay["code"] == StableErrorCode.CONFIRMATION_CONSUMED
    assert len(requests) == 1

    expired_preview = call_tool(
        server, "api_country_groups_create_preview", {"countryGroup": PARTIAL_COUNTRY_GROUP}
    )
    clock.now += timedelta(minutes=6)
    expired = call_tool(
        server,
        "api_country_groups_create_execute",
        {"confirmation_ticket": expired_preview["confirmation_ticket"]},
    )
    assert expired["code"] == StableErrorCode.CONFIRMATION_EXPIRED
    assert len(requests) == 1


def test_ticket_binding_rejects_a_changed_country_group_request() -> None:
    store = ConfirmationStore()
    specification = WriteOperationSpec(
        execute_tool_name="api_country_groups_update_execute",
        method=WriteMethod.PUT,
        collection_path="/countryGroups",
        singular_root="countryGroup",
        plural_root="countryGroups",
        payload={"name": "Nordics"},
        resource_id="group-1",
        organization_id=None,
        summary="Update one Billy country group.",
        expected_effect_state={"action": "update", "resource": "countryGroup", "id": "group-1"},
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
    preview = call_tool(
        server, "api_country_groups_create_preview", {"countryGroup": PARTIAL_COUNTRY_GROUP}
    )
    error = call_tool(
        server,
        "api_country_groups_create_execute",
        {"confirmation_ticket": preview["confirmation_ticket"]},
    )

    assert error["code"] == StableErrorCode.AUTH_REQUIRED
    assert requests == []


def test_failed_country_group_write_is_not_retried() -> None:
    server, requests = make_server(
        lambda request: httpx.Response(500, json={"errorCode": "INTERNAL_SERVER_ERROR"})
    )
    preview = call_tool(
        server, "api_country_groups_create_preview", {"countryGroup": PARTIAL_COUNTRY_GROUP}
    )
    error = call_tool(
        server,
        "api_country_groups_create_execute",
        {"confirmation_ticket": preview["confirmation_ticket"]},
    )

    assert error["code"] == StableErrorCode.BILLY_ERROR
    assert len(requests) == 1
