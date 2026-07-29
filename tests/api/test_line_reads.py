"""Contract tests for typed, read-only Billy document-line API tools."""

from __future__ import annotations

import asyncio

import httpx
import pytest
from fastmcp import FastMCP
from pydantic import ValidationError

from billy_mcp.api.line_reads import (
    BillLineGetSuccess,
    BillLineListSuccess,
    DaybookTransactionLineGetSuccess,
    DaybookTransactionLineListSuccess,
    InvoiceLineGetSuccess,
    InvoiceLineListSuccess,
    LineGetRequest,
    LineListRequest,
    LineReadService,
    SortDirection,
    register_line_read_tools,
)
from billy_mcp.client import BillyHttpClient
from billy_mcp.models import StableErrorCode, ToolError


def make_client(handler: httpx.MockTransport) -> BillyHttpClient:
    """Create a token-backed locked client against an in-process mock transport."""

    return BillyHttpClient(lambda: "test-token", transport=handler)


def test_singular_reads_use_documented_paths_encode_ids_and_map_roots() -> None:
    requests: list[httpx.Request] = []
    responses: dict[str, dict[str, object]] = {
        "/v2/invoiceLines/invoice 1": {"invoiceLine": {"id": "invoice 1", "amount": 10}},
        "/v2/billLines/bill 1": {"billLine": {"id": "bill 1", "amount": 20}},
        "/v2/daybookTransactionLines/transaction 1": {
            "daybookTransactionLine": {"id": "transaction 1", "side": "debit"}
        },
    }

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return httpx.Response(200, json=responses[request.url.path])

    service = LineReadService(make_client(httpx.MockTransport(handler)))
    invoice = service.invoice_lines_get(LineGetRequest(id="invoice 1", include="invoice"))
    bill = service.bill_lines_get(LineGetRequest(id="bill 1", include="bill"))
    transaction = service.daybook_transaction_lines_get(
        LineGetRequest(id="transaction 1", include="daybookTransaction")
    )

    assert isinstance(invoice, InvoiceLineGetSuccess)
    assert invoice.invoiceLine.model_dump() == {"id": "invoice 1", "amount": 10}
    assert isinstance(bill, BillLineGetSuccess)
    assert bill.billLine.model_dump() == {"id": "bill 1", "amount": 20}
    assert isinstance(transaction, DaybookTransactionLineGetSuccess)
    assert transaction.daybookTransactionLine.model_dump() == {
        "id": "transaction 1",
        "side": "debit",
    }
    assert [str(request.url) for request in requests] == [
        "https://api.billysbilling.com/v2/invoiceLines/invoice%201?include=invoice",
        "https://api.billysbilling.com/v2/billLines/bill%201?include=bill",
        "https://api.billysbilling.com/v2/daybookTransactionLines/transaction%201?include=daybookTransaction",
    ]


def test_collection_reads_use_only_global_query_fields_and_preserve_optional_paging() -> None:
    requests: list[httpx.Request] = []
    responses: dict[str, dict[str, object]] = {
        "/v2/invoiceLines": {
            "invoiceLines": [{"id": "invoice-line-1", "amount": 10}],
            "meta": {"paging": {"page": 2, "pageCount": 3, "pageSize": 25, "total": 70}},
        },
        "/v2/billLines": {"billLines": [{"id": "bill-line-1", "amount": 20}]},
        "/v2/daybookTransactionLines": {
            "daybookTransactionLines": [{"id": "transaction-line-1", "side": "credit"}]
        },
    }

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return httpx.Response(200, json=responses[request.url.path])

    request = LineListRequest(
        page=2,
        pageSize=25,
        include="invoice,bill",
        sortProperty="priority",
        sortDirection=SortDirection.DESC,
    )
    service = LineReadService(make_client(httpx.MockTransport(handler)))
    invoice = service.invoice_lines_list(request)
    bill = service.bill_lines_list(request)
    transaction = service.daybook_transaction_lines_list(request)

    assert isinstance(invoice, InvoiceLineListSuccess)
    assert invoice.invoiceLines[0].model_dump() == {"id": "invoice-line-1", "amount": 10}
    assert invoice.meta is not None
    assert invoice.meta.paging is not None
    assert invoice.meta.paging.model_dump() == {
        "page": 2,
        "page_count": 3,
        "page_size": 25,
        "total": 70,
        "first_url": None,
        "previous_url": None,
        "next_url": None,
        "last_url": None,
    }
    assert isinstance(bill, BillLineListSuccess)
    assert bill.billLines[0].model_dump() == {"id": "bill-line-1", "amount": 20}
    assert bill.meta is None
    assert bill.model_dump() == {"billLines": [{"id": "bill-line-1", "amount": 20}]}
    assert isinstance(transaction, DaybookTransactionLineListSuccess)
    assert transaction.daybookTransactionLines[0].model_dump() == {
        "id": "transaction-line-1",
        "side": "credit",
    }
    assert transaction.meta is None
    assert [request.url.path for request in requests] == [
        "/v2/invoiceLines",
        "/v2/billLines",
        "/v2/daybookTransactionLines",
    ]
    expected_params = httpx.QueryParams(
        {
            "page": "2",
            "pageSize": "25",
            "include": "invoice,bill",
            "sortProperty": "priority",
            "sortDirection": "DESC",
        }
    )
    assert all(request.url.params == expected_params for request in requests)
    assert all(set(request.url.params) == set(expected_params) for request in requests)


def test_collection_reads_keep_default_paging_and_absent_meta_optional() -> None:
    requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return httpx.Response(200, json={"invoiceLines": []})

    result = LineReadService(make_client(httpx.MockTransport(handler))).invoice_lines_list(
        LineListRequest()
    )

    assert isinstance(result, InvoiceLineListSuccess)
    assert result.invoiceLines == []
    assert result.meta is None
    assert result.model_dump() == {"invoiceLines": []}
    assert requests[0].url.params == httpx.QueryParams({"page": "1", "pageSize": "1000"})


def test_collection_reads_preserve_an_empty_meta_without_fabricating_paging() -> None:
    result = LineReadService(
        make_client(
            httpx.MockTransport(
                lambda request: httpx.Response(200, json={"billLines": [], "meta": {}})
            )
        )
    ).bill_lines_list(LineListRequest())

    assert isinstance(result, BillLineListSuccess)
    assert result.meta is not None
    assert result.meta.paging is None
    assert result.model_dump() == {"billLines": [], "meta": {}}


@pytest.mark.parametrize(
    ("input_type", "values", "field"),
    [
        (LineGetRequest, {"id": "line-1", "page": 1}, "page"),
        (LineGetRequest, {"id": "line-1", "include": ""}, "include"),
        (LineListRequest, {"page": 0}, "page"),
        (LineListRequest, {"pageSize": 0}, "pageSize"),
        (LineListRequest, {"pageSize": 1001}, "pageSize"),
        (LineListRequest, {"sortDirection": "DOWN"}, "sortDirection"),
        (LineListRequest, {"include": ""}, "include"),
        (LineListRequest, {"offset": 10}, "offset"),
        (LineListRequest, {"invoiceId": "invoice-1"}, "invoiceId"),
        (LineListRequest, {"billId": "bill-1"}, "billId"),
        (LineListRequest, {"daybookTransactionId": "transaction-1"}, "daybookTransactionId"),
        (LineListRequest, {"unexpected": "value"}, "unexpected"),
    ],
)
def test_requests_reject_undocumented_fields_and_invalid_boundaries(
    input_type: type[LineGetRequest] | type[LineListRequest],
    values: dict[str, object],
    field: str,
) -> None:
    with pytest.raises(ValidationError, match=field):
        input_type.model_validate(values)


@pytest.mark.parametrize("error_code", ["AUTHENTICATION_REQUIRED", "OAUTH_INVALID_ACCESS_TOKEN"])
def test_documented_authentication_errors_remain_typed(error_code: str) -> None:
    service = LineReadService(
        make_client(
            httpx.MockTransport(lambda request: httpx.Response(401, json={"errorCode": error_code}))
        )
    )
    results = [
        service.invoice_lines_get(LineGetRequest(id="invoice-line-1")),
        service.invoice_lines_list(LineListRequest()),
        service.bill_lines_get(LineGetRequest(id="bill-line-1")),
        service.bill_lines_list(LineListRequest()),
        service.daybook_transaction_lines_get(LineGetRequest(id="transaction-line-1")),
        service.daybook_transaction_lines_list(LineListRequest()),
    ]

    assert all(isinstance(result, ToolError) for result in results)
    assert {result.code for result in results if isinstance(result, ToolError)} == {
        StableErrorCode.AUTH_REQUIRED
    }


def test_registers_exactly_six_typed_document_line_read_tools() -> None:
    server = FastMCP("document-line-test")

    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/v2/invoiceLines/invoice-line-1":
            return httpx.Response(200, json={"invoiceLine": {"id": "invoice-line-1"}})
        return httpx.Response(200, json={"invoiceLines": []})

    register_line_read_tools(
        server,
        make_client(httpx.MockTransport(handler)),
    )

    tools = {tool.name: tool for tool in asyncio.run(server.list_tools())}

    assert set(tools) == {
        "api_invoice_lines_get",
        "api_invoice_lines_list",
        "api_bill_lines_get",
        "api_bill_lines_list",
        "api_daybook_transaction_lines_get",
        "api_daybook_transaction_lines_list",
    }
    for name in {
        "api_invoice_lines_list",
        "api_bill_lines_list",
        "api_daybook_transaction_lines_list",
    }:
        assert set(tools[name].parameters["properties"]) == {
            "page",
            "pageSize",
            "include",
            "sortProperty",
            "sortDirection",
        }
        assert "offset" not in tools[name].parameters["properties"]
        assert "invoiceId" not in tools[name].parameters["properties"]
        assert "billId" not in tools[name].parameters["properties"]
        assert "daybookTransactionId" not in tools[name].parameters["properties"]
    for name in {
        "api_invoice_lines_get",
        "api_bill_lines_get",
        "api_daybook_transaction_lines_get",
    }:
        assert set(tools[name].parameters["properties"]) == {"id", "include"}
    assert asyncio.run(
        server.call_tool("api_invoice_lines_get", {"id": "invoice-line-1"})
    ).structured_content == {"result": {"invoiceLine": {"id": "invoice-line-1"}}}
    assert asyncio.run(
        server.call_tool("api_invoice_lines_list", {"page": 1, "pageSize": 1000})
    ).structured_content == {"result": {"invoiceLines": []}}
