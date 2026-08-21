"""Contract tests for the ticketed singular Billy account write tools."""

from __future__ import annotations

import asyncio
import json
from collections.abc import Callable
from datetime import UTC, datetime
from typing import cast

import httpx
import pytest
from fastmcp import FastMCP
from pydantic import ValidationError

from billy_mcp.api.account_writes import (
    AccountCreatePreviewInput,
    AccountDeletePreviewInput,
    AccountGroupCreatePreviewInput,
    AccountGroupDeletePreviewInput,
    AccountGroupUpdatePreviewInput,
    AccountUpdatePreviewInput,
    register_account_write_tools,
)
from billy_mcp.api.daybook_balance_account_writes import (
    register_daybook_balance_account_write_tools,
)
from billy_mcp.api.write_protocol import (
    WriteExecuteInput,
    WriteMethod,
    WriteOperationSpec,
    WriteProtocolService,
    confirmation_binding_for,
)
from billy_mcp.client import BillyHttpClient
from billy_mcp.confirmations import (
    MAX_TICKET_TTL,
    ConfirmationFailure,
    ConfirmationStore,
)
from billy_mcp.models import StableErrorCode

MockHandler = Callable[[httpx.Request], httpx.Response]


class Clock:
    """Mutable UTC clock for deterministic confirmation-ticket expiry tests."""

    def __init__(self) -> None:
        self.now = datetime(2026, 7, 29, tzinfo=UTC)

    def __call__(self) -> datetime:
        return self.now


def make_server(
    handler: MockHandler,
    *,
    token: str | None = "account-write-test-token",
    confirmations: ConfirmationStore | None = None,
    include_daybook_balance_account_tools: bool = False,
) -> tuple[FastMCP, list[httpx.Request]]:
    """Create a fully local FastMCP server with a recording locked client."""

    requests: list[httpx.Request] = []

    def recording_handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return handler(request)

    client = BillyHttpClient(
        lambda: token,
        transport=httpx.MockTransport(recording_handler),
    )
    server = FastMCP("account-write-contract-test")
    write_protocol = WriteProtocolService(client, confirmations or ConfirmationStore())
    register_account_write_tools(
        server,
        client,
        write_protocol,
    )
    if include_daybook_balance_account_tools:
        register_daybook_balance_account_write_tools(server, client, write_protocol)
    return server, requests


def call_tool(server: FastMCP, tool_name: str, arguments: dict[str, object]) -> dict[str, object]:
    """Call one registered tool and return its structured result payload."""

    result = asyncio.run(server.call_tool(tool_name, arguments))
    structured_content = result.structured_content
    assert isinstance(structured_content, dict)
    payload = structured_content.get("result", structured_content)
    assert isinstance(payload, dict)
    return cast(dict[str, object], payload)


def test_registers_exactly_twelve_flat_strict_account_write_tools() -> None:
    server, _ = make_server(lambda request: httpx.Response(200, json={}))

    tools = {tool.name: tool for tool in asyncio.run(server.list_tools())}
    expected_properties = {
        "api_account_groups_create_preview": {"accountGroup"},
        "api_account_groups_create_execute": {"confirmation_ticket"},
        "api_account_groups_update_preview": {"id", "accountGroup"},
        "api_account_groups_update_execute": {"confirmation_ticket"},
        "api_account_groups_delete_preview": {"id"},
        "api_account_groups_delete_execute": {"confirmation_ticket"},
        "api_accounts_create_preview": {"account"},
        "api_accounts_create_execute": {"confirmation_ticket"},
        "api_accounts_update_preview": {"id", "account"},
        "api_accounts_update_execute": {"confirmation_ticket"},
        "api_accounts_delete_preview": {"id"},
        "api_accounts_delete_execute": {"confirmation_ticket"},
    }

    assert set(tools) == set(expected_properties)
    for name, fields in expected_properties.items():
        schema = tools[name].parameters
        properties = cast(dict[str, object], schema["properties"])
        assert schema["additionalProperties"] is False
        assert set(properties) == fields
        assert "input" not in properties
        if fields == {"confirmation_ticket"}:
            ticket = properties["confirmation_ticket"]
            assert isinstance(ticket, dict)
            assert ticket["minLength"] == 1
        elif "id" in fields:
            identifier = properties["id"]
            assert isinstance(identifier, dict)
            assert identifier["minLength"] == 1


@pytest.mark.parametrize(
    ("input_model", "payload"),
    [
        (AccountGroupCreatePreviewInput, {"accountGroup": {}, "unexpected": True}),
        (
            AccountGroupUpdatePreviewInput,
            {"id": "group-1", "accountGroup": {}, "unexpected": True},
        ),
        (AccountGroupDeletePreviewInput, {"id": "group-1", "unexpected": True}),
        (AccountCreatePreviewInput, {"account": {}, "unexpected": True}),
        (AccountUpdatePreviewInput, {"id": "account-1", "account": {}, "unexpected": True}),
        (AccountDeletePreviewInput, {"id": "account-1", "unexpected": True}),
        (AccountGroupUpdatePreviewInput, {"id": "", "accountGroup": {}}),
        (AccountDeletePreviewInput, {"id": ""}),
        (WriteExecuteInput, {"confirmation_ticket": "ticket", "account": {}}),
    ],
)
def test_outer_inputs_forbid_extras_and_empty_identifiers(
    input_model: type[AccountGroupCreatePreviewInput]
    | type[AccountGroupUpdatePreviewInput]
    | type[AccountGroupDeletePreviewInput]
    | type[AccountCreatePreviewInput]
    | type[AccountUpdatePreviewInput]
    | type[AccountDeletePreviewInput]
    | type[WriteExecuteInput],
    payload: dict[str, object],
) -> None:
    with pytest.raises(ValidationError):
        input_model.model_validate(payload)


@pytest.mark.parametrize(
    ("tool_name", "arguments", "expected_request"),
    [
        (
            "api_account_groups_create_preview",
            {"accountGroup": {"name": "Revenue", "customField": {"rank": 2}}},
            {"accountGroup": {"name": "Revenue", "customField": {"rank": 2}}},
        ),
        (
            "api_account_groups_update_preview",
            {"id": "group-1", "accountGroup": {"name": "Revenue"}},
            {"accountGroup": {"name": "Revenue"}},
        ),
        ("api_account_groups_delete_preview", {"id": "group-1"}, {"id": "group-1"}),
        (
            "api_accounts_create_preview",
            {"account": {"name": "Sales", "accountGroupId": "group-1"}},
            {"account": {"name": "Sales", "accountGroupId": "group-1"}},
        ),
        (
            "api_accounts_update_preview",
            {"id": "account-1", "account": {"name": "Replacement"}},
            {"account": {"name": "Replacement"}},
        ),
        ("api_accounts_delete_preview", {"id": "account-1"}, {"id": "account-1"}),
    ],
)
def test_previews_are_mutation_free_and_bind_exact_canonical_requests(
    tool_name: str,
    arguments: dict[str, object],
    expected_request: dict[str, object],
) -> None:
    server, requests = make_server(
        lambda request: pytest.fail(f"preview made an HTTP request: {request.method} {request.url}")
    )

    preview = call_tool(server, tool_name, arguments)

    assert requests == []
    assert preview["canonical_request"] == expected_request
    action = tool_name.removesuffix("_preview").rsplit("_", maxsplit=1)[-1]
    resource = "accountGroup" if tool_name.startswith("api_account_groups_") else "account"
    expected_effect_state: dict[str, object] = {"action": action, "resource": resource}
    if "id" in arguments:
        expected_effect_state["id"] = arguments["id"]
    assert preview["expected_effect_state"] == expected_effect_state
    assert isinstance(preview["confirmation_ticket"], str)
    assert preview["confirmation_ticket"]


@pytest.mark.parametrize(
    (
        "preview_tool",
        "execute_tool",
        "preview_input",
        "response",
        "expected_method",
        "expected_path",
        "expected_body",
        "expected_records",
        "expected_deleted_records",
    ),
    [
        (
            "api_account_groups_create_preview",
            "api_account_groups_create_execute",
            {"accountGroup": {"name": "Revenue"}},
            {"accountGroups": [{"id": "group-1", "name": "Revenue"}]},
            "POST",
            "/v2/accountGroups",
            {"accountGroup": {"name": "Revenue"}},
            {"accountGroups": [{"id": "group-1", "name": "Revenue"}]},
            None,
        ),
        (
            "api_account_groups_update_preview",
            "api_account_groups_update_execute",
            {"id": "group /?", "accountGroup": {"name": "Replacement"}},
            {"accountGroups": [{"id": "group /?", "name": "Replacement"}]},
            "PUT",
            "/v2/accountGroups/group%20%2F%3F",
            {"accountGroup": {"name": "Replacement"}},
            {"accountGroups": [{"id": "group /?", "name": "Replacement"}]},
            None,
        ),
        (
            "api_account_groups_delete_preview",
            "api_account_groups_delete_execute",
            {"id": "group /?"},
            {"meta": {"deletedRecords": {"accountGroups": ["group /?"]}}},
            "DELETE",
            "/v2/accountGroups/group%20%2F%3F",
            None,
            {},
            {"accountGroups": ["group /?"]},
        ),
        (
            "api_accounts_create_preview",
            "api_accounts_create_execute",
            {"account": {"name": "Sales", "accountGroupId": "group-1"}},
            {"accounts": [{"id": "account-1", "name": "Sales"}]},
            "POST",
            "/v2/accounts",
            {"account": {"name": "Sales", "accountGroupId": "group-1"}},
            {"accounts": [{"id": "account-1", "name": "Sales"}]},
            None,
        ),
        (
            "api_accounts_update_preview",
            "api_accounts_update_execute",
            {"id": "account /?", "account": {"name": "Replacement"}},
            {"accounts": [{"id": "account /?", "name": "Replacement"}]},
            "PUT",
            "/v2/accounts/account%20%2F%3F",
            {"account": {"name": "Replacement"}},
            {"accounts": [{"id": "account /?", "name": "Replacement"}]},
            None,
        ),
        (
            "api_accounts_delete_preview",
            "api_accounts_delete_execute",
            {"id": "account /?"},
            {"meta": {"deletedRecords": {"accounts": ["account /?"]}}},
            "DELETE",
            "/v2/accounts/account%20%2F%3F",
            None,
            {},
            {"accounts": ["account /?"]},
        ),
    ],
)
def test_execute_sends_exact_singular_account_cud_shapes_once(
    preview_tool: str,
    execute_tool: str,
    preview_input: dict[str, object],
    response: dict[str, object],
    expected_method: str,
    expected_path: str,
    expected_body: dict[str, object] | None,
    expected_records: dict[str, object],
    expected_deleted_records: dict[str, list[str]] | None,
) -> None:
    server, requests = make_server(lambda request: httpx.Response(200, json=response))

    preview = call_tool(server, preview_tool, preview_input)
    execution = call_tool(
        server,
        execute_tool,
        {"confirmation_ticket": preview["confirmation_ticket"]},
    )

    assert len(requests) == 1
    request = requests[0]
    assert request.method == expected_method
    assert request.url.raw_path.decode() == expected_path
    assert execution["changed_records"] == expected_records
    assert execution["deleted_records"] == expected_deleted_records
    if expected_body is None:
        assert request.content == b""
    else:
        assert json.loads(request.content) == expected_body


def test_invalid_tampered_expired_and_replayed_tickets_fail_without_extra_writes() -> None:
    clock = Clock()
    server, requests = make_server(
        lambda request: httpx.Response(200, json={"accounts": [{"id": "account-1"}]}),
        confirmations=ConfirmationStore(clock),
    )

    invalid = call_tool(
        server,
        "api_accounts_create_execute",
        {"confirmation_ticket": "not-an-account-ticket"},
    )
    assert invalid["code"] == StableErrorCode.CONFIRMATION_INVALID
    assert requests == []

    tamper_preview = call_tool(
        server,
        "api_accounts_create_preview",
        {"account": {"name": "Sales"}},
    )
    ticket = tamper_preview["confirmation_ticket"]
    assert isinstance(ticket, str)
    tampered = call_tool(
        server,
        "api_accounts_create_execute",
        {"confirmation_ticket": f"{ticket}tampered"},
    )
    assert tampered["code"] == StableErrorCode.CONFIRMATION_INVALID
    assert requests == []

    expired_preview = call_tool(
        server,
        "api_accounts_create_preview",
        {"account": {"name": "Sales"}},
    )
    clock.now += MAX_TICKET_TTL
    expired = call_tool(
        server,
        "api_accounts_create_execute",
        {"confirmation_ticket": expired_preview["confirmation_ticket"]},
    )
    assert expired["code"] == StableErrorCode.CONFIRMATION_EXPIRED
    assert requests == []

    replay_preview = call_tool(
        server,
        "api_accounts_create_preview",
        {"account": {"name": "Sales"}},
    )
    first = call_tool(
        server,
        "api_accounts_create_execute",
        {"confirmation_ticket": replay_preview["confirmation_ticket"]},
    )
    replayed = call_tool(
        server,
        "api_accounts_create_execute",
        {"confirmation_ticket": replay_preview["confirmation_ticket"]},
    )

    assert first["changed_records"] == {"accounts": [{"id": "account-1"}]}
    assert replayed["code"] == StableErrorCode.CONFIRMATION_CONSUMED
    assert len(requests) == 1


def test_account_ticket_rejects_a_different_executor_in_the_same_module() -> None:
    server, requests = make_server(
        lambda request: httpx.Response(200, json={"accounts": [{"id": "account-1"}]}),
    )

    preview = call_tool(
        server,
        "api_accounts_create_preview",
        {"account": {"name": "Sales"}},
    )
    wrong_executor = call_tool(
        server,
        "api_account_groups_delete_execute",
        {"confirmation_ticket": preview["confirmation_ticket"]},
    )

    assert wrong_executor["code"] == StableErrorCode.CONFIRMATION_MISMATCH
    assert requests == []

    correct_executor = call_tool(
        server,
        "api_accounts_create_execute",
        {"confirmation_ticket": preview["confirmation_ticket"]},
    )
    assert correct_executor["changed_records"] == {"accounts": [{"id": "account-1"}]}
    assert len(requests) == 1


def test_account_ticket_rejects_a_different_module_executor() -> None:
    server, requests = make_server(
        lambda request: httpx.Response(200, json={"accounts": [{"id": "account-1"}]}),
        include_daybook_balance_account_tools=True,
    )

    preview = call_tool(
        server,
        "api_accounts_create_preview",
        {"account": {"name": "Sales"}},
    )
    wrong_executor = call_tool(
        server,
        "api_daybook_balance_accounts_delete_execute",
        {"confirmation_ticket": preview["confirmation_ticket"]},
    )

    assert wrong_executor["code"] == StableErrorCode.CONFIRMATION_MISMATCH
    assert requests == []

    correct_executor = call_tool(
        server,
        "api_accounts_create_execute",
        {"confirmation_ticket": preview["confirmation_ticket"]},
    )
    assert correct_executor["changed_records"] == {"accounts": [{"id": "account-1"}]}
    assert len(requests) == 1


@pytest.mark.parametrize(
    "changes",
    [
        {"execute_tool_name": "api_accounts_other_execute"},
        {"organization_id": "other-organisation"},
        {"resource_id": "other-account"},
        {"payload": {"name": "Changed"}},
        {"expected_effect_state": {"action": "other"}},
    ],
)
def test_account_ticket_binding_rejects_every_mutated_operation_field(
    changes: dict[str, object],
) -> None:
    specification = WriteOperationSpec(
        execute_tool_name="api_accounts_update_execute",
        method=WriteMethod.PUT,
        collection_path="/accounts",
        singular_root="account",
        plural_root="accounts",
        payload={"name": "Sales"},
        resource_id="account-1",
        organization_id=None,
        summary="Update one Billy account.",
        expected_effect_state={"action": "update", "resource": "account", "id": "account-1"},
    )
    store = ConfirmationStore()
    ticket = store.issue(confirmation_binding_for(specification))
    mismatched = specification.model_copy(update=changes)

    with pytest.raises(ConfirmationFailure) as failure:
        store.consume(ticket.value, confirmation_binding_for(mismatched))

    assert failure.value.error.code is StableErrorCode.CONFIRMATION_MISMATCH


@pytest.mark.parametrize(
    ("status", "response", "preview_tool", "preview_input", "execute_tool", "expected_code"),
    [
        (
            401,
            {"errorCode": "AUTHENTICATION_REQUIRED"},
            "api_account_groups_create_preview",
            {"accountGroup": {"name": "Revenue"}},
            "api_account_groups_create_execute",
            StableErrorCode.AUTH_REQUIRED,
        ),
        (
            404,
            {"errorCode": "RECORD_NOT_FOUND"},
            "api_accounts_update_preview",
            {"id": "missing-account", "account": {"name": "Sales"}},
            "api_accounts_update_execute",
            StableErrorCode.NOT_FOUND,
        ),
    ],
)
def test_typed_authentication_and_not_found_errors_propagate(
    status: int,
    response: dict[str, str],
    preview_tool: str,
    preview_input: dict[str, object],
    execute_tool: str,
    expected_code: StableErrorCode,
) -> None:
    server, requests = make_server(lambda request: httpx.Response(status, json=response))

    preview = call_tool(server, preview_tool, preview_input)
    error = call_tool(
        server,
        execute_tool,
        {"confirmation_ticket": preview["confirmation_ticket"]},
    )

    assert error["code"] == expected_code
    assert len(requests) == 1


def test_empty_token_returns_typed_auth_error_without_network_access() -> None:
    server, requests = make_server(
        lambda request: pytest.fail(f"empty token attempted network access: {request.url}"),
        token="",
    )

    preview = call_tool(
        server,
        "api_accounts_create_preview",
        {"account": {"name": "Sales"}},
    )
    error = call_tool(
        server,
        "api_accounts_create_execute",
        {"confirmation_ticket": preview["confirmation_ticket"]},
    )

    assert error["code"] == StableErrorCode.AUTH_REQUIRED
    assert requests == []


def test_absent_optional_deleted_records_are_not_fabricated() -> None:
    server, _ = make_server(lambda request: httpx.Response(200, json={"meta": {}}))

    preview = call_tool(server, "api_accounts_delete_preview", {"id": "account-1"})
    execution = call_tool(
        server,
        "api_accounts_delete_execute",
        {"confirmation_ticket": preview["confirmation_ticket"]},
    )

    assert execution == {"changed_records": {}, "deleted_records": None}
