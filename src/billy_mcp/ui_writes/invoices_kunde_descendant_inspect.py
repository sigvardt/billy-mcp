"""Read-only live capture of Kunde pickerfield descendants (E87B6AEF)."""

from __future__ import annotations

from typing import Final, cast

from billy_mcp.ui_writes.invoices_form_page import Page
from billy_mcp.ui_writes.invoices_kunde_control import event_type_token
from billy_mcp.ui_writes.invoices_kunde_descendant_rows import (
    as_str_map,
    classify_handler_source,
    sanitize_descendant,
)
from billy_mcp.ui_writes.invoices_kunde_descendants import (
    apply_kunde_descendant_dump,
    empty_kunde_descendants,
)

_WALK_JS: Final = """() => {
  const input = document.querySelector("input[name='contact']");
  if (!input) {
    return {ok: false};
  }
  const wrapper = input.closest(".pickerfield") || input.parentElement;
  if (!wrapper) {
    return {ok: false};
  }
  const wbox = wrapper.getBoundingClientRect();
  const rows = [];
  wrapper.querySelectorAll("*").forEach((el) => {
    if (rows.length >= 16) {
      return;
    }
    const style = window.getComputedStyle(el);
    const box = el.getBoundingClientRect();
    const visible = style.display !== "none" && style.visibility !== "hidden"
      && box.width > 0 && box.height > 0;
    if (!visible) {
      return;
    }
    const raw = el.className ? String(el.className) : "";
    const names = [];
    if (el.attributes) {
      for (const attr of el.attributes) {
        if (attr && typeof attr.name === "string" && attr.name.indexOf("data-") === 0) {
          names.push(attr.name);
        }
      }
    }
    names.sort();
    const disabled = el.disabled === true || el.getAttribute("aria-disabled") === "true";
    const interactive = !disabled && (
      el.tabIndex >= 0
      || ["A", "BUTTON", "INPUT", "SELECT", "TEXTAREA"].indexOf(el.tagName) >= 0
      || !!el.getAttribute("role")
    );
    rows.push({
      tag: el.tagName,
      role: el.getAttribute("role") || "",
      visible: true,
      interactive: interactive,
      class_tokens: raw.split(/\\s+/).filter(Boolean),
      data_attr_names: names,
      dx: box.left - wbox.left,
      dy: box.top - wbox.top,
      w: box.width,
      h: box.height,
      pointer_events: style.pointerEvents,
    });
  });
  return {ok: true, wrapper_tag: wrapper.tagName, rows: rows};
}"""
_WRAPPER_OBJECT_JS: Final = """(() => {
  const el = document.querySelector("input[name='contact']");
  return el ? (el.closest(".pickerfield") || el.parentElement) : null;
})()"""
_SOURCE_WINDOW: Final = 400


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


def _wrapper_tag(raw: object) -> str:
    if isinstance(raw, str) and raw.upper() == "DIV":
        return "DIV"
    return "other"


async def _listener_types_for(session: object, object_id: str) -> list[str]:
    raw = await _send(session, "DOMDebugger.getEventListeners", {"objectId": object_id})
    envelope = as_str_map(raw)
    if envelope is None:
        return []
    rows_raw = envelope.get("listeners")
    if not isinstance(rows_raw, list):
        return []
    tokens: list[str] = []
    for item in cast(list[object], rows_raw):
        listener = as_str_map(item)
        if listener is None:
            continue
        event_type = listener.get("type")
        token = event_type_token(event_type if isinstance(event_type, str) else None)
        if token not in tokens:
            tokens.append(token)
    tokens.sort()
    return tokens


async def _classify_wrapper_guard(session: object, wrapper_id: str) -> str:
    raw = await _send(session, "DOMDebugger.getEventListeners", {"objectId": wrapper_id})
    envelope = as_str_map(raw)
    if envelope is None:
        return "none"
    rows_raw = envelope.get("listeners")
    if not isinstance(rows_raw, list):
        return "none"
    script_id = ""
    column = 0
    for item in cast(list[object], rows_raw):
        listener = as_str_map(item)
        if listener is None or listener.get("type") != "click":
            continue
        sid = listener.get("scriptId")
        if isinstance(sid, str) and sid != "":
            script_id = sid
            col = listener.get("columnNumber")
            column = col if isinstance(col, int) else 0
            break
    if script_id == "":
        return "none"
    source_raw = await _send(session, "Debugger.getScriptSource", {"scriptId": script_id})
    source_map = as_str_map(source_raw)
    source = source_map.get("scriptSource") if source_map is not None else None
    if not isinstance(source, str) or source == "":
        return "none"
    start = max(column - _SOURCE_WINDOW, 0)
    window = source[start : column + _SOURCE_WINDOW]
    del source
    return classify_handler_source(window)


async def inspect_kunde_descendants(page: Page) -> dict[str, object]:
    """Read-only descendant map. Does not click or type."""

    payload = empty_kunde_descendants()
    walked = await page.evaluate(_WALK_JS)
    envelope = as_str_map(walked)
    if envelope is None or envelope.get("ok") is not True:
        return apply_kunde_descendant_dump(payload)
    payload["wrapper_tag"] = _wrapper_tag(envelope.get("wrapper_tag"))
    rows: list[dict[str, object]] = []
    raw_rows = envelope.get("rows")
    if isinstance(raw_rows, list):
        for item in cast(list[object], raw_rows):
            row = as_str_map(item)
            if row is None:
                continue
            rows.append(sanitize_descendant(row))
    context = getattr(page, "context", None)
    factory = getattr(context, "new_cdp_session", None) if context is not None else None
    if factory is not None:
        session = await factory(page)
        await _send(session, "Debugger.enable")
        await _send(session, "DOM.enable")
        await _send(session, "Runtime.enable")
        for index, row in enumerate(rows):
            object_id = await _object_id(
                session,
                (
                    "(() => { const input = document.querySelector(\"input[name='contact']\");"
                    " const wrap = input && (input.closest('.pickerfield') || input.parentElement);"
                    " if (!wrap) { return null; }"
                    " const visible = [];"
                    " wrap.querySelectorAll('*').forEach((el) => {"
                    "   const style = window.getComputedStyle(el);"
                    "   const box = el.getBoundingClientRect();"
                    "   if (style.display !== 'none' && style.visibility !== 'hidden'"
                    "     && box.width > 0 && box.height > 0) { visible.push(el); }"
                    " });"
                    f" return visible[{index}] || null; }})()"
                ),
            )
            if object_id is not None:
                row["listener_types"] = await _listener_types_for(session, object_id)
        wrapper_id = await _object_id(session, _WRAPPER_OBJECT_JS)
        if wrapper_id is not None:
            payload["wrapper_handler_guard"] = await _classify_wrapper_guard(session, wrapper_id)
        detach = getattr(session, "detach", None)
        if detach is not None:
            await detach()
    payload["descendants"] = rows
    return apply_kunde_descendant_dump(payload)
