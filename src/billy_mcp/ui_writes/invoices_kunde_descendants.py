"""Invoice Kunde pickerfield descendant keys (E87B6AEF).

Never stores raw names, raw text, URLs, source, or customer values.
"""

from __future__ import annotations

import json
from collections.abc import Mapping
from pathlib import Path
from typing import Final, Literal, cast

from billy_mcp.ui_writes.invoices_form_page import write_json
from billy_mcp.ui_writes.invoices_kunde_descendant_rows import (
    DESCENDANT_CAP,
    GUARD_TOKENS,
    TARGET_CATEGORIES,
    as_str_map,
    classify_handler_source,
    row_is_present,
    row_target_category,
    sanitize_descendant,
    unique_target_from_descendants,
    unused_descendants,
    wrapper_handler_guard_from_metadata,
)

DescendantKey = Literal[
    "wrapper_tag",
    "visible_descendant_count",
    "descendants",
    "unique_target",
    "unique_target_category",
    "wrapper_handler_guard",
    "kunde_descendant_missing_keys",
]

REQUIRED_KUNDE_DESCENDANT_KEYS: Final[tuple[DescendantKey, ...]] = (
    "wrapper_tag",
    "visible_descendant_count",
    "descendants",
    "unique_target",
    "unique_target_category",
    "wrapper_handler_guard",
    "kunde_descendant_missing_keys",
)
KUNDE_DESCENDANT_DUMP: Final = (
    Path.home() / ".local" / "share" / "billy-mcp" / "inspect-live-invoices-kunde-descendants.json"
)


def _key_is_present(payload: Mapping[str, object], key: DescendantKey) -> bool:
    value = payload.get(key)
    match key:
        case "wrapper_tag":
            return value in {"DIV", "other"}
        case "visible_descendant_count":
            return isinstance(value, int) and value >= 0
        case "descendants":
            return isinstance(value, list) and all(
                row_is_present(item) for item in cast(list[object], value)
            )
        case "unique_target":
            return isinstance(value, bool)
        case "unique_target_category":
            return value in TARGET_CATEGORIES
        case "wrapper_handler_guard":
            return value in GUARD_TOKENS
        case "kunde_descendant_missing_keys":
            return isinstance(value, list)


def kunde_descendant_missing_keys(payload: Mapping[str, object]) -> list[str]:
    """Keys E87B6AEF requires that this dump does not record."""

    return [key for key in REQUIRED_KUNDE_DESCENDANT_KEYS if not _key_is_present(payload, key)]


def empty_kunde_descendants() -> dict[str, object]:
    """Structurally complete E87B6AEF keys before a live map."""

    return {
        "wrapper_tag": "DIV",
        "visible_descendant_count": 0,
        "descendants": [],
        "unique_target": False,
        "unique_target_category": "none",
        "wrapper_handler_guard": "none",
        "kunde_descendant_missing_keys": [],
    }


def descendant_dump_is_delivered(path: Path | None = None) -> bool:
    """True when the owner dump already recorded the read-only map."""

    target = path or KUNDE_DESCENDANT_DUMP
    if not target.is_file():
        return False
    try:
        raw = json.loads(target.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return False
    payload = as_str_map(raw)
    return payload is not None and kunde_descendant_missing_keys(payload) == []


def apply_kunde_descendant_dump(
    payload: Mapping[str, object],
    *,
    dump_path: Path | None = None,
) -> dict[str, object]:
    """Copy allowlisted keys and write the owner-only summary."""

    result = empty_kunde_descendants()
    for key in REQUIRED_KUNDE_DESCENDANT_KEYS:
        if key in payload and key != "kunde_descendant_missing_keys":
            result[key] = payload[key]
    rows_raw = result.get("descendants")
    rows: list[dict[str, object]] = []
    if isinstance(rows_raw, list):
        for item in cast(list[object], rows_raw):
            if len(rows) >= DESCENDANT_CAP:
                break
            row = as_str_map(item)
            if row is None:
                continue
            rows.append(row)
    result["descendants"] = rows
    result["visible_descendant_count"] = len(rows)
    unique = unique_target_from_descendants(result)
    result["unique_target"] = unique
    unused = unused_descendants(rows)
    result["unique_target_category"] = row_target_category(unused[0]) if unique else "none"
    result["wrapper_handler_guard"] = wrapper_handler_guard_from_metadata(result)
    result["kunde_descendant_missing_keys"] = kunde_descendant_missing_keys(result)
    if not unique:
        result["code"] = "UI_CHANGED"
        result["message"] = "Billy Kunde descendant map has no unused unique target."
    summary = {key: result.get(key) for key in REQUIRED_KUNDE_DESCENDANT_KEYS}
    write_json(dump_path or KUNDE_DESCENDANT_DUMP, summary)
    return result


def descendant_dump_json(payload: Mapping[str, object]) -> str:
    """Stable JSON for leak checks. Never includes source or URLs."""

    return json.dumps(dict(payload), sort_keys=True)


__all__ = [
    "KUNDE_DESCENDANT_DUMP",
    "REQUIRED_KUNDE_DESCENDANT_KEYS",
    "apply_kunde_descendant_dump",
    "classify_handler_source",
    "descendant_dump_is_delivered",
    "descendant_dump_json",
    "empty_kunde_descendants",
    "kunde_descendant_missing_keys",
    "sanitize_descendant",
    "unique_target_from_descendants",
    "wrapper_handler_guard_from_metadata",
]
