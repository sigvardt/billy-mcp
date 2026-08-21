"""Given an empty dump, When checking product archive-list keys, Then they are missing."""

from __future__ import annotations

from pathlib import Path
from typing import Final

_REQUIRED: Final[list[str]] = [
    "products_path_class",
    "products_heading_token",
    "search_control_visible",
    "vis_arkiverede_count",
    "arkiverede_count",
    "skjul_arkiverede_count",
    "archived_filter_token",
    "unique_restore_readback",
    "proved_bind",
    "missing_keys",
]


def test_empty_dump_misses_products_archive_list_keys() -> None:
    """Given an empty dump, When checking archive-list keys, Then the plan set is missing."""

    from billy_mcp.ui_writes.products_archive_list import (
        REQUIRED_PRODUCTS_ARCHIVE_LIST_KEYS,
        products_archive_list_missing_keys,
    )

    missing = products_archive_list_missing_keys({})
    assert missing == _REQUIRED
    assert list(REQUIRED_PRODUCTS_ARCHIVE_LIST_KEYS) == _REQUIRED


def test_complete_archive_list_dump_has_no_missing_keys(tmp_path: Path) -> None:
    """Given a filled archive-list dump, When checking keys, Then none are missing."""

    from billy_mcp.ui_writes.products_archive_list import (
        apply_products_archive_list_dump,
        empty_products_archive_list,
        products_archive_list_missing_keys,
        unique_restore_readback_from,
    )

    payload = empty_products_archive_list()
    assert products_archive_list_missing_keys(payload) == []
    assert unique_restore_readback_from(payload) == "none"
    applied = apply_products_archive_list_dump(payload, dump_path=tmp_path / "archive.json")
    assert applied["archived_filter_token"] == "none"
    assert applied["unique_restore_readback"] == "none"
    assert applied["proved_bind"] == "none"
    assert applied["code"] == "UI_CHANGED"
    assert (tmp_path / "archive.json").is_file()


def test_unique_restore_needs_exactly_one_named_count() -> None:
    """Given mixed archive counts, When classifying, Then restore stays none."""

    from billy_mcp.ui_writes.products_archive_list import (
        archived_filter_token_from,
        empty_products_archive_list,
        unique_restore_readback_from,
    )

    payload = empty_products_archive_list()
    assert archived_filter_token_from(payload) == "none"
    payload["vis_arkiverede_count"] = 1
    assert archived_filter_token_from(payload) == "vis_arkiverede"
    assert unique_restore_readback_from(payload) == "show_archived_filter"
    payload["arkiverede_count"] = 2
    assert archived_filter_token_from(payload) == "none"
    assert unique_restore_readback_from(payload) == "none"
    payload["arkiverede_count"] = 1
    payload["skjul_arkiverede_count"] = 0
    assert archived_filter_token_from(payload) == "none"
    payload["vis_arkiverede_count"] = 0
    payload["arkiverede_count"] = 0
    payload["skjul_arkiverede_count"] = 1
    assert archived_filter_token_from(payload) == "skjul_arkiverede"
    assert unique_restore_readback_from(payload) == "show_archived_filter"


def test_archive_list_never_keeps_values() -> None:
    """Given live labels, When classified, Then only tokens remain."""

    from billy_mcp.ui_writes.products_archive_list import (
        empty_products_archive_list,
        products_archive_list_dump_json,
    )
    from billy_mcp.ui_writes.products_delete_chrome import classify_products_path

    assert classify_products_path("https://mit.billy.dk/acme/products") == "products"
    encoded = products_archive_list_dump_json(empty_products_archive_list())
    assert "https://" not in encoded
    assert "acme" not in encoded
    assert "MCP-TEST-PRODUCT-" not in encoded
    assert "Vis arkiverede" not in encoded


def test_delivered_archive_list_dump_requires_complete_keys(tmp_path: Path) -> None:
    """Given a complete dump file, When checking delivery, Then it is delivered."""

    from billy_mcp.ui_writes.products_archive_list import (
        apply_products_archive_list_dump,
        empty_products_archive_list,
        products_archive_list_dump_is_delivered,
    )

    missing = tmp_path / "missing.json"
    assert products_archive_list_dump_is_delivered(missing) is False
    path = tmp_path / "delivered.json"
    apply_products_archive_list_dump(empty_products_archive_list(), dump_path=path)
    assert products_archive_list_dump_is_delivered(path) is True


def test_persist_gate_ignores_archive_list_restore_token() -> None:
    """Given the persist gate, When reading source, Then it still requires Mere/Slet."""

    from billy_mcp.ui_writes import products_delete_chrome

    body = Path(products_delete_chrome.__file__).read_text(encoding="utf-8")
    assert "def product_persist_allowed" in body
    assert "proved_delete_path_from" in body
    assert "unique_restore_readback" not in body
    assert "products_archive_list" not in body


def test_product_persist_stays_closed_when_archive_list_is_unique(tmp_path: Path) -> None:
    """Given a unique list filter, When checking persist, Then create stays closed."""

    from billy_mcp.ui_writes.products_archive_list import (
        apply_products_archive_list_dump,
        empty_products_archive_list,
    )
    from billy_mcp.ui_writes.products_delete_chrome import (
        PRODUCTS_DELETE_CHROME_DUMP,
        product_persist_allowed,
    )

    payload = empty_products_archive_list()
    payload["vis_arkiverede_count"] = 1
    apply_products_archive_list_dump(payload, dump_path=tmp_path / "archive.json")
    assert product_persist_allowed(PRODUCTS_DELETE_CHROME_DUMP) is False
    assert product_persist_allowed(tmp_path / "archive.json") is False


def test_products_create_honesty_row_names_preview_and_is_proved() -> None:
    """Given the proved product create row, When reading the manifest, Then it is green."""

    import yaml

    root = Path(__file__).resolve().parents[2]
    document = yaml.safe_load((root / "coverage" / "ui_workflows_manifest.yaml").read_text())
    rows = {str(row["id"]): row for row in document["workflows"]}
    row = rows["ui.parity.products.create"]
    assert row["tool_name"] == "ui_products_create_preview"
    assert row["parity_status"] == "preview_execute"
    assert row["implemented"] is True
    assert row["live_tested"] is True
    assert row["vision_verified"] is True


def test_archive_list_helper_has_no_identity_inspectors() -> None:
    """Given the archive-list helper, When reading source, Then closed inspectors stay closed."""

    from billy_mcp.ui_writes import products_archive_list

    body = Path(products_archive_list.__file__).read_text(encoding="utf-8")
    assert "getEventListeners" not in body
    assert "getScriptSource" not in body
    assert "Ember.View" not in body
    assert "__reactFiber" not in body
    assert "page.evaluate" not in body
    assert ".evaluate(" not in body
    assert "page.goto" not in body
    assert "force=True" not in body
    assert "click_exact_label" not in body
    assert "_MERE" not in body
    assert "_GEM" not in body
    assert "_OPRET" not in body
