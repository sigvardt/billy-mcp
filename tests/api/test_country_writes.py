"""Contract tests for ticketed singular Billy country write tools."""

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

from billy_mcp.api.country_writes import (
    CountryCreatePreviewInput,
    CountryUpdatePreviewInput,
    register_country_write_tools,
)
from billy_mcp.api.write_protocol import WriteExecuteInput, WriteProtocolService
from billy_mcp.client import BillyHttpClient
from billy_mcp.confirmations import ConfirmationStore

MockHandler = Callable[[httpx.Request], httpx.Response]

DOCUMENTED_FIELDS = {
    "name",
    "hasStates",
    "hasFiniteStates",
    "hasFiniteZipcodes",
    "icon",
    "locale",
}
BOOLEAN_FIELDS = {"hasStates", "hasFiniteStates", "hasFiniteZipcodes"}
STRING_FIELDS = {"name", "icon", "locale"}
PARTIAL_COUNTRY = {"name": "X"}
FULL_COUNTRY = {
    "name": "X",
    "hasStates": True,
    "hasFiniteStates": False,
    "hasFiniteZipcodes": True,
    "icon": "flag",
    "locale": "da_DK",
}


def make_server(
    handler: MockHandler,
    *,
    token: str | None = "country-write-test-token",
    confirmations: ConfirmationStore | None = None,
) -> tuple[FastMCP, list[httpx.Request]]:
    """Create a fully local FastMCP server with a recording locked client."""

    requests: list[httpx.Request] = []

    def recording_handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return handler(request)

    client = BillyHttpClient(lambda: token, transport=httpx.MockTransport(recording_handler))
    server = FastMCP("country-write-contract-test")
    register_country_write_tools(
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


def test_registers_exactly_four_flat_typed_country_write_tools() -> None:
    server, _ = make_server(lambda request: httpx.Response(200, json={}))

    by_name = {tool.name: tool for tool in asyncio.run(server.list_tools())}
    expected_properties = {
        "api_countries_create_preview": {"country"},
        "api_countries_create_execute": {"confirmation_ticket"},
        "api_countries_update_preview": {"id", "country"},
        "api_countries_update_execute": {"confirmation_ticket"},
    }
    assert set(by_name) == set(expected_properties)
    for name, fields in expected_properties.items():
        schema = by_name[name].parameters
        properties = cast(dict[str, object], schema["properties"])
        assert schema["additionalProperties"] is False
        assert set(properties) == fields
        assert "input" not in properties
    for tool_name in (
        "api_countries_create_preview",
        "api_countries_update_preview",
    ):
        nested_schema = cast(
            dict[str, object], by_name[tool_name].parameters["properties"]["country"]
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
        for field_name in BOOLEAN_FIELDS:
            assert _schema_mentions_json_type(nested[field_name], "boolean")
        for field_name in STRING_FIELDS:
            assert _schema_mentions_json_type(nested[field_name], "string")


@pytest.mark.parametrize(
    ("input_model", "payload"),
    [
        (CountryCreatePreviewInput, {"country": {}, "extra": True}),
        (CountryUpdatePreviewInput, {"id": "dk", "country": {}, "extra": True}),
        (CountryUpdatePreviewInput, {"id": "", "country": {}}),
        (WriteExecuteInput, {"confirmation_ticket": "ticket", "country": {}}),
        (CountryCreatePreviewInput, {"country": {"localeId": "da_DK"}}),
        (CountryCreatePreviewInput, {"country": {"locale": ["da_DK"]}}),
        (CountryCreatePreviewInput, {"country": {"hasStates": ["yes"]}}),
        (CountryCreatePreviewInput, {"country": {"name": {"id": "X"}}}),
        (CountryUpdatePreviewInput, {"id": "dk", "country": {"name": "X", "undocumented": True}}),
    ],
)
def test_outer_inputs_forbid_extra_fields_aliases_arrays_and_empty_ids(
    input_model: type[CountryCreatePreviewInput]
    | type[CountryUpdatePreviewInput]
    | type[WriteExecuteInput],
    payload: dict[str, object],
) -> None:
    with pytest.raises(ValidationError):
        input_model.model_validate(payload)


@pytest.mark.parametrize(
    ("tool_name", "arguments"),
    [
        ("api_countries_create_preview", {"country": {"name": "X", "localeId": "da_DK"}}),
        ("api_countries_create_preview", {"country": {"locale": ["da_DK"]}}),
        ("api_countries_create_preview", {"country": {"hasStates": {"value": True}}}),
        (
            "api_countries_update_preview",
            {"id": "dk", "country": {"name": "X", "undocumented": True}},
        ),
        ("api_countries_create_preview", {"country": {"name": {"id": "X"}}}),
    ],
)
def test_preview_tools_reject_aliased_array_nested_and_object_keys(
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
            "api_countries_create_preview",
            {"country": FULL_COUNTRY},
            {"country": FULL_COUNTRY},
        ),
        (
            "api_countries_update_preview",
            {"id": "dk", "country": PARTIAL_COUNTRY},
            {"country": PARTIAL_COUNTRY},
        ),
        ("api_countries_create_preview", {"country": {}}, {"country": {}}),
        (
            "api_countries_create_preview",
            {"country": {"hasStates": True}},
            {"country": {"hasStates": True}},
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
        "action": tool_name.removeprefix("api_countries_").removesuffix("_preview"),
        "resource": "country",
        **({"id": arguments["id"]} if "id" in arguments else {}),
    }
    assert isinstance(preview["confirmation_ticket"], str)
