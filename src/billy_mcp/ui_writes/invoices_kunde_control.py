"""Invoice Kunde loaded control-contract keys (452E0773).

Never stores source text, URLs, tokens, or customer values.
"""

from __future__ import annotations

import hashlib
import json
import re
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Final, Literal, cast
from urllib.parse import urlsplit

from billy_mcp.ui_writes.invoices_form_page import Page, write_json

ControlKey = Literal[
    "input_listener_types",
    "wrapper_listener_types",
    "input_listeners",
    "wrapper_listeners",
    "wrapper_data_attr_names",
    "wrapper_class_tokens",
    "binding_script",
    "named_next_action",
    "named_next_action_token",
]
EventTypeToken = Literal[
    "click",
    "focus",
    "blur",
    "input",
    "change",
    "keydown",
    "keyup",
    "mousedown",
    "mouseup",
    "pointerdown",
    "pointerup",
    "other",
]
BindingTokenClass = Literal[
    "name_eq_contact",
    "name_quoted_contact",
    "name_selector",
    "contact_id",
    "none",
]
ActionToken = Literal["click_open", "focus_open", "input_filter", "none"]

REQUIRED_KUNDE_CONTROL_KEYS: Final[tuple[ControlKey, ...]] = (
    "input_listener_types",
    "wrapper_listener_types",
    "input_listeners",
    "wrapper_listeners",
    "wrapper_data_attr_names",
    "wrapper_class_tokens",
    "binding_script",
    "named_next_action",
    "named_next_action_token",
)
EVENT_TYPE_TOKENS: Final[frozenset[str]] = frozenset(
    {
        "click",
        "focus",
        "blur",
        "input",
        "change",
        "keydown",
        "keyup",
        "mousedown",
        "mouseup",
        "pointerdown",
        "pointerup",
        "other",
    }
)
BINDING_TOKEN_CLASSES: Final[frozenset[str]] = frozenset(
    {
        "name_eq_contact",
        "name_quoted_contact",
        "name_selector",
        "contact_id",
        "none",
    }
)
ACTION_TOKENS: Final[frozenset[str]] = frozenset(
    {"click_open", "focus_open", "input_filter", "none"}
)
LISTENER_ROW_KEYS: Final[tuple[str, ...]] = (
    "type",
    "capture",
    "script_basename",
    "script_hash",
    "line",
    "column",
)
BINDING_ROW_KEYS: Final[tuple[str, ...]] = (
    "basename",
    "hash",
    "line",
    "column",
    "token_class",
)
LISTENER_CAP: Final = 16
_HEX_RUN: Final = re.compile(r"[0-9A-Fa-f]{8,}")
_OWN_MARKERS: Final[tuple[str, ...]] = ("__billyKundeEvents",)
KUNDE_CONTROL_DUMP: Final = (
    Path.home() / ".local" / "share" / "billy-mcp" / "inspect-live-invoices-kunde-control.json"
)
_WRAPPER_JS: Final = """() => {
  const el = document.querySelector("input[name='contact']");
  if (!el) {
    return null;
  }
  let node = el.parentElement;
  let smallest = null;
  while (node && node.tagName !== "BODY" && node.tagName !== "HTML") {
    if (node.querySelectorAll("input[name='contact']").length === 1) {
      smallest = node;
      break;
    }
    node = node.parentElement;
  }
  if (!smallest) {
    smallest = el.parentElement || el;
  }
  const names = [];
  if (smallest.attributes) {
    for (const attr of smallest.attributes) {
      if (attr && typeof attr.name === "string" && attr.name.indexOf("data-") === 0) {
        names.push(attr.name);
      }
    }
  }
  names.sort();
  const raw = smallest.className ? String(smallest.className) : "";
  const tokens = raw.split(/\\s+/).filter(Boolean);
  return {class_tokens: tokens, data_names: names};
}"""
_INPUT_OBJECT_JS: Final = "document.querySelector(\"input[name='contact']\")"
_WRAPPER_OBJECT_JS: Final = """(() => {
  const el = document.querySelector("input[name='contact']");
  if (!el) {
    return null;
  }
  let node = el.parentElement;
  let smallest = null;
  while (node && node.tagName !== "BODY" && node.tagName !== "HTML") {
    if (node.querySelectorAll("input[name='contact']").length === 1) {
      smallest = node;
      break;
    }
    node = node.parentElement;
  }
  return smallest || el.parentElement || el;
})()"""


def event_type_token(raw: str | None) -> EventTypeToken:
    """Allowlisted DOM event type. Unknown names become other."""

    compact = (raw or "").strip().casefold()
    if compact in EVENT_TYPE_TOKENS and compact != "other":
        return cast(EventTypeToken, compact)
    return "other"


def _is_script_url(url: str) -> bool:
    path = urlsplit(url).path.casefold()
    return path.endswith(".js") or path.endswith(".mjs")


def sanitize_script_basename(url: str | None) -> str:
    """Last path segment only. Query stripped. Long hex becomes :id."""

    raw = (url or "").strip()
    if raw == "":
        return "inline"
    if not _is_script_url(raw):
        return "inline"
    path = urlsplit(raw).path
    name = path.rsplit("/", 1)[-1] if path else ""
    if name == "":
        return "inline"
    return _HEX_RUN.sub(":id", name)


def script_hash_for(basename: str) -> str:
    """16-char hex of the sanitized basename. Never a URL."""

    digest = hashlib.sha256(basename.encode()).hexdigest()
    return digest[:16]


def binding_token_class(source: str | None) -> BindingTokenClass:
    """Classify already-loaded source. Never stores the source."""

    text = source or ""
    if "input[name=contact]" in text or "input[name='contact']" in text:
        return "name_selector"
    if 'name:"contact"' in text or "name:'contact'" in text or 'name: "contact"' in text:
        return "name_quoted_contact"
    if "name=contact" in text:
        return "name_eq_contact"
    if "contactId" in text:
        return "contact_id"
    return "none"


def _as_str_map(value: object) -> dict[str, object] | None:
    if not isinstance(value, dict):
        return None
    return dict(cast(dict[str, object], value))


def _string_list_is_present(value: object, allowed: frozenset[str] | None) -> bool:
    if not isinstance(value, list):
        return False
    for item in cast(list[object], value):
        if not isinstance(item, str):
            return False
        if allowed is not None and item not in allowed:
            return False
    return True


def _listener_rows_are_present(value: object) -> bool:
    if not isinstance(value, list):
        return False
    rows = cast(list[object], value)
    if len(rows) > LISTENER_CAP:
        return False
    for item in rows:
        row = _as_str_map(item)
        if row is None:
            return False
        if any(key not in row for key in LISTENER_ROW_KEYS):
            return False
        if row.get("type") not in EVENT_TYPE_TOKENS:
            return False
        if not isinstance(row.get("capture"), bool):
            return False
        basename = row.get("script_basename")
        digest = row.get("script_hash")
        line = row.get("line")
        column = row.get("column")
        if not isinstance(basename, str) or basename == "":
            return False
        if not isinstance(digest, str) or len(digest) != 16:
            return False
        if any(char not in "0123456789abcdef" for char in digest):
            return False
        if not isinstance(line, int) or line < 0:
            return False
        if not isinstance(column, int) or column < 0:
            return False
    return True


def _binding_is_present(value: object) -> bool:
    if value is None:
        return True
    row = _as_str_map(value)
    if row is None:
        return False
    if any(key not in row for key in BINDING_ROW_KEYS):
        return False
    if row.get("token_class") not in BINDING_TOKEN_CLASSES:
        return False
    basename = row.get("basename")
    digest = row.get("hash")
    line = row.get("line")
    column = row.get("column")
    if not isinstance(basename, str) or basename == "":
        return False
    if not isinstance(digest, str) or len(digest) != 16:
        return False
    if any(char not in "0123456789abcdef" for char in digest):
        return False
    if not isinstance(line, int) or line < 0:
        return False
    if not isinstance(column, int) or column < 0:
        return False
    return True


def _key_is_present(payload: Mapping[str, object], key: ControlKey) -> bool:
    match key:
        case "input_listener_types" | "wrapper_listener_types":
            return _string_list_is_present(payload.get(key), EVENT_TYPE_TOKENS)
        case "input_listeners" | "wrapper_listeners":
            return _listener_rows_are_present(payload.get(key))
        case "wrapper_data_attr_names" | "wrapper_class_tokens":
            return _string_list_is_present(payload.get(key), None)
        case "binding_script":
            return key in payload and _binding_is_present(payload.get(key))
        case "named_next_action":
            return isinstance(payload.get(key), bool)
        case "named_next_action_token":
            return payload.get(key) in ACTION_TOKENS


def kunde_control_missing_keys(payload: Mapping[str, object]) -> list[str]:
    """Keys 452E0773 requires that this dump does not record."""

    return [key for key in REQUIRED_KUNDE_CONTROL_KEYS if not _key_is_present(payload, key)]


def empty_kunde_control() -> dict[str, object]:
    """Structurally complete 452E0773 keys when CDP is unavailable."""

    return {
        "input_listener_types": [],
        "wrapper_listener_types": [],
        "input_listeners": [],
        "wrapper_listeners": [],
        "wrapper_data_attr_names": [],
        "wrapper_class_tokens": [],
        "binding_script": None,
        "named_next_action": False,
        "named_next_action_token": "none",
    }


def _listener_row(
    *,
    event_type: str,
    capture: bool,
    url: str | None,
    line: int,
    column: int,
) -> dict[str, object]:
    basename = sanitize_script_basename(url)
    return {
        "type": event_type_token(event_type),
        "capture": capture,
        "script_basename": basename,
        "script_hash": script_hash_for(basename),
        "line": max(line, 0),
        "column": max(column, 0),
    }


def _types_from_rows(rows: Sequence[Mapping[str, object]]) -> list[str]:
    seen: list[str] = []
    for row in rows:
        token = row.get("type")
        if isinstance(token, str) and token not in seen:
            seen.append(token)
    return seen


def named_next_action_from_control(payload: Mapping[str, object]) -> tuple[bool, ActionToken]:
    """True only when a listener type plus a non-none binding names one action."""

    binding = _as_str_map(payload.get("binding_script"))
    token_class = "none"
    if binding is not None:
        raw = binding.get("token_class")
        if isinstance(raw, str):
            token_class = raw
    if token_class == "none":
        return False, "none"
    types: list[str] = []
    for key in ("input_listener_types", "wrapper_listener_types"):
        raw_types = payload.get(key)
        if isinstance(raw_types, list):
            for item in cast(list[object], raw_types):
                if isinstance(item, str) and item not in types:
                    types.append(item)
    if "click" in types and token_class in {
        "name_eq_contact",
        "name_quoted_contact",
        "name_selector",
    }:
        return True, "click_open"
    if "focus" in types and token_class in {
        "name_eq_contact",
        "name_quoted_contact",
        "name_selector",
    }:
        return True, "focus_open"
    if "input" in types:
        return True, "input_filter"
    return False, "none"


def apply_kunde_control_dump(
    payload: Mapping[str, object],
    *,
    dump_path: Path | None = None,
) -> dict[str, object]:
    """Copy allowlisted keys and write the owner-only summary."""

    result = dict(payload)
    result.update(empty_kunde_control())
    for key in REQUIRED_KUNDE_CONTROL_KEYS:
        if key in payload:
            result[key] = payload[key]
    named, token = named_next_action_from_control(result)
    result["named_next_action"] = named
    result["named_next_action_token"] = token
    result["kunde_control_missing_keys"] = kunde_control_missing_keys(result)
    if not named:
        result["code"] = "UI_CHANGED"
        result["message"] = "Billy Kunde control contract names no next action."
    target = dump_path or KUNDE_CONTROL_DUMP
    dump_keys = (*REQUIRED_KUNDE_CONTROL_KEYS, "kunde_control_missing_keys")
    write_json(target, {key: result.get(key) for key in dump_keys})
    return result


def _is_own_listener(handler: object) -> bool:
    row = _as_str_map(handler)
    if row is None:
        return False
    description = row.get("description")
    if not isinstance(description, str):
        return False
    return any(marker in description for marker in _OWN_MARKERS)


def _script_url(scripts: Mapping[str, str], script_id: object) -> str | None:
    if not isinstance(script_id, str):
        return None
    return scripts.get(script_id)


async def _send(session: object, method: str, params: dict[str, object] | None = None) -> object:
    send = getattr(session, "send", None)
    if send is None:
        return None
    if params is None:
        return await send(method)
    return await send(method, params)


async def _object_id(session: object, expression: str) -> str | None:
    raw = await _send(
        session,
        "Runtime.evaluate",
        {"expression": expression, "returnByValue": False},
    )
    envelope = _as_str_map(raw)
    if envelope is None:
        return None
    result = _as_str_map(envelope.get("result"))
    if result is None:
        return None
    object_id = result.get("objectId")
    return object_id if isinstance(object_id, str) else None


async def _listeners_for(
    session: object,
    object_id: str,
    scripts: Mapping[str, str],
) -> list[dict[str, object]]:
    raw = await _send(session, "DOMDebugger.getEventListeners", {"objectId": object_id})
    envelope = _as_str_map(raw)
    if envelope is None:
        return []
    rows_raw = envelope.get("listeners")
    if not isinstance(rows_raw, list):
        return []
    rows: list[dict[str, object]] = []
    for item in cast(list[object], rows_raw):
        if len(rows) >= LISTENER_CAP:
            break
        listener = _as_str_map(item)
        if listener is None:
            continue
        if _is_own_listener(listener.get("handler")):
            continue
        line_raw = listener.get("lineNumber")
        column_raw = listener.get("columnNumber")
        line = line_raw if isinstance(line_raw, int) else 0
        column = column_raw if isinstance(column_raw, int) else 0
        event_type = listener.get("type")
        capture = listener.get("useCapture") is True
        url = _script_url(scripts, listener.get("scriptId"))
        rows.append(
            _listener_row(
                event_type=event_type if isinstance(event_type, str) else "other",
                capture=capture,
                url=url,
                line=line,
                column=column,
            )
        )
    return rows


async def _binding_from_scripts(
    session: object,
    scripts: Mapping[str, str],
    listener_script_ids: Sequence[str],
) -> dict[str, object] | None:
    ordered: list[tuple[str, str]] = []
    seen: set[str] = set()
    for script_id in listener_script_ids:
        if script_id in scripts and script_id not in seen:
            ordered.append((script_id, scripts[script_id]))
            seen.add(script_id)
    for script_id, url in scripts.items():
        if script_id in seen:
            continue
        host = urlsplit(url).hostname or ""
        if host not in {"mit.billy.dk", "api.billysbilling.com"}:
            continue
        if not _is_script_url(url):
            continue
        ordered.append((script_id, url))
    for script_id, url in ordered[:32]:
        raw = await _send(session, "Debugger.getScriptSource", {"scriptId": script_id})
        envelope = _as_str_map(raw)
        if envelope is None:
            continue
        source = envelope.get("scriptSource")
        if not isinstance(source, str):
            continue
        token = binding_token_class(source)
        if token == "none":
            continue
        basename = sanitize_script_basename(url)
        line = 0
        for index, text in enumerate(source.splitlines()):
            if binding_token_class(text) != "none":
                line = index
                break
        return {
            "basename": basename,
            "hash": script_hash_for(basename),
            "line": line,
            "column": 0,
            "token_class": token,
        }
    return None


async def inspect_kunde_control(page: Page) -> dict[str, object]:
    """Read-only CDP dump of the already-loaded contact field. Does not click."""

    payload = empty_kunde_control()
    wrapper_raw = await page.evaluate(_WRAPPER_JS)
    wrapper = _as_str_map(wrapper_raw)
    if wrapper is not None:
        class_tokens = wrapper.get("class_tokens")
        data_names = wrapper.get("data_names")
        if isinstance(class_tokens, list):
            payload["wrapper_class_tokens"] = [
                item for item in cast(list[object], class_tokens) if isinstance(item, str)
            ]
        if isinstance(data_names, list):
            payload["wrapper_data_attr_names"] = [
                item for item in cast(list[object], data_names) if isinstance(item, str)
            ]
    context = getattr(page, "context", None)
    factory = getattr(context, "new_cdp_session", None) if context is not None else None
    if factory is None:
        return apply_kunde_control_dump(payload)
    session = await factory(page)
    scripts: dict[str, str] = {}

    def _on_script(params: object) -> None:
        row = _as_str_map(params)
        if row is None:
            return
        script_id = row.get("scriptId")
        url = row.get("url")
        if isinstance(script_id, str) and isinstance(url, str):
            scripts[script_id] = url

    on = getattr(session, "on", None)
    if on is not None:
        on("Debugger.scriptParsed", _on_script)
    await _send(session, "Debugger.enable")
    await _send(session, "DOM.enable")
    await _send(session, "Runtime.enable")
    input_id = await _object_id(session, _INPUT_OBJECT_JS)
    wrapper_id = await _object_id(session, _WRAPPER_OBJECT_JS)
    listener_ids: list[str] = []
    if input_id is not None:
        input_rows = await _listeners_for(session, input_id, scripts)
        payload["input_listeners"] = input_rows
        payload["input_listener_types"] = _types_from_rows(input_rows)
    if wrapper_id is not None:
        wrapper_rows = await _listeners_for(session, wrapper_id, scripts)
        payload["wrapper_listeners"] = wrapper_rows
        payload["wrapper_listener_types"] = _types_from_rows(wrapper_rows)
    for key in ("input_listeners", "wrapper_listeners"):
        rows = payload.get(key)
        if not isinstance(rows, list):
            continue
        for item in cast(list[object], rows):
            row = _as_str_map(item)
            if row is None:
                continue
            basename = row.get("script_basename")
            if not isinstance(basename, str):
                continue
            for script_id, url in scripts.items():
                if sanitize_script_basename(url) == basename and script_id not in listener_ids:
                    listener_ids.append(script_id)
    payload["binding_script"] = await _binding_from_scripts(session, scripts, listener_ids)
    detach = getattr(session, "detach", None)
    if detach is not None:
        await detach()
    return apply_kunde_control_dump(payload)


def control_dump_json(payload: Mapping[str, object]) -> str:
    """Stable JSON for leak checks. Never includes source or URLs."""

    return json.dumps(dict(payload), sort_keys=True)
