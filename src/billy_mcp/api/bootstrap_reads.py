"""Typed, read-only bootstrap tools for the authenticated Billy API."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Annotated, Any, Literal, cast
from urllib.parse import quote

from fastmcp import FastMCP
from pydantic import BaseModel, ConfigDict, Field

from billy_mcp.client import DEFAULT_PAGE_SIZE, MAX_PAGE_SIZE, BillyHttpClient, BillyResponse
from billy_mcp.models import StableErrorCode, ToolError
from billy_mcp.redaction import redact

type Record = dict[str, Any]
type SortDirection = Literal["ASC", "DESC"]


class _InputModel(BaseModel):
    """Common strict configuration for public request models."""

    model_config = ConfigDict(extra="forbid", populate_by_name=True)


class _SuccessModel(BaseModel):
    """Common strict configuration for public success models."""

    model_config = ConfigDict(extra="forbid")


class UserGetInput(_InputModel):
    """Input for the current authenticated Billy user."""


class UserListOrganizationsInput(_InputModel):
    """Input for organisations available to the current authenticated user."""


class OrganizationGetInput(_InputModel):
    """Input for one organisation by its Billy identifier."""

    id: str = Field(min_length=1)
    include: str | None = None


class OrganizationsListInput(_InputModel):
    """Documented collection controls for organisations."""

    page: int = Field(default=1, ge=1)
    page_size: int = Field(
        default=DEFAULT_PAGE_SIZE,
        alias="pageSize",
        ge=1,
        le=MAX_PAGE_SIZE,
    )
    include: str | None = None
    sort_property: str | None = Field(default=None, alias="sortProperty")
    sort_direction: SortDirection | None = Field(default=None, alias="sortDirection")


class UserGetSuccess(_SuccessModel):
    """The documented user root with opaque fields preserved unless sensitive."""

    user: Record


class UserListOrganizationsSuccess(_SuccessModel):
    """The documented organisations root for the authenticated user."""

    organizations: list[Record]


class OrganizationGetSuccess(_SuccessModel):
    """The documented organisation root, with sensitive fields redacted."""

    organization: Record


class OrganizationsListSuccess(_SuccessModel):
    """The documented organisations root and optional opaque paging metadata."""

    organizations: list[Record]
    paging: Record | None = None


def _unexpected_response(message: str) -> ToolError:
    return ToolError(code=StableErrorCode.BILLY_ERROR, message=message)


def _as_record(value: object, *, name: str) -> Record | ToolError:
    """Validate an opaque JSON object and redact sensitive values recursively."""

    if not isinstance(value, Mapping):
        return _unexpected_response(f"Billy API response did not contain an object for {name}.")
    record: Record = {}
    mapping = cast(Mapping[object, object], value)
    for key, item in mapping.items():
        if not isinstance(key, str):
            return _unexpected_response(
                f"Billy API response contained a non-string key for {name}."
            )
        record[key] = item
    redacted = redact(record)
    if not isinstance(redacted, dict):
        raise AssertionError("redacting a mapping must produce a mapping")
    return {key: item for key, item in redacted.items()}


def _payload(response: BillyResponse | ToolError) -> Record | ToolError:
    """Return a successful top-level object or propagate the typed client error."""

    if isinstance(response, ToolError):
        return response
    return _as_record(response.data, name="response")


def _root_record(response: BillyResponse | ToolError, *, root: str) -> Record | ToolError:
    """Map one documented singular response root without assuming its fields."""

    payload = _payload(response)
    if isinstance(payload, ToolError):
        return payload
    return _as_record(payload.get(root), name=root)


def _root_list(response: BillyResponse | ToolError, *, root: str) -> list[Record] | ToolError:
    """Map one documented plural response root without assuming record fields."""

    payload = _payload(response)
    if isinstance(payload, ToolError):
        return payload
    values = payload.get(root)
    if not isinstance(values, list):
        return _unexpected_response(f"Billy API response did not contain a list for {root}.")
    records: list[Record] = []
    for value in cast(list[object], values):
        record = _as_record(value, name=root)
        if isinstance(record, ToolError):
            return record
        records.append(record)
    return records


def _optional_paging(response: BillyResponse | ToolError) -> Record | None | ToolError:
    """Map `meta.paging` only when it is present and shaped as a JSON object."""

    payload = _payload(response)
    if isinstance(payload, ToolError):
        return payload
    meta = payload.get("meta")
    if meta is None:
        return None
    meta_record = _as_record(meta, name="meta")
    if isinstance(meta_record, ToolError):
        return meta_record
    paging = meta_record.get("paging")
    if paging is None:
        return None
    return _as_record(paging, name="meta.paging")


def _query_params(**values: str | int | None) -> dict[str, str | int]:
    """Omit undocumented empty query controls before calling the locked client."""

    return {key: value for key, value in values.items() if value is not None}


class _BootstrapReadHandlers:
    """Bound FastMCP handlers sharing the injected, locked HTTP client."""

    def __init__(self, client: BillyHttpClient) -> None:
        self._client = client

    def api_user_get(self) -> UserGetSuccess | ToolError:
        """Get the current authenticated Billy API user."""

        UserGetInput()
        user = _root_record(self._client.request("GET", "/user"), root="user")
        if isinstance(user, ToolError):
            return user
        return UserGetSuccess(user=user)

    def api_user_list_organizations(self) -> UserListOrganizationsSuccess | ToolError:
        """List organisations available to the current authenticated Billy user."""

        UserListOrganizationsInput()
        organizations = _root_list(
            self._client.request("GET", "/user/organizations"), root="organizations"
        )
        if isinstance(organizations, ToolError):
            return organizations
        return UserListOrganizationsSuccess(organizations=organizations)

    def api_organizations_get(
        self,
        id: Annotated[str, Field(min_length=1)],
        include: str | None = None,
    ) -> OrganizationGetSuccess | ToolError:
        """Get one Billy organisation by ID using only the documented include control."""

        request = OrganizationGetInput(id=id, include=include)
        organization = _root_record(
            self._client.request(
                "GET",
                f"/organizations/{quote(request.id, safe='')}",
                params=_query_params(include=request.include) or None,
            ),
            root="organization",
        )
        if isinstance(organization, ToolError):
            return organization
        return OrganizationGetSuccess(organization=organization)

    def api_organizations_list(
        self,
        page: Annotated[int, Field(ge=1)] = 1,
        pageSize: Annotated[int, Field(ge=1, le=MAX_PAGE_SIZE)] = DEFAULT_PAGE_SIZE,
        include: str | None = None,
        sortProperty: str | None = None,
        sortDirection: SortDirection | None = None,
    ) -> OrganizationsListSuccess | ToolError:
        """List organisations with only the frozen documented paging and sort controls."""

        request = OrganizationsListInput(
            page=page,
            pageSize=pageSize,
            include=include,
            sortProperty=sortProperty,
            sortDirection=sortDirection,
        )
        response = self._client.request(
            "GET",
            "/organizations",
            params=_query_params(
                page=request.page,
                pageSize=request.page_size,
                include=request.include,
                sortProperty=request.sort_property,
                sortDirection=request.sort_direction,
            ),
        )
        organizations = _root_list(response, root="organizations")
        if isinstance(organizations, ToolError):
            return organizations
        paging = _optional_paging(response)
        if isinstance(paging, ToolError):
            return paging
        return OrganizationsListSuccess(organizations=organizations, paging=paging)


def register_bootstrap_read_tools(server: FastMCP, client: BillyHttpClient) -> None:
    """Register only the four implemented bootstrap read tools on a FastMCP server."""

    handlers = _BootstrapReadHandlers(client)
    server.tool(name="api_user_get", description="Get the current authenticated Billy user.")(
        handlers.api_user_get
    )
    server.tool(
        name="api_user_list_organizations",
        description="List organisations available to the current authenticated Billy user.",
    )(handlers.api_user_list_organizations)
    server.tool(name="api_organizations_get", description="Get one Billy organisation by ID.")(
        handlers.api_organizations_get
    )
    server.tool(
        name="api_organizations_list",
        description="List Billy organisations with documented paging and sort controls.",
    )(handlers.api_organizations_list)
