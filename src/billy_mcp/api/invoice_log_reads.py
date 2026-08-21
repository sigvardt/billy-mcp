"""Typed, read-only tools for the documented Billy invoice log collection."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Literal, cast

from fastmcp import FastMCP
from pydantic import BaseModel, ConfigDict, Field, ValidationError

from billy_mcp.client import BillyHttpClient, BillyResponse
from billy_mcp.models import StableErrorCode, ToolError


class _StrictInput(BaseModel):
    """Forbid every query control outside the frozen documented sample."""

    model_config = ConfigDict(extra="forbid")


class InvoiceLogsListRequest(_StrictInput):
    """The complete frozen query shape for the invoice log collection."""

    invoiceId: str = Field(min_length=1)
    organizationId: str = Field(min_length=1)
    sortProperty: Literal["eventTime"] = "eventTime"
    sortDirection: Literal["DESC"] = "DESC"


class InvoiceLogEntry(BaseModel):
    """An opaque documented invoice log entry, preserving upstream additions."""

    model_config = ConfigDict(extra="allow")


class InvoiceLogsListSuccess(BaseModel):
    """Mapped success envelope for ``api_invoice_logs_list``."""

    model_config = ConfigDict(extra="forbid")

    invoiceLogs: list[InvoiceLogEntry]


class InvoiceLogReadService:
    """List-only invoice log handler over the locked Billy HTTP client."""

    def __init__(self, client: BillyHttpClient) -> None:
        self._client = client

    def invoice_logs_list(
        self, request: InvoiceLogsListRequest
    ) -> InvoiceLogsListSuccess | ToolError:
        """List invoice delivery log entries using only the documented query."""

        entries = _invoice_logs_from_response(
            self._client.request(
                "GET",
                "/invoiceLogs",
                params={
                    "invoiceId": request.invoiceId,
                    "organizationId": request.organizationId,
                    "sortProperty": request.sortProperty,
                    "sortDirection": request.sortDirection,
                },
            )
        )
        if isinstance(entries, ToolError):
            return entries
        return InvoiceLogsListSuccess(invoiceLogs=entries)


def register_invoice_log_read_tools(server: FastMCP, client: BillyHttpClient) -> None:
    """Register exactly the documented list-only invoice log read tool."""

    service = InvoiceLogReadService(client)

    def api_invoice_logs_list(
        invoiceId: str = Field(min_length=1),
        organizationId: str = Field(min_length=1),
        sortProperty: Literal["eventTime"] = "eventTime",
        sortDirection: Literal["DESC"] = "DESC",
    ) -> InvoiceLogsListSuccess | ToolError:
        """List Billy invoice delivery log entries in documented event-time order."""

        return service.invoice_logs_list(
            InvoiceLogsListRequest(
                invoiceId=invoiceId,
                organizationId=organizationId,
                sortProperty=sortProperty,
                sortDirection=sortDirection,
            )
        )

    server.tool(name="api_invoice_logs_list", description="List Billy invoice delivery logs.")(
        api_invoice_logs_list
    )


def _invoice_logs_from_response(
    response: BillyResponse | ToolError,
) -> list[InvoiceLogEntry] | ToolError:
    """Map only the documented ``invoiceLogs`` array root."""

    if isinstance(response, ToolError):
        return response
    data = response.data
    if not isinstance(data, Mapping):
        return _invalid_response()
    payload = cast(Mapping[str, object], data)
    values = payload.get("invoiceLogs")
    if not isinstance(values, list):
        return _invalid_response()
    entries: list[InvoiceLogEntry] = []
    for value in cast(list[object], values):
        if not isinstance(value, Mapping):
            return _invalid_response()
        try:
            entries.append(InvoiceLogEntry.model_validate(value))
        except ValidationError:
            return _invalid_response()
    return entries


def _invalid_response() -> ToolError:
    return ToolError(
        code=StableErrorCode.BILLY_ERROR,
        message="Billy API response did not contain the documented invoiceLogs array.",
        details={"expected_root": "invoiceLogs"},
    )
