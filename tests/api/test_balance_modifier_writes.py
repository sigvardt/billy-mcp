"""Contract tests for ticketed singular balance-modifier writes."""

from __future__ import annotations

import asyncio
from collections.abc import Callable
from typing import cast

import httpx
import pytest
from fastmcp import FastMCP
from fastmcp.exceptions import ValidationError as FastMcpValidationError
from pydantic import ValidationError

from billy_mcp.api.balance_modifier_writes import (
    BalanceModifierCreatePreviewInput,
    BalanceModifierUpdatePreviewInput,
    register_balance_modifier_write_tools,
)
from billy_mcp.api.write_protocol import WriteExecuteInput, WriteProtocolService
from billy_mcp.client import BillyHttpClient
from billy_mcp.confirmations import ConfirmationStore

MockHandler = Callable[[httpx.Request], httpx.Response]

VALID_MODIFIER = {"modifier": "modifier-1", "subject": "subject-1"}


def make_server(
    handler: MockHandler,
    *,
    token: str | None = "balance-modifier-write-test-token",
    confirmations: ConfirmationStore | None = None,
) -> tuple[FastMCP, list[httpx.Request]]:
    """Create a fully local FastMCP server with a recording locked client."""

    requests: list[httpx.Request] = []

    def recording_handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return handler(request)

    client = BillyHttpClient(lambda: token, transport=httpx.MockTransport(recording_handler))
    server = FastMCP("balance-modifier-write-contract-test")
    register_balance_modifier_write_tools(
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


def test_registers_exactly_four_flat_typed_balance_modifier_write_tools() -> None:
    server, _ = make_server(lambda request: httpx.Response(200, json={}))
    by_name = {tool.name: tool for tool in asyncio.run(server.list_tools())}
    expected_properties = {
        "api_balance_modifiers_create_preview": {"balanceModifier"},
        "api_balance_modifiers_create_execute": {"confirmation_ticket"},
        "api_balance_modifiers_update_preview": {"id", "balanceModifier"},
        "api_balance_modifiers_update_execute": {"confirmation_ticket"},
    }
    assert set(by_name) == set(expected_properties)
    for name, fields in expected_properties.items():
        schema = by_name[name].parameters
        properties = cast(dict[str, object], schema["properties"])
        assert schema["additionalProperties"] is False
        assert set(properties) == fields
        assert "input" not in properties
    documented = {"modifier", "subject"}
    for tool_name in (
        "api_balance_modifiers_create_preview",
        "api_balance_modifiers_update_preview",
    ):
        schema = by_name[tool_name].parameters
        nested_schema = cast(dict[str, object], schema["properties"]["balanceModifier"])
        if "$ref" in nested_schema:
            ref = str(nested_schema["$ref"]).rsplit("/", maxsplit=1)[-1]
            defs = schema.get("$defs") or schema.get("defs")
            assert isinstance(defs, dict)
            nested_schema = cast(dict[str, object], defs[ref])
        nested = cast(dict[str, object], nested_schema["properties"])
        required = nested_schema.get("required")
        assert set(nested) == documented
        assert nested_schema.get("additionalProperties") is False
        assert isinstance(required, list)
        assert set(cast(list[str], required)) == documented
        for field_name in documented:
            field_schema = cast(dict[str, object], nested[field_name])
            assert field_schema.get("type") == "string"


@pytest.mark.parametrize(
    ("input_model", "payload"),
    [
        (BalanceModifierCreatePreviewInput, {"balanceModifier": VALID_MODIFIER, "extra": True}),
        (
            BalanceModifierUpdatePreviewInput,
            {"id": "bm-1", "balanceModifier": VALID_MODIFIER, "extra": True},
        ),
        (BalanceModifierUpdatePreviewInput, {"id": "", "balanceModifier": VALID_MODIFIER}),
        (WriteExecuteInput, {"confirmation_ticket": "ticket", "balanceModifier": {}}),
        (BalanceModifierCreatePreviewInput, {"balanceModifier": {}}),
        (BalanceModifierCreatePreviewInput, {"balanceModifier": {"modifier": "modifier-1"}}),
        (BalanceModifierCreatePreviewInput, {"balanceModifier": {"subject": "subject-1"}}),
        (
            BalanceModifierCreatePreviewInput,
            {"balanceModifier": {"modifier": "", "subject": "subject-1"}},
        ),
        (
            BalanceModifierCreatePreviewInput,
            {"balanceModifier": {**VALID_MODIFIER, "amount": 1.0}},
        ),
        (
            BalanceModifierCreatePreviewInput,
            {"balanceModifier": {**VALID_MODIFIER, "modifierId": "m1"}},
        ),
        (
            BalanceModifierUpdatePreviewInput,
            {"id": "bm-1", "balanceModifier": {**VALID_MODIFIER, "subjectId": "s1"}},
        ),
        (
            BalanceModifierUpdatePreviewInput,
            {"id": "bm-1", "balanceModifier": {**VALID_MODIFIER, "isVoided": True}},
        ),
    ],
)
def test_outer_inputs_forbid_extras_empty_ids_and_readonly_nested_keys(
    input_model: type[BalanceModifierCreatePreviewInput]
    | type[BalanceModifierUpdatePreviewInput]
    | type[WriteExecuteInput],
    payload: dict[str, object],
) -> None:
    with pytest.raises(ValidationError):
        input_model.model_validate(payload)


@pytest.mark.parametrize(
    ("tool_name", "arguments"),
    [
        (
            "api_balance_modifiers_create_preview",
            {"balanceModifier": {**VALID_MODIFIER, "entryDate": "2026-08-20"}},
        ),
        (
            "api_balance_modifiers_create_preview",
            {"balanceModifier": {**VALID_MODIFIER, "realizedCurrencyDifference": 0.0}},
        ),
        (
            "api_balance_modifiers_create_preview",
            {"balanceModifier": {**VALID_MODIFIER, "modifier": ["modifier-1"]}},
        ),
        (
            "api_balance_modifiers_update_preview",
            {"id": "bm-1", "balanceModifier": {**VALID_MODIFIER, "subject": {"id": "s1"}}},
        ),
        ("api_balance_modifiers_create_preview", {"balanceModifier": {"modifier": "modifier-1"}}),
        ("api_balance_modifiers_update_preview", {"id": "bm-1", "balanceModifier": {}}),
    ],
)
def test_preview_tools_reject_readonly_missing_and_aliased_nested_keys(
    tool_name: str,
    arguments: dict[str, object],
) -> None:
    server, requests = make_server(
        lambda request: pytest.fail(f"preview made an HTTP request: {request.method} {request.url}")
    )
    with pytest.raises(FastMcpValidationError):
        asyncio.run(server.call_tool(tool_name, arguments))
    assert requests == []


@pytest.mark.parametrize(
    ("tool_name", "arguments", "expected_request"),
    [
        (
            "api_balance_modifiers_create_preview",
            {"balanceModifier": VALID_MODIFIER},
            {"balanceModifier": VALID_MODIFIER},
        ),
        (
            "api_balance_modifiers_update_preview",
            {"id": "bm-1", "balanceModifier": VALID_MODIFIER},
            {"balanceModifier": VALID_MODIFIER},
        ),
    ],
)
def test_previews_are_mutation_free_and_bind_the_exact_canonical_request(
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
    assert preview["expected_effect_state"] == {
        "action": tool_name.removeprefix("api_balance_modifiers_").removesuffix("_preview"),
        "resource": "balanceModifier",
        **({"id": arguments["id"]} if "id" in arguments else {}),
    }
    assert isinstance(preview["confirmation_ticket"], str)
