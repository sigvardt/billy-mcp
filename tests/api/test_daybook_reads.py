"""Contract tests for the typed, read-only daybook-parent API tools."""

from __future__ import annotations

import asyncio

import httpx
import pytest
from fastmcp import FastMCP
from pydantic import ValidationError

from billy_mcp.api.daybook_reads import (
    DaybookBalanceAccountGetInput,
    DaybookBalanceAccountGetSuccess,
    DaybookBalanceAccountListInput,
    DaybookBalanceAccountListSuccess,
    DaybookGetInput,
    DaybookGetSuccess,
    DaybookListInput,
    DaybookListSuccess,
    SortDirection,
    get_daybook,
    get_daybook_balance_account,
    list_daybook_balance_accounts,
    list_daybooks,
    register_daybook_read_tools,
)
from billy_mcp.client import BillyHttpClient
from billy_mcp.models import StableErrorCode, ToolError


def make_client(handler: httpx.MockTransport) -> BillyHttpClient:
    """Create the locked client against an in-process mock transport."""

    return BillyHttpClient(lambda: "test-token", transport=handler)


def test_gets_use_documented_paths_encoded_ids_and_singular_roots() -> None:
    requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        if request.url.path.startswith("/v2/daybooks/"):
            return httpx.Response(200, json={"daybook": {"id": "daybook /?", "name": "Sales"}})
        return httpx.Response(
            200,
            json={"daybookBalanceAccount": {"id": "balance /?", "priority": 1}},
        )

    client = make_client(httpx.MockTransport(handler))
    daybook = get_daybook(client, DaybookGetInput(id="daybook /?", include="balanceAccounts"))
    balance_account = get_daybook_balance_account(
        client,
        DaybookBalanceAccountGetInput(id="balance /?"),
    )

    assert isinstance(daybook, DaybookGetSuccess)
    assert daybook.daybook.model_dump() == {"id": "daybook /?", "name": "Sales"}
    assert isinstance(balance_account, DaybookBalanceAccountGetSuccess)
    assert balance_account.daybookBalanceAccount.model_dump() == {"id": "balance /?", "priority": 1}
    assert str(requests[0].url) == (
        "https://api.billysbilling.com/v2/daybooks/daybook%20%2F%3F?include=balanceAccounts"
    )
    assert str(requests[1].url) == (
        "https://api.billysbilling.com/v2/daybookBalanceAccounts/balance%20%2F%3F"
    )
    assert {request.method for request in requests} == {"GET"}


def test_daybooks_list_uses_only_documented_query_parameters_and_maps_paging() -> None:
    requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return httpx.Response(
            200,
            json={
                "daybooks": [{"id": "daybook-1", "name": "Sales"}],
                "meta": {
                    "paging": {
                        "page": 2,
                        "pageCount": 3,
                        "pageSize": 50,
                        "total": 125,
                        "nextUrl": "/daybooks?page=3",
                    }
                },
            },
        )

    result = list_daybooks(
        make_client(httpx.MockTransport(handler)),
        DaybookListInput(
            page=2,
            pageSize=50,
            include="balanceAccounts",
            sortProperty="name",
            sortDirection=SortDirection.DESC,
        ),
    )

    assert isinstance(result, DaybookListSuccess)
    assert result.daybooks[0].model_dump() == {"id": "daybook-1", "name": "Sales"}
    assert result.meta is not None
    assert result.meta.paging is not None
    assert result.meta.paging.page_count == 3
    assert result.meta.paging.next_url == "/daybooks?page=3"
    assert requests[0].url.path == "/v2/daybooks"
    assert requests[0].url.params == httpx.QueryParams(
        {
            "page": "2",
            "pageSize": "50",
            "include": "balanceAccounts",
            "sortProperty": "name",
            "sortDirection": "DESC",
        }
    )
    assert set(requests[0].url.params) == {
        "page",
        "pageSize",
        "include",
        "sortProperty",
        "sortDirection",
    }


def test_present_meta_without_paging_does_not_fabricate_a_paging_object() -> None:
    result = list_daybooks(
        make_client(
            httpx.MockTransport(
                lambda request: httpx.Response(200, json={"daybooks": [], "meta": {}})
            )
        ),
        DaybookListInput(),
    )

    assert isinstance(result, DaybookListSuccess)
    assert result.meta is not None
    assert result.meta.paging is None
    assert result.model_dump() == {"daybooks": [], "meta": {}}


def test_balance_account_list_uses_all_documented_query_parameters_and_preserves_absent_meta() -> (
    None
):
    requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return httpx.Response(
            200,
            json={"daybookBalanceAccounts": [{"id": "balance-1", "priority": 1}]},
        )

    result = list_daybook_balance_accounts(
        make_client(httpx.MockTransport(handler)),
        DaybookBalanceAccountListInput(
            page=3,
            pageSize=25,
            include="account",
            sortProperty="priority",
            sortDirection=SortDirection.ASC,
        ),
    )

    assert isinstance(result, DaybookBalanceAccountListSuccess)
    assert result.daybookBalanceAccounts[0].model_dump() == {"id": "balance-1", "priority": 1}
    assert result.meta is None
    assert result.model_dump() == {"daybookBalanceAccounts": [{"id": "balance-1", "priority": 1}]}
    assert requests[0].url.path == "/v2/daybookBalanceAccounts"
    assert requests[0].url.params == httpx.QueryParams(
        {
            "page": "3",
            "pageSize": "25",
            "include": "account",
            "sortProperty": "priority",
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


@pytest.mark.parametrize(
    ("input_type", "values", "field"),
    [
        (DaybookGetInput, {"id": "daybook-1", "page": 1}, "page"),
        (DaybookGetInput, {"id": "daybook-1", "include": ""}, "include"),
        (DaybookBalanceAccountGetInput, {"id": "balance-1", "offset": 1}, "offset"),
        (DaybookListInput, {"offset": 1}, "offset"),
        (DaybookListInput, {"include": ""}, "include"),
        (DaybookListInput, {"sortProperty": ""}, "sortProperty"),
        (DaybookListInput, {"daybookId": "daybook-1"}, "daybookId"),
        (DaybookListInput, {"organizationId": "organization-1"}, "organizationId"),
        (DaybookBalanceAccountListInput, {"offset": 1}, "offset"),
        (DaybookBalanceAccountListInput, {"daybookId": "daybook-1"}, "daybookId"),
        (DaybookBalanceAccountListInput, {"organizationId": "organization-1"}, "organizationId"),
        (DaybookBalanceAccountListInput, {"include": ""}, "include"),
        (DaybookBalanceAccountListInput, {"sortProperty": ""}, "sortProperty"),
        (DaybookBalanceAccountListInput, {"madeUp": True}, "madeUp"),
        (DaybookListInput, {"page": 0}, "page"),
        (DaybookListInput, {"pageSize": 1001}, "pageSize"),
        (DaybookBalanceAccountListInput, {"sortDirection": "DOWN"}, "sortDirection"),
    ],
)
def test_inputs_reject_invented_filters_unknown_fields_and_invalid_controls(
    input_type: type[
        DaybookGetInput
        | DaybookBalanceAccountGetInput
        | DaybookListInput
        | DaybookBalanceAccountListInput
    ],
    values: dict[str, object],
    field: str,
) -> None:
    with pytest.raises(ValidationError) as failure:
        input_type.model_validate(values)

    assert failure.value.errors()[0]["loc"] == (field,)


@pytest.mark.parametrize("error_code", ["AUTHENTICATION_REQUIRED", "OAUTH_INVALID_ACCESS_TOKEN"])
def test_documented_authentication_envelopes_remain_typed(error_code: str) -> None:
    result = get_daybook(
        make_client(
            httpx.MockTransport(lambda request: httpx.Response(401, json={"errorCode": error_code}))
        ),
        DaybookGetInput(id="daybook-1"),
    )

    assert isinstance(result, ToolError)
    assert result.code is StableErrorCode.AUTH_REQUIRED


def test_registration_exposes_exactly_four_typed_daybook_parent_tools() -> None:
    server = FastMCP("daybook-parent-test")
    register_daybook_read_tools(
        server,
        make_client(
            httpx.MockTransport(
                lambda request: httpx.Response(
                    200,
                    json={
                        "daybooks": [],
                        "daybookBalanceAccounts": [],
                    },
                )
            )
        ),
    )

    tools = {tool.name: tool for tool in asyncio.run(server.list_tools())}

    assert set(tools) == {
        "api_daybooks_get",
        "api_daybooks_list",
        "api_daybook_balance_accounts_get",
        "api_daybook_balance_accounts_list",
    }
    for tool_name in ("api_daybooks_list", "api_daybook_balance_accounts_list"):
        properties = tools[tool_name].parameters["properties"]
        assert set(properties) == {
            "page",
            "pageSize",
            "include",
            "sortProperty",
            "sortDirection",
        }
        assert "offset" not in properties
        assert "daybookId" not in properties
        assert "organizationId" not in properties

    assert asyncio.run(
        server.call_tool("api_daybooks_list", {"page": 1, "pageSize": 1000})
    ).structured_content == {"result": {"daybooks": []}}
    assert asyncio.run(
        server.call_tool("api_daybook_balance_accounts_list", {"page": 1, "pageSize": 1000})
    ).structured_content == {"result": {"daybookBalanceAccounts": []}}
