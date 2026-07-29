"""Typed, read-only tools for documented Billy contact-person endpoints."""

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


class ContactPersonsGetRequest(_RequestModel):
    """Input for retrieving one contact person by its Billy identifier."""

    id: str = Field(min_length=1)
    include: str | None = None

    def query_params(self) -> dict[str, str]:
        """Return only the documented optional include query field."""

        return {} if self.include is None else {"include": self.include}


class ContactPersonsListRequest(_RequestModel):
    """Input for the documented contact-person collection read."""

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


class ContactPersonPayload(BaseModel):
    """An opaque JSON object returned by Billy for a contact person."""

    model_config = ConfigDict(extra="allow")


class ContactPersonsPaging(BaseModel):
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


class ContactPersonsMeta(BaseModel):
    """The subset of Billy list metadata documented for contact persons."""

    model_config = ConfigDict(extra="ignore")

    paging: ContactPersonsPaging | None = None


class ContactPersonsGetSuccess(BaseModel):
    """Successful response for ``api_contact_persons_get``."""

    model_config = ConfigDict(extra="forbid")

    contact_person: ContactPersonPayload = Field(
        alias="contactPerson", serialization_alias="contactPerson"
    )


class ContactPersonsListSuccess(BaseModel):
    """Successful response for ``api_contact_persons_list``."""

    model_config = ConfigDict(extra="forbid")

    contact_persons: list[ContactPersonPayload] = Field(
        alias="contactPersons", serialization_alias="contactPersons"
    )
    meta: ContactPersonsMeta | None = None

    @model_serializer(mode="wrap")
    def serialize_optional_meta(self, handler: SerializerFunctionWrapHandler) -> dict[str, object]:
        """Keep an absent upstream paging root absent in the tool result."""

        serialized = cast(dict[str, object], handler(self))
        return {key: value for key, value in serialized.items() if value is not None}


def get_contact_person(
    client: BillyHttpClient, request: ContactPersonsGetRequest
) -> ContactPersonsGetSuccess | ToolError:
    """Retrieve one contact person and map only its documented singular response root."""

    response = client.request(
        "GET",
        f"/contactPersons/{quote(request.id, safe='')}",
        params=request.query_params() or None,
    )
    if isinstance(response, ToolError):
        return response
    payload = _response_mapping(response)
    if payload is None or not isinstance(payload.get("contactPerson"), Mapping):
        return _unexpected_response("contactPerson")
    try:
        return ContactPersonsGetSuccess(
            contactPerson=ContactPersonPayload.model_validate(payload["contactPerson"])
        )
    except ValidationError:
        return _unexpected_response("contactPerson")


def list_contact_persons(
    client: BillyHttpClient, request: ContactPersonsListRequest
) -> ContactPersonsListSuccess | ToolError:
    """Retrieve contact persons and map their documented list root and optional paging."""

    response = client.request("GET", "/contactPersons", params=request.query_params())
    if isinstance(response, ToolError):
        return response
    payload = _response_mapping(response)
    contact_persons_value: object = None if payload is None else payload.get("contactPersons")
    if not isinstance(contact_persons_value, list):
        return _unexpected_response("contactPersons")
    contact_persons: list[Mapping[str, object]] = []
    for contact_person_value in cast(list[object], contact_persons_value):
        contact_person = _object_mapping(contact_person_value)
        if contact_person is None:
            return _unexpected_response("contactPersons")
        contact_persons.append(contact_person)
    meta_value: object = None if payload is None else payload.get("meta")
    meta = _object_mapping(meta_value)
    if meta_value is not None and meta is None:
        return _unexpected_response("meta")
    try:
        return ContactPersonsListSuccess(
            contactPersons=[
                ContactPersonPayload.model_validate(contact_person)
                for contact_person in contact_persons
            ],
            meta=None if meta is None else ContactPersonsMeta.model_validate(meta),
        )
    except ValidationError:
        return _unexpected_response("contactPersons")


def register_contact_person_read_tools(server: FastMCP, client: BillyHttpClient) -> None:
    """Register the two contact-person reads without changing root server wiring."""

    def api_contact_persons_get(
        id: str = Field(min_length=1), include: str | None = None
    ) -> ContactPersonsGetSuccess | ToolError:
        """Read one Billy contact person by identifier."""

        return get_contact_person(client, ContactPersonsGetRequest(id=id, include=include))

    def api_contact_persons_list(
        page: int = Field(default=1, ge=1),
        pageSize: int = Field(default=DEFAULT_PAGE_SIZE, ge=1, le=MAX_PAGE_SIZE),
        include: str | None = None,
        sortProperty: str | None = None,
        sortDirection: SortDirection | None = None,
    ) -> ContactPersonsListSuccess | ToolError:
        """Read Billy contact persons with documented paging, inclusion, and sorting only."""

        return list_contact_persons(
            client,
            ContactPersonsListRequest(
                page=page,
                pageSize=pageSize,
                include=include,
                sortProperty=sortProperty,
                sortDirection=sortDirection,
            ),
        )

    server.tool(name="api_contact_persons_get", description="Read one Billy contact person.")(
        api_contact_persons_get
    )
    server.tool(
        name="api_contact_persons_list",
        description="Read Billy contact persons with documented paging, inclusion, and sorting.",
    )(api_contact_persons_list)


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
        message="Billy API response did not contain the documented contact-person root.",
        details={"expected_root": root},
    )
