"""Typed, read-only reference-data tools for the frozen Billy API contract."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Literal, cast
from urllib.parse import quote

from fastmcp import FastMCP
from pydantic import BaseModel, ConfigDict, Field, ValidationError

from billy_mcp.client import DEFAULT_PAGE_SIZE, MAX_PAGE_SIZE, BillyHttpClient, BillyResponse
from billy_mcp.models import StableErrorCode, ToolError


class _ReferenceInput(BaseModel):
    """Common strict configuration for documented reference-data inputs."""

    model_config = ConfigDict(extra="forbid", populate_by_name=True)


class ReferenceGetInput(_ReferenceInput):
    """Documented request values for a single reference-data record."""

    id: str = Field(min_length=1)
    include: str | None = Field(default=None, min_length=1)


class ReferenceListInput(_ReferenceInput):
    """The complete documented query surface shared by reference-data lists."""

    page: int = Field(default=1, ge=1)
    page_size: int = Field(
        default=DEFAULT_PAGE_SIZE,
        alias="pageSize",
        ge=1,
        le=MAX_PAGE_SIZE,
    )
    include: str | None = Field(default=None, min_length=1)
    sort_property: str | None = Field(default=None, alias="sortProperty", min_length=1)
    sort_direction: Literal["ASC", "DESC"] | None = Field(default=None, alias="sortDirection")


class CurrencyGetInput(ReferenceGetInput):
    """Request input for ``api_currencies_get``."""


class CurrencyListInput(ReferenceListInput):
    """Request input for ``api_currencies_list``."""


class CountryGetInput(ReferenceGetInput):
    """Request input for ``api_countries_get``."""


class CountryListInput(ReferenceListInput):
    """Request input for ``api_countries_list``."""


class LocaleGetInput(ReferenceGetInput):
    """Request input for ``api_locales_get``."""


class LocaleListInput(ReferenceListInput):
    """Request input for ``api_locales_list``."""


class ReferenceRecord(BaseModel):
    """An opaque Billy reference record; field schemas remain intentionally unfrozen."""

    model_config = ConfigDict(extra="allow")


class Paging(BaseModel):
    """The optional paging envelope documented for collection responses."""

    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    page: int | None = None
    page_count: int | None = Field(default=None, alias="pageCount")
    page_size: int | None = Field(default=None, alias="pageSize")
    total: int | None = None
    first_url: str | None = Field(default=None, alias="firstUrl")
    previous_url: str | None = Field(default=None, alias="previousUrl")
    next_url: str | None = Field(default=None, alias="nextUrl")
    last_url: str | None = Field(default=None, alias="lastUrl")


class CurrencyGetSuccess(BaseModel):
    """Success response for ``api_currencies_get``."""

    model_config = ConfigDict(extra="forbid")

    currency: ReferenceRecord


class CountryGetSuccess(BaseModel):
    """Success response for ``api_countries_get``."""

    model_config = ConfigDict(extra="forbid")

    country: ReferenceRecord


class LocaleGetSuccess(BaseModel):
    """Success response for ``api_locales_get``."""

    model_config = ConfigDict(extra="forbid")

    locale: ReferenceRecord


class _ReferenceListSuccess(BaseModel):
    """Common documented paging field for all reference-data list responses."""

    model_config = ConfigDict(extra="forbid")

    paging: Paging | None = None


class CurrencyListSuccess(_ReferenceListSuccess):
    """Success response for ``api_currencies_list``."""

    currencies: list[ReferenceRecord]


class CountryListSuccess(_ReferenceListSuccess):
    """Success response for ``api_countries_list``."""

    countries: list[ReferenceRecord]


class LocaleListSuccess(_ReferenceListSuccess):
    """Success response for ``api_locales_list``."""

    locales: list[ReferenceRecord]


def _invalid_response(root: str) -> ToolError:
    return ToolError(
        code=StableErrorCode.BILLY_ERROR,
        message="Billy API returned an unexpected reference-data response.",
        details={"expected_root": root},
    )


def _response_mapping(data: object, root: str) -> Mapping[str, object] | ToolError:
    if not isinstance(data, Mapping):
        return _invalid_response(root)
    return cast(Mapping[str, object], data)


def _record_from_response(data: object, root: str) -> ReferenceRecord | ToolError:
    payload = _response_mapping(data, root)
    if isinstance(payload, ToolError):
        return payload
    record = payload.get(root)
    if not isinstance(record, Mapping):
        return _invalid_response(root)
    try:
        return ReferenceRecord.model_validate(record)
    except ValidationError:
        return _invalid_response(root)


def _paging_from_response(payload: Mapping[str, object], root: str) -> Paging | ToolError | None:
    meta = payload.get("meta")
    if meta is None:
        return None
    if not isinstance(meta, Mapping):
        return _invalid_response(root)
    meta_mapping = cast(Mapping[str, object], meta)
    paging = meta_mapping.get("paging")
    if paging is None:
        return None
    if not isinstance(paging, Mapping):
        return _invalid_response(root)
    try:
        return Paging.model_validate(paging)
    except ValidationError:
        return _invalid_response(root)


def _list_from_response(
    data: object, root: str
) -> tuple[list[ReferenceRecord], Paging | None] | ToolError:
    payload = _response_mapping(data, root)
    if isinstance(payload, ToolError):
        return payload
    values = payload.get(root)
    if not isinstance(values, list):
        return _invalid_response(root)
    records: list[ReferenceRecord] = []
    for value in cast(list[object], values):
        if not isinstance(value, Mapping):
            return _invalid_response(root)
        try:
            records.append(ReferenceRecord.model_validate(value))
        except ValidationError:
            return _invalid_response(root)
    paging = _paging_from_response(payload, root)
    if isinstance(paging, ToolError):
        return paging
    return records, paging


def _get_params(input: ReferenceGetInput) -> dict[str, str]:
    return {"include": input.include} if input.include is not None else {}


def _list_params(input: ReferenceListInput) -> dict[str, int | str]:
    params: dict[str, int | str] = {"page": input.page, "pageSize": input.page_size}
    if input.include is not None:
        params["include"] = input.include
    if input.sort_property is not None:
        params["sortProperty"] = input.sort_property
    if input.sort_direction is not None:
        params["sortDirection"] = input.sort_direction
    return params


def _get_record(
    client: BillyHttpClient, path: str, root: str, input: ReferenceGetInput
) -> ReferenceRecord | ToolError:
    response = client.request("GET", path, params=_get_params(input))
    if isinstance(response, ToolError):
        return response
    return _record_from_response(response.data, root)


def _list_records(
    client: BillyHttpClient, path: str, root: str, input: ReferenceListInput
) -> tuple[list[ReferenceRecord], Paging | None] | ToolError:
    response: BillyResponse | ToolError = client.request("GET", path, params=_list_params(input))
    if isinstance(response, ToolError):
        return response
    return _list_from_response(response.data, root)


def currencies_get(
    client: BillyHttpClient, input: CurrencyGetInput
) -> CurrencyGetSuccess | ToolError:
    """Read one currency through the documented singular root."""

    record = _get_record(client, f"/currencies/{quote(input.id, safe='')}", "currency", input)
    if isinstance(record, ToolError):
        return record
    return CurrencyGetSuccess(currency=record)


def currencies_list(
    client: BillyHttpClient, input: CurrencyListInput
) -> CurrencyListSuccess | ToolError:
    """Read currencies with the only documented reference-data list controls."""

    result = _list_records(client, "/currencies", "currencies", input)
    if isinstance(result, ToolError):
        return result
    currencies, paging = result
    return CurrencyListSuccess(currencies=currencies, paging=paging)


def countries_get(client: BillyHttpClient, input: CountryGetInput) -> CountryGetSuccess | ToolError:
    """Read one country through the documented singular root."""

    record = _get_record(client, f"/countries/{quote(input.id, safe='')}", "country", input)
    if isinstance(record, ToolError):
        return record
    return CountryGetSuccess(country=record)


def countries_list(
    client: BillyHttpClient, input: CountryListInput
) -> CountryListSuccess | ToolError:
    """Read countries with the only documented reference-data list controls."""

    result = _list_records(client, "/countries", "countries", input)
    if isinstance(result, ToolError):
        return result
    countries, paging = result
    return CountryListSuccess(countries=countries, paging=paging)


def locales_get(client: BillyHttpClient, input: LocaleGetInput) -> LocaleGetSuccess | ToolError:
    """Read one locale through the documented singular root."""

    record = _get_record(client, f"/locales/{quote(input.id, safe='')}", "locale", input)
    if isinstance(record, ToolError):
        return record
    return LocaleGetSuccess(locale=record)


def locales_list(client: BillyHttpClient, input: LocaleListInput) -> LocaleListSuccess | ToolError:
    """Read locales with the only documented reference-data list controls."""

    result = _list_records(client, "/locales", "locales", input)
    if isinstance(result, ToolError):
        return result
    locales, paging = result
    return LocaleListSuccess(locales=locales, paging=paging)


def register_reference_reads(server: FastMCP, client: BillyHttpClient) -> None:
    """Register only the six implemented, typed reference-data read tools."""

    def api_currencies_get(input: CurrencyGetInput) -> CurrencyGetSuccess | ToolError:
        return currencies_get(client, input)

    def api_currencies_list(input: CurrencyListInput) -> CurrencyListSuccess | ToolError:
        return currencies_list(client, input)

    def api_countries_get(input: CountryGetInput) -> CountryGetSuccess | ToolError:
        return countries_get(client, input)

    def api_countries_list(input: CountryListInput) -> CountryListSuccess | ToolError:
        return countries_list(client, input)

    def api_locales_get(input: LocaleGetInput) -> LocaleGetSuccess | ToolError:
        return locales_get(client, input)

    def api_locales_list(input: LocaleListInput) -> LocaleListSuccess | ToolError:
        return locales_list(client, input)

    server.tool(name="api_currencies_get", description="Read one Billy currency.")(
        api_currencies_get
    )
    server.tool(name="api_currencies_list", description="List Billy currencies.")(
        api_currencies_list
    )
    server.tool(name="api_countries_get", description="Read one Billy country.")(api_countries_get)
    server.tool(name="api_countries_list", description="List Billy countries.")(api_countries_list)
    server.tool(name="api_locales_get", description="Read one Billy locale.")(api_locales_get)
    server.tool(name="api_locales_list", description="List Billy locales.")(api_locales_list)
