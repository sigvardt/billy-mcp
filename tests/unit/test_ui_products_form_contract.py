"""Given an empty dump, When checking product form-contract keys, Then they are missing."""

from __future__ import annotations

from pathlib import Path
from typing import Final

_REQUIRED: Final[list[str]] = [
    "inventory_path_class",
    "inventory_heading_token",
    "create_form_open",
    "dialog_heading_token",
    "name_field_visible",
    "gem_produkt_count",
    "gem_count",
    "save_cta_token",
    "arkiveret_count",
    "cleanup_token",
    "unique_cleanup_path",
    "proved_submit",
    "missing_keys",
]


def test_empty_dump_misses_products_form_contract_keys() -> None:
    """Given an empty dump, When checking form-contract keys, Then the plan set is missing."""

    from billy_mcp.ui_writes.products_form_contract import (
        REQUIRED_PRODUCTS_FORM_CONTRACT_KEYS,
        products_form_contract_missing_keys,
    )

    missing = products_form_contract_missing_keys({})
    assert missing == _REQUIRED
    assert list(REQUIRED_PRODUCTS_FORM_CONTRACT_KEYS) == _REQUIRED


def test_complete_form_contract_dump_has_no_missing_keys(tmp_path: Path) -> None:
    """Given a filled form-contract dump, When checking keys, Then none are missing."""

    from billy_mcp.ui_writes.products_form_contract import (
        apply_products_form_contract_dump,
        empty_products_form_contract,
        products_form_contract_missing_keys,
        proved_submit_from,
        unique_cleanup_path_from,
    )

    payload = empty_products_form_contract()
    assert products_form_contract_missing_keys(payload) == []
    assert proved_submit_from(payload) == "none"
    assert unique_cleanup_path_from(payload) == "none"
    applied = apply_products_form_contract_dump(payload, dump_path=tmp_path / "contract.json")
    assert applied["proved_submit"] == "none"
    assert applied["unique_cleanup_path"] == "none"
    assert applied["code"] == "UI_CHANGED"
    assert (tmp_path / "contract.json").is_file()


def test_proved_submit_needs_exactly_one_gem_produkt() -> None:
    """Given Gem produkt count not exactly one, When classifying, Then submit stays none."""

    from billy_mcp.ui_writes.products_form_contract import (
        empty_products_form_contract,
        proved_submit_from,
    )

    payload = empty_products_form_contract()
    payload["gem_produkt_count"] = 0
    assert proved_submit_from(payload) == "none"
    payload["gem_produkt_count"] = 2
    assert proved_submit_from(payload) == "none"
    payload["gem_produkt_count"] = 1
    assert proved_submit_from(payload) == "gem_produkt"


def test_unique_cleanup_path_needs_exactly_one_arkiveret() -> None:
    """Given Arkiveret count not exactly one, When classifying, Then cleanup stays none."""

    from billy_mcp.ui_writes.products_form_contract import (
        empty_products_form_contract,
        unique_cleanup_path_from,
    )

    payload = empty_products_form_contract()
    payload["arkiveret_count"] = 0
    assert unique_cleanup_path_from(payload) == "none"
    payload["arkiveret_count"] = 2
    assert unique_cleanup_path_from(payload) == "none"
    payload["arkiveret_count"] = 1
    assert unique_cleanup_path_from(payload) == "archive_checkbox"


def test_save_and_heading_classification_never_keeps_values() -> None:
    """Given live labels, When classified, Then only tokens remain."""

    from billy_mcp.ui_writes.products_delete_chrome import classify_inventory_path
    from billy_mcp.ui_writes.products_form_contract import (
        classify_dialog_heading,
        classify_dialog_heading_from_counts,
        classify_save_cta,
        empty_products_form_contract,
        products_form_contract_dump_json,
    )

    assert classify_inventory_path("https://mit.billy.dk/acme/inventory") == "inventory"
    assert classify_dialog_heading("Opret produkt") == "opret_produkt"
    assert classify_dialog_heading("Ret produkt") == "ret_produkt"
    assert classify_dialog_heading("Lagermodul") == "other"
    assert classify_dialog_heading_from_counts(opret_count=1, ret_count=1) == "other"
    assert classify_save_cta(gem_produkt_count=1, gem_count=0, create_form_open=True) == (
        "gem_produkt"
    )
    assert classify_save_cta(gem_produkt_count=0, gem_count=1, create_form_open=True) == "gem"
    assert classify_save_cta(gem_produkt_count=0, gem_count=0, create_form_open=True) == "other"
    encoded = products_form_contract_dump_json(empty_products_form_contract())
    assert "https://" not in encoded
    assert "acme" not in encoded
    assert "MCP-TEST-PRODUCT-" not in encoded


def test_delivered_form_contract_dump_requires_complete_keys(tmp_path: Path) -> None:
    """Given a complete dump file, When checking delivery, Then it is delivered."""

    from billy_mcp.ui_writes.products_form_contract import (
        apply_products_form_contract_dump,
        empty_products_form_contract,
        products_form_contract_dump_is_delivered,
    )

    missing = tmp_path / "missing.json"
    assert products_form_contract_dump_is_delivered(missing) is False
    path = tmp_path / "delivered.json"
    apply_products_form_contract_dump(empty_products_form_contract(), dump_path=path)
    assert products_form_contract_dump_is_delivered(path) is True


def test_execute_names_gem_produkt_while_persist_stays_closed() -> None:
    """Given the live official save label, When reading execute, Then persist stays closed."""

    from billy_mcp.ui_writes import products_submit
    from billy_mcp.ui_writes.products_delete_chrome import (
        PRODUCTS_DELETE_CHROME_DUMP,
        product_persist_allowed,
    )

    body = Path(products_submit.__file__).read_text(encoding="utf-8")
    assert "Gem produkt" in body
    assert 'clicks=("Gem",)' not in body
    assert product_persist_allowed(PRODUCTS_DELETE_CHROME_DUMP) is False


def test_product_persist_stays_closed_when_archive_is_present(tmp_path: Path) -> None:
    """Given official archive chrome, When checking persist, Then create stays closed."""

    from billy_mcp.ui_writes.products_delete_chrome import product_persist_allowed
    from billy_mcp.ui_writes.products_form_contract import (
        apply_products_form_contract_dump,
        empty_products_form_contract,
    )

    payload = empty_products_form_contract()
    payload["gem_produkt_count"] = 1
    payload["arkiveret_count"] = 1
    apply_products_form_contract_dump(payload, dump_path=tmp_path / "contract.json")
    assert product_persist_allowed(tmp_path / "missing-delete.json") is False


def test_form_contract_helper_has_no_identity_inspectors() -> None:
    """Given the form-contract helper, When reading source, Then closed inspectors stay closed."""

    from billy_mcp.ui_writes import products_form_contract

    body = Path(products_form_contract.__file__).read_text(encoding="utf-8")
    assert "getEventListeners" not in body
    assert "getScriptSource" not in body
    assert "Ember.View" not in body
    assert "__reactFiber" not in body
    assert "page.evaluate" not in body
    assert ".evaluate(" not in body
    assert "page.goto" not in body
    assert "force=True" not in body
