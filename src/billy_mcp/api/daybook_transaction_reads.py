"""Typed, read-only tools for documented Billy daybook-transaction endpoints."""

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


class _DaybookTransactionInput(BaseModel):
    """Reject every input outside the frozen daybook-transaction contract."""

    model_config = ConfigDict(extra="forbid", validate_by_alias=True, validate_by_name=True)


class DaybookTransactionState(StrEnum):
    """The documented states accepted by the daybook-transaction list."""

    DRAFT = "draft"
    APPROVED = "approved"
    VOIDED = "voided"


class DaybookTransactionSortProperty(StrEnum):
    """The complete documented daybook-transaction sort-property enum."""

    PRIORITY = "priority"
    ENTRY_DATE = "entryDate"
    CREATED_TIME = "createdTime"


class SortDirection(StrEnum):
    """The two documented sort directions."""

    ASC = "ASC"
    DESC = "DESC"


class DaybookTransactionGetInput(_DaybookTransactionInput):
    """Input for ``api_daybook_transactions_get``."""

    id: str = Field(min_length=1)
    include: str | None = Field(default=None, min_length=1)

    def query_params(self) -> dict[str, str]:
        """Return only the optional documented singular-read query field."""

        return {} if self.include is None else {"include": self.include}


class DaybookTransactionListInput(_DaybookTransactionInput):
    """The complete documented query surface for the collection read."""

    page: int = Field(default=1, ge=1)
    page_size: int = Field(
        default=DEFAULT_PAGE_SIZE,
        alias="pageSize",
        serialization_alias="pageSize",
        ge=1,
        le=MAX_PAGE_SIZE,
    )
    include: str | None = Field(default=None, min_length=1)
    organization_id: str | None = Field(
        default=None,
        alias="organizationId",
        serialization_alias="organizationId",
        min_length=1,
    )
    daybook_id: str | None = Field(
        default=None,
        alias="daybookId",
        serialization_alias="daybookId",
        min_length=1,
    )
    api_type: str | None = Field(
        default=None,
        alias="apiType",
        serialization_alias="apiType",
        min_length=1,
    )
    state: DaybookTransactionState | None = None
    min_entry_date: date | None = Field(
        default=None,
        alias="minEntryDate",
        serialization_alias="minEntryDate",
    )
    max_entry_date: date | None = Field(
        default=None,
        alias="maxEntryDate",
        serialization_alias="maxEntryDate",
    )
    q: str | None = Field(default=None, min_length=1)
    sort_property: DaybookTransactionSortProperty | None = Field(
        default=None,
        alias="sortProperty",
        serialization_alias="sortProperty",
    )
    sort_direction: SortDirection | None = Field(
        default=None,
        alias="sortDirection",
        serialization_alias="sortDirection",
    )

    def query_params(self) -> dict[str, str | int]:
        """Serialise only the frozen, documented collection query allowlist."""

        return cast(
            dict[str, str | int],
            self.model_dump(by_alias=True, exclude_none=True, mode="json"),
        )


class DaybookTransactionRecord(BaseModel):
    """An opaque daybook-transaction payload whose fields are not frozen."""

    model_config = ConfigDict(extra="allow")


class DaybookTransactionPaging(BaseModel):
    """The optional documented paging fields returned by the collection read."""

    model_config = ConfigDict(extra="ignore", validate_by_alias=True, validate_by_name=True)

    page: int | None = None
    page_count: int | None = Field(default=None, alias="pageCount")
    page_size: int | None = Field(default=None, alias="pageSize")
    total: int | None = None
    first_url: str | None = Field(default=None, alias="firstUrl")
    previous_url: str | None = Field(default=None, alias="previousUrl")
    next_url: str | None = Field(default=None, alias="nextUrl")
    last_url: str | None = Field(default=None, alias="lastUrl")


class DaybookTransactionsMeta(BaseModel):
    """The optional metadata root for daybook-transaction list responses."""

    model_config = ConfigDict(extra="ignore")

    paging: DaybookTransactionPaging | None = None

    @model_serializer(mode="wrap")
    def serialize_optional_paging(
        self, handler: SerializerFunctionWrapHandler
    ) -> dict[str, object]:
        """Do not fabricate a paging object when the upstream omits it."""

        serialized = cast(dict[str, object], handler(self))
        return {key: value for key, value in serialized.items() if value is not None}


class DaybookTransactionGetSuccess(BaseModel):
    """Successful response for ``api_daybook_transactions_get``."""

    model_config = ConfigDict(extra="forbid")

    daybookTransaction: DaybookTransactionRecord


class DaybookTransactionListSuccess(BaseModel):
    """Successful response for ``api_daybook_transactions_list``."""

    model_config = ConfigDict(extra="forbid")

    daybookTransactions: list[DaybookTransactionRecord]
    meta: DaybookTransactionsMeta | None = None

    @model_serializer(mode="wrap")
    def serialize_optional_meta(self, handler: SerializerFunctionWrapHandler) -> dict[str, object]:
        """Keep an absent upstream metadata root absent in the tool result."""

        serialized = cast(dict[str, object], handler(self))
        return {key: value for key, value in serialized.items() if value is not None}


def get_daybook_transaction(
    client: BillyHttpClient, input: DaybookTransactionGetInput
) -> DaybookTransactionGetSuccess | ToolError:
    """Read one daybook transaction through its documented singular root."""

    response = client.request(
        "GET",
        f"/daybookTransactions/{quote(input.id, safe='')}",
        params=input.query_params() or None,
    )
    if isinstance(response, ToolError):
        return response
    payload = _response_mapping(response)
    record = None if payload is None else _object_mapping(payload.get("daybookTransaction"))
    if record is None:
        return _unexpected_response("daybookTransaction")
    try:
        return DaybookTransactionGetSuccess(
            daybookTransaction=DaybookTransactionRecord.model_validate(record)
        )
    except ValidationError:
        return _unexpected_response("daybookTransaction")


def list_daybook_transactions(
    client: BillyHttpClient, input: DaybookTransactionListInput
) -> DaybookTransactionListSuccess | ToolError:
    """Read daybook transactions and map their optional metadata paging root."""

    response = client.request("GET", "/daybookTransactions", params=input.query_params())
    if isinstance(response, ToolError):
        return response
    payload = _response_mapping(response)
    values: object = None if payload is None else payload.get("daybookTransactions")
    if not isinstance(values, list):
        return _unexpected_response("daybookTransactions")
    transactions: list[DaybookTransactionRecord] = []
    for value in cast(list[object], values):
        record = _object_mapping(value)
        if record is None:
            return _unexpected_response("daybookTransactions")
        try:
            transactions.append(DaybookTransactionRecord.model_validate(record))
        except ValidationError:
            return _unexpected_response("daybookTransactions")
    meta_value: object = None if payload is None else payload.get("meta")
    meta = _object_mapping(meta_value)
    if meta_value is not None and meta is None:
        return _unexpected_response("meta")
    try:
        return DaybookTransactionListSuccess(
            daybookTransactions=transactions,
            meta=None if meta is None else DaybookTransactionsMeta.model_validate(meta),
        )
    except ValidationError:
        return _unexpected_response("meta")


def register_daybook_transaction_read_tools(server: FastMCP, client: BillyHttpClient) -> None:
    """Register only the two typed daybook-transaction read tools."""

    def api_daybook_transactions_get(
        input: DaybookTransactionGetInput,
    ) -> DaybookTransactionGetSuccess | ToolError:
        """Read one Billy daybook transaction by identifier."""

        return get_daybook_transaction(client, input)

    def api_daybook_transactions_list(
        input: DaybookTransactionListInput,
    ) -> DaybookTransactionListSuccess | ToolError:
        """Read Billy daybook transactions with documented filters only."""

        return list_daybook_transactions(client, input)

    server.tool(
        name="api_daybook_transactions_get",
        description="Read one Billy daybook transaction.",
    )(api_daybook_transactions_get)
    server.tool(
        name="api_daybook_transactions_list",
        description="Read Billy daybook transactions with documented filters only.",
    )(api_daybook_transactions_list)


def _response_mapping(response: BillyResponse) -> Mapping[str, object] | None:
    """Narrow a successful client payload to the expected JSON object shape."""

    return _object_mapping(response.data)


def _object_mapping(value: object) -> Mapping[str, object] | None:
    """Narrow decoded JSON values to object mappings without coercion."""

    if not isinstance(value, Mapping):
        return None
    return cast(Mapping[str, object], value)


def _unexpected_response(root: str) -> ToolError:
    """Return a typed failure instead of inventing an undocumented success shape."""

    return ToolError(
        code=StableErrorCode.BILLY_ERROR,
        message="Billy API response did not contain the documented daybook-transaction root.",
        details={"expected_root": root},
    )
