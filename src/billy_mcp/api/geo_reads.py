"""Typed, read-only tools for the frozen Billy geo endpoints."""

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
    """Reject inputs outside the frozen geo read contract."""

    model_config = ConfigDict(
        extra="forbid", strict=True, validate_by_alias=True, validate_by_name=True
    )


class SortDirection(StrEnum):
    """The two documented collection sort directions."""

    ASC = "ASC"
    DESC = "DESC"


class _GetRequest(_RequestModel):
    """Shared inputs for a singular geo read."""

    id: str = Field(min_length=1)
    include: str | None = Field(default=None, min_length=1)

    def query_params(self) -> dict[str, str]:
        """Return only the optional documented singular-read query field."""

        return {} if self.include is None else {"include": self.include}


class _ListRequest(_RequestModel):
    """The default frozen collection-query allowlist."""

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
        """Serialise only the frozen documented list fields."""

        return cast(
            dict[str, str | int],
            self.model_dump(by_alias=True, exclude_none=True, mode="json"),
        )


class _CountryBoundListRequest(_ListRequest):
    """List inputs for geo collections that Billy requires to be country-scoped."""

    country_id: str = Field(alias="countryId", serialization_alias="countryId", min_length=1)


class CountryGroupGetRequest(_GetRequest):
    """Input for retrieving one country group."""


class CityGetRequest(_GetRequest):
    """Input for retrieving one city."""


class StateGetRequest(_GetRequest):
    """Input for retrieving one state."""


class ZipcodeGetRequest(_GetRequest):
    """Input for retrieving one zipcode."""


class CountryGroupsListRequest(_ListRequest):
    """Input for the country-groups collection read."""


class CitiesListRequest(_CountryBoundListRequest):
    """Input for the country-scoped cities collection read."""


class StatesListRequest(_CountryBoundListRequest):
    """Input for the country-scoped states collection read."""


class ZipcodesListRequest(_CountryBoundListRequest):
    """Input for the country-scoped zipcodes collection read."""


class GeoPayload(BaseModel):
    """An opaque JSON object returned by a frozen geo endpoint."""

    model_config = ConfigDict(extra="allow")


class GeoPaging(BaseModel):
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


class GeoMeta(BaseModel):
    """The optional metadata root shared by the frozen geo lists."""

    model_config = ConfigDict(extra="ignore")

    paging: GeoPaging | None = None


class CountryGroupGetSuccess(BaseModel):
    """Successful response for ``api_country_groups_get``."""

    model_config = ConfigDict(extra="forbid")

    countryGroup: GeoPayload


class CityGetSuccess(BaseModel):
    """Successful response for ``api_cities_get``."""

    model_config = ConfigDict(extra="forbid")

    city: GeoPayload


class StateGetSuccess(BaseModel):
    """Successful response for ``api_states_get``."""

    model_config = ConfigDict(extra="forbid")

    state: GeoPayload


class ZipcodeGetSuccess(BaseModel):
    """Successful response for ``api_zipcodes_get``."""

    model_config = ConfigDict(extra="forbid")

    zipcode: GeoPayload


class _ListSuccess(BaseModel):
    """Preserve an absent upstream metadata root in collection results."""

    model_config = ConfigDict(extra="forbid")

    meta: GeoMeta | None = None

    @model_serializer(mode="wrap")
    def serialize_optional_meta(self, handler: SerializerFunctionWrapHandler) -> dict[str, object]:
        """Avoid fabricating an empty metadata root when Billy omits it."""

        serialized = cast(dict[str, object], handler(self))
        return {key: value for key, value in serialized.items() if value is not None}


class CountryGroupsListSuccess(_ListSuccess):
    """Successful response for ``api_country_groups_list``."""

    countryGroups: list[GeoPayload]


class CitiesListSuccess(_ListSuccess):
    """Successful response for ``api_cities_list``."""

    cities: list[GeoPayload]


class StatesListSuccess(_ListSuccess):
    """Successful response for ``api_states_list``."""

    states: list[GeoPayload]


class ZipcodesListSuccess(_ListSuccess):
    """Successful response for ``api_zipcodes_list``."""

    zipcodes: list[GeoPayload]


def get_country_group(
    client: BillyHttpClient, request: CountryGroupGetRequest
) -> CountryGroupGetSuccess | ToolError:
    """Retrieve one country group through its documented singular root."""

    record = _get_record(client, request, "/countryGroups", "countryGroup")
    if isinstance(record, ToolError):
        return record
    try:
        return CountryGroupGetSuccess(countryGroup=GeoPayload.model_validate(record))
    except ValidationError:
        return _unexpected_response("countryGroup")


def get_city(client: BillyHttpClient, request: CityGetRequest) -> CityGetSuccess | ToolError:
    """Retrieve one city through its documented singular root."""

    record = _get_record(client, request, "/cities", "city")
    if isinstance(record, ToolError):
        return record
    try:
        return CityGetSuccess(city=GeoPayload.model_validate(record))
    except ValidationError:
        return _unexpected_response("city")


def get_state(client: BillyHttpClient, request: StateGetRequest) -> StateGetSuccess | ToolError:
    """Retrieve one state through its documented singular root."""

    record = _get_record(client, request, "/states", "state")
    if isinstance(record, ToolError):
        return record
    try:
        return StateGetSuccess(state=GeoPayload.model_validate(record))
    except ValidationError:
        return _unexpected_response("state")


def get_zipcode(
    client: BillyHttpClient, request: ZipcodeGetRequest
) -> ZipcodeGetSuccess | ToolError:
    """Retrieve one zipcode through its documented singular root."""

    record = _get_record(client, request, "/zipcodes", "zipcode")
    if isinstance(record, ToolError):
        return record
    try:
        return ZipcodeGetSuccess(zipcode=GeoPayload.model_validate(record))
    except ValidationError:
        return _unexpected_response("zipcode")


def list_country_groups(
    client: BillyHttpClient, request: CountryGroupsListRequest
) -> CountryGroupsListSuccess | ToolError:
    """Retrieve country groups and their optional documented paging metadata."""

    records = _list_records(client, request, "/countryGroups", "countryGroups")
    if isinstance(records, ToolError):
        return records
    values, meta = records
    try:
        return CountryGroupsListSuccess(
            countryGroups=[GeoPayload.model_validate(value) for value in values], meta=meta
        )
    except ValidationError:
        return _unexpected_response("countryGroups")


def list_cities(
    client: BillyHttpClient, request: CitiesListRequest
) -> CitiesListSuccess | ToolError:
    """Retrieve country-scoped cities and optional paging metadata."""

    records = _list_records(client, request, "/cities", "cities")
    if isinstance(records, ToolError):
        return records
    values, meta = records
    try:
        return CitiesListSuccess(
            cities=[GeoPayload.model_validate(value) for value in values], meta=meta
        )
    except ValidationError:
        return _unexpected_response("cities")


def list_states(
    client: BillyHttpClient, request: StatesListRequest
) -> StatesListSuccess | ToolError:
    """Retrieve country-scoped states and optional paging metadata."""

    records = _list_records(client, request, "/states", "states")
    if isinstance(records, ToolError):
        return records
    values, meta = records
    try:
        return StatesListSuccess(
            states=[GeoPayload.model_validate(value) for value in values], meta=meta
        )
    except ValidationError:
        return _unexpected_response("states")


def list_zipcodes(
    client: BillyHttpClient, request: ZipcodesListRequest
) -> ZipcodesListSuccess | ToolError:
    """Retrieve country-scoped zipcodes and optional paging metadata."""

    records = _list_records(client, request, "/zipcodes", "zipcodes")
    if isinstance(records, ToolError):
        return records
    values, meta = records
    try:
        return ZipcodesListSuccess(
            zipcodes=[GeoPayload.model_validate(value) for value in values], meta=meta
        )
    except ValidationError:
        return _unexpected_response("zipcodes")


def register_geo_read_tools(server: FastMCP, client: BillyHttpClient) -> None:
    """Register exactly the eight typed frozen geo read tools."""

    def api_country_groups_get(
        id: str = Field(min_length=1), include: str | None = Field(default=None, min_length=1)
    ) -> CountryGroupGetSuccess | ToolError:
        """Read one Billy country group by identifier."""

        return get_country_group(client, CountryGroupGetRequest(id=id, include=include))

    def api_country_groups_list(
        page: int = Field(default=1, ge=1),
        pageSize: int = Field(default=DEFAULT_PAGE_SIZE, ge=1, le=MAX_PAGE_SIZE),
        include: str | None = Field(default=None, min_length=1),
        sortProperty: str | None = None,
        sortDirection: SortDirection | None = None,
    ) -> CountryGroupsListSuccess | ToolError:
        """Read country groups with documented paging, inclusion, and sorting only."""

        return list_country_groups(
            client,
            CountryGroupsListRequest(
                page=page,
                pageSize=pageSize,
                include=include,
                sortProperty=sortProperty,
                sortDirection=sortDirection,
            ),
        )

    def api_cities_get(
        id: str = Field(min_length=1), include: str | None = Field(default=None, min_length=1)
    ) -> CityGetSuccess | ToolError:
        """Read one Billy city by identifier."""

        return get_city(client, CityGetRequest(id=id, include=include))

    def api_cities_list(
        countryId: str = Field(min_length=1),
        page: int = Field(default=1, ge=1),
        pageSize: int = Field(default=DEFAULT_PAGE_SIZE, ge=1, le=MAX_PAGE_SIZE),
        include: str | None = Field(default=None, min_length=1),
        sortProperty: str | None = None,
        sortDirection: SortDirection | None = None,
    ) -> CitiesListSuccess | ToolError:
        """Read country-scoped Billy cities with documented list fields only."""

        return list_cities(
            client,
            CitiesListRequest(
                countryId=countryId,
                page=page,
                pageSize=pageSize,
                include=include,
                sortProperty=sortProperty,
                sortDirection=sortDirection,
            ),
        )

    def api_states_get(
        id: str = Field(min_length=1), include: str | None = Field(default=None, min_length=1)
    ) -> StateGetSuccess | ToolError:
        """Read one Billy state by identifier."""

        return get_state(client, StateGetRequest(id=id, include=include))

    def api_states_list(
        countryId: str = Field(min_length=1),
        page: int = Field(default=1, ge=1),
        pageSize: int = Field(default=DEFAULT_PAGE_SIZE, ge=1, le=MAX_PAGE_SIZE),
        include: str | None = Field(default=None, min_length=1),
        sortProperty: str | None = None,
        sortDirection: SortDirection | None = None,
    ) -> StatesListSuccess | ToolError:
        """Read country-scoped Billy states with documented list fields only."""

        return list_states(
            client,
            StatesListRequest(
                countryId=countryId,
                page=page,
                pageSize=pageSize,
                include=include,
                sortProperty=sortProperty,
                sortDirection=sortDirection,
            ),
        )

    def api_zipcodes_get(
        id: str = Field(min_length=1), include: str | None = Field(default=None, min_length=1)
    ) -> ZipcodeGetSuccess | ToolError:
        """Read one Billy zipcode by identifier."""

        return get_zipcode(client, ZipcodeGetRequest(id=id, include=include))

    def api_zipcodes_list(
        countryId: str = Field(min_length=1),
        page: int = Field(default=1, ge=1),
        pageSize: int = Field(default=DEFAULT_PAGE_SIZE, ge=1, le=MAX_PAGE_SIZE),
        include: str | None = Field(default=None, min_length=1),
        sortProperty: str | None = None,
        sortDirection: SortDirection | None = None,
    ) -> ZipcodesListSuccess | ToolError:
        """Read country-scoped Billy zipcodes with documented list fields only."""

        return list_zipcodes(
            client,
            ZipcodesListRequest(
                countryId=countryId,
                page=page,
                pageSize=pageSize,
                include=include,
                sortProperty=sortProperty,
                sortDirection=sortDirection,
            ),
        )

    server.tool(name="api_country_groups_get", description="Read one Billy country group.")(
        api_country_groups_get
    )
    server.tool(
        name="api_country_groups_list",
        description="Read Billy country groups with documented paging, inclusion, and sorting.",
    )(api_country_groups_list)
    server.tool(name="api_cities_get", description="Read one Billy city.")(api_cities_get)
    server.tool(
        name="api_cities_list",
        description="Read Billy cities scoped to a country with documented list fields.",
    )(api_cities_list)
    server.tool(name="api_states_get", description="Read one Billy state.")(api_states_get)
    server.tool(
        name="api_states_list",
        description="Read Billy states scoped to a country with documented list fields.",
    )(api_states_list)
    server.tool(name="api_zipcodes_get", description="Read one Billy zipcode.")(api_zipcodes_get)
    server.tool(
        name="api_zipcodes_list",
        description="Read Billy zipcodes scoped to a country with documented list fields.",
    )(api_zipcodes_list)


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
) -> tuple[list[Mapping[str, object]], GeoMeta | None] | ToolError:
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
        return records, None if meta is None else GeoMeta.model_validate(meta)
    except ValidationError:
        return _unexpected_response("meta")


def _response_mapping(response: BillyResponse) -> Mapping[str, object] | None:
    """Narrow a successful client payload to the JSON object expected by these reads."""

    return _object_mapping(response.data)


def _object_mapping(value: object) -> Mapping[str, object] | None:
    """Narrow decoded JSON values to object mappings without coercion."""

    if not isinstance(value, Mapping):
        return None
    return cast(Mapping[str, object], value)


def _unexpected_response(root: str) -> ToolError:
    """Avoid inventing a success shape when Billy omits a documented response root."""

    return ToolError(
        code=StableErrorCode.BILLY_ERROR,
        message="Billy API response did not contain a documented geo root.",
        details={"expected_root": root},
    )
