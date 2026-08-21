"""Contract tests for the catalogue read-only Billy API tool registration."""

from __future__ import annotations

import asyncio
from collections.abc import Callable

import httpx
import pytest
from fastmcp import FastMCP
from pydantic import ValidationError

from billy_mcp.api.catalog_reads import (
    CatalogGetRequest,
    CatalogListRequest,
    CatalogReadService,
    ProductGetSuccess,
    ProductListSuccess,
    ProductPriceGetSuccess,
    ProductPriceListSuccess,
    SortDirection,
    register_catalog_read_tools,
)
from billy_mcp.client import BillyHttpClient
from billy_mcp.models import StableErrorCode, ToolError

MockHandler = Callable[[httpx.Request], httpx.Response]
ClientFactory = Callable[[MockHandler], tuple[BillyHttpClient, list[httpx.Request]]]


@pytest.fixture
def client_factory() -> ClientFactory:
    """Provide a locked client connected only to an in-process mock transport."""

    def build(handler: MockHandler) -> tuple[BillyHttpClient, list[httpx.Request]]:
        requests: list[httpx.Request] = []

        def recording_handler(request: httpx.Request) -> httpx.Response:
            requests.append(request)
            return handler(request)

        return (
            BillyHttpClient(
                lambda: "catalogue-token", transport=httpx.MockTransport(recording_handler)
            ),
            requests,
        )

    return build


def test_registers_exactly_the_four_typed_catalogue_tools(client_factory: ClientFactory) -> None:
    client, requests = client_factory(
        lambda request: httpx.Response(200, json={"product": {"id": "registered-product"}})
    )
    server = FastMCP("catalogue-contract-test")

    register_catalog_read_tools(server, client)

    tools = asyncio.run(server.list_tools())
    tool_names = {tool.name for tool in tools}
    assert tool_names == {
        "api_product_prices_get",
        "api_product_prices_list",
        "api_products_get",
        "api_products_list",
    }
    parameters = {tool.name: tool.parameters["properties"] for tool in tools}
    assert set(parameters["api_products_get"]) == {"id", "include"}
    assert set(parameters["api_product_prices_get"]) == {"id", "include"}
    assert set(parameters["api_products_list"]) == {
        "page",
        "pageSize",
        "include",
        "sortProperty",
        "sortDirection",
    }
    assert set(parameters["api_product_prices_list"]) == {
        "page",
        "pageSize",
        "include",
        "sortProperty",
        "sortDirection",
    }
    result = asyncio.run(server.call_tool("api_products_get", {"id": "registered-product"}))
    assert result.structured_content == {"result": {"product": {"id": "registered-product"}}}
    assert [request.url.path for request in requests] == ["/v2/products/registered-product"]


def test_singular_reads_use_documented_paths_and_map_singular_roots(
    client_factory: ClientFactory,
) -> None:
    product_client, product_requests = client_factory(
        lambda request: httpx.Response(200, json={"product": {"id": "product-1", "name": "Desk"}})
    )
    product_price_client, price_requests = client_factory(
        lambda request: httpx.Response(
            200, json={"productPrice": {"id": "price-1", "amount": 199.95}}
        )
    )

    product_result = CatalogReadService(product_client).products_get(
        CatalogGetRequest(id="product-1", include="productPrices")
    )
    price_result = CatalogReadService(product_price_client).product_prices_get(
        CatalogGetRequest(id="price-1")
    )

    assert isinstance(product_result, ProductGetSuccess)
    assert product_result.product == {"id": "product-1", "name": "Desk"}
    assert str(product_requests[0].url) == (
        "https://api.billysbilling.com/v2/products/product-1?include=productPrices"
    )
    assert isinstance(price_result, ProductPriceGetSuccess)
    assert price_result.productPrice == {"id": "price-1", "amount": 199.95}
    assert str(price_requests[0].url) == "https://api.billysbilling.com/v2/productPrices/price-1"


def test_list_reads_map_plural_roots_and_optional_paging(client_factory: ClientFactory) -> None:
    products_client, product_requests = client_factory(
        lambda request: httpx.Response(
            200,
            json={
                "products": [{"id": "product-1"}],
                "meta": {"paging": {"page": 1, "pageCount": 2, "pageSize": 1000, "total": 1001}},
            },
        )
    )
    prices_client, price_requests = client_factory(
        lambda request: httpx.Response(200, json={"productPrices": [{"id": "price-1"}]})
    )
    request = CatalogListRequest(
        page=1,
        pageSize=1000,
        include="product",
        sortProperty="createdTime",
        sortDirection=SortDirection.DESC,
    )

    products_result = CatalogReadService(products_client).products_list(request)
    prices_result = CatalogReadService(prices_client).product_prices_list(request)

    assert isinstance(products_result, ProductListSuccess)
    assert products_result.products == [{"id": "product-1"}]
    assert products_result.paging is not None
    assert products_result.paging.model_dump() == {
        "page": 1,
        "pageCount": 2,
        "pageSize": 1000,
        "total": 1001,
    }
    assert str(product_requests[0].url) == (
        "https://api.billysbilling.com/v2/products?page=1&pageSize=1000&include=product&"
        "sortProperty=createdTime&sortDirection=DESC"
    )
    assert isinstance(prices_result, ProductPriceListSuccess)
    assert prices_result.productPrices == [{"id": "price-1"}]
    assert prices_result.paging is None
    assert str(price_requests[0].url) == (
        "https://api.billysbilling.com/v2/productPrices?page=1&pageSize=1000&include=product&"
        "sortProperty=createdTime&sortDirection=DESC"
    )


@pytest.mark.parametrize(
    ("arguments", "field"),
    [({"page": 0}, "page"), ({"pageSize": 0}, "pageSize"), ({"pageSize": 1001}, "pageSize")],
)
def test_list_input_rejects_undocumented_paging_boundaries(
    arguments: dict[str, int], field: str
) -> None:
    with pytest.raises(ValidationError) as failure:
        CatalogListRequest.model_validate(arguments)

    assert failure.value.errors()[0]["loc"] == (field,)


def test_authentication_errors_remain_typed_for_all_catalogue_reads(
    client_factory: ClientFactory,
) -> None:
    def unauthorized(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            401,
            json={"errorCode": "AUTHENTICATION_REQUIRED", "meta": {"statusCode": 401}},
        )

    client, requests = client_factory(unauthorized)
    service = CatalogReadService(client)
    results = [
        service.products_get(CatalogGetRequest(id="product-1")),
        service.products_list(CatalogListRequest()),
        service.product_prices_get(CatalogGetRequest(id="price-1")),
        service.product_prices_list(CatalogListRequest()),
    ]

    assert all(isinstance(result, ToolError) for result in results)
    assert {result.code for result in results if isinstance(result, ToolError)} == {
        StableErrorCode.AUTH_REQUIRED
    }
    assert [request.url.path for request in requests] == [
        "/v2/products/product-1",
        "/v2/products",
        "/v2/productPrices/price-1",
        "/v2/productPrices",
    ]
