"""Read-only CDP listener contract on proved Kunde hosts (28C8FBC8)."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Final, cast

from billy_mcp.ui_writes.invoices_form_page import Page
from billy_mcp.ui_writes.invoices_kunde_listeners import (
    KUNDE_LISTENER_DUMP,
    ROW_CAP,
    accepted_key_category_from,
    apply_kunde_listener_dump,
    as_str_map,
    empty_kunde_listeners,
    invoked_action_token_from,
    phase_token,
    property_categories_from,
    sanitize_listener_row,
    target_category_token,
)

_OWN_MARKERS: Final[tuple[str, ...]] = ("__billyKundeEvents",)
_SOURCE_WINDOW: Final = 400
_INPUT_JS: Final = "document.querySelector(\"input[name='contact']\")"
_WRAPPER_JS: Final = """(() => {
  const el = document.querySelector("input[name='contact']");
  return el ? el.closest(".pickerfield") : null;
})()"""
_OVERLAY_JS: Final = """(() => {
  const input = document.querySelector("input[name='contact']");
  const wrap = input && input.closest(".pickerfield");
  if (!wrap) { return null; }
  const wbox = wrap.getBoundingClientRect();
  let overlay = null;
  wrap.querySelectorAll("*").forEach((el) => {
    const style = window.getComputedStyle(el);
    const box = el.getBoundingClientRect();
    if (style.display === "none" || style.visibility === "hidden") { return; }
    if (box.width <= 0 || box.height <= 0) { return; }
    const dx = box.left - wbox.left;
    if (dx >= 200 && box.width >= 30 && box.width <= 50
        && box.height >= 30 && box.height <= 50) {
      overlay = el;
    }
  });
  return overlay;
})()"""
_ANCESTOR_JS: Final = """((index) => {
  const input = document.querySelector("input[name='contact']");
  const wrap = input && input.closest(".pickerfield");
  let node = wrap && wrap.parentElement;
  const chain = [];
  while (node && chain.length < 8 && node.tagName !== "BODY"
      && node.tagName !== "HTML" && node.tagName !== "FORM") {
    chain.push(node);
    node = node.parentElement;
  }
  return chain[index] || null;
})"""


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


def _is_own_listener(handler: object) -> bool:
    row = as_str_map(handler)
    if row is None:
        return False
    description = row.get("description")
    if not isinstance(description, str):
        return False
    return any(marker in description for marker in _OWN_MARKERS)


async def _classify_source(
    session: object, script_id: str, line: int, column: int
) -> dict[str, object]:
    raw = await _send(session, "Debugger.getScriptSource", {"scriptId": script_id})
    envelope = as_str_map(raw)
    source = envelope.get("scriptSource") if envelope is not None else None
    if not isinstance(source, str) or source == "":
        empty: dict[str, object] = {
            "event_property_categories": [],
            "accepted_key_category": "none",
            "invoked_action_token": "none",
        }
        return empty
    lines = source.splitlines()
    del source
    text = lines[line] if 0 <= line < len(lines) else ""
    start = max(column - _SOURCE_WINDOW, 0)
    window = text[start : column + _SOURCE_WINDOW]
    del text
    classified: dict[str, object] = {
        "event_property_categories": property_categories_from(window),
        "accepted_key_category": accepted_key_category_from(window),
        "invoked_action_token": invoked_action_token_from(window),
    }
    del window
    return classified


async def _rows_for(
    session: object,
    object_id: str,
    target: str,
    rows: list[dict[str, object]],
) -> None:
    raw = await _send(session, "DOMDebugger.getEventListeners", {"objectId": object_id})
    envelope = as_str_map(raw)
    if envelope is None:
        return
    rows_raw = envelope.get("listeners")
    if not isinstance(rows_raw, list):
        return
    for item in cast(list[object], rows_raw):
        if len(rows) >= ROW_CAP:
            return
        listener = as_str_map(item)
        if listener is None or _is_own_listener(listener.get("handler")):
            continue
        event_type = listener.get("type")
        script_id = listener.get("scriptId")
        line_raw = listener.get("lineNumber")
        column_raw = listener.get("columnNumber")
        classified: Mapping[str, object] = {
            "event_property_categories": [],
            "accepted_key_category": "none",
            "invoked_action_token": "none",
        }
        if isinstance(script_id, str) and script_id != "":
            classified = await _classify_source(
                session,
                script_id,
                line_raw if isinstance(line_raw, int) else 0,
                column_raw if isinstance(column_raw, int) else 0,
            )
        rows.append(
            sanitize_listener_row(
                {
                    "event_type": event_type if isinstance(event_type, str) else "other",
                    "phase": phase_token(listener.get("useCapture")),
                    "target_category": target_category_token(target),
                    "event_property_categories": classified.get("event_property_categories"),
                    "accepted_key_category": classified.get("accepted_key_category"),
                    "invoked_action_token": classified.get("invoked_action_token"),
                }
            )
        )


async def inspect_kunde_listeners(page: Page) -> dict[str, object]:
    """Read-only listener contract. Does not click, type, or invoke."""

    payload = empty_kunde_listeners()
    context = getattr(page, "context", None)
    factory = getattr(context, "new_cdp_session", None) if context is not None else None
    if factory is None:
        return apply_kunde_listener_dump(payload, dump_path=KUNDE_LISTENER_DUMP)
    session = await factory(page)
    await _send(session, "Debugger.enable")
    await _send(session, "DOM.enable")
    await _send(session, "Runtime.enable")
    rows: list[dict[str, object]] = []
    hosts: list[tuple[str, str]] = [
        (_INPUT_JS, "input"),
        (_OVERLAY_JS, "overlay"),
        (_WRAPPER_JS, "pickerfield"),
    ]
    for expression, target in hosts:
        object_id = await _object_id(session, expression)
        if object_id is not None:
            await _rows_for(session, object_id, target, rows)
    for index in range(8):
        object_id = await _object_id(session, f"{_ANCESTOR_JS}({index})")
        if object_id is None:
            break
        await _rows_for(session, object_id, "ancestor", rows)
    payload["rows"] = rows
    detach = getattr(session, "detach", None)
    if detach is not None:
        await detach()
    return apply_kunde_listener_dump(payload, dump_path=KUNDE_LISTENER_DUMP)
