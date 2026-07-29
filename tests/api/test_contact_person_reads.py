"""Contract tests for the typed, read-only contact-person API tools."""

from __future__ import annotations

import httpx
import pytest
from fastmcp import FastMCP
from pydantic import ValidationError

from billy_mcp.api.contact_person_reads import (
    ContactPersonsGetRequest,
    ContactPersonsGetSuccess,
    ContactPersonsListRequest,
    ContactPersonsListSuccess,
    SortDirection,
    get_contact_person,
    list_contact_persons,
    register_contact_person_read_tools,
)
from billy_mcp.client import BillyHttpClient
from billy_mcp.models import StableErrorCode, ToolError


def make_client(handler: httpx.MockTransport) -> BillyHttpClient:
    """Create a token-backed locked client against a mock transport."""

    return BillyHttpClient(lambda: "test-token", transport=handler)


def test_get_encodes_id_and_maps_singular_contact_person_root() -> None:
    requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return httpx.Response(200, json={"contactPerson": {"id": "person/1", "name": "Ada"}})

    result = get_contact_person(
        make_client(httpx.MockTransport(handler)),
        ContactPersonsGetRequest(id="person/1", include="contact"),
    )

    assert isinstance(result, ContactPersonsGetSuccess)
    assert result.contact_person.model_dump() == {"id": "person/1", "name": "Ada"}
    assert str(requests[0].url) == (
        "https://api.billysbilling.com/v2/contactPersons/person%2F1?include=contact"
    )
    assert requests[0].method == "GET"


def test_list_sends_only_documented_query_parameters_and_maps_paging() -> None:
    requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return httpx.Response(
            200,
            json={
                "contactPersons": [{"id": "person-1", "name": "Ada"}],
                "meta": {
                    "paging": {
                        "page": 1000,
                        "pageCount": 1000,
                        "pageSize": 1000,
                        "total": 1_000_000,
                        "firstUrl": "/contactPersons?page=1",
                        "previousUrl": "/contactPersons?page=999",
                        "nextUrl": None,
                        "lastUrl": "/contactPersons?page=1000",
                    }
                },
            },
        )

    result = list_contact_persons(
        make_client(httpx.MockTransport(handler)),
        ContactPersonsListRequest(
            page=1000,
            pageSize=1000,
            include="contact",
            sortProperty="name",
            sortDirection=SortDirection.ASC,
        ),
    )

    assert isinstance(result, ContactPersonsListSuccess)
    assert result.contact_persons[0].model_dump() == {"id": "person-1", "name": "Ada"}
    assert result.meta is not None
    assert result.meta.paging is not None
    assert result.meta.paging.page == 1000
    assert result.meta.paging.page_size == 1000
    assert requests[0].url.params == httpx.QueryParams(
        {
            "page": "1000",
            "pageSize": "1000",
            "include": "contact",
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
        return httpx.Response(200, json={"contactPersons": []})

    result = list_contact_persons(
        make_client(httpx.MockTransport(handler)),
        ContactPersonsListRequest(),
    )

    assert isinstance(result, ContactPersonsListSuccess)
    assert result.contact_persons == []
    assert result.meta is None
    assert result.model_dump(by_alias=True) == {"contactPersons": []}
    assert requests[0].url.params == httpx.QueryParams({"page": "1", "pageSize": "1000"})


@pytest.mark.parametrize(
    ("kwargs", "field"),
    [
        ({"page": 0}, "page"),
        ({"pageSize": 0}, "pageSize"),
        ({"pageSize": 1001}, "pageSize"),
        ({"sortDirection": "DOWN"}, "sortDirection"),
        ({"offset": 0}, "offset"),
        ({"contactId": "contact-1"}, "contactId"),
        ({"other": True}, "other"),
    ],
)
def test_list_request_rejects_out_of_contract_paging_and_filters(
    kwargs: dict[str, object], field: str
) -> None:
    with pytest.raises(ValidationError, match=field):
        ContactPersonsListRequest.model_validate(kwargs)


def test_get_request_rejects_undeclared_input() -> None:
    with pytest.raises(ValidationError, match="contactId"):
        ContactPersonsGetRequest.model_validate({"id": "person-1", "contactId": "contact-1"})


@pytest.mark.parametrize("error_code", ["AUTHENTICATION_REQUIRED", "OAUTH_INVALID_ACCESS_TOKEN"])
def test_documented_authentication_errors_remain_typed(error_code: str) -> None:
    result = get_contact_person(
        make_client(
            httpx.MockTransport(lambda request: httpx.Response(401, json={"errorCode": error_code}))
        ),
        ContactPersonsGetRequest(id="person-1"),
    )

    assert isinstance(result, ToolError)
    assert result.code is StableErrorCode.AUTH_REQUIRED


@pytest.mark.asyncio
async def test_registers_only_the_two_typed_contact_person_read_tools() -> None:
    server = FastMCP("contact-persons-test")
    register_contact_person_read_tools(
        server,
        make_client(
            httpx.MockTransport(lambda request: httpx.Response(200, json={"contactPersons": []}))
        ),
    )

    tools = await server.list_tools()
    names = {tool.name for tool in tools}
    assert names == {"api_contact_persons_get", "api_contact_persons_list"}
    list_tool = await server.get_tool("api_contact_persons_list")
    assert list_tool is not None
    assert set(list_tool.parameters["properties"]) == {
        "page",
        "pageSize",
        "include",
        "sortProperty",
        "sortDirection",
    }
    assert "offset" not in list_tool.parameters["properties"]
    assert "contactId" not in list_tool.parameters["properties"]
    assert "other" not in list_tool.parameters["properties"]
    result = await server.call_tool("api_contact_persons_list", {"page": 1, "pageSize": 1000})
    assert result.structured_content == {"result": {"contactPersons": []}}
