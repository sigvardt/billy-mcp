"""Given an empty dump, When checking list-CTA keys, Then they are missing."""

from __future__ import annotations

from pathlib import Path
from typing import Final

_REQUIRED: Final[list[str]] = [
    "list_path_class",
    "exact_list_opret_faktura_count",
    "list_opret_faktura_role",
    "clicked_list_opret_faktura",
    "destination_path_class",
    "destination_query_token_class",
    "destination_heading_token",
    "contact_input_present",
    "contact_input_value_len",
    "contact_input_matches_tag",
    "option_role_count",
    "aria_expanded_token",
    "unique_action",
    "proved_bind",
    "missing_keys",
]


def test_empty_dump_misses_list_opret_faktura_keys() -> None:
    """Given an empty dump, When checking list-CTA keys, Then the research set is missing."""

    from billy_mcp.ui_writes.invoices_list_opret_faktura import (
        REQUIRED_LIST_OPRET_FAKTURA_KEYS,
        list_opret_faktura_missing_keys,
    )

    missing = list_opret_faktura_missing_keys({})
    assert missing == _REQUIRED
    assert list(REQUIRED_LIST_OPRET_FAKTURA_KEYS) == _REQUIRED


def test_complete_list_cta_dump_has_no_missing_keys(tmp_path: Path) -> None:
    """Given a filled list-CTA dump, When checking keys, Then none are missing."""

    from billy_mcp.ui_writes.invoices_list_opret_faktura import (
        apply_list_opret_faktura_dump,
        empty_list_opret_faktura,
        list_opret_faktura_missing_keys,
        unique_action_from,
    )

    payload = empty_list_opret_faktura()
    assert list_opret_faktura_missing_keys(payload) == []
    assert unique_action_from(payload) == "none"
    applied = apply_list_opret_faktura_dump(payload, dump_path=tmp_path / "list-cta.json")
    assert applied["unique_action"] == "none"
    assert applied["proved_bind"] == "none"
    assert applied["code"] == "UI_CHANGED"
    assert (tmp_path / "list-cta.json").is_file()


def test_query_token_alone_is_not_a_bind(tmp_path: Path) -> None:
    """Given a contact query token without a match, When applying, Then bind stays none."""

    from billy_mcp.ui_writes.invoices_list_opret_faktura import (
        apply_list_opret_faktura_dump,
        empty_list_opret_faktura,
        proved_bind_from,
    )

    payload = empty_list_opret_faktura()
    payload["destination_path_class"] = "invoices_new_with_query"
    payload["destination_query_token_class"] = "contact"
    payload["contact_input_matches_tag"] = False
    payload["option_role_count"] = 0
    assert proved_bind_from(payload) == "none"
    applied = apply_list_opret_faktura_dump(payload, dump_path=tmp_path / "query-only.json")
    assert applied["proved_bind"] == "none"
    assert applied["code"] == "UI_CHANGED"


def test_prebound_tag_match_proves_list_cta_prebound(tmp_path: Path) -> None:
    """Given a matching contact field, When applying, Then bind is list_cta_prebound."""

    from billy_mcp.ui_writes.invoices_list_opret_faktura import (
        apply_list_opret_faktura_dump,
        empty_list_opret_faktura,
    )

    payload = empty_list_opret_faktura()
    payload["clicked_list_opret_faktura"] = True
    payload["contact_input_present"] = True
    payload["contact_input_matches_tag"] = True
    payload["contact_input_value_len"] = 19
    applied = apply_list_opret_faktura_dump(payload, dump_path=tmp_path / "prebound.json")
    assert applied["proved_bind"] == "list_cta_prebound"
    assert "code" not in applied


def test_one_option_proves_existing_option_bind(tmp_path: Path) -> None:
    """Given one visible option and no tag match, When applying, Then bind is existing_option."""

    from billy_mcp.ui_writes.invoices_list_opret_faktura import (
        apply_list_opret_faktura_dump,
        empty_list_opret_faktura,
    )

    payload = empty_list_opret_faktura()
    payload["option_role_count"] = 1
    payload["contact_input_matches_tag"] = False
    applied = apply_list_opret_faktura_dump(payload, dump_path=tmp_path / "option.json")
    assert applied["unique_action"] == "existing_option"
    assert applied["proved_bind"] == "list_cta_existing_option"
    assert "code" not in applied


def test_list_path_and_dump_json_never_keep_values() -> None:
    """Given list URLs and a dump, When classified, Then only tokens remain."""

    from billy_mcp.ui_writes.invoices_list_opret_faktura import (
        classify_list_path,
        empty_list_opret_faktura,
        list_opret_faktura_dump_json,
    )

    assert classify_list_path("https://mit.billy.dk/acme/invoices") == "invoices"
    assert classify_list_path("https://mit.billy.dk/acme/invoices/empty") == "invoices_empty"
    assert classify_list_path("https://mit.billy.dk/acme/invoices/new") == "other"
    payload = empty_list_opret_faktura()
    encoded = list_opret_faktura_dump_json(payload)
    assert "https://" not in encoded
    assert "acme" not in encoded
    assert "MCP-UI-INV-" not in encoded


def test_delivered_list_cta_dump_requires_complete_keys(tmp_path: Path) -> None:
    """Given a complete dump file, When checking delivery, Then it is delivered."""

    from billy_mcp.ui_writes.invoices_list_opret_faktura import (
        apply_list_opret_faktura_dump,
        empty_list_opret_faktura,
        list_opret_faktura_dump_is_delivered,
    )

    missing = tmp_path / "missing.json"
    assert list_opret_faktura_dump_is_delivered(missing) is False
    path = tmp_path / "delivered.json"
    apply_list_opret_faktura_dump(empty_list_opret_faktura(), dump_path=path)
    assert list_opret_faktura_dump_is_delivered(path) is True


def test_list_cta_helper_does_not_goto_create() -> None:
    """Given the list-CTA helper, When reading source, Then closed probes stay closed."""

    from billy_mcp.ui_writes import invoices_list_opret_faktura

    body = Path(invoices_list_opret_faktura.__file__).read_text(encoding="utf-8")
    assert "invoices/new" not in body
    assert "page.goto" not in body
    assert "press_sequentially" not in body
    assert "Gem som kladde" not in body
    assert "getEventListeners" not in body
    assert "Ember.View" not in body
    assert "__reactFiber" not in body
