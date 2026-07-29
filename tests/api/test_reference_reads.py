"""Contract tests for the frozen, read-only Billy reference-data tools."""

from __future__ import annotations

import asyncio

import httpx
import pytest
from fastmcp import FastMCP
from fastmcp.tools.base import ToolResult
from pydantic import ValidationError

from billy_mcp.api.reference_reads import (
    CountryGetInput,
    CountryGetSuccess,
    CountryListInput,
    CountryListSuccess,
    CurrencyGetInput,
    CurrencyGetSuccess,
    CurrencyListInput,
    CurrencyListSuccess,
    LocaleGetInput,
    LocaleGetSuccess,
    LocaleListInput,
    LocaleListSuccess,
    countries_get,
    countries_list,
    currencies_get,
    currencies_list,
    locales_get,
    locales_list,
    register_reference_reads,
)
from billy_mcp.client import BillyHttpClient
from billy_mcp.models import StableErrorCode, ToolError


def test_singular_tools_use_documented_paths_and_map_singular_roots() -> None:
    requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        payloads: dict[str, object] = {
            "/v2/currencies/DKK": {"currency": {"id": "DKK", "symbol": "kr"}},
            "/v2/countries/DK": {"country": {"id": "DK", "name": "Denmark"}},
            "/v2/locales/da_DK": {"locale": {"id": "da_DK", "label": "Dansk"}},
        }
        return httpx.Response(200, json=payloads[request.url.path])

    client = BillyHttpClient(lambda: "token", transport=httpx.MockTransport(handler))

    currency = currencies_get(client, CurrencyGetInput(id="DKK", include="symbol"))
    country = countries_get(client, CountryGetInput(id="DK"))
    locale = locales_get(client, LocaleGetInput(id="da_DK"))

    assert isinstance(currency, CurrencyGetSuccess)
    assert currency.currency.model_dump() == {"id": "DKK", "symbol": "kr"}
    assert isinstance(country, CountryGetSuccess)
    assert country.country.model_dump() == {"id": "DK", "name": "Denmark"}
    assert isinstance(locale, LocaleGetSuccess)
    assert locale.locale.model_dump() == {"id": "da_DK", "label": "Dansk"}
    assert [request.url.path for request in requests] == [
        "/v2/currencies/DKK",
        "/v2/countries/DK",
        "/v2/locales/da_DK",
    ]
    assert dict(requests[0].url.params) == {"include": "symbol"}
    assert dict(requests[1].url.params) == {}


def test_list_tools_map_plural_roots_and_optional_paging() -> None:
    requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        payloads: dict[str, object] = {
            "/v2/currencies": {
                "currencies": [{"id": "DKK", "code": "DKK"}],
                "meta": {
                    "paging": {
                        "page": 1,
                        "pageCount": 2,
                        "pageSize": 1000,
                        "total": 1001,
                        "firstUrl": "https://example.test/first",
                        "previousUrl": None,
                        "nextUrl": "https://example.test/next",
                        "lastUrl": "https://example.test/last",
                    }
                },
            },
            "/v2/countries": {"countries": [{"id": "DK", "name": "Denmark"}]},
            "/v2/locales": {"locales": [{"id": "da_DK", "label": "Dansk"}], "meta": {}},
        }
        return httpx.Response(200, json=payloads[request.url.path])

    client = BillyHttpClient(lambda: "token", transport=httpx.MockTransport(handler))

    currencies = currencies_list(
        client,
        CurrencyListInput(
            page=1,
            pageSize=1000,
            include="currency.symbol",
            sortProperty="code",
            sortDirection="ASC",
        ),
    )
    countries = countries_list(client, CountryListInput(page=2, pageSize=1))
    locales = locales_list(client, LocaleListInput(page=3, pageSize=1000, sortDirection="DESC"))

    assert isinstance(currencies, CurrencyListSuccess)
    assert currencies.currencies[0].model_dump() == {"id": "DKK", "code": "DKK"}
    assert currencies.paging is not None
    assert currencies.paging.page_count == 2
    assert currencies.paging.next_url == "https://example.test/next"
    assert isinstance(countries, CountryListSuccess)
    assert countries.countries[0].model_dump() == {"id": "DK", "name": "Denmark"}
    assert countries.paging is None
    assert isinstance(locales, LocaleListSuccess)
    assert locales.locales[0].model_dump() == {"id": "da_DK", "label": "Dansk"}
    assert locales.paging is None
    assert dict(requests[0].url.params) == {
        "page": "1",
        "pageSize": "1000",
        "include": "currency.symbol",
        "sortProperty": "code",
        "sortDirection": "ASC",
    }
    assert dict(requests[1].url.params) == {"page": "2", "pageSize": "1"}
    assert dict(requests[2].url.params) == {
        "page": "3",
        "pageSize": "1000",
        "sortDirection": "DESC",
    }


def test_list_inputs_enforce_documented_paging_bounds_and_sort_direction() -> None:
    assert CurrencyListInput(page=1, pageSize=1000).page_size == 1000
    assert CountryListInput(page=1, pageSize=1).page_size == 1
    assert LocaleListInput(page=2, pageSize=999).page == 2

    with pytest.raises(ValidationError):
        CurrencyListInput(page=0)
    with pytest.raises(ValidationError):
        CountryListInput(pageSize=1001)
    with pytest.raises(ValidationError):
        LocaleListInput.model_validate({"sortDirection": "ascending"})


def test_all_tools_return_typed_authentication_errors() -> None:
    client = BillyHttpClient(
        lambda: "invalid-token",
        transport=httpx.MockTransport(
            lambda request: httpx.Response(401, json={"errorCode": "OAUTH_INVALID_ACCESS_TOKEN"})
        ),
    )

    results = [
        currencies_get(client, CurrencyGetInput(id="DKK")),
        currencies_list(client, CurrencyListInput()),
        countries_get(client, CountryGetInput(id="DK")),
        countries_list(client, CountryListInput()),
        locales_get(client, LocaleGetInput(id="da_DK")),
        locales_list(client, LocaleListInput()),
    ]

    for result in results:
        assert isinstance(result, ToolError)
        assert result.code is StableErrorCode.AUTH_REQUIRED


def test_registration_exposes_only_the_six_typed_reference_data_tools() -> None:
    server = FastMCP("reference-data-test")
    client = BillyHttpClient(
        lambda: "token",
        transport=httpx.MockTransport(
            lambda request: httpx.Response(200, json={"currency": {"id": "DKK"}})
        ),
    )

    register_reference_reads(server, client)
    tools = {tool.name: tool for tool in asyncio.run(server.list_tools())}

    assert set(tools) == {
        "api_currencies_get",
        "api_currencies_list",
        "api_countries_get",
        "api_countries_list",
        "api_locales_get",
        "api_locales_list",
    }
    assert tools["api_currencies_get"].parameters["properties"]["input"]["properties"] == {
        "id": {"minLength": 1, "type": "string"},
        "include": {
            "anyOf": [{"minLength": 1, "type": "string"}, {"type": "null"}],
            "default": None,
        },
    }
    assert tools["api_currencies_list"].parameters["properties"]["input"]["properties"].keys() == {
        "page",
        "pageSize",
        "include",
        "sortProperty",
        "sortDirection",
    }

    result = asyncio.run(server.call_tool("api_currencies_get", {"input": {"id": "DKK"}}))

    assert isinstance(result, ToolResult)
    assert result.structured_content == {"result": {"currency": {"id": "DKK"}}}
