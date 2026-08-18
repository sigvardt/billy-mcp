"""Given closed create-form evidence, When deriving an action, Then none remains."""

from __future__ import annotations

from pathlib import Path
from typing import Final

_REQUIRED: Final[list[str]] = [
    "ember_unique_normal_action",
    "fiber_unique_normal_action",
    "listener_unique_normal_action",
    "descendant_unique_target",
    "post_click_exact_match",
    "structure_transferable_action",
    "vaelg_kunde_proved_bind",
    "draft_save_proved_bind",
    "scoped_unique_action",
    "list_cta_proved_bind",
    "closed_action_set_complete",
    "derived_interaction",
    "unique_normal_action",
    "next_slice",
    "proved_bind",
    "missing_keys",
]


def test_empty_evidence_misses_create_form_control_keys() -> None:
    """Given empty evidence, When checking keys, Then the research set is missing."""

    from billy_mcp.ui_writes.invoices_create_form_control import (
        REQUIRED_CREATE_FORM_CONTROL_KEYS,
        create_form_control_missing_keys,
    )

    missing = create_form_control_missing_keys({})
    assert missing == _REQUIRED
    assert list(REQUIRED_CREATE_FORM_CONTROL_KEYS) == _REQUIRED


def test_closed_evidence_derives_no_interaction(tmp_path: Path) -> None:
    """Given every closed probe, When deriving, Then next slice is product create."""

    from billy_mcp.ui_writes.invoices_create_form_control import (
        apply_create_form_control,
        closed_create_form_evidence,
        derived_interaction_from,
    )

    payload = closed_create_form_evidence()
    assert derived_interaction_from(payload) == "none"
    applied = apply_create_form_control(payload, dump_path=tmp_path / "control.json")
    assert applied["unique_normal_action"] is False
    assert applied["derived_interaction"] == "none"
    assert applied["next_slice"] == "product_create"
    assert applied["proved_bind"] == "none"
    assert applied["code"] == "UI_CHANGED"
    assert (tmp_path / "control.json").is_file()


def test_closed_action_token_is_not_unique(tmp_path: Path) -> None:
    """Given a closed click token, When deriving, Then it is not a unique action."""

    from billy_mcp.ui_writes.invoices_create_form_control import (
        apply_create_form_control,
        closed_create_form_evidence,
    )

    payload = closed_create_form_evidence()
    payload["derived_interaction"] = "click_wrapper"
    applied = apply_create_form_control(payload, dump_path=tmp_path / "closed.json")
    assert applied["derived_interaction"] == "none"
    assert applied["unique_normal_action"] is False
    assert applied["next_slice"] == "product_create"
    assert applied["code"] == "UI_CHANGED"


def test_fabricated_action_token_is_ignored(tmp_path: Path) -> None:
    """Given an invented token, When deriving, Then it is not a unique action."""

    from billy_mcp.ui_writes.invoices_create_form_control import (
        apply_create_form_control,
        closed_create_form_evidence,
    )

    payload = closed_create_form_evidence()
    payload["derived_interaction"] = "arrow_open"
    applied = apply_create_form_control(payload, dump_path=tmp_path / "invented.json")
    assert applied["derived_interaction"] == "none"
    assert applied["unique_normal_action"] is False
    assert applied["next_slice"] == "product_create"
    assert applied["code"] == "UI_CHANGED"


def test_helper_does_not_enumerate_entry_ctas() -> None:
    """Given the derivation helper, When reading source, Then entry-CTA dumps stay closed."""

    from billy_mcp.ui_writes import invoices_create_form_control

    body = Path(invoices_create_form_control.__file__).read_text(encoding="utf-8")
    assert "debtorbalance" not in body
    assert "ui_debtor_balances_list" not in body
    assert "Opret faktura" not in body
    assert "arrow_open" not in body
    assert "getEventListeners" not in body
    assert "Ember.View" not in body
    assert "__reactFiber" not in body


def test_dump_json_never_keeps_source_or_urls() -> None:
    """Given a derived dump, When serialized, Then source and URLs are absent."""

    from billy_mcp.ui_writes.invoices_create_form_control import (
        closed_create_form_evidence,
        create_form_control_dump_json,
    )

    text = create_form_control_dump_json(closed_create_form_evidence())
    assert "http" not in text
    assert "source" not in text
    assert "script" not in text
