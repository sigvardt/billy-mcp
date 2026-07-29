"""Typed, read-only tools for documented Billy ledger and users endpoints."""

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
    """Reject all input outside the frozen ledger/users read contract."""

    model_config = ConfigDict(
        extra="forbid", strict=True, validate_by_alias=True, validate_by_name=True
    )


class SortDirection(StrEnum):
    """The two documented collection sort directions."""

    ASC = "ASC"
    DESC = "DESC"


class _GetRequest(_RequestModel):
    """Shared documented input for one singular ledger/users read."""

    id: str = Field(min_length=1)
    include: str | None = Field(default=None, min_length=1)

    def query_params(self) -> dict[str, str]:
        """Return only the optional documented singular-read query field."""

        return {} if self.include is None else {"include": self.include}


class _ListRequest(_RequestModel):
    """The complete documented list-query allowlist for this module."""

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
        """Serialise only documented paging, inclusion, and sorting controls."""

        return cast(
            dict[str, str | int],
            self.model_dump(by_alias=True, exclude_none=True, mode="json"),
        )


class TransactionGetRequest(_GetRequest):
    """Input for ``api_transactions_get``."""


class PostingGetRequest(_GetRequest):
    """Input for ``api_postings_get``."""


class UserGetRequest(_GetRequest):
    """Input for ``api_users_get``; this is not the ``/user`` special."""


class TransactionsListRequest(_ListRequest):
    """Input for ``api_transactions_list``."""


class PostingsListRequest(_ListRequest):
    """Input for ``api_postings_list``."""


class UsersListRequest(_ListRequest):
    """Input for ``api_users_list``; this is not ``/user/organizations``."""


class _OpaquePayload(BaseModel):
    """An opaque JSON object returned by Billy."""

    model_config = ConfigDict(extra="allow")


class TransactionPayload(_OpaquePayload):
    """An opaque transaction payload."""


class PostingPayload(_OpaquePayload):
    """An opaque posting payload."""


class UserPayload(_OpaquePayload):
    """An opaque ``/users`` payload; email and phone remain unmodelled."""


class Paging(BaseModel):
    """The optional documented collection paging fields."""

    model_config = ConfigDict(extra="ignore")

    page: int | None = None
    page_count: int | None = Field(default=None, alias="pageCount")
    page_size: int | None = Field(default=None, alias="pageSize")
    total: int | None = None
    first_url: str | None = Field(default=None, alias="firstUrl")
    previous_url: str | None = Field(default=None, alias="previousUrl")
    next_url: str | None = Field(default=None, alias="nextUrl")
    last_url: str | None = Field(default=None, alias="lastUrl")


class LedgerUsersMeta(BaseModel):
    """The optional metadata root for these collection responses."""

    model_config = ConfigDict(extra="ignore")

    paging: Paging | None = None


class TransactionGetSuccess(BaseModel):
    """Successful response for ``api_transactions_get``."""

    model_config = ConfigDict(extra="forbid")

    transaction: TransactionPayload


class PostingGetSuccess(BaseModel):
    """Successful response for ``api_postings_get``."""

    model_config = ConfigDict(extra="forbid")

    posting: PostingPayload


class UserGetSuccess(BaseModel):
    """Successful response for ``api_users_get``."""

    model_config = ConfigDict(extra="forbid")

    user: UserPayload


class _ListSuccess(BaseModel):
    """Keep an absent upstream metadata root absent from structured output."""

    model_config = ConfigDict(extra="forbid")

    meta: LedgerUsersMeta | None = None

    @model_serializer(mode="wrap")
    def serialize_optional_meta(self, handler: SerializerFunctionWrapHandler) -> dict[str, object]:
        """Avoid fabricating an empty metadata root when Billy omits it."""

        serialized = cast(dict[str, object], handler(self))
        return {key: value for key, value in serialized.items() if value is not None}


class TransactionsListSuccess(_ListSuccess):
    """Successful response for ``api_transactions_list``."""

    transactions: list[TransactionPayload]


class PostingsListSuccess(_ListSuccess):
    """Successful response for ``api_postings_list``."""

    postings: list[PostingPayload]


class UsersListSuccess(_ListSuccess):
    """Successful response for ``api_users_list``."""

    users: list[UserPayload]


def get_transaction(
    client: BillyHttpClient, request: TransactionGetRequest
) -> TransactionGetSuccess | ToolError:
    """Retrieve one transaction through its documented singular response root."""

    record = _get_record(client, request, "/transactions", "transaction")
    if isinstance(record, ToolError):
        return record
    try:
        return TransactionGetSuccess(transaction=TransactionPayload.model_validate(record))
    except ValidationError:
        return _unexpected_response("transaction")


def get_posting(
    client: BillyHttpClient, request: PostingGetRequest
) -> PostingGetSuccess | ToolError:
    """Retrieve one posting through its documented singular response root."""

    record = _get_record(client, request, "/postings", "posting")
    if isinstance(record, ToolError):
        return record
    try:
        return PostingGetSuccess(posting=PostingPayload.model_validate(record))
    except ValidationError:
        return _unexpected_response("posting")


def get_user(client: BillyHttpClient, request: UserGetRequest) -> UserGetSuccess | ToolError:
    """Retrieve one ``/users`` resource record through its documented root."""

    record = _get_record(client, request, "/users", "user")
    if isinstance(record, ToolError):
        return record
    try:
        return UserGetSuccess(user=UserPayload.model_validate(record))
    except ValidationError:
        return _unexpected_response("user")


def list_transactions(
    client: BillyHttpClient, request: TransactionsListRequest
) -> TransactionsListSuccess | ToolError:
    """Retrieve transactions and their optional documented paging metadata."""

    records = _list_records(client, request, "/transactions", "transactions")
    if isinstance(records, ToolError):
        return records
    values, meta = records
    try:
        return TransactionsListSuccess(
            transactions=[TransactionPayload.model_validate(value) for value in values], meta=meta
        )
    except ValidationError:
        return _unexpected_response("transactions")


def list_postings(
    client: BillyHttpClient, request: PostingsListRequest
) -> PostingsListSuccess | ToolError:
    """Retrieve postings and their optional documented paging metadata."""

    records = _list_records(client, request, "/postings", "postings")
    if isinstance(records, ToolError):
        return records
    values, meta = records
    try:
        return PostingsListSuccess(
            postings=[PostingPayload.model_validate(value) for value in values], meta=meta
        )
    except ValidationError:
        return _unexpected_response("postings")


def list_users(client: BillyHttpClient, request: UsersListRequest) -> UsersListSuccess | ToolError:
    """Retrieve ``/users`` records and their optional paging metadata."""

    records = _list_records(client, request, "/users", "users")
    if isinstance(records, ToolError):
        return records
    values, meta = records
    try:
        return UsersListSuccess(
            users=[UserPayload.model_validate(value) for value in values], meta=meta
        )
    except ValidationError:
        return _unexpected_response("users")


def register_ledger_user_read_tools(server: FastMCP, client: BillyHttpClient) -> None:
    """Register exactly the six typed ledger and ``/users`` read tools."""

    def api_transactions_get(
        id: str = Field(min_length=1), include: str | None = Field(default=None, min_length=1)
    ) -> TransactionGetSuccess | ToolError:
        """Read one Billy transaction by identifier."""

        return get_transaction(client, TransactionGetRequest(id=id, include=include))

    def api_transactions_list(
        page: int = Field(default=1, ge=1),
        pageSize: int = Field(default=DEFAULT_PAGE_SIZE, ge=1, le=MAX_PAGE_SIZE),
        include: str | None = Field(default=None, min_length=1),
        sortProperty: str | None = Field(default=None, min_length=1),
        sortDirection: SortDirection | None = None,
    ) -> TransactionsListSuccess | ToolError:
        """Read Billy transactions with documented paging, inclusion, and sorting only."""

        return list_transactions(
            client,
            TransactionsListRequest(
                page=page,
                pageSize=pageSize,
                include=include,
                sortProperty=sortProperty,
                sortDirection=sortDirection,
            ),
        )

    def api_postings_get(
        id: str = Field(min_length=1), include: str | None = Field(default=None, min_length=1)
    ) -> PostingGetSuccess | ToolError:
        """Read one Billy posting by identifier."""

        return get_posting(client, PostingGetRequest(id=id, include=include))

    def api_postings_list(
        page: int = Field(default=1, ge=1),
        pageSize: int = Field(default=DEFAULT_PAGE_SIZE, ge=1, le=MAX_PAGE_SIZE),
        include: str | None = Field(default=None, min_length=1),
        sortProperty: str | None = Field(default=None, min_length=1),
        sortDirection: SortDirection | None = None,
    ) -> PostingsListSuccess | ToolError:
        """Read Billy postings with documented paging, inclusion, and sorting only."""

        return list_postings(
            client,
            PostingsListRequest(
                page=page,
                pageSize=pageSize,
                include=include,
                sortProperty=sortProperty,
                sortDirection=sortDirection,
            ),
        )

    def api_users_get(
        id: str = Field(min_length=1), include: str | None = Field(default=None, min_length=1)
    ) -> UserGetSuccess | ToolError:
        """Read one Billy ``/users`` resource record by identifier."""

        return get_user(client, UserGetRequest(id=id, include=include))

    def api_users_list(
        page: int = Field(default=1, ge=1),
        pageSize: int = Field(default=DEFAULT_PAGE_SIZE, ge=1, le=MAX_PAGE_SIZE),
        include: str | None = Field(default=None, min_length=1),
        sortProperty: str | None = Field(default=None, min_length=1),
        sortDirection: SortDirection | None = None,
    ) -> UsersListSuccess | ToolError:
        """Read Billy ``/users`` records with documented paging and sorting only."""

        return list_users(
            client,
            UsersListRequest(
                page=page,
                pageSize=pageSize,
                include=include,
                sortProperty=sortProperty,
                sortDirection=sortDirection,
            ),
        )

    server.tool(name="api_transactions_get", description="Read one Billy transaction.")(
        api_transactions_get
    )
    server.tool(
        name="api_transactions_list",
        description="Read Billy transactions with documented paging, inclusion, and sorting.",
    )(api_transactions_list)
    server.tool(name="api_postings_get", description="Read one Billy posting.")(api_postings_get)
    server.tool(
        name="api_postings_list",
        description="Read Billy postings with documented paging, inclusion, and sorting.",
    )(api_postings_list)
    server.tool(name="api_users_get", description="Read one Billy users resource record.")(
        api_users_get
    )
    server.tool(
        name="api_users_list",
        description="Read Billy users resource records with documented paging and sorting.",
    )(api_users_list)


def _get_record(
    client: BillyHttpClient, request: _GetRequest, collection_path: str, root: str
) -> Mapping[str, object] | ToolError:
    """Read a singular resource and validate its documented object root."""

    response = client.request(
        "GET",
        f"{collection_path}/{quote(request.id, safe='')}",
        params=request.query_params() or None,
    )
    if isinstance(response, ToolError):
        return response
    payload = _response_mapping(response)
    record = None if payload is None else _object_mapping(payload.get(root))
    return _unexpected_response(root) if record is None else record


def _list_records(
    client: BillyHttpClient, request: _ListRequest, collection_path: str, root: str
) -> tuple[list[Mapping[str, object]], LedgerUsersMeta | None] | ToolError:
    """Read a collection and validate its documented list and optional meta roots."""

    response = client.request("GET", collection_path, params=request.query_params())
    if isinstance(response, ToolError):
        return response
    payload = _response_mapping(response)
    values: object = None if payload is None else payload.get(root)
    if not isinstance(values, list):
        return _unexpected_response(root)
    records: list[Mapping[str, object]] = []
    for value in cast(list[object], values):
        record = _object_mapping(value)
        if record is None:
            return _unexpected_response(root)
        records.append(record)
    meta_value: object = None if payload is None else payload.get("meta")
    meta = _object_mapping(meta_value)
    if meta_value is not None and meta is None:
        return _unexpected_response("meta")
    try:
        return records, None if meta is None else LedgerUsersMeta.model_validate(meta)
    except ValidationError:
        return _unexpected_response("meta")


def _response_mapping(response: BillyResponse) -> Mapping[str, object] | None:
    """Narrow a successful client payload to the JSON object expected by these reads."""

    return _object_mapping(response.data)


def _object_mapping(value: object) -> Mapping[str, object] | None:
    """Narrow untyped decoded JSON to an object mapping."""

    if not isinstance(value, Mapping):
        return None
    return cast(Mapping[str, object], value)


def _unexpected_response(root: str) -> ToolError:
    """Avoid inventing a success shape when Billy omits a documented response root."""

    return ToolError(
        code=StableErrorCode.BILLY_ERROR,
        message="Billy API response did not contain a documented ledger or users root.",
        details={"expected_root": root},
    )
