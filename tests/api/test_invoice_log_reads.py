"""Transport-only contract tests for the list-only Billy invoice log tool."""

from __future__ import annotations

import asyncio
from collections.abc import Callable, Iterator
from dataclasses import dataclass
from typing import cast

import httpx
import pytest
from fastmcp import FastMCP
from fastmcp.tools.base import ToolResult
from pydantic import ValidationError

from billy_mcp.api.invoice_log_reads import (
    InvoiceLogReadService,
    InvoiceLogsListRequest,
    InvoiceLogsListSuccess,
    register_invoice_log_read_tools,
)
from billy_mcp.client import BillyHttpClient
from billy_mcp.models import StableErrorCode, ToolError

MockHandler = Callable[[httpx.Request], httpx.Response]


@dataclass
class RegisteredInvoiceLogTools:
    server: FastMCP
    client: BillyHttpClient
    requests: list[httpx.Request]


@pytest.fixture
def registered_invoice_log_tools() -> Iterator[RegisteredInvoiceLogTools]:
    """Provide the single registered tool on a deterministic in-process transport."""

    requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        assert request.method == "GET"
        assert request.url.path == "/v2/invoiceLogs"
        return httpx.Response(
            200,
            json={
                "invoiceLogs": [
                    {
                        "type": "received",
                        "message": "Delivered to the recipient inbox.",
                        "messageKey": "delivery.received",
                        "eventTime": "2026-07-30T16:00:00Z",
                        "upstreamDeliveryContext": {"channel": "einvoice"},
                    }
                ]
            },
        )

    client = BillyHttpClient(
        lambda: "fixture-token",
        transport=httpx.MockTransport(handler),
        max_read_retries=0,
    )
    server = FastMCP("invoice-log-contract-test")
    register_invoice_log_read_tools(server, client)
    try:
        yield RegisteredInvoiceLogTools(server=server, client=client, requests=requests)
    finally:
        client.close()


def test_list_uses_the_complete_frozen_query_and_preserves_opaque_entries(
    registered_invoice_log_tools: RegisteredInvoiceLogTools,
) -> None:
    result = InvoiceLogReadService(registered_invoice_log_tools.client).invoice_logs_list(
        InvoiceLogsListRequest(invoiceId="invoice-1", organizationId="organization-1")
    )

    assert isinstance(result, InvoiceLogsListSuccess)
    assert result.invoiceLogs[0].model_dump() == {
        "type": "received",
        "message": "Delivered to the recipient inbox.",
        "messageKey": "delivery.received",
        "eventTime": "2026-07-30T16:00:00Z",
        "upstreamDeliveryContext": {"channel": "einvoice"},
    }
    request = registered_invoice_log_tools.requests[0]
    assert request.url.params == httpx.QueryParams(
        {
            "invoiceId": "invoice-1",
            "organizationId": "organization-1",
            "sortProperty": "eventTime",
            "sortDirection": "DESC",
        }
    )
    assert set(request.url.params) == {
        "invoiceId",
        "organizationId",
        "sortProperty",
        "sortDirection",
    }


@pytest.mark.parametrize(
    ("arguments", "field"),
    [
        ({"invoiceId": "", "organizationId": "organization-1"}, "invoiceId"),
        ({"invoiceId": "invoice-1", "organizationId": ""}, "organizationId"),
        ({"organizationId": "organization-1"}, "invoiceId"),
        ({"invoiceId": "invoice-1"}, "organizationId"),
        ({"invoiceId": "invoice-1", "organizationId": "organization-1", "page": 1}, "page"),
        (
            {"invoiceId": "invoice-1", "organizationId": "organization-1", "pageSize": 25},
            "pageSize",
        ),
        (
            {
                "invoiceId": "invoice-1",
                "organizationId": "organization-1",
                "sortProperty": "createdTime",
            },
            "sortProperty",
        ),
        (
            {
                "invoiceId": "invoice-1",
                "organizationId": "organization-1",
                "sortDirection": "ASC",
            },
            "sortDirection",
        ),
        ({"invoiceId": "invoice-1", "organizationId": "organization-1", "q": "delivery"}, "q"),
    ],
)
def test_request_rejects_missing_invalid_and_undeclared_controls(
    arguments: dict[str, object], field: str
) -> None:
    with pytest.raises(ValidationError) as failure:
        InvoiceLogsListRequest.model_validate(arguments)

    assert failure.value.errors()[0]["loc"] == (field,)


@pytest.mark.parametrize(
    "payload",
    [
        {},
        {"invoiceLogs": {}},
        {"invoiceLogs": ["not-an-object"]},
        ["not-an-envelope"],
    ],
)
def test_malformed_documented_root_or_entry_returns_typed_billy_error(
    payload: object,
) -> None:
    client = BillyHttpClient(
        lambda: "fixture-token",
        transport=httpx.MockTransport(lambda request: httpx.Response(200, json=payload)),
        max_read_retries=0,
    )
    try:
        result = InvoiceLogReadService(client).invoice_logs_list(
            InvoiceLogsListRequest(invoiceId="invoice-1", organizationId="organization-1")
        )
    finally:
        client.close()

    assert isinstance(result, ToolError)
    assert result.code == StableErrorCode.BILLY_ERROR
    assert result.details == {"expected_root": "invoiceLogs"}


@pytest.mark.parametrize("upstream_code", ["AUTHENTICATION_REQUIRED", "OAUTH_INVALID_ACCESS_TOKEN"])
def test_list_preserves_typed_authentication_errors(upstream_code: str) -> None:
    client = BillyHttpClient(
        lambda: "invalid-token",
        transport=httpx.MockTransport(
            lambda request: httpx.Response(401, json={"errorCode": upstream_code})
        ),
        max_read_retries=0,
    )
    try:
        result = InvoiceLogReadService(client).invoice_logs_list(
            InvoiceLogsListRequest(invoiceId="invoice-1", organizationId="organization-1")
        )
    finally:
        client.close()

    assert isinstance(result, ToolError)
    assert result.code == StableErrorCode.AUTH_REQUIRED
    assert result.message == "Billy API authentication is required."


def test_registration_exposes_exactly_one_typed_tool_and_structured_result(
    registered_invoice_log_tools: RegisteredInvoiceLogTools,
) -> None:
    tools = {
        tool.name: tool for tool in asyncio.run(registered_invoice_log_tools.server.list_tools())
    }

    assert set(tools) == {"api_invoice_logs_list"}
    parameters = tools["api_invoice_logs_list"].parameters
    assert set(parameters["properties"]) == {
        "invoiceId",
        "organizationId",
        "sortProperty",
        "sortDirection",
    }
    assert parameters["required"] == ["invoiceId", "organizationId"]
    assert parameters["properties"]["sortProperty"]["default"] == "eventTime"
    assert parameters["properties"]["sortDirection"]["default"] == "DESC"
    assert parameters["additionalProperties"] is False

    result = asyncio.run(
        registered_invoice_log_tools.server.call_tool(
            "api_invoice_logs_list",
            {"invoiceId": "invoice-1", "organizationId": "organization-1"},
        )
    )

    assert isinstance(result, ToolResult)
    assert result.is_error is False
    assert result.structured_content == {
        "result": {
            "invoiceLogs": [
                {
                    "type": "received",
                    "message": "Delivered to the recipient inbox.",
                    "messageKey": "delivery.received",
                    "eventTime": "2026-07-30T16:00:00Z",
                    "upstreamDeliveryContext": {"channel": "einvoice"},
                }
            ]
        }
    }
    structured_content = result.structured_content
    assert isinstance(structured_content, dict)
    payload = cast(dict[str, object], structured_content["result"])
    invoice_logs = cast(list[dict[str, object]], payload["invoiceLogs"])
    assert invoice_logs[0]["type"] == "received"
