"""Invoice Kunde post-click DOM and AX keys (07600147).

Never stores raw names, raw text, URLs, or customer values.
"""

from __future__ import annotations

import asyncio
import hashlib
import json
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Final, Literal, cast

from billy_mcp.ui_writes.invoices_form_page import Page, write_json

PostClickKey = Literal[
    "baseline_input_tag",
    "baseline_wrapper_class_categories",
    "baseline_hidden_subtree_count",
    "click_target",
    "click_count",
    "changed_node_count",
    "changed_nodes",
    "exact_match_count",
    "exact_match_target",
    "kunde_post_click_missing_keys",
]
RoleToken = Literal["option", "listbox", "listitem", "button", "link", "none", "other"]
WrapperCategory = Literal["pickerfield", "ember-view", "text-field", "super-field", "other"]
NodeCategory = Literal[
    "pickerfield",
    "ember-view",
    "list",
    "option",
    "portal",
    "dropdown",
    "menu",
    "other",
]

REQUIRED_KUNDE_POST_CLICK_KEYS: Final[tuple[PostClickKey, ...]] = (
    "baseline_input_tag",
    "baseline_wrapper_class_categories",
    "baseline_hidden_subtree_count",
    "click_target",
    "click_count",
    "changed_node_count",
    "changed_nodes",
    "exact_match_count",
    "exact_match_target",
    "kunde_post_click_missing_keys",
)
WRAPPER_CATEGORIES: Final[frozenset[str]] = frozenset(
    {"pickerfield", "ember-view", "text-field", "super-field", "other"}
)
NODE_CATEGORIES: Final[frozenset[str]] = frozenset(
    {
        "pickerfield",
        "ember-view",
        "list",
        "option",
        "portal",
        "dropdown",
        "menu",
        "other",
    }
)
ROLE_TOKENS: Final[frozenset[str]] = frozenset(
    {"option", "listbox", "listitem", "button", "link", "none", "other"}
)
NODE_ROW_KEYS: Final[tuple[str, ...]] = (
    "tag",
    "role",
    "visible",
    "interactive",
    "class_token_categories",
    "data_attr_names",
    "text_len",
    "text_hash",
    "text_exact_match",
    "box",
    "z_index",
    "ownership_path",
    "ax_name_hash",
    "ax_name_exact_match",
)
CHANGED_NODE_CAP: Final = 16
PATH_CAP: Final = 8
KUNDE_POST_CLICK_DUMP: Final = (
    Path.home() / ".local" / "share" / "billy-mcp" / "inspect-live-invoices-kunde-post-click.json"
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
  const hidden = [];
  const consider = (el) => {
    if (!el || el.nodeType !== 1 || el === input) {
      return;
    }
    const style = window.getComputedStyle(el);
    const hiddenish = style.display === "none" || style.visibility === "hidden"
      || el.hidden === true || el.getAttribute("aria-hidden") === "true";
    if (hiddenish) {
      hidden.push(el);
    }
  };
  wrapper.querySelectorAll("*").forEach(consider);
  let sibling = wrapper.nextElementSibling;
  let hops = 0;
  while (sibling && hops < 4) {
    consider(sibling);
    sibling.querySelectorAll("*").forEach(consider);
    sibling = sibling.nextElementSibling;
    hops += 1;
  }
  const controls = wrapper.getAttribute("aria-controls");
  if (controls) {
    const linked = document.getElementById(controls);
    if (linked) {
      consider(linked);
      linked.querySelectorAll("*").forEach(consider);
    }
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
  const roots = [wrapper].concat(hidden);
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
      attributeFilter: ["class", "style", "hidden", "aria-hidden", "aria-expanded"],
    });
  }
  window.__billyKundePostClick = {observer, mutations, wrapper, input};
  const raw = wrapper.className ? String(wrapper.className) : "";
  return {
    ok: true,
    baseline_input_tag: input.tagName,
    wrapper_class_tokens: raw.split(/\\s+/).filter(Boolean),
    baseline_hidden_subtree_count: hidden.length,
  };
}"""
_COLLECT_JS: Final = """() => {
  const state = window.__billyKundePostClick;
  if (!state || !state.wrapper) {
    return {nodes: []};
  }
  const unique = [];
  const seen = new Set();
  const add = (el) => {
    if (!el || el.nodeType !== 1 || el === state.input || seen.has(el)) {
      return;
    }
    seen.add(el);
    unique.push(el);
  };
  (state.mutations || []).forEach(add);
  unique.slice().forEach((el) => {
    if (el.querySelectorAll) {
      el.querySelectorAll("*").forEach(add);
    }
  });
  const pathOf = (el) => {
    const rows = [];
    let node = el.parentElement;
    while (node && rows.length < 8 && node.tagName !== "BODY" && node.tagName !== "HTML") {
      rows.push({tag: node.tagName, role: node.getAttribute("role") || ""});
      node = node.parentElement;
    }
    return rows;
  };
  const nodes = [];
  for (const el of unique) {
    if (nodes.length >= 16) {
      break;
    }
    const style = window.getComputedStyle(el);
    const box = el.getBoundingClientRect();
    const visible = style.display !== "none" && style.visibility !== "hidden"
      && box.width > 0 && box.height > 0;
    const text = ((el.innerText || el.textContent || "") + "").replace(/^\\s+|\\s+$/g, "");
    const ax = ((el.getAttribute("aria-label") || el.getAttribute("title") || "") + "");
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
    const interactive = visible && !disabled && (
      el.tabIndex >= 0
      || ["A", "BUTTON", "LI"].indexOf(el.tagName) >= 0
      || !!el.getAttribute("role")
    );
    nodes.push({
      tag: el.tagName,
      role: el.getAttribute("role") || "",
      visible: visible,
      interactive: interactive,
      class_tokens: raw.split(/\\s+/).filter(Boolean),
      data_attr_names: names,
      text: text,
      ax: ax,
      w: box.width,
      h: box.height,
      z: style.zIndex,
      path: pathOf(el),
    });
  }
  if (state.observer) {
    state.observer.disconnect();
  }
  window.__billyKundePostClick = null;
  return {nodes: nodes};
}"""


def text_hash_for(value: str) -> str:
    """16-char sha256 of the exact comparison string."""

    return hashlib.sha256(value.encode("utf-8")).hexdigest()[:16]


def _as_str_map(value: object) -> dict[str, object] | None:
    if not isinstance(value, dict):
        return None
    return cast(dict[str, object], value)


def _tag_token(raw: object) -> str:
    if not isinstance(raw, str) or raw == "":
        return "other"
    token = raw.upper()
    if token.isalnum() and 1 <= len(token) <= 12:
        return token
    return "other"


def _role_token(raw: object) -> RoleToken:
    if not isinstance(raw, str) or raw == "":
        return "none"
    lowered = raw.lower()
    if lowered in ROLE_TOKENS:
        return cast(RoleToken, lowered)
    return "other"


def _categories(raw: object, allow: frozenset[str]) -> list[str]:
    tokens: list[str] = []
    source: Sequence[object]
    if isinstance(raw, str):
        source = raw.split()
    elif isinstance(raw, list):
        source = cast(list[object], raw)
    else:
        source = []
    for item in source:
        if not isinstance(item, str) or item == "":
            continue
        matched = "other"
        lowered = item.lower()
        for allowed in sorted(allow):
            if allowed != "other" and allowed in lowered:
                matched = allowed
                break
        if matched not in tokens:
            tokens.append(matched)
    tokens.sort()
    return tokens


def _hash_or_empty(value: str) -> str:
    if value == "":
        return ""
    return text_hash_for(value)


def _box_of(raw_w: object, raw_h: object) -> dict[str, float] | None:
    if not isinstance(raw_w, (int, float)) or not isinstance(raw_h, (int, float)):
        return None
    width = round(float(raw_w), 1)
    height = round(float(raw_h), 1)
    if width <= 0 or height <= 0:
        return None
    return {"w": width, "h": height}


def _z_index(raw: object) -> int | Literal["auto"]:
    if isinstance(raw, int):
        return raw
    if isinstance(raw, str) and raw.lstrip("-").isdigit():
        return int(raw)
    return "auto"


def _path_of(raw: object) -> list[dict[str, str]]:
    if not isinstance(raw, list):
        return []
    rows: list[dict[str, str]] = []
    for item in cast(list[object], raw):
        if len(rows) >= PATH_CAP:
            break
        row = _as_str_map(item)
        if row is None:
            continue
        rows.append({"tag": _tag_token(row.get("tag")), "role": _role_token(row.get("role"))})
    return rows


def sanitize_changed_node(raw: Mapping[str, object], expected: str) -> dict[str, object]:
    """Allowlisted node row. Drops raw text and names."""

    text = raw.get("text")
    ax_name = raw.get("ax")
    text_value = text if isinstance(text, str) else ""
    ax_value = ax_name if isinstance(ax_name, str) else ""
    text_len = len(text_value)
    data_names: list[str] = []
    raw_names = raw.get("data_attr_names")
    if isinstance(raw_names, list):
        for item in cast(list[object], raw_names):
            if isinstance(item, str) and item.startswith("data-"):
                data_names.append(item)
    return {
        "tag": _tag_token(raw.get("tag")),
        "role": _role_token(raw.get("role")),
        "visible": raw.get("visible") is True,
        "interactive": raw.get("interactive") is True,
        "class_token_categories": _categories(raw.get("class_tokens"), NODE_CATEGORIES),
        "data_attr_names": data_names,
        "text_len": text_len,
        "text_hash": _hash_or_empty(text_value),
        "text_exact_match": expected != "" and text_value == expected,
        "box": _box_of(raw.get("w"), raw.get("h")),
        "z_index": _z_index(raw.get("z")),
        "ownership_path": _path_of(raw.get("path")),
        "ax_name_hash": _hash_or_empty(ax_value),
        "ax_name_exact_match": expected != "" and ax_value == expected,
    }


def _node_is_present(value: object) -> bool:
    row = _as_str_map(value)
    if row is None:
        return False
    if any(key not in row for key in NODE_ROW_KEYS):
        return False
    if not isinstance(row.get("visible"), bool) or not isinstance(row.get("interactive"), bool):
        return False
    if not isinstance(row.get("text_len"), int) or cast(int, row["text_len"]) < 0:
        return False
    digest = row.get("text_hash")
    ax_digest = row.get("ax_name_hash")
    if not isinstance(digest, str) or (digest != "" and len(digest) != 16):
        return False
    if not isinstance(ax_digest, str) or (ax_digest != "" and len(ax_digest) != 16):
        return False
    if row.get("role") not in ROLE_TOKENS:
        return False
    categories = row.get("class_token_categories")
    if not isinstance(categories, list):
        return False
    for item in cast(list[object], categories):
        if isinstance(item, str) and item not in NODE_CATEGORIES:
            return False
    return True


def _key_is_present(payload: Mapping[str, object], key: PostClickKey) -> bool:
    value = payload.get(key)
    match key:
        case "baseline_input_tag":
            return isinstance(value, str) and value != ""
        case "baseline_wrapper_class_categories":
            return isinstance(value, list) and all(
                isinstance(item, str) and item in WRAPPER_CATEGORIES
                for item in cast(list[object], value)
            )
        case (
            "baseline_hidden_subtree_count"
            | "click_count"
            | "changed_node_count"
            | "exact_match_count"
        ):
            return isinstance(value, int) and value >= 0
        case "click_target":
            return value == "pickerfield"
        case "changed_nodes":
            if not isinstance(value, list):
                return False
            return all(_node_is_present(item) for item in cast(list[object], value))
        case "exact_match_target":
            return isinstance(value, bool)
        case "kunde_post_click_missing_keys":
            return isinstance(value, list)


def kunde_post_click_missing_keys(payload: Mapping[str, object]) -> list[str]:
    """Keys 07600147 requires that this dump does not record."""

    return [key for key in REQUIRED_KUNDE_POST_CLICK_KEYS if not _key_is_present(payload, key)]


def empty_kunde_post_click() -> dict[str, object]:
    """Structurally complete 07600147 keys before a live click."""

    return {
        "baseline_input_tag": "INPUT",
        "baseline_wrapper_class_categories": [],
        "baseline_hidden_subtree_count": 0,
        "click_target": "pickerfield",
        "click_count": 0,
        "changed_node_count": 0,
        "changed_nodes": [],
        "exact_match_count": 0,
        "exact_match_target": False,
        "kunde_post_click_missing_keys": [],
    }


def post_click_dump_is_delivered(path: Path | None = None) -> bool:
    """True when the owner dump already recorded the one wrapper click."""

    target = path or KUNDE_POST_CLICK_DUMP
    if not target.is_file():
        return False
    try:
        raw = json.loads(target.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return False
    payload = _as_str_map(raw)
    if payload is None:
        return False
    if kunde_post_click_missing_keys(payload):
        return False
    return payload.get("click_count") == 1 and payload.get("click_target") == "pickerfield"


def exact_match_count_from_nodes(nodes: Sequence[Mapping[str, object]]) -> int:
    """Count visible interactive nodes that exact-match the tagged customer."""

    count = 0
    for node in nodes:
        if node.get("visible") is not True or node.get("interactive") is not True:
            continue
        if node.get("text_exact_match") is True or node.get("ax_name_exact_match") is True:
            count += 1
    return count


def exact_match_target_from_post_click(payload: Mapping[str, object]) -> bool:
    """True only when exactly one changed node is the tagged customer."""

    count = payload.get("exact_match_count")
    if isinstance(count, int):
        return count == 1
    nodes = payload.get("changed_nodes")
    if not isinstance(nodes, list):
        return False
    typed = [row for item in cast(list[object], nodes) if (row := _as_str_map(item)) is not None]
    return exact_match_count_from_nodes(typed) == 1


def apply_kunde_post_click_dump(
    payload: Mapping[str, object],
    *,
    dump_path: Path | None = None,
) -> dict[str, object]:
    """Copy allowlisted keys and write the owner-only summary."""

    result = empty_kunde_post_click()
    for key in REQUIRED_KUNDE_POST_CLICK_KEYS:
        if key in payload and key != "kunde_post_click_missing_keys":
            result[key] = payload[key]
    nodes_raw = result.get("changed_nodes")
    nodes: list[dict[str, object]] = []
    if isinstance(nodes_raw, list):
        for item in cast(list[object], nodes_raw):
            row = _as_str_map(item)
            if row is None:
                continue
            nodes.append(row)
    result["changed_nodes"] = nodes
    result["changed_node_count"] = len(nodes)
    match_count = exact_match_count_from_nodes(nodes)
    result["exact_match_count"] = match_count
    result["exact_match_target"] = match_count == 1
    result["kunde_post_click_missing_keys"] = kunde_post_click_missing_keys(result)
    if match_count != 1:
        result["code"] = "UI_CHANGED"
        result["message"] = "Billy Kunde post-click dump has no exact interactive match."
    summary = {key: result.get(key) for key in REQUIRED_KUNDE_POST_CLICK_KEYS}
    write_json(dump_path or KUNDE_POST_CLICK_DUMP, summary)
    return result


async def inspect_kunde_post_click(page: Page, expected: str) -> dict[str, object]:
    """Baseline, one pickerfield click, then sanitized changed nodes."""

    payload = empty_kunde_post_click()
    attached = await page.evaluate(_ATTACH_JS)
    envelope = _as_str_map(attached)
    if envelope is None or envelope.get("ok") is not True:
        return apply_kunde_post_click_dump(payload)
    payload["baseline_input_tag"] = _tag_token(envelope.get("baseline_input_tag"))
    payload["baseline_wrapper_class_categories"] = _categories(
        envelope.get("wrapper_class_tokens"),
        WRAPPER_CATEGORIES,
    )
    hidden = envelope.get("baseline_hidden_subtree_count")
    hidden_ok = isinstance(hidden, int) and hidden >= 0
    payload["baseline_hidden_subtree_count"] = hidden if hidden_ok else 0
    wrapper = page.locator("input[name='contact']").locator(
        "xpath=ancestor::*[contains(@class,'pickerfield')][1]"
    )
    if await wrapper.count() < 1 or not await wrapper.first.is_visible():
        return apply_kunde_post_click_dump(payload)
    await wrapper.first.click()
    await asyncio.sleep(0.4)
    payload["click_count"] = 1
    collected = await page.evaluate(_COLLECT_JS)
    collected_map = _as_str_map(collected)
    nodes: list[dict[str, object]] = []
    raw_nodes = collected_map.get("nodes") if collected_map is not None else None
    if isinstance(raw_nodes, list):
        for item in cast(list[object], raw_nodes):
            if len(nodes) >= CHANGED_NODE_CAP:
                break
            row = _as_str_map(item)
            if row is None:
                continue
            nodes.append(sanitize_changed_node(row, expected))
    payload["changed_nodes"] = nodes
    return apply_kunde_post_click_dump(payload)


def post_click_dump_json(payload: Mapping[str, object]) -> str:
    """Stable JSON for leak checks. Never includes source or URLs."""

    return json.dumps(dict(payload), sort_keys=True)
