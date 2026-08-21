"""Contract tests for the typed, read-only invoice API tools."""

from __future__ import annotations

import httpx
import pytest
from fastmcp import FastMCP
from pydantic import ValidationError

from billy_mcp.api.invoice_reads import (
    InvoicesGetRequest,
    InvoicesGetSuccess,
    InvoicesListRequest,
    InvoicesListSuccess,
    InvoiceSortProperty,
    InvoiceState,
    SortDirection,
    get_invoice,
    list_invoices,
    register_invoice_read_tools,
)
from billy_mcp.client import BillyHttpClient
from billy_mcp.models import StableErrorCode, ToolError


def make_client(handler: httpx.MockTransport) -> BillyHttpClient:
    """Create a token-backed locked client against a mock transport."""

    return BillyHttpClient(lambda: "test-token", transport=handler)


def test_get_builds_relative_request_and_maps_singular_invoice_root() -> None:
    requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return httpx.Response(200, json={"invoice": {"id": "invoice 1", "invoiceNo": "42"}})

    result = get_invoice(
        make_client(httpx.MockTransport(handler)),
        InvoicesGetRequest(id="invoice 1", include="lines"),
    )

    assert isinstance(result, InvoicesGetSuccess)
    assert result.invoice.model_dump() == {"id": "invoice 1", "invoiceNo": "42"}
    assert (
        str(requests[0].url)
        == "https://api.billysbilling.com/v2/invoices/invoice%201?include=lines"
    )
    assert requests[0].method == "GET"


def test_list_builds_only_documented_query_parameters_and_maps_paging() -> None:
    requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return httpx.Response(
            200,
            json={
                "invoices": [{"id": "invoice-1", "invoiceNo": "42"}],
                "meta": {
                    "paging": {
                        "page": 2,
                        "pageCount": 3,
                        "pageSize": 25,
                        "total": 74,
                        "firstUrl": "/invoices?page=1",
                        "previousUrl": "/invoices?page=1",
                        "nextUrl": "/invoices?page=3",
                        "lastUrl": "/invoices?page=3",
                    }
                },
            },
        )

    result = list_invoices(
        make_client(httpx.MockTransport(handler)),
        InvoicesListRequest(
            page=2,
            pageSize=25,
            include="lines",
            sortProperty=InvoiceSortProperty.ENTRY_DATE,
            sortDirection=SortDirection.DESC,
            organizationId="organization-1",
            contactId="contact-1",
            creditedInvoiceId="invoice-0",
            state=InvoiceState.APPROVED,
            invoiceNo="42",
            externalId="external-1",
            minEntryDate="2026-01-01",
            maxEntryDate="2026-01-31",
            entryDatePeriod="dates:2026-01-01...2026-01-31",
            minApprovedTime="2026-01-01T00:00:00Z",
            maxApprovedTime="2026-01-31T23:59:59Z",
            approvedTimePeriod="from:2026-01-01T00:00:00Z",
            minDueDate="2026-02-01",
            maxDueDate="2026-02-28",
            isPaid=False,
            currencyId="currency-1",
            recurringInvoiceId="recurring-1",
            amount=12.5,
            quoteId="quote-1",
            q="Ada",
        ),
    )

    assert isinstance(result, InvoicesListSuccess)
    assert result.invoices[0].model_dump() == {"id": "invoice-1", "invoiceNo": "42"}
    assert result.meta is not None
    assert result.meta.paging is not None
    assert result.meta.paging.page == 2
    assert result.meta.paging.page_size == 25
    assert requests[0].url.path == "/v2/invoices"
    assert requests[0].url.params == httpx.QueryParams(
        {
            "page": "2",
            "pageSize": "25",
            "include": "lines",
            "sortProperty": "entryDate",
            "sortDirection": "DESC",
            "organizationId": "organization-1",
            "contactId": "contact-1",
            "creditedInvoiceId": "invoice-0",
            "state": "approved",
            "invoiceNo": "42",
            "externalId": "external-1",
            "minEntryDate": "2026-01-01",
            "maxEntryDate": "2026-01-31",
            "entryDatePeriod": "dates:2026-01-01...2026-01-31",
            "minApprovedTime": "2026-01-01T00:00:00Z",
            "maxApprovedTime": "2026-01-31T23:59:59Z",
            "approvedTimePeriod": "from:2026-01-01T00:00:00Z",
            "minDueDate": "2026-02-01",
            "maxDueDate": "2026-02-28",
            "isPaid": "false",
            "currencyId": "currency-1",
            "recurringInvoiceId": "recurring-1",
            "amount": "12.5",
            "quoteId": "quote-1",
            "q": "Ada",
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
        "creditedInvoiceId",
        "state",
        "invoiceNo",
        "externalId",
        "minEntryDate",
        "maxEntryDate",
        "entryDatePeriod",
        "minApprovedTime",
        "maxApprovedTime",
        "approvedTimePeriod",
        "minDueDate",
        "maxDueDate",
        "isPaid",
        "currencyId",
        "recurringInvoiceId",
        "amount",
        "quoteId",
        "q",
    }


def test_list_maps_absent_optional_paging_without_fabricating_it() -> None:
    requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return httpx.Response(200, json={"invoices": []})

    result = list_invoices(
        make_client(httpx.MockTransport(handler)),
        InvoicesListRequest(),
    )

    assert isinstance(result, InvoicesListSuccess)
    assert result.invoices == []
    assert result.meta is None
    assert result.model_dump() == {"invoices": []}
    assert requests[0].url.params == httpx.QueryParams({"page": "1", "pageSize": "1000"})


@pytest.mark.parametrize(
    ("kwargs", "field"),
    [
        ({"page": 0}, "page"),
        ({"pageSize": 0}, "pageSize"),
        ({"pageSize": 1001}, "pageSize"),
        ({"sortProperty": "updatedTime"}, "sortProperty"),
        ({"sortDirection": "DOWN"}, "sortDirection"),
        ({"state": "paid"}, "state"),
        ({"q": ""}, "q"),
        ({"offset": 1}, "offset"),
        ({"email": "invoice@example.test"}, "email"),
    ],
)
def test_list_request_rejects_out_of_contract_paging_filters_and_enums(
    kwargs: dict[str, object], field: str
) -> None:
    with pytest.raises(ValidationError, match=field):
        InvoicesListRequest.model_validate(kwargs)


@pytest.mark.parametrize("error_code", ["AUTHENTICATION_REQUIRED", "OAUTH_INVALID_ACCESS_TOKEN"])
def test_documented_authentication_errors_remain_typed(error_code: str) -> None:
    result = get_invoice(
        make_client(
            httpx.MockTransport(lambda request: httpx.Response(401, json={"errorCode": error_code}))
        ),
        InvoicesGetRequest(id="invoice-1"),
    )

    assert isinstance(result, ToolError)
    assert result.code is StableErrorCode.AUTH_REQUIRED


@pytest.mark.asyncio
async def test_registers_only_the_two_typed_invoice_read_tools() -> None:
    server = FastMCP("invoices-test")
    register_invoice_read_tools(
        server,
        make_client(
            httpx.MockTransport(lambda request: httpx.Response(200, json={"invoices": []}))
        ),
    )

    tools = await server.list_tools()
    names = {tool.name for tool in tools}
    assert names == {"api_invoices_get", "api_invoices_list"}
    list_tool = await server.get_tool("api_invoices_list")
    assert list_tool is not None
    assert set(list_tool.parameters["properties"]) == {
        "page",
        "pageSize",
        "include",
        "sortProperty",
        "sortDirection",
        "organizationId",
        "contactId",
        "creditedInvoiceId",
        "state",
        "invoiceNo",
        "externalId",
        "minEntryDate",
        "maxEntryDate",
        "entryDatePeriod",
        "minApprovedTime",
        "maxApprovedTime",
        "approvedTimePeriod",
        "minDueDate",
        "maxDueDate",
        "isPaid",
        "currencyId",
        "recurringInvoiceId",
        "amount",
        "quoteId",
        "q",
    }
    assert "offset" not in list_tool.parameters["properties"]
    assert "email" not in list_tool.parameters["properties"]
    result = await server.call_tool("api_invoices_list", {"page": 1, "pageSize": 1000})
    assert result.structured_content == {"result": {"invoices": []}}
