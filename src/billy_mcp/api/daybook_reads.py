"""Typed, read-only tools for documented Billy daybook-parent endpoints."""

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


class _DaybookReadInput(BaseModel):
    """Reject every input outside the documented daybook-parent contract."""

    model_config = ConfigDict(
        extra="forbid", strict=True, validate_by_alias=True, validate_by_name=True
    )


class SortDirection(StrEnum):
    """The two documented list sort directions."""

    ASC = "ASC"
    DESC = "DESC"


class DaybookGetInput(_DaybookReadInput):
    """Input for ``api_daybooks_get``."""

    id: str = Field(min_length=1)
    include: str | None = Field(default=None, min_length=1)

    def query_params(self) -> dict[str, str]:
        """Return only the optional documented singular-read query field."""

        return {} if self.include is None else {"include": self.include}


class DaybookListInput(_DaybookReadInput):
    """The complete documented query surface for daybook collection reads."""

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
        default=None, alias="sortDirection", serialization_alias="sortDirection"
    )

    def query_params(self) -> dict[str, str | int]:
        """Serialise only documented paging, include, and sorting controls."""

        return cast(
            dict[str, str | int],
            self.model_dump(by_alias=True, exclude_none=True, mode="json"),
        )


class DaybookBalanceAccountGetInput(DaybookGetInput):
    """Input for ``api_daybook_balance_accounts_get``."""


class DaybookBalanceAccountListInput(DaybookListInput):
    """The complete documented daybook-balance-account list input surface."""


class DaybookRecord(BaseModel):
    """An opaque daybook payload whose fields are not frozen in this leaf."""

    model_config = ConfigDict(extra="allow")


class DaybookBalanceAccountRecord(BaseModel):
    """An opaque daybook-balance-account payload from Billy."""

    model_config = ConfigDict(extra="allow")


class Paging(BaseModel):
    """The optional documented collection paging fields."""

    model_config = ConfigDict(extra="ignore", validate_by_alias=True, validate_by_name=True)

    page: int | None = None
    page_count: int | None = Field(default=None, alias="pageCount")
    page_size: int | None = Field(default=None, alias="pageSize")
    total: int | None = None
    first_url: str | None = Field(default=None, alias="firstUrl")
    previous_url: str | None = Field(default=None, alias="previousUrl")
    next_url: str | None = Field(default=None, alias="nextUrl")
    last_url: str | None = Field(default=None, alias="lastUrl")


class DaybookMeta(BaseModel):
    """The optional metadata root for a daybook collection response."""

    model_config = ConfigDict(extra="ignore")

    paging: Paging | None = None

    @model_serializer(mode="wrap")
    def serialize_optional_paging(
        self, handler: SerializerFunctionWrapHandler
    ) -> dict[str, object]:
        """Do not fabricate a paging object when the upstream omits it."""

        serialized = cast(dict[str, object], handler(self))
        return {key: value for key, value in serialized.items() if value is not None}


class DaybookBalanceAccountsMeta(BaseModel):
    """The optional metadata root for a balance-account collection response."""

    model_config = ConfigDict(extra="ignore")

    paging: Paging | None = None

    @model_serializer(mode="wrap")
    def serialize_optional_paging(
        self, handler: SerializerFunctionWrapHandler
    ) -> dict[str, object]:
        """Do not fabricate a paging object when the upstream omits it."""

        serialized = cast(dict[str, object], handler(self))
        return {key: value for key, value in serialized.items() if value is not None}


class DaybookGetSuccess(BaseModel):
    """Successful response for ``api_daybooks_get``."""

    model_config = ConfigDict(extra="forbid")

    daybook: DaybookRecord


class DaybookListSuccess(BaseModel):
    """Successful response for ``api_daybooks_list``."""

    model_config = ConfigDict(extra="forbid")

    daybooks: list[DaybookRecord]
    meta: DaybookMeta | None = None

    @model_serializer(mode="wrap")
    def serialize_optional_meta(self, handler: SerializerFunctionWrapHandler) -> dict[str, object]:
        """Keep an absent upstream metadata root absent in the tool result."""

        serialized = cast(dict[str, object], handler(self))
        return {key: value for key, value in serialized.items() if value is not None}


class DaybookBalanceAccountGetSuccess(BaseModel):
    """Successful response for ``api_daybook_balance_accounts_get``."""

    model_config = ConfigDict(extra="forbid")

    daybookBalanceAccount: DaybookBalanceAccountRecord


class DaybookBalanceAccountListSuccess(BaseModel):
    """Successful response for ``api_daybook_balance_accounts_list``."""

    model_config = ConfigDict(extra="forbid")

    daybookBalanceAccounts: list[DaybookBalanceAccountRecord]
    meta: DaybookBalanceAccountsMeta | None = None

    @model_serializer(mode="wrap")
    def serialize_optional_meta(self, handler: SerializerFunctionWrapHandler) -> dict[str, object]:
        """Keep an absent upstream metadata root absent in the tool result."""

        serialized = cast(dict[str, object], handler(self))
        return {key: value for key, value in serialized.items() if value is not None}


def get_daybook(client: BillyHttpClient, input: DaybookGetInput) -> DaybookGetSuccess | ToolError:
    """Read one daybook through its documented singular root."""

    record = _get_record(client, "/daybooks", "daybook", input, DaybookRecord)
    if isinstance(record, ToolError):
        return record
    return DaybookGetSuccess(daybook=record)


def list_daybooks(
    client: BillyHttpClient, input: DaybookListInput
) -> DaybookListSuccess | ToolError:
    """Read daybooks with only documented paging, include, and sorting controls."""

    result = _list_records(client, "/daybooks", "daybooks", input, DaybookRecord)
    if isinstance(result, ToolError):
        return result
    records, meta = result
    try:
        return DaybookListSuccess(
            daybooks=records,
            meta=None if meta is None else DaybookMeta.model_validate(meta),
        )
    except ValidationError:
        return _unexpected_response("meta")


def get_daybook_balance_account(
    client: BillyHttpClient, input: DaybookBalanceAccountGetInput
) -> DaybookBalanceAccountGetSuccess | ToolError:
    """Read one daybook balance account through its documented singular root."""

    record = _get_record(
        client,
        "/daybookBalanceAccounts",
        "daybookBalanceAccount",
        input,
        DaybookBalanceAccountRecord,
    )
    if isinstance(record, ToolError):
        return record
    return DaybookBalanceAccountGetSuccess(daybookBalanceAccount=record)


def list_daybook_balance_accounts(
    client: BillyHttpClient, input: DaybookBalanceAccountListInput
) -> DaybookBalanceAccountListSuccess | ToolError:
    """Read balance accounts with only documented generic collection controls."""

    result = _list_records(
        client,
        "/daybookBalanceAccounts",
        "daybookBalanceAccounts",
        input,
        DaybookBalanceAccountRecord,
    )
    if isinstance(result, ToolError):
        return result
    records, meta = result
    try:
        return DaybookBalanceAccountListSuccess(
            daybookBalanceAccounts=records,
            meta=None if meta is None else DaybookBalanceAccountsMeta.model_validate(meta),
        )
    except ValidationError:
        return _unexpected_response("meta")


def register_daybook_read_tools(server: FastMCP, client: BillyHttpClient) -> None:
    """Register only the four typed daybook-parent read tools."""

    def api_daybooks_get(
        id: str = Field(min_length=1), include: str | None = Field(default=None, min_length=1)
    ) -> DaybookGetSuccess | ToolError:
        """Read one Billy daybook by identifier."""

        return get_daybook(client, DaybookGetInput(id=id, include=include))

    def api_daybooks_list(
        page: int = Field(default=1, ge=1),
        pageSize: int = Field(default=DEFAULT_PAGE_SIZE, ge=1, le=MAX_PAGE_SIZE),
        include: str | None = Field(default=None, min_length=1),
        sortProperty: str | None = Field(default=None, min_length=1),
        sortDirection: SortDirection | None = None,
    ) -> DaybookListSuccess | ToolError:
        """Read Billy daybooks with documented paging, inclusion, and sorting only."""

        return list_daybooks(
            client,
            DaybookListInput(
                page=page,
                pageSize=pageSize,
                include=include,
                sortProperty=sortProperty,
                sortDirection=sortDirection,
            ),
        )

    def api_daybook_balance_accounts_get(
        id: str = Field(min_length=1), include: str | None = Field(default=None, min_length=1)
    ) -> DaybookBalanceAccountGetSuccess | ToolError:
        """Read one Billy daybook balance account by identifier."""

        return get_daybook_balance_account(
            client, DaybookBalanceAccountGetInput(id=id, include=include)
        )

    def api_daybook_balance_accounts_list(
        page: int = Field(default=1, ge=1),
        pageSize: int = Field(default=DEFAULT_PAGE_SIZE, ge=1, le=MAX_PAGE_SIZE),
        include: str | None = Field(default=None, min_length=1),
        sortProperty: str | None = Field(default=None, min_length=1),
        sortDirection: SortDirection | None = None,
    ) -> DaybookBalanceAccountListSuccess | ToolError:
        """Read Billy daybook balance accounts with generic controls only."""

        return list_daybook_balance_accounts(
            client,
            DaybookBalanceAccountListInput(
                page=page,
                pageSize=pageSize,
                include=include,
                sortProperty=sortProperty,
                sortDirection=sortDirection,
            ),
        )

    server.tool(name="api_daybooks_get", description="Read one Billy daybook.")(api_daybooks_get)
    server.tool(name="api_daybooks_list", description="List Billy daybooks.")(api_daybooks_list)
    server.tool(
        name="api_daybook_balance_accounts_get",
        description="Read one Billy daybook balance account.",
    )(api_daybook_balance_accounts_get)
    server.tool(
        name="api_daybook_balance_accounts_list",
        description="List Billy daybook balance accounts.",
    )(api_daybook_balance_accounts_list)


def _get_record[RecordT: (DaybookRecord, DaybookBalanceAccountRecord)](
    client: BillyHttpClient,
    collection_path: str,
    root: str,
    input: DaybookGetInput,
    record_type: type[RecordT],
) -> RecordT | ToolError:
    """Map one documented root while preserving the opaque record payload."""

    response = client.request(
        "GET",
        f"{collection_path}/{quote(input.id, safe='')}",
        params=input.query_params() or None,
    )
    if isinstance(response, ToolError):
        return response
    payload = _response_mapping(response)
    record = None if payload is None else _object_mapping(payload.get(root))
    if record is None:
        return _unexpected_response(root)
    try:
        return record_type.model_validate(record)
    except ValidationError:
        return _unexpected_response(root)


def _list_records[RecordT: (DaybookRecord, DaybookBalanceAccountRecord)](
    client: BillyHttpClient,
    path: str,
    root: str,
    input: DaybookListInput,
    record_type: type[RecordT],
) -> tuple[list[RecordT], Mapping[str, object] | None] | ToolError:
    """Map a documented plural root and its optional metadata mapping."""

    response = client.request("GET", path, params=input.query_params())
    if isinstance(response, ToolError):
        return response
    payload = _response_mapping(response)
    values: object = None if payload is None else payload.get(root)
    if not isinstance(values, list):
        return _unexpected_response(root)
    records: list[RecordT] = []
    for value in cast(list[object], values):
        record = _object_mapping(value)
        if record is None:
            return _unexpected_response(root)
        try:
            records.append(record_type.model_validate(record))
        except ValidationError:
            return _unexpected_response(root)
    meta_value: object = None if payload is None else payload.get("meta")
    meta = _object_mapping(meta_value)
    if meta_value is not None and meta is None:
        return _unexpected_response("meta")
    return records, meta


def _response_mapping(response: BillyResponse) -> Mapping[str, object] | None:
    """Narrow a successful client payload to the JSON object expected by these reads."""

    return _object_mapping(response.data)


def _object_mapping(value: object) -> Mapping[str, object] | None:
    """Narrow decoded JSON values to mappings without inventing their contents."""

    if not isinstance(value, Mapping):
        return None
    return cast(Mapping[str, object], value)


def _unexpected_response(root: str) -> ToolError:
    """Return a typed failure instead of inventing an undocumented success shape."""

    return ToolError(
        code=StableErrorCode.BILLY_ERROR,
        message="Billy API response did not contain the documented daybook-parent root.",
        details={"expected_root": root},
    )
