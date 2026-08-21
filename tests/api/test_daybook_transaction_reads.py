"""Contract tests for the typed, read-only daybook-transaction API tools."""

from __future__ import annotations

import asyncio
from datetime import date

import httpx
import pytest
from fastmcp import FastMCP
from pydantic import ValidationError

from billy_mcp.api.daybook_transaction_reads import (
    DaybookTransactionGetInput,
    DaybookTransactionGetSuccess,
    DaybookTransactionListInput,
    DaybookTransactionListSuccess,
    DaybookTransactionSortProperty,
    DaybookTransactionState,
    SortDirection,
    get_daybook_transaction,
    list_daybook_transactions,
    register_daybook_transaction_read_tools,
)
from billy_mcp.client import BillyHttpClient
from billy_mcp.models import StableErrorCode, ToolError


def make_client(handler: httpx.MockTransport) -> BillyHttpClient:
    """Create the locked client against an in-process mock transport."""

    return BillyHttpClient(lambda: "test-token", transport=handler)


def test_get_uses_the_documented_relative_path_and_singular_root() -> None:
    requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return httpx.Response(
            200,
            json={"daybookTransaction": {"id": "transaction 1", "state": "approved"}},
        )

    result = get_daybook_transaction(
        make_client(httpx.MockTransport(handler)),
        DaybookTransactionGetInput(id="transaction 1", include="entries"),
    )

    assert isinstance(result, DaybookTransactionGetSuccess)
    assert result.daybookTransaction.model_dump() == {
        "id": "transaction 1",
        "state": "approved",
    }
    assert str(requests[0].url) == (
        "https://api.billysbilling.com/v2/daybookTransactions/transaction%201?include=entries"
    )
    assert requests[0].method == "GET"


def test_list_uses_only_documented_filters_and_maps_paging() -> None:
    requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return httpx.Response(
            200,
            json={
                "daybookTransactions": [{"id": "transaction-1", "priority": 3}],
                "meta": {
                    "paging": {
                        "page": 2,
                        "pageCount": 3,
                        "pageSize": 50,
                        "total": 125,
                        "firstUrl": "/daybookTransactions?page=1",
                        "previousUrl": "/daybookTransactions?page=1",
                        "nextUrl": "/daybookTransactions?page=3",
                        "lastUrl": "/daybookTransactions?page=3",
                    }
                },
            },
        )

    result = list_daybook_transactions(
        make_client(httpx.MockTransport(handler)),
        DaybookTransactionListInput(
            page=2,
            pageSize=50,
            include="entries",
            organizationId="organization-1",
            daybookId="daybook-1",
            apiType="manual",
            state=DaybookTransactionState.APPROVED,
            minEntryDate=date(2026, 1, 1),
            maxEntryDate=date(2026, 1, 31),
            q="consulting",
            sortProperty=DaybookTransactionSortProperty.ENTRY_DATE,
            sortDirection=SortDirection.DESC,
        ),
    )

    assert isinstance(result, DaybookTransactionListSuccess)
    assert result.daybookTransactions[0].model_dump() == {"id": "transaction-1", "priority": 3}
    assert result.meta is not None
    assert result.meta.paging is not None
    assert result.meta.paging.page_count == 3
    assert result.meta.paging.next_url == "/daybookTransactions?page=3"
    assert requests[0].url.params == httpx.QueryParams(
        {
            "page": "2",
            "pageSize": "50",
            "include": "entries",
            "organizationId": "organization-1",
            "daybookId": "daybook-1",
            "apiType": "manual",
            "state": "approved",
            "minEntryDate": "2026-01-01",
            "maxEntryDate": "2026-01-31",
            "q": "consulting",
            "sortProperty": "entryDate",
            "sortDirection": "DESC",
        }
    )
    assert set(requests[0].url.params) == {
        "page",
        "pageSize",
        "include",
        "organizationId",
        "daybookId",
        "apiType",
        "state",
        "minEntryDate",
        "maxEntryDate",
        "q",
        "sortProperty",
        "sortDirection",
    }


def test_list_preserves_an_absent_optional_meta_paging_root() -> None:
    requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return httpx.Response(200, json={"daybookTransactions": []})

    result = list_daybook_transactions(
        make_client(httpx.MockTransport(handler)), DaybookTransactionListInput()
    )

    assert isinstance(result, DaybookTransactionListSuccess)
    assert result.daybookTransactions == []
    assert result.meta is None
    assert result.model_dump() == {"daybookTransactions": []}
    assert requests[0].url.params == httpx.QueryParams({"page": "1", "pageSize": "1000"})


@pytest.mark.parametrize(
    ("input_type", "values", "field"),
    [
        (DaybookTransactionGetInput, {"id": "transaction-1", "page": 1}, "page"),
        (DaybookTransactionListInput, {"page": 0}, "page"),
        (DaybookTransactionListInput, {"pageSize": 1001}, "pageSize"),
        (DaybookTransactionListInput, {"offset": 100}, "offset"),
        (DaybookTransactionListInput, {"contactId": "contact-1"}, "contactId"),
        (DaybookTransactionListInput, {"state": "pending"}, "state"),
        (DaybookTransactionListInput, {"sortProperty": "voucherNo"}, "sortProperty"),
        (DaybookTransactionListInput, {"sortDirection": "DOWN"}, "sortDirection"),
    ],
)
def test_inputs_reject_unknown_and_invalid_contract_values(
    input_type: type[DaybookTransactionGetInput] | type[DaybookTransactionListInput],
    values: dict[str, object],
    field: str,
) -> None:
    with pytest.raises(ValidationError) as failure:
        input_type.model_validate(values)

    assert failure.value.errors()[0]["loc"] == (field,)


@pytest.mark.parametrize("error_code", ["AUTHENTICATION_REQUIRED", "OAUTH_INVALID_ACCESS_TOKEN"])
def test_documented_authentication_envelopes_remain_typed(error_code: str) -> None:
    result = get_daybook_transaction(
        make_client(
            httpx.MockTransport(lambda request: httpx.Response(401, json={"errorCode": error_code}))
        ),
        DaybookTransactionGetInput(id="transaction-1"),
    )

    assert isinstance(result, ToolError)
    assert result.code is StableErrorCode.AUTH_REQUIRED


def test_registration_exposes_exactly_two_typed_daybook_transaction_tools() -> None:
    server = FastMCP("daybook-transaction-test")
    register_daybook_transaction_read_tools(
        server,
        make_client(
            httpx.MockTransport(
                lambda request: httpx.Response(200, json={"daybookTransactions": []})
            )
        ),
    )

    tools = {tool.name: tool for tool in asyncio.run(server.list_tools())}

    assert set(tools) == {"api_daybook_transactions_get", "api_daybook_transactions_list"}
    get_input_schema = tools["api_daybook_transactions_get"].parameters["properties"]["input"]
    assert get_input_schema["additionalProperties"] is False
    assert get_input_schema["required"] == ["id"]
    assert set(get_input_schema["properties"]) == {"id", "include"}
    list_input_schema = tools["api_daybook_transactions_list"].parameters["properties"]["input"]
    assert list_input_schema["additionalProperties"] is False
    list_properties = list_input_schema["properties"]
    assert set(list_properties) == {
        "page",
        "pageSize",
        "include",
        "organizationId",
        "daybookId",
        "apiType",
        "state",
        "minEntryDate",
        "maxEntryDate",
        "q",
        "sortProperty",
        "sortDirection",
    }
    assert "offset" not in list_properties
    assert "contactId" not in list_properties
    assert asyncio.run(
        server.call_tool("api_daybook_transactions_list", {"input": {"page": 1, "pageSize": 1000}})
    ).structured_content == {"result": {"daybookTransactions": []}}
