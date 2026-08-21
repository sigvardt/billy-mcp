"""Contract tests for ticketed sales-tax account and meta-field write tools."""

from __future__ import annotations

import asyncio
import json
from collections.abc import Callable
from datetime import UTC, datetime, timedelta
from typing import cast

import httpx
import pytest
from fastmcp import FastMCP
from pydantic import BaseModel, ValidationError

from billy_mcp.api.sales_tax_account_meta_writes import (
    SalesTaxAccountCreatePreviewInput,
    SalesTaxAccountDeletePreviewInput,
    SalesTaxAccountUpdatePreviewInput,
    SalesTaxMetaFieldCreatePreviewInput,
    SalesTaxMetaFieldDeletePreviewInput,
    SalesTaxMetaFieldUpdatePreviewInput,
    register_sales_tax_account_meta_write_tools,
)
from billy_mcp.api.write_protocol import (
    WriteExecuteInput,
    WriteMethod,
    WriteOperationSpec,
    WriteProtocolService,
    confirmation_binding_for,
)
from billy_mcp.client import BillyHttpClient
from billy_mcp.confirmations import ConfirmationFailure, ConfirmationStore
from billy_mcp.models import StableErrorCode

MockHandler = Callable[[httpx.Request], httpx.Response]


class Clock:
    """Controllable clock used only by local ticket-expiry tests."""

    def __init__(self) -> None:
        self.now = datetime(2026, 7, 30, tzinfo=UTC)

    def __call__(self) -> datetime:
        return self.now


def make_server(
    handler: MockHandler,
    *,
    token: str | None = "sales-tax-account-meta-write-test-token",
    confirmations: ConfirmationStore | None = None,
) -> tuple[FastMCP, list[httpx.Request]]:
    """Create a fully local server with a locked recording transport."""

    requests: list[httpx.Request] = []

    def recording_handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return handler(request)

    client = BillyHttpClient(
        lambda: token,
        transport=httpx.MockTransport(recording_handler),
    )
    server = FastMCP("sales-tax-account-meta-write-contract-test")
    register_sales_tax_account_meta_write_tools(
        server,
        client,
        WriteProtocolService(client, confirmations or ConfirmationStore()),
    )
    return server, requests


def call_tool(server: FastMCP, tool_name: str, arguments: dict[str, object]) -> dict[str, object]:
    """Call one typed tool with its direct MCP argument object."""

    result = asyncio.run(server.call_tool(tool_name, arguments))
    structured_content = result.structured_content
    assert isinstance(structured_content, dict)
    payload = structured_content.get("result", structured_content)
    assert isinstance(payload, dict)
    return cast(dict[str, object], payload)


def test_registers_exactly_twelve_flat_typed_sales_tax_account_meta_write_tools() -> None:
    server, _ = make_server(lambda request: httpx.Response(200, json={}))

    by_name = {tool.name: tool for tool in asyncio.run(server.list_tools())}
    expected_properties = {
        "api_sales_tax_accounts_create_preview": {"salesTaxAccount"},
        "api_sales_tax_accounts_create_execute": {"confirmation_ticket"},
        "api_sales_tax_accounts_update_preview": {"id", "salesTaxAccount"},
        "api_sales_tax_accounts_update_execute": {"confirmation_ticket"},
        "api_sales_tax_accounts_delete_preview": {"id"},
        "api_sales_tax_accounts_delete_execute": {"confirmation_ticket"},
        "api_sales_tax_meta_fields_create_preview": {"salesTaxMetaField"},
        "api_sales_tax_meta_fields_create_execute": {"confirmation_ticket"},
        "api_sales_tax_meta_fields_update_preview": {"id", "salesTaxMetaField"},
        "api_sales_tax_meta_fields_update_execute": {"confirmation_ticket"},
        "api_sales_tax_meta_fields_delete_preview": {"id"},
        "api_sales_tax_meta_fields_delete_execute": {"confirmation_ticket"},
    }

    assert set(by_name) == set(expected_properties)
    for name, fields in expected_properties.items():
        schema = by_name[name].parameters
        properties = cast(dict[str, dict[str, object]], schema["properties"])
        assert schema["additionalProperties"] is False
        assert set(properties) == fields
        assert "input" not in properties
        for field in fields & {"id", "confirmation_ticket"}:
            assert properties[field]["minLength"] == 1


@pytest.mark.parametrize(
    ("input_model", "payload"),
    [
        (SalesTaxAccountCreatePreviewInput, {"salesTaxAccount": {}, "extra": True}),
        (
            SalesTaxAccountUpdatePreviewInput,
            {"id": "account-1", "salesTaxAccount": {}, "extra": True},
        ),
        (SalesTaxAccountDeletePreviewInput, {"id": "account-1", "extra": True}),
        (SalesTaxMetaFieldCreatePreviewInput, {"salesTaxMetaField": {}, "extra": True}),
        (
            SalesTaxMetaFieldUpdatePreviewInput,
            {"id": "meta-1", "salesTaxMetaField": {}, "extra": True},
        ),
        (SalesTaxMetaFieldDeletePreviewInput, {"id": "meta-1", "extra": True}),
        (SalesTaxAccountUpdatePreviewInput, {"id": "", "salesTaxAccount": {}}),
        (SalesTaxAccountDeletePreviewInput, {"id": ""}),
        (SalesTaxMetaFieldUpdatePreviewInput, {"id": "", "salesTaxMetaField": {}}),
        (SalesTaxMetaFieldDeletePreviewInput, {"id": ""}),
        (
            SalesTaxAccountUpdatePreviewInput,
            {"id": "account-1", "salesTaxAccount": {"id": "other"}},
        ),
        (
            SalesTaxMetaFieldUpdatePreviewInput,
            {"id": "meta-1", "salesTaxMetaField": {"id": "other"}},
        ),
        (WriteExecuteInput, {"confirmation_ticket": "ticket", "salesTaxAccount": {}}),
    ],
)
def test_outer_inputs_forbid_extras_empty_ids_and_mismatched_body_ids(
    input_model: type[BaseModel], payload: dict[str, object]
) -> None:
    with pytest.raises(ValidationError):
        input_model.model_validate(payload)


def test_opaque_inner_payloads_preserve_unknown_fields_and_matching_ids() -> None:
    account = SalesTaxAccountUpdatePreviewInput.model_validate(
        {"id": "account-1", "salesTaxAccount": {"id": "account-1", "future": {"rank": 2}}}
    )
    meta_field = SalesTaxMetaFieldUpdatePreviewInput.model_validate(
        {"id": "meta-1", "salesTaxMetaField": {"id": "meta-1", "future": {"rank": 3}}}
    )

    assert account.sales_tax_account["future"] == {"rank": 2}
    assert meta_field.sales_tax_meta_field["future"] == {"rank": 3}


@pytest.mark.parametrize(
    ("tool_name", "arguments", "expected_request", "expected_effect"),
    [
        (
            "api_sales_tax_accounts_create_preview",
            {"salesTaxAccount": {"opaqueAccountValue": {"rank": 2}}},
            {"salesTaxAccount": {"opaqueAccountValue": {"rank": 2}}},
            {"action": "create", "resource": "salesTaxAccount"},
        ),
        (
            "api_sales_tax_accounts_update_preview",
            {"id": "account-1", "salesTaxAccount": {"priority": 2}},
            {"salesTaxAccount": {"priority": 2}},
            {"action": "update", "resource": "salesTaxAccount", "id": "account-1"},
        ),
        (
            "api_sales_tax_accounts_delete_preview",
            {"id": "account-1"},
            {"id": "account-1"},
            {"action": "delete", "resource": "salesTaxAccount", "id": "account-1"},
        ),
        (
            "api_sales_tax_meta_fields_create_preview",
            {"salesTaxMetaField": {"opaqueMetaValue": {"rank": 2}}},
            {"salesTaxMetaField": {"opaqueMetaValue": {"rank": 2}}},
            {"action": "create", "resource": "salesTaxMetaField"},
        ),
        (
            "api_sales_tax_meta_fields_update_preview",
            {"id": "meta-1", "salesTaxMetaField": {"priority": 2}},
            {"salesTaxMetaField": {"priority": 2}},
            {"action": "update", "resource": "salesTaxMetaField", "id": "meta-1"},
        ),
        (
            "api_sales_tax_meta_fields_delete_preview",
            {"id": "meta-1"},
            {"id": "meta-1"},
            {"action": "delete", "resource": "salesTaxMetaField", "id": "meta-1"},
        ),
    ],
)
def test_previews_are_mutation_free_and_bind_exact_requests(
    tool_name: str,
    arguments: dict[str, object],
    expected_request: dict[str, object],
    expected_effect: dict[str, object],
) -> None:
    server, requests = make_server(
        lambda request: pytest.fail(f"preview made an HTTP request: {request.method} {request.url}")
    )

    preview = call_tool(server, tool_name, arguments)

    assert requests == []
    assert preview["canonical_request"] == expected_request
    assert preview["expected_effect_state"] == expected_effect
    assert isinstance(preview["confirmation_ticket"], str)


@pytest.mark.parametrize(
    (
        "preview_name, execute_name, arguments, response, method, path, body, "
        "expected_changed, expected_deleted"
    ),
    [
        (
            "api_sales_tax_accounts_create_preview",
            "api_sales_tax_accounts_create_execute",
            {"salesTaxAccount": {"account": {"id": "accounting-1"}, "type": "opaque"}},
            {"salesTaxAccounts": [{"id": "account-1"}], "salesTaxMetaFields": [{"id": "meta-1"}]},
            "POST",
            "/v2/salesTaxAccounts",
            {"salesTaxAccount": {"account": {"id": "accounting-1"}, "type": "opaque"}},
            {"salesTaxAccounts": [{"id": "account-1"}]},
            None,
        ),
        (
            "api_sales_tax_accounts_update_preview",
            "api_sales_tax_accounts_update_execute",
            {"id": "account /?", "salesTaxAccount": {"priority": 2}},
            {"salesTaxAccounts": [{"id": "account /?", "priority": 2}]},
            "PUT",
            "/v2/salesTaxAccounts/account%20%2F%3F",
            {"salesTaxAccount": {"priority": 2}},
            {"salesTaxAccounts": [{"id": "account /?", "priority": 2}]},
            None,
        ),
        (
            "api_sales_tax_accounts_delete_preview",
            "api_sales_tax_accounts_delete_execute",
            {"id": "account /?"},
            {"meta": {"deletedRecords": {"salesTaxAccounts": ["account /?"]}}},
            "DELETE",
            "/v2/salesTaxAccounts/account%20%2F%3F",
            None,
            {},
            {"salesTaxAccounts": ["account /?"]},
        ),
        (
            "api_sales_tax_meta_fields_create_preview",
            "api_sales_tax_meta_fields_create_execute",
            {"salesTaxMetaField": {"name": "Opaque field", "isPredefined": False}},
            {"salesTaxMetaFields": [{"id": "meta-1", "name": "Opaque field"}]},
            "POST",
            "/v2/salesTaxMetaFields",
            {"salesTaxMetaField": {"name": "Opaque field", "isPredefined": False}},
            {"salesTaxMetaFields": [{"id": "meta-1", "name": "Opaque field"}]},
            None,
        ),
        (
            "api_sales_tax_meta_fields_update_preview",
            "api_sales_tax_meta_fields_update_execute",
            {"id": "meta /?", "salesTaxMetaField": {"priority": 2}},
            {"salesTaxMetaFields": [{"id": "meta /?", "priority": 2}]},
            "PUT",
            "/v2/salesTaxMetaFields/meta%20%2F%3F",
            {"salesTaxMetaField": {"priority": 2}},
            {"salesTaxMetaFields": [{"id": "meta /?", "priority": 2}]},
            None,
        ),
        (
            "api_sales_tax_meta_fields_delete_preview",
            "api_sales_tax_meta_fields_delete_execute",
            {"id": "meta /?"},
            {"meta": {"deletedRecords": {"salesTaxMetaFields": ["meta /?"]}}},
            "DELETE",
            "/v2/salesTaxMetaFields/meta%20%2F%3F",
            None,
            {},
            {"salesTaxMetaFields": ["meta /?"]},
        ),
    ],
)
def test_execute_sends_exact_singular_cud_shapes_once(
    preview_name: str,
    execute_name: str,
    arguments: dict[str, object],
    response: dict[str, object],
    method: str,
    path: str,
    body: dict[str, object] | None,
    expected_changed: dict[str, object],
    expected_deleted: dict[str, list[str]] | None,
) -> None:
    server, requests = make_server(lambda request: httpx.Response(200, json=response))

    preview = call_tool(server, preview_name, arguments)
    execution = call_tool(
        server, execute_name, {"confirmation_ticket": preview["confirmation_ticket"]}
    )

    assert len(requests) == 1
    request = requests[0]
    assert request.method == method
    assert request.url.raw_path.decode() == path
    assert execution["changed_records"] == expected_changed
    assert execution["deleted_records"] == expected_deleted
    if body is None:
        assert request.content == b""
    else:
        assert json.loads(request.content) == body


@pytest.mark.parametrize(
    "response",
    [
        {"salesTaxMetaFields": [{"id": "meta-1"}]},
        {"salesTaxAccounts": {"id": "account-1"}},
    ],
)
def test_create_does_not_map_sibling_roots_or_malformed_primary_roots(
    response: dict[str, object],
) -> None:
    server, _ = make_server(lambda request: httpx.Response(200, json=response))

    preview = call_tool(
        server,
        "api_sales_tax_accounts_create_preview",
        {"salesTaxAccount": {"type": "opaque"}},
    )
    execution = call_tool(
        server,
        "api_sales_tax_accounts_create_execute",
        {"confirmation_ticket": preview["confirmation_ticket"]},
    )

    assert execution["code"] == StableErrorCode.VALIDATION_ERROR


def test_deletes_do_not_invent_absent_roots_or_deleted_metadata() -> None:
    server, _ = make_server(lambda request: httpx.Response(200, json={"meta": {}}))

    preview = call_tool(server, "api_sales_tax_meta_fields_delete_preview", {"id": "meta-1"})
    execution = call_tool(
        server,
        "api_sales_tax_meta_fields_delete_execute",
        {"confirmation_ticket": preview["confirmation_ticket"]},
    )

    assert execution == {"changed_records": {}, "deleted_records": None}


def test_tampered_expired_replayed_and_same_resource_executor_tickets_do_not_write() -> None:
    clock = Clock()
    server, requests = make_server(
        lambda request: httpx.Response(200, json={"salesTaxAccounts": [{"id": "account-1"}]}),
        confirmations=ConfirmationStore(clock),
    )
    preview = call_tool(
        server,
        "api_sales_tax_accounts_create_preview",
        {"salesTaxAccount": {"type": "opaque"}},
    )
    ticket = cast(str, preview["confirmation_ticket"])

    tampered = call_tool(
        server,
        "api_sales_tax_accounts_create_execute",
        {"confirmation_ticket": f"{ticket}x"},
    )
    wrong_executor = call_tool(
        server,
        "api_sales_tax_accounts_delete_execute",
        {"confirmation_ticket": ticket},
    )
    assert tampered["code"] == StableErrorCode.CONFIRMATION_INVALID
    assert wrong_executor["code"] == StableErrorCode.CONFIRMATION_MISMATCH
    assert requests == []

    clock.now += timedelta(minutes=6)
    expired = call_tool(
        server,
        "api_sales_tax_accounts_create_execute",
        {"confirmation_ticket": ticket},
    )
    assert expired["code"] == StableErrorCode.CONFIRMATION_EXPIRED
    assert requests == []

    replay_preview = call_tool(
        server,
        "api_sales_tax_accounts_create_preview",
        {"salesTaxAccount": {"type": "opaque"}},
    )
    replay_ticket = cast(str, replay_preview["confirmation_ticket"])
    first = call_tool(
        server,
        "api_sales_tax_accounts_create_execute",
        {"confirmation_ticket": replay_ticket},
    )
    replay = call_tool(
        server,
        "api_sales_tax_accounts_create_execute",
        {"confirmation_ticket": replay_ticket},
    )
    assert first["changed_records"] == {"salesTaxAccounts": [{"id": "account-1"}]}
    assert replay["code"] == StableErrorCode.CONFIRMATION_CONSUMED
    assert len(requests) == 1


@pytest.mark.parametrize(
    "changes",
    [
        {"execute_tool_name": "api_sales_tax_accounts_other_execute"},
        {"organization_id": "other-organisation"},
        {"resource_id": "other-account"},
        {"payload": {"priority": 3}},
        {"expected_effect_state": {"action": "other"}},
    ],
)
def test_ticket_binding_rejects_executor_organisation_target_payload_and_effect_changes(
    changes: dict[str, object],
) -> None:
    specification = WriteOperationSpec(
        execute_tool_name="api_sales_tax_accounts_update_execute",
        method=WriteMethod.PUT,
        collection_path="/salesTaxAccounts",
        singular_root="salesTaxAccount",
        plural_root="salesTaxAccounts",
        additional_plural_roots=(),
        payload={"priority": 2},
        resource_id="account-1",
        organization_id=None,
        summary="Update one Billy sales-tax account.",
        expected_effect_state={
            "action": "update",
            "resource": "salesTaxAccount",
            "id": "account-1",
        },
    )
    store = ConfirmationStore()
    ticket = store.issue(confirmation_binding_for(specification))

    with pytest.raises(ConfirmationFailure) as failure:
        store.consume(
            ticket.value, confirmation_binding_for(specification.model_copy(update=changes))
        )

    assert failure.value.error.code is StableErrorCode.CONFIRMATION_MISMATCH


def test_empty_token_returns_typed_auth_error_without_network_activity() -> None:
    server, requests = make_server(
        lambda request: pytest.fail(f"missing token attempted HTTP request: {request.url}"),
        token="",
    )
    preview = call_tool(
        server,
        "api_sales_tax_meta_fields_create_preview",
        {"salesTaxMetaField": {"name": "opaque"}},
    )
    error = call_tool(
        server,
        "api_sales_tax_meta_fields_create_execute",
        {"confirmation_ticket": preview["confirmation_ticket"]},
    )

    assert error["code"] == StableErrorCode.AUTH_REQUIRED
    assert requests == []


@pytest.mark.parametrize(
    "status, response, preview_name, arguments, execute_name, expected_code",
    [
        (
            401,
            {"errorCode": "AUTHENTICATION_REQUIRED"},
            "api_sales_tax_accounts_create_preview",
            {"salesTaxAccount": {"type": "opaque"}},
            "api_sales_tax_accounts_create_execute",
            StableErrorCode.AUTH_REQUIRED,
        ),
        (
            404,
            {"errorCode": "RECORD_NOT_FOUND"},
            "api_sales_tax_meta_fields_update_preview",
            {"id": "missing", "salesTaxMetaField": {"priority": 2}},
            "api_sales_tax_meta_fields_update_execute",
            StableErrorCode.NOT_FOUND,
        ),
    ],
)
def test_typed_authentication_and_not_found_errors_propagate(
    status: int,
    response: dict[str, str],
    preview_name: str,
    arguments: dict[str, object],
    execute_name: str,
    expected_code: StableErrorCode,
) -> None:
    server, requests = make_server(lambda request: httpx.Response(status, json=response))

    preview = call_tool(server, preview_name, arguments)
    error = call_tool(server, execute_name, {"confirmation_ticket": preview["confirmation_ticket"]})

    assert error["code"] == expected_code
    assert len(requests) == 1


def test_write_failure_is_not_retried() -> None:
    server, requests = make_server(
        lambda request: httpx.Response(500, json={"errorCode": "INTERNAL_SERVER_ERROR"})
    )
    preview = call_tool(
        server,
        "api_sales_tax_meta_fields_create_preview",
        {"salesTaxMetaField": {"name": "opaque"}},
    )
    error = call_tool(
        server,
        "api_sales_tax_meta_fields_create_execute",
        {"confirmation_ticket": preview["confirmation_ticket"]},
    )

    assert error["code"] == StableErrorCode.BILLY_ERROR
    assert len(requests) == 1
