"""Ticketed FastMCP tools for documented singular Billy catalog writes."""

from __future__ import annotations

from fastmcp import FastMCP
from pydantic import BaseModel, ConfigDict, Field, JsonValue

from billy_mcp.api.write_protocol import (
    WriteExecuteInput,
    WriteExecutionResult,
    WriteMethod,
    WriteOperationSpec,
    WritePreviewResult,
    WriteProtocolService,
)
from billy_mcp.client import BillyHttpClient
from billy_mcp.models import ToolError


class _CatalogWritePreviewInput(BaseModel):
    """Base model that rejects undeclared inputs around opaque catalog payloads."""

    model_config = ConfigDict(extra="forbid", validate_by_alias=True, validate_by_name=True)


class ProductCreatePreviewInput(_CatalogWritePreviewInput):
    """Opaque documented product payload for a creation preview."""

    product: dict[str, JsonValue]


class ProductUpdatePreviewInput(ProductCreatePreviewInput):
    """Opaque documented product payload and identifier for an update preview."""

    id: str = Field(min_length=1)


class ProductDeletePreviewInput(_CatalogWritePreviewInput):
    """Identifier for a bodyless product deletion preview."""

    id: str = Field(min_length=1)


class ProductPriceCreatePreviewInput(_CatalogWritePreviewInput):
    """Opaque documented product-price payload for a creation preview."""

    product_price: dict[str, JsonValue] = Field(
        alias="productPrice", serialization_alias="productPrice"
    )


class ProductPriceUpdatePreviewInput(ProductPriceCreatePreviewInput):
    """Opaque documented product-price payload and identifier for an update preview."""

    id: str = Field(min_length=1)


class ProductPriceDeletePreviewInput(_CatalogWritePreviewInput):
    """Identifier for a bodyless product-price deletion preview."""

    id: str = Field(min_length=1)


def register_catalog_write_tools(
    server: FastMCP,
    client: BillyHttpClient,
    write_protocol: WriteProtocolService,
) -> None:
    """Register exactly the twelve frozen ticketed catalog write tools."""

    del client

    def api_products_create_preview(product: dict[str, JsonValue]) -> WritePreviewResult:
        """Preview creation of one Billy product without sending a mutation."""

        input = ProductCreatePreviewInput(product=product)
        return write_protocol.preview(
            _product_specification(
                execute_tool_name="api_products_create_execute",
                method=WriteMethod.POST,
                payload=input.product,
                resource_id=None,
            )
        )

    def api_products_create_execute(
        confirmation_ticket: str = Field(min_length=1),
    ) -> WriteExecutionResult | ToolError:
        """Execute exactly the product creation represented by a confirmation ticket."""

        return write_protocol.execute(
            WriteExecuteInput(confirmation_ticket=confirmation_ticket),
            execute_tool_name="api_products_create_execute",
        )

    def api_products_update_preview(
        product: dict[str, JsonValue], id: str = Field(min_length=1)
    ) -> WritePreviewResult:
        """Preview an update to one Billy product without sending a mutation."""

        input = ProductUpdatePreviewInput(id=id, product=product)
        return write_protocol.preview(
            _product_specification(
                execute_tool_name="api_products_update_execute",
                method=WriteMethod.PUT,
                payload=input.product,
                resource_id=input.id,
            )
        )

    def api_products_update_execute(
        confirmation_ticket: str = Field(min_length=1),
    ) -> WriteExecutionResult | ToolError:
        """Execute exactly the product update represented by a confirmation ticket."""

        return write_protocol.execute(
            WriteExecuteInput(confirmation_ticket=confirmation_ticket),
            execute_tool_name="api_products_update_execute",
        )

    def api_products_delete_preview(id: str = Field(min_length=1)) -> WritePreviewResult:
        """Preview deletion of one Billy product without sending a mutation."""

        input = ProductDeletePreviewInput(id=id)
        return write_protocol.preview(
            _product_specification(
                execute_tool_name="api_products_delete_execute",
                method=WriteMethod.DELETE,
                payload=None,
                resource_id=input.id,
            )
        )

    def api_products_delete_execute(
        confirmation_ticket: str = Field(min_length=1),
    ) -> WriteExecutionResult | ToolError:
        """Execute exactly the product deletion represented by a confirmation ticket."""

        return write_protocol.execute(
            WriteExecuteInput(confirmation_ticket=confirmation_ticket),
            execute_tool_name="api_products_delete_execute",
        )

    def api_product_prices_create_preview(
        productPrice: dict[str, JsonValue],
    ) -> WritePreviewResult:
        """Preview creation of one Billy product price without sending a mutation."""

        input = ProductPriceCreatePreviewInput(productPrice=productPrice)
        return write_protocol.preview(
            _product_price_specification(
                execute_tool_name="api_product_prices_create_execute",
                method=WriteMethod.POST,
                payload=input.product_price,
                resource_id=None,
            )
        )

    def api_product_prices_create_execute(
        confirmation_ticket: str = Field(min_length=1),
    ) -> WriteExecutionResult | ToolError:
        """Execute exactly the product-price creation represented by a confirmation ticket."""

        return write_protocol.execute(
            WriteExecuteInput(confirmation_ticket=confirmation_ticket),
            execute_tool_name="api_product_prices_create_execute",
        )

    def api_product_prices_update_preview(
        productPrice: dict[str, JsonValue], id: str = Field(min_length=1)
    ) -> WritePreviewResult:
        """Preview an update to one Billy product price without sending a mutation."""

        input = ProductPriceUpdatePreviewInput(id=id, productPrice=productPrice)
        return write_protocol.preview(
            _product_price_specification(
                execute_tool_name="api_product_prices_update_execute",
                method=WriteMethod.PUT,
                payload=input.product_price,
                resource_id=input.id,
            )
        )

    def api_product_prices_update_execute(
        confirmation_ticket: str = Field(min_length=1),
    ) -> WriteExecutionResult | ToolError:
        """Execute exactly the product-price update represented by a confirmation ticket."""

        return write_protocol.execute(
            WriteExecuteInput(confirmation_ticket=confirmation_ticket),
            execute_tool_name="api_product_prices_update_execute",
        )

    def api_product_prices_delete_preview(id: str = Field(min_length=1)) -> WritePreviewResult:
        """Preview deletion of one Billy product price without sending a mutation."""

        input = ProductPriceDeletePreviewInput(id=id)
        return write_protocol.preview(
            _product_price_specification(
                execute_tool_name="api_product_prices_delete_execute",
                method=WriteMethod.DELETE,
                payload=None,
                resource_id=input.id,
            )
        )

    def api_product_prices_delete_execute(
        confirmation_ticket: str = Field(min_length=1),
    ) -> WriteExecutionResult | ToolError:
        """Execute exactly the product-price deletion represented by a confirmation ticket."""

        return write_protocol.execute(
            WriteExecuteInput(confirmation_ticket=confirmation_ticket),
            execute_tool_name="api_product_prices_delete_execute",
        )

    server.tool(
        name="api_products_create_preview",
        description="Preview creation of one Billy product without making a mutation.",
    )(api_products_create_preview)
    server.tool(
        name="api_products_create_execute",
        description="Execute a previewed Billy product creation with its confirmation ticket.",
    )(api_products_create_execute)
    server.tool(
        name="api_products_update_preview",
        description="Preview an update to one Billy product without making a mutation.",
    )(api_products_update_preview)
    server.tool(
        name="api_products_update_execute",
        description="Execute a previewed Billy product update with its confirmation ticket.",
    )(api_products_update_execute)
    server.tool(
        name="api_products_delete_preview",
        description="Preview deletion of one Billy product without making a mutation.",
    )(api_products_delete_preview)
    server.tool(
        name="api_products_delete_execute",
        description="Execute a previewed Billy product deletion with its confirmation ticket.",
    )(api_products_delete_execute)
    server.tool(
        name="api_product_prices_create_preview",
        description="Preview creation of one Billy product price without making a mutation.",
    )(api_product_prices_create_preview)
    server.tool(
        name="api_product_prices_create_execute",
        description=(
            "Execute a previewed Billy product-price creation with its confirmation ticket."
        ),
    )(api_product_prices_create_execute)
    server.tool(
        name="api_product_prices_update_preview",
        description="Preview an update to one Billy product price without making a mutation.",
    )(api_product_prices_update_preview)
    server.tool(
        name="api_product_prices_update_execute",
        description="Execute a previewed Billy product-price update with its confirmation ticket.",
    )(api_product_prices_update_execute)
    server.tool(
        name="api_product_prices_delete_preview",
        description="Preview deletion of one Billy product price without making a mutation.",
    )(api_product_prices_delete_preview)
    server.tool(
        name="api_product_prices_delete_execute",
        description=(
            "Execute a previewed Billy product-price deletion with its confirmation ticket."
        ),
    )(api_product_prices_delete_execute)


def _product_specification(
    *,
    execute_tool_name: str,
    method: WriteMethod,
    payload: dict[str, JsonValue] | None,
    resource_id: str | None,
) -> WriteOperationSpec:
    """Build the server-known singular write shape for one Billy product."""

    return _catalog_specification(
        execute_tool_name=execute_tool_name,
        method=method,
        collection_path="/products",
        singular_root="product",
        plural_root="products",
        additional_plural_roots=("productPrices",),
        payload=payload,
        resource_id=resource_id,
        resource="product",
    )


def _product_price_specification(
    *,
    execute_tool_name: str,
    method: WriteMethod,
    payload: dict[str, JsonValue] | None,
    resource_id: str | None,
) -> WriteOperationSpec:
    """Build the server-known singular write shape for one Billy product price."""

    return _catalog_specification(
        execute_tool_name=execute_tool_name,
        method=method,
        collection_path="/productPrices",
        singular_root="productPrice",
        plural_root="productPrices",
        additional_plural_roots=(),
        payload=payload,
        resource_id=resource_id,
        resource="productPrice",
    )


def _catalog_specification(
    *,
    execute_tool_name: str,
    method: WriteMethod,
    collection_path: str,
    singular_root: str,
    plural_root: str,
    additional_plural_roots: tuple[str, ...],
    payload: dict[str, JsonValue] | None,
    resource_id: str | None,
    resource: str,
) -> WriteOperationSpec:
    """Build one complete server-known catalog operation for the shared protocol."""

    action = {
        WriteMethod.POST: "create",
        WriteMethod.PUT: "update",
        WriteMethod.DELETE: "delete",
    }[method]
    expected_effect_state: dict[str, JsonValue] = {"action": action, "resource": resource}
    if resource_id is not None:
        expected_effect_state["id"] = resource_id
    return WriteOperationSpec(
        execute_tool_name=execute_tool_name,
        method=method,
        collection_path=collection_path,
        singular_root=singular_root,
        plural_root=plural_root,
        additional_plural_roots=additional_plural_roots,
        payload=payload,
        resource_id=resource_id,
        organization_id=None,
        summary=f"{action.capitalize()} one Billy {resource.replace('Price', ' price')}.",
        expected_effect_state=expected_effect_state,
    )
