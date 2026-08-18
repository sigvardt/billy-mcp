"""Scoped Gem som kladde validation capture on invoices/new.

Never stores source, URLs, locators, ids, or customer names.
"""

from __future__ import annotations

import asyncio
import json
import re
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Final, Literal, cast
from urllib.parse import urlsplit

from billy_mcp.ui_writes.invoices_form_page import Page, click_exact, write_json

ScopedKey = Literal[
    "gem_clicked",
    "invoice_persisted",
    "contact_input_present",
    "pickerfield_present",
    "active_element_category",
    "mutation_owned_count",
    "scoped_rows",
    "unique_action",
    "unique_action_owned_by_picker",
    "proved_bind",
    "missing_keys",
]
ActiveCategory = Literal["contact_input", "gem_button", "option", "opret_ny", "other", "none"]
UniqueAction = Literal["existing_option", "inline_opret_ny", "none"]
ProvedBind = Literal["draft_save_scoped_existing_option", "none"]
ExactMatch = Literal["validation", "empty_list", "opret_ny", "option", "none"]
PathToken = Literal["pickerfield", "input", "list", "option", "nav", "header", "other"]

REQUIRED_DRAFT_SAVE_SCOPED_KEYS: Final[tuple[ScopedKey, ...]] = (
    "gem_clicked",
    "invoice_persisted",
    "contact_input_present",
    "pickerfield_present",
    "active_element_category",
    "mutation_owned_count",
    "scoped_rows",
    "unique_action",
    "unique_action_owned_by_picker",
    "proved_bind",
    "missing_keys",
)
ACTIVE_CATEGORIES: Final[frozenset[str]] = frozenset(
    {"contact_input", "gem_button", "option", "opret_ny", "other", "none"}
)
UNIQUE_ACTIONS: Final[frozenset[str]] = frozenset({"existing_option", "inline_opret_ny", "none"})
PROVED_BIND_TOKENS: Final[frozenset[str]] = frozenset({"draft_save_scoped_existing_option", "none"})
EXACT_MATCHES: Final[frozenset[str]] = frozenset(
    {"validation", "empty_list", "opret_ny", "option", "none"}
)
PATH_TOKENS: Final[frozenset[str]] = frozenset(
    {"pickerfield", "input", "list", "option", "nav", "header", "other"}
)
ROLE_TOKENS: Final[frozenset[str]] = frozenset(
    {"option", "listbox", "listitem", "button", "link", "none", "other"}
)
ROW_KEYS: Final[tuple[str, ...]] = (
    "tag",
    "role",
    "visible",
    "interactive",
    "exact_match",
    "box",
    "z_index",
    "ownership_path",
    "is_mutation_owned",
)
ROW_CAP: Final = 16
PATH_CAP: Final = 8
_GEM = "Gem som kladde"
_CREATE_PATH = re.compile(r"^/[^/]+/invoices/new/?$")
DRAFT_SAVE_SCOPED_DUMP: Final = (
    Path.home() / ".local" / "share" / "billy-mcp" / "inspect-live-invoices-draft-save-scoped.json"
)
_ATTACH_JS: Final = """() => {
  const input = document.querySelector("input[name='contact']");
  if (!input) {
    return {ok: false};
  }
  const wrapper = input.closest(".pickerfield") || input.parentElement;
  if (!wrapper) {
    return {ok: false};
  }
  const mutations = [];
  const observer = new MutationObserver((records) => {
    for (const record of records) {
      if (record.target && record.target.nodeType === 1) {
        mutations.push(record.target);
      }
      record.addedNodes.forEach((node) => {
        if (node.nodeType === 1) {
          mutations.push(node);
        }
      });
    }
  });
  const roots = [wrapper];
  const named = [];
  const pushNamed = (value) => {
    if (!value) {
      return;
    }
    String(value).split(/\\s+/).forEach((id) => {
      if (id) {
        named.push(id);
      }
    });
  };
  pushNamed(wrapper.getAttribute("aria-controls"));
  pushNamed(wrapper.getAttribute("aria-owns"));
  pushNamed(input.getAttribute("aria-controls"));
  pushNamed(input.getAttribute("aria-owns"));
  named.forEach((id) => {
    const linked = document.getElementById(id);
    if (linked && linked.tagName !== "BODY" && linked.tagName !== "HTML") {
      roots.push(linked);
    }
  });
  if (input.id) {
    const safeId = input.id.replace(/\\\\/g, "\\\\\\\\").replace(/'/g, "\\\\'");
    const forSel = "label[for='" + safeId + "']";
    document.querySelectorAll(forSel).forEach((label) => {
      if (label && label.tagName !== "BODY") {
        roots.push(label);
      }
    });
  }
  let ancestor = wrapper.parentElement;
  let hops = 0;
  while (ancestor && hops < 3 && ancestor.tagName !== "BODY" && ancestor.tagName !== "HTML") {
    roots.push(ancestor);
    const cls = ancestor.className ? String(ancestor.className) : "";
    if (cls.indexOf("super-field") >= 0 || cls.indexOf("pickerfield") >= 0) {
      break;
    }
    ancestor = ancestor.parentElement;
    hops += 1;
  }
  let child = wrapper.firstElementChild;
  while (child) {
    if (child !== input && child.tagName !== "BODY") {
      roots.push(child);
    }
    child = child.nextElementSibling;
  }
  const seen = new Set();
  for (const root of roots) {
    if (!root || seen.has(root)) {
      continue;
    }
    seen.add(root);
    observer.observe(root, {
      childList: true,
      subtree: true,
      attributes: true,
      attributeFilter: ["class", "style", "hidden", "aria-hidden", "aria-expanded", "aria-invalid"],
    });
  }
  window.__billyDraftSaveScoped = {
    observer: observer, mutations: mutations, wrapper: wrapper, input: input, roots: roots
  };
  const cls = wrapper.className ? String(wrapper.className) : "";
  return {
    ok: true,
    contact_input_present: true,
    pickerfield_present: cls.indexOf("pickerfield") >= 0,
  };
}"""
_COLLECT_JS: Final = """(expected) => {
  const state = window.__billyDraftSaveScoped;
  if (!state || !state.wrapper || !state.input) {
    return {rows: [], active: "none", mutation_owned_count: 0};
  }
  const mutated = new Set();
  (state.mutations || []).forEach((el) => {
    if (el && el.nodeType === 1) {
      mutated.add(el);
    }
  });
  const unique = [];
  const seen = new Set();
  const allowed = (state.roots || [state.wrapper]).filter((root) => {
    return root && root.tagName !== "BODY" && root.tagName !== "HTML";
  });
  const inside = (el) => {
    return allowed.some((root) => root === el || (root.contains && root.contains(el)));
  };
  const add = (el) => {
    if (!el || el.nodeType !== 1 || el === state.input || seen.has(el)) {
      return;
    }
    if (el.tagName === "BODY" || el.tagName === "HTML" || el.tagName === "HEAD") {
      return;
    }
    if (!inside(el)) {
      return;
    }
    seen.add(el);
    unique.push(el);
  };
  mutated.forEach(add);
  unique.slice().forEach((el) => {
    if (!el.querySelectorAll) {
      return;
    }
    el.querySelectorAll("*").forEach(add);
  });
  state.wrapper.querySelectorAll("*").forEach((el) => {
    const role = (el.getAttribute("role") || "").toLowerCase();
    const text = ((el.innerText || el.textContent || "") + "").replace(/^\\s+|\\s+$/g, "");
    if (role === "option" || role === "listbox" || text === "Opret ny"
      || text === "Ingen kontakter fundet." || text === "Dette felt skal udfyldes.") {
      add(el);
    }
  });
  const inputBox = state.input.getBoundingClientRect();
  const pathOf = (el) => {
    const rows = [];
    let node = el;
    while (node && rows.length < 8 && node.tagName !== "BODY" && node.tagName !== "HTML") {
      const cls = (node.className ? String(node.className) : "");
      const role = (node.getAttribute("role") || "").toLowerCase();
      let token = "other";
      if (cls.indexOf("pickerfield") >= 0) {
        token = "pickerfield";
      } else if (node === state.input || node.getAttribute("name") === "contact") {
        token = "input";
      } else if (role === "listbox" || role === "list") {
        token = "list";
      } else if (role === "option") {
        token = "option";
      } else if (node.tagName === "NAV" || role === "navigation") {
        token = "nav";
      } else if (node.tagName === "HEADER") {
        token = "header";
      }
      rows.push(token);
      node = node.parentElement;
    }
    return rows;
  };
  const exactOf = (text) => {
    if (text === "Dette felt skal udfyldes.") {
      return "validation";
    }
    if (text === "Ingen kontakter fundet.") {
      return "empty_list";
    }
    if (text === "Opret ny") {
      return "opret_ny";
    }
    if (expected && text === expected) {
      return "option";
    }
    return "none";
  };
  const rows = [];
  for (const el of unique) {
    const style = window.getComputedStyle(el);
    const box = el.getBoundingClientRect();
    const visible = style.display !== "none" && style.visibility !== "hidden"
      && box.width > 0 && box.height > 0;
    const text = ((el.innerText || el.textContent || "") + "").replace(/^\\s+|\\s+$/g, "");
    const path = pathOf(el);
    const owned = path.indexOf("pickerfield") >= 0 || path.indexOf("list") >= 0
      || (box.top - inputBox.bottom >= -4 && box.left - inputBox.left > -20
        && box.left - inputBox.left < inputBox.width + 40);
    const mutationOwned = mutated.has(el);
    const exact = exactOf(text);
    const compact = box.width > 0 && box.width <= 400 && box.height > 0 && box.height <= 80;
    const keep = exact !== "none" || owned || (mutationOwned && compact);
    if (!visible && !mutationOwned) {
      continue;
    }
    if (!keep) {
      continue;
    }
    if (path.indexOf("nav") >= 0 && exact !== "opret_ny" && !owned) {
      continue;
    }
    const disabled = el.disabled === true || el.getAttribute("aria-disabled") === "true";
    const interactive = visible && !disabled && (
      el.tabIndex >= 0
      || ["A", "BUTTON", "LI"].indexOf(el.tagName) >= 0
      || !!el.getAttribute("role")
    );
    rows.push({
      tag: el.tagName,
      role: el.getAttribute("role") || "",
      visible: visible,
      interactive: interactive,
      exact_match: exact,
      dx: Math.round(box.left - inputBox.left),
      dy: Math.round(box.top - inputBox.top),
      w: Math.round(box.width),
      h: Math.round(box.height),
      z: style.zIndex,
      path: path,
      is_mutation_owned: mutationOwned,
    });
  }
  const rank = {"option": 0, "opret_ny": 1, "validation": 2, "empty_list": 3, "none": 4};
  rows.sort((a, b) => (rank[a.exact_match] || 4) - (rank[b.exact_match] || 4));
  if (rows.length > 16) {
    rows.length = 16;
  }
  const active = document.activeElement;
  let activeCategory = "none";
  if (active === state.input) {
    activeCategory = "contact_input";
  } else if (active && ((active.innerText || "").replace(
    /^\\s+|\\s+$/g, "") === "Gem som kladde")) {
    activeCategory = "gem_button";
  } else if (active && (active.getAttribute("role") || "") === "option") {
    activeCategory = "option";
  } else if (active && ((active.innerText || "").replace(/^\\s+|\\s+$/g, "") === "Opret ny")) {
    activeCategory = "opret_ny";
  } else if (active) {
    activeCategory = "other";
  }
  if (state.observer) {
    state.observer.disconnect();
  }
  window.__billyDraftSaveScoped = null;
  return {rows: rows, active: activeCategory, mutation_owned_count: mutated.size};
}"""


def _as_str_map(value: object) -> dict[str, object] | None:
    if not isinstance(value, dict):
        return None
    return cast(dict[str, object], value)


def _int_count(raw: object) -> int:
    return raw if isinstance(raw, int) and raw >= 0 else 0


def _tag_token(raw: object) -> str:
    if not isinstance(raw, str) or raw == "":
        return "other"
    token = raw.upper()
    if token.isalnum() and 1 <= len(token) <= 12:
        return token
    return "other"


def _role_token(raw: object) -> str:
    if not isinstance(raw, str) or raw == "":
        return "none"
    lowered = raw.lower()
    if lowered in ROLE_TOKENS:
        return lowered
    return "other"


def _exact_match_token(raw: object) -> ExactMatch:
    if raw in EXACT_MATCHES:
        return cast(ExactMatch, raw)
    return "none"


def _active_token(raw: object) -> ActiveCategory:
    if raw in ACTIVE_CATEGORIES:
        return cast(ActiveCategory, raw)
    return "none"


def _unique_action_token(raw: object) -> UniqueAction:
    if raw in UNIQUE_ACTIONS:
        return cast(UniqueAction, raw)
    return "none"


def _path_tokens(raw: object) -> list[str]:
    if not isinstance(raw, list):
        return []
    tokens: list[str] = []
    for item in cast(list[object], raw):
        if len(tokens) >= PATH_CAP:
            break
        if item in PATH_TOKENS:
            tokens.append(str(item))
        else:
            tokens.append("other")
    return tokens


def _box_of(
    raw: Mapping[str, object] | None, dx: object, dy: object, w: object, h: object
) -> dict[str, int]:
    source: dict[str, object] = dict(raw) if raw is not None else {}
    values: dict[str, object] = {
        "dx": source.get("dx", dx),
        "dy": source.get("dy", dy),
        "w": source.get("w", w),
        "h": source.get("h", h),
    }
    box: dict[str, int] = {}
    for key in ("dx", "dy", "w", "h"):
        value: object = values[key]
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            box[key] = 0
            continue
        box[key] = int(round(float(value)))
    return box


def _z_index(raw: object) -> int | Literal["auto"]:
    if isinstance(raw, int):
        return raw
    if isinstance(raw, str) and raw.lstrip("-").isdigit():
        return int(raw)
    return "auto"


def sanitize_scoped_row(raw: Mapping[str, object]) -> dict[str, object]:
    """Allowlisted scoped row. Drops raw text and names."""

    box_map = _as_str_map(raw.get("box"))
    return {
        "tag": _tag_token(raw.get("tag")),
        "role": _role_token(raw.get("role")),
        "visible": raw.get("visible") is True,
        "interactive": raw.get("interactive") is True,
        "exact_match": _exact_match_token(raw.get("exact_match")),
        "box": _box_of(box_map, raw.get("dx"), raw.get("dy"), raw.get("w"), raw.get("h")),
        "z_index": _z_index(raw.get("z_index", raw.get("z"))),
        "ownership_path": _path_tokens(raw.get("ownership_path", raw.get("path"))),
        "is_mutation_owned": raw.get("is_mutation_owned") is True,
    }


def row_owned_by_picker(row: Mapping[str, object]) -> bool:
    """True when the row belongs to the Kunde picker, not the sidebar."""

    path = row.get("ownership_path")
    tokens = [item for item in cast(list[object], path)] if isinstance(path, list) else []
    if "nav" in tokens and "pickerfield" not in tokens and "list" not in tokens:
        return False
    box = _as_str_map(row.get("box"))
    if box is not None:
        dx: object = box.get("dx")
        if isinstance(dx, (int, float)) and dx < -80:
            return False
    return "pickerfield" in tokens or "list" in tokens


def unique_action_from(rows: Sequence[Mapping[str, object]]) -> tuple[UniqueAction, bool]:
    """Derive at most one picker-owned action from scoped rows."""

    options: list[Mapping[str, object]] = []
    footers: list[Mapping[str, object]] = []
    for row in rows:
        if row.get("visible") is not True:
            continue
        if not row_owned_by_picker(row):
            continue
        if row.get("exact_match") == "option" and row.get("role") == "option":
            options.append(row)
        elif row.get("exact_match") == "opret_ny":
            footers.append(row)
    if len(options) == 1:
        return "existing_option", True
    if len(options) == 0 and len(footers) == 1:
        return "inline_opret_ny", True
    return "none", False


def proved_bind_from(payload: Mapping[str, object]) -> ProvedBind:
    if payload.get("gem_clicked") is not True:
        return "none"
    if payload.get("invoice_persisted") is True:
        return "none"
    if payload.get("unique_action") != "existing_option":
        return "none"
    if payload.get("unique_action_owned_by_picker") is not True:
        return "none"
    if payload.get("proved_bind") != "draft_save_scoped_existing_option":
        return "none"
    return "draft_save_scoped_existing_option"


def _row_is_present(value: object) -> bool:
    row = _as_str_map(value)
    if row is None:
        return False
    if any(key not in row for key in ROW_KEYS):
        return False
    if not isinstance(row.get("visible"), bool) or not isinstance(row.get("interactive"), bool):
        return False
    if row.get("exact_match") not in EXACT_MATCHES:
        return False
    if row.get("role") not in ROLE_TOKENS:
        return False
    path = row.get("ownership_path")
    if not isinstance(path, list):
        return False
    for item in cast(list[object], path):
        if item not in PATH_TOKENS:
            return False
    box = _as_str_map(row.get("box"))
    if box is None:
        return False
    for key in ("dx", "dy", "w", "h"):
        if not isinstance(box.get(key), int):
            return False
    return isinstance(row.get("is_mutation_owned"), bool)


def _key_is_present(payload: Mapping[str, object], key: ScopedKey) -> bool:
    value = payload.get(key)
    match key:
        case (
            "gem_clicked"
            | "invoice_persisted"
            | "contact_input_present"
            | "pickerfield_present"
            | "unique_action_owned_by_picker"
        ):
            return isinstance(value, bool)
        case "active_element_category":
            return value in ACTIVE_CATEGORIES
        case "mutation_owned_count":
            return isinstance(value, int) and value >= 0
        case "scoped_rows":
            return isinstance(value, list) and all(
                _row_is_present(item) for item in cast(list[object], value)
            )
        case "unique_action":
            return value in UNIQUE_ACTIONS
        case "proved_bind":
            return value in PROVED_BIND_TOKENS
        case "missing_keys":
            return isinstance(value, list)


def draft_save_scoped_missing_keys(payload: Mapping[str, object]) -> list[str]:
    """Keys the scoped dump requires that this payload does not record."""

    if "gem_clicked" not in payload:
        return list(REQUIRED_DRAFT_SAVE_SCOPED_KEYS)
    return [key for key in REQUIRED_DRAFT_SAVE_SCOPED_KEYS if not _key_is_present(payload, key)]


def empty_draft_save_scoped() -> dict[str, object]:
    """Structurally complete scoped keys before a live inspect."""

    return {
        "gem_clicked": False,
        "invoice_persisted": False,
        "contact_input_present": False,
        "pickerfield_present": False,
        "active_element_category": "none",
        "mutation_owned_count": 0,
        "scoped_rows": [],
        "unique_action": "none",
        "unique_action_owned_by_picker": False,
        "proved_bind": "none",
        "missing_keys": [],
    }


def _create_path_open(page: Page) -> bool:
    try:
        path = urlsplit(page.url).path
    except Exception:
        return False
    return bool(_CREATE_PATH.match(path))


def apply_draft_save_scoped_dump(
    payload: Mapping[str, object],
    *,
    dump_path: Path | None = None,
) -> dict[str, object]:
    """Copy allowlisted keys and write the owner-only summary."""

    result = empty_draft_save_scoped()
    result["gem_clicked"] = payload.get("gem_clicked") is True
    result["invoice_persisted"] = payload.get("invoice_persisted") is True
    result["contact_input_present"] = payload.get("contact_input_present") is True
    result["pickerfield_present"] = payload.get("pickerfield_present") is True
    result["active_element_category"] = _active_token(payload.get("active_element_category"))
    result["mutation_owned_count"] = _int_count(payload.get("mutation_owned_count"))
    rows: list[dict[str, object]] = []
    raw_rows = payload.get("scoped_rows")
    if isinstance(raw_rows, list):
        for item in cast(list[object], raw_rows):
            if len(rows) >= ROW_CAP:
                break
            row = _as_str_map(item)
            if row is None:
                continue
            rows.append(sanitize_scoped_row(row))
    result["scoped_rows"] = rows
    if rows:
        action, owned = unique_action_from(rows)
        result["unique_action"] = action
        result["unique_action_owned_by_picker"] = owned
    else:
        result["unique_action"] = _unique_action_token(payload.get("unique_action"))
        owned = payload.get("unique_action_owned_by_picker") is True
        result["unique_action_owned_by_picker"] = owned
    result["proved_bind"] = proved_bind_from(
        {
            "gem_clicked": result["gem_clicked"],
            "invoice_persisted": result["invoice_persisted"],
            "unique_action": result["unique_action"],
            "unique_action_owned_by_picker": result["unique_action_owned_by_picker"],
            "proved_bind": payload.get("proved_bind"),
        }
    )
    result["missing_keys"] = draft_save_scoped_missing_keys(result)
    if result["proved_bind"] == "none":
        result["code"] = "UI_CHANGED"
        result["message"] = "Billy invoice create has no proved scoped existing-customer bind."
    summary = {key: result.get(key) for key in REQUIRED_DRAFT_SAVE_SCOPED_KEYS}
    write_json(dump_path or DRAFT_SAVE_SCOPED_DUMP, summary)
    return result


async def capture_draft_save_scoped(
    page: Page,
    *,
    tag: str,
    dump_path: Path | None = None,
) -> dict[str, object]:
    """Collect contact-owned rows after one Gem som kladde click. Do not save."""

    payload = empty_draft_save_scoped()
    attached = await page.evaluate(_ATTACH_JS)
    envelope = _as_str_map(attached)
    if envelope is not None and envelope.get("ok") is True:
        payload["contact_input_present"] = envelope.get("contact_input_present") is True
        payload["pickerfield_present"] = envelope.get("pickerfield_present") is True
    tag_ok = tag.startswith("MCP-UI-INV-") and len(tag) == 19
    expected = tag if tag_ok else ""
    clicked = await click_exact(page, _GEM)
    if clicked is None:
        payload["gem_clicked"] = True
        await asyncio.sleep(0.5)
    collected = await page.evaluate(_COLLECT_JS, expected)
    collected_map = _as_str_map(collected)
    if collected_map is not None:
        payload["active_element_category"] = _active_token(collected_map.get("active"))
        payload["mutation_owned_count"] = _int_count(collected_map.get("mutation_owned_count"))
        raw_rows = collected_map.get("rows")
        rows: list[dict[str, object]] = []
        if isinstance(raw_rows, list):
            for item in cast(list[object], raw_rows):
                if len(rows) >= ROW_CAP:
                    break
                row = _as_str_map(item)
                if row is None:
                    continue
                rows.append(sanitize_scoped_row(row))
        payload["scoped_rows"] = rows
    if payload["gem_clicked"] is True:
        payload["invoice_persisted"] = not _create_path_open(page)
        action, owned = unique_action_from(cast(list[Mapping[str, object]], payload["scoped_rows"]))
        payload["unique_action"] = action
        payload["unique_action_owned_by_picker"] = owned
        if action == "existing_option" and owned and payload["invoice_persisted"] is False:
            payload["proved_bind"] = "draft_save_scoped_existing_option"
    return apply_draft_save_scoped_dump(payload, dump_path=dump_path)


def draft_save_scoped_dump_is_delivered(path: Path | None = None) -> bool:
    """True when the owner dump already recorded the scoped inspect."""

    target = path or DRAFT_SAVE_SCOPED_DUMP
    if not target.is_file():
        return False
    try:
        raw = json.loads(target.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return False
    if not isinstance(raw, dict):
        return False
    return draft_save_scoped_missing_keys(cast(dict[str, object], raw)) == []


def draft_save_scoped_dump_json(payload: Mapping[str, object]) -> str:
    """Stable JSON for leak checks. Never includes source or URLs."""

    return json.dumps(dict(payload), sort_keys=True)


__all__ = [
    "DRAFT_SAVE_SCOPED_DUMP",
    "REQUIRED_DRAFT_SAVE_SCOPED_KEYS",
    "apply_draft_save_scoped_dump",
    "capture_draft_save_scoped",
    "draft_save_scoped_dump_is_delivered",
    "draft_save_scoped_dump_json",
    "draft_save_scoped_missing_keys",
    "empty_draft_save_scoped",
    "proved_bind_from",
    "unique_action_from",
]
