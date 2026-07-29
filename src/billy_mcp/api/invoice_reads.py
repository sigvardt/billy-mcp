"""Typed, read-only tools for documented Billy invoices endpoints."""

from __future__ import annotations

from collections.abc import Mapping
from enum import StrEnum
from typing import cast
from urllib.parse import quote

from fastmcp import FastMCP
from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    SerializerFunctionWrapHandler,
    ValidationError,
    model_serializer,
)

from billy_mcp.client import DEFAULT_PAGE_SIZE, MAX_PAGE_SIZE, BillyHttpClient, BillyResponse
from billy_mcp.models import StableErrorCode, ToolError


class _RequestModel(BaseModel):
    """Reject undeclared API inputs while accepting documented wire aliases."""

    model_config = ConfigDict(
        extra="forbid", strict=True, validate_by_alias=True, validate_by_name=True
    )


class SortDirection(StrEnum):
    """The documented invoice-list sort directions."""

    ASC = "ASC"
    DESC = "DESC"


class InvoiceSortProperty(StrEnum):
    """The frozen documented invoice-list sort-property values."""

    ENTRY_DATE = "entryDate"
    DUE_DATE = "dueDate"
    CREATED_TIME = "createdTime"
    INVOICE_NO = "invoiceNo"
    LINE_DESCRIPTION = "lineDescription"
    AMOUNT = "amount"
    GROSS_AMOUNT = "grossAmount"
    BALANCE = "balance"
    CONTACT_NAME = "contact.name"
    APPROVED_TIME = "approvedTime"
    ORDER_NO = "orderNo"


class InvoiceState(StrEnum):
    """The frozen documented invoice states."""

    DRAFT = "draft"
    APPROVED = "approved"
    VOIDED = "voided"


class InvoicesGetRequest(_RequestModel):
    """Input for retrieving one invoice by its Billy identifier."""

    id: str = Field(min_length=1)
    include: str | None = None

    def query_params(self) -> dict[str, str]:
        """Return only the documented optional include query field."""

        return {} if self.include is None else {"include": self.include}


class InvoicesListRequest(_RequestModel):
    """Input for the frozen documented invoice collection read."""

    page: int = Field(default=1, ge=1)
    page_size: int = Field(
        default=DEFAULT_PAGE_SIZE,
        alias="pageSize",
        serialization_alias="pageSize",
        ge=1,
        le=MAX_PAGE_SIZE,
    )
    include: str | None = None
    sort_property: InvoiceSortProperty | None = Field(
        default=None, alias="sortProperty", serialization_alias="sortProperty"
    )
    sort_direction: SortDirection | None = Field(
        default=None, alias="sortDirection", serialization_alias="sortDirection"
    )
    organization_id: str | None = Field(
        default=None, alias="organizationId", serialization_alias="organizationId"
    )
    contact_id: str | None = Field(default=None, alias="contactId", serialization_alias="contactId")
    credited_invoice_id: str | None = Field(
        default=None, alias="creditedInvoiceId", serialization_alias="creditedInvoiceId"
    )
    state: InvoiceState | None = None
    invoice_no: str | None = Field(default=None, alias="invoiceNo", serialization_alias="invoiceNo")
    external_id: str | None = Field(
        default=None, alias="externalId", serialization_alias="externalId"
    )
    min_entry_date: str | None = Field(
        default=None, alias="minEntryDate", serialization_alias="minEntryDate"
    )
    max_entry_date: str | None = Field(
        default=None, alias="maxEntryDate", serialization_alias="maxEntryDate"
    )
    entry_date_period: str | None = Field(
        default=None, alias="entryDatePeriod", serialization_alias="entryDatePeriod"
    )
    min_approved_time: str | None = Field(
        default=None, alias="minApprovedTime", serialization_alias="minApprovedTime"
    )
    max_approved_time: str | None = Field(
        default=None, alias="maxApprovedTime", serialization_alias="maxApprovedTime"
    )
    approved_time_period: str | None = Field(
        default=None, alias="approvedTimePeriod", serialization_alias="approvedTimePeriod"
    )
    min_due_date: str | None = Field(
        default=None, alias="minDueDate", serialization_alias="minDueDate"
    )
    max_due_date: str | None = Field(
        default=None, alias="maxDueDate", serialization_alias="maxDueDate"
    )
    is_paid: bool | None = Field(default=None, alias="isPaid", serialization_alias="isPaid")
    currency_id: str | None = Field(
        default=None, alias="currencyId", serialization_alias="currencyId"
    )
    recurring_invoice_id: str | None = Field(
        default=None, alias="recurringInvoiceId", serialization_alias="recurringInvoiceId"
    )
    amount: float | None = None
    quote_id: str | None = Field(default=None, alias="quoteId", serialization_alias="quoteId")
    q: str | None = None

    def query_params(self) -> dict[str, str | int | float | bool]:
        """Serialise only the documented invoice query surface."""

        return cast(
            dict[str, str | int | float | bool],
            self.model_dump(by_alias=True, exclude_none=True, mode="json"),
        )


class InvoicePayload(BaseModel):
    """An opaque JSON object returned by Billy for an invoice."""

    model_config = ConfigDict(extra="allow")


class InvoicesPaging(BaseModel):
    """The documented optional invoice collection paging fields."""

    model_config = ConfigDict(extra="ignore")

    page: int | None = None
    page_count: int | None = Field(default=None, alias="pageCount")
    page_size: int | None = Field(default=None, alias="pageSize")
    total: int | None = None
    first_url: str | None = Field(default=None, alias="firstUrl")
    previous_url: str | None = Field(default=None, alias="previousUrl")
    next_url: str | None = Field(default=None, alias="nextUrl")
    last_url: str | None = Field(default=None, alias="lastUrl")


class InvoicesMeta(BaseModel):
    """The subset of Billy list metadata documented for invoices."""

    model_config = ConfigDict(extra="ignore")

    paging: InvoicesPaging | None = None


class InvoicesGetSuccess(BaseModel):
    """Successful response for ``api_invoices_get``."""

    model_config = ConfigDict(extra="forbid")

    invoice: InvoicePayload


class InvoicesListSuccess(BaseModel):
    """Successful response for ``api_invoices_list``."""

    model_config = ConfigDict(extra="forbid")

    invoices: list[InvoicePayload]
    meta: InvoicesMeta | None = None

    @model_serializer(mode="wrap")
    def serialize_optional_meta(self, handler: SerializerFunctionWrapHandler) -> dict[str, object]:
        """Keep an absent upstream paging root absent in the tool result."""

        serialized = cast(dict[str, object], handler(self))
        return {key: value for key, value in serialized.items() if value is not None}


def get_invoice(
    client: BillyHttpClient, request: InvoicesGetRequest
) -> InvoicesGetSuccess | ToolError:
    """Retrieve one invoice and map only its documented singular response root."""

    response = client.request(
        "GET",
        f"/invoices/{quote(request.id, safe='')}",
        params=request.query_params() or None,
    )
    if isinstance(response, ToolError):
        return response
    payload = _response_mapping(response)
    if payload is None or not isinstance(payload.get("invoice"), Mapping):
        return _unexpected_response("invoice")
    try:
        return InvoicesGetSuccess(invoice=InvoicePayload.model_validate(payload["invoice"]))
    except ValidationError:
        return _unexpected_response("invoice")


def list_invoices(
    client: BillyHttpClient, request: InvoicesListRequest
) -> InvoicesListSuccess | ToolError:
    """Retrieve invoices and map their documented list root and optional paging."""

    response = client.request("GET", "/invoices", params=request.query_params())
    if isinstance(response, ToolError):
        return response
    payload = _response_mapping(response)
    invoices_value: object = None if payload is None else payload.get("invoices")
    if not isinstance(invoices_value, list):
        return _unexpected_response("invoices")
    invoices: list[Mapping[str, object]] = []
    for invoice_value in cast(list[object], invoices_value):
        invoice = _object_mapping(invoice_value)
        if invoice is None:
            return _unexpected_response("invoices")
        invoices.append(invoice)
    meta_value: object = None if payload is None else payload.get("meta")
    meta = _object_mapping(meta_value)
    if meta_value is not None and meta is None:
        return _unexpected_response("meta")
    try:
        return InvoicesListSuccess(
            invoices=[InvoicePayload.model_validate(invoice) for invoice in invoices],
            meta=None if meta is None else InvoicesMeta.model_validate(meta),
        )
    except ValidationError:
        return _unexpected_response("invoices")


def register_invoice_read_tools(server: FastMCP, client: BillyHttpClient) -> None:
    """Register the two implemented invoice reads without changing root server wiring."""

    def api_invoices_get(
        id: str = Field(min_length=1), include: str | None = None
    ) -> InvoicesGetSuccess | ToolError:
        """Read one Billy invoice by identifier."""

        return get_invoice(client, InvoicesGetRequest(id=id, include=include))

    def api_invoices_list(
        page: int = Field(default=1, ge=1),
        pageSize: int = Field(default=DEFAULT_PAGE_SIZE, ge=1, le=MAX_PAGE_SIZE),
        include: str | None = None,
        sortProperty: InvoiceSortProperty | None = None,
        sortDirection: SortDirection | None = None,
        organizationId: str | None = None,
        contactId: str | None = None,
        creditedInvoiceId: str | None = None,
        state: InvoiceState | None = None,
        invoiceNo: str | None = None,
        externalId: str | None = None,
        minEntryDate: str | None = None,
        maxEntryDate: str | None = None,
        entryDatePeriod: str | None = None,
        minApprovedTime: str | None = None,
        maxApprovedTime: str | None = None,
        approvedTimePeriod: str | None = None,
        minDueDate: str | None = None,
        maxDueDate: str | None = None,
        isPaid: bool | None = None,
        currencyId: str | None = None,
        recurringInvoiceId: str | None = None,
        amount: float | None = None,
        quoteId: str | None = None,
        q: str | None = None,
    ) -> InvoicesListSuccess | ToolError:
        """Read Billy invoices with frozen paging, filters, and sorting only."""

        return list_invoices(
            client,
            InvoicesListRequest(
                page=page,
                pageSize=pageSize,
                include=include,
                sortProperty=sortProperty,
                sortDirection=sortDirection,
                organizationId=organizationId,
                contactId=contactId,
                creditedInvoiceId=creditedInvoiceId,
                state=state,
                invoiceNo=invoiceNo,
                externalId=externalId,
                minEntryDate=minEntryDate,
                maxEntryDate=maxEntryDate,
                entryDatePeriod=entryDatePeriod,
                minApprovedTime=minApprovedTime,
                maxApprovedTime=maxApprovedTime,
                approvedTimePeriod=approvedTimePeriod,
                minDueDate=minDueDate,
                maxDueDate=maxDueDate,
                isPaid=isPaid,
                currencyId=currencyId,
                recurringInvoiceId=recurringInvoiceId,
                amount=amount,
                quoteId=quoteId,
                q=q,
            ),
        )

    server.tool(name="api_invoices_get", description="Read one Billy invoice.")(api_invoices_get)
    server.tool(
        name="api_invoices_list",
        description="Read Billy invoices with documented paging, filters, and sorting.",
    )(api_invoices_list)


def _response_mapping(response: BillyResponse) -> Mapping[str, object] | None:
    """Narrow a successful client payload to the JSON object expected by these reads."""

    return _object_mapping(response.data)


def _object_mapping(value: object) -> Mapping[str, object] | None:
    """Narrow untyped decoded JSON to the object shape expected by the models."""

    if not isinstance(value, Mapping):
        return None
    return cast(Mapping[str, object], value)


def _unexpected_response(root: str) -> ToolError:
    """Avoid inventing a success shape when Billy omits a documented response root."""

    return ToolError(
        code=StableErrorCode.BILLY_ERROR,
        message="Billy API response did not contain the documented invoices root.",
        details={"expected_root": root},
    )
