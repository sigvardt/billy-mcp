"""Given an empty dump, When checking organization phone keys, Then they are missing."""

from __future__ import annotations

from pathlib import Path
from typing import Final

_REQUIRED: Final[list[str]] = [
    "settings_path_class",
    "heading_token",
    "company_panel_markers_present",
    "phone_field_visible",
    "phone_input_name_class",
    "phone_value_len",
    "save_cta_token",
    "save_cta_count",
    "forbidden_surface_token",
    "proved_phone_only",
    "missing_keys",
]


def test_empty_dump_misses_organizations_phone_keys() -> None:
    """Given an empty dump, When checking phone-dump keys, Then the plan set is missing."""

    from billy_mcp.ui_writes.organizations_phone_dump import (
        REQUIRED_ORGANIZATIONS_PHONE_DUMP_KEYS,
        organizations_phone_dump_missing_keys,
    )

    missing = organizations_phone_dump_missing_keys({})
    assert missing == _REQUIRED
    assert list(REQUIRED_ORGANIZATIONS_PHONE_DUMP_KEYS) == _REQUIRED


def test_complete_phone_dump_has_no_missing_keys(tmp_path: Path) -> None:
    """Given a filled phone dump, When checking keys, Then none are missing."""

    from billy_mcp.ui_writes.organizations_phone_dump import (
        apply_organizations_phone_dump,
        empty_organizations_phone_dump,
        organizations_phone_dump_missing_keys,
        proved_phone_only_from,
    )

    payload = empty_organizations_phone_dump()
    assert organizations_phone_dump_missing_keys(payload) == []
    assert proved_phone_only_from(payload) is False
    applied = apply_organizations_phone_dump(payload, dump_path=tmp_path / "phone.json")
    assert applied["proved_phone_only"] is False
    assert applied["code"] == "UI_CHANGED"
    assert (tmp_path / "phone.json").is_file()


def test_proved_phone_only_needs_every_gate() -> None:
    """Given a near-complete surface, When one gate fails, Then proved stays false."""

    from billy_mcp.ui_writes.organizations_phone_dump import (
        empty_organizations_phone_dump,
        proved_phone_only_from,
    )

    payload = empty_organizations_phone_dump()
    payload.update(
        {
            "settings_path_class": "settings",
            "heading_token": "indstillinger",
            "company_panel_markers_present": True,
            "phone_input_name_class": "phone",
            "save_cta_token": "gem_aendringer",
            "save_cta_count": 1,
            "forbidden_surface_token": "none",
        }
    )
    assert proved_phone_only_from(payload) is True
    payload["save_cta_count"] = 2
    assert proved_phone_only_from(payload) is False
    payload["save_cta_count"] = 1
    payload["forbidden_surface_token"] = "users"
    assert proved_phone_only_from(payload) is False


def test_empty_original_phone_allows_persist() -> None:
    """Given a proved surface with value_len 0, When persist is checked, Then it is allowed."""

    from billy_mcp.ui_writes.organizations_phone_dump import (
        empty_organizations_phone_dump,
        persist_allowed_from,
        proved_phone_only_from,
    )

    payload = empty_organizations_phone_dump()
    payload.update(
        {
            "settings_path_class": "settings",
            "heading_token": "indstillinger",
            "company_panel_markers_present": True,
            "phone_field_visible": True,
            "phone_input_name_class": "phone",
            "phone_value_len": 0,
            "save_cta_token": "gem_aendringer",
            "save_cta_count": 1,
            "forbidden_surface_token": "none",
        }
    )
    assert proved_phone_only_from(payload) is True
    assert persist_allowed_from(payload) is True
    payload["phone_value_len"] = 8
    assert persist_allowed_from(payload) is True


def test_path_heading_and_save_classification_never_keeps_values() -> None:
    """Given live URLs and labels, When classified, Then only tokens remain."""

    from billy_mcp.ui_writes.organizations_phone_dump import (
        classify_forbidden_surface,
        classify_heading,
        classify_phone_input_name,
        classify_save_cta,
        classify_settings_path,
        empty_organizations_phone_dump,
        organizations_phone_dump_json,
    )

    assert classify_settings_path("https://mit.billy.dk/acme/settings") == "settings"
    assert classify_settings_path("https://mit.billy.dk/acme/settings/users") == "other"
    assert classify_heading("Indstillinger") == "indstillinger"
    assert classify_save_cta("Gem ændringer") == "gem_aendringer"
    assert classify_save_cta("Gem") == "other"
    assert classify_phone_input_name("phone") == "phone"
    assert classify_phone_input_name("tel") == "other"
    assert classify_forbidden_surface("https://mit.billy.dk/acme/settings/users") == "users"
    assert classify_forbidden_surface("https://mit.billy.dk/acme/settings") == "none"
    encoded = organizations_phone_dump_json(empty_organizations_phone_dump())
    assert "https://" not in encoded
    assert "acme" not in encoded
    assert "+45" not in encoded


def test_delivered_phone_dump_requires_complete_keys(tmp_path: Path) -> None:
    """Given a complete dump file, When checking delivery, Then it is delivered."""

    from billy_mcp.ui_writes.organizations_phone_dump import (
        apply_organizations_phone_dump,
        empty_organizations_phone_dump,
        organizations_phone_dump_is_delivered,
    )

    missing = tmp_path / "missing.json"
    assert organizations_phone_dump_is_delivered(missing) is False
    path = tmp_path / "delivered.json"
    apply_organizations_phone_dump(empty_organizations_phone_dump(), dump_path=path)
    assert organizations_phone_dump_is_delivered(path) is True


def test_phone_dump_helper_has_no_identity_inspectors() -> None:
    """Given the phone-dump helper, When reading source, Then closed inspectors stay closed."""

    from billy_mcp.ui_writes import organizations_phone_dump

    body = Path(organizations_phone_dump.__file__).read_text(encoding="utf-8")
    assert "getEventListeners" not in body
    assert "getScriptSource" not in body
    assert "Ember.View" not in body
    assert "__reactFiber" not in body
    assert "page.evaluate" not in body
    assert ".evaluate(" not in body
    assert "page.goto" not in body
    assert "force=True" not in body
