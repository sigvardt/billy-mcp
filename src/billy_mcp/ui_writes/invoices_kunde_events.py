"""Invoice Kunde phase-scoped event and pageerror keys (4A5CD1E7)."""

from __future__ import annotations

import hashlib
import re
from collections.abc import Mapping
from typing import Final, Literal, cast

EventKey = Literal[
    "event_counts",
    "console_delta",
    "errors",
    "pageerror_unrelated_at_rest",
]
EventPhase = Literal["at_rest", "after_click", "after_type"]

REQUIRED_KUNDE_EVENT_KEYS: Final[tuple[EventKey, ...]] = (
    "event_counts",
    "console_delta",
    "errors",
    "pageerror_unrelated_at_rest",
)
EVENT_COUNT_KEYS: Final[tuple[str, ...]] = (
    "focus",
    "input",
    "change",
    "keydown",
    "keyup",
)
CONSOLE_DELTA_KEYS: Final[tuple[str, ...]] = ("script", "pageerror", "other")
ERROR_ROW_KEYS: Final[tuple[str, ...]] = (
    "error_class",
    "fingerprint",
    "phase",
    "source_class",
)
ERROR_CLASSES: Final[frozenset[str]] = frozenset(
    {
        "TypeError",
        "ReferenceError",
        "SyntaxError",
        "RangeError",
        "URIError",
        "EvalError",
        "EmberError",
        "other",
    }
)
SOURCE_CLASSES: Final[frozenset[str]] = frozenset({"inline", "same_origin", "worker", "unknown"})
EVENT_PHASES: Final[frozenset[str]] = frozenset({"at_rest", "after_click", "after_type"})
_HEX_RE: Final = re.compile(r"[0-9A-Fa-f]{8,}")
_URL_RE: Final = re.compile(r"https?://\S+")
_QUOTED_RE: Final = re.compile(r"""(['"])(?:\\.|(?!\1).)*\1""")
_SAME_ORIGIN_HOSTS: Final[frozenset[str]] = frozenset(
    {"mit.billy.dk", "api.billysbilling.com", "download.billy.dk"}
)
EVENT_ERROR_CAP: Final = 8
KUNDE_EVENT_INIT_SCRIPT: Final = """
(() => {
  if (window.__billyKundeEvents) {
    return;
  }
  window.__billyKundeEvents = {
    focus: 0,
    input: 0,
    change: 0,
    keydown: 0,
    keyup: 0
  };
  const bump = (type, ev) => {
    const target = ev && ev.target;
    if (!target || typeof target.getAttribute !== "function") {
      return;
    }
    if (target.getAttribute("name") !== "contact") {
      return;
    }
    window.__billyKundeEvents[type] += 1;
  };
  for (const type of ["focus", "input", "change", "keydown", "keyup"]) {
    document.addEventListener(type, (ev) => bump(type, ev), true);
  }
})();
"""


def _as_str_map(value: object) -> dict[str, object] | None:
    if not isinstance(value, dict):
        return None
    return dict(cast(dict[str, object], value))


def _mapping_has_keys(value: object, keys: tuple[str, ...]) -> bool:
    parsed = _as_str_map(value)
    if parsed is None:
        return False
    return all(key in parsed for key in keys)


def error_class_token(raw: str | None) -> str:
    """Allowlisted constructor name. Unknown names become other."""

    name = (raw or "").strip()
    if name in ERROR_CLASSES and name != "other":
        return name
    return "other"


def source_class_token(raw: str | None) -> str:
    """Allowlisted source class. Never stores the URL."""

    value = (raw or "").strip()
    if value == "" or value.startswith(("inline", "about:", "blob:")):
        return "inline"
    if "worker" in value.casefold():
        return "worker"
    host = value
    if "://" in value:
        host = value.split("://", 1)[1].split("/", 1)[0].split("@")[-1].split(":")[0]
    if host.casefold() in _SAME_ORIGIN_HOSTS:
        return "same_origin"
    return "unknown"


def scrub_message_shape(raw: str | None) -> str:
    """Stable shape for hashing. Never write this string into git dumps."""

    text = raw or ""
    text = _URL_RE.sub("URL", text)
    text = _QUOTED_RE.sub("STR", text)
    text = _HEX_RE.sub("HEX", text)
    return " ".join(text.split())


def fingerprint_for(error_class: str, source_class: str, message_shape: str) -> str:
    """16-char hex of class + source + scrubbed shape. Never the raw message."""

    classified = error_class_token(error_class)
    source = source_class_token(source_class)
    digest = hashlib.sha256(f"{classified}|{source}|{message_shape}".encode()).hexdigest()
    return digest[:16]


def empty_event_counts() -> dict[str, int]:
    """Zeroed phase-scoped field-event counts."""

    return {key: 0 for key in EVENT_COUNT_KEYS}


def empty_console_delta() -> dict[str, int]:
    """Zeroed phase-scoped console counts."""

    return {key: 0 for key in CONSOLE_DELTA_KEYS}


def empty_kunde_event() -> dict[str, object]:
    """Structurally complete 4A5CD1E7 keys when no listener has run."""

    return {
        "event_counts": empty_event_counts(),
        "console_delta": empty_console_delta(),
        "errors": [],
        "pageerror_unrelated_at_rest": False,
    }


def _event_counts_are_present(value: object) -> bool:
    parsed = _as_str_map(value)
    if parsed is None or not _mapping_has_keys(value, EVENT_COUNT_KEYS):
        return False
    return all(isinstance(parsed[key], int) for key in EVENT_COUNT_KEYS)


def _console_delta_is_present(value: object) -> bool:
    parsed = _as_str_map(value)
    if parsed is None or not _mapping_has_keys(value, CONSOLE_DELTA_KEYS):
        return False
    return all(isinstance(parsed[key], int) for key in CONSOLE_DELTA_KEYS)


def _errors_are_present(value: object) -> bool:
    if not isinstance(value, list):
        return False
    for item in cast(list[object], value):
        row = _as_str_map(item)
        if row is None or not _mapping_has_keys(row, ERROR_ROW_KEYS):
            return False
        if row.get("error_class") not in ERROR_CLASSES:
            return False
        if row.get("source_class") not in SOURCE_CLASSES:
            return False
        if row.get("phase") not in EVENT_PHASES:
            return False
        fingerprint = row.get("fingerprint")
        if not isinstance(fingerprint, str) or len(fingerprint) != 16:
            return False
        if any(char not in "0123456789abcdef" for char in fingerprint):
            return False
    return True


def _key_is_present(payload: Mapping[str, object], key: EventKey) -> bool:
    match key:
        case "event_counts":
            return _event_counts_are_present(payload.get(key))
        case "console_delta":
            return _console_delta_is_present(payload.get(key))
        case "errors":
            return _errors_are_present(payload.get(key))
        case "pageerror_unrelated_at_rest":
            return isinstance(payload.get(key), bool)


def kunde_event_missing_keys(payload: Mapping[str, object]) -> list[str]:
    """Keys 4A5CD1E7 requires that this phase dump does not record."""

    return [key for key in REQUIRED_KUNDE_EVENT_KEYS if not _key_is_present(payload, key)]


def pageerror_unrelated_at_rest(*, rest_pageerror: int, click_delta: int, type_delta: int) -> bool:
    """True when the rest pageerror stays and later phases add none."""

    return rest_pageerror >= 1 and click_delta == 0 and type_delta == 0


def event_sequence_is_wrong(counts: Mapping[str, object]) -> bool:
    """True when tagged type produced no keydown and no input."""

    return counts.get("keydown") == 0 and counts.get("input") == 0


def mapping_int(raw: object, key: str) -> int:
    """Read an int field from a dump mapping. Missing or wrong types are 0."""

    parsed = _as_str_map(raw)
    if parsed is None or key not in parsed:
        return 0
    value = parsed[key]
    return value if isinstance(value, int) else 0


def requests_have_contacts(raw: object) -> bool:
    """True when any redacted request row is the contacts path class."""

    if not isinstance(raw, list):
        return False
    for item in cast(list[object], raw):
        parsed = _as_str_map(item)
        if parsed is not None and parsed.get("path_class") == "contacts":
            return True
    return False


def as_str_object_map(raw: object) -> dict[str, object] | None:
    """Copy a mapping with string keys. Other shapes are None."""

    parsed = _as_str_map(raw)
    return None if parsed is None else dict(parsed)


def event_names_change_gap(counts: Mapping[str, object], *, contacts: bool) -> bool:
    """True when input fired, change did not, and no contacts request."""

    input_count = counts.get("input")
    return (
        isinstance(input_count, int)
        and input_count > 0
        and counts.get("change") == 0
        and not contacts
    )


def next_event_phase(phase: str) -> EventPhase:
    """Advance the recording phase after a snapshot."""

    match phase:
        case "at_rest":
            return "after_click"
        case "after_click":
            return "after_type"
        case "after_type":
            return "after_type"
        case _:
            return "after_type"


def parse_event_counts(raw: object) -> dict[str, int]:
    """Parse window event totals. Unknown shapes become zeros."""

    parsed = _as_str_map(raw)
    counts = empty_event_counts()
    if parsed is None:
        return counts
    for key in EVENT_COUNT_KEYS:
        value = parsed.get(key)
        counts[key] = value if isinstance(value, int) and value >= 0 else 0
    return counts


def count_deltas(current: Mapping[str, int], previous: Mapping[str, int]) -> dict[str, int]:
    """Non-negative per-key delta. Used for phase-scoped counts."""

    return {key: max(0, int(current.get(key, 0)) - int(previous.get(key, 0))) for key in current}


def event_error_row(
    *,
    name: str | None,
    source: str | None,
    message: str | None,
    phase: str,
) -> dict[str, str]:
    """Allowlisted error row. Raw message is hashed, never stored."""

    classified = error_class_token(name)
    source_class = source_class_token(source)
    recorded_phase = phase if phase in EVENT_PHASES else "at_rest"
    return {
        "error_class": classified,
        "fingerprint": fingerprint_for(classified, source_class, scrub_message_shape(message)),
        "phase": recorded_phase,
        "source_class": source_class,
    }


def event_name_of(event: object) -> str:
    """Constructor name from a Playwright console or pageerror event."""

    name = getattr(event, "name", None)
    if isinstance(name, str) and name.strip():
        return name
    return type(event).__name__


def event_message_of(event: object) -> str:
    """Message text for hashing only. Never persist the return value."""

    for attr in ("text", "message"):
        value = getattr(event, attr, None)
        if isinstance(value, str) and value:
            return value
    return str(event)


def event_source_of(event: object) -> str:
    """URL-like source for classification. Never persisted."""

    location = getattr(event, "location", None)
    parsed_location = _as_str_map(location)
    if parsed_location is not None:
        url = parsed_location.get("url")
        if isinstance(url, str) and url:
            return url
    stack = getattr(event, "stack", None)
    if isinstance(stack, str) and stack:
        return stack.splitlines()[0]
    return ""
