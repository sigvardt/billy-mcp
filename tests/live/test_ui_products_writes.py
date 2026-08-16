"""Live MCP product-create write test.

Live submit waits for a root radio go-ahead. Parent 72C01DF9: contacts family
holds the current live slot. This file must not submit until that go-ahead
arrives. That skip is a concrete live blocker, not an unsafe skipped submit.

Cleanup blocker (research176): Billy has no equivalent product delete chrome
on mit.billy.dk. Do not invent ui_products_delete_*. Do not POST/PUT/DELETE
api.billysbilling.com. If a later submit lands, record the leftover unique
tagged name; do not API-delete it.

When a go-ahead arrives: unique tagged name MCP-TEST-PRODUCT-<node>-<nonce>,
FastMCP call_tool preview then execute, independent second UI session
read-back, four-state capture, purge raw frames, keep only a non-sensitive
vision record.
"""

from __future__ import annotations

import pytest

pytestmark = pytest.mark.live


def test_live_product_create_submit_waits_for_root_slot() -> None:
    pytest.skip(
        "Live submit blocked by parent radio 72C01DF9: contacts family holds "
        "the live slot. Not an unsafe skipped submit. Cleanup blocker: "
        "research176 dual-proved no Slet/Slet produkt UI delete chrome."
    )
