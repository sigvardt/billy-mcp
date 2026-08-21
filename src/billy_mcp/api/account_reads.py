"""Typed, read-only tools for documented Billy chart-of-accounts endpoints."""

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
    """Reject undeclared inputs while accepting documented Billy wire aliases."""

    model_config = ConfigDict(
        extra="forbid", strict=True, validate_by_alias=True, validate_by_name=True
    )


class SortDirection(StrEnum):
    """The two documented collection sort directions."""

    ASC = "ASC"
    DESC = "DESC"


class _GetRequest(_RequestModel):
    """Shared documented input for a singular chart-of-accounts read."""

    id: str = Field(min_length=1)
    include: str | None = None

    def query_params(self) -> dict[str, str]:
        """Return only the optional documented singular-read query field."""

        return {} if self.include is None else {"include": self.include}


class _ListRequest(_RequestModel):
    """Shared, deliberately small list-query allowlist for this read cluster."""

    page: int = Field(default=1, ge=1)
    page_size: int = Field(
        default=DEFAULT_PAGE_SIZE,
        alias="pageSize",
        serialization_alias="pageSize",
        ge=1,
        le=MAX_PAGE_SIZE,
    )
    include: str | None = None
    sort_property: str | None = Field(
        default=None, alias="sortProperty", serialization_alias="sortProperty"
    )
    sort_direction: SortDirection | None = Field(
        default=None, alias="sortDirection", serialization_alias="sortDirection"
    )

    def query_params(self) -> dict[str, str | int]:
        """Serialise only documented paging, inclusion, and sorting parameters."""

        return cast(
            dict[str, str | int],
            self.model_dump(by_alias=True, exclude_none=True, mode="json"),
        )


class AccountGetRequest(_GetRequest):
    """Input for retrieving one account."""


class AccountGroupGetRequest(_GetRequest):
    """Input for retrieving one account group."""


class AccountNatureGetRequest(_GetRequest):
    """Input for retrieving one account nature."""


class AccountsListRequest(_ListRequest):
    """Input for the documented accounts collection read."""


class AccountGroupsListRequest(_ListRequest):
    """Input for the documented account-groups collection read."""


class AccountNaturesListRequest(_ListRequest):
    """Input for the documented account-natures collection read."""


class _OpaquePayload(BaseModel):
    """An opaque JSON object returned by Billy."""

    model_config = ConfigDict(extra="allow")


class AccountPayload(_OpaquePayload):
    """An opaque account payload; bank fields are intentionally not modelled."""


class AccountGroupPayload(_OpaquePayload):
    """An opaque account-group payload."""


class AccountNaturePayload(_OpaquePayload):
    """An opaque account-nature payload."""


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


class AccountsMeta(BaseModel):
    """The optional metadata root shared by the chart-of-accounts lists."""

    model_config = ConfigDict(extra="ignore")

    paging: Paging | None = None


class AccountGetSuccess(BaseModel):
    """Successful response for ``api_accounts_get``."""

    model_config = ConfigDict(extra="forbid")

    account: AccountPayload


class AccountGroupGetSuccess(BaseModel):
    """Successful response for ``api_account_groups_get``."""

    model_config = ConfigDict(extra="forbid")

    accountGroup: AccountGroupPayload


class AccountNatureGetSuccess(BaseModel):
    """Successful response for ``api_account_natures_get``."""

    model_config = ConfigDict(extra="forbid")

    accountNature: AccountNaturePayload


class _ListSuccess(BaseModel):
    """Keep absent upstream metadata absent from collection tool results."""

    model_config = ConfigDict(extra="forbid")

    meta: AccountsMeta | None = None

    @model_serializer(mode="wrap")
    def serialize_optional_meta(self, handler: SerializerFunctionWrapHandler) -> dict[str, object]:
        """Avoid fabricating an empty metadata root when Billy omits it."""

        serialized = cast(dict[str, object], handler(self))
        return {key: value for key, value in serialized.items() if value is not None}


class AccountsListSuccess(_ListSuccess):
    """Successful response for ``api_accounts_list``."""

    accounts: list[AccountPayload]


class AccountGroupsListSuccess(_ListSuccess):
    """Successful response for ``api_account_groups_list``."""

    accountGroups: list[AccountGroupPayload]


class AccountNaturesListSuccess(_ListSuccess):
    """Successful response for ``api_account_natures_list``."""

    accountNatures: list[AccountNaturePayload]


def get_account(
    client: BillyHttpClient, request: AccountGetRequest
) -> AccountGetSuccess | ToolError:
    """Retrieve one account through its documented singular response root."""

    record = _get_record(client, request, "/accounts", "account")
    if isinstance(record, ToolError):
        return record
    try:
        return AccountGetSuccess(account=AccountPayload.model_validate(record))
    except ValidationError:
        return _unexpected_response("account")


def get_account_group(
    client: BillyHttpClient, request: AccountGroupGetRequest
) -> AccountGroupGetSuccess | ToolError:
    """Retrieve one account group through its documented singular response root."""

    record = _get_record(client, request, "/accountGroups", "accountGroup")
    if isinstance(record, ToolError):
        return record
    try:
        return AccountGroupGetSuccess(accountGroup=AccountGroupPayload.model_validate(record))
    except ValidationError:
        return _unexpected_response("accountGroup")


def get_account_nature(
    client: BillyHttpClient, request: AccountNatureGetRequest
) -> AccountNatureGetSuccess | ToolError:
    """Retrieve one account nature through its documented singular response root."""

    record = _get_record(client, request, "/accountNatures", "accountNature")
    if isinstance(record, ToolError):
        return record
    try:
        return AccountNatureGetSuccess(accountNature=AccountNaturePayload.model_validate(record))
    except ValidationError:
        return _unexpected_response("accountNature")


def list_accounts(
    client: BillyHttpClient, request: AccountsListRequest
) -> AccountsListSuccess | ToolError:
    """Retrieve accounts and their optional documented paging metadata."""

    records = _list_records(client, request, "/accounts", "accounts")
    if isinstance(records, ToolError):
        return records
    values, meta = records
    try:
        return AccountsListSuccess(
            accounts=[AccountPayload.model_validate(value) for value in values], meta=meta
        )
    except ValidationError:
        return _unexpected_response("accounts")


def list_account_groups(
    client: BillyHttpClient, request: AccountGroupsListRequest
) -> AccountGroupsListSuccess | ToolError:
    """Retrieve account groups and their optional documented paging metadata."""

    records = _list_records(client, request, "/accountGroups", "accountGroups")
    if isinstance(records, ToolError):
        return records
    values, meta = records
    try:
        return AccountGroupsListSuccess(
            accountGroups=[AccountGroupPayload.model_validate(value) for value in values], meta=meta
        )
    except ValidationError:
        return _unexpected_response("accountGroups")


def list_account_natures(
    client: BillyHttpClient, request: AccountNaturesListRequest
) -> AccountNaturesListSuccess | ToolError:
    """Retrieve account natures and their optional documented paging metadata."""

    records = _list_records(client, request, "/accountNatures", "accountNatures")
    if isinstance(records, ToolError):
        return records
    values, meta = records
    try:
        return AccountNaturesListSuccess(
            accountNatures=[AccountNaturePayload.model_validate(value) for value in values],
            meta=meta,
        )
    except ValidationError:
        return _unexpected_response("accountNatures")


def register_account_read_tools(server: FastMCP, client: BillyHttpClient) -> None:
    """Register exactly the six typed chart-of-accounts read tools."""

    def api_accounts_get(
        id: str = Field(min_length=1), include: str | None = None
    ) -> AccountGetSuccess | ToolError:
        """Read one Billy account by identifier."""

        return get_account(client, AccountGetRequest(id=id, include=include))

    def api_accounts_list(
        page: int = Field(default=1, ge=1),
        pageSize: int = Field(default=DEFAULT_PAGE_SIZE, ge=1, le=MAX_PAGE_SIZE),
        include: str | None = None,
        sortProperty: str | None = None,
        sortDirection: SortDirection | None = None,
    ) -> AccountsListSuccess | ToolError:
        """Read Billy accounts with documented paging, inclusion, and sorting only."""

        return list_accounts(
            client,
            AccountsListRequest(
                page=page,
                pageSize=pageSize,
                include=include,
                sortProperty=sortProperty,
                sortDirection=sortDirection,
            ),
        )

    def api_account_groups_get(
        id: str = Field(min_length=1), include: str | None = None
    ) -> AccountGroupGetSuccess | ToolError:
        """Read one Billy account group by identifier."""

        return get_account_group(client, AccountGroupGetRequest(id=id, include=include))

    def api_account_groups_list(
        page: int = Field(default=1, ge=1),
        pageSize: int = Field(default=DEFAULT_PAGE_SIZE, ge=1, le=MAX_PAGE_SIZE),
        include: str | None = None,
        sortProperty: str | None = None,
        sortDirection: SortDirection | None = None,
    ) -> AccountGroupsListSuccess | ToolError:
        """Read Billy account groups with documented paging, inclusion, and sorting only."""

        return list_account_groups(
            client,
            AccountGroupsListRequest(
                page=page,
                pageSize=pageSize,
                include=include,
                sortProperty=sortProperty,
                sortDirection=sortDirection,
            ),
        )

    def api_account_natures_get(
        id: str = Field(min_length=1), include: str | None = None
    ) -> AccountNatureGetSuccess | ToolError:
        """Read one Billy account nature by identifier."""

        return get_account_nature(client, AccountNatureGetRequest(id=id, include=include))

    def api_account_natures_list(
        page: int = Field(default=1, ge=1),
        pageSize: int = Field(default=DEFAULT_PAGE_SIZE, ge=1, le=MAX_PAGE_SIZE),
        include: str | None = None,
        sortProperty: str | None = None,
        sortDirection: SortDirection | None = None,
    ) -> AccountNaturesListSuccess | ToolError:
        """Read Billy account natures with documented paging, inclusion, and sorting only."""

        return list_account_natures(
            client,
            AccountNaturesListRequest(
                page=page,
                pageSize=pageSize,
                include=include,
                sortProperty=sortProperty,
                sortDirection=sortDirection,
            ),
        )

    server.tool(name="api_accounts_get", description="Read one Billy account.")(api_accounts_get)
    server.tool(
        name="api_accounts_list",
        description="Read Billy accounts with documented paging, inclusion, and sorting.",
    )(api_accounts_list)
    server.tool(name="api_account_groups_get", description="Read one Billy account group.")(
        api_account_groups_get
    )
    server.tool(
        name="api_account_groups_list",
        description="Read Billy account groups with documented paging, inclusion, and sorting.",
    )(api_account_groups_list)
    server.tool(name="api_account_natures_get", description="Read one Billy account nature.")(
        api_account_natures_get
    )
    server.tool(
        name="api_account_natures_list",
        description="Read Billy account natures with documented paging, inclusion, and sorting.",
    )(api_account_natures_list)


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
) -> tuple[list[Mapping[str, object]], AccountsMeta | None] | ToolError:
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
        return records, None if meta is None else AccountsMeta.model_validate(meta)
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
        message="Billy API response did not contain a documented chart-of-accounts root.",
        details={"expected_root": root},
    )
