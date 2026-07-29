"""Contract tests for the frozen typed Billy geo API tools."""

from __future__ import annotations

import httpx
import pytest
from fastmcp import FastMCP
from pydantic import BaseModel, ValidationError

from billy_mcp.api.geo_reads import (
    CitiesListRequest,
    CitiesListSuccess,
    CityGetRequest,
    CityGetSuccess,
    CountryGroupGetRequest,
    CountryGroupGetSuccess,
    CountryGroupsListRequest,
    CountryGroupsListSuccess,
    SortDirection,
    StateGetRequest,
    StateGetSuccess,
    StatesListRequest,
    StatesListSuccess,
    ZipcodeGetRequest,
    ZipcodeGetSuccess,
    ZipcodesListRequest,
    ZipcodesListSuccess,
    get_city,
    get_country_group,
    get_state,
    get_zipcode,
    list_cities,
    list_country_groups,
    list_states,
    list_zipcodes,
    register_geo_read_tools,
)
from billy_mcp.client import BillyHttpClient
from billy_mcp.models import StableErrorCode, ToolError


def make_client(handler: httpx.MockTransport) -> BillyHttpClient:
    """Create a token-backed locked client against an in-process mock transport."""

    return BillyHttpClient(lambda: "test-token", transport=handler)


def test_singular_reads_encode_ids_and_map_each_documented_root() -> None:
    requests: list[httpx.Request] = []
    roots = iter(
        (
            ("countryGroup", {"id": "group /?", "name": "Europe"}),
            ("city", {"id": "city /?", "name": "Copenhagen"}),
            ("state", {"id": "state /?", "name": "Capital Region"}),
            ("zipcode", {"id": "zip /?", "zipcode": "2100"}),
        )
    )

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        root, value = next(roots)
        return httpx.Response(200, json={root: value})

    client = make_client(httpx.MockTransport(handler))
    country_group = get_country_group(
        client, CountryGroupGetRequest(id="group /?", include="memberCountries")
    )
    city = get_city(client, CityGetRequest(id="city /?", include="country"))
    state = get_state(client, StateGetRequest(id="state /?", include="country"))
    zipcode = get_zipcode(client, ZipcodeGetRequest(id="zip /?", include="city"))

    assert isinstance(country_group, CountryGroupGetSuccess)
    assert country_group.countryGroup.model_dump() == {"id": "group /?", "name": "Europe"}
    assert isinstance(city, CityGetSuccess)
    assert city.city.model_dump() == {"id": "city /?", "name": "Copenhagen"}
    assert isinstance(state, StateGetSuccess)
    assert state.state.model_dump() == {"id": "state /?", "name": "Capital Region"}
    assert isinstance(zipcode, ZipcodeGetSuccess)
    assert zipcode.zipcode.model_dump() == {"id": "zip /?", "zipcode": "2100"}
    assert [str(request.url) for request in requests] == [
        "https://api.billysbilling.com/v2/countryGroups/group%20%2F%3F?include=memberCountries",
        "https://api.billysbilling.com/v2/cities/city%20%2F%3F?include=country",
        "https://api.billysbilling.com/v2/states/state%20%2F%3F?include=country",
        "https://api.billysbilling.com/v2/zipcodes/zip%20%2F%3F?include=city",
    ]
    assert all(request.method == "GET" for request in requests)


def test_lists_use_only_the_frozen_queries_and_preserve_paging() -> None:
    requests: list[httpx.Request] = []
    roots = {
        "/v2/countryGroups": "countryGroups",
        "/v2/cities": "cities",
        "/v2/states": "states",
        "/v2/zipcodes": "zipcodes",
    }

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        root = roots[request.url.path]
        return httpx.Response(
            200,
            json={
                root: [{"id": root, "name": root}],
                "meta": {
                    "paging": {
                        "page": 2,
                        "pageCount": 3,
                        "pageSize": 25,
                        "total": 60,
                        "firstUrl": f"/{root}?page=1",
                        "previousUrl": f"/{root}?page=1",
                        "nextUrl": f"/{root}?page=3",
                        "lastUrl": f"/{root}?page=3",
                    }
                },
            },
        )

    client = make_client(httpx.MockTransport(handler))
    country_groups = list_country_groups(
        client,
        CountryGroupsListRequest(
            page=2,
            pageSize=25,
            include="memberCountries",
            sortProperty="name",
            sortDirection=SortDirection.ASC,
        ),
    )
    cities = list_cities(
        client,
        CitiesListRequest(
            countryId="DK",
            page=2,
            pageSize=25,
            include="country",
            sortProperty="name",
            sortDirection=SortDirection.DESC,
        ),
    )
    states = list_states(
        client,
        StatesListRequest(
            countryId="US",
            page=2,
            pageSize=25,
            include="country",
            sortProperty="name",
            sortDirection=SortDirection.ASC,
        ),
    )
    zipcodes = list_zipcodes(
        client,
        ZipcodesListRequest(
            countryId="DK",
            page=2,
            pageSize=25,
            include="city",
            sortProperty="zipcode",
            sortDirection=SortDirection.DESC,
        ),
    )

    assert isinstance(country_groups, CountryGroupsListSuccess)
    assert country_groups.countryGroups[0].model_dump()["id"] == "countryGroups"
    assert isinstance(cities, CitiesListSuccess)
    assert cities.cities[0].model_dump()["id"] == "cities"
    assert isinstance(states, StatesListSuccess)
    assert states.states[0].model_dump()["id"] == "states"
    assert isinstance(zipcodes, ZipcodesListSuccess)
    assert zipcodes.zipcodes[0].model_dump()["id"] == "zipcodes"
    for result in (country_groups, cities, states, zipcodes):
        assert result.meta is not None and result.meta.paging is not None
        assert result.meta.paging.page_count == 3
        assert result.meta.paging.page_size == 25
        assert result.meta.paging.next_url is not None and result.meta.paging.next_url.endswith(
            "?page=3"
        )
    assert requests[0].url.params == httpx.QueryParams(
        {
            "page": "2",
            "pageSize": "25",
            "include": "memberCountries",
            "sortProperty": "name",
            "sortDirection": "ASC",
        }
    )
    assert requests[1].url.params == httpx.QueryParams(
        {
            "page": "2",
            "pageSize": "25",
            "include": "country",
            "sortProperty": "name",
            "sortDirection": "DESC",
            "countryId": "DK",
        }
    )
    assert requests[2].url.params == httpx.QueryParams(
        {
            "page": "2",
            "pageSize": "25",
            "include": "country",
            "sortProperty": "name",
            "sortDirection": "ASC",
            "countryId": "US",
        }
    )
    assert requests[3].url.params == httpx.QueryParams(
        {
            "page": "2",
            "pageSize": "25",
            "include": "city",
            "sortProperty": "zipcode",
            "sortDirection": "DESC",
            "countryId": "DK",
        }
    )
    assert "countryId" not in requests[0].url.params
    assert all("countryId" in request.url.params for request in requests[1:])


def test_lists_preserve_absent_optional_meta_without_fabricating_it() -> None:
    result = list_country_groups(
        make_client(
            httpx.MockTransport(lambda request: httpx.Response(200, json={"countryGroups": []}))
        ),
        CountryGroupsListRequest(),
    )

    assert isinstance(result, CountryGroupsListSuccess)
    assert result.meta is None
    assert result.model_dump() == {"countryGroups": []}


@pytest.mark.parametrize(
    "request_type", [CitiesListRequest, StatesListRequest, ZipcodesListRequest]
)
def test_country_id_is_required_only_for_geo_dependent_lists(
    request_type: type[BaseModel],
) -> None:
    with pytest.raises(ValidationError, match="countryId"):
        request_type.model_validate({})
    with pytest.raises(ValidationError, match="countryId"):
        request_type.model_validate({"countryId": ""})

    assert CountryGroupsListRequest().query_params() == {"page": 1, "pageSize": 1000}
    assert CityGetRequest(id="city-1").query_params() == {}
    with pytest.raises(ValidationError, match="countryId"):
        CityGetRequest.model_validate({"id": "city-1", "countryId": "DK"})


@pytest.mark.parametrize(
    ("request_type", "values", "field"),
    [
        (CountryGroupsListRequest, {"page": 0}, "page"),
        (CountryGroupsListRequest, {"pageSize": 0}, "pageSize"),
        (CountryGroupsListRequest, {"pageSize": 1001}, "pageSize"),
        (CountryGroupsListRequest, {"sortDirection": "DOWN"}, "sortDirection"),
        (CountryGroupsListRequest, {"include": ""}, "include"),
        (CountryGroupsListRequest, {"offset": 0}, "offset"),
        (CountryGroupsListRequest, {"countryId": "DK"}, "countryId"),
        (CitiesListRequest, {"countryId": "DK", "stateId": "state-1"}, "stateId"),
        (StatesListRequest, {"countryId": "DK", "cityId": "city-1"}, "cityId"),
        (ZipcodesListRequest, {"countryId": "DK", "parentId": "parent-1"}, "parentId"),
        (CitiesListRequest, {"countryId": "DK", "q": "Copenhagen"}, "q"),
        (StatesListRequest, {"countryId": "DK", "unexpected": "value"}, "unexpected"),
        (ZipcodesListRequest, {"countryId": "DK", "offset": 0}, "offset"),
        (CountryGroupGetRequest, {"id": "group-1", "page": 1}, "page"),
        (ZipcodeGetRequest, {"id": "zipcode-1", "include": ""}, "include"),
    ],
)
def test_requests_reject_undeclared_fields_and_invalid_boundaries(
    request_type: type[BaseModel], values: dict[str, object], field: str
) -> None:
    with pytest.raises(ValidationError, match=field):
        request_type.model_validate(values)


@pytest.mark.parametrize("error_code", ["AUTHENTICATION_REQUIRED", "OAUTH_INVALID_ACCESS_TOKEN"])
def test_documented_authentication_errors_remain_typed_for_all_eight_tools(error_code: str) -> None:
    client = make_client(
        httpx.MockTransport(lambda request: httpx.Response(401, json={"errorCode": error_code}))
    )
    results = (
        get_country_group(client, CountryGroupGetRequest(id="group-1")),
        list_country_groups(client, CountryGroupsListRequest()),
        get_city(client, CityGetRequest(id="city-1")),
        list_cities(client, CitiesListRequest(countryId="DK")),
        get_state(client, StateGetRequest(id="state-1")),
        list_states(client, StatesListRequest(countryId="DK")),
        get_zipcode(client, ZipcodeGetRequest(id="zipcode-1")),
        list_zipcodes(client, ZipcodesListRequest(countryId="DK")),
    )

    assert all(isinstance(result, ToolError) for result in results)
    assert {result.code for result in results if isinstance(result, ToolError)} == {
        StableErrorCode.AUTH_REQUIRED
    }


def test_undeclared_response_root_returns_a_typed_error() -> None:
    result = get_zipcode(
        make_client(httpx.MockTransport(lambda request: httpx.Response(200, json={"wrong": {}}))),
        ZipcodeGetRequest(id="zipcode-1"),
    )

    assert isinstance(result, ToolError)
    assert result.code is StableErrorCode.BILLY_ERROR
    assert result.details == {"expected_root": "zipcode"}


@pytest.mark.asyncio
async def test_registration_exposes_exactly_eight_flat_geo_tools() -> None:
    roots = {
        "/v2/countryGroups": "countryGroups",
        "/v2/cities": "cities",
        "/v2/states": "states",
        "/v2/zipcodes": "zipcodes",
    }

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={roots[request.url.path]: []})

    server = FastMCP("geo-reads-test")
    register_geo_read_tools(server, make_client(httpx.MockTransport(handler)))

    tools = {tool.name: tool for tool in await server.list_tools()}
    assert set(tools) == {
        "api_country_groups_get",
        "api_country_groups_list",
        "api_cities_get",
        "api_cities_list",
        "api_states_get",
        "api_states_list",
        "api_zipcodes_get",
        "api_zipcodes_list",
    }
    for name in (
        "api_country_groups_get",
        "api_cities_get",
        "api_states_get",
        "api_zipcodes_get",
    ):
        assert set(tools[name].parameters["properties"]) == {"id", "include"}
    assert set(tools["api_country_groups_list"].parameters["properties"]) == {
        "page",
        "pageSize",
        "include",
        "sortProperty",
        "sortDirection",
    }
    for name in ("api_cities_list", "api_states_list", "api_zipcodes_list"):
        properties = tools[name].parameters["properties"]
        assert set(properties) == {
            "countryId",
            "page",
            "pageSize",
            "include",
            "sortProperty",
            "sortDirection",
        }
        assert "countryId" in tools[name].parameters["required"]
        assert "offset" not in properties
        assert "stateId" not in properties
        assert "parentId" not in properties
    assert (
        await server.call_tool("api_country_groups_list", {"page": 1, "pageSize": 1000})
    ).structured_content == {"result": {"countryGroups": []}}
    assert (
        await server.call_tool("api_cities_list", {"countryId": "DK", "page": 1, "pageSize": 1000})
    ).structured_content == {"result": {"cities": []}}
