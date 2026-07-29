"""Typed, read-only tools for frozen contact-balance and invoice extensions."""

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


class SortDirection(StrEnum):
    """The two documented collection sort directions."""

    ASC = "ASC"
    DESC = "DESC"


class _ReadRequest(BaseModel):
    """Strictly validate the deliberately small frozen read surface."""

    model_config = ConfigDict(
        extra="forbid", strict=True, validate_by_alias=True, validate_by_name=True
    )


class BalanceInvoiceExtensionGetRequest(_ReadRequest):
    """Documented inputs shared by each singular read."""

    id: str = Field(min_length=1)
    include: str | None = Field(default=None, min_length=1)


class BalanceInvoiceExtensionListRequest(_ReadRequest):
    """The complete documented list-query allowlist for this leaf."""

    page: int = Field(default=1, ge=1)
    page_size: int = Field(
        default=DEFAULT_PAGE_SIZE,
        alias="pageSize",
        serialization_alias="pageSize",
        ge=1,
        le=MAX_PAGE_SIZE,
    )
    include: str | None = Field(default=None, min_length=1)
    sort_property: str | None = Field(
        default=None,
        alias="sortProperty",
        serialization_alias="sortProperty",
        min_length=1,
    )
    sort_direction: SortDirection | None = Field(
        default=None,
        alias="sortDirection",
        serialization_alias="sortDirection",
    )


class BalanceInvoiceExtensionRecord(BaseModel):
    """An opaque record returned by a documented read endpoint."""

    model_config = ConfigDict(extra="allow")


class BalanceInvoiceExtensionPaging(BaseModel):
    """The documented paging envelope, preserved without invented fields."""

    model_config = ConfigDict(extra="allow")


class BalanceInvoiceExtensionMeta(BaseModel):
    """The optional metadata subset documented for collection reads."""

    model_config = ConfigDict(extra="ignore")

    paging: BalanceInvoiceExtensionPaging | None = None


class ContactBalancePaymentGetSuccess(BaseModel):
    """Successful response for ``api_contact_balance_payments_get``."""

    model_config = ConfigDict(extra="forbid")

    contactBalancePayment: BalanceInvoiceExtensionRecord


class ContactBalancePostingGetSuccess(BaseModel):
    """Successful response for ``api_contact_balance_postings_get``."""

    model_config = ConfigDict(extra="forbid")

    contactBalancePosting: BalanceInvoiceExtensionRecord


class InvoiceLateFeeGetSuccess(BaseModel):
    """Successful response for ``api_invoice_late_fees_get``."""

    model_config = ConfigDict(extra="forbid")

    invoiceLateFee: BalanceInvoiceExtensionRecord


class InvoiceReminderGetSuccess(BaseModel):
    """Successful response for ``api_invoice_reminders_get``."""

    model_config = ConfigDict(extra="forbid")

    invoiceReminder: BalanceInvoiceExtensionRecord


class InvoiceReminderAssociationGetSuccess(BaseModel):
    """Successful response for ``api_invoice_reminder_associations_get``."""

    model_config = ConfigDict(extra="forbid")

    invoiceReminderAssociation: BalanceInvoiceExtensionRecord


class _ListSuccess(BaseModel):
    """Avoid fabricating metadata when an upstream collection omits it."""

    model_config = ConfigDict(extra="forbid")

    meta: BalanceInvoiceExtensionMeta | None = None

    @model_serializer(mode="wrap")
    def serialize_optional_meta(self, handler: SerializerFunctionWrapHandler) -> dict[str, object]:
        """Omit an absent optional metadata root from structured tool output."""

        serialized = cast(dict[str, object], handler(self))
        return {key: value for key, value in serialized.items() if value is not None}


class ContactBalancePaymentsListSuccess(_ListSuccess):
    """Successful response for ``api_contact_balance_payments_list``."""

    contactBalancePayments: list[BalanceInvoiceExtensionRecord]


class ContactBalancePostingsListSuccess(_ListSuccess):
    """Successful response for ``api_contact_balance_postings_list``."""

    contactBalancePostings: list[BalanceInvoiceExtensionRecord]


class InvoiceLateFeesListSuccess(_ListSuccess):
    """Successful response for ``api_invoice_late_fees_list``."""

    invoiceLateFees: list[BalanceInvoiceExtensionRecord]


class InvoiceRemindersListSuccess(_ListSuccess):
    """Successful response for ``api_invoice_reminders_list``."""

    invoiceReminders: list[BalanceInvoiceExtensionRecord]


class InvoiceReminderAssociationsListSuccess(_ListSuccess):
    """Successful response for ``api_invoice_reminder_associations_list``."""

    invoiceReminderAssociations: list[BalanceInvoiceExtensionRecord]


class BalanceInvoiceExtensionReadService:
    """Run the ten frozen reads through the locked Billy client."""

    def __init__(self, client: BillyHttpClient) -> None:
        self._client = client

    def contact_balance_payments_get(
        self, request: BalanceInvoiceExtensionGetRequest
    ) -> ContactBalancePaymentGetSuccess | ToolError:
        """Read one contact balance payment."""

        record = self._get("/contactBalancePayments", "contactBalancePayment", request)
        return (
            record
            if isinstance(record, ToolError)
            else ContactBalancePaymentGetSuccess(contactBalancePayment=record)
        )

    def contact_balance_payments_list(
        self, request: BalanceInvoiceExtensionListRequest
    ) -> ContactBalancePaymentsListSuccess | ToolError:
        """List contact balance payments."""

        records = self._list("/contactBalancePayments", "contactBalancePayments", request)
        if isinstance(records, ToolError):
            return records
        payments, meta = records
        return ContactBalancePaymentsListSuccess(contactBalancePayments=payments, meta=meta)

    def contact_balance_postings_get(
        self, request: BalanceInvoiceExtensionGetRequest
    ) -> ContactBalancePostingGetSuccess | ToolError:
        """Read one contact balance posting."""

        record = self._get("/contactBalancePostings", "contactBalancePosting", request)
        return (
            record
            if isinstance(record, ToolError)
            else ContactBalancePostingGetSuccess(contactBalancePosting=record)
        )

    def contact_balance_postings_list(
        self, request: BalanceInvoiceExtensionListRequest
    ) -> ContactBalancePostingsListSuccess | ToolError:
        """List contact balance postings."""

        records = self._list("/contactBalancePostings", "contactBalancePostings", request)
        if isinstance(records, ToolError):
            return records
        postings, meta = records
        return ContactBalancePostingsListSuccess(contactBalancePostings=postings, meta=meta)

    def invoice_late_fees_get(
        self, request: BalanceInvoiceExtensionGetRequest
    ) -> InvoiceLateFeeGetSuccess | ToolError:
        """Read one invoice late fee."""

        record = self._get("/invoiceLateFees", "invoiceLateFee", request)
        return (
            record
            if isinstance(record, ToolError)
            else InvoiceLateFeeGetSuccess(invoiceLateFee=record)
        )

    def invoice_late_fees_list(
        self, request: BalanceInvoiceExtensionListRequest
    ) -> InvoiceLateFeesListSuccess | ToolError:
        """List invoice late fees."""

        records = self._list("/invoiceLateFees", "invoiceLateFees", request)
        if isinstance(records, ToolError):
            return records
        late_fees, meta = records
        return InvoiceLateFeesListSuccess(invoiceLateFees=late_fees, meta=meta)

    def invoice_reminders_get(
        self, request: BalanceInvoiceExtensionGetRequest
    ) -> InvoiceReminderGetSuccess | ToolError:
        """Read one invoice reminder."""

        record = self._get("/invoiceReminders", "invoiceReminder", request)
        return (
            record
            if isinstance(record, ToolError)
            else InvoiceReminderGetSuccess(invoiceReminder=record)
        )

    def invoice_reminders_list(
        self, request: BalanceInvoiceExtensionListRequest
    ) -> InvoiceRemindersListSuccess | ToolError:
        """List invoice reminders."""

        records = self._list("/invoiceReminders", "invoiceReminders", request)
        if isinstance(records, ToolError):
            return records
        reminders, meta = records
        return InvoiceRemindersListSuccess(invoiceReminders=reminders, meta=meta)

    def invoice_reminder_associations_get(
        self, request: BalanceInvoiceExtensionGetRequest
    ) -> InvoiceReminderAssociationGetSuccess | ToolError:
        """Read one invoice reminder association."""

        record = self._get("/invoiceReminderAssociations", "invoiceReminderAssociation", request)
        return (
            record
            if isinstance(record, ToolError)
            else InvoiceReminderAssociationGetSuccess(invoiceReminderAssociation=record)
        )

    def invoice_reminder_associations_list(
        self, request: BalanceInvoiceExtensionListRequest
    ) -> InvoiceReminderAssociationsListSuccess | ToolError:
        """List invoice reminder associations."""

        records = self._list("/invoiceReminderAssociations", "invoiceReminderAssociations", request)
        if isinstance(records, ToolError):
            return records
        associations, meta = records
        return InvoiceReminderAssociationsListSuccess(
            invoiceReminderAssociations=associations,
            meta=meta,
        )

    def _get(
        self,
        collection_path: str,
        root: str,
        request: BalanceInvoiceExtensionGetRequest,
    ) -> BalanceInvoiceExtensionRecord | ToolError:
        response = self._client.request(
            "GET",
            _item_path(collection_path, request.id),
            params=_get_params(request),
        )
        return _record_from_response(response, root)

    def _list(
        self,
        collection_path: str,
        root: str,
        request: BalanceInvoiceExtensionListRequest,
    ) -> tuple[list[BalanceInvoiceExtensionRecord], BalanceInvoiceExtensionMeta | None] | ToolError:
        response = self._client.request("GET", collection_path, params=_list_params(request))
        return _list_from_response(response, root)


def register_balance_invoice_extension_read_tools(server: FastMCP, client: BillyHttpClient) -> None:
    """Register exactly the ten frozen balance and invoice-extension read tools."""

    service = BalanceInvoiceExtensionReadService(client)

    def api_contact_balance_payments_get(
        id: str = Field(min_length=1),
        include: str | None = Field(default=None, min_length=1),
    ) -> ContactBalancePaymentGetSuccess | ToolError:
        """Read one Billy contact balance payment by identifier."""

        return service.contact_balance_payments_get(
            BalanceInvoiceExtensionGetRequest(id=id, include=include)
        )

    def api_contact_balance_payments_list(
        page: int = Field(default=1, ge=1),
        pageSize: int = Field(default=DEFAULT_PAGE_SIZE, ge=1, le=MAX_PAGE_SIZE),
        include: str | None = Field(default=None, min_length=1),
        sortProperty: str | None = Field(default=None, min_length=1),
        sortDirection: SortDirection | None = None,
    ) -> ContactBalancePaymentsListSuccess | ToolError:
        """List Billy contact balance payments with documented query fields only."""

        return service.contact_balance_payments_list(
            BalanceInvoiceExtensionListRequest(
                page=page,
                pageSize=pageSize,
                include=include,
                sortProperty=sortProperty,
                sortDirection=sortDirection,
            )
        )

    def api_contact_balance_postings_get(
        id: str = Field(min_length=1),
        include: str | None = Field(default=None, min_length=1),
    ) -> ContactBalancePostingGetSuccess | ToolError:
        """Read one Billy contact balance posting by identifier."""

        return service.contact_balance_postings_get(
            BalanceInvoiceExtensionGetRequest(id=id, include=include)
        )

    def api_contact_balance_postings_list(
        page: int = Field(default=1, ge=1),
        pageSize: int = Field(default=DEFAULT_PAGE_SIZE, ge=1, le=MAX_PAGE_SIZE),
        include: str | None = Field(default=None, min_length=1),
        sortProperty: str | None = Field(default=None, min_length=1),
        sortDirection: SortDirection | None = None,
    ) -> ContactBalancePostingsListSuccess | ToolError:
        """List Billy contact balance postings with documented query fields only."""

        return service.contact_balance_postings_list(
            BalanceInvoiceExtensionListRequest(
                page=page,
                pageSize=pageSize,
                include=include,
                sortProperty=sortProperty,
                sortDirection=sortDirection,
            )
        )

    def api_invoice_late_fees_get(
        id: str = Field(min_length=1),
        include: str | None = Field(default=None, min_length=1),
    ) -> InvoiceLateFeeGetSuccess | ToolError:
        """Read one Billy invoice late fee by identifier."""

        return service.invoice_late_fees_get(
            BalanceInvoiceExtensionGetRequest(id=id, include=include)
        )

    def api_invoice_late_fees_list(
        page: int = Field(default=1, ge=1),
        pageSize: int = Field(default=DEFAULT_PAGE_SIZE, ge=1, le=MAX_PAGE_SIZE),
        include: str | None = Field(default=None, min_length=1),
        sortProperty: str | None = Field(default=None, min_length=1),
        sortDirection: SortDirection | None = None,
    ) -> InvoiceLateFeesListSuccess | ToolError:
        """List Billy invoice late fees with documented query fields only."""

        return service.invoice_late_fees_list(
            BalanceInvoiceExtensionListRequest(
                page=page,
                pageSize=pageSize,
                include=include,
                sortProperty=sortProperty,
                sortDirection=sortDirection,
            )
        )

    def api_invoice_reminders_get(
        id: str = Field(min_length=1),
        include: str | None = Field(default=None, min_length=1),
    ) -> InvoiceReminderGetSuccess | ToolError:
        """Read one Billy invoice reminder by identifier."""

        return service.invoice_reminders_get(
            BalanceInvoiceExtensionGetRequest(id=id, include=include)
        )

    def api_invoice_reminders_list(
        page: int = Field(default=1, ge=1),
        pageSize: int = Field(default=DEFAULT_PAGE_SIZE, ge=1, le=MAX_PAGE_SIZE),
        include: str | None = Field(default=None, min_length=1),
        sortProperty: str | None = Field(default=None, min_length=1),
        sortDirection: SortDirection | None = None,
    ) -> InvoiceRemindersListSuccess | ToolError:
        """List Billy invoice reminders with documented query fields only."""

        return service.invoice_reminders_list(
            BalanceInvoiceExtensionListRequest(
                page=page,
                pageSize=pageSize,
                include=include,
                sortProperty=sortProperty,
                sortDirection=sortDirection,
            )
        )

    def api_invoice_reminder_associations_get(
        id: str = Field(min_length=1),
        include: str | None = Field(default=None, min_length=1),
    ) -> InvoiceReminderAssociationGetSuccess | ToolError:
        """Read one Billy invoice reminder association by identifier."""

        return service.invoice_reminder_associations_get(
            BalanceInvoiceExtensionGetRequest(id=id, include=include)
        )

    def api_invoice_reminder_associations_list(
        page: int = Field(default=1, ge=1),
        pageSize: int = Field(default=DEFAULT_PAGE_SIZE, ge=1, le=MAX_PAGE_SIZE),
        include: str | None = Field(default=None, min_length=1),
        sortProperty: str | None = Field(default=None, min_length=1),
        sortDirection: SortDirection | None = None,
    ) -> InvoiceReminderAssociationsListSuccess | ToolError:
        """List Billy invoice reminder associations with documented query fields only."""

        return service.invoice_reminder_associations_list(
            BalanceInvoiceExtensionListRequest(
                page=page,
                pageSize=pageSize,
                include=include,
                sortProperty=sortProperty,
                sortDirection=sortDirection,
            )
        )

    server.tool(
        name="api_contact_balance_payments_get",
        description="Read one Billy contact balance payment.",
    )(api_contact_balance_payments_get)
    server.tool(
        name="api_contact_balance_payments_list",
        description="List Billy contact balance payments.",
    )(api_contact_balance_payments_list)
    server.tool(
        name="api_contact_balance_postings_get",
        description="Read one Billy contact balance posting.",
    )(api_contact_balance_postings_get)
    server.tool(
        name="api_contact_balance_postings_list",
        description="List Billy contact balance postings.",
    )(api_contact_balance_postings_list)
    server.tool(name="api_invoice_late_fees_get", description="Read one Billy invoice late fee.")(
        api_invoice_late_fees_get
    )
    server.tool(name="api_invoice_late_fees_list", description="List Billy invoice late fees.")(
        api_invoice_late_fees_list
    )
    server.tool(name="api_invoice_reminders_get", description="Read one Billy invoice reminder.")(
        api_invoice_reminders_get
    )
    server.tool(name="api_invoice_reminders_list", description="List Billy invoice reminders.")(
        api_invoice_reminders_list
    )
    server.tool(
        name="api_invoice_reminder_associations_get",
        description="Read one Billy invoice reminder association.",
    )(api_invoice_reminder_associations_get)
    server.tool(
        name="api_invoice_reminder_associations_list",
        description="List Billy invoice reminder associations.",
    )(api_invoice_reminder_associations_list)


def _item_path(collection_path: str, identifier: str) -> str:
    """Build a collection item path with the identifier confined to one segment."""

    return f"{collection_path}/{quote(identifier, safe='')}"


def _get_params(request: BalanceInvoiceExtensionGetRequest) -> dict[str, str] | None:
    """Return the singular-read query allowlist without empty parameters."""

    return None if request.include is None else {"include": request.include}


def _list_params(request: BalanceInvoiceExtensionListRequest) -> dict[str, int | str]:
    """Return exactly the frozen collection query allowlist."""

    params: dict[str, int | str] = {"page": request.page, "pageSize": request.page_size}
    if request.include is not None:
        params["include"] = request.include
    if request.sort_property is not None:
        params["sortProperty"] = request.sort_property
    if request.sort_direction is not None:
        params["sortDirection"] = request.sort_direction.value
    return params


def _record_from_response(
    response: BillyResponse | ToolError, root: str
) -> BalanceInvoiceExtensionRecord | ToolError:
    """Map only a documented singular object root from a client response."""

    payload = _response_mapping(response, root)
    if isinstance(payload, ToolError):
        return payload
    record = payload.get(root)
    if not isinstance(record, Mapping):
        return _invalid_response(root)
    try:
        return BalanceInvoiceExtensionRecord.model_validate(record)
    except ValidationError:
        return _invalid_response(root)


def _list_from_response(
    response: BillyResponse | ToolError, root: str
) -> tuple[list[BalanceInvoiceExtensionRecord], BalanceInvoiceExtensionMeta | None] | ToolError:
    """Map only a documented plural array root and optional paging envelope."""

    payload = _response_mapping(response, root)
    if isinstance(payload, ToolError):
        return payload
    values = payload.get(root)
    if not isinstance(values, list):
        return _invalid_response(root)
    records: list[BalanceInvoiceExtensionRecord] = []
    for value in cast(list[object], values):
        if not isinstance(value, Mapping):
            return _invalid_response(root)
        try:
            records.append(BalanceInvoiceExtensionRecord.model_validate(value))
        except ValidationError:
            return _invalid_response(root)
    meta = _meta_from_response(payload, root)
    if isinstance(meta, ToolError):
        return meta
    return records, meta


def _response_mapping(
    response: BillyResponse | ToolError, root: str
) -> Mapping[str, object] | ToolError:
    """Narrow successful decoded JSON to the object expected by this contract."""

    if isinstance(response, ToolError):
        return response
    data: object = response.data
    if not isinstance(data, Mapping):
        return _invalid_response(root)
    return cast(Mapping[str, object], data)


def _meta_from_response(
    payload: Mapping[str, object], root: str
) -> BalanceInvoiceExtensionMeta | ToolError | None:
    """Validate the optional metadata object without requiring it upstream."""

    meta = payload.get("meta")
    if meta is None:
        return None
    if not isinstance(meta, Mapping):
        return _invalid_response(root)
    try:
        return BalanceInvoiceExtensionMeta.model_validate(meta)
    except ValidationError:
        return _invalid_response(root)


def _invalid_response(root: str) -> ToolError:
    """Return a typed error instead of inventing an undocumented success shape."""

    return ToolError(
        code=StableErrorCode.BILLY_ERROR,
        message=(
            "Billy API response did not contain the documented balance or invoice extension root."
        ),
        details={"expected_root": root},
    )
