"""Live MCP submit for ui_organizations_update.

Blocked by parent radio D5136C2E until root grants this family the live slot.
Contacts holds the current slot. This file must not click Gem ændringer or
change company settings until that go-ahead exists.

Set BILLY_UI_ORG_WRITES_LIVE_SLOT=1 only after root radios the slot. The
offline preview path below uses a recording submitter and never opens a browser.
"""

from __future__ import annotations

import asyncio
import os
from typing import cast

import pytest
from fastmcp import FastMCP

from billy_mcp.confirmations import ConfirmationStore
from billy_mcp.ui_writes.organizations import (
    RecordingOrganizationSubmitter,
    register_ui_organization_write_tools,
)
from billy_mcp.ui_writes.protocol import UiWriteProtocol

pytestmark = pytest.mark.live

LIVE_SLOT_ENV = "BILLY_UI_ORG_WRITES_LIVE_SLOT"


def _call_tool(server: FastMCP, tool_name: str, arguments: dict[str, object]) -> dict[str, object]:
    result = asyncio.run(server.call_tool(tool_name, arguments))
    structured_content = result.structured_content
    assert isinstance(structured_content, dict)
    payload = structured_content.get("result", structured_content)
    assert isinstance(payload, dict)
    return cast(dict[str, object], payload)


def test_preview_is_mutation_free_and_live_execute_waits_for_root_slot() -> None:
    """Preview via FastMCP. Skip execute submit until root radios the slot."""

    submitter = RecordingOrganizationSubmitter()
    server = FastMCP("ui-organization-live-wait")
    register_ui_organization_write_tools(
        server,
        UiWriteProtocol(ConfirmationStore()),
        submitter=submitter,
    )

    preview = _call_tool(
        server,
        "ui_organizations_update_preview",
        {"phone": "+4599990000"},
    )
    assert preview["confirmation_ticket"]
    assert submitter.calls == []

    if os.environ.get(LIVE_SLOT_ENV, "").strip() != "1":
        pytest.skip(
            "Live org-settings submit blocked by radio D5136C2E; "
            "contacts family holds the current slot. No company field changed."
        )

    pytest.fail(
        "Live slot flag is set. Wire FastMCP execute submit, second-session "
        "read-back, four-state capture, and restore before claiming pass."
    )
