"""Contract tests for ticketed singular Billy state write tools."""

from __future__ import annotations

import asyncio
from collections.abc import Callable
from typing import cast

import httpx
import pytest
from fastmcp import FastMCP
from fastmcp.exceptions import ValidationError as FastMcpValidationError
from pydantic import ValidationError

from billy_mcp.api.state_writes import (
    StateCreatePreviewInput,
    StatePayload,
    StateUpdatePreviewInput,
    register_state_write_tools,
)
from billy_mcp.api.write_protocol import WriteExecuteInput, WriteProtocolService
from billy_mcp.client import BillyHttpClient
from billy_mcp.confirmations import ConfirmationStore

MockHandler = Callable[[httpx.Request], httpx.Response]

DOCUMENTED_FIELDS = {"stateCode", "name", "country"}
PARTIAL_STATE = {"name": "California"}


def make_server(
    handler: MockHandler,
    *,
    token: str | None = "state-write-test-token",
    confirmations: ConfirmationStore | None = None,
) -> tuple[FastMCP, list[httpx.Request]]:
    """Create a fully local FastMCP server with a recording locked client."""

    requests: list[httpx.Request] = []

    def recording_handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return handler(request)

    client = BillyHttpClient(lambda: token, transport=httpx.MockTransport(recording_handler))
    server = FastMCP("state-write-contract-test")
    register_state_write_tools(
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


def test_registers_exactly_four_flat_typed_state_write_tools() -> None:
    server, _ = make_server(lambda request: httpx.Response(200, json={}))

    by_name = {tool.name: tool for tool in asyncio.run(server.list_tools())}
    expected_properties = {
        "api_states_create_preview": {"state"},
        "api_states_create_execute": {"confirmation_ticket"},
        "api_states_update_preview": {"id", "state"},
        "api_states_update_execute": {"confirmation_ticket"},
    }
    assert set(by_name) == set(expected_properties)
    for name, fields in expected_properties.items():
        schema = by_name[name].parameters
        properties = cast(dict[str, object], schema["properties"])
        assert schema["additionalProperties"] is False
        assert set(properties) == fields
        assert "input" not in properties
    for tool_name in ("api_states_create_preview", "api_states_update_preview"):
        nested_schema = cast(
            dict[str, object], by_name[tool_name].parameters["properties"]["state"]
        )
        if "$ref" in nested_schema:
            ref = str(nested_schema["$ref"]).rsplit("/", maxsplit=1)[-1]
            defs = by_name[tool_name].parameters.get("$defs") or by_name[tool_name].parameters.get(
                "defs"
            )
            assert isinstance(defs, dict)
            nested_schema = cast(dict[str, object], defs[ref])
        nested = cast(dict[str, object], nested_schema["properties"])
        assert set(nested) == DOCUMENTED_FIELDS
        assert nested_schema.get("additionalProperties") is False
        assert not nested_schema.get("required")


def test_state_payload_fields_are_optional_strings() -> None:
    for field_name in DOCUMENTED_FIELDS:
        field = StatePayload.model_fields[field_name]
        assert field.annotation == str | None
        assert field.is_required() is False


@pytest.mark.parametrize(
    ("input_model", "payload"),
    [
        (StateCreatePreviewInput, {"state": {}, "extra": True}),
        (StateUpdatePreviewInput, {"id": "state-1", "state": {}, "extra": True}),
        (StateUpdatePreviewInput, {"id": "", "state": {}}),
        (WriteExecuteInput, {"confirmation_ticket": "ticket", "state": {}}),
        (StateCreatePreviewInput, {"state": {"stateId": "state-1"}}),
        (StateCreatePreviewInput, {"state": {"countryId": "US"}}),
        (StateCreatePreviewInput, {"state": {"name": ["X"]}}),
        (StateCreatePreviewInput, {"state": {"country": {"id": "US"}}}),
        (StateUpdatePreviewInput, {"id": "state-1", "state": {"name": "X", "undocumented": True}}),
    ],
)
def test_outer_inputs_forbid_extra_fields_aliases_and_empty_ids(
    input_model: type[StateCreatePreviewInput]
    | type[StateUpdatePreviewInput]
    | type[WriteExecuteInput],
    payload: dict[str, object],
) -> None:
    with pytest.raises(ValidationError):
        input_model.model_validate(payload)


@pytest.mark.parametrize(
    ("tool_name", "arguments"),
    [
        ("api_states_create_preview", {"state": {"name": "X", "stateId": "state-1"}}),
        ("api_states_create_preview", {"state": {"countryId": "US"}}),
        (
            "api_states_update_preview",
            {"id": "state-1", "state": {"name": "X", "undocumented": True}},
        ),
        ("api_states_create_preview", {"state": {"country": {"id": "US"}}}),
        ("api_states_create_preview", {"state": {"name": ["X"]}}),
    ],
)
def test_preview_tools_reject_aliased_nested_and_object_state_keys(
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
            "api_states_create_preview",
            {"state": {"stateCode": "CA", "name": "California", "country": "US"}},
            {"state": {"stateCode": "CA", "name": "California", "country": "US"}},
        ),
        (
            "api_states_update_preview",
            {"id": "state-1", "state": PARTIAL_STATE},
            {"state": PARTIAL_STATE},
        ),
        ("api_states_create_preview", {"state": {}}, {"state": {}}),
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
        "action": tool_name.removeprefix("api_states_").removesuffix("_preview"),
        "resource": "state",
        **({"id": arguments["id"]} if "id" in arguments else {}),
    }
    assert isinstance(preview["confirmation_ticket"], str)
