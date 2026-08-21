"""Contract tests for ticketed singular Billy account-nature write tools."""

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

from billy_mcp.api.account_nature_writes import (
    AccountNatureCreatePreviewInput,
    AccountNatureUpdatePreviewInput,
    register_account_nature_write_tools,
)
from billy_mcp.api.write_protocol import WriteExecuteInput, WriteProtocolService
from billy_mcp.client import BillyHttpClient
from billy_mcp.confirmations import ConfirmationStore

MockHandler = Callable[[httpx.Request], httpx.Response]


def make_server(
    handler: MockHandler,
    *,
    token: str | None = "account-nature-write-test-token",
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
    server = FastMCP("account-nature-write-contract-test")
    register_account_nature_write_tools(
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


def test_registers_exactly_four_flat_typed_account_nature_write_tools() -> None:
    server, _ = make_server(lambda request: httpx.Response(200, json={}))

    by_name = {tool.name: tool for tool in asyncio.run(server.list_tools())}

    assert set(by_name) == {
        "api_account_natures_create_preview",
        "api_account_natures_create_execute",
        "api_account_natures_update_preview",
        "api_account_natures_update_execute",
    }
    expected_properties = {
        "api_account_natures_create_preview": {"accountNature"},
        "api_account_natures_create_execute": {"confirmation_ticket"},
        "api_account_natures_update_preview": {"accountNature", "id"},
        "api_account_natures_update_execute": {"confirmation_ticket"},
    }
    for name, fields in expected_properties.items():
        schema = by_name[name].parameters
        properties = cast(dict[str, object], schema["properties"])
        assert schema["additionalProperties"] is False
        assert set(properties) == fields
        assert "input" not in properties
    documented = {"reportType", "name", "normalBalance"}
    for tool_name in (
        "api_account_natures_create_preview",
        "api_account_natures_update_preview",
    ):
        nature_schema = cast(
            dict[str, object], by_name[tool_name].parameters["properties"]["accountNature"]
        )
        if "$ref" in nature_schema:
            ref = str(nature_schema["$ref"]).rsplit("/", maxsplit=1)[-1]
            defs = by_name[tool_name].parameters.get("$defs") or by_name[tool_name].parameters.get(
                "defs"
            )
            assert isinstance(defs, dict)
            nature_schema = cast(dict[str, object], defs[ref])
        nested = cast(dict[str, object], nature_schema["properties"])
        assert set(nested) == documented
        assert nature_schema.get("additionalProperties") is False


@pytest.mark.parametrize(
    ("input_model", "payload"),
    [
        (AccountNatureCreatePreviewInput, {"accountNature": {}, "extra": True}),
        (
            AccountNatureUpdatePreviewInput,
            {"id": "nature-1", "accountNature": {}, "extra": True},
        ),
        (AccountNatureUpdatePreviewInput, {"id": "", "accountNature": {}}),
        (WriteExecuteInput, {"confirmation_ticket": "ticket", "accountNature": {}}),
        (AccountNatureCreatePreviewInput, {"accountNature": {"customField": "x"}}),
        (
            AccountNatureUpdatePreviewInput,
            {"id": "nature-1", "accountNature": {"name": "Asset", "undocumented": True}},
        ),
    ],
)
def test_outer_inputs_forbid_extra_fields_and_empty_ids(
    input_model: type[AccountNatureCreatePreviewInput]
    | type[AccountNatureUpdatePreviewInput]
    | type[WriteExecuteInput],
    payload: dict[str, object],
) -> None:
    with pytest.raises(ValidationError):
        input_model.model_validate(payload)


@pytest.mark.parametrize(
    ("tool_name", "arguments"),
    [
        (
            "api_account_natures_create_preview",
            {"accountNature": {"name": "Asset", "customField": "x"}},
        ),
        (
            "api_account_natures_update_preview",
            {
                "id": "nature-1",
                "accountNature": {"name": "Asset", "undocumented": True},
            },
        ),
    ],
)
def test_preview_tools_reject_undocumented_nested_account_nature_keys(
    tool_name: str,
    arguments: dict[str, object],
) -> None:
    server, requests = make_server(
        lambda request: pytest.fail(f"preview made an HTTP request: {request.method} {request.url}")
    )

    with pytest.raises(FastMcpValidationError, match="extra_forbidden"):
        asyncio.run(server.call_tool(tool_name, arguments))

    assert requests == []


@pytest.mark.parametrize(
    ("tool_name", "arguments", "expected_request"),
    [
        (
            "api_account_natures_create_preview",
            {
                "accountNature": {
                    "name": "Asset",
                    "reportType": "balance",
                    "normalBalance": "debit",
                }
            },
            {
                "accountNature": {
                    "name": "Asset",
                    "reportType": "balance",
                    "normalBalance": "debit",
                }
            },
        ),
        (
            "api_account_natures_update_preview",
            {
                "id": "nature-1",
                "accountNature": {"name": "Liability", "normalBalance": "credit"},
            },
            {"accountNature": {"name": "Liability", "normalBalance": "credit"}},
        ),
        (
            "api_account_natures_create_preview",
            {"accountNature": {}},
            {"accountNature": {}},
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
        "action": tool_name.removeprefix("api_account_natures_").removesuffix("_preview"),
        "resource": "accountNature",
        **({"id": arguments["id"]} if "id" in arguments else {}),
    }
    assert isinstance(preview["confirmation_ticket"], str)


@pytest.mark.parametrize(
    ("preview_name", "execute_name", "arguments", "response", "method", "path", "body"),
    [
        (
            "api_account_natures_create_preview",
            "api_account_natures_create_execute",
            {"accountNature": {"name": "Asset", "reportType": "balance"}},
            {"accountNatures": [{"id": "nature-1", "name": "Asset"}]},
            "POST",
            "/v2/accountNatures",
            {"accountNature": {"name": "Asset", "reportType": "balance"}},
        ),
        (
            "api_account_natures_update_preview",
            "api_account_natures_update_execute",
            {"id": "nature /?", "accountNature": {"name": "Equity"}},
            {"accountNatures": [{"id": "nature /?", "name": "Equity"}]},
            "PUT",
            "/v2/accountNatures/nature%20%2F%3F",
            {"accountNature": {"name": "Equity"}},
        ),
    ],
)
def test_execute_sends_exact_singular_account_nature_write_shapes_once(
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
    assert request.url.raw_path.decode() == path
    assert json.loads(request.content) == body
    assert execution["changed_records"] == response
    assert execution["deleted_records"] is None
