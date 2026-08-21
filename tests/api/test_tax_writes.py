"""Contract tests for ticketed singular Billy tax write tools."""

from __future__ import annotations

import asyncio
import json
from collections.abc import Callable
from datetime import UTC, datetime, timedelta
from typing import cast

import httpx
import pytest
from fastmcp import FastMCP
from pydantic import ValidationError

from billy_mcp.api.tax_writes import (
    TaxRateCreatePreviewInput,
    TaxRateDeductionComponentCreatePreviewInput,
    TaxRateDeductionComponentDeletePreviewInput,
    TaxRateDeductionComponentUpdatePreviewInput,
    TaxRateDeletePreviewInput,
    TaxRateUpdatePreviewInput,
    register_tax_write_tools,
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
    """Controllable confirmation clock used only by local ticket-expiry tests."""

    def __init__(self) -> None:
        self.now = datetime(2026, 7, 29, tzinfo=UTC)

    def __call__(self) -> datetime:
        return self.now


def make_server(
    handler: MockHandler,
    *,
    token: str | None = "tax-write-test-token",
    confirmations: ConfirmationStore | None = None,
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
    server = FastMCP("tax-write-contract-test")
    register_tax_write_tools(
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
    structured_result = structured_content.get("result", structured_content)
    assert isinstance(structured_result, dict)
    return cast(dict[str, object], structured_result)


def test_registers_exactly_twelve_flat_typed_tax_write_tools() -> None:
    server, _ = make_server(lambda request: httpx.Response(200, json={}))

    by_name = {tool.name: tool for tool in asyncio.run(server.list_tools())}
    expected_properties = {
        "api_tax_rates_create_preview": {"taxRate"},
        "api_tax_rates_create_execute": {"confirmation_ticket"},
        "api_tax_rates_update_preview": {"id", "taxRate"},
        "api_tax_rates_update_execute": {"confirmation_ticket"},
        "api_tax_rates_delete_preview": {"id"},
        "api_tax_rates_delete_execute": {"confirmation_ticket"},
        "api_tax_rate_deduction_components_create_preview": {"taxRateDeductionComponent"},
        "api_tax_rate_deduction_components_create_execute": {"confirmation_ticket"},
        "api_tax_rate_deduction_components_update_preview": {
            "id",
            "taxRateDeductionComponent",
        },
        "api_tax_rate_deduction_components_update_execute": {"confirmation_ticket"},
        "api_tax_rate_deduction_components_delete_preview": {"id"},
        "api_tax_rate_deduction_components_delete_execute": {"confirmation_ticket"},
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
        (TaxRateCreatePreviewInput, {"taxRate": {}, "extra": True}),
        (TaxRateUpdatePreviewInput, {"id": "rate-1", "taxRate": {}, "extra": True}),
        (TaxRateDeletePreviewInput, {"id": "rate-1", "extra": True}),
        (
            TaxRateDeductionComponentCreatePreviewInput,
            {"taxRateDeductionComponent": {}, "extra": True},
        ),
        (
            TaxRateDeductionComponentUpdatePreviewInput,
            {"id": "component-1", "taxRateDeductionComponent": {}, "extra": True},
        ),
        (TaxRateDeductionComponentDeletePreviewInput, {"id": "component-1", "extra": True}),
        (TaxRateUpdatePreviewInput, {"id": "", "taxRate": {}}),
        (TaxRateDeletePreviewInput, {"id": ""}),
        (TaxRateDeductionComponentUpdatePreviewInput, {"id": "", "taxRateDeductionComponent": {}}),
        (TaxRateDeductionComponentDeletePreviewInput, {"id": ""}),
        (TaxRateUpdatePreviewInput, {"id": "rate-1", "taxRate": {"id": "other"}}),
        (
            TaxRateDeductionComponentUpdatePreviewInput,
            {"id": "component-1", "taxRateDeductionComponent": {"id": "other"}},
        ),
        (WriteExecuteInput, {"confirmation_ticket": "ticket", "taxRate": {}}),
    ],
)
def test_outer_inputs_forbid_extras_empty_ids_and_mismatched_body_ids(
    input_model: type[TaxRateCreatePreviewInput]
    | type[TaxRateUpdatePreviewInput]
    | type[TaxRateDeletePreviewInput]
    | type[TaxRateDeductionComponentCreatePreviewInput]
    | type[TaxRateDeductionComponentUpdatePreviewInput]
    | type[TaxRateDeductionComponentDeletePreviewInput]
    | type[WriteExecuteInput],
    payload: dict[str, object],
) -> None:
    with pytest.raises(ValidationError):
        input_model.model_validate(payload)


def test_opaque_inner_tax_payloads_preserve_unknown_fields_and_matching_ids() -> None:
    tax_rate = TaxRateUpdatePreviewInput.model_validate(
        {"id": "rate-1", "taxRate": {"id": "rate-1", "futureField": {"rank": 2}}}
    )
    component = TaxRateDeductionComponentUpdatePreviewInput.model_validate(
        {
            "id": "component-1",
            "taxRateDeductionComponent": {
                "id": "component-1",
                "futureField": {"rank": 2},
            },
        }
    )

    assert tax_rate.tax_rate["futureField"] == {"rank": 2}
    assert component.tax_rate_deduction_component["futureField"] == {"rank": 2}


@pytest.mark.parametrize(
    ("tool_name", "arguments", "expected_request", "expected_effect_state"),
    [
        (
            "api_tax_rates_create_preview",
            {"taxRate": {"unrecognisedRateField": {"rank": 2}}},
            {"taxRate": {"unrecognisedRateField": {"rank": 2}}},
            {"action": "create", "resource": "taxRate"},
        ),
        (
            "api_tax_rates_update_preview",
            {"id": "rate-1", "taxRate": {"isActive": False}},
            {"taxRate": {"isActive": False}},
            {"action": "update", "resource": "taxRate", "id": "rate-1"},
        ),
        (
            "api_tax_rates_delete_preview",
            {"id": "rate-1"},
            {"id": "rate-1"},
            {"action": "delete", "resource": "taxRate", "id": "rate-1"},
        ),
        (
            "api_tax_rate_deduction_components_create_preview",
            {"taxRateDeductionComponent": {"unrecognisedComponentField": {"rank": 2}}},
            {"taxRateDeductionComponent": {"unrecognisedComponentField": {"rank": 2}}},
            {"action": "create", "resource": "taxRateDeductionComponent"},
        ),
        (
            "api_tax_rate_deduction_components_update_preview",
            {"id": "component-1", "taxRateDeductionComponent": {"priority": 2}},
            {"taxRateDeductionComponent": {"priority": 2}},
            {
                "action": "update",
                "resource": "taxRateDeductionComponent",
                "id": "component-1",
            },
        ),
        (
            "api_tax_rate_deduction_components_delete_preview",
            {"id": "component-1"},
            {"id": "component-1"},
            {
                "action": "delete",
                "resource": "taxRateDeductionComponent",
                "id": "component-1",
            },
        ),
    ],
)
def test_previews_are_mutation_free_and_bind_exact_tax_requests(
    tool_name: str,
    arguments: dict[str, object],
    expected_request: dict[str, object],
    expected_effect_state: dict[str, object],
) -> None:
    server, requests = make_server(
        lambda request: pytest.fail(f"preview made an HTTP request: {request.method} {request.url}")
    )

    preview = call_tool(server, tool_name, arguments)

    assert requests == []
    assert preview["canonical_request"] == expected_request
    assert preview["expected_effect_state"] == expected_effect_state
    assert isinstance(preview["confirmation_ticket"], str)


@pytest.mark.parametrize(
    (
        "preview_name",
        "execute_name",
        "arguments",
        "response",
        "method",
        "path",
        "body",
        "expected_changed_records",
        "expected_deleted_records",
    ),
    [
        (
            "api_tax_rates_create_preview",
            "api_tax_rates_create_execute",
            {"taxRate": {"name": "Standard", "rate": 25}},
            {
                "taxRates": [{"id": "rate-1", "name": "Standard"}],
                "taxRateDeductionComponents": [{"id": "component-1", "priority": 1}],
            },
            "POST",
            "/v2/taxRates",
            {"taxRate": {"name": "Standard", "rate": 25}},
            {
                "taxRates": [{"id": "rate-1", "name": "Standard"}],
                "taxRateDeductionComponents": [{"id": "component-1", "priority": 1}],
            },
            None,
        ),
        (
            "api_tax_rates_update_preview",
            "api_tax_rates_update_execute",
            {"id": "rate /?", "taxRate": {"isActive": False}},
            {"taxRates": [{"id": "rate /?", "isActive": False}]},
            "PUT",
            "/v2/taxRates/rate%20%2F%3F",
            {"taxRate": {"isActive": False}},
            {"taxRates": [{"id": "rate /?", "isActive": False}]},
            None,
        ),
        (
            "api_tax_rates_delete_preview",
            "api_tax_rates_delete_execute",
            {"id": "rate /?"},
            {"meta": {"deletedRecords": {"taxRates": ["rate /?"]}}},
            "DELETE",
            "/v2/taxRates/rate%20%2F%3F",
            None,
            {},
            {"taxRates": ["rate /?"]},
        ),
        (
            "api_tax_rate_deduction_components_create_preview",
            "api_tax_rate_deduction_components_create_execute",
            {"taxRateDeductionComponent": {"taxRateId": "rate-1", "share": 50}},
            {"taxRateDeductionComponents": [{"id": "component-1", "share": 50}]},
            "POST",
            "/v2/taxRateDeductionComponents",
            {"taxRateDeductionComponent": {"taxRateId": "rate-1", "share": 50}},
            {"taxRateDeductionComponents": [{"id": "component-1", "share": 50}]},
            None,
        ),
        (
            "api_tax_rate_deduction_components_update_preview",
            "api_tax_rate_deduction_components_update_execute",
            {"id": "component /?", "taxRateDeductionComponent": {"priority": 2}},
            {"taxRateDeductionComponents": [{"id": "component /?", "priority": 2}]},
            "PUT",
            "/v2/taxRateDeductionComponents/component%20%2F%3F",
            {"taxRateDeductionComponent": {"priority": 2}},
            {"taxRateDeductionComponents": [{"id": "component /?", "priority": 2}]},
            None,
        ),
        (
            "api_tax_rate_deduction_components_delete_preview",
            "api_tax_rate_deduction_components_delete_execute",
            {"id": "component /?"},
            {"meta": {"deletedRecords": {"taxRateDeductionComponents": ["component /?"]}}},
            "DELETE",
            "/v2/taxRateDeductionComponents/component%20%2F%3F",
            None,
            {},
            {"taxRateDeductionComponents": ["component /?"]},
        ),
    ],
)
def test_execute_sends_exact_singular_tax_cud_shapes_once(
    preview_name: str,
    execute_name: str,
    arguments: dict[str, object],
    response: dict[str, object],
    method: str,
    path: str,
    body: dict[str, object] | None,
    expected_changed_records: dict[str, object],
    expected_deleted_records: dict[str, list[str]] | None,
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
    assert request.url.raw_path.decode() == path
    assert execution["changed_records"] == expected_changed_records
    assert execution["deleted_records"] == expected_deleted_records
    if body is None:
        assert request.content == b""
    else:
        assert json.loads(request.content) == body


def test_parent_response_maps_optional_components_only_when_present() -> None:
    server, _ = make_server(
        lambda request: httpx.Response(200, json={"taxRates": [{"id": "rate-1"}]})
    )

    preview = call_tool(
        server,
        "api_tax_rates_create_preview",
        {"taxRate": {"name": "Standard", "rate": 25}},
    )
    execution = call_tool(
        server,
        "api_tax_rates_create_execute",
        {"confirmation_ticket": preview["confirmation_ticket"]},
    )

    changed_records = execution["changed_records"]
    assert changed_records == {"taxRates": [{"id": "rate-1"}]}
    assert isinstance(changed_records, dict)
    assert "taxRateDeductionComponents" not in changed_records


def test_child_response_does_not_fabricate_parent_tax_rates() -> None:
    server, _ = make_server(
        lambda request: httpx.Response(
            200,
            json={"taxRateDeductionComponents": [{"id": "component-1"}]},
        )
    )

    preview = call_tool(
        server,
        "api_tax_rate_deduction_components_create_preview",
        {"taxRateDeductionComponent": {"taxRateId": "rate-1", "share": 50}},
    )
    execution = call_tool(
        server,
        "api_tax_rate_deduction_components_create_execute",
        {"confirmation_ticket": preview["confirmation_ticket"]},
    )

    changed_records = execution["changed_records"]
    assert changed_records == {"taxRateDeductionComponents": [{"id": "component-1"}]}
    assert isinstance(changed_records, dict)
    assert "taxRates" not in changed_records


def test_tampered_expired_and_replayed_tickets_fail_without_extra_writes() -> None:
    clock = Clock()
    server, requests = make_server(
        lambda request: httpx.Response(200, json={"taxRates": [{"id": "rate-1"}]}),
        confirmations=ConfirmationStore(clock),
    )

    preview = call_tool(
        server,
        "api_tax_rates_create_preview",
        {"taxRate": {"name": "Standard", "rate": 25}},
    )
    ticket = preview["confirmation_ticket"]
    assert isinstance(ticket, str)
    tampered = call_tool(
        server,
        "api_tax_rates_create_execute",
        {"confirmation_ticket": f"{ticket}x"},
    )
    assert tampered["code"] == StableErrorCode.CONFIRMATION_INVALID
    assert requests == []

    clock.now += timedelta(minutes=6)
    expired = call_tool(
        server,
        "api_tax_rates_create_execute",
        {"confirmation_ticket": ticket},
    )
    assert expired["code"] == StableErrorCode.CONFIRMATION_EXPIRED
    assert requests == []

    replay_preview = call_tool(
        server,
        "api_tax_rates_create_preview",
        {"taxRate": {"name": "Standard", "rate": 25}},
    )
    replay_ticket = replay_preview["confirmation_ticket"]
    assert isinstance(replay_ticket, str)
    first = call_tool(
        server,
        "api_tax_rates_create_execute",
        {"confirmation_ticket": replay_ticket},
    )
    replayed = call_tool(
        server,
        "api_tax_rates_create_execute",
        {"confirmation_ticket": replay_ticket},
    )

    assert first["changed_records"] == {"taxRates": [{"id": "rate-1"}]}
    assert replayed["code"] == StableErrorCode.CONFIRMATION_CONSUMED
    assert len(requests) == 1


def test_tax_ticket_rejects_a_different_executor_before_http() -> None:
    server, requests = make_server(
        lambda request: httpx.Response(200, json={"taxRates": [{"id": "rate-1"}]}),
    )

    preview = call_tool(
        server,
        "api_tax_rates_create_preview",
        {"taxRate": {"name": "Standard", "rate": 25}},
    )
    wrong_executor = call_tool(
        server,
        "api_tax_rate_deduction_components_create_execute",
        {"confirmation_ticket": preview["confirmation_ticket"]},
    )

    assert wrong_executor["code"] == StableErrorCode.CONFIRMATION_MISMATCH
    assert requests == []

    correct_executor = call_tool(
        server,
        "api_tax_rates_create_execute",
        {"confirmation_ticket": preview["confirmation_ticket"]},
    )
    assert correct_executor["changed_records"] == {"taxRates": [{"id": "rate-1"}]}
    assert len(requests) == 1


@pytest.mark.parametrize(
    "changes",
    [
        {"execute_tool_name": "api_tax_rates_other_execute"},
        {"organization_id": "other-organisation"},
        {"resource_id": "other-rate"},
        {"payload": {"isActive": False}},
        {"expected_effect_state": {"action": "other"}},
    ],
)
def test_tax_ticket_binding_rejects_mutated_executor_org_target_and_payload(
    changes: dict[str, object],
) -> None:
    specification = WriteOperationSpec(
        execute_tool_name="api_tax_rates_update_execute",
        method=WriteMethod.PUT,
        collection_path="/taxRates",
        singular_root="taxRate",
        plural_root="taxRates",
        additional_plural_roots=("taxRateDeductionComponents",),
        payload={"isActive": True},
        resource_id="rate-1",
        organization_id=None,
        summary="Update one Billy tax rate.",
        expected_effect_state={"action": "update", "resource": "taxRate", "id": "rate-1"},
    )
    store = ConfirmationStore()
    ticket = store.issue(confirmation_binding_for(specification))
    mismatched = specification.model_copy(update=changes)

    with pytest.raises(ConfirmationFailure) as failure:
        store.consume(ticket.value, confirmation_binding_for(mismatched))

    assert failure.value.error.code is StableErrorCode.CONFIRMATION_MISMATCH


def test_empty_token_returns_typed_auth_error_without_network_activity() -> None:
    server, requests = make_server(
        lambda request: pytest.fail(f"missing token attempted HTTP request: {request.url}"),
        token="",
    )

    preview = call_tool(
        server,
        "api_tax_rate_deduction_components_create_preview",
        {"taxRateDeductionComponent": {"taxRateId": "rate-1", "share": 50}},
    )
    error = call_tool(
        server,
        "api_tax_rate_deduction_components_create_execute",
        {"confirmation_ticket": preview["confirmation_ticket"]},
    )

    assert error["code"] == StableErrorCode.AUTH_REQUIRED
    assert requests == []


@pytest.mark.parametrize(
    ("status", "response", "preview_name", "arguments", "execute_name", "expected_code"),
    [
        (
            401,
            {"errorCode": "AUTHENTICATION_REQUIRED"},
            "api_tax_rates_create_preview",
            {"taxRate": {"name": "Standard", "rate": 25}},
            "api_tax_rates_create_execute",
            StableErrorCode.AUTH_REQUIRED,
        ),
        (
            404,
            {"errorCode": "RECORD_NOT_FOUND"},
            "api_tax_rate_deduction_components_update_preview",
            {"id": "missing-component", "taxRateDeductionComponent": {"priority": 2}},
            "api_tax_rate_deduction_components_update_execute",
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
    error = call_tool(
        server,
        execute_name,
        {"confirmation_ticket": preview["confirmation_ticket"]},
    )

    assert error["code"] == expected_code
    assert len(requests) == 1


def test_write_failure_is_not_retried() -> None:
    server, requests = make_server(
        lambda request: httpx.Response(500, json={"errorCode": "INTERNAL_SERVER_ERROR"})
    )

    preview = call_tool(
        server,
        "api_tax_rate_deduction_components_create_preview",
        {"taxRateDeductionComponent": {"taxRateId": "rate-1", "share": 50}},
    )
    error = call_tool(
        server,
        "api_tax_rate_deduction_components_create_execute",
        {"confirmation_ticket": preview["confirmation_ticket"]},
    )

    assert error["code"] == StableErrorCode.BILLY_ERROR
    assert len(requests) == 1


def test_deletes_do_not_fabricate_absent_deleted_records() -> None:
    server, _ = make_server(lambda request: httpx.Response(200, json={"meta": {}}))

    preview = call_tool(server, "api_tax_rates_delete_preview", {"id": "rate-1"})
    execution = call_tool(
        server,
        "api_tax_rates_delete_execute",
        {"confirmation_ticket": preview["confirmation_ticket"]},
    )

    assert execution == {"changed_records": {}, "deleted_records": None}
