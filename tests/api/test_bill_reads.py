"""Contract tests for the typed, read-only bills API tools."""

from __future__ import annotations

from datetime import date

import httpx
import pytest
from fastmcp import FastMCP
from pydantic import ValidationError

from billy_mcp.api.bill_reads import (
    BillsGetRequest,
    BillsGetSuccess,
    BillsListRequest,
    BillsListSuccess,
    BillSortProperty,
    BillState,
    SortDirection,
    get_bill,
    list_bills,
    register_bill_read_tools,
)
from billy_mcp.client import BillyHttpClient
from billy_mcp.models import StableErrorCode, ToolError


def make_client(handler: httpx.MockTransport) -> BillyHttpClient:
    """Create a token-backed locked client against a mock transport."""

    return BillyHttpClient(lambda: "test-token", transport=handler)


def test_get_builds_relative_request_and_maps_singular_bill_root() -> None:
    requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return httpx.Response(200, json={"bill": {"id": "bill 1", "amount": 42.5}})

    result = get_bill(
        make_client(httpx.MockTransport(handler)),
        BillsGetRequest(id="bill 1", include="contact"),
    )

    assert isinstance(result, BillsGetSuccess)
    assert result.bill.model_dump() == {"id": "bill 1", "amount": 42.5}
    assert str(requests[0].url) == "https://api.billysbilling.com/v2/bills/bill%201?include=contact"
    assert requests[0].method == "GET"


def test_list_builds_only_documented_query_parameters_and_maps_paging() -> None:
    requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return httpx.Response(
            200,
            json={
                "bills": [{"id": "bill-1", "amount": 42.5}],
                "meta": {
                    "paging": {
                        "page": 3,
                        "pageCount": 8,
                        "pageSize": 25,
                        "total": 200,
                        "firstUrl": "/bills?page=1",
                        "previousUrl": "/bills?page=2",
                        "nextUrl": "/bills?page=4",
                        "lastUrl": "/bills?page=8",
                    }
                },
            },
        )

    result = list_bills(
        make_client(httpx.MockTransport(handler)),
        BillsListRequest(
            page=3,
            pageSize=25,
            include="contact",
            sortProperty=BillSortProperty.DUE_DATE,
            sortDirection=SortDirection.DESC,
            organizationId="organization-1",
            contactId="contact-1",
            creditedBillId="bill-0",
            minEntryDate=date(2026, 1, 2),
            maxEntryDate=date(2026, 1, 31),
            minDueDate=date(2026, 2, 1),
            maxDueDate=date(2026, 2, 28),
            isPaid=True,
            hasAttachments=False,
            state=BillState.APPROVED,
            currencyId="DKK",
            suppliersInvoiceNo="SUP-1",
            isBare=True,
            amount=42.5,
            q="supplier search",
        ),
    )

    assert isinstance(result, BillsListSuccess)
    assert result.bills[0].model_dump() == {"id": "bill-1", "amount": 42.5}
    assert result.meta is not None
    assert result.meta.paging is not None
    assert result.meta.paging.page == 3
    assert result.meta.paging.page_size == 25
    assert requests[0].url.params == httpx.QueryParams(
        {
            "page": "3",
            "pageSize": "25",
            "include": "contact",
            "sortProperty": "dueDate",
            "sortDirection": "DESC",
            "organizationId": "organization-1",
            "contactId": "contact-1",
            "creditedBillId": "bill-0",
            "minEntryDate": "2026-01-02",
            "maxEntryDate": "2026-01-31",
            "minDueDate": "2026-02-01",
            "maxDueDate": "2026-02-28",
            "isPaid": "true",
            "hasAttachments": "false",
            "state": "approved",
            "currencyId": "DKK",
            "suppliersInvoiceNo": "SUP-1",
            "isBare": "true",
            "amount": "42.5",
            "q": "supplier search",
        }
    )
    assert set(requests[0].url.params) == {
        "page",
        "pageSize",
        "include",
        "sortProperty",
        "sortDirection",
        "organizationId",
        "contactId",
        "creditedBillId",
        "minEntryDate",
        "maxEntryDate",
        "minDueDate",
        "maxDueDate",
        "isPaid",
        "hasAttachments",
        "state",
        "currencyId",
        "suppliersInvoiceNo",
        "isBare",
        "amount",
        "q",
    }


def test_list_maps_absent_optional_paging_without_fabricating_it() -> None:
    requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return httpx.Response(200, json={"bills": []})

    result = list_bills(make_client(httpx.MockTransport(handler)), BillsListRequest())

    assert isinstance(result, BillsListSuccess)
    assert result.bills == []
    assert result.meta is None
    assert result.model_dump() == {"bills": []}
    assert requests[0].url.params == httpx.QueryParams({"page": "1", "pageSize": "1000"})


@pytest.mark.parametrize(
    ("kwargs", "field"),
    [
        ({"page": 0}, "page"),
        ({"pageSize": 0}, "pageSize"),
        ({"pageSize": 1001}, "pageSize"),
        ({"sortProperty": "invoiceNo"}, "sortProperty"),
        ({"sortDirection": "DOWN"}, "sortDirection"),
        ({"state": "paid"}, "state"),
        ({"q": ""}, "q"),
        ({"offset": 1}, "offset"),
        ({"entryDatePeriod": "thisMonth"}, "entryDatePeriod"),
        ({"minApprovedTime": "2026-01-01"}, "minApprovedTime"),
        ({"maxApprovedTime": "2026-01-31"}, "maxApprovedTime"),
        ({"approvedTimePeriod": "thisMonth"}, "approvedTimePeriod"),
        ({"quoteId": "quote-1"}, "quoteId"),
        ({"recurringInvoiceId": "recurring-1"}, "recurringInvoiceId"),
        ({"invoiceNo": "INV-1"}, "invoiceNo"),
        ({"externalId": "external-1"}, "externalId"),
    ],
)
def test_list_request_rejects_out_of_contract_filters_and_enum_values(
    kwargs: dict[str, object], field: str
) -> None:
    with pytest.raises(ValidationError, match=field):
        BillsListRequest.model_validate(kwargs)


@pytest.mark.parametrize("error_code", ["AUTHENTICATION_REQUIRED", "OAUTH_INVALID_ACCESS_TOKEN"])
def test_documented_authentication_errors_remain_typed(error_code: str) -> None:
    result = get_bill(
        make_client(
            httpx.MockTransport(lambda request: httpx.Response(401, json={"errorCode": error_code}))
        ),
        BillsGetRequest(id="bill-1"),
    )

    assert isinstance(result, ToolError)
    assert result.code is StableErrorCode.AUTH_REQUIRED


@pytest.mark.asyncio
async def test_registers_only_the_two_typed_bill_read_tools() -> None:
    server = FastMCP("bills-test")
    register_bill_read_tools(
        server,
        make_client(httpx.MockTransport(lambda request: httpx.Response(200, json={"bills": []}))),
    )

    tools = await server.list_tools()
    assert {tool.name for tool in tools} == {"api_bills_get", "api_bills_list"}
    get_tool = await server.get_tool("api_bills_get")
    assert get_tool is not None
    assert set(get_tool.parameters["properties"]) == {"id", "include"}
    list_tool = await server.get_tool("api_bills_list")
    assert list_tool is not None
    assert set(list_tool.parameters["properties"]) == {
        "page",
        "pageSize",
        "include",
        "sortProperty",
        "sortDirection",
        "organizationId",
        "contactId",
        "creditedBillId",
        "minEntryDate",
        "maxEntryDate",
        "minDueDate",
        "maxDueDate",
        "isPaid",
        "hasAttachments",
        "state",
        "currencyId",
        "suppliersInvoiceNo",
        "isBare",
        "amount",
        "q",
    }
    for invoice_only_filter in {
        "entryDatePeriod",
        "minApprovedTime",
        "maxApprovedTime",
        "approvedTimePeriod",
        "quoteId",
        "recurringInvoiceId",
        "invoiceNo",
        "externalId",
    }:
        assert invoice_only_filter not in list_tool.parameters["properties"]
    result = await server.call_tool("api_bills_list", {"page": 1, "pageSize": 1000})
    assert result.structured_content == {"result": {"bills": []}}
