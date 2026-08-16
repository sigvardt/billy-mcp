"""Live invoice UI writes stay gated until root radios a live slot.

Contacts family holds the current slot (parent radio 30D194C8). This file must
not click Gem som kladde, Godkend, Send, or email. It must not construct
BrowserRuntime as a pass proof.
"""

from __future__ import annotations

import ast
import os
from pathlib import Path

import pytest

pytestmark = pytest.mark.live

_LIVE_SLOT_ENV = "BILLY_UI_WRITE_LIVE_SLOT"
_BLOCKER = (
    "root radio 30D194C8: contacts family has the live slot; "
    "invoice UI execute must not click Gem som kladde, Godkend, Send, or email"
)


def test_live_invoice_draft_submit_blocked_until_root_slot() -> None:
    """Record the contacts-slot hold. Do not submit an invoice."""

    granted = os.environ.get(_LIVE_SLOT_ENV, "").strip()
    assert granted != "invoices", (
        "live slot env is set to invoices, but this file still must not submit "
        "until the dual-session draft harness is written after root radio go-ahead"
    )
    assert "30D194C8" in _BLOCKER
    assert "Gem som kladde" in _BLOCKER
    tree = ast.parse(Path(__file__).read_text(encoding="utf-8"))
    imported: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module is not None:
            imported.add(node.module)
    assert "billy_mcp.browser" not in imported
    assert "billy_mcp.client" not in imported
    assert "httpx" not in imported
