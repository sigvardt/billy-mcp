"""Contract tests for the ticketed singular Billy catalog write tools."""

from __future__ import annotations

import asyncio
import json
from collections.abc import Callable
from datetime import UTC, datetime
from typing import cast

import httpx
import pytest
from fastmcp import FastMCP
from pydantic import ValidationError

from billy_mcp.api.catalog_writes import (
    ProductCreatePreviewInput,
    ProductDeletePreviewInput,
    ProductPriceCreatePreviewInput,
    ProductPriceDeletePreviewInput,
    ProductPriceUpdatePreviewInput,
    ProductUpdatePreviewInput,
    register_catalog_write_tools,
)
from billy_mcp.api.write_protocol import WriteExecuteInput, WriteProtocolService
from billy_mcp.client import BillyHttpClient
from billy_mcp.confirmations import MAX_TICKET_TTL, ConfirmationStore
from billy_mcp.models import StableErrorCode

MockHandler = Callable[[httpx.Request], httpx.Response]


class Clock:
    """Mutable UTC clock for deterministic confirmation-ticket expiry tests."""

    def __init__(self) -> None:
        self.now = datetime(2026, 7, 29, tzinfo=UTC)

    def __call__(self) -> datetime:
        return self.now


def make_server(
    handler: MockHandler,
    *,
    confirmations: ConfirmationStore | None = None,
    token: str | None = "catalog-write-test-token",
) -> tuple[FastMCP, list[httpx.Request]]:
    """Create a local catalog-write server with a recording locked client."""

    requests: list[httpx.Request] = []

    def recording_handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return handler(request)

    client = BillyHttpClient(
        lambda: token,
        transport=httpx.MockTransport(recording_handler),
    )
    server = FastMCP("catalog-write-contract-test")
    register_catalog_write_tools(
        server,
        client,
        WriteProtocolService(client, confirmations or ConfirmationStore()),
    )
    return server, requests


def call_tool(server: FastMCP, tool_name: str, arguments: dict[str, object]) -> dict[str, object]:
    """Call one typed tool and return its structured result payload."""

    result = asyncio.run(server.call_tool(tool_name, arguments))
    assert isinstance(result.structured_content, dict)
    structured_content = cast(dict[str, object], result.structured_content)
    payload = structured_content.get("result", structured_content)
    assert isinstance(payload, dict)
    return cast(dict[str, object], payload)


def test_registers_twelve_flat_strict_catalog_write_tools() -> None:
    server, _ = make_server(lambda request: httpx.Response(200, json={}))

    tools = {tool.name: tool for tool in asyncio.run(server.list_tools())}
    expected_properties = {
        "api_products_create_preview": {"product"},
        "api_products_create_execute": {"confirmation_ticket"},
        "api_products_update_preview": {"id", "product"},
        "api_products_update_execute": {"confirmation_ticket"},
        "api_products_delete_preview": {"id"},
        "api_products_delete_execute": {"confirmation_ticket"},
        "api_product_prices_create_preview": {"productPrice"},
        "api_product_prices_create_execute": {"confirmation_ticket"},
        "api_product_prices_update_preview": {"id", "productPrice"},
        "api_product_prices_update_execute": {"confirmation_ticket"},
        "api_product_prices_delete_preview": {"id"},
        "api_product_prices_delete_execute": {"confirmation_ticket"},
    }

    assert set(tools) == set(expected_properties)
    for name, fields in expected_properties.items():
        schema = tools[name].parameters
        properties = cast(dict[str, object], schema["properties"])
        assert schema["additionalProperties"] is False
        assert set(properties) == fields
        assert "input" not in properties
        if fields == {"confirmation_ticket"}:
            ticket = properties["confirmation_ticket"]
            assert isinstance(ticket, dict)
            assert ticket["minLength"] == 1


@pytest.mark.parametrize(
    ("input_model", "payload"),
    [
        (ProductCreatePreviewInput, {"product": {}, "unexpected": True}),
        (ProductUpdatePreviewInput, {"id": "product-1", "product": {}, "unexpected": True}),
        (ProductDeletePreviewInput, {"id": "product-1", "unexpected": True}),
        (ProductPriceCreatePreviewInput, {"productPrice": {}, "unexpected": True}),
        (
            ProductPriceUpdatePreviewInput,
            {"id": "price-1", "productPrice": {}, "unexpected": True},
        ),
        (ProductPriceDeletePreviewInput, {"id": "price-1", "unexpected": True}),
        (ProductUpdatePreviewInput, {"id": "", "product": {}}),
        (ProductPriceUpdatePreviewInput, {"id": "", "productPrice": {}}),
        (ProductDeletePreviewInput, {"id": ""}),
        (ProductPriceDeletePreviewInput, {"id": ""}),
        (WriteExecuteInput, {"confirmation_ticket": "ticket", "product": {}}),
    ],
)
def test_outer_inputs_forbid_extras_and_empty_identifiers(
    input_model: type[ProductCreatePreviewInput]
    | type[ProductUpdatePreviewInput]
    | type[ProductDeletePreviewInput]
    | type[ProductPriceCreatePreviewInput]
    | type[ProductPriceUpdatePreviewInput]
    | type[ProductPriceDeletePreviewInput]
    | type[WriteExecuteInput],
    payload: dict[str, object],
) -> None:
    with pytest.raises(ValidationError):
        input_model.model_validate(payload)


@pytest.mark.parametrize(
    ("tool_name", "arguments", "expected_request"),
    [
        (
            "api_products_create_preview",
            {
                "product": {
                    "name": "Desk",
                    "prices": [{"unitPrice": 199.95, "currencyId": "DKK"}],
                }
            },
            {
                "product": {
                    "name": "Desk",
                    "prices": [{"unitPrice": 199.95, "currencyId": "DKK"}],
                }
            },
        ),
        (
            "api_products_update_preview",
            {"id": "product /?", "product": {"name": "Replacement"}},
            {"product": {"name": "Replacement"}},
        ),
        ("api_products_delete_preview", {"id": "product /?"}, {"id": "product /?"}),
        (
            "api_product_prices_create_preview",
            {"productPrice": {"productId": "product-1", "unitPrice": 199.95, "currencyId": "DKK"}},
            {"productPrice": {"productId": "product-1", "unitPrice": 199.95, "currencyId": "DKK"}},
        ),
        (
            "api_product_prices_update_preview",
            {"id": "price /?", "productPrice": {"unitPrice": 249.95}},
            {"productPrice": {"unitPrice": 249.95}},
        ),
        ("api_product_prices_delete_preview", {"id": "price /?"}, {"id": "price /?"}),
    ],
)
def test_previews_are_mutation_free_and_bind_exact_catalog_requests(
    tool_name: str,
    arguments: dict[str, object],
    expected_request: dict[str, object],
) -> None:
    server, requests = make_server(
        lambda request: pytest.fail(f"preview made an HTTP request: {request.method} {request.url}")
    )

    preview = call_tool(server, tool_name, arguments)

    assert requests == []
    assert preview["canonical_request"] == expected_request
    assert isinstance(preview["confirmation_ticket"], str)
    assert preview["confirmation_ticket"]


@pytest.mark.parametrize(
    (
        "preview_tool",
        "execute_tool",
        "preview_input",
        "response",
        "expected_method",
        "expected_path",
        "expected_body",
        "expected_records",
        "expected_deleted_records",
    ),
    [
        (
            "api_products_create_preview",
            "api_products_create_execute",
            {
                "product": {
                    "name": "Desk",
                    "prices": [{"unitPrice": 199.95, "currencyId": "DKK"}],
                }
            },
            {
                "products": [{"id": "product-1", "name": "Desk"}],
                "productPrices": [{"id": "price-1", "productId": "product-1"}],
            },
            "POST",
            "/v2/products",
            {
                "product": {
                    "name": "Desk",
                    "prices": [{"unitPrice": 199.95, "currencyId": "DKK"}],
                }
            },
            {
                "products": [{"id": "product-1", "name": "Desk"}],
                "productPrices": [{"id": "price-1", "productId": "product-1"}],
            },
            None,
        ),
        (
            "api_products_update_preview",
            "api_products_update_execute",
            {"id": "product /?", "product": {"name": "Replacement"}},
            {"products": [{"id": "product /?", "name": "Replacement"}]},
            "PUT",
            "/v2/products/product%20%2F%3F",
            {"product": {"name": "Replacement"}},
            {"products": [{"id": "product /?", "name": "Replacement"}]},
            None,
        ),
        (
            "api_products_delete_preview",
            "api_products_delete_execute",
            {"id": "product /?"},
            {"meta": {"deletedRecords": {"products": ["product /?"]}}},
            "DELETE",
            "/v2/products/product%20%2F%3F",
            None,
            {},
            {"products": ["product /?"]},
        ),
        (
            "api_product_prices_create_preview",
            "api_product_prices_create_execute",
            {"productPrice": {"productId": "product-1", "unitPrice": 199.95, "currencyId": "DKK"}},
            {"productPrices": [{"id": "price-1", "productId": "product-1"}]},
            "POST",
            "/v2/productPrices",
            {"productPrice": {"productId": "product-1", "unitPrice": 199.95, "currencyId": "DKK"}},
            {"productPrices": [{"id": "price-1", "productId": "product-1"}]},
            None,
        ),
        (
            "api_product_prices_update_preview",
            "api_product_prices_update_execute",
            {"id": "price /?", "productPrice": {"unitPrice": 249.95}},
            {"productPrices": [{"id": "price /?", "unitPrice": 249.95}]},
            "PUT",
            "/v2/productPrices/price%20%2F%3F",
            {"productPrice": {"unitPrice": 249.95}},
            {"productPrices": [{"id": "price /?", "unitPrice": 249.95}]},
            None,
        ),
        (
            "api_product_prices_delete_preview",
            "api_product_prices_delete_execute",
            {"id": "price /?"},
            {"meta": {"deletedRecords": {"productPrices": ["price /?"]}}},
            "DELETE",
            "/v2/productPrices/price%20%2F%3F",
            None,
            {},
            {"productPrices": ["price /?"]},
        ),
    ],
)
def test_executes_exact_singular_catalog_cud_requests_once(
    preview_tool: str,
    execute_tool: str,
    preview_input: dict[str, object],
    response: dict[str, object],
    expected_method: str,
    expected_path: str,
    expected_body: dict[str, object] | None,
    expected_records: dict[str, object],
    expected_deleted_records: dict[str, list[str]] | None,
) -> None:
    server, requests = make_server(lambda request: httpx.Response(200, json=response))

    preview = call_tool(server, preview_tool, preview_input)
    execution = call_tool(
        server,
        execute_tool,
        {"confirmation_ticket": preview["confirmation_ticket"]},
    )

    assert len(requests) == 1
    request = requests[0]
    assert request.method == expected_method
    assert request.url.raw_path.decode() == expected_path
    assert execution["changed_records"] == expected_records
    assert execution["deleted_records"] == expected_deleted_records
    if expected_body is None:
        assert request.content == b""
    else:
        assert json.loads(request.content) == expected_body


def test_invalid_expired_and_replayed_tickets_do_not_perform_extra_writes() -> None:
    clock = Clock()
    server, requests = make_server(
        lambda request: httpx.Response(200, json={"products": [{"id": "product-1"}]}),
        confirmations=ConfirmationStore(clock),
    )

    invalid = call_tool(
        server,
        "api_products_create_execute",
        {"confirmation_ticket": "not-a-catalog-ticket"},
    )
    assert invalid["code"] == StableErrorCode.CONFIRMATION_INVALID
    assert requests == []

    expired_preview = call_tool(
        server,
        "api_products_create_preview",
        {"product": {"name": "Desk"}},
    )
    clock.now += MAX_TICKET_TTL
    expired = call_tool(
        server,
        "api_products_create_execute",
        {"confirmation_ticket": expired_preview["confirmation_ticket"]},
    )
    assert expired["code"] == StableErrorCode.CONFIRMATION_EXPIRED
    assert requests == []

    replay_preview = call_tool(
        server,
        "api_products_create_preview",
        {"product": {"name": "Desk"}},
    )
    first = call_tool(
        server,
        "api_products_create_execute",
        {"confirmation_ticket": replay_preview["confirmation_ticket"]},
    )
    replayed = call_tool(
        server,
        "api_products_create_execute",
        {"confirmation_ticket": replay_preview["confirmation_ticket"]},
    )

    assert first["changed_records"] == {"products": [{"id": "product-1"}]}
    assert replayed["code"] == StableErrorCode.CONFIRMATION_CONSUMED
    assert len(requests) == 1


def test_empty_token_returns_typed_auth_error_without_network_access() -> None:
    server, requests = make_server(
        lambda request: pytest.fail(f"empty token attempted network access: {request.url}"),
        token="",
    )

    preview = call_tool(
        server,
        "api_product_prices_create_preview",
        {"productPrice": {"productId": "product-1", "unitPrice": 199.95, "currencyId": "DKK"}},
    )
    result = call_tool(
        server,
        "api_product_prices_create_execute",
        {"confirmation_ticket": preview["confirmation_ticket"]},
    )

    assert result["code"] == StableErrorCode.AUTH_REQUIRED
    assert requests == []


@pytest.mark.parametrize(
    ("status", "response", "preview_tool", "preview_input", "execute_tool", "expected_code"),
    [
        (
            401,
            {"errorCode": "AUTHENTICATION_REQUIRED"},
            "api_products_create_preview",
            {"product": {"name": "Desk"}},
            "api_products_create_execute",
            StableErrorCode.AUTH_REQUIRED,
        ),
        (
            404,
            {"errorCode": "RECORD_NOT_FOUND"},
            "api_product_prices_update_preview",
            {"id": "missing-price", "productPrice": {"unitPrice": 199.95}},
            "api_product_prices_update_execute",
            StableErrorCode.NOT_FOUND,
        ),
    ],
)
def test_typed_upstream_authentication_and_not_found_errors_propagate(
    status: int,
    response: dict[str, str],
    preview_tool: str,
    preview_input: dict[str, object],
    execute_tool: str,
    expected_code: StableErrorCode,
) -> None:
    server, requests = make_server(lambda request: httpx.Response(status, json=response))

    preview = call_tool(server, preview_tool, preview_input)
    result = call_tool(
        server,
        execute_tool,
        {"confirmation_ticket": preview["confirmation_ticket"]},
    )

    assert result["code"] == expected_code
    assert len(requests) == 1


def test_delete_does_not_fabricate_absent_deleted_records() -> None:
    server, _ = make_server(lambda request: httpx.Response(200, json={"meta": {}}))

    preview = call_tool(server, "api_products_delete_preview", {"id": "product-1"})
    result = call_tool(
        server,
        "api_products_delete_execute",
        {"confirmation_ticket": preview["confirmation_ticket"]},
    )

    assert result == {"changed_records": {}, "deleted_records": None}
