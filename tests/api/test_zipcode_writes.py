"""Contract tests for ticketed singular Billy zipcode write tools."""

from __future__ import annotations

import asyncio
import json
from collections.abc import Callable
from typing import cast

import httpx
import pytest
from fastmcp import FastMCP
from fastmcp.exceptions import ValidationError as FastMcpValidationError
from pydantic import ValidationError

from billy_mcp.api.write_protocol import WriteExecuteInput, WriteProtocolService
from billy_mcp.api.zipcode_writes import (
    ZipcodeCreatePreviewInput,
    ZipcodePayload,
    ZipcodeUpdatePreviewInput,
    register_zipcode_write_tools,
)
from billy_mcp.client import BillyHttpClient
from billy_mcp.confirmations import ConfirmationStore

MockHandler = Callable[[httpx.Request], httpx.Response]

DOCUMENTED_FIELDS = {"zipcode", "city", "state", "country", "latitude", "longitude"}
STRING_FIELDS = {"zipcode", "city", "state", "country"}
NUMBER_FIELDS = {"latitude", "longitude"}
PARTIAL_ZIPCODE = {"zipcode": "2100"}
FULL_ZIPCODE = {
    "zipcode": "2100",
    "city": "city-1",
    "state": "state-1",
    "country": "DK",
    "latitude": 55.68,
    "longitude": 12.57,
}


def make_server(
    handler: MockHandler,
    *,
    token: str | None = "zipcode-write-test-token",
    confirmations: ConfirmationStore | None = None,
) -> tuple[FastMCP, list[httpx.Request]]:
    """Create a fully local FastMCP server with a recording locked client."""

    requests: list[httpx.Request] = []

    def recording_handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return handler(request)

    client = BillyHttpClient(lambda: token, transport=httpx.MockTransport(recording_handler))
    server = FastMCP("zipcode-write-contract-test")
    register_zipcode_write_tools(
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


def _schema_mentions_json_type(schema: object, json_type: str) -> bool:
    encoded = json.dumps(schema)
    return f'"type": "{json_type}"' in encoded or f'"type":"{json_type}"' in encoded


def test_registers_exactly_four_flat_typed_zipcode_write_tools() -> None:
    server, _ = make_server(lambda request: httpx.Response(200, json={}))

    by_name = {tool.name: tool for tool in asyncio.run(server.list_tools())}
    expected_properties = {
        "api_zipcodes_create_preview": {"zipcode"},
        "api_zipcodes_create_execute": {"confirmation_ticket"},
        "api_zipcodes_update_preview": {"id", "zipcode"},
        "api_zipcodes_update_execute": {"confirmation_ticket"},
    }
    assert set(by_name) == set(expected_properties)
    for name, fields in expected_properties.items():
        schema = by_name[name].parameters
        properties = cast(dict[str, object], schema["properties"])
        assert schema["additionalProperties"] is False
        assert set(properties) == fields
        assert "input" not in properties
    for tool_name in (
        "api_zipcodes_create_preview",
        "api_zipcodes_update_preview",
    ):
        nested_schema = cast(
            dict[str, object], by_name[tool_name].parameters["properties"]["zipcode"]
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
        for field_name in STRING_FIELDS:
            assert _schema_mentions_json_type(nested[field_name], "string")
        for field_name in NUMBER_FIELDS:
            assert _schema_mentions_json_type(nested[field_name], "number")


def test_zipcode_payload_fields_match_documented_optional_types() -> None:
    for field_name in STRING_FIELDS:
        field = ZipcodePayload.model_fields[field_name]
        assert field.annotation == str | None
        assert field.is_required() is False
    for field_name in NUMBER_FIELDS:
        field = ZipcodePayload.model_fields[field_name]
        assert field.annotation == float | None
        assert field.is_required() is False
    assert "id" not in ZipcodePayload.model_fields


@pytest.mark.parametrize(
    ("input_model", "payload"),
    [
        (ZipcodeCreatePreviewInput, {"zipcode": {}, "extra": True}),
        (ZipcodeUpdatePreviewInput, {"id": "zip-1", "zipcode": {}, "extra": True}),
        (ZipcodeUpdatePreviewInput, {"id": "", "zipcode": {}}),
        (WriteExecuteInput, {"confirmation_ticket": "ticket", "zipcode": {}}),
        (ZipcodeCreatePreviewInput, {"zipcode": {"zipcodeId": "zip-1"}}),
        (ZipcodeCreatePreviewInput, {"zipcode": {"cityId": "city-1"}}),
        (ZipcodeCreatePreviewInput, {"zipcode": {"stateId": "state-1"}}),
        (ZipcodeCreatePreviewInput, {"zipcode": {"countryId": "DK"}}),
        (ZipcodeCreatePreviewInput, {"zipcode": {"zipcode": ["2100"]}}),
        (ZipcodeCreatePreviewInput, {"zipcode": {"city": {"id": "city-1"}}}),
        (ZipcodeCreatePreviewInput, {"zipcode": {"longitude": [12.57]}}),
        (
            ZipcodeUpdatePreviewInput,
            {"id": "zip-1", "zipcode": {"zipcode": "2100", "undocumented": True}},
        ),
    ],
)
def test_outer_inputs_forbid_extra_fields_aliases_and_empty_ids(
    input_model: type[ZipcodeCreatePreviewInput]
    | type[ZipcodeUpdatePreviewInput]
    | type[WriteExecuteInput],
    payload: dict[str, object],
) -> None:
    with pytest.raises(ValidationError):
        input_model.model_validate(payload)


@pytest.mark.parametrize(
    ("tool_name", "arguments"),
    [
        ("api_zipcodes_create_preview", {"zipcode": {"zipcode": "X", "zipcodeId": "zip-1"}}),
        ("api_zipcodes_create_preview", {"zipcode": {"countryId": "DK"}}),
        (
            "api_zipcodes_update_preview",
            {"id": "zip-1", "zipcode": {"zipcode": "X", "undocumented": True}},
        ),
        ("api_zipcodes_create_preview", {"zipcode": {"city": {"id": "city-1"}}}),
        ("api_zipcodes_create_preview", {"zipcode": {"zipcode": ["2100"]}}),
        ("api_zipcodes_create_preview", {"zipcode": {"latitude": {"value": 55.68}}}),
    ],
)
def test_preview_tools_reject_aliased_nested_and_object_zipcode_keys(
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
            "api_zipcodes_create_preview",
            {"zipcode": FULL_ZIPCODE},
            {"zipcode": FULL_ZIPCODE},
        ),
        (
            "api_zipcodes_update_preview",
            {"id": "zip-1", "zipcode": PARTIAL_ZIPCODE},
            {"zipcode": PARTIAL_ZIPCODE},
        ),
        (
            "api_zipcodes_create_preview",
            {"zipcode": {"latitude": 55.68, "longitude": 12.57}},
            {"zipcode": {"latitude": 55.68, "longitude": 12.57}},
        ),
        ("api_zipcodes_create_preview", {"zipcode": {}}, {"zipcode": {}}),
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
        "action": tool_name.removeprefix("api_zipcodes_").removesuffix("_preview"),
        "resource": "zipcode",
        **({"id": arguments["id"]} if "id" in arguments else {}),
    }
    assert isinstance(preview["confirmation_ticket"], str)
