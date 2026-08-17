"""Vendor typeahead contract for draft bill writes.

Official bill belongs-to is contact/contactId. UI label is Leverandør.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Final

VENDOR_CHROME_DUMP: Final = (
    Path.home() / ".local" / "share" / "billy-mcp" / "inspect-live-bills-vendor.json"
)
VENDOR_WRAPPER_DUMP: Final = (
    Path.home() / ".local" / "share" / "billy-mcp" / "inspect-live-bills-vendor-wrapper.json"
)

VENDOR_INPUT_SELECTORS: Final[tuple[str, ...]] = ("input[name='vendor']",)
VENDOR_LABEL: Final = "Leverandør"
DROPDOWN_SELECTORS: Final[tuple[str, ...]] = (
    ".ds-dropdown-list",
    "[role='listbox']",
    "[role='option']",
)
CREATE_VENDOR_LABEL: Final = "Opret leverandør"


def is_create_vendor_option(label: str, unique_tag: str) -> bool:
    """True when a dropdown row creates a supplier for this tag."""

    text = label.strip()
    if text == CREATE_VENDOR_LABEL:
        return True
    return text == f'Opret "{unique_tag}"'


def create_vendor_labels(unique_tag: str) -> tuple[str, ...]:
    """Exact create-row texts to click, in preference order."""

    return (CREATE_VENDOR_LABEL, f'Opret "{unique_tag}"')


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
