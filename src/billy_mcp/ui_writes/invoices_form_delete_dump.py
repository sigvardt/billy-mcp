"""Owner-only post-Slet dump. No confirm click."""

from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Final
from urllib.parse import urlsplit

from pydantic import BaseModel, ConfigDict, ValidationError

from billy_mcp.ui_writes.invoices_form_page import Page, persist_hit, write_json

POST_SLET_DUMP: Final = (
    Path.home() / ".local" / "share" / "billy-mcp" / "inspect-live-invoices-post-slet.json"
)
_LABEL_ALLOW: Final = frozenset(
    {
        "annuller",
        "bekræft",
        "gem",
        "gem som kladde",
        "godkend",
        "ja",
        "ja, slet",
        "ja, slet faktura",
        "luk",
        "mere",
        "nej",
        "ok",
        "opdater",
        "slet",
    }
)
_HEADING_ALLOW: Final = frozenset({"rediger fakturakladde", "fakturaer", "faktura", "kladde"})
_CANDIDATE_SCRIPT: Final = """() => {
  const allow = new Set(__ALLOW__);
  const seen = new Set();
  const rows = [];
  const token = (raw) => {
    const text = String(raw || "").trim().toLowerCase();
    if (!text) return "";
    return allow.has(text) ? text : "other";
  };
  const add = (el, role) => {
    if (!el || seen.has(el)) return;
    seen.add(el);
    const box = el.getBoundingClientRect();
    const zRaw = Number.parseInt(window.getComputedStyle(el).zIndex, 10);
    const active = document.activeElement;
    const labels = [];
    el.querySelectorAll("button, a, [role='button']").forEach((node) => {
      const label = token(node.innerText);
      if (label) labels.push(label);
    });
    rows.push({
      role,
      labels,
      geometry: {
        x: Math.round(box.x),
        y: Math.round(box.y),
        w: Math.round(box.width),
        h: Math.round(box.height),
      },
      z_index: Number.isFinite(zRaw) ? zRaw : 0,
      active_contained: Boolean(active && el.contains(active)),
    });
  };
  document.querySelectorAll("[role='dialog']").forEach((el) => add(el, "dialog"));
  document.querySelectorAll("[role='alertdialog']").forEach((el) => add(el, "alertdialog"));
  document.querySelectorAll("[aria-modal='true']").forEach((el) => {
    const role = el.getAttribute("role");
    if (role === "dialog" || role === "alertdialog") return;
    add(el, "aria-modal");
  });
  return rows;
}"""


class OverlayBox(BaseModel):
    """Integer box for one overlay candidate."""

    model_config = ConfigDict(frozen=True, extra="ignore")

    x: int
    y: int
    w: int
    h: int


class OverlayCandidate(BaseModel):
    """One dialog, alertdialog, or aria-modal node. Extra keys dropped."""

    model_config = ConfigDict(frozen=True, extra="ignore")

    role: str
    labels: list[str]
    geometry: OverlayBox
    z_index: int
    active_contained: bool


class OverlayDump(BaseModel):
    """Evaluate envelope. Extra keys dropped."""

    model_config = ConfigDict(frozen=True, extra="ignore")

    rows: list[OverlayCandidate]


class _Active(BaseModel):
    """Sanitized focused-element tag and role."""

    model_config = ConfigDict(frozen=True, extra="ignore")

    tag: str = "none"
    role: str = "none"


async def capture_post_slet(
    page: Page, seen: list[str], start_path: str, hit_tag: str
) -> dict[str, object]:
    """Record scoped overlay candidates after one Slet click."""

    for _ in range(8):
        if any(persist_hit(item, "DELETE") for item in seen):
            break
        if await page.get_by_role("dialog").count() >= 1:
            break
        await asyncio.sleep(0.25)
    candidates = await overlay_candidates(page)
    active = await _active_element(page)
    dump: dict[str, object] = {
        "heading_token": heading_token(await _first_heading(page)),
        "path_class": path_class_from_url(page.url),
        "active_tag": active.tag,
        "active_role": active.role,
        "candidates": candidates,
        "dialog_count": await page.get_by_role("dialog").count(),
        "alertdialog_count": await page.get_by_role("alertdialog").count(),
        "overlay_count": await page.locator("[aria-modal='true']").count(),
        "hit_tag": hit_tag,
        "delete_seen": any(persist_hit(item, "DELETE") for item in seen),
        "navigated": ui_path(page.url) != start_path,
    }
    write_json(POST_SLET_DUMP, dump)
    return dump


async def overlay_candidates(page: Page) -> list[dict[str, object]]:
    """Exact dialog, alertdialog, and remaining aria-modal nodes."""

    allow = "[" + ",".join(f'"{item}"' for item in sorted(_LABEL_ALLOW)) + "]"
    raw: object = await page.evaluate(_CANDIDATE_SCRIPT.replace("__ALLOW__", allow))
    try:
        parsed = OverlayDump.model_validate({"rows": raw})
    except ValidationError:
        return []
    return [row.model_dump() for row in parsed.rows[:16]]


def path_class_from_url(url: str) -> str:
    """Sanitized invoice UI path class. Never stores the org slug or id."""

    path = urlsplit(url).path.rstrip("/")
    if path.endswith("/edit") and "/invoices/" in path:
        return "invoices_edit"
    if path.endswith("/invoices"):
        return "invoices"
    if "/invoices/" in path:
        return "invoices_other"
    return "other"


def heading_token(raw: str) -> str:
    """Allowlisted heading token. Unknown text is other."""

    lowered = raw.strip().lower()
    if not lowered:
        return "none"
    for allowed in sorted(_HEADING_ALLOW, key=len, reverse=True):
        if allowed in lowered:
            return allowed.replace(" ", "_")
    return "other"


def allowlisted_label(raw: str) -> str:
    """Keep known chrome labels. Anything else is other."""

    lowered = raw.strip().lower()
    if lowered in _LABEL_ALLOW:
        return lowered
    return "other"


def ui_path(url: str) -> str:
    """Path without the org slug. Ids become a placeholder."""

    parts = [part for part in urlsplit(url).path.split("/") if part]
    if not parts:
        return "/"
    rest = parts[1:]
    cleaned = ["id" if len(part) >= 16 else part for part in rest]
    return "/" + "/".join(cleaned)


async def _first_heading(page: Page) -> str:
    headings = page.get_by_role("heading")
    if await headings.count() < 1:
        return ""
    first = headings.first
    if not await first.is_visible():
        return ""
    return await first.inner_text()


async def _active_element(page: Page) -> _Active:
    raw = await page.evaluate(
        """() => {
          const el = document.activeElement;
          if (!el) return {tag: "none", role: "none"};
          return {
            tag: String(el.tagName || "none").toLowerCase(),
            role: el.getAttribute("role") || "none",
          };
        }"""
    )
    try:
        return _Active.model_validate(raw)
    except ValidationError:
        return _Active()
