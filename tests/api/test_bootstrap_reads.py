from __future__ import annotations

import asyncio
from collections.abc import Iterator
from dataclasses import dataclass
from typing import Any, cast

import httpx
import pytest
from fastmcp import FastMCP
from fastmcp.tools.base import ToolResult
from pydantic import ValidationError

from billy_mcp.api.bootstrap_reads import (
    OrganizationsListInput,
    register_bootstrap_read_tools,
)
from billy_mcp.client import BillyHttpClient
from billy_mcp.models import StableErrorCode
from billy_mcp.redaction import REDACTED


@dataclass
class RegisteredBootstrapTools:
    server: FastMCP
    client: BillyHttpClient
    requests: list[httpx.Request]


@pytest.fixture
def registered_bootstrap_tools() -> Iterator[RegisteredBootstrapTools]:
    """Provide the four registered tools behind a deterministic mock transport."""

    requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        if request.url.path == "/v2/user":
            return httpx.Response(200, json={"user": {"id": "user-1", "name": "Ada"}})
        if request.url.path == "/v2/user/organizations":
            return httpx.Response(
                200,
                json={"organizations": [{"id": "organization-1", "name": "Northwind"}]},
            )
        if request.url.path == "/v2/organizations/organization-1":
            return httpx.Response(
                200,
                json={
                    "organization": {
                        "id": "organization-1",
                        "name": "Northwind",
                        "subscriptionCardNumber": "4111111111111111",
                    }
                },
            )
        if request.url.path == "/v2/organizations":
            if request.url.params["page"] == "2":
                return httpx.Response(
                    200,
                    json={
                        "organizations": [{"id": "organization-2", "name": "Second"}],
                        "meta": {
                            "paging": {
                                "page": 2,
                                "pageSize": 1,
                                "total": 2,
                                "nextUrl": None,
                            }
                        },
                    },
                )
            return httpx.Response(200, json={"organizations": [{"id": "organization-1"}]})
        raise AssertionError(f"unexpected mock request: {request.url}")

    client = BillyHttpClient(
        lambda: "fixture-token",
        transport=httpx.MockTransport(handler),
        max_read_retries=0,
    )
    server = FastMCP("bootstrap-test")
    register_bootstrap_read_tools(server, client)
    try:
        yield RegisteredBootstrapTools(server=server, client=client, requests=requests)
    finally:
        client.close()


def invoke(server: FastMCP, name: str, arguments: dict[str, Any] | None = None) -> dict[str, Any]:
    result = asyncio.run(server.call_tool(name, arguments))
    assert isinstance(result, ToolResult)
    assert result.is_error is False
    assert isinstance(result.structured_content, dict)
    payload = result.structured_content["result"]
    assert isinstance(payload, dict)
    return cast(dict[str, Any], payload)


def test_registration_exposes_only_four_typed_bootstrap_read_tools(
    registered_bootstrap_tools: RegisteredBootstrapTools,
) -> None:
    tools = {
        tool.name: tool for tool in asyncio.run(registered_bootstrap_tools.server.list_tools())
    }

    assert set(tools) == {
        "api_user_get",
        "api_user_list_organizations",
        "api_organizations_get",
        "api_organizations_list",
    }
    assert tools["api_user_get"].parameters["properties"] == {}
    assert tools["api_user_list_organizations"].parameters["properties"] == {}
    assert set(tools["api_organizations_get"].parameters["properties"]) == {"id", "include"}
    list_parameters = tools["api_organizations_list"].parameters["properties"]
    assert set(list_parameters) == {
        "page",
        "pageSize",
        "include",
        "sortProperty",
        "sortDirection",
    }
    assert list_parameters["pageSize"]["minimum"] == 1
    assert list_parameters["pageSize"]["maximum"] == 1000
    assert list_parameters["sortDirection"]["anyOf"][0]["enum"] == ["ASC", "DESC"]
    output_schema = tools["api_user_get"].output_schema
    assert isinstance(output_schema, dict)
    output_properties = cast(dict[str, Any], output_schema["properties"])
    result_schema = output_properties["result"]
    assert isinstance(result_schema, dict)
    variants = cast(list[dict[str, Any]], result_schema["anyOf"])
    assert any("user" in cast(dict[str, Any], variant["properties"]) for variant in variants)
    assert any(
        {"code", "message"}.issubset(cast(dict[str, Any], variant["properties"]))
        for variant in variants
    )


def test_user_tools_construct_documented_paths_and_map_roots(
    registered_bootstrap_tools: RegisteredBootstrapTools,
) -> None:
    user = invoke(registered_bootstrap_tools.server, "api_user_get")
    organizations = invoke(registered_bootstrap_tools.server, "api_user_list_organizations")

    assert user == {"user": {"id": "user-1", "name": "Ada"}}
    assert organizations == {"organizations": [{"id": "organization-1", "name": "Northwind"}]}
    assert [request.url.path for request in registered_bootstrap_tools.requests] == [
        "/v2/user",
        "/v2/user/organizations",
    ]
    assert all(not request.url.params for request in registered_bootstrap_tools.requests)


def test_organization_get_uses_documented_query_and_redacts_subscription_fields(
    registered_bootstrap_tools: RegisteredBootstrapTools,
) -> None:
    result = invoke(
        registered_bootstrap_tools.server,
        "api_organizations_get",
        {"id": "organization-1", "include": "subscriptions"},
    )

    assert result == {
        "organization": {
            "id": "organization-1",
            "name": "Northwind",
            "subscriptionCardNumber": REDACTED,
        }
    }
    request = registered_bootstrap_tools.requests[-1]
    assert request.url.path == "/v2/organizations/organization-1"
    assert dict(request.url.params) == {"include": "subscriptions"}


def test_organizations_list_maps_optional_paging_and_documented_boundaries(
    registered_bootstrap_tools: RegisteredBootstrapTools,
) -> None:
    first_page = invoke(registered_bootstrap_tools.server, "api_organizations_list")
    second_page = invoke(
        registered_bootstrap_tools.server,
        "api_organizations_list",
        {
            "page": 2,
            "pageSize": 1,
            "include": "contacts:embed",
            "sortProperty": "name",
            "sortDirection": "DESC",
        },
    )

    assert first_page == {"organizations": [{"id": "organization-1"}], "paging": None}
    assert second_page == {
        "organizations": [{"id": "organization-2", "name": "Second"}],
        "paging": {"page": 2, "pageSize": 1, "total": 2, "nextUrl": None},
    }
    assert dict(registered_bootstrap_tools.requests[0].url.params) == {
        "page": "1",
        "pageSize": "1000",
    }
    assert dict(registered_bootstrap_tools.requests[1].url.params) == {
        "page": "2",
        "pageSize": "1",
        "include": "contacts:embed",
        "sortProperty": "name",
        "sortDirection": "DESC",
    }
    with pytest.raises(ValidationError):
        OrganizationsListInput(page=0)
    with pytest.raises(ValidationError):
        OrganizationsListInput(pageSize=1001)


@pytest.mark.parametrize("upstream_code", ["AUTHENTICATION_REQUIRED", "OAUTH_INVALID_ACCESS_TOKEN"])
def test_documented_authentication_errors_remain_typed(upstream_code: str) -> None:
    client = BillyHttpClient(
        lambda: "invalid-token",
        transport=httpx.MockTransport(
            lambda request: httpx.Response(401, json={"errorCode": upstream_code})
        ),
        max_read_retries=0,
    )
    server = FastMCP("bootstrap-auth-error-test")
    register_bootstrap_read_tools(server, client)
    try:
        result = invoke(server, "api_user_get")
    finally:
        client.close()

    assert result["code"] == StableErrorCode.AUTH_REQUIRED
    assert result["message"] == "Billy API authentication is required."
