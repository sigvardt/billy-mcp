"""Typed, read-only catalogue tools for documented Billy product endpoints."""

from __future__ import annotations

from enum import StrEnum
from typing import cast
from urllib.parse import quote

from fastmcp import FastMCP
from pydantic import BaseModel, ConfigDict, Field

from billy_mcp.client import DEFAULT_PAGE_SIZE, MAX_PAGE_SIZE, BillyHttpClient, BillyResponse
from billy_mcp.models import StableErrorCode, ToolError


class SortDirection(StrEnum):
    """The two documented list sort directions."""

    ASC = "ASC"
    DESC = "DESC"


class CatalogGetRequest(BaseModel):
    """Documented inputs shared by product and product-price singular reads."""

    model_config = ConfigDict(extra="forbid")

    id: str = Field(min_length=1)
    include: str | None = None


class CatalogListRequest(BaseModel):
    """The complete documented list input surface for catalogue resources."""

    model_config = ConfigDict(extra="forbid")

    page: int = Field(default=1, ge=1)
    pageSize: int = Field(default=DEFAULT_PAGE_SIZE, ge=1, le=MAX_PAGE_SIZE)
    include: str | None = None
    sortProperty: str | None = None
    sortDirection: SortDirection | None = None


class Paging(BaseModel):
    """An optional upstream paging object preserved without assumed fields."""

    model_config = ConfigDict(extra="allow")


class ProductGetSuccess(BaseModel):
    """Mapped success envelope for a single documented product read."""

    model_config = ConfigDict(extra="forbid")

    product: dict[str, object]


class ProductListSuccess(BaseModel):
    """Mapped success envelope for a documented products collection read."""

    model_config = ConfigDict(extra="forbid")

    products: list[dict[str, object]]
    paging: Paging | None = None


class ProductPriceGetSuccess(BaseModel):
    """Mapped success envelope for a single documented product-price read."""

    model_config = ConfigDict(extra="forbid")

    productPrice: dict[str, object]


class ProductPriceListSuccess(BaseModel):
    """Mapped success envelope for a documented product-prices collection read."""

    model_config = ConfigDict(extra="forbid")

    productPrices: list[dict[str, object]]
    paging: Paging | None = None


class CatalogReadService:
    """Typed handlers over the locked Billy client, kept separate from root wiring."""

    def __init__(self, client: BillyHttpClient) -> None:
        self._client = client

    def products_get(self, request: CatalogGetRequest) -> ProductGetSuccess | ToolError:
        """Read one product by its Billy identifier."""

        response = self._client.request(
            "GET", _item_path("/products", request.id), params=_include_params(request.include)
        )
        return _map_product_response(response)

    def products_list(self, request: CatalogListRequest) -> ProductListSuccess | ToolError:
        """Read one documented page of products."""

        response = self._client.request("GET", "/products", params=_list_params(request))
        return _map_product_list_response(response)

    def product_prices_get(self, request: CatalogGetRequest) -> ProductPriceGetSuccess | ToolError:
        """Read one product price by its Billy identifier."""

        response = self._client.request(
            "GET",
            _item_path("/productPrices", request.id),
            params=_include_params(request.include),
        )
        return _map_product_price_response(response)

    def product_prices_list(
        self, request: CatalogListRequest
    ) -> ProductPriceListSuccess | ToolError:
        """Read one documented page of product prices."""

        response = self._client.request("GET", "/productPrices", params=_list_params(request))
        return _map_product_price_list_response(response)


def register_catalog_read_tools(server: FastMCP, client: BillyHttpClient) -> None:
    """Register only the four verified catalogue read tools on a FastMCP server."""

    service = CatalogReadService(client)

    def api_products_get(
        id: str = Field(min_length=1), include: str | None = None
    ) -> ProductGetSuccess | ToolError:
        """Read one Billy product by identifier."""

        return service.products_get(CatalogGetRequest(id=id, include=include))

    def api_products_list(
        page: int = Field(default=1, ge=1),
        pageSize: int = Field(default=DEFAULT_PAGE_SIZE, ge=1, le=MAX_PAGE_SIZE),
        include: str | None = None,
        sortProperty: str | None = None,
        sortDirection: SortDirection | None = None,
    ) -> ProductListSuccess | ToolError:
        """List Billy products with documented paging, inclusion, and sorting."""

        return service.products_list(
            CatalogListRequest(
                page=page,
                pageSize=pageSize,
                include=include,
                sortProperty=sortProperty,
                sortDirection=sortDirection,
            )
        )

    def api_product_prices_get(
        id: str = Field(min_length=1), include: str | None = None
    ) -> ProductPriceGetSuccess | ToolError:
        """Read one Billy product price by identifier."""

        return service.product_prices_get(CatalogGetRequest(id=id, include=include))

    def api_product_prices_list(
        page: int = Field(default=1, ge=1),
        pageSize: int = Field(default=DEFAULT_PAGE_SIZE, ge=1, le=MAX_PAGE_SIZE),
        include: str | None = None,
        sortProperty: str | None = None,
        sortDirection: SortDirection | None = None,
    ) -> ProductPriceListSuccess | ToolError:
        """List Billy product prices with documented paging, inclusion, and sorting."""

        return service.product_prices_list(
            CatalogListRequest(
                page=page,
                pageSize=pageSize,
                include=include,
                sortProperty=sortProperty,
                sortDirection=sortDirection,
            )
        )

    server.tool(name="api_products_get", description="Read one Billy product.")(api_products_get)
    server.tool(name="api_products_list", description="List Billy products.")(api_products_list)
    server.tool(name="api_product_prices_get", description="Read one Billy product price.")(
        api_product_prices_get
    )
    server.tool(name="api_product_prices_list", description="List Billy product prices.")(
        api_product_prices_list
    )


def _item_path(collection_path: str, identifier: str) -> str:
    return f"{collection_path}/{quote(identifier, safe='')}"


def _include_params(include: str | None) -> dict[str, str]:
    return {} if include is None else {"include": include}


def _list_params(request: CatalogListRequest) -> dict[str, int | str]:
    params: dict[str, int | str] = {"page": request.page, "pageSize": request.pageSize}
    if request.include is not None:
        params["include"] = request.include
    if request.sortProperty is not None:
        params["sortProperty"] = request.sortProperty
    if request.sortDirection is not None:
        params["sortDirection"] = request.sortDirection.value
    return params


def _map_product_response(response: BillyResponse | ToolError) -> ProductGetSuccess | ToolError:
    root = _singular_root(response, "product")
    if isinstance(root, ToolError):
        return root
    return ProductGetSuccess(product=root)


def _map_product_price_response(
    response: BillyResponse | ToolError,
) -> ProductPriceGetSuccess | ToolError:
    root = _singular_root(response, "productPrice")
    if isinstance(root, ToolError):
        return root
    return ProductPriceGetSuccess(productPrice=root)


def _map_product_list_response(
    response: BillyResponse | ToolError,
) -> ProductListSuccess | ToolError:
    roots = _list_root_and_paging(response, "products")
    if isinstance(roots, ToolError):
        return roots
    products, paging = roots
    return ProductListSuccess(products=products, paging=paging)


def _map_product_price_list_response(
    response: BillyResponse | ToolError,
) -> ProductPriceListSuccess | ToolError:
    roots = _list_root_and_paging(response, "productPrices")
    if isinstance(roots, ToolError):
        return roots
    product_prices, paging = roots
    return ProductPriceListSuccess(productPrices=product_prices, paging=paging)


def _singular_root(
    response: BillyResponse | ToolError, root_name: str
) -> dict[str, object] | ToolError:
    if isinstance(response, ToolError):
        return response
    data = _response_object(response.data)
    if data is None:
        return _invalid_response(root_name)
    root = data.get(root_name)
    if not isinstance(root, dict):
        return _invalid_response(root_name)
    return cast(dict[str, object], root)


def _list_root_and_paging(
    response: BillyResponse | ToolError, root_name: str
) -> tuple[list[dict[str, object]], Paging | None] | ToolError:
    if isinstance(response, ToolError):
        return response
    data = _response_object(response.data)
    if data is None:
        return _invalid_response(root_name)
    root = data.get(root_name)
    if not isinstance(root, list):
        return _invalid_response(root_name)
    records: list[dict[str, object]] = []
    for item in cast(list[object], root):
        record = _response_object(item)
        if record is None:
            return _invalid_response(root_name)
        records.append(record)
    paging = _paging_from(data)
    if isinstance(paging, ToolError):
        return paging
    return records, paging


def _response_object(data: object) -> dict[str, object] | None:
    if not isinstance(data, dict):
        return None
    raw_object = cast(dict[object, object], data)
    return {str(key): value for key, value in raw_object.items()}


def _paging_from(data: dict[str, object]) -> Paging | ToolError | None:
    meta = data.get("meta")
    if meta is None:
        return None
    meta_object = _response_object(meta)
    if meta_object is None:
        return _invalid_response("meta")
    raw_paging = meta_object.get("paging")
    if raw_paging is None:
        return None
    paging_object = _response_object(raw_paging)
    if paging_object is None:
        return _invalid_response("meta.paging")
    return Paging.model_validate(paging_object)


def _invalid_response(root_name: str) -> ToolError:
    return ToolError(
        code=StableErrorCode.VALIDATION_ERROR,
        message=f"Billy response did not contain a valid {root_name} root.",
    )
