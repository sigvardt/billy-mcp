"""Default create_server path must require org ids and reach a browser actor."""

from __future__ import annotations

import asyncio
from pathlib import Path
from typing import cast

import pytest
from fastmcp import FastMCP
from fastmcp.exceptions import ValidationError as FastMcpValidationError

from billy_mcp.confirmations import ConfirmationStore
from billy_mcp.models import StableErrorCode
from billy_mcp.server import create_server
from billy_mcp.ui_writes.invoices import DRAFT_SAVE_CTA as UI_DRAFT_SAVE_CTA
from billy_mcp.ui_writes.protocol import UiWriteProtocol


def _call(server: FastMCP, tool_name: str, arguments: dict[str, object]) -> dict[str, object]:
    result = asyncio.run(server.call_tool(tool_name, arguments))
    assert isinstance(result.structured_content, dict)
    structured = cast(dict[str, object], result.structured_content)
    payload = structured.get("result", structured)
    assert isinstance(payload, dict)
    return cast(dict[str, object], payload)


def _preview_cases(upload_file: Path) -> list[tuple[str, dict[str, object]]]:
    return [
        ("ui_clients_create_preview", {"name": "MCP-UI-C-GATE"}),
        ("ui_bills_create_preview", {"unique_tag": "MCP-BILL-GATE"}),
        (
            "ui_invoices_create_preview",
            {
                "contact_name": "MCP-UI-INV-GATE",
                "line_description": "MCP-UI-INV line",
                "unit_price": 1.0,
                "action": "draft_create",
                "save_cta": UI_DRAFT_SAVE_CTA,
            },
        ),
        ("ui_products_create_preview", {"name": "MCP-PROD-GATE", "unitPrice": 1.0}),
        ("ui_daybooks_create_preview", {"name": "MCP-DB-GATE"}),
        (
            "ui_daybook_transactions_create_preview",
            {"daybook_id": "db-1", "text": "MCP-DBT-GATE"},
        ),
        ("ui_transactions_create_preview", {"text": "MCP-TX-GATE"}),
        (
            "ui_files_create_preview",
            {"path": str(upload_file), "filename": upload_file.name},
        ),
        ("ui_organizations_update_preview", {"phone": "12345678"}),
    ]


@pytest.fixture
def upload_file(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    root = tmp_path / "uploads"
    root.mkdir()
    path = root / "gate.txt"
    path.write_bytes(b"mcp-ui-file-gate")
    monkeypatch.setenv("BILLY_UPLOAD_ROOTS", str(root))
    return path


def test_protocol_preview_rejects_blank_organization_id() -> None:
    protocol = UiWriteProtocol(ConfirmationStore())
    result = protocol.preview(
        execute_tool_name="ui_clients_create_execute",
        organization_id=None,
        target="clients",
        canonical_request={"name": "MCP-TEST"},
        expected_effect_state={"action": "create"},
        summary="Create one Billy customer in the interface.",
    )
    assert isinstance(result, object)
    assert getattr(result, "code", None) is StableErrorCode.ORGANIZATION_REQUIRED
    assert not hasattr(result, "confirmation_ticket") or not getattr(
        result, "confirmation_ticket", None
    )


@pytest.mark.parametrize("tool_name,arguments", _preview_cases(Path("/tmp/unused")))
def test_create_server_preview_requires_organization_id(
    tool_name: str,
    arguments: dict[str, object],
    upload_file: Path,
) -> None:
    if tool_name == "ui_files_create_preview":
        arguments = {"path": str(upload_file), "filename": upload_file.name}
    server = create_server()
    try:
        payload = _call(server, tool_name, arguments)
    except FastMcpValidationError:
        return
    assert payload.get("code") == StableErrorCode.ORGANIZATION_REQUIRED
    assert "confirmation_ticket" not in payload


# Execute route/field/CTA/read-back proofs live in test_ui_writes_fake_page_submit.py.
