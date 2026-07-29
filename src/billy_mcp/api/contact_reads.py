"""Typed, read-only tools for documented Billy contacts endpoints."""

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
    """The two documented list sort directions."""

    ASC = "ASC"
    DESC = "DESC"


class ContactsGetRequest(_RequestModel):
    """Input for retrieving one contact by its Billy identifier."""

    id: str = Field(min_length=1)
    include: str | None = None

    def query_params(self) -> dict[str, str]:
        """Return only optional documented query fields."""

        return {} if self.include is None else {"include": self.include}


class ContactsListRequest(_RequestModel):
    """Input for the documented contacts collection read."""

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
        """Serialise the complete, intentionally small documented query surface."""

        return cast(
            dict[str, str | int],
            self.model_dump(by_alias=True, exclude_none=True, mode="json"),
        )


class ContactPayload(BaseModel):
    """An opaque JSON object returned by Billy for a contact."""

    model_config = ConfigDict(extra="allow")


class ContactsPaging(BaseModel):
    """The documented optional collection paging fields."""

    model_config = ConfigDict(extra="ignore")

    page: int | None = None
    page_count: int | None = Field(default=None, alias="pageCount")
    page_size: int | None = Field(default=None, alias="pageSize")
    total: int | None = None
    first_url: str | None = Field(default=None, alias="firstUrl")
    previous_url: str | None = Field(default=None, alias="previousUrl")
    next_url: str | None = Field(default=None, alias="nextUrl")
    last_url: str | None = Field(default=None, alias="lastUrl")


class ContactsMeta(BaseModel):
    """The subset of Billy list metadata documented for contacts."""

    model_config = ConfigDict(extra="ignore")

    paging: ContactsPaging | None = None


class ContactsGetSuccess(BaseModel):
    """Successful response for ``api_contacts_get``."""

    model_config = ConfigDict(extra="forbid")

    contact: ContactPayload


class ContactsListSuccess(BaseModel):
    """Successful response for ``api_contacts_list``."""

    model_config = ConfigDict(extra="forbid")

    contacts: list[ContactPayload]
    meta: ContactsMeta | None = None

    @model_serializer(mode="wrap")
    def serialize_optional_meta(self, handler: SerializerFunctionWrapHandler) -> dict[str, object]:
        """Keep an absent upstream paging root absent in the tool result."""

        serialized = cast(dict[str, object], handler(self))
        return {key: value for key, value in serialized.items() if value is not None}


def get_contact(
    client: BillyHttpClient, request: ContactsGetRequest
) -> ContactsGetSuccess | ToolError:
    """Retrieve one contact and map only its documented singular response root."""

    response = client.request(
        "GET",
        f"/contacts/{quote(request.id, safe='')}",
        params=request.query_params() or None,
    )
    if isinstance(response, ToolError):
        return response
    payload = _response_mapping(response)
    if payload is None or not isinstance(payload.get("contact"), Mapping):
        return _unexpected_response("contact")
    try:
        return ContactsGetSuccess(contact=ContactPayload.model_validate(payload["contact"]))
    except ValidationError:
        return _unexpected_response("contact")


def list_contacts(
    client: BillyHttpClient, request: ContactsListRequest
) -> ContactsListSuccess | ToolError:
    """Retrieve contacts and map their documented list root and optional paging."""

    response = client.request("GET", "/contacts", params=request.query_params())
    if isinstance(response, ToolError):
        return response
    payload = _response_mapping(response)
    contacts_value: object = None if payload is None else payload.get("contacts")
    if not isinstance(contacts_value, list):
        return _unexpected_response("contacts")
    contacts: list[Mapping[str, object]] = []
    for contact_value in cast(list[object], contacts_value):
        contact = _object_mapping(contact_value)
        if contact is None:
            return _unexpected_response("contacts")
        contacts.append(contact)
    meta_value: object = None if payload is None else payload.get("meta")
    meta = _object_mapping(meta_value)
    if meta_value is not None and meta is None:
        return _unexpected_response("meta")
    try:
        return ContactsListSuccess(
            contacts=[ContactPayload.model_validate(contact) for contact in contacts],
            meta=None if meta is None else ContactsMeta.model_validate(meta),
        )
    except ValidationError:
        return _unexpected_response("contacts")


def register_contact_read_tools(server: FastMCP, client: BillyHttpClient) -> None:
    """Register the two implemented contacts reads without changing root server wiring."""

    def api_contacts_get(
        id: str = Field(min_length=1), include: str | None = None
    ) -> ContactsGetSuccess | ToolError:
        """Read one Billy contact by identifier."""

        return get_contact(client, ContactsGetRequest(id=id, include=include))

    def api_contacts_list(
        page: int = Field(default=1, ge=1),
        pageSize: int = Field(default=DEFAULT_PAGE_SIZE, ge=1, le=MAX_PAGE_SIZE),
        include: str | None = None,
        sortProperty: str | None = None,
        sortDirection: SortDirection | None = None,
    ) -> ContactsListSuccess | ToolError:
        """Read Billy contacts with documented paging, inclusion, and sorting only."""

        return list_contacts(
            client,
            ContactsListRequest(
                page=page,
                pageSize=pageSize,
                include=include,
                sortProperty=sortProperty,
                sortDirection=sortDirection,
            ),
        )

    server.tool(name="api_contacts_get", description="Read one Billy contact.")(api_contacts_get)
    server.tool(
        name="api_contacts_list",
        description="Read Billy contacts with documented paging, inclusion, and sorting.",
    )(api_contacts_list)


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
        message="Billy API response did not contain the documented contacts root.",
        details={"expected_root": root},
    )
