"""Offline FastMCP ticket contract for UI product create preview/execute."""

from __future__ import annotations

import asyncio
from datetime import UTC, datetime, timedelta
from typing import cast

import pytest
from fastmcp import FastMCP
from pydantic import ValidationError

from billy_mcp.confirmations import MAX_TICKET_TTL, ConfirmationStore
from billy_mcp.models import StableErrorCode
from billy_mcp.server import create_server
from billy_mcp.ui_writes.products import (
    UiProductsCreatePreviewInput,
    register_ui_product_write_tools,
)
from billy_mcp.ui_writes.protocol import UiWriteProtocol


class Clock:
    """Mutable UTC clock for deterministic ticket expiry."""

    def __init__(self) -> None:
        self.now = datetime(2026, 8, 16, tzinfo=UTC)

    def __call__(self) -> datetime:
        return self.now


def make_server(protocol: UiWriteProtocol | None = None) -> FastMCP:
    """Register only the product UI write tools on a local FastMCP server."""

    server = FastMCP("ui-products-write-contract-test")
    register_ui_product_write_tools(server, protocol or UiWriteProtocol(ConfirmationStore()))
    return server


def call_tool(server: FastMCP, tool_name: str, arguments: dict[str, object]) -> dict[str, object]:
    """Call one typed tool and return its structured result payload."""

    result = asyncio.run(server.call_tool(tool_name, arguments))
    assert isinstance(result.structured_content, dict)
    structured_content = cast(dict[str, object], result.structured_content)
    payload = structured_content.get("result", structured_content)
    assert isinstance(payload, dict)
    return cast(dict[str, object], payload)


def test_create_server_registers_product_create_preview_and_execute() -> None:
    server = create_server()
    tools = {tool.name: tool for tool in asyncio.run(server.list_tools())}

    assert "ui_products_create_preview" in tools
    assert "ui_products_create_execute" in tools
    preview = tools["ui_products_create_preview"].parameters
    execute = tools["ui_products_create_execute"].parameters
    preview_properties = cast(dict[str, object], preview["properties"])
    execute_properties = cast(dict[str, object], execute["properties"])
    assert preview["additionalProperties"] is False
    assert execute["additionalProperties"] is False
    assert set(preview_properties) == {"name", "account", "salesTaxRuleset", "unitPrice"}
    assert set(execute_properties) == {"confirmation_ticket"}
    ticket = execute_properties["confirmation_ticket"]
    assert isinstance(ticket, dict)
    assert ticket["minLength"] == 1


def test_preview_returns_ticket_and_does_not_submit() -> None:
    server = make_server()

    preview = call_tool(
        server,
        "ui_products_create_preview",
        {"name": "MCP-TEST-PRODUCT-OFFLINE-1"},
    )

    assert preview["confirmation_ticket"]
    assert preview["canonical_request"] == {"name": "MCP-TEST-PRODUCT-OFFLINE-1"}
    assert preview["expected_effect_state"] == {"action": "create", "resource": "product"}
    assert "submit" not in str(preview["summary"]).lower()


def test_preview_binds_optional_form_fields() -> None:
    server = make_server()

    preview = call_tool(
        server,
        "ui_products_create_preview",
        {
            "name": "MCP-TEST-PRODUCT-OFFLINE-FIELDS",
            "account": "1000",
            "salesTaxRuleset": "ruleset-1",
            "unitPrice": 12.5,
        },
    )

    assert preview["canonical_request"] == {
        "name": "MCP-TEST-PRODUCT-OFFLINE-FIELDS",
        "account": "1000",
        "salesTaxRuleset": "ruleset-1",
        "unitPrice": 12.5,
    }


def test_preview_input_rejects_empty_name_and_unknown_fields() -> None:
    with pytest.raises(ValidationError):
        UiProductsCreatePreviewInput(name="")
    with pytest.raises(ValidationError):
        UiProductsCreatePreviewInput.model_validate(
            {"name": "MCP-TEST-PRODUCT-OFFLINE-X", "unexpected": True}
        )


def test_execute_consumes_ticket_once_and_echoes_previewed_name() -> None:
    server = make_server()
    preview = call_tool(
        server,
        "ui_products_create_preview",
        {"name": "MCP-TEST-PRODUCT-OFFLINE-2"},
    )

    first = call_tool(
        server,
        "ui_products_create_execute",
        {"confirmation_ticket": preview["confirmation_ticket"]},
    )
    replay = call_tool(
        server,
        "ui_products_create_execute",
        {"confirmation_ticket": preview["confirmation_ticket"]},
    )

    request = first["canonical_request"]
    assert isinstance(request, dict)
    assert request["name"] == "MCP-TEST-PRODUCT-OFFLINE-2"
    assert replay["code"] == StableErrorCode.CONFIRMATION_CONSUMED


def test_execute_rejects_expired_ticket() -> None:
    clock = Clock()
    server = make_server(UiWriteProtocol(ConfirmationStore(clock=clock)))
    preview = call_tool(
        server,
        "ui_products_create_preview",
        {"name": "MCP-TEST-PRODUCT-OFFLINE-3"},
    )

    clock.now = clock.now + MAX_TICKET_TTL + timedelta(seconds=1)
    expired = call_tool(
        server,
        "ui_products_create_execute",
        {"confirmation_ticket": preview["confirmation_ticket"]},
    )

    assert expired["code"] == StableErrorCode.CONFIRMATION_EXPIRED


def test_execute_rejects_ticket_bound_to_another_tool() -> None:
    protocol = UiWriteProtocol(ConfirmationStore())
    server = make_server(protocol)
    foreign = protocol.preview(
        execute_tool_name="ui_bills_create_execute",
        organization_id=None,
        target="bills",
        canonical_request={"name": "not-a-product"},
        expected_effect_state={"action": "create", "resource": "bill"},
        summary="Create one Billy bill in the interface.",
    )

    mismatch = call_tool(
        server,
        "ui_products_create_execute",
        {"confirmation_ticket": foreign.confirmation_ticket},
    )

    assert mismatch["code"] == StableErrorCode.CONFIRMATION_MISMATCH
