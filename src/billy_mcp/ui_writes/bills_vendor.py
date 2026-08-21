"""Vendor typeahead contract for draft bill writes.

Official bill belongs-to is contact/contactId. UI label is Leverandør.
"""

from __future__ import annotations

import json
import os
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Final

VENDOR_CHROME_DUMP: Final = (
    Path.home() / ".local" / "share" / "billy-mcp" / "inspect-live-bills-vendor.json"
)
VENDOR_WRAPPER_DUMP: Final = (
    Path.home() / ".local" / "share" / "billy-mcp" / "inspect-live-bills-vendor-wrapper.json"
)
DATE_CHROME_DUMP: Final = (
    Path.home() / ".local" / "share" / "billy-mcp" / "inspect-live-bills-date.json"
)

VENDOR_INPUT_SELECTORS: Final[tuple[str, ...]] = ("input[name='vendor']",)
VENDOR_LABEL: Final = "Leverandør"
DROPDOWN_SELECTORS: Final[tuple[str, ...]] = (
    ".ds-dropdown-list",
    "[role='listbox']",
    "[role='option']",
)
CREATE_VENDOR_LABEL: Final = "Opret leverandør"
PORTAL_FOOTER_WRAPPER: Final = "[class*='DropdownFooterWrapper']"
VENDOR_SEARCH_TOGGLE: Final = "[data-testid='search']"
VENDOR_CLEAR: Final = "[data-testid='circleX']"
LEFTOVER_PORTAL_DUMP: Final = (
    Path.home() / ".local" / "share" / "billy-mcp" / "inspect-live-bills-leftover.json"
)


def is_create_vendor_option(label: str, unique_tag: str) -> bool:
    """True when a dropdown row creates a supplier for this tag."""

    text = label.strip()
    if text == CREATE_VENDOR_LABEL:
        return True
    return text == f'Opret "{unique_tag}"'


def create_vendor_labels(unique_tag: str) -> tuple[str, ...]:
    """Exact create-row texts to click, in preference order."""

    return (CREATE_VENDOR_LABEL, portal_create_footer_label(unique_tag))


def portal_create_footer_label(unique_tag: str) -> str:
    """Exact empty-list footer text observed on the vendor typeahead."""

    return f'Opret "{unique_tag}"'


def portal_list_item_flags(text: str, unique_tag: str) -> dict[str, bool]:
    """Non-PII flags for one portal list. Never stores the tag."""

    compact = " ".join(text.split())
    footer = portal_create_footer_label(unique_tag)
    return {
        "has_opret": "Opret" in text,
        "has_tag": unique_tag in text,
        "has_empty": "Ingen resultater" in text,
        "has_create_footer": footer in text,
        "visible": True,
        "short": len(compact) < 200,
    }


def pick_portal_create_index(items: Sequence[Mapping[str, object]]) -> int | None:
    """Index of the empty vendor list with a create footer. Skip huge ancestors."""

    for index, item in enumerate(items):
        if item.get("has_empty") is not True:
            continue
        if item.get("has_create_footer") is not True:
            continue
        if item.get("short") is False:
            continue
        if item.get("visible") is False:
            continue
        return index
    return None


def pick_portal_existing_option_index(items: Sequence[Mapping[str, object]]) -> int | None:
    """Index of a visible existing supplier option. Create footer is not this bind."""

    for index, item in enumerate(items):
        if item.get("has_tag") is not True:
            continue
        if item.get("visible") is False:
            continue
        if item.get("short") is False:
            continue
        if item.get("has_empty") is True:
            continue
        return index
    return None


def vendor_option_click_targets(unique_tag: str) -> tuple[tuple[str, str], ...]:
    """Dropdown-scoped (root, text) pairs. Never a page-wide tag click."""

    texts = (unique_tag, *create_vendor_labels(unique_tag))
    return tuple((root, text) for root in DROPDOWN_SELECTORS for text in texts)


def dropdown_create_row_matches(label: str, unique_tag: str) -> bool:
    """True when a dropdown row creates this tag. Page-wide text is not a row."""

    text = " ".join(label.split())
    if unique_tag not in text:
        return False
    return text.startswith("Opret") or is_create_vendor_option(text, unique_tag)


def wait_all_plus_tab_is_close() -> bool:
    """A wait-all-visible plus Tab is never a leftover portal close."""

    return False


def generic_portal_sweep_is_close() -> bool:
    """Closing every ds-moved-with-portal node is never a leftover close."""

    return False


def circle_x_is_close() -> bool:
    """The vendor clear control unbinds the supplier. It is not a close."""

    return False


def escape_is_close() -> bool:
    """Escape is forbidden as a leftover portal close."""

    return False


def leftover_portal_kind(
    *,
    visible: bool,
    has_opret: bool,
    has_empty: bool,
    has_modal_heading: bool,
) -> str | None:
    """Classify the one leftover Leverandør portal. None when nothing remains."""

    if has_modal_heading:
        return "create_vendor_modal"
    if visible:
        return "vendor_list"
    return None


def leftover_close_action(kind: str | None) -> str | None:
    """The one allowed close for an observed leftover. Nothing else."""

    if kind == "vendor_list":
        return "search_toggle"
    if kind == "create_vendor_modal":
        return "modal_gem"
    return None


def leftover_close_after_existing_option() -> None:
    """Selecting an existing supplier completes the typeahead. No leftover close."""

    return None


def leftover_follow_up_is_close() -> bool:
    """A second close after the observed leftover is never allowed."""

    return False


def leftover_role(kind: str | None) -> str | None:
    """ARIA-ish role of the one leftover. Never a tag."""

    if kind == "vendor_list":
        return "listbox"
    if kind == "create_vendor_modal":
        return "dialog"
    return None


def leftover_heading(*, kind: str | None, has_empty: bool) -> str | None:
    """Exact chrome heading of the leftover. Never a unique tag."""

    if kind == "create_vendor_modal":
        return CREATE_VENDOR_LABEL
    if kind == "vendor_list" and has_empty:
        return "Ingen resultater"
    return None


def leftover_owning_control(kind: str | None) -> str | None:
    """Owning close control of the leftover. circleX is not a close."""

    if kind == "vendor_list":
        return "search"
    if kind == "create_vendor_modal":
        return "modal_gem"
    return None


def leftover_inspect_record(
    *,
    kind: str | None,
    visible_count: int,
    has_opret: bool,
    has_empty: bool,
    search_trigger: bool,
    clear_trigger: bool,
) -> dict[str, object]:
    """Non-PII leftover dump payload. Never stores a tag."""

    return {
        "kind": kind,
        "role": leftover_role(kind),
        "heading": leftover_heading(kind=kind, has_empty=has_empty),
        "owning_control": leftover_owning_control(kind),
        "visible_count": visible_count,
        "has_opret": has_opret,
        "has_empty": has_empty,
        "search_trigger": search_trigger,
        "clear_trigger": clear_trigger,
        "close": leftover_close_action(kind),
    }


def dump_leftover_portal(
    artifact: dict[str, object],
    *,
    destination: Path | None = None,
) -> None:
    """Write one non-PII leftover portal observation outside git."""

    path = destination if destination is not None else LEFTOVER_PORTAL_DUMP
    current = os.environ.get("PYTEST_CURRENT_TEST", "")
    if destination is None and current and "/live/" not in current.replace("\\", "/"):
        return
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(artifact, indent=2) + "\n", encoding="utf-8")
    except OSError:
        return


def leftover_footer_means_bound(*, leftover_count: int | None, count_failed: bool) -> bool:
    """True only when the create footer is gone. A count error is not a bind."""

    if count_failed:
        return False
    return leftover_count == 0


def vendor_bind_is_complete(*, option_clicked: bool, enter_selected: bool) -> bool:
    """True only when a dropdown row or Enter selection bound the vendor."""

    return option_clicked or enter_selected


def pre_submit_dump_path(
    draft_cta: str,
    *,
    create_path: Path,
    update_path: Path,
) -> Path:
    """Keep the create dump off the update/unit-test overwrite path."""

    if draft_cta == "Gem som kladde":
        return create_path
    return update_path


def dump_scoped_vendor_wrapper(
    artifact: dict[str, object],
    *,
    destination: Path | None = None,
) -> None:
    """Write one non-PII Leverandør wrapper observation outside git."""

    path = destination if destination is not None else VENDOR_WRAPPER_DUMP
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(artifact, indent=2) + "\n", encoding="utf-8")
    except OSError:
        return


def dump_date_chrome(
    artifact: dict[str, object],
    *,
    destination: Path | None = None,
) -> None:
    """Write one non-PII billDate observation outside git."""

    path = destination if destination is not None else DATE_CHROME_DUMP
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(artifact, indent=2) + "\n", encoding="utf-8")
    except OSError:
        return


def dump_vendor_chrome(
    *,
    names: list[str],
    chosen: str | None,
    destination: Path | None = None,
) -> None:
    """Write non-PII vendor input names outside git."""

    path = destination if destination is not None else VENDOR_CHROME_DUMP
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps({"input_names": names, "chosen": chosen}, indent=2) + "\n",
            encoding="utf-8",
        )
    except OSError:
        return
