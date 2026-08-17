"""DIV-ownership keys for the invoice Kunde right-edge hit (9F777B8F)."""

from __future__ import annotations

from pathlib import Path


def _live_div_ownership_payload() -> dict[str, object]:
    """Current live opener after the 198.8 dump. 9F777B8F keys are absent."""

    return {
        "field_name": "contact",
        "right_edge_offset": {"dx": 242, "dy": 20},
        "right_edge_element_from_point": {
            "tag": "DIV",
            "class_tokens": [],
            "name": None,
            "testid": None,
        },
        "right_edge_same_input": False,
        "appearance_token": "none",
        "background_image_kind": "none",
        "before_content_kind": "none",
        "after_content_kind": "none",
        "input_child_count": 0,
        "box": {"x": 65, "y": 121, "w": 250, "h": 40},
        "pointer_events": "auto",
        "named_opener": None,
    }


def test_live_opener_misses_9f777b8f_div_ownership_keys() -> None:
    """Given the current live opener, When checking DIV ownership, Then keys are missing."""

    from billy_mcp.ui_writes.invoices_kunde_div import (
        REQUIRED_DIV_OWNERSHIP_KEYS,
        div_ownership_missing_keys,
    )

    payload = _live_div_ownership_payload()
    assert div_ownership_missing_keys(payload) == list(REQUIRED_DIV_OWNERSHIP_KEYS)
    assert "right_edge_elements_from_point_stack" not in payload
    assert "hit_box" not in payload
    assert "hit_pointer_events" not in payload
    assert "hit_role" not in payload
    assert "hit_name_present" not in payload
    assert "hit_testid" not in payload
    assert "hit_class_tokens" not in payload
    assert "hit_direct_parent" not in payload
    assert "hit_contained_by_input" not in payload
    assert "hit_contains_input" not in payload
    assert "hit_shares_smallest_wrapper" not in payload
    assert "smallest_wrapper" not in payload
    assert "nearest_clickable_ancestor" not in payload


def test_complete_div_ownership_has_no_missing_keys() -> None:
    """Given a filled DIV-ownership dump, When checking keys, Then none are missing."""

    from billy_mcp.ui_writes.invoices_kunde_div import (
        div_belongs_to_kunde_control,
        div_ownership_missing_keys,
        empty_div_ownership,
        ownership_click_point,
        pointer_events_token,
    )

    payload = _live_div_ownership_payload()
    payload.update(empty_div_ownership())
    assert div_ownership_missing_keys(payload) == []
    assert pointer_events_token("AUTO") == "auto"
    assert pointer_events_token("") == "none"
    assert pointer_events_token("visible") == "other"
    assert div_belongs_to_kunde_control(payload) is False
    assert ownership_click_point(payload) is None


def test_div_belongs_to_kunde_control_requires_shared_wrapper() -> None:
    """Given wrapper and stack proof, When gating click, Then the point is allowed."""

    from billy_mcp.ui_writes.invoices_kunde_div import (
        div_belongs_to_kunde_control,
        empty_div_ownership,
        ownership_click_point,
    )

    payload = _live_div_ownership_payload()
    payload.update(empty_div_ownership())
    payload["hit_shares_smallest_wrapper"] = True
    payload["smallest_wrapper"] = {
        "tag": "DIV",
        "class_tokens": ["ember-view"],
        "contact_input_count": 1,
        "child_input_count": 1,
    }
    payload["right_edge_elements_from_point_stack"] = [
        {
            "tag": "DIV",
            "class_tokens": [],
            "name": None,
            "testid": None,
            "role": None,
            "pointer_events": "auto",
        },
        {
            "tag": "INPUT",
            "class_tokens": ["ember-text-field"],
            "name": "contact",
            "testid": None,
            "role": None,
            "pointer_events": "auto",
        },
    ]
    assert div_belongs_to_kunde_control(payload) is True
    assert ownership_click_point(payload) == {"x": 307, "y": 141}
    payload["smallest_wrapper"] = {
        "tag": "BODY",
        "class_tokens": [],
        "contact_input_count": 2,
        "child_input_count": 11,
    }
    assert div_belongs_to_kunde_control(payload) is False
    assert ownership_click_point(payload) is None


def test_observe_records_9f777b8f_div_ownership_keys() -> None:
    """Given the observe helper, Then it records the DIV-ownership keys."""

    source = Path("src/billy_mcp/ui_writes/invoices_form_observe.py").read_text(encoding="utf-8")
    assert "elementsFromPoint" in source
    assert "hit_shares_smallest_wrapper" in source
    assert "nearest_clickable_ancestor" in source
    bind = Path("src/billy_mcp/ui_writes/invoices_form_bind.py").read_text(encoding="utf-8")
    assert "capture_kunde_div_ownership_dump" in bind
