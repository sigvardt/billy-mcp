"""Contract tests for the typed, read-only contacts API tools."""

from __future__ import annotations

import httpx
import pytest
from fastmcp import FastMCP
from pydantic import ValidationError

from billy_mcp.api.contact_reads import (
    ContactsGetRequest,
    ContactsGetSuccess,
    ContactsListRequest,
    ContactsListSuccess,
    SortDirection,
    get_contact,
    list_contacts,
    register_contact_read_tools,
)
from billy_mcp.client import BillyHttpClient
from billy_mcp.models import StableErrorCode, ToolError


def make_client(handler: httpx.MockTransport) -> BillyHttpClient:
    """Create a token-backed locked client against a mock transport."""

    return BillyHttpClient(lambda: "test-token", transport=handler)


def test_get_builds_relative_request_and_maps_singular_contact_root() -> None:
    requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return httpx.Response(200, json={"contact": {"id": "contact 1", "name": "Ada"}})

    result = get_contact(
        make_client(httpx.MockTransport(handler)),
        ContactsGetRequest(id="contact 1", include="contactPersons"),
    )

    assert isinstance(result, ContactsGetSuccess)
    assert result.contact.model_dump() == {"id": "contact 1", "name": "Ada"}
    assert str(requests[0].url) == (
        "https://api.billysbilling.com/v2/contacts/contact%201?include=contactPersons"
    )
    assert requests[0].method == "GET"


def test_list_builds_only_documented_query_parameters_and_maps_paging() -> None:
    requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return httpx.Response(
            200,
            json={
                "contacts": [{"id": "contact-1", "name": "Ada"}],
                "meta": {
                    "paging": {
                        "page": 1000,
                        "pageCount": 1000,
                        "pageSize": 1000,
                        "total": 1_000_000,
                        "firstUrl": "/contacts?page=1",
                        "previousUrl": "/contacts?page=999",
                        "nextUrl": None,
                        "lastUrl": "/contacts?page=1000",
                    }
                },
            },
        )

    result = list_contacts(
        make_client(httpx.MockTransport(handler)),
        ContactsListRequest(
            page=1000,
            pageSize=1000,
            include="contactPersons",
            sortProperty="name",
            sortDirection=SortDirection.ASC,
        ),
    )

    assert isinstance(result, ContactsListSuccess)
    assert result.contacts[0].model_dump() == {"id": "contact-1", "name": "Ada"}
    assert result.meta is not None
    assert result.meta.paging is not None
    assert result.meta.paging.page == 1000
    assert result.meta.paging.page_size == 1000
    assert requests[0].url.params == httpx.QueryParams(
        {
            "page": "1000",
            "pageSize": "1000",
            "include": "contactPersons",
            "sortProperty": "name",
            "sortDirection": "ASC",
        }
    )
    assert set(requests[0].url.params) == {
        "page",
        "pageSize",
        "include",
        "sortProperty",
        "sortDirection",
    }


def test_list_maps_absent_optional_paging_without_fabricating_it() -> None:
    requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return httpx.Response(200, json={"contacts": []})

    result = list_contacts(
        make_client(httpx.MockTransport(handler)),
        ContactsListRequest(),
    )

    assert isinstance(result, ContactsListSuccess)
    assert result.contacts == []
    assert result.meta is None
    assert result.model_dump() == {"contacts": []}
    assert requests[0].url.params == httpx.QueryParams({"page": "1", "pageSize": "1000"})


@pytest.mark.parametrize(
    ("kwargs", "field"),
    [
        ({"page": 0}, "page"),
        ({"pageSize": 0}, "pageSize"),
        ({"pageSize": 1001}, "pageSize"),
        ({"sortDirection": "DOWN"}, "sortDirection"),
        ({"q": "Ada"}, "q"),
        ({"customer": True}, "customer"),
        ({"supplier": True}, "supplier"),
    ],
)
def test_list_request_rejects_out_of_contract_paging_and_filters(
    kwargs: dict[str, object], field: str
) -> None:
    with pytest.raises(ValidationError, match=field):
        ContactsListRequest.model_validate(kwargs)


@pytest.mark.parametrize("error_code", ["AUTHENTICATION_REQUIRED", "OAUTH_INVALID_ACCESS_TOKEN"])
def test_documented_authentication_errors_remain_typed(error_code: str) -> None:
    result = get_contact(
        make_client(
            httpx.MockTransport(lambda request: httpx.Response(401, json={"errorCode": error_code}))
        ),
        ContactsGetRequest(id="contact-1"),
    )

    assert isinstance(result, ToolError)
    assert result.code is StableErrorCode.AUTH_REQUIRED


@pytest.mark.asyncio
async def test_registers_only_the_two_typed_contacts_read_tools() -> None:
    server = FastMCP("contacts-test")
    register_contact_read_tools(
        server,
        make_client(
            httpx.MockTransport(lambda request: httpx.Response(200, json={"contacts": []}))
        ),
    )

    tools = await server.list_tools()
    names = {tool.name for tool in tools}
    assert names == {"api_contacts_get", "api_contacts_list"}
    list_tool = await server.get_tool("api_contacts_list")
    assert list_tool is not None
    assert set(list_tool.parameters["properties"]) == {
        "page",
        "pageSize",
        "include",
        "sortProperty",
        "sortDirection",
    }
    assert "q" not in list_tool.parameters["properties"]
    assert "customer" not in list_tool.parameters["properties"]
    assert "supplier" not in list_tool.parameters["properties"]
    result = await server.call_tool("api_contacts_list", {"page": 1, "pageSize": 1000})
    assert result.structured_content == {"result": {"contacts": []}}
