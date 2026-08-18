"""Given an empty dump, When checking product delete-chrome keys, Then they are missing."""

from __future__ import annotations

from pathlib import Path
from typing import Final

_REQUIRED: Final[list[str]] = [
    "products_path_class",
    "products_heading_token",
    "products_mere_open",
    "products_mere_slet_count",
    "products_mere_slet_produkt_count",
    "inventory_path_class",
    "inventory_heading_token",
    "inventory_slet_count",
    "inventory_slet_produkt_count",
    "save_cta_token",
    "create_form_open",
    "name_field_visible",
    "proved_delete_path",
    "missing_keys",
]


def test_empty_dump_misses_products_delete_chrome_keys() -> None:
    """Given an empty dump, When checking delete-chrome keys, Then the plan set is missing."""

    from billy_mcp.ui_writes.products_delete_chrome import (
        REQUIRED_PRODUCTS_DELETE_CHROME_KEYS,
        products_delete_chrome_missing_keys,
    )

    missing = products_delete_chrome_missing_keys({})
    assert missing == _REQUIRED
    assert list(REQUIRED_PRODUCTS_DELETE_CHROME_KEYS) == _REQUIRED


def test_complete_delete_chrome_dump_has_no_missing_keys(tmp_path: Path) -> None:
    """Given a filled delete-chrome dump, When checking keys, Then none are missing."""

    from billy_mcp.ui_writes.products_delete_chrome import (
        apply_products_delete_chrome_dump,
        empty_products_delete_chrome,
        products_delete_chrome_missing_keys,
        proved_delete_path_from,
    )

    payload = empty_products_delete_chrome()
    assert products_delete_chrome_missing_keys(payload) == []
    assert proved_delete_path_from(payload) == "none"
    applied = apply_products_delete_chrome_dump(payload, dump_path=tmp_path / "chrome.json")
    assert applied["proved_delete_path"] == "none"
    assert applied["code"] == "UI_CHANGED"
    assert (tmp_path / "chrome.json").is_file()


def test_proved_delete_path_needs_exactly_one_unique_count() -> None:
    """Given two delete counts of 1, When classifying, Then the path stays none."""

    from billy_mcp.ui_writes.products_delete_chrome import (
        empty_products_delete_chrome,
        proved_delete_path_from,
    )

    payload = empty_products_delete_chrome()
    payload["products_mere_slet_count"] = 1
    payload["inventory_slet_count"] = 1
    assert proved_delete_path_from(payload) == "none"
    payload["inventory_slet_count"] = 0
    assert proved_delete_path_from(payload) == "products_mere_slet"
    payload["products_mere_slet_count"] = 2
    assert proved_delete_path_from(payload) == "none"


def test_path_and_heading_classification_never_keeps_values() -> None:
    """Given live URLs and headings, When classified, Then only tokens remain."""

    from billy_mcp.ui_writes.products_delete_chrome import (
        classify_inventory_heading,
        classify_inventory_path,
        classify_products_heading,
        classify_products_path,
        classify_save_cta,
        empty_products_delete_chrome,
        products_delete_chrome_dump_json,
    )

    assert classify_products_path("https://mit.billy.dk/acme/products") == "products"
    assert classify_products_path("https://mit.billy.dk/acme/products/new") == "other"
    assert classify_inventory_path("https://mit.billy.dk/acme/inventory") == "inventory"
    assert classify_products_heading("Produkter") == "produkter"
    assert classify_inventory_heading("Lagermodul") == "lagermodul"
    assert classify_save_cta("Gem") == "gem"
    assert classify_save_cta("Gem som kladde") == "other"
    encoded = products_delete_chrome_dump_json(empty_products_delete_chrome())
    assert "https://" not in encoded
    assert "acme" not in encoded
    assert "MCP-TEST-PRODUCT-" not in encoded


def test_delivered_delete_chrome_dump_requires_complete_keys(tmp_path: Path) -> None:
    """Given a complete dump file, When checking delivery, Then it is delivered."""

    from billy_mcp.ui_writes.products_delete_chrome import (
        apply_products_delete_chrome_dump,
        empty_products_delete_chrome,
        products_delete_chrome_dump_is_delivered,
    )

    missing = tmp_path / "missing.json"
    assert products_delete_chrome_dump_is_delivered(missing) is False
    path = tmp_path / "delivered.json"
    apply_products_delete_chrome_dump(empty_products_delete_chrome(), dump_path=path)
    assert products_delete_chrome_dump_is_delivered(path) is True


def test_product_persist_allowed_requires_unique_delete_path(tmp_path: Path) -> None:
    """Given a closed delete-chrome dump, When checking persist, Then create stays closed."""

    from billy_mcp.ui_writes.products_delete_chrome import (
        apply_products_delete_chrome_dump,
        empty_products_delete_chrome,
        product_persist_allowed,
    )

    missing = tmp_path / "missing.json"
    assert product_persist_allowed(missing) is False
    closed = tmp_path / "closed.json"
    apply_products_delete_chrome_dump(empty_products_delete_chrome(), dump_path=closed)
    assert product_persist_allowed(closed) is False
    allowed = tmp_path / "allowed.json"
    payload = empty_products_delete_chrome()
    payload["products_mere_slet_count"] = 1
    apply_products_delete_chrome_dump(payload, dump_path=allowed)
    assert product_persist_allowed(allowed) is True


def test_browser_submitter_refuses_without_delete_path(tmp_path: Path) -> None:
    """Given no proved delete path, When submit_create runs, Then it does not persist."""

    import asyncio

    from billy_mcp.models import StableErrorCode, ToolError
    from billy_mcp.ui_writes.products import BrowserProductSubmitter
    from billy_mcp.ui_writes.products_delete_chrome import (
        apply_products_delete_chrome_dump,
        empty_products_delete_chrome,
    )

    class _StubRuntime:
        def independent_readback_runtime(self) -> _StubRuntime:
            return self

    dump = tmp_path / "closed.json"
    apply_products_delete_chrome_dump(empty_products_delete_chrome(), dump_path=dump)
    actor = BrowserProductSubmitter(_StubRuntime(), delete_chrome_dump=dump)  # type: ignore[arg-type]
    result = asyncio.run(actor.submit_create({"name": "MCP-UI-PRD-x"}, organization_id="org"))
    assert isinstance(result, ToolError)
    assert result.code == StableErrorCode.UI_CHANGED


def test_delete_chrome_helper_has_no_identity_inspectors() -> None:
    """Given the delete-chrome helper, When reading source, Then closed inspectors stay closed."""

    from billy_mcp.ui_writes import products_delete_chrome

    body = Path(products_delete_chrome.__file__).read_text(encoding="utf-8")
    assert "getEventListeners" not in body
    assert "getScriptSource" not in body
    assert "Ember.View" not in body
    assert "__reactFiber" not in body
    assert "page.evaluate" not in body
    assert ".evaluate(" not in body
    assert "page.goto" not in body
    assert "force=True" not in body
