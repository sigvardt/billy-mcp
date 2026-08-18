"""Read-only live capture of the Kunde React fiber."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Final, cast

from billy_mcp.ui_writes.invoices_form_page import Page
from billy_mcp.ui_writes.invoices_kunde_fiber import (
    KUNDE_FIBER_DUMP,
    apply_kunde_fiber_dump,
    as_str_map,
    empty_kunde_fiber,
    fiber_key_class,
    method_token,
    name_token,
    sanitize_prop_row,
    type_token,
    value_type_token,
)

_WALK_JS: Final = """() => {
  const input = document.querySelector("input[name='contact']");
  const wrapper = input && (input.closest(".pickerfield") || input.parentElement);
  const SELECTION = new Set([
    "contact", "contactId", "value", "selection", "selected", "selectedContact", "model"
  ]);
  const COLLECTION = new Set([
    "content", "contents", "options", "items", "results", "source", "sources"
  ]);
  const OPEN = new Set(["isOpen", "opened", "expanded", "isExpanded", "isOpened"]);
  const METHODS = new Set([
    "open", "close", "toggle", "expand", "collapse", "select", "setValue", "set",
    "choose", "filter", "search", "query", "onOpen", "onSelect", "onChange"
  ]);
  function keyClass(el) {
    if (!el) return "none";
    const names = Object.getOwnPropertyNames(el);
    for (const name of names) {
      if (name.startsWith("__reactFiber")) return "react_fiber";
      if (name.startsWith("__reactInternalInstance")) return "react_internal";
      if (name.startsWith("__reactProps")) return "react_props";
    }
    return "none";
  }
  function fiberOf(el) {
    if (!el) return null;
    const names = Object.getOwnPropertyNames(el);
    for (const name of names) {
      if (name.startsWith("__reactFiber") || name.startsWith("__reactInternalInstance")) {
        return el[name];
      }
    }
    return null;
  }
  function typeName(fiber) {
    if (!fiber) return "";
    const typed = fiber.type || fiber.elementType;
    if (!typed) return "";
    if (typeof typed === "string") return typed;
    if (typeof typed === "function" || typeof typed === "object") {
      return String(typed.displayName || typed.name || "");
    }
    return "";
  }
  function typeToken(name) {
    const lowered = String(name || "").replace(/-/g, "_").toLowerCase();
    if (!lowered) return "none";
    if (lowered.includes("picker")) return "picker";
    if (lowered.includes("combobox")) return "combobox";
    if (lowered.includes("autocomplete")) return "autocomplete";
    if (lowered.includes("select")) return "select";
    if (lowered.includes("contact")) return "contact";
    return "other";
  }
  function hostClass(node) {
    if (!node || node.nodeType !== 1) return "none";
    if (node === input) return "input";
    if (node === wrapper) return "wrapper";
    if (wrapper && wrapper.contains(node) && node !== input) {
      const box = wrapper.getBoundingClientRect();
      const nodeBox = node.getBoundingClientRect();
      const dx = Math.round(nodeBox.left - box.left);
      if (Math.abs(dx - 242) <= 4 && Math.round(nodeBox.width) === 40
          && Math.round(nodeBox.height) === 40) {
        return "overlay";
      }
    }
    return "other";
  }
  function valueType(value) {
    if (value === undefined) return "undefined";
    if (value === null) return "null";
    if (Array.isArray(value)) return "array";
    const typed = typeof value;
    if (typed === "boolean" || typed === "number" || typed === "string"
        || typed === "function" || typed === "object") {
      return typed;
    }
    return "other";
  }
  function nameToken(name) {
    if (SELECTION.has(name) || COLLECTION.has(name) || OPEN.has(name)) return name;
    return "other";
  }
  const propRows = [];
  const methods = [];
  let typeTok = "none";
  let host = "none";
  let otherHosts = 0;
  let lengthClass = "unknown";
  let openState = null;
  let openKey = "none";
  function harvest(obj) {
    if (!obj || typeof obj !== "object") return;
    for (const name of Object.keys(obj)) {
      const value = obj[name];
      const typed = valueType(value);
      if (METHODS.has(name) && typed === "function" && methods.indexOf(name) === -1) {
        methods.push(name);
      }
      const token = nameToken(name);
      if (token !== "other" && propRows.length < 16) {
        let found = false;
        for (const row of propRows) {
          if (row.name_token === token) found = true;
        }
        if (!found) propRows.push({name_token: token, value_type: typed});
      }
      if (COLLECTION.has(name) && Array.isArray(value)) {
        lengthClass = value.length === 0 ? "zero" : "nonzero";
      }
      if (OPEN.has(name) && typeof value === "boolean" && openState === null) {
        openKey = name;
        openState = value;
      }
    }
  }
  function visit(fiber, depth) {
    if (!fiber || depth > 8) return;
    if (typeTok === "none" || typeTok === "other") {
      const token = typeToken(typeName(fiber));
      if (token !== "none") typeTok = token;
    }
    const node = fiber.stateNode;
    if (node && node.nodeType === 1) {
      const classified = hostClass(node);
      if (host === "none") host = classified;
      if (classified === "other") otherHosts += 1;
    }
    harvest(fiber.memoizedProps);
    harvest(fiber.pendingProps);
    harvest(fiber.memoizedState);
    visit(fiber.return, depth + 1);
  }
  if (!input || !wrapper) {
    return {ok: false};
  }
  const inputFiber = fiberOf(input);
  const wrapperFiber = fiberOf(wrapper);
  visit(inputFiber, 0);
  if (wrapperFiber && wrapperFiber !== inputFiber) {
    visit(wrapperFiber, 0);
  }
  methods.sort();
  return {
    ok: true,
    fiber_key_class: keyClass(input),
    wrapper_fiber_key_class: keyClass(wrapper),
    type_token: typeTok,
    prop_rows: propRows,
    method_name_tokens: methods.slice(0, 16),
    candidate_length_class: lengthClass,
    open_state_key: openKey,
    open_state: openState,
    host_class: host,
    unique_fiber_host: otherHosts === 1
  };
}"""
_INPUT_OBJECT_JS: Final = """(() => {
  return document.querySelector("input[name='contact']");
})()"""
_WRAPPER_OBJECT_JS: Final = """(() => {
  const input = document.querySelector("input[name='contact']");
  return input ? (input.closest(".pickerfield") || input.parentElement) : null;
})()"""
_INPUT_FIBER_JS: Final = """(() => {
  const input = document.querySelector("input[name='contact']");
  if (!input) return null;
  const names = Object.getOwnPropertyNames(input);
  for (const name of names) {
    if (name.startsWith("__reactFiber") || name.startsWith("__reactInternalInstance")) {
      return input[name];
    }
  }
  return null;
})()"""
_BOOLEAN_NAMES: Final = frozenset({"isOpen", "opened", "expanded", "isExpanded", "isOpened"})
_COLLECTION_NAMES: Final = frozenset(
    {"content", "contents", "options", "items", "results", "source", "sources"}
)


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
    envelope = as_str_map(raw)
    if envelope is None:
        return None
    result = as_str_map(envelope.get("result"))
    if result is None:
        return None
    object_id = result.get("objectId")
    return object_id if isinstance(object_id, str) else None


def _descriptor_type(descriptor: Mapping[str, object]) -> str:
    value = as_str_map(descriptor.get("value"))
    if value is None:
        return "other"
    return value_type_token(value.get("type"), value.get("subtype"))


def _descriptor_length_class(descriptor: Mapping[str, object]) -> str:
    value = as_str_map(descriptor.get("value"))
    if value is None:
        return "unknown"
    preview = as_str_map(value.get("preview"))
    if preview is None:
        return "unknown"
    properties = preview.get("properties")
    if not isinstance(properties, list):
        return "unknown"
    return "zero" if len(cast(list[object], properties)) == 0 else "nonzero"


def _descriptor_bool(descriptor: Mapping[str, object]) -> bool | None:
    value = as_str_map(descriptor.get("value"))
    if value is None or value.get("type") != "boolean":
        return None
    raw = value.get("value")
    return raw if isinstance(raw, bool) else None


async def _properties(session: object, object_id: str, *, own: bool) -> list[dict[str, object]]:
    raw = await _send(
        session,
        "Runtime.getProperties",
        {
            "objectId": object_id,
            "ownProperties": own,
            "accessorPropertiesOnly": False,
            "generatePreview": True,
        },
    )
    envelope = as_str_map(raw)
    if envelope is None:
        return []
    rows_raw = envelope.get("result")
    if not isinstance(rows_raw, list):
        return []
    rows: list[dict[str, object]] = []
    for item in cast(list[object], rows_raw):
        descriptor = as_str_map(item)
        if descriptor is None:
            continue
        name = descriptor.get("name")
        if not isinstance(name, str) or name == "":
            continue
        rows.append(descriptor)
    return rows


def _own_fiber_key_class(descriptors: list[dict[str, object]]) -> str:
    for descriptor in descriptors:
        classified = fiber_key_class(descriptor.get("name"))
        if classified != "none":
            return classified
    return "none"


async def _collect_from_fiber(
    session: object, object_id: str
) -> tuple[list[dict[str, object]], list[str], str, bool | None, str]:
    property_rows: list[dict[str, object]] = []
    methods: list[str] = []
    length_class = "unknown"
    open_state: bool | None = None
    type_tok = "none"
    current: str | None = object_id
    hops = 0
    while current is not None and hops <= 8:
        hops += 1
        return_id: str | None = None
        for descriptor in await _properties(session, current, own=True):
            name = descriptor.get("name")
            if not isinstance(name, str):
                continue
            typed = _descriptor_type(descriptor)
            if name in {"type", "elementType"} and type_tok in {"none", "other"}:
                value = as_str_map(descriptor.get("value"))
                type_id = value.get("objectId") if value is not None else None
                if isinstance(type_id, str):
                    type_tok = await _type_token_from_object(session, type_id)
                elif typed == "string":
                    raw_value = value.get("value") if value is not None else None
                    type_tok = type_token(raw_value)
            if name in {"memoizedProps", "pendingProps", "memoizedState"} and typed == "object":
                value = as_str_map(descriptor.get("value"))
                props_id = value.get("objectId") if value is not None else None
                if isinstance(props_id, str):
                    extra_rows, extra_methods, extra_length, extra_open = await _collect_from_props(
                        session, props_id
                    )
                    for row in extra_rows:
                        if len(property_rows) >= 16:
                            break
                        if row not in property_rows:
                            property_rows.append(row)
                    for token in extra_methods:
                        if token not in methods and len(methods) < 16:
                            methods.append(token)
                    if extra_length != "unknown":
                        length_class = extra_length
                    if extra_open is not None and open_state is None:
                        open_state = extra_open
            if name == "return":
                value = as_str_map(descriptor.get("value"))
                candidate = value.get("objectId") if value is not None else None
                if isinstance(candidate, str):
                    return_id = candidate
        current = return_id
    methods.sort()
    return property_rows[:16], methods[:16], length_class, open_state, type_tok


async def _type_token_from_object(session: object, object_id: str) -> str:
    for descriptor in await _properties(session, object_id, own=True):
        name = descriptor.get("name")
        if name not in {"displayName", "name"}:
            continue
        value = as_str_map(descriptor.get("value"))
        if value is None or value.get("type") != "string":
            continue
        return type_token(value.get("value"))
    return "none"


async def _collect_from_props(
    session: object, object_id: str
) -> tuple[list[dict[str, object]], list[str], str, bool | None]:
    property_rows: list[dict[str, object]] = []
    methods: list[str] = []
    length_class = "unknown"
    open_state: bool | None = None
    for descriptor in await _properties(session, object_id, own=True):
        name = descriptor.get("name")
        if not isinstance(name, str) or name.startswith("_"):
            continue
        typed = _descriptor_type(descriptor)
        token = method_token(name)
        if typed == "function" and token is not None and token not in methods:
            methods.append(token)
        row = sanitize_prop_row({"name": name, "type": typed, "subtype": None})
        if row["name_token"] != "other" and row not in property_rows:
            property_rows.append(row)
        if name in _BOOLEAN_NAMES and open_state is None:
            open_state = _descriptor_bool(descriptor)
        if name_token(name) in _COLLECTION_NAMES and typed == "array":
            length_class = _descriptor_length_class(descriptor)
    return property_rows[:16], methods[:16], length_class, open_state


def _merge_class(current: object, incoming: str) -> str:
    if incoming != "none":
        return incoming
    return (
        incoming
        if current not in {"react_fiber", "react_internal", "react_props"}
        else str(current)
    )


async def inspect_kunde_fiber(page: Page) -> dict[str, object]:
    """Read-only fiber inspect. Does not click, type, or invoke methods."""

    payload = empty_kunde_fiber()
    walked = await page.evaluate(_WALK_JS)
    envelope = as_str_map(walked)
    if envelope is None or envelope.get("ok") is not True:
        return apply_kunde_fiber_dump(payload, dump_path=KUNDE_FIBER_DUMP)
    for key in (
        "fiber_key_class",
        "wrapper_fiber_key_class",
        "type_token",
        "prop_rows",
        "method_name_tokens",
        "candidate_length_class",
        "open_state_key",
        "open_state",
        "host_class",
        "unique_fiber_host",
    ):
        if key in envelope:
            payload[key] = envelope[key]
    context = getattr(page, "context", None)
    factory = getattr(context, "new_cdp_session", None) if context is not None else None
    if factory is None:
        return apply_kunde_fiber_dump(payload, dump_path=KUNDE_FIBER_DUMP)
    session = await factory(page)
    await _send(session, "Runtime.enable")
    input_id = await _object_id(session, _INPUT_OBJECT_JS)
    wrapper_id = await _object_id(session, _WRAPPER_OBJECT_JS)
    if input_id is not None:
        classified = _own_fiber_key_class(await _properties(session, input_id, own=True))
        payload["fiber_key_class"] = _merge_class(payload.get("fiber_key_class"), classified)
    if wrapper_id is not None:
        classified = _own_fiber_key_class(await _properties(session, wrapper_id, own=True))
        payload["wrapper_fiber_key_class"] = _merge_class(
            payload.get("wrapper_fiber_key_class"), classified
        )
    fiber_id = await _object_id(session, _INPUT_FIBER_JS)
    if fiber_id is not None:
        rows, methods, length_class, open_state, type_tok = await _collect_from_fiber(
            session, fiber_id
        )
        existing_rows = payload.get("prop_rows")
        merged_rows: list[object] = []
        if isinstance(existing_rows, list):
            merged_rows = list(cast(list[object], existing_rows))
        for row in rows:
            if row not in merged_rows and len(merged_rows) < 16:
                merged_rows.append(row)
        payload["prop_rows"] = merged_rows
        existing_methods = payload.get("method_name_tokens")
        merged_methods = (
            list(cast(list[object], existing_methods)) if isinstance(existing_methods, list) else []
        )
        for token in methods:
            if token not in merged_methods and len(merged_methods) < 16:
                merged_methods.append(token)
        payload["method_name_tokens"] = merged_methods
        if length_class != "unknown":
            payload["candidate_length_class"] = length_class
        if open_state is not None and payload.get("open_state") is None:
            payload["open_state"] = open_state
        if type_tok != "none" and payload.get("type_token") in {"none", "other"}:
            payload["type_token"] = type_tok
    detach = getattr(session, "detach", None)
    if detach is not None:
        await detach()
    return apply_kunde_fiber_dump(payload, dump_path=KUNDE_FIBER_DUMP)
