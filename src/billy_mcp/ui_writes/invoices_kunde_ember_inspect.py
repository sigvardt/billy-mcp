"""Read-only live capture of the Kunde Ember view (31B0C7A6)."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Final, cast

from billy_mcp.ui_writes.invoices_form_page import Page
from billy_mcp.ui_writes.invoices_kunde_ember import (
    KUNDE_EMBER_DUMP,
    apply_kunde_ember_dump,
    as_str_map,
    constructor_token,
    empty_kunde_ember,
    method_token,
    name_token,
    sanitize_property_row,
    value_type_token,
)

_FLAGS_JS: Final = """() => {
  const input = document.querySelector("input[name='contact']");
  if (!input) {
    return {ok: false};
  }
  const wrapper = input.closest(".pickerfield") || input.parentElement;
  if (!wrapper) {
    return {ok: false};
  }
  const ember = window.Ember;
  const emberPresent = !!(ember && typeof ember === "object");
  const views = emberPresent && ember.View && ember.View.views;
  const registryPresent = !!(views && typeof views === "object");
  const rawId = typeof wrapper.id === "string" ? wrapper.id : "";
  let idClass = "none";
  if (rawId) {
    idClass = /^ember\\d+$/.test(rawId) ? "ember_digit" : "other";
  }
  const className = wrapper.className ? String(wrapper.className) : "";
  return {
    ok: true,
    ember_global_present: emberPresent,
    view_registry_present: registryPresent,
    wrapper_ember_id_class: idClass,
    wrapper_class: className
  };
}"""
_VIEW_OBJECT_JS: Final = """(() => {
  const input = document.querySelector("input[name='contact']");
  const wrapper = input && (input.closest(".pickerfield") || input.parentElement);
  const ember = window.Ember;
  if (!wrapper || !ember || !ember.View || !ember.View.views) {
    return null;
  }
  const rawId = typeof wrapper.id === "string" ? wrapper.id : "";
  if (!/^ember\\d+$/.test(rawId)) {
    return null;
  }
  return ember.View.views[rawId] || null;
})()"""
_WRAPPER_OBJECT_JS: Final = """(() => {
  const el = document.querySelector("input[name='contact']");
  return el ? (el.closest(".pickerfield") || el.parentElement) : null;
})()"""
_BOOLEAN_NAMES: Final = frozenset({"isOpen", "opened", "expanded", "isExpanded", "isOpened"})


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
    subtype = value.get("subtype")
    raw_type = value.get("type")
    return value_type_token(raw_type, subtype)


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
        if not isinstance(name, str) or name == "" or name.startswith("_"):
            continue
        rows.append(descriptor)
    return rows


async def _collect_from_object(
    session: object, object_id: str
) -> tuple[list[dict[str, object]], list[str], str, bool | None]:
    property_rows: list[dict[str, object]] = []
    methods: list[str] = []
    length_class = "unknown"
    open_state: bool | None = None
    descriptors = await _properties(session, object_id, own=True)
    proto_id = None
    for descriptor in descriptors:
        name = descriptor.get("name")
        if not isinstance(name, str):
            continue
        if name == "__proto__":
            value = as_str_map(descriptor.get("value"))
            if value is not None:
                candidate = value.get("objectId")
                if isinstance(candidate, str):
                    proto_id = candidate
            continue
        typed = _descriptor_type(descriptor)
        token = method_token(name)
        if typed == "function" and token is not None and token not in methods:
            methods.append(token)
        row = sanitize_property_row({"name": name, "type": typed, "subtype": None})
        if row["name_token"] != "other" or typed == "function":
            if row["name_token"] == "other" and typed != "function":
                continue
            if row["name_token"] != "other":
                property_rows.append(row)
        if name in _BOOLEAN_NAMES and open_state is None:
            open_state = _descriptor_bool(descriptor)
        collection_names = {
            "content",
            "contents",
            "options",
            "items",
            "results",
            "source",
            "sources",
        }
        if name_token(name) in collection_names:
            if typed == "array":
                length_class = _descriptor_length_class(descriptor)
        if name == "actions" and typed == "object":
            value = as_str_map(descriptor.get("value"))
            action_id = value.get("objectId") if value is not None else None
            if isinstance(action_id, str):
                for action in await _properties(session, action_id, own=True):
                    action_name = action.get("name")
                    token = method_token(action_name)
                    if token is not None and token not in methods:
                        methods.append(token)
    if proto_id is not None:
        for descriptor in await _properties(session, proto_id, own=True):
            name = descriptor.get("name")
            token = method_token(name)
            if _descriptor_type(descriptor) == "function" and token is not None:
                if token not in methods:
                    methods.append(token)
    methods.sort()
    return property_rows[:16], methods[:16], length_class, open_state


async def inspect_kunde_ember(page: Page) -> dict[str, object]:
    """Read-only Ember inspect. Does not click, type, or invoke methods."""

    payload = empty_kunde_ember()
    flags = await page.evaluate(_FLAGS_JS)
    envelope = as_str_map(flags)
    if envelope is None or envelope.get("ok") is not True:
        return apply_kunde_ember_dump(payload, dump_path=KUNDE_EMBER_DUMP)
    payload["ember_global_present"] = envelope.get("ember_global_present") is True
    payload["view_registry_present"] = envelope.get("view_registry_present") is True
    id_class = envelope.get("wrapper_ember_id_class")
    payload["wrapper_ember_id_class"] = (
        id_class if id_class in {"ember_digit", "other", "none"} else "none"
    )
    payload["view_constructor_token"] = constructor_token(envelope.get("wrapper_class"))
    context = getattr(page, "context", None)
    factory = getattr(context, "new_cdp_session", None) if context is not None else None
    if factory is None:
        return apply_kunde_ember_dump(payload, dump_path=KUNDE_EMBER_DUMP)
    session = await factory(page)
    await _send(session, "Runtime.enable")
    view_id = None
    lookup: str = "none"
    if payload["view_registry_present"] is True and payload["wrapper_ember_id_class"] == (
        "ember_digit"
    ):
        view_id = await _object_id(session, _VIEW_OBJECT_JS)
        if view_id is not None:
            lookup = "view_registry"
    if view_id is None:
        view_id = await _object_id(session, _WRAPPER_OBJECT_JS)
        if view_id is not None:
            lookup = "element_properties"
    payload["lookup_class"] = lookup
    payload["view_present"] = view_id is not None and lookup == "view_registry"
    if view_id is not None:
        rows, methods, length_class, open_state = await _collect_from_object(session, view_id)
        payload["property_rows"] = rows
        payload["method_name_tokens"] = methods
        payload["candidate_length_class"] = length_class
        payload["open_state"] = open_state
    detach = getattr(session, "detach", None)
    if detach is not None:
        await detach()
    return apply_kunde_ember_dump(payload, dump_path=KUNDE_EMBER_DUMP)
