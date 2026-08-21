"""Integration tests for attachment tickets in the root shared confirmation service."""

from __future__ import annotations

import asyncio
from collections.abc import Mapping
from typing import cast

from fastmcp import FastMCP
from pytest import MonkeyPatch

from billy_mcp.client import BillyHttpClient, BillyResponse
from billy_mcp.models import StableErrorCode
from billy_mcp.server import create_server


def call_tool(server: FastMCP, tool_name: str, arguments: dict[str, object]) -> dict[str, object]:
    """Call one typed MCP tool and return its structured payload."""

    result = asyncio.run(server.call_tool(tool_name, arguments))
    structured_content = result.structured_content
    assert isinstance(structured_content, dict)
    payload = structured_content.get("result", structured_content)
    assert isinstance(payload, dict)
    return cast(dict[str, object], payload)


def test_root_service_rejects_cross_resource_executor_before_consuming_or_writing(
    monkeypatch: MonkeyPatch,
) -> None:
    """An attachment ticket remains usable only by its exact root-registered executor."""

    requests: list[tuple[str, str, object | None]] = []

    def fake_request(
        self: BillyHttpClient,
        method: str,
        path: str,
        *,
        params: Mapping[str, str | int | float | bool] | None = None,
        json_body: object | None = None,
    ) -> BillyResponse:
        del self, params
        requests.append((method, path, json_body))
        if path == "/attachments":
            return BillyResponse(200, {"attachments": [{"id": "attachment-1"}]})
        raise AssertionError(f"unexpected request: {method} {path}")

    monkeypatch.setattr(BillyHttpClient, "request", fake_request)
    server = create_server()
    preview = call_tool(
        server,
        "api_attachments_create_preview",
        {"attachment": {"priority": 2}},
    )

    mismatch = call_tool(
        server,
        "api_sales_tax_rules_delete_execute",
        {"confirmation_ticket": preview["confirmation_ticket"]},
    )

    assert mismatch["code"] == StableErrorCode.CONFIRMATION_MISMATCH
    assert requests == []

    execution = call_tool(
        server,
        "api_attachments_create_execute",
        {"confirmation_ticket": preview["confirmation_ticket"]},
    )
    assert execution["changed_records"] == {"attachments": [{"id": "attachment-1"}]}
    assert requests == [("POST", "/attachments", {"attachment": {"priority": 2}})]
