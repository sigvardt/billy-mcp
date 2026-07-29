"""Contract tests for typed, read-only chart-of-accounts API tools."""

from __future__ import annotations

import httpx
import pytest
from fastmcp import FastMCP
from pydantic import BaseModel, ValidationError

from billy_mcp.api.account_reads import (
    AccountGetRequest,
    AccountGetSuccess,
    AccountGroupGetRequest,
    AccountGroupGetSuccess,
    AccountGroupsListRequest,
    AccountGroupsListSuccess,
    AccountNatureGetRequest,
    AccountNatureGetSuccess,
    AccountNaturesListRequest,
    AccountNaturesListSuccess,
    AccountsListRequest,
    AccountsListSuccess,
    SortDirection,
    get_account,
    get_account_group,
    get_account_nature,
    list_account_groups,
    list_account_natures,
    list_accounts,
    register_account_read_tools,
)
from billy_mcp.client import BillyHttpClient
from billy_mcp.models import StableErrorCode, ToolError


def make_client(handler: httpx.MockTransport) -> BillyHttpClient:
    """Create a token-backed locked client against an in-process mock transport."""

    return BillyHttpClient(lambda: "test-token", transport=handler)


def test_account_get_uses_the_documented_encoded_path_and_singular_root() -> None:
    requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return httpx.Response(200, json={"account": {"id": "account /?", "name": "Sales"}})

    result = get_account(
        make_client(httpx.MockTransport(handler)),
        AccountGetRequest(id="account /?", include="group"),
    )

    assert isinstance(result, AccountGetSuccess)
    assert result.account.model_dump() == {"id": "account /?", "name": "Sales"}
    assert str(requests[0].url) == (
        "https://api.billysbilling.com/v2/accounts/account%20%2F%3F?include=group"
    )
    assert requests[0].method == "GET"


def test_account_group_get_uses_the_documented_encoded_path_and_singular_root() -> None:
    requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return httpx.Response(
            200,
            json={"accountGroup": {"id": "group /?", "name": "Revenue"}},
        )

    result = get_account_group(
        make_client(httpx.MockTransport(handler)),
        AccountGroupGetRequest(id="group /?", include="nature"),
    )

    assert isinstance(result, AccountGroupGetSuccess)
    assert result.accountGroup.model_dump() == {"id": "group /?", "name": "Revenue"}
    assert str(requests[0].url) == (
        "https://api.billysbilling.com/v2/accountGroups/group%20%2F%3F?include=nature"
    )
    assert requests[0].method == "GET"


def test_account_nature_get_uses_the_documented_encoded_path_and_singular_root() -> None:
    requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return httpx.Response(
            200,
            json={"accountNature": {"id": "nature /?", "name": "Income"}},
        )

    result = get_account_nature(
        make_client(httpx.MockTransport(handler)),
        AccountNatureGetRequest(id="nature /?", include="reportType"),
    )

    assert isinstance(result, AccountNatureGetSuccess)
    assert result.accountNature.model_dump() == {"id": "nature /?", "name": "Income"}
    assert str(requests[0].url) == (
        "https://api.billysbilling.com/v2/accountNatures/nature%20%2F%3F?include=reportType"
    )
    assert requests[0].method == "GET"


def test_lists_use_only_the_documented_query_and_map_each_root_with_paging() -> None:
    requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        roots = {
            "/v2/accounts": "accounts",
            "/v2/accountGroups": "accountGroups",
            "/v2/accountNatures": "accountNatures",
        }
        root = roots[request.url.path]
        return httpx.Response(
            200,
            json={
                root: [{"id": root, "name": root}],
                "meta": {
                    "paging": {
                        "page": 2,
                        "pageCount": 3,
                        "pageSize": 50,
                        "total": 125,
                        "firstUrl": f"/{root}?page=1",
                        "previousUrl": f"/{root}?page=1",
                        "nextUrl": f"/{root}?page=3",
                        "lastUrl": f"/{root}?page=3",
                    }
                },
            },
        )

    client = make_client(httpx.MockTransport(handler))
    accounts = list_accounts(
        client,
        AccountsListRequest(
            page=2,
            pageSize=50,
            include="group",
            sortProperty="name",
            sortDirection=SortDirection.ASC,
        ),
    )
    groups = list_account_groups(
        client,
        AccountGroupsListRequest(
            page=2,
            pageSize=50,
            include="nature",
            sortProperty="name",
            sortDirection=SortDirection.DESC,
        ),
    )
    natures = list_account_natures(
        client,
        AccountNaturesListRequest(
            page=2,
            pageSize=50,
            include="reportType",
            sortProperty="name",
            sortDirection=SortDirection.ASC,
        ),
    )

    assert isinstance(accounts, AccountsListSuccess)
    assert isinstance(groups, AccountGroupsListSuccess)
    assert isinstance(natures, AccountNaturesListSuccess)
    assert accounts.accounts[0].model_dump() == {"id": "accounts", "name": "accounts"}
    assert groups.accountGroups[0].model_dump() == {"id": "accountGroups", "name": "accountGroups"}
    assert natures.accountNatures[0].model_dump() == {
        "id": "accountNatures",
        "name": "accountNatures",
    }
    assert accounts.meta is not None and accounts.meta.paging is not None
    assert groups.meta is not None and groups.meta.paging is not None
    assert natures.meta is not None and natures.meta.paging is not None
    assert accounts.meta.paging.page_count == 3
    assert groups.meta.paging.next_url == "/accountGroups?page=3"
    assert natures.meta.paging.page_size == 50
    assert requests[0].url.params == httpx.QueryParams(
        {
            "page": "2",
            "pageSize": "50",
            "include": "group",
            "sortProperty": "name",
            "sortDirection": "ASC",
        }
    )
    assert requests[1].url.params == httpx.QueryParams(
        {
            "page": "2",
            "pageSize": "50",
            "include": "nature",
            "sortProperty": "name",
            "sortDirection": "DESC",
        }
    )
    assert requests[2].url.params == httpx.QueryParams(
        {
            "page": "2",
            "pageSize": "50",
            "include": "reportType",
            "sortProperty": "name",
            "sortDirection": "ASC",
        }
    )
    assert {key for key, _ in requests[0].url.params.multi_items()} == {
        "page",
        "pageSize",
        "include",
        "sortProperty",
        "sortDirection",
    }


def test_lists_preserve_an_absent_optional_meta_root() -> None:
    requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        roots = {
            "/v2/accounts": "accounts",
            "/v2/accountGroups": "accountGroups",
            "/v2/accountNatures": "accountNatures",
        }
        return httpx.Response(200, json={roots[request.url.path]: []})

    client = make_client(httpx.MockTransport(handler))
    accounts = list_accounts(client, AccountsListRequest())
    groups = list_account_groups(client, AccountGroupsListRequest())
    natures = list_account_natures(client, AccountNaturesListRequest())

    assert isinstance(accounts, AccountsListSuccess)
    assert isinstance(groups, AccountGroupsListSuccess)
    assert isinstance(natures, AccountNaturesListSuccess)
    assert accounts.model_dump() == {"accounts": []}
    assert groups.model_dump() == {"accountGroups": []}
    assert natures.model_dump() == {"accountNatures": []}
    assert [request.url.params for request in requests] == [
        httpx.QueryParams({"page": "1", "pageSize": "1000"}),
        httpx.QueryParams({"page": "1", "pageSize": "1000"}),
        httpx.QueryParams({"page": "1", "pageSize": "1000"}),
    ]


@pytest.mark.parametrize(
    ("request_type", "values", "field"),
    [
        (AccountsListRequest, {"page": 0}, "page"),
        (AccountGroupsListRequest, {"pageSize": 0}, "pageSize"),
        (AccountNaturesListRequest, {"pageSize": 1001}, "pageSize"),
        (AccountsListRequest, {"sortDirection": "DOWN"}, "sortDirection"),
        (AccountsListRequest, {"offset": 1}, "offset"),
        (AccountsListRequest, {"organizationId": "organization-1"}, "organizationId"),
        (AccountsListRequest, {"groupId": "group-1"}, "groupId"),
        (AccountsListRequest, {"natureId": "nature-1"}, "natureId"),
        (AccountGroupsListRequest, {"organizationId": "organization-1"}, "organizationId"),
        (AccountGroupsListRequest, {"natureId": "nature-1"}, "natureId"),
        (AccountNaturesListRequest, {"organizationId": "organization-1"}, "organizationId"),
        (AccountNaturesListRequest, {"groupId": "group-1"}, "groupId"),
        (AccountNaturesListRequest, {"q": "income"}, "q"),
    ],
)
def test_list_requests_reject_invalid_paging_and_undeclared_filters(
    request_type: type[BaseModel], values: dict[str, object], field: str
) -> None:
    with pytest.raises(ValidationError) as failure:
        request_type.model_validate(values)

    assert failure.value.errors()[0]["loc"] == (field,)


@pytest.mark.parametrize("error_code", ["AUTHENTICATION_REQUIRED", "OAUTH_INVALID_ACCESS_TOKEN"])
def test_documented_authentication_errors_remain_typed_for_each_tool(error_code: str) -> None:
    client = make_client(
        httpx.MockTransport(lambda request: httpx.Response(401, json={"errorCode": error_code}))
    )
    results = (
        get_account(client, AccountGetRequest(id="account-1")),
        get_account_group(client, AccountGroupGetRequest(id="group-1")),
        get_account_nature(client, AccountNatureGetRequest(id="nature-1")),
        list_accounts(client, AccountsListRequest()),
        list_account_groups(client, AccountGroupsListRequest()),
        list_account_natures(client, AccountNaturesListRequest()),
    )

    assert all(isinstance(result, ToolError) for result in results)
    assert {result.code for result in results if isinstance(result, ToolError)} == {
        StableErrorCode.AUTH_REQUIRED
    }


def test_undeclared_response_root_returns_a_typed_error() -> None:
    result = get_account(
        make_client(httpx.MockTransport(lambda request: httpx.Response(200, json={"wrong": {}}))),
        AccountGetRequest(id="account-1"),
    )

    assert isinstance(result, ToolError)
    assert result.code is StableErrorCode.BILLY_ERROR
    assert result.details == {"expected_root": "account"}


@pytest.mark.asyncio
async def test_registration_exposes_exactly_six_scoped_typed_read_tools() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        roots = {
            "/v2/accounts": "accounts",
            "/v2/accountGroups": "accountGroups",
            "/v2/accountNatures": "accountNatures",
        }
        return httpx.Response(200, json={roots[request.url.path]: []})

    server = FastMCP("account-reads-test")
    register_account_read_tools(server, make_client(httpx.MockTransport(handler)))

    tools = {tool.name: tool for tool in await server.list_tools()}
    assert set(tools) == {
        "api_accounts_get",
        "api_accounts_list",
        "api_account_groups_get",
        "api_account_groups_list",
        "api_account_natures_get",
        "api_account_natures_list",
    }
    for name in ("api_accounts_get", "api_account_groups_get", "api_account_natures_get"):
        assert set(tools[name].parameters["properties"]) == {"id", "include"}
    for name in ("api_accounts_list", "api_account_groups_list", "api_account_natures_list"):
        properties = tools[name].parameters["properties"]
        assert set(properties) == {
            "page",
            "pageSize",
            "include",
            "sortProperty",
            "sortDirection",
        }
        assert "offset" not in properties
        assert "organizationId" not in properties
        assert "groupId" not in properties
        assert "natureId" not in properties
    assert (
        await server.call_tool("api_accounts_list", {"page": 1, "pageSize": 1000})
    ).structured_content == {"result": {"accounts": []}}
    assert (
        await server.call_tool("api_account_groups_list", {"page": 1, "pageSize": 1000})
    ).structured_content == {"result": {"accountGroups": []}}
    assert (
        await server.call_tool("api_account_natures_list", {"page": 1, "pageSize": 1000})
    ).structured_content == {"result": {"accountNatures": []}}
