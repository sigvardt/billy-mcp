"""Given an empty dump, When checking prebind keys, Then they are missing."""

from __future__ import annotations

from pathlib import Path
from typing import Final

_REQUIRED: Final[list[str]] = [
    "detail_path_class",
    "tagged_name_visible",
    "exact_ret_count",
    "exact_opret_faktura_role",
    "exact_opret_faktura_count",
    "href_path_class",
    "href_query_token_class",
    "clicked_opret_faktura",
    "destination_heading_token",
    "contact_input_value_len",
    "contact_input_matches_tag",
    "unique_normal_action",
    "proved_prebind",
    "missing_keys",
]


def test_empty_dump_misses_customer_detail_prebind_keys() -> None:
    """Given an empty dump, When checking prebind keys, Then the research set is missing."""

    from billy_mcp.ui_writes.invoices_customer_detail_prebind import (
        REQUIRED_CUSTOMER_DETAIL_PREBIND_KEYS,
        customer_detail_prebind_missing_keys,
    )

    missing = customer_detail_prebind_missing_keys({})
    assert missing == _REQUIRED
    assert list(REQUIRED_CUSTOMER_DETAIL_PREBIND_KEYS) == _REQUIRED


def test_complete_prebind_dump_has_no_missing_keys(tmp_path: Path) -> None:
    """Given a filled prebind dump, When checking keys, Then none are missing."""

    from billy_mcp.ui_writes.invoices_customer_detail_prebind import (
        apply_customer_detail_prebind_dump,
        customer_detail_prebind_missing_keys,
        empty_customer_detail_prebind,
        unique_normal_action_from,
    )

    payload = empty_customer_detail_prebind()
    assert customer_detail_prebind_missing_keys(payload) == []
    assert unique_normal_action_from(payload) is False
    applied = apply_customer_detail_prebind_dump(payload, dump_path=tmp_path / "prebind.json")
    assert applied["unique_normal_action"] is False
    assert applied["proved_prebind"] == "none"
    assert applied["code"] == "UI_CHANGED"
    assert (tmp_path / "prebind.json").is_file()


def test_proved_prebind_needs_heading_and_tag_match(tmp_path: Path) -> None:
    """Given one Opret faktura without a selected tag, Then prebind stays none."""

    from billy_mcp.ui_writes.invoices_customer_detail_prebind import (
        apply_customer_detail_prebind_dump,
        empty_customer_detail_prebind,
        proved_prebind_from,
    )

    payload = empty_customer_detail_prebind()
    payload["exact_opret_faktura_count"] = 1
    payload["exact_opret_faktura_role"] = "link"
    payload["destination_heading_token"] = "opret_faktura"
    payload["contact_input_matches_tag"] = False
    assert proved_prebind_from(payload) == "none"
    applied = apply_customer_detail_prebind_dump(payload, dump_path=tmp_path / "no-match.json")
    assert applied["unique_normal_action"] is True
    assert applied["proved_prebind"] == "none"
    assert applied["code"] == "UI_CHANGED"


def test_proved_prebind_accepts_heading_and_tag(tmp_path: Path) -> None:
    """Given heading Opret faktura and a matching contact field, Then prebind is proved."""

    from billy_mcp.ui_writes.invoices_customer_detail_prebind import (
        apply_customer_detail_prebind_dump,
        empty_customer_detail_prebind,
    )

    payload = empty_customer_detail_prebind()
    payload["exact_opret_faktura_count"] = 1
    payload["destination_heading_token"] = "opret_faktura"
    payload["contact_input_matches_tag"] = True
    payload["contact_input_value_len"] = 19
    applied = apply_customer_detail_prebind_dump(payload, dump_path=tmp_path / "proved.json")
    assert applied["unique_normal_action"] is True
    assert applied["proved_prebind"] == "customer_detail_opret_faktura"
    assert "code" not in applied


def test_href_classification_never_keeps_values() -> None:
    """Given an invoice-new href with a contact query, When classified, Then only tokens remain."""

    from billy_mcp.ui_writes.invoices_customer_detail_prebind import (
        classify_detail_path,
        classify_heading,
        classify_href,
        customer_detail_prebind_dump_json,
        empty_customer_detail_prebind,
    )

    path_class, query_class = classify_href("/acme/invoices/new?contact=secret-id")
    assert path_class == "invoices_new_with_query"
    assert query_class == "contact"
    bare_path, bare_query = classify_href("/acme/invoices/new")
    assert bare_path == "invoices_new"
    assert bare_query == "none"
    other_path, other_query = classify_href("/acme/invoices")
    assert other_path == "other"
    assert other_query == "none"
    assert classify_detail_path("https://mit.billy.dk/acme/contacts/abc/customer") == (
        "contacts_customer"
    )
    assert classify_heading("Opret faktura") == "opret_faktura"
    payload = empty_customer_detail_prebind()
    encoded = customer_detail_prebind_dump_json(payload)
    assert "https://" not in encoded
    assert "secret-id" not in encoded
    assert "MCP-UI-INV-" not in encoded
    assert "acme" not in encoded


def test_delivered_prebind_dump_requires_complete_keys(tmp_path: Path) -> None:
    """Given a complete dump file, When checking delivery, Then it is delivered."""

    from billy_mcp.ui_writes.invoices_customer_detail_prebind import (
        apply_customer_detail_prebind_dump,
        customer_detail_prebind_dump_is_delivered,
        empty_customer_detail_prebind,
    )

    missing = tmp_path / "missing.json"
    assert customer_detail_prebind_dump_is_delivered(missing) is False
    path = tmp_path / "delivered.json"
    apply_customer_detail_prebind_dump(empty_customer_detail_prebind(), dump_path=path)
    assert customer_detail_prebind_dump_is_delivered(path) is True


def test_prebind_helper_has_no_identity_inspectors() -> None:
    """Given the prebind helper, When reading source, Then closed inspectors stay closed."""

    from billy_mcp.ui_writes import invoices_customer_detail_prebind

    body = Path(invoices_customer_detail_prebind.__file__).read_text(encoding="utf-8")
    assert "getEventListeners" not in body
    assert "getScriptSource" not in body
    assert "Ember.View" not in body
    assert "__reactFiber" not in body
    assert "press_sequentially" not in body
    assert "callFunctionOn" not in body
    assert "page.goto" not in body
