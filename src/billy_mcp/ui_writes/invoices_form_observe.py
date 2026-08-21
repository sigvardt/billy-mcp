"""Non-PII Kunde chrome dumps. Never stores the tag or credentials."""

from __future__ import annotations

from collections.abc import Mapping
from inspect import isawaitable
from pathlib import Path
from time import monotonic
from typing import Final, cast

from billy_mcp.ui_writes.invoices_form_page import Locator, Page, write_json
from billy_mcp.ui_writes.invoices_kunde import (
    autocomplete_token,
    chevron_hit_missing_keys,
    empty_chevron_hit,
    empty_widget_contract,
    named_kunde_opener,
    opener_dump_missing_keys,
    pick_kunde_create_index,
    pick_kunde_existing_option_index,
    placeholder_flags,
    portal_list_item_flags,
    widget_contract_missing_keys,
)
from billy_mcp.ui_writes.invoices_kunde_div import (
    div_ownership_missing_keys,
    empty_div_ownership,
)
from billy_mcp.ui_writes.invoices_kunde_events import (
    CONSOLE_DELTA_KEYS,
    EVENT_ERROR_CAP,
    KUNDE_EVENT_INIT_SCRIPT,
    count_deltas,
    empty_console_delta,
    empty_event_counts,
    event_error_row,
    event_message_of,
    event_name_of,
    event_source_of,
    kunde_event_missing_keys,
    next_event_phase,
    parse_event_counts,
    scrub_message_shape,
)
from billy_mcp.ui_writes.invoices_kunde_routes import (
    pending_from_url,
    row_from_pending,
)
from billy_mcp.ui_writes.invoices_kunde_trace import (
    TRACE_REQUEST_CAP,
    kunde_trace_missing_keys,
    name_token,
    request_url_class,
)

KUNDE_CHROME_DUMP: Final = (
    Path.home() / ".local" / "share" / "billy-mcp" / "inspect-live-invoices-kunde.json"
)
KUNDE_OPENER_DUMP: Final = (
    Path.home() / ".local" / "share" / "billy-mcp" / "inspect-live-invoices-kunde-opener.json"
)
KUNDE_FIELD_SHOT: Final = (
    Path.home() / ".local" / "share" / "billy-mcp" / "inspect-live-invoices-kunde-field.png"
)
KUNDE_LOOKUP_DUMP: Final = (
    Path.home() / ".local" / "share" / "billy-mcp" / "inspect-live-invoices-kunde-lookup.json"
)
KUNDE_TRACE_DUMP: Final = (
    Path.home() / ".local" / "share" / "billy-mcp" / "inspect-live-invoices-kunde-trace.json"
)
KUNDE_EVENT_MESSAGE_DUMP: Final = (
    Path.home()
    / ".local"
    / "share"
    / "billy-mcp"
    / "inspect-live-invoices-kunde-event-messages.json"
)
ALT_LIST_SELECTORS: Final[tuple[str, ...]] = (
    ".ember-power-select-dropdown",
    ".ember-basic-dropdown-content",
    "[role='listbox']",
)


async def portal_items(
    page: Page, unique_tag: str, *, root: Locator | None = None
) -> list[dict[str, bool]]:
    """Non-PII flags for Kunde dropdown lists."""

    lists = root if root is not None else page.locator(".ds-dropdown-list.ds-moved-with-portal")
    count = await lists.count()
    items: list[dict[str, bool]] = []
    for index in range(min(count, 9)):
        node = lists.nth(index)
        try:
            text = (await node.inner_text()).strip()
            visible = await node.is_visible()
        except (TimeoutError, RuntimeError):
            continue
        flags = portal_list_item_flags(text, unique_tag)
        flags["visible"] = visible
        items.append(flags)
    return items


async def observe_kunde(
    page: Page,
    field: Locator,
    unique_tag: str,
    *,
    phase: str,
    wrapper: Locator | None = None,
) -> dict[str, object]:
    """Flags for one Kunde phase. Never stores the tag."""

    items = await portal_items(page, unique_tag)
    wrapper_items: list[dict[str, bool]] = []
    alt_items: list[dict[str, bool]] = []
    search_n = 0
    clear_n = 0
    trigger_n = 0
    if wrapper is not None:
        wrapper_items = await portal_items(
            page, unique_tag, root=wrapper.locator(".ds-dropdown-list")
        )
        search_n = await wrapper.locator("[data-testid='search']").count()
        clear_n = await wrapper.locator("[data-testid='circleX']").count()
        trigger_n = await wrapper.locator("[class*='trigger'], [class*='caret']").count()
    for selector in ALT_LIST_SELECTORS:
        alt_items.extend(await portal_items(page, unique_tag, root=page.locator(selector)))
    box = await field.bounding_box()
    value_len = -1
    try:
        value_len = len(await field.input_value())
    except (TimeoutError, RuntimeError):
        value_len = -1
    combined = [*wrapper_items, *alt_items, *items]
    owned = await _ownership_dump(field)
    raw_owners = owned.get("owners")
    owner_rows: list[dict[str, object]] = []
    if isinstance(raw_owners, list):
        for item in cast(list[object], raw_owners):
            if isinstance(item, dict):
                owner_rows.append(cast(dict[str, object], item))
    payload: dict[str, object] = {
        "phase": phase,
        "field_name": await field.get_attribute("name"),
        "field_role": await field.get_attribute("role"),
        "aria_expanded": await field.get_attribute("aria-expanded"),
        "value_len": value_len,
        "tag_len": len(unique_tag),
        "search_trigger": search_n > 0,
        "clear_trigger": clear_n > 0,
        "trigger_count": trigger_n,
        "page_search_count": await page.locator("[data-testid='search']").count(),
        "box": None
        if box is None
        else {
            "w": round(float(box.get("width", 0)), 1),
            "h": round(float(box.get("height", 0)), 1),
        },
        "portal_count": len(items),
        "wrapper_count": len(wrapper_items),
        "alt_list_count": len(alt_items),
        "existing_index": pick_kunde_existing_option_index(combined),
        "create_index": pick_kunde_create_index(combined),
        "option_role_count": await page.locator("[role='option']").count(),
        "items": items,
        "wrapper_items": wrapper_items,
        "alt_items": alt_items,
        "owners_n": len(owner_rows),
        "reached_form": any(row.get("is_form") is True for row in owner_rows),
        "element_from_point": owned.get("element_from_point"),
        "pointer_events": owned.get("pointer_events"),
        "z_index": owned.get("z_index"),
        "input": owned.get("input"),
        "datalist_count": owned.get("datalist_count", 0),
        "datalist_option_count": owned.get("datalist_option_count", 0),
        "visible_input_count": owned.get("visible_input_count", 0),
        "a11y_snapshot": owned.get("a11y_snapshot"),
        "field_shot": owned.get("field_shot"),
        "contact_get_count": 0,
        "right_edge_offset": owned.get("right_edge_offset"),
        "right_edge_element_from_point": owned.get("right_edge_element_from_point"),
        "right_edge_same_input": owned.get("right_edge_same_input"),
        "appearance_token": owned.get("appearance_token"),
        "background_image_kind": owned.get("background_image_kind"),
        "before_content_kind": owned.get("before_content_kind"),
        "after_content_kind": owned.get("after_content_kind"),
        "input_child_count": owned.get("input_child_count"),
        "right_edge_elements_from_point_stack": owned.get("right_edge_elements_from_point_stack"),
        "hit_box": owned.get("hit_box"),
        "hit_pointer_events": owned.get("hit_pointer_events"),
        "hit_role": owned.get("hit_role"),
        "hit_name_present": owned.get("hit_name_present"),
        "hit_testid": owned.get("hit_testid"),
        "hit_class_tokens": owned.get("hit_class_tokens"),
        "hit_direct_parent": owned.get("hit_direct_parent"),
        "hit_contained_by_input": owned.get("hit_contained_by_input"),
        "hit_contains_input": owned.get("hit_contains_input"),
        "hit_shares_smallest_wrapper": owned.get("hit_shares_smallest_wrapper"),
        "smallest_wrapper": owned.get("smallest_wrapper"),
        "nearest_clickable_ancestor": owned.get("nearest_clickable_ancestor"),
    }
    return await _attach_widget_contract(page, field, payload)


def dump_kunde_phases(after_click: dict[str, object], after_type: dict[str, object]) -> None:
    """Write the no-click after-type dump IR asked for."""

    write_json(
        KUNDE_CHROME_DUMP,
        {
            "path_class": "invoices_new",
            "after_click": after_click,
            "after_type": after_type,
        },
    )


def dump_kunde_opener(payload: Mapping[str, object]) -> None:
    """Write non-PII opener chrome to the opener dump, never the owner file."""

    write_json(KUNDE_OPENER_DUMP, dict(payload))


def _class_tokens(raw: str | None) -> list[str]:
    if not raw:
        return []
    return sorted(
        token for token in raw.split() if token.startswith(("ds-", "ember-", "Dropdown", "input"))
    )


async def _safe_count(node: Locator) -> int:
    try:
        return await node.count()
    except (TimeoutError, RuntimeError):
        return 0


async def _safe_attr(node: Locator, name: str) -> str | None:
    try:
        value = await node.get_attribute(name)
    except (TimeoutError, RuntimeError):
        return None
    return value if isinstance(value, str) and value else None


POWER_SELECT_TRIGGER: Final = ".ember-power-select-trigger"
_OWNERSHIP_JS: Final = """el => {
  const token = (raw) => (typeof raw === "string" ? raw : "")
    .split(/\\s+/).filter((t) => /^(ds-|ember-|Dropdown|input|form)/.test(t)).sort();
  const ariaNames = [];
  for (const name of el.getAttributeNames()) {
    if (name.startsWith("aria-")) ariaNames.push(name);
  }
  const box = el.getBoundingClientRect();
  const style = window.getComputedStyle(el);
  const rawAuto = (el.getAttribute("autocomplete") || "").trim().toLowerCase();
  const autocompleteToken = !rawAuto
    ? "empty"
    : (rawAuto === "on" || rawAuto === "off" || rawAuto === "name" ? rawAuto : "other");
  const listId = el.getAttribute("list") || "";
  const linked = listId ? document.getElementById(listId) : null;
  const visibleInputs = Array.from(document.querySelectorAll("input")).filter((node) => {
    const computed = window.getComputedStyle(node);
    return computed.display !== "none" && computed.visibility !== "hidden"
      && node.getClientRects().length > 0;
  });
  const owners = [];
  let node = el.parentElement;
  while (node && owners.length < 16) {
    const tag = node.tagName || "";
    owners.push({
      tag,
      has_id: Boolean(node.id),
      role: node.getAttribute("role"),
      has_name: Boolean(node.getAttribute("name")),
      testid: node.getAttribute("data-testid"),
      class_tokens: token(node.className),
      is_form: tag === "FORM",
    });
    if (tag === "FORM") break;
    node = node.parentElement;
  }
  const id = el.id || "";
  const forLabel = id ? document.querySelector("label[for=\\"" + CSS.escape(id) + "\\"]") : null;
  const wrapLabel = el.closest("label");
  const active = document.activeElement;
  const hit = document.elementFromPoint(box.left + box.width / 2, box.top + box.height / 2);
  const dx = Math.max(0, Math.round(box.width) - 8);
  const dy = Math.max(0, Math.floor(box.height / 2));
  const rightHit = document.elementFromPoint(box.left + dx, box.top + dy);
  const appearanceRaw = String(style.appearance || style.webkitAppearance || "")
    .trim().toLowerCase();
  const appearanceToken = (appearanceRaw === "auto" || appearanceRaw === "none"
    || appearanceRaw === "textfield")
    ? appearanceRaw
    : (appearanceRaw ? "other" : "none");
  const bg = String(style.backgroundImage || "").trim();
  const bgLower = bg.toLowerCase();
  const backgroundImageKind = (!bg || bgLower === "none")
    ? "none"
    : (bgLower.includes("url(") ? "url"
      : (bgLower.includes("gradient") ? "gradient" : "other"));
  const kind = (raw) => {
    if (!raw || String(raw).toLowerCase() === "none") return "none";
    const compact = String(raw).trim();
    if (compact === '""' || compact === "''") return "empty";
    return "present";
  };
  const beforeRaw = window.getComputedStyle(el, "::before").content;
  const afterRaw = window.getComputedStyle(el, "::after").content;
  const sameInput = Boolean(
    rightHit && rightHit.tagName === "INPUT" && rightHit.getAttribute("name") === "contact"
  );
  const peToken = (node) => {
    const pe = String(window.getComputedStyle(node).pointerEvents || "").toLowerCase();
    return (pe === "auto" || pe === "none") ? pe : (pe ? "other" : "none");
  };
  const namePresent = (node) => Boolean(
    node.getAttribute("aria-label") || node.getAttribute("name") || node.getAttribute("title")
  );
  const stackSrc = (document.elementsFromPoint
    ? document.elementsFromPoint(box.left + dx, box.top + dy)
    : (rightHit ? [rightHit] : [])).slice(0, 8);
  const stack = stackSrc.map((node) => ({
    tag: node.tagName || "",
    class_tokens: token(node.className),
    name: node.getAttribute("name"),
    testid: node.getAttribute("data-testid"),
    role: node.getAttribute("role"),
    pointer_events: peToken(node),
  }));
  const hitRect = rightHit ? rightHit.getBoundingClientRect() : null;
  const hitParent = rightHit ? rightHit.parentElement : null;
  const contactCount = (node) => {
    if (!node) return 0;
    let n = (node.tagName === "INPUT" && node.getAttribute("name") === "contact") ? 1 : 0;
    n += node.querySelectorAll("input[name='contact']").length;
    return n;
  };
  let smallest = null;
  let walk = rightHit;
  while (walk) {
    if (walk.contains(el)) { smallest = walk; break; }
    walk = walk.parentElement;
  }
  let nearest = null;
  walk = rightHit;
  while (walk) {
    const role = (walk.getAttribute("role") || "").toLowerCase();
    const tag = walk.tagName || "";
    const isContact = tag === "INPUT" && walk.getAttribute("name") === "contact";
    if (isContact || tag === "BUTTON" || tag === "A"
        || role === "button" || role === "link" || role === "combobox" || role === "listbox") {
      nearest = {
        tag,
        role: walk.getAttribute("role"),
        name_present: namePresent(walk),
        testid: walk.getAttribute("data-testid"),
        is_contact_input: isContact,
      };
      break;
    }
    walk = walk.parentElement;
  }
  return {
    input: {
      tag: el.tagName || "",
      type: el.getAttribute("type"),
      has_id: Boolean(id),
      has_autocomplete: Boolean(el.getAttribute("autocomplete")),
      autocomplete_token: autocompleteToken,
      list_present: Boolean(listId),
      disabled: Boolean(el.disabled),
      readonly: Boolean(el.readOnly),
      aria_names: ariaNames.sort(),
    },
    datalist_count: document.querySelectorAll("datalist").length,
    datalist_option_count: linked ? linked.querySelectorAll("option").length : 0,
    visible_input_count: visibleInputs.length,
    owners,
    label: {has_for: Boolean(forLabel), has_wrap: Boolean(wrapLabel)},
    aria: {
      labelledby: Boolean(el.getAttribute("aria-labelledby")),
      describedby: Boolean(el.getAttribute("aria-describedby")),
      controls: Boolean(el.getAttribute("aria-controls")),
      owns: Boolean(el.getAttribute("aria-owns")),
      activedescendant: Boolean(el.getAttribute("aria-activedescendant")),
      autocomplete: Boolean(el.getAttribute("aria-autocomplete")),
      haspopup: Boolean(el.getAttribute("aria-haspopup")),
      expanded: el.getAttribute("aria-expanded"),
    },
    active_element: active && {
      tag: active.tagName || "",
      name: active.getAttribute("name"),
      role: active.getAttribute("role"),
      testid: active.getAttribute("data-testid"),
    },
    a11y: {
      role: el.getAttribute("role"),
      has_name: Boolean(el.getAttribute("aria-label") || forLabel || wrapLabel),
      disabled: el.getAttribute("aria-disabled") === "true" || Boolean(el.disabled),
      invalid: el.getAttribute("aria-invalid") === "true",
      busy: el.getAttribute("aria-busy") === "true",
      expanded: el.getAttribute("aria-expanded"),
    },
    box: {
      x: Math.round(box.x), y: Math.round(box.y),
      w: Math.round(box.width), h: Math.round(box.height)
    },
    pointer_events: style.pointerEvents || "unknown",
    z_index: style.zIndex || "auto",
    element_from_point: hit && {
      tag: hit.tagName || "",
      class_tokens: token(hit.className),
      name: hit.getAttribute("name"),
      testid: hit.getAttribute("data-testid"),
    },
    right_edge_offset: {dx, dy},
    right_edge_element_from_point: rightHit && {
      tag: rightHit.tagName || "",
      class_tokens: token(rightHit.className),
      name: rightHit.getAttribute("name"),
      testid: rightHit.getAttribute("data-testid"),
    },
    right_edge_same_input: sameInput,
    appearance_token: appearanceToken,
    background_image_kind: backgroundImageKind,
    before_content_kind: kind(beforeRaw),
    after_content_kind: kind(afterRaw),
    input_child_count: el.children ? el.children.length : 0,
    right_edge_elements_from_point_stack: stack,
    hit_box: hitRect && {
      x: Math.round(hitRect.x), y: Math.round(hitRect.y),
      w: Math.round(hitRect.width), h: Math.round(hitRect.height)
    },
    hit_pointer_events: rightHit ? peToken(rightHit) : "none",
    hit_role: rightHit ? rightHit.getAttribute("role") : null,
    hit_name_present: rightHit ? namePresent(rightHit) : false,
    hit_testid: rightHit ? rightHit.getAttribute("data-testid") : null,
    hit_class_tokens: rightHit ? token(rightHit.className) : [],
    hit_direct_parent: hitParent && {
      tag: hitParent.tagName || "",
      class_tokens: token(hitParent.className),
      role: hitParent.getAttribute("role"),
      name_present: namePresent(hitParent),
      testid: hitParent.getAttribute("data-testid"),
      contains_contact_input: contactCount(hitParent) > 0,
    },
    hit_contained_by_input: Boolean(rightHit && el.contains(rightHit) && rightHit !== el),
    hit_contains_input: Boolean(rightHit && rightHit.contains(el)),
    hit_shares_smallest_wrapper: Boolean(smallest),
    smallest_wrapper: smallest && {
      tag: smallest.tagName || "",
      class_tokens: token(smallest.className),
      contact_input_count: contactCount(smallest),
      child_input_count: smallest.querySelectorAll("input").length
        + ((smallest.tagName === "INPUT") ? 1 : 0),
    },
    nearest_clickable_ancestor: nearest,
  };
}"""


def empty_ownership() -> dict[str, object]:
    """Structurally complete 5E1EDFB4 keys when evaluate is unavailable."""

    return {
        "input": {
            "tag": None,
            "type": None,
            "has_id": False,
            "has_autocomplete": False,
            "autocomplete_token": "empty",
            "list_present": False,
            "disabled": False,
            "readonly": False,
            "aria_names": [],
        },
        "datalist_count": 0,
        "datalist_option_count": 0,
        "visible_input_count": 0,
        "owners": [],
        "label": {"has_for": False, "has_wrap": False},
        "aria": {
            "labelledby": False,
            "describedby": False,
            "controls": False,
            "owns": False,
            "activedescendant": False,
            "autocomplete": False,
            "haspopup": False,
            "expanded": None,
        },
        "active_element": None,
        "a11y": {
            "role": None,
            "has_name": False,
            "disabled": False,
            "invalid": False,
            "busy": False,
            "expanded": None,
        },
        "box": None,
        "pointer_events": "unknown",
        "z_index": "auto",
        "element_from_point": None,
        **empty_chevron_hit(),
        **empty_div_ownership(),
    }


async def _ownership_dump(field: Locator) -> dict[str, object]:
    """Read-only ownership walk. Never clicks. Never stores the tag."""

    payload = empty_ownership()
    evaluate = getattr(field, "evaluate", None)
    if evaluate is None:
        return payload
    try:
        raw = await evaluate(_OWNERSHIP_JS)
    except (TimeoutError, RuntimeError, AttributeError):
        return payload
    if not isinstance(raw, dict):
        return payload
    typed_raw = cast(dict[str, object], raw)
    for key in payload:
        if key in typed_raw:
            payload[key] = typed_raw[key]
    for key, value in typed_raw.items():
        if key not in payload:
            payload[key] = value
    return payload


def _count_a11y(node: object) -> dict[str, object]:
    """Role and control counts only. Never stores names."""

    role_counts: dict[str, int] = {}
    control_count = 0
    listbox_present = False

    def walk(item: object) -> None:
        nonlocal control_count, listbox_present
        if not isinstance(item, Mapping):
            return
        typed_item = cast(Mapping[str, object], item)
        role = typed_item.get("role")
        if isinstance(role, str) and role:
            role_counts[role] = role_counts.get(role, 0) + 1
            if role in {"textbox", "combobox", "button", "link", "searchbox"}:
                control_count += 1
            if role == "listbox":
                listbox_present = True
        children = typed_item.get("children")
        if isinstance(children, list):
            for child in cast(list[object], children):
                walk(child)

    walk(node)
    return {
        "control_count": control_count,
        "listbox_present": listbox_present,
        "role_counts": role_counts,
    }


async def _a11y_snapshot_counts(page: Page) -> dict[str, object]:
    """Playwright accessibility snapshot reduced to counts."""

    accessibility = getattr(page, "accessibility", None)
    snap_fn = getattr(accessibility, "snapshot", None) if accessibility is not None else None
    if snap_fn is None:
        return cast(dict[str, object], empty_widget_contract()["a11y_snapshot"])
    try:
        snapshot = await snap_fn()
    except (TimeoutError, RuntimeError, TypeError):
        return cast(dict[str, object], empty_widget_contract()["a11y_snapshot"])
    return _count_a11y(snapshot)


async def _field_shot(page: Page, field: Locator) -> dict[str, object]:
    """Owner-only cropped field shot. Repo stores flags and box only."""

    box = None
    try:
        box = await field.bounding_box()
    except (TimeoutError, RuntimeError):
        box = None
    shot = getattr(page, "screenshot", None)
    if shot is None or box is None:
        return {"present": False, "bytes": 0, "box": None}
    clip = {
        "x": float(box.get("x", 0)),
        "y": float(box.get("y", 0)),
        "width": float(box.get("width", 0)),
        "height": float(box.get("height", 0)),
    }
    if clip["width"] <= 0 or clip["height"] <= 0:
        return {"present": False, "bytes": 0, "box": None}
    try:
        KUNDE_FIELD_SHOT.parent.mkdir(parents=True, exist_ok=True)
        await shot(path=str(KUNDE_FIELD_SHOT), full_page=False, clip=clip)
        size = KUNDE_FIELD_SHOT.stat().st_size if KUNDE_FIELD_SHOT.is_file() else 0
        return {
            "present": size > 0,
            "bytes": size,
            "box": {
                "x": round(clip["x"]),
                "y": round(clip["y"]),
                "w": round(clip["width"]),
                "h": round(clip["height"]),
            },
        }
    except (OSError, TimeoutError, RuntimeError, TypeError):
        return {"present": False, "bytes": 0, "box": None}


class KundeTraceSink:
    """Redacted same-origin request and console counters. Never stores bodies."""

    def __init__(self) -> None:
        self.requests: list[dict[str, object]] = []
        self.console_categories: dict[str, int] = {"script": 0, "pageerror": 0, "other": 0}
        self._pending: dict[int, dict[str, object]] = {}
        self._started: dict[int, float] = {}
        self.event_totals: dict[str, int] = empty_event_counts()
        self._console_marked: dict[str, int] = empty_console_delta()
        self.phase_errors: list[dict[str, str]] = []
        self.current_phase: str = "at_rest"
        self.scrubbed_messages: list[str] = []
        self.route_templates: list[str] = []

    def snapshot_requests(self) -> list[dict[str, object]]:
        rows = list(self.requests)
        for request_id, row in self._pending.items():
            if len(rows) >= TRACE_REQUEST_CAP:
                break
            started = self._started.get(request_id, monotonic())
            rows.append(
                row_from_pending(
                    row,
                    status=0,
                    timing_ms=max(0, int((monotonic() - started) * 1000)),
                    phase=self.current_phase,
                )
            )
        return rows[:TRACE_REQUEST_CAP]

    def note_request(self, request_id: int, method: str, url: str) -> None:
        pending = pending_from_url(method, url)
        path_class = str(pending.get("path_class") or request_url_class(url))
        if (
            len(self.requests) >= TRACE_REQUEST_CAP
            and request_id not in self._pending
            and path_class not in {"contacts", "invoices"}
        ):
            return
        self._pending[request_id] = pending
        self._started[request_id] = monotonic()
        template = pending.get("template")
        if isinstance(template, str) and path_class == "other_v2":
            if template not in self.route_templates:
                self.route_templates.append(template)

    def _store_row(self, row: dict[str, object]) -> None:
        if len(self.requests) < TRACE_REQUEST_CAP:
            self.requests.append(row)
            return
        if row.get("path_class") not in {"contacts", "invoices"}:
            return
        for index, existing in enumerate(self.requests):
            if existing.get("path_class") not in {"contacts", "invoices"}:
                self.requests[index] = row
                return
        self.requests[-1] = row

    def note_response(self, request_id: int, method: str, url: str, status: int) -> None:
        pending = self._pending.pop(request_id, None)
        started = self._started.pop(request_id, monotonic())
        if pending is None:
            pending = pending_from_url(method, url)
        row = row_from_pending(
            pending,
            status=status,
            timing_ms=max(0, int((monotonic() - started) * 1000)),
            phase=self.current_phase,
        )
        self._store_row(row)

    def note_console(self, kind: str, event: object | None = None) -> None:
        if kind == "error":
            self.console_categories["script"] += 1
            if event is not None:
                self._record_event_error(event)
            return
        self.console_categories["other"] += 1

    def note_page_error(self, event: object | None = None) -> None:
        self.console_categories["pageerror"] += 1
        if event is not None:
            self._record_event_error(event)

    def _record_event_error(self, event: object) -> None:
        message = event_message_of(event)
        self.scrubbed_messages.append(scrub_message_shape(message))
        if len(self.phase_errors) >= EVENT_ERROR_CAP:
            return
        self.phase_errors.append(
            event_error_row(
                name=event_name_of(event),
                source=event_source_of(event),
                message=message,
                phase=self.current_phase,
            )
        )

    def snapshot_phase(self, phase: str, event_totals: dict[str, int]) -> dict[str, object]:
        """Freeze phase-scoped event and console deltas, then advance."""

        event_counts = count_deltas(event_totals, self.event_totals)
        self.event_totals = dict(event_totals)
        console_delta = count_deltas(self.console_categories, self._console_marked)
        self._console_marked = {key: self.console_categories[key] for key in CONSOLE_DELTA_KEYS}
        errors = [row for row in self.phase_errors if row.get("phase") == phase]
        self.current_phase = next_event_phase(phase)
        return {
            "event_counts": event_counts,
            "console_delta": console_delta,
            "errors": errors,
        }


def watch_kunde_trace(page: Page, sink: KundeTraceSink) -> None:
    """Attach read-only request/console listeners. Call before goto."""

    def _on_request(event: object) -> None:
        url = str(getattr(event, "url", "") or "")
        request = getattr(event, "request", None)
        method = str(
            getattr(event, "method", "")
            or (getattr(request, "method", "") if request is not None else "")
        )
        sink.note_request(id(event), method, url)

    def _on_response(event: object) -> None:
        request = getattr(event, "request", None)
        request_id = id(request) if request is not None else id(event)
        url = str(getattr(event, "url", "") or "")
        if request is not None:
            url = str(getattr(request, "url", "") or url)
        method = str(
            getattr(event, "method", "")
            or (getattr(request, "method", "") if request is not None else "")
        )
        status_raw = getattr(event, "status", 0)
        status = status_raw if isinstance(status_raw, int) else 0
        sink.note_response(request_id, method, url, status)

    def _on_console(event: object) -> None:
        sink.note_console(str(getattr(event, "type", "") or "").casefold(), event)

    def _on_page_error(event: object) -> None:
        sink.note_page_error(event)

    page.on("request", _on_request)
    page.on("response", _on_response)
    page.on("console", _on_console)
    page.on("pageerror", _on_page_error)


async def install_kunde_event_listeners(page: Page) -> None:
    """Install contact-field event counters before the invoice form opens."""

    added = page.add_init_script(KUNDE_EVENT_INIT_SCRIPT)
    if isawaitable(added):
        await added


async def read_kunde_event_counts(page: Page) -> dict[str, int]:
    """Read document event totals. Counts only name=contact targets."""

    raw = await page.evaluate("() => window.__billyKundeEvents || null")
    return parse_event_counts(raw)


def attach_kunde_event(
    payload: dict[str, object],
    bundle: Mapping[str, object],
    *,
    pageerror_unrelated_at_rest: bool,
) -> dict[str, object]:
    """Copy phase-scoped event keys onto a dump. Never stores message text."""

    payload["event_counts"] = bundle.get("event_counts") or empty_event_counts()
    payload["console_delta"] = bundle.get("console_delta") or empty_console_delta()
    errors = bundle.get("errors")
    payload["errors"] = errors if isinstance(errors, list) else []
    payload["pageerror_unrelated_at_rest"] = pageerror_unrelated_at_rest
    payload["kunde_event_missing_keys"] = kunde_event_missing_keys(payload)
    return payload


async def observe_kunde_active_element(page: Page) -> dict[str, object]:
    """Active-element flags only. Never stores ids or accessible names."""

    raw = await page.evaluate(
        """() => {
          const el = document.activeElement;
          if (!el) {
            return {tag: null, name: "", aria_expanded: false};
          }
          return {
            tag: el.tagName || null,
            name: el.getAttribute("name") || "",
            aria_expanded: el.getAttribute("aria-expanded") != null,
          };
        }"""
    )
    if not isinstance(raw, dict):
        return {"tag": None, "name_token": "empty", "aria_expanded_present": False}
    typed = cast(dict[str, object], raw)
    name_raw = typed.get("name")
    name = name_raw if isinstance(name_raw, str) else None
    tag_raw = typed.get("tag")
    tag = tag_raw if isinstance(tag_raw, str) else None
    return {
        "tag": tag,
        "name_token": name_token(name),
        "aria_expanded_present": typed.get("aria_expanded") is True,
    }


def attach_kunde_trace(
    payload: dict[str, object],
    sink: KundeTraceSink,
    *,
    listener_attached_before_form: bool,
    rest_portal_count: int,
) -> dict[str, object]:
    """Copy redacted trace fields onto a phase dump. Never stores tag text."""

    portal_count_raw = payload.get("portal_count")
    portal_count = portal_count_raw if isinstance(portal_count_raw, int) else 0
    payload["listener_attached_before_form"] = listener_attached_before_form
    payload["requests"] = sink.snapshot_requests()
    payload["console_categories"] = dict(sink.console_categories)
    payload["portal_inserted"] = portal_count > rest_portal_count
    payload["portal_count"] = portal_count
    option_raw = payload.get("option_role_count")
    payload["option_role_count"] = option_raw if isinstance(option_raw, int) else 0
    payload["kunde_trace_missing_keys"] = kunde_trace_missing_keys(payload)
    return payload


def dump_kunde_trace(payload: Mapping[str, object]) -> None:
    """Write the redacted tagged-flow dump. Never stores URLs or customer text."""

    write_json(KUNDE_TRACE_DUMP, dict(payload))


def dump_kunde_event_messages(shapes: list[str]) -> None:
    """Owner-only scrubbed shapes. Never commit this file."""

    write_json(KUNDE_EVENT_MESSAGE_DUMP, {"shapes": shapes[-32:]})


def watch_contact_lookups(page: Page, seen: list[str]) -> None:
    """Count browser GET /v2/contacts. Never stores the query string."""

    def _on_request(event: object) -> None:
        url = str(getattr(event, "url", "") or "")
        request = getattr(event, "request", None)
        method = str(
            getattr(event, "method", "")
            or (getattr(request, "method", "") if request is not None else "")
        )
        path = url.split("?", 1)[0]
        if method == "GET" and path.endswith("/v2/contacts"):
            seen.append("GET /v2/contacts")

    page.on("request", _on_request)


def dump_kunde_lookup(count: int) -> None:
    """Write the count-only lookup trace. Never stores URLs or query strings."""

    write_json(KUNDE_LOOKUP_DUMP, {"contact_get_count": count, "path": "/v2/contacts"})


async def _attach_widget_contract(
    page: Page, field: Locator, payload: dict[str, object]
) -> dict[str, object]:
    """Fill 51E18E60 widget keys. Never stores tag, names, or pixels."""

    defaults = empty_widget_contract()
    for key, value in defaults.items():
        if payload.get(key) is None:
            payload[key] = value
    raw_input = payload.get("input")
    input_map: dict[str, object] = (
        dict(cast(Mapping[str, object], raw_input)) if isinstance(raw_input, Mapping) else {}
    )
    if "autocomplete_token" not in input_map:
        input_map["autocomplete_token"] = autocomplete_token(
            await _safe_attr(field, "autocomplete")
        )
    if "list_present" not in input_map:
        input_map["list_present"] = bool(await _safe_attr(field, "list"))
    payload["input"] = input_map
    payload["a11y_snapshot"] = await _a11y_snapshot_counts(page)
    payload["field_shot"] = await _field_shot(page, field)
    defaults_chevron = empty_chevron_hit()
    for key, value in defaults_chevron.items():
        if payload.get(key) is None:
            payload[key] = value
    defaults_div = empty_div_ownership()
    for key, value in defaults_div.items():
        if payload.get(key) is None:
            payload[key] = value
    payload["widget_missing_keys"] = widget_contract_missing_keys(payload)
    payload["chevron_missing_keys"] = chevron_hit_missing_keys(payload)
    payload["div_ownership_missing_keys"] = div_ownership_missing_keys(payload)
    return payload


async def observe_kunde_opener(page: Page, field: Locator) -> dict[str, object]:
    """Ancestor, sibling, and 5E1EDFB4 ownership flags. Never stores the tag."""

    parent = field.locator("xpath=..")
    uncle = parent.locator("xpath=..")
    grand = uncle.locator("xpath=..")
    sibling_search = await _safe_count(parent.locator("[data-testid='search']"))
    uncle_search = await _safe_count(uncle.locator("[data-testid='search']"))
    sibling_caret = await _safe_count(parent.locator("[class*='trigger'], [class*='caret']"))
    uncle_caret = await _safe_count(uncle.locator("[class*='trigger'], [class*='caret']"))
    ancestor_class_tokens = [
        _class_tokens(await _safe_attr(parent, "class")),
        _class_tokens(await _safe_attr(uncle, "class")),
        _class_tokens(await _safe_attr(grand, "class")),
    ]
    trigger_n = await _safe_count(page.locator(POWER_SELECT_TRIGGER))
    payload: dict[str, object] = {
        "parent_testid": await _safe_attr(parent, "data-testid"),
        "parent_class_tokens": ancestor_class_tokens[0],
        "ancestor_class_tokens": ancestor_class_tokens,
        "sibling_search": sibling_search > 0,
        "uncle_search": uncle_search > 0,
        "sibling_caret": sibling_caret > 0,
        "uncle_caret": uncle_caret > 0,
        "kunde_label_count": await _safe_count(page.get_by_text("Kunde", exact=True)),
        "contact_id_count": await _safe_count(page.locator("input[name='contactId']")),
        "combobox_count": await _safe_count(page.locator("[role='combobox']")),
        "power_select_trigger_count": trigger_n,
        "placeholder_present": bool(await _safe_attr(field, "placeholder")),
        "placeholder_flags": placeholder_flags(await _safe_attr(field, "placeholder")),
        "field_name": await _safe_attr(field, "name"),
    }
    payload.update(await _ownership_dump(field))
    payload["named_opener"] = named_kunde_opener(payload)
    payload["missing_keys"] = opener_dump_missing_keys(payload)
    return await _attach_widget_contract(page, field, payload)


async def dump_kunde_chrome(page: Page) -> None:
    """Write non-PII invoice-form chrome when Kunde bind fails before a field."""

    names: list[str] = []
    inputs = page.locator("input, textarea, [role='combobox']")
    count = await inputs.count()
    for index in range(min(count, 30)):
        node = inputs.nth(index)
        name = await node.get_attribute("name")
        role = await node.get_attribute("role")
        data_cy = await node.get_attribute("data-cy")
        visible = await node.is_visible()
        names.append(f"name={name or ''} role={role or ''} cy={data_cy or ''} vis={visible}")
    heading = page.locator("h1")
    heading_text = ""
    if await heading.count() >= 1:
        heading_text = (await heading.first.inner_text()).strip()
    kunde_text = page.get_by_text("Kunde", exact=True)
    write_json(
        KUNDE_CHROME_DUMP,
        {
            "path_class": "/:org_slug/invoices/new" if "/invoices/new" in page.url else "other",
            "heading": heading_text,
            "fields": names,
            "kunde_text_count": await kunde_text.count(),
        },
    )
