"""Typed, read-only tools for documented Billy bills endpoints."""

from __future__ import annotations

from collections.abc import Mapping
from datetime import date
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
    """The two documented bill-list sort directions."""

    ASC = "ASC"
    DESC = "DESC"


class BillSortProperty(StrEnum):
    """The documented bill-list sort properties."""

    ENTRY_DATE = "entryDate"
    DUE_DATE = "dueDate"
    CREATED_TIME = "createdTime"
    LINE_DESCRIPTION = "lineDescription"
    AMOUNT = "amount"
    GROSS_AMOUNT = "grossAmount"
    BALANCE = "balance"
    CONTACT_NAME = "contact.name"
    VOUCHER_NO = "voucherNo"
    SUPPLIERS_INVOICE_NO = "suppliersInvoiceNo"
    ATTACHMENTS = "attachments"


class BillState(StrEnum):
    """The documented bill-list states."""

    DRAFT = "draft"
    APPROVED = "approved"
    VOIDED = "voided"


class BillsGetRequest(_RequestModel):
    """Input for retrieving one bill by its Billy identifier."""

    id: str = Field(min_length=1)
    include: str | None = None

    def query_params(self) -> dict[str, str]:
        """Return only the documented optional singular-read query field."""

        return {} if self.include is None else {"include": self.include}


class BillsListRequest(_RequestModel):
    """The complete documented query surface for the bills collection read."""

    page: int = Field(default=1, ge=1)
    page_size: int = Field(
        default=DEFAULT_PAGE_SIZE,
        alias="pageSize",
        serialization_alias="pageSize",
        ge=1,
        le=MAX_PAGE_SIZE,
    )
    include: str | None = None
    sort_property: BillSortProperty | None = Field(
        default=None, alias="sortProperty", serialization_alias="sortProperty"
    )
    sort_direction: SortDirection | None = Field(
        default=None, alias="sortDirection", serialization_alias="sortDirection"
    )
    organization_id: str | None = Field(
        default=None, alias="organizationId", serialization_alias="organizationId"
    )
    contact_id: str | None = Field(default=None, alias="contactId", serialization_alias="contactId")
    credited_bill_id: str | None = Field(
        default=None, alias="creditedBillId", serialization_alias="creditedBillId"
    )
    min_entry_date: date | None = Field(
        default=None, alias="minEntryDate", serialization_alias="minEntryDate"
    )
    max_entry_date: date | None = Field(
        default=None, alias="maxEntryDate", serialization_alias="maxEntryDate"
    )
    min_due_date: date | None = Field(
        default=None, alias="minDueDate", serialization_alias="minDueDate"
    )
    max_due_date: date | None = Field(
        default=None, alias="maxDueDate", serialization_alias="maxDueDate"
    )
    is_paid: bool | None = Field(default=None, alias="isPaid", serialization_alias="isPaid")
    has_attachments: bool | None = Field(
        default=None, alias="hasAttachments", serialization_alias="hasAttachments"
    )
    state: BillState | None = None
    currency_id: str | None = Field(
        default=None, alias="currencyId", serialization_alias="currencyId"
    )
    suppliers_invoice_no: str | None = Field(
        default=None, alias="suppliersInvoiceNo", serialization_alias="suppliersInvoiceNo"
    )
    is_bare: bool | None = Field(default=None, alias="isBare", serialization_alias="isBare")
    amount: float | None = None
    q: str | None = Field(default=None, min_length=1)

    def query_params(self) -> dict[str, str | int | float | bool]:
        """Serialise only the documented bill-list query fields."""

        return cast(
            dict[str, str | int | float | bool],
            self.model_dump(by_alias=True, exclude_none=True, mode="json"),
        )


class BillPayload(BaseModel):
    """An opaque JSON object returned by Billy for a bill."""

    model_config = ConfigDict(extra="allow")


class BillsPaging(BaseModel):
    """The documented optional bill-list paging fields."""

    model_config = ConfigDict(extra="ignore")

    page: int | None = None
    page_count: int | None = Field(default=None, alias="pageCount")
    page_size: int | None = Field(default=None, alias="pageSize")
    total: int | None = None
    first_url: str | None = Field(default=None, alias="firstUrl")
    previous_url: str | None = Field(default=None, alias="previousUrl")
    next_url: str | None = Field(default=None, alias="nextUrl")
    last_url: str | None = Field(default=None, alias="lastUrl")


class BillsMeta(BaseModel):
    """The documented optional metadata envelope for a bills response."""

    model_config = ConfigDict(extra="ignore")

    paging: BillsPaging | None = None


class BillsGetSuccess(BaseModel):
    """Successful response for ``api_bills_get``."""

    model_config = ConfigDict(extra="forbid")

    bill: BillPayload


class BillsListSuccess(BaseModel):
    """Successful response for ``api_bills_list``."""

    model_config = ConfigDict(extra="forbid")

    bills: list[BillPayload]
    meta: BillsMeta | None = None

    @model_serializer(mode="wrap")
    def serialize_optional_meta(self, handler: SerializerFunctionWrapHandler) -> dict[str, object]:
        """Keep absent upstream metadata absent in the tool result."""

        serialized = cast(dict[str, object], handler(self))
        return {key: value for key, value in serialized.items() if value is not None}


def get_bill(client: BillyHttpClient, request: BillsGetRequest) -> BillsGetSuccess | ToolError:
    """Retrieve one bill and map only its documented singular response root."""

    response = client.request(
        "GET",
        f"/bills/{quote(request.id, safe='')}",
        params=request.query_params() or None,
    )
    if isinstance(response, ToolError):
        return response
    payload = _response_mapping(response)
    if payload is None or not isinstance(payload.get("bill"), Mapping):
        return _unexpected_response("bill")
    try:
        return BillsGetSuccess(bill=BillPayload.model_validate(payload["bill"]))
    except ValidationError:
        return _unexpected_response("bill")


def list_bills(client: BillyHttpClient, request: BillsListRequest) -> BillsListSuccess | ToolError:
    """Retrieve bills and map their documented list root and optional paging."""

    response = client.request("GET", "/bills", params=request.query_params())
    if isinstance(response, ToolError):
        return response
    payload = _response_mapping(response)
    bills_value: object = None if payload is None else payload.get("bills")
    if not isinstance(bills_value, list):
        return _unexpected_response("bills")
    bills: list[Mapping[str, object]] = []
    for bill_value in cast(list[object], bills_value):
        bill = _object_mapping(bill_value)
        if bill is None:
            return _unexpected_response("bills")
        bills.append(bill)
    meta_value: object = None if payload is None else payload.get("meta")
    meta = _object_mapping(meta_value)
    if meta_value is not None and meta is None:
        return _unexpected_response("meta")
    try:
        return BillsListSuccess(
            bills=[BillPayload.model_validate(bill) for bill in bills],
            meta=None if meta is None else BillsMeta.model_validate(meta),
        )
    except ValidationError:
        return _unexpected_response("bills")


def register_bill_read_tools(server: FastMCP, client: BillyHttpClient) -> None:
    """Register the two implemented bill reads without changing root server wiring."""

    def api_bills_get(
        id: str = Field(min_length=1), include: str | None = None
    ) -> BillsGetSuccess | ToolError:
        """Read one Billy bill by identifier."""

        return get_bill(client, BillsGetRequest(id=id, include=include))

    def api_bills_list(
        page: int = Field(default=1, ge=1),
        pageSize: int = Field(default=DEFAULT_PAGE_SIZE, ge=1, le=MAX_PAGE_SIZE),
        include: str | None = None,
        sortProperty: BillSortProperty | None = None,
        sortDirection: SortDirection | None = None,
        organizationId: str | None = None,
        contactId: str | None = None,
        creditedBillId: str | None = None,
        minEntryDate: date | None = None,
        maxEntryDate: date | None = None,
        minDueDate: date | None = None,
        maxDueDate: date | None = None,
        isPaid: bool | None = None,
        hasAttachments: bool | None = None,
        state: BillState | None = None,
        currencyId: str | None = None,
        suppliersInvoiceNo: str | None = None,
        isBare: bool | None = None,
        amount: float | None = None,
        q: str | None = Field(default=None, min_length=1),
    ) -> BillsListSuccess | ToolError:
        """Read Billy bills with documented paging, filters, and sorting only."""

        return list_bills(
            client,
            BillsListRequest(
                page=page,
                pageSize=pageSize,
                include=include,
                sortProperty=sortProperty,
                sortDirection=sortDirection,
                organizationId=organizationId,
                contactId=contactId,
                creditedBillId=creditedBillId,
                minEntryDate=minEntryDate,
                maxEntryDate=maxEntryDate,
                minDueDate=minDueDate,
                maxDueDate=maxDueDate,
                isPaid=isPaid,
                hasAttachments=hasAttachments,
                state=state,
                currencyId=currencyId,
                suppliersInvoiceNo=suppliersInvoiceNo,
                isBare=isBare,
                amount=amount,
                q=q,
            ),
        )

    server.tool(name="api_bills_get", description="Read one Billy bill.")(api_bills_get)
    server.tool(
        name="api_bills_list",
        description="Read Billy bills with documented paging, filters, and sorting.",
    )(api_bills_list)


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
        message="Billy API response did not contain the documented bills root.",
        details={"expected_root": root},
    )
