"""Ticket tamper, expiry, replay, and auth tests for balance-modifier writes."""

from __future__ import annotations

import json
from datetime import UTC, datetime, timedelta
from typing import cast

import httpx
import pytest

from billy_mcp.confirmations import ConfirmationStore
from billy_mcp.models import StableErrorCode
from tests.api.test_balance_modifier_writes import VALID_MODIFIER, call_tool, make_server


class Clock:
    """Controllable clock used only by local confirmation-expiry tests."""

    def __init__(self) -> None:
        self.now = datetime(2026, 7, 30, tzinfo=UTC)

    def __call__(self) -> datetime:
        return self.now


@pytest.mark.parametrize(
    ("preview_name", "execute_name", "arguments", "response", "method", "path", "body"),
    [
        (
            "api_balance_modifiers_create_preview",
            "api_balance_modifiers_create_execute",
            {"balanceModifier": VALID_MODIFIER},
            {"balanceModifiers": [{"id": "bm-1", **VALID_MODIFIER}]},
            "POST",
            "/v2/balanceModifiers",
            {"balanceModifier": VALID_MODIFIER},
        ),
        (
            "api_balance_modifiers_update_preview",
            "api_balance_modifiers_update_execute",
            {"id": "dk /?", "balanceModifier": VALID_MODIFIER},
            {"balanceModifiers": [{"id": "dk /?", **VALID_MODIFIER}]},
            "PUT",
            "/v2/balanceModifiers/dk%20%2F%3F",
            {"balanceModifier": VALID_MODIFIER},
        ),
    ],
)
def test_execute_sends_exact_singular_balance_modifier_write_shapes_once(
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
        server, execute_name, {"confirmation_ticket": preview["confirmation_ticket"]}
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
    assert "balanceModifier" not in execution


def test_execute_maps_deleted_records_without_inventing_singular_write_root() -> None:
    deleted_ids: list[str] = []
    response: dict[str, object] = {
        "balanceModifiers": [{"id": "bm-1", **VALID_MODIFIER}],
        "meta": {"deletedRecords": {"balanceModifiers": deleted_ids}},
    }
    server, _ = make_server(lambda request: httpx.Response(200, json=response))
    preview = call_tool(
        server, "api_balance_modifiers_create_preview", {"balanceModifier": VALID_MODIFIER}
    )
    execution = call_tool(
        server,
        "api_balance_modifiers_create_execute",
        {"confirmation_ticket": preview["confirmation_ticket"]},
    )
    assert execution["changed_records"] == {"balanceModifiers": [{"id": "bm-1", **VALID_MODIFIER}]}
    assert execution["deleted_records"] == {"balanceModifiers": []}
    assert "balanceModifier" not in execution


def test_tamper_wrong_executor_expiry_and_replay_do_not_make_unexpected_writes() -> None:
    clock = Clock()
    server, requests = make_server(
        lambda request: httpx.Response(200, json={"balanceModifiers": [{"id": "bm-1"}]}),
        confirmations=ConfirmationStore(clock),
    )
    preview = call_tool(
        server, "api_balance_modifiers_create_preview", {"balanceModifier": VALID_MODIFIER}
    )
    ticket = cast(str, preview["confirmation_ticket"])
    tampered = call_tool(
        server, "api_balance_modifiers_create_execute", {"confirmation_ticket": f"{ticket}x"}
    )
    wrong_executor = call_tool(
        server, "api_balance_modifiers_update_execute", {"confirmation_ticket": ticket}
    )
    assert tampered["code"] == StableErrorCode.CONFIRMATION_INVALID
    assert wrong_executor["code"] == StableErrorCode.CONFIRMATION_MISMATCH
    assert requests == []
    first = call_tool(
        server, "api_balance_modifiers_create_execute", {"confirmation_ticket": ticket}
    )
    replay = call_tool(
        server, "api_balance_modifiers_create_execute", {"confirmation_ticket": ticket}
    )
    assert first["changed_records"] == {"balanceModifiers": [{"id": "bm-1"}]}
    assert replay["code"] == StableErrorCode.CONFIRMATION_CONSUMED
    assert len(requests) == 1
    expired_preview = call_tool(
        server, "api_balance_modifiers_create_preview", {"balanceModifier": VALID_MODIFIER}
    )
    clock.now += timedelta(minutes=6)
    expired = call_tool(
        server,
        "api_balance_modifiers_create_execute",
        {"confirmation_ticket": expired_preview["confirmation_ticket"]},
    )
    assert expired["code"] == StableErrorCode.CONFIRMATION_EXPIRED
    assert len(requests) == 1


def test_empty_token_returns_typed_auth_required_without_network_activity() -> None:
    server, requests = make_server(
        lambda request: pytest.fail(f"missing token attempted HTTP request: {request.url}"),
        token="",
    )
    preview = call_tool(
        server, "api_balance_modifiers_create_preview", {"balanceModifier": VALID_MODIFIER}
    )
    error = call_tool(
        server,
        "api_balance_modifiers_create_execute",
        {"confirmation_ticket": preview["confirmation_ticket"]},
    )
    assert error["code"] == StableErrorCode.AUTH_REQUIRED
    assert requests == []


def test_failed_balance_modifier_write_is_not_retried() -> None:
    server, requests = make_server(
        lambda request: httpx.Response(500, json={"errorCode": "INTERNAL_SERVER_ERROR"})
    )
    preview = call_tool(
        server, "api_balance_modifiers_create_preview", {"balanceModifier": VALID_MODIFIER}
    )
    error = call_tool(
        server,
        "api_balance_modifiers_create_execute",
        {"confirmation_ticket": preview["confirmation_ticket"]},
    )
    assert error["code"] == StableErrorCode.BILLY_ERROR
    assert len(requests) == 1
