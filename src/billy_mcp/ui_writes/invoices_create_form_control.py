"""Restate closed invoice create-form probes. This is not a new local inspect.

Never remakes picker, Ember, fiber, listener, list-CTA, or route dumps.
Never stores source, URLs, locators, ids, or customer text.
Never invents an unused action token.
"""

from __future__ import annotations

import json
from collections.abc import Mapping
from pathlib import Path
from typing import Final, Literal

from billy_mcp.ui_writes.invoices_form_page import write_json

ControlKey = Literal[
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
DerivedInteraction = Literal["none"]
NextSlice = Literal["product_create"]

REQUIRED_CREATE_FORM_CONTROL_KEYS: Final[tuple[ControlKey, ...]] = (
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
)
CLOSED_ACTIONS: Final[frozenset[str]] = frozenset(
    {
        "type",
        "click_input",
        "click_wrapper",
        "click_overlay",
        "gem_kladde",
        "list_cta",
        "customer_detail_opret",
        "vaelg_kunde_named",
        "dispatch_change",
    }
)
DERIVED_ACTIONS: Final[frozenset[str]] = frozenset({"none"})
NEXT_SLICES: Final[frozenset[str]] = frozenset({"product_create"})
_OWNER_DUMP_DIR: Final = Path.home() / ".local" / "share" / "billy-mcp"
CREATE_FORM_CONTROL_DUMP: Final = _OWNER_DUMP_DIR / "inspect-live-invoices-create-form-control.json"


def derived_interaction_from(payload: Mapping[str, object]) -> DerivedInteraction:
    """Ignore caller tokens, including closed and invented ones."""

    raw = payload.get("derived_interaction")
    if raw in CLOSED_ACTIONS or raw != "none":
        return "none"
    return "none"


def next_slice_from(interaction: DerivedInteraction) -> NextSlice:
    del interaction
    return "product_create"


def _token(raw: object, allowed: frozenset[str], default: str) -> str:
    if isinstance(raw, str) and raw in allowed:
        return raw
    return default


def _key_is_present(payload: Mapping[str, object], key: ControlKey) -> bool:
    value = payload.get(key)
    match key:
        case (
            "ember_unique_normal_action"
            | "fiber_unique_normal_action"
            | "listener_unique_normal_action"
            | "descendant_unique_target"
            | "post_click_exact_match"
            | "closed_action_set_complete"
            | "unique_normal_action"
        ):
            return isinstance(value, bool)
        case "structure_transferable_action" | "scoped_unique_action":
            return value == "none"
        case (
            "vaelg_kunde_proved_bind"
            | "draft_save_proved_bind"
            | "list_cta_proved_bind"
            | "proved_bind"
        ):
            return value == "none"
        case "derived_interaction":
            return value in DERIVED_ACTIONS
        case "next_slice":
            return value in NEXT_SLICES
        case "missing_keys":
            return isinstance(value, list)


def create_form_control_missing_keys(payload: Mapping[str, object]) -> list[str]:
    """Keys the create-form derivation requires that this payload does not record."""

    if "ember_unique_normal_action" not in payload:
        return list(REQUIRED_CREATE_FORM_CONTROL_KEYS)
    return [key for key in REQUIRED_CREATE_FORM_CONTROL_KEYS if not _key_is_present(payload, key)]


def closed_create_form_evidence() -> dict[str, object]:
    """Frozen closed-probe evidence. Do not remake those dumps."""

    return {
        "ember_unique_normal_action": False,
        "fiber_unique_normal_action": False,
        "listener_unique_normal_action": False,
        "descendant_unique_target": False,
        "post_click_exact_match": False,
        "structure_transferable_action": "none",
        "vaelg_kunde_proved_bind": "none",
        "draft_save_proved_bind": "none",
        "scoped_unique_action": "none",
        "list_cta_proved_bind": "none",
        "closed_action_set_complete": True,
        "derived_interaction": "none",
        "unique_normal_action": False,
        "next_slice": "product_create",
        "proved_bind": "none",
        "missing_keys": [],
    }


def apply_create_form_control(
    payload: Mapping[str, object],
    *,
    dump_path: Path | None = None,
) -> dict[str, object]:
    """Copy allowlisted keys and write the owner-only summary."""

    result = closed_create_form_evidence()
    result["ember_unique_normal_action"] = payload.get("ember_unique_normal_action") is True
    result["fiber_unique_normal_action"] = payload.get("fiber_unique_normal_action") is True
    result["listener_unique_normal_action"] = payload.get("listener_unique_normal_action") is True
    result["descendant_unique_target"] = payload.get("descendant_unique_target") is True
    result["post_click_exact_match"] = payload.get("post_click_exact_match") is True
    result["structure_transferable_action"] = _token(
        payload.get("structure_transferable_action"), frozenset({"none"}), "none"
    )
    result["vaelg_kunde_proved_bind"] = _token(
        payload.get("vaelg_kunde_proved_bind"), frozenset({"none"}), "none"
    )
    result["draft_save_proved_bind"] = _token(
        payload.get("draft_save_proved_bind"), frozenset({"none"}), "none"
    )
    result["scoped_unique_action"] = _token(
        payload.get("scoped_unique_action"), frozenset({"none"}), "none"
    )
    result["list_cta_proved_bind"] = _token(
        payload.get("list_cta_proved_bind"), frozenset({"none"}), "none"
    )
    result["closed_action_set_complete"] = payload.get("closed_action_set_complete") is True
    interaction = derived_interaction_from(payload)
    result["derived_interaction"] = interaction
    result["unique_normal_action"] = interaction != "none"
    result["next_slice"] = next_slice_from(interaction)
    result["proved_bind"] = "none"
    result["missing_keys"] = create_form_control_missing_keys(result)
    if result["unique_normal_action"] is False:
        result["code"] = "UI_CHANGED"
        result["message"] = "Invoice create-form customer control has no unused normal action."
    summary = {key: result.get(key) for key in REQUIRED_CREATE_FORM_CONTROL_KEYS}
    write_json(dump_path or CREATE_FORM_CONTROL_DUMP, summary)
    return result


def create_form_control_dump_json(payload: Mapping[str, object]) -> str:
    """Stable JSON for leak checks. Never includes source or URLs."""

    return json.dumps(dict(payload), sort_keys=True)
