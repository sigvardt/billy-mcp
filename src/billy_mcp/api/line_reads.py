"""Typed, read-only tools for documented Billy document-line endpoints."""

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


class _LineReadRequest(BaseModel):
    """Reject inputs outside the documented document-line read contract."""

    model_config = ConfigDict(
        extra="forbid", strict=True, validate_by_alias=True, validate_by_name=True
    )


class SortDirection(StrEnum):
    """The two documented collection sort directions."""

    ASC = "ASC"
    DESC = "DESC"


class LineGetRequest(_LineReadRequest):
    """Inputs shared by all documented singular document-line reads."""

    id: str = Field(min_length=1)
    include: str | None = Field(default=None, min_length=1)

    def query_params(self) -> dict[str, str]:
        """Return only the optional documented singular-read query field."""

        return {} if self.include is None else {"include": self.include}


class LineListRequest(_LineReadRequest):
    """The complete documented collection query surface for document lines."""

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
        default=None, alias="sortProperty", serialization_alias="sortProperty"
    )
    sort_direction: SortDirection | None = Field(
        default=None, alias="sortDirection", serialization_alias="sortDirection"
    )

    def query_params(self) -> dict[str, str | int]:
        """Serialise only the frozen global paging, include, and sort fields."""

        return cast(
            dict[str, str | int],
            self.model_dump(by_alias=True, exclude_none=True, mode="json"),
        )


class LinePayload(BaseModel):
    """An opaque JSON object returned by Billy for a document line."""

    model_config = ConfigDict(extra="allow")


class LinePaging(BaseModel):
    """The optional documented paging fields returned by a collection read."""

    model_config = ConfigDict(extra="ignore")

    page: int | None = None
    page_count: int | None = Field(default=None, alias="pageCount")
    page_size: int | None = Field(default=None, alias="pageSize")
    total: int | None = None
    first_url: str | None = Field(default=None, alias="firstUrl")
    previous_url: str | None = Field(default=None, alias="previousUrl")
    next_url: str | None = Field(default=None, alias="nextUrl")
    last_url: str | None = Field(default=None, alias="lastUrl")


class LineMeta(BaseModel):
    """The documented optional metadata root for a document-line collection."""

    model_config = ConfigDict(extra="ignore")

    paging: LinePaging | None = None

    @model_serializer(mode="wrap")
    def serialize_optional_paging(
        self, handler: SerializerFunctionWrapHandler
    ) -> dict[str, object]:
        """Keep an absent upstream paging object absent from metadata."""

        serialized = cast(dict[str, object], handler(self))
        return {key: value for key, value in serialized.items() if value is not None}


class InvoiceLineGetSuccess(BaseModel):
    """Successful response for ``api_invoice_lines_get``."""

    model_config = ConfigDict(extra="forbid")

    invoiceLine: LinePayload


class BillLineGetSuccess(BaseModel):
    """Successful response for ``api_bill_lines_get``."""

    model_config = ConfigDict(extra="forbid")

    billLine: LinePayload


class DaybookTransactionLineGetSuccess(BaseModel):
    """Successful response for ``api_daybook_transaction_lines_get``."""

    model_config = ConfigDict(extra="forbid")

    daybookTransactionLine: LinePayload


class _LineListSuccess(BaseModel):
    """Shared optional metadata preservation for document-line collection reads."""

    model_config = ConfigDict(extra="forbid")

    meta: LineMeta | None = None

    @model_serializer(mode="wrap")
    def serialize_optional_meta(self, handler: SerializerFunctionWrapHandler) -> dict[str, object]:
        """Keep absent upstream metadata absent in the typed tool result."""

        serialized = cast(dict[str, object], handler(self))
        return {key: value for key, value in serialized.items() if value is not None}


class InvoiceLineListSuccess(_LineListSuccess):
    """Successful response for ``api_invoice_lines_list``."""

    invoiceLines: list[LinePayload]


class BillLineListSuccess(_LineListSuccess):
    """Successful response for ``api_bill_lines_list``."""

    billLines: list[LinePayload]


class DaybookTransactionLineListSuccess(_LineListSuccess):
    """Successful response for ``api_daybook_transaction_lines_list``."""

    daybookTransactionLines: list[LinePayload]


class LineReadService:
    """Typed handlers over the locked client, separate from root server wiring."""

    def __init__(self, client: BillyHttpClient) -> None:
        self._client = client

    def invoice_lines_get(self, request: LineGetRequest) -> InvoiceLineGetSuccess | ToolError:
        """Read one invoice line by its Billy identifier."""

        line = self._get("/invoiceLines", "invoiceLine", request)
        if isinstance(line, ToolError):
            return line
        return InvoiceLineGetSuccess(invoiceLine=line)

    def invoice_lines_list(self, request: LineListRequest) -> InvoiceLineListSuccess | ToolError:
        """Read one documented page of invoice lines."""

        lines = self._list("/invoiceLines", "invoiceLines", request)
        if isinstance(lines, ToolError):
            return lines
        records, meta = lines
        return InvoiceLineListSuccess(invoiceLines=records, meta=meta)

    def bill_lines_get(self, request: LineGetRequest) -> BillLineGetSuccess | ToolError:
        """Read one bill line by its Billy identifier."""

        line = self._get("/billLines", "billLine", request)
        if isinstance(line, ToolError):
            return line
        return BillLineGetSuccess(billLine=line)

    def bill_lines_list(self, request: LineListRequest) -> BillLineListSuccess | ToolError:
        """Read one documented page of bill lines."""

        lines = self._list("/billLines", "billLines", request)
        if isinstance(lines, ToolError):
            return lines
        records, meta = lines
        return BillLineListSuccess(billLines=records, meta=meta)

    def daybook_transaction_lines_get(
        self, request: LineGetRequest
    ) -> DaybookTransactionLineGetSuccess | ToolError:
        """Read one daybook transaction line by its Billy identifier."""

        line = self._get("/daybookTransactionLines", "daybookTransactionLine", request)
        if isinstance(line, ToolError):
            return line
        return DaybookTransactionLineGetSuccess(daybookTransactionLine=line)

    def daybook_transaction_lines_list(
        self, request: LineListRequest
    ) -> DaybookTransactionLineListSuccess | ToolError:
        """Read one documented page of daybook transaction lines."""

        lines = self._list("/daybookTransactionLines", "daybookTransactionLines", request)
        if isinstance(lines, ToolError):
            return lines
        records, meta = lines
        return DaybookTransactionLineListSuccess(daybookTransactionLines=records, meta=meta)

    def _get(
        self, collection_path: str, root_name: str, request: LineGetRequest
    ) -> LinePayload | ToolError:
        response = self._client.request(
            "GET",
            f"{collection_path}/{quote(request.id, safe='')}",
            params=request.query_params() or None,
        )
        if isinstance(response, ToolError):
            return response
        payload = _response_mapping(response)
        root = None if payload is None else _object_mapping(payload.get(root_name))
        if root is None:
            return _unexpected_response(root_name)
        try:
            return LinePayload.model_validate(root)
        except ValidationError:
            return _unexpected_response(root_name)

    def _list(
        self, collection_path: str, root_name: str, request: LineListRequest
    ) -> tuple[list[LinePayload], LineMeta | None] | ToolError:
        response = self._client.request("GET", collection_path, params=request.query_params())
        if isinstance(response, ToolError):
            return response
        payload = _response_mapping(response)
        raw_records = None if payload is None else payload.get(root_name)
        if not isinstance(raw_records, list):
            return _unexpected_response(root_name)
        records: list[LinePayload] = []
        for raw_record in cast(list[object], raw_records):
            record = _object_mapping(raw_record)
            if record is None:
                return _unexpected_response(root_name)
            try:
                records.append(LinePayload.model_validate(record))
            except ValidationError:
                return _unexpected_response(root_name)
        meta_value = None if payload is None else payload.get("meta")
        meta = _object_mapping(meta_value)
        if meta_value is not None and meta is None:
            return _unexpected_response("meta")
        try:
            return records, None if meta is None else LineMeta.model_validate(meta)
        except ValidationError:
            return _unexpected_response("meta")


def register_line_read_tools(server: FastMCP, client: BillyHttpClient) -> None:
    """Register only the six typed document-line reads on a FastMCP server."""

    service = LineReadService(client)

    def api_invoice_lines_get(
        id: str = Field(min_length=1), include: str | None = Field(default=None, min_length=1)
    ) -> InvoiceLineGetSuccess | ToolError:
        """Read one Billy invoice line by identifier."""

        return service.invoice_lines_get(LineGetRequest(id=id, include=include))

    def api_invoice_lines_list(
        page: int = Field(default=1, ge=1),
        pageSize: int = Field(default=DEFAULT_PAGE_SIZE, ge=1, le=MAX_PAGE_SIZE),
        include: str | None = Field(default=None, min_length=1),
        sortProperty: str | None = None,
        sortDirection: SortDirection | None = None,
    ) -> InvoiceLineListSuccess | ToolError:
        """List Billy invoice lines with documented paging, inclusion, and sorting."""

        return service.invoice_lines_list(
            LineListRequest(
                page=page,
                pageSize=pageSize,
                include=include,
                sortProperty=sortProperty,
                sortDirection=sortDirection,
            )
        )

    def api_bill_lines_get(
        id: str = Field(min_length=1), include: str | None = Field(default=None, min_length=1)
    ) -> BillLineGetSuccess | ToolError:
        """Read one Billy bill line by identifier."""

        return service.bill_lines_get(LineGetRequest(id=id, include=include))

    def api_bill_lines_list(
        page: int = Field(default=1, ge=1),
        pageSize: int = Field(default=DEFAULT_PAGE_SIZE, ge=1, le=MAX_PAGE_SIZE),
        include: str | None = Field(default=None, min_length=1),
        sortProperty: str | None = None,
        sortDirection: SortDirection | None = None,
    ) -> BillLineListSuccess | ToolError:
        """List Billy bill lines with documented paging, inclusion, and sorting."""

        return service.bill_lines_list(
            LineListRequest(
                page=page,
                pageSize=pageSize,
                include=include,
                sortProperty=sortProperty,
                sortDirection=sortDirection,
            )
        )

    def api_daybook_transaction_lines_get(
        id: str = Field(min_length=1), include: str | None = Field(default=None, min_length=1)
    ) -> DaybookTransactionLineGetSuccess | ToolError:
        """Read one Billy daybook transaction line by identifier."""

        return service.daybook_transaction_lines_get(LineGetRequest(id=id, include=include))

    def api_daybook_transaction_lines_list(
        page: int = Field(default=1, ge=1),
        pageSize: int = Field(default=DEFAULT_PAGE_SIZE, ge=1, le=MAX_PAGE_SIZE),
        include: str | None = Field(default=None, min_length=1),
        sortProperty: str | None = None,
        sortDirection: SortDirection | None = None,
    ) -> DaybookTransactionLineListSuccess | ToolError:
        """List Billy daybook transaction lines with documented paging, inclusion, and sorting."""

        return service.daybook_transaction_lines_list(
            LineListRequest(
                page=page,
                pageSize=pageSize,
                include=include,
                sortProperty=sortProperty,
                sortDirection=sortDirection,
            )
        )

    server.tool(name="api_invoice_lines_get", description="Read one Billy invoice line.")(
        api_invoice_lines_get
    )
    server.tool(name="api_invoice_lines_list", description="List Billy invoice lines.")(
        api_invoice_lines_list
    )
    server.tool(name="api_bill_lines_get", description="Read one Billy bill line.")(
        api_bill_lines_get
    )
    server.tool(name="api_bill_lines_list", description="List Billy bill lines.")(
        api_bill_lines_list
    )
    server.tool(
        name="api_daybook_transaction_lines_get",
        description="Read one Billy daybook transaction line.",
    )(api_daybook_transaction_lines_get)
    server.tool(
        name="api_daybook_transaction_lines_list",
        description="List Billy daybook transaction lines.",
    )(api_daybook_transaction_lines_list)


def _response_mapping(response: BillyResponse) -> Mapping[str, object] | None:
    """Narrow a successful client payload to the expected JSON object shape."""

    return _object_mapping(response.data)


def _object_mapping(value: object) -> Mapping[str, object] | None:
    """Narrow decoded JSON values to object mappings without coercion."""

    if not isinstance(value, Mapping):
        return None
    return cast(Mapping[str, object], value)


def _unexpected_response(root: str) -> ToolError:
    """Avoid inventing a success shape when Billy omits a documented root."""

    return ToolError(
        code=StableErrorCode.BILLY_ERROR,
        message="Billy API response did not contain the documented document-line root.",
        details={"expected_root": root},
    )
