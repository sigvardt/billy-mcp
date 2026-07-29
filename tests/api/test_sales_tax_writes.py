"""Contract tests for ticketed singular Billy sales-tax write tools."""

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

from billy_mcp.api.sales_tax_writes import (
    SalesTaxRuleCreatePreviewInput,
    SalesTaxRuleDeletePreviewInput,
    SalesTaxRulesetCreatePreviewInput,
    SalesTaxRulesetDeletePreviewInput,
    SalesTaxRulesetUpdatePreviewInput,
    SalesTaxRuleUpdatePreviewInput,
    register_sales_tax_write_tools,
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
    token: str | None = "sales-tax-write-test-token",
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
    server = FastMCP("sales-tax-write-contract-test")
    register_sales_tax_write_tools(
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


def test_registers_exactly_twelve_flat_typed_sales_tax_write_tools() -> None:
    server, _ = make_server(lambda request: httpx.Response(200, json={}))

    by_name = {tool.name: tool for tool in asyncio.run(server.list_tools())}
    expected_properties = {
        "api_sales_tax_rulesets_create_preview": {"salesTaxRuleset"},
        "api_sales_tax_rulesets_create_execute": {"confirmation_ticket"},
        "api_sales_tax_rulesets_update_preview": {"id", "salesTaxRuleset"},
        "api_sales_tax_rulesets_update_execute": {"confirmation_ticket"},
        "api_sales_tax_rulesets_delete_preview": {"id"},
        "api_sales_tax_rulesets_delete_execute": {"confirmation_ticket"},
        "api_sales_tax_rules_create_preview": {"salesTaxRule"},
        "api_sales_tax_rules_create_execute": {"confirmation_ticket"},
        "api_sales_tax_rules_update_preview": {"id", "salesTaxRule"},
        "api_sales_tax_rules_update_execute": {"confirmation_ticket"},
        "api_sales_tax_rules_delete_preview": {"id"},
        "api_sales_tax_rules_delete_execute": {"confirmation_ticket"},
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
        (SalesTaxRulesetCreatePreviewInput, {"salesTaxRuleset": {}, "extra": True}),
        (
            SalesTaxRulesetUpdatePreviewInput,
            {"id": "ruleset-1", "salesTaxRuleset": {}, "extra": True},
        ),
        (SalesTaxRulesetDeletePreviewInput, {"id": "ruleset-1", "extra": True}),
        (SalesTaxRuleCreatePreviewInput, {"salesTaxRule": {}, "extra": True}),
        (SalesTaxRuleUpdatePreviewInput, {"id": "rule-1", "salesTaxRule": {}, "extra": True}),
        (SalesTaxRuleDeletePreviewInput, {"id": "rule-1", "extra": True}),
        (SalesTaxRulesetUpdatePreviewInput, {"id": "", "salesTaxRuleset": {}}),
        (SalesTaxRulesetDeletePreviewInput, {"id": ""}),
        (SalesTaxRuleUpdatePreviewInput, {"id": "", "salesTaxRule": {}}),
        (SalesTaxRuleDeletePreviewInput, {"id": ""}),
        (
            SalesTaxRulesetUpdatePreviewInput,
            {"id": "ruleset-1", "salesTaxRuleset": {"id": "other"}},
        ),
        (SalesTaxRuleUpdatePreviewInput, {"id": "rule-1", "salesTaxRule": {"id": "other"}}),
        (WriteExecuteInput, {"confirmation_ticket": "ticket", "salesTaxRule": {}}),
    ],
)
def test_outer_inputs_forbid_extras_empty_ids_and_mismatched_body_ids(
    input_model: type[SalesTaxRulesetCreatePreviewInput]
    | type[SalesTaxRulesetUpdatePreviewInput]
    | type[SalesTaxRulesetDeletePreviewInput]
    | type[SalesTaxRuleCreatePreviewInput]
    | type[SalesTaxRuleUpdatePreviewInput]
    | type[SalesTaxRuleDeletePreviewInput]
    | type[WriteExecuteInput],
    payload: dict[str, object],
) -> None:
    with pytest.raises(ValidationError):
        input_model.model_validate(payload)


def test_opaque_inner_sales_tax_payloads_preserve_unknown_fields_and_matching_ids() -> None:
    ruleset = SalesTaxRulesetUpdatePreviewInput.model_validate(
        {"id": "ruleset-1", "salesTaxRuleset": {"id": "ruleset-1", "futureField": {"rank": 2}}}
    )
    rule = SalesTaxRuleUpdatePreviewInput.model_validate(
        {"id": "rule-1", "salesTaxRule": {"id": "rule-1", "futureField": {"rank": 2}}}
    )

    assert ruleset.sales_tax_ruleset["futureField"] == {"rank": 2}
    assert rule.sales_tax_rule["futureField"] == {"rank": 2}


@pytest.mark.parametrize(
    ("tool_name", "arguments", "expected_request", "expected_effect_state"),
    [
        (
            "api_sales_tax_rulesets_create_preview",
            {"salesTaxRuleset": {"unrecognisedRulesetField": {"rank": 2}}},
            {"salesTaxRuleset": {"unrecognisedRulesetField": {"rank": 2}}},
            {"action": "create", "resource": "salesTaxRuleset"},
        ),
        (
            "api_sales_tax_rulesets_update_preview",
            {"id": "ruleset-1", "salesTaxRuleset": {"futureField": False}},
            {"salesTaxRuleset": {"futureField": False}},
            {"action": "update", "resource": "salesTaxRuleset", "id": "ruleset-1"},
        ),
        (
            "api_sales_tax_rulesets_delete_preview",
            {"id": "ruleset-1"},
            {"id": "ruleset-1"},
            {"action": "delete", "resource": "salesTaxRuleset", "id": "ruleset-1"},
        ),
        (
            "api_sales_tax_rules_create_preview",
            {"salesTaxRule": {"unrecognisedRuleField": {"rank": 2}}},
            {"salesTaxRule": {"unrecognisedRuleField": {"rank": 2}}},
            {"action": "create", "resource": "salesTaxRule"},
        ),
        (
            "api_sales_tax_rules_update_preview",
            {"id": "rule-1", "salesTaxRule": {"futureField": 2}},
            {"salesTaxRule": {"futureField": 2}},
            {"action": "update", "resource": "salesTaxRule", "id": "rule-1"},
        ),
        (
            "api_sales_tax_rules_delete_preview",
            {"id": "rule-1"},
            {"id": "rule-1"},
            {"action": "delete", "resource": "salesTaxRule", "id": "rule-1"},
        ),
    ],
)
def test_previews_are_mutation_free_and_bind_exact_sales_tax_requests(
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
            "api_sales_tax_rulesets_create_preview",
            "api_sales_tax_rulesets_create_execute",
            {"salesTaxRuleset": {"name": "Danish VAT", "organizationId": "org-1"}},
            {
                "salesTaxRulesets": [{"id": "ruleset-1", "name": "Danish VAT"}],
                "salesTaxRules": [{"id": "rule-1", "priority": 1}],
            },
            "POST",
            "/v2/salesTaxRulesets",
            {"salesTaxRuleset": {"name": "Danish VAT", "organizationId": "org-1"}},
            {
                "salesTaxRulesets": [{"id": "ruleset-1", "name": "Danish VAT"}],
                "salesTaxRules": [{"id": "rule-1", "priority": 1}],
            },
            None,
        ),
        (
            "api_sales_tax_rulesets_update_preview",
            "api_sales_tax_rulesets_update_execute",
            {"id": "ruleset /?", "salesTaxRuleset": {"description": "Updated"}},
            {"salesTaxRulesets": [{"id": "ruleset /?", "description": "Updated"}]},
            "PUT",
            "/v2/salesTaxRulesets/ruleset%20%2F%3F",
            {"salesTaxRuleset": {"description": "Updated"}},
            {"salesTaxRulesets": [{"id": "ruleset /?", "description": "Updated"}]},
            None,
        ),
        (
            "api_sales_tax_rulesets_delete_preview",
            "api_sales_tax_rulesets_delete_execute",
            {"id": "ruleset /?"},
            {"meta": {"deletedRecords": {"salesTaxRulesets": ["ruleset /?"]}}},
            "DELETE",
            "/v2/salesTaxRulesets/ruleset%20%2F%3F",
            None,
            {},
            {"salesTaxRulesets": ["ruleset /?"]},
        ),
        (
            "api_sales_tax_rules_create_preview",
            "api_sales_tax_rules_create_execute",
            {"salesTaxRule": {"rulesetId": "ruleset-1", "countryId": "DK"}},
            {"salesTaxRules": [{"id": "rule-1", "countryId": "DK"}]},
            "POST",
            "/v2/salesTaxRules",
            {"salesTaxRule": {"rulesetId": "ruleset-1", "countryId": "DK"}},
            {"salesTaxRules": [{"id": "rule-1", "countryId": "DK"}]},
            None,
        ),
        (
            "api_sales_tax_rules_update_preview",
            "api_sales_tax_rules_update_execute",
            {"id": "rule /?", "salesTaxRule": {"priority": 2}},
            {"salesTaxRules": [{"id": "rule /?", "priority": 2}]},
            "PUT",
            "/v2/salesTaxRules/rule%20%2F%3F",
            {"salesTaxRule": {"priority": 2}},
            {"salesTaxRules": [{"id": "rule /?", "priority": 2}]},
            None,
        ),
        (
            "api_sales_tax_rules_delete_preview",
            "api_sales_tax_rules_delete_execute",
            {"id": "rule /?"},
            {"meta": {"deletedRecords": {"salesTaxRules": ["rule /?"]}}},
            "DELETE",
            "/v2/salesTaxRules/rule%20%2F%3F",
            None,
            {},
            {"salesTaxRules": ["rule /?"]},
        ),
    ],
)
def test_execute_sends_exact_singular_sales_tax_cud_shapes_once(
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


def test_ruleset_response_maps_optional_rules_only_when_present() -> None:
    server, _ = make_server(
        lambda request: httpx.Response(200, json={"salesTaxRulesets": [{"id": "ruleset-1"}]})
    )

    preview = call_tool(
        server,
        "api_sales_tax_rulesets_create_preview",
        {"salesTaxRuleset": {"name": "Danish VAT"}},
    )
    execution = call_tool(
        server,
        "api_sales_tax_rulesets_create_execute",
        {"confirmation_ticket": preview["confirmation_ticket"]},
    )

    changed_records = execution["changed_records"]
    assert changed_records == {"salesTaxRulesets": [{"id": "ruleset-1"}]}
    assert isinstance(changed_records, dict)
    assert "salesTaxRules" not in changed_records


def test_rule_response_does_not_fabricate_parent_rulesets() -> None:
    server, _ = make_server(
        lambda request: httpx.Response(200, json={"salesTaxRules": [{"id": "rule-1"}]})
    )

    preview = call_tool(
        server,
        "api_sales_tax_rules_create_preview",
        {"salesTaxRule": {"rulesetId": "ruleset-1", "countryId": "DK"}},
    )
    execution = call_tool(
        server,
        "api_sales_tax_rules_create_execute",
        {"confirmation_ticket": preview["confirmation_ticket"]},
    )

    changed_records = execution["changed_records"]
    assert changed_records == {"salesTaxRules": [{"id": "rule-1"}]}
    assert isinstance(changed_records, dict)
    assert "salesTaxRulesets" not in changed_records


def test_tampered_expired_and_replayed_tickets_fail_without_extra_writes() -> None:
    clock = Clock()
    server, requests = make_server(
        lambda request: httpx.Response(200, json={"salesTaxRulesets": [{"id": "ruleset-1"}]}),
        confirmations=ConfirmationStore(clock),
    )

    preview = call_tool(
        server,
        "api_sales_tax_rulesets_create_preview",
        {"salesTaxRuleset": {"name": "Danish VAT"}},
    )
    ticket = preview["confirmation_ticket"]
    assert isinstance(ticket, str)
    tampered = call_tool(
        server,
        "api_sales_tax_rulesets_create_execute",
        {"confirmation_ticket": f"{ticket}x"},
    )
    assert tampered["code"] == StableErrorCode.CONFIRMATION_INVALID
    assert requests == []

    clock.now += timedelta(minutes=6)
    expired = call_tool(
        server,
        "api_sales_tax_rulesets_create_execute",
        {"confirmation_ticket": ticket},
    )
    assert expired["code"] == StableErrorCode.CONFIRMATION_EXPIRED
    assert requests == []

    replay_preview = call_tool(
        server,
        "api_sales_tax_rulesets_create_preview",
        {"salesTaxRuleset": {"name": "Danish VAT"}},
    )
    replay_ticket = replay_preview["confirmation_ticket"]
    assert isinstance(replay_ticket, str)
    first = call_tool(
        server,
        "api_sales_tax_rulesets_create_execute",
        {"confirmation_ticket": replay_ticket},
    )
    replayed = call_tool(
        server,
        "api_sales_tax_rulesets_create_execute",
        {"confirmation_ticket": replay_ticket},
    )

    assert first["changed_records"] == {"salesTaxRulesets": [{"id": "ruleset-1"}]}
    assert replayed["code"] == StableErrorCode.CONFIRMATION_CONSUMED
    assert len(requests) == 1


def test_sales_tax_ticket_rejects_a_different_executor_before_http() -> None:
    server, requests = make_server(
        lambda request: httpx.Response(200, json={"salesTaxRulesets": [{"id": "ruleset-1"}]}),
    )

    preview = call_tool(
        server,
        "api_sales_tax_rulesets_create_preview",
        {"salesTaxRuleset": {"name": "Danish VAT"}},
    )
    cross_resource_executor = call_tool(
        server,
        "api_sales_tax_rules_create_execute",
        {"confirmation_ticket": preview["confirmation_ticket"]},
    )
    same_resource_executor = call_tool(
        server,
        "api_sales_tax_rulesets_delete_execute",
        {"confirmation_ticket": preview["confirmation_ticket"]},
    )

    assert cross_resource_executor["code"] == StableErrorCode.CONFIRMATION_MISMATCH
    assert same_resource_executor["code"] == StableErrorCode.CONFIRMATION_MISMATCH
    assert requests == []

    correct_executor = call_tool(
        server,
        "api_sales_tax_rulesets_create_execute",
        {"confirmation_ticket": preview["confirmation_ticket"]},
    )
    assert correct_executor["changed_records"] == {"salesTaxRulesets": [{"id": "ruleset-1"}]}
    assert len(requests) == 1


@pytest.mark.parametrize(
    "changes",
    [
        {"execute_tool_name": "api_sales_tax_rulesets_other_execute"},
        {"organization_id": "other-organisation"},
        {"resource_id": "other-ruleset"},
        {"payload": {"description": "Changed"}},
        {"expected_effect_state": {"action": "other"}},
    ],
)
def test_sales_tax_ticket_binding_rejects_mutated_executor_org_target_and_payload(
    changes: dict[str, object],
) -> None:
    specification = WriteOperationSpec(
        execute_tool_name="api_sales_tax_rulesets_update_execute",
        method=WriteMethod.PUT,
        collection_path="/salesTaxRulesets",
        singular_root="salesTaxRuleset",
        plural_root="salesTaxRulesets",
        additional_plural_roots=("salesTaxRules",),
        payload={"description": "Original"},
        resource_id="ruleset-1",
        organization_id=None,
        summary="Update one Billy sales-tax ruleset.",
        expected_effect_state={
            "action": "update",
            "resource": "salesTaxRuleset",
            "id": "ruleset-1",
        },
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
        "api_sales_tax_rules_create_preview",
        {"salesTaxRule": {"rulesetId": "ruleset-1", "countryId": "DK"}},
    )
    error = call_tool(
        server,
        "api_sales_tax_rules_create_execute",
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
            "api_sales_tax_rulesets_create_preview",
            {"salesTaxRuleset": {"name": "Danish VAT"}},
            "api_sales_tax_rulesets_create_execute",
            StableErrorCode.AUTH_REQUIRED,
        ),
        (
            404,
            {"errorCode": "RECORD_NOT_FOUND"},
            "api_sales_tax_rules_update_preview",
            {"id": "missing-rule", "salesTaxRule": {"priority": 2}},
            "api_sales_tax_rules_update_execute",
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
        "api_sales_tax_rules_create_preview",
        {"salesTaxRule": {"rulesetId": "ruleset-1", "countryId": "DK"}},
    )
    error = call_tool(
        server,
        "api_sales_tax_rules_create_execute",
        {"confirmation_ticket": preview["confirmation_ticket"]},
    )

    assert error["code"] == StableErrorCode.BILLY_ERROR
    assert len(requests) == 1


def test_deletes_do_not_fabricate_absent_deleted_records() -> None:
    server, _ = make_server(lambda request: httpx.Response(200, json={"meta": {}}))

    preview = call_tool(server, "api_sales_tax_rulesets_delete_preview", {"id": "ruleset-1"})
    execution = call_tool(
        server,
        "api_sales_tax_rulesets_delete_execute",
        {"confirmation_ticket": preview["confirmation_ticket"]},
    )

    assert execution == {"changed_records": {}, "deleted_records": None}
