"""Prove a real Playwright pointer click on the customer save button."""

from __future__ import annotations

from collections.abc import Callable
from typing import Protocol

from pydantic import JsonValue

_SAVE = "button[data-cy='save-button']"
_HIT_JS = """([x, y]) => {
  const el = document.elementFromPoint(x, y);
  if (!el) return null;
  const save = el.closest("button[data-cy='save-button']");
  if (save) return "save-button";
  const cls = typeof el.className === "string" ? el.className.split(/\\s+/)[0] : "";
  return cls ? `${el.tagName}.${cls}` : el.tagName;
}"""


class _BoxLocator(Protocol):
    @property
    def first(self) -> _BoxLocator: ...

    async def count(self) -> int: ...

    async def is_visible(self) -> bool: ...

    async def is_disabled(self) -> bool: ...

    async def bounding_box(self) -> dict[str, float] | None: ...


class _Mouse(Protocol):
    async def click(self, x: float, y: float) -> None: ...


class ClickPage(Protocol):
    def locator(self, selector: str) -> _BoxLocator: ...

    def on(self, event: str, handler: Callable[[object], None]) -> None: ...

    async def evaluate(self, expression: str, arg: object | None = None) -> object: ...

    @property
    def mouse(self) -> _Mouse: ...


def listen_console_errors(page: ClickPage) -> list[str]:
    errors: list[str] = []

    def _on(message: object) -> None:
        kind = getattr(message, "type", "")
        text = str(getattr(message, "text", "") or "")
        if kind == "error" and "token" not in text.lower() and "password" not in text.lower():
            errors.append(text[:200])

    page.on("console", _on)
    return errors


async def inspect_save_delivery(page: ClickPage) -> dict[str, JsonValue]:
    button = page.locator(_SAVE).first
    visible = await button.count() >= 1 and await button.is_visible()
    disabled = await button.is_disabled() if visible else None
    box = await button.bounding_box() if visible else None
    center_x: float | None = None
    center_y: float | None = None
    hit: str | None = None
    box_payload: JsonValue = None
    if box is not None:
        center_x = box["x"] + box["width"] / 2
        center_y = box["y"] + box["height"] / 2
        raw = await page.evaluate(_HIT_JS, [center_x, center_y])
        hit = raw if isinstance(raw, str) else None
        box_payload = {
            "x": box["x"],
            "y": box["y"],
            "width": box["width"],
            "height": box["height"],
        }
    blocked = (not visible) or bool(disabled) or box is None or hit != "save-button"
    center_payload: JsonValue = (
        [center_x, center_y] if center_x is not None and center_y is not None else None
    )
    return {
        "visible": visible,
        "disabled": disabled,
        "box": box_payload,
        "center": center_payload,
        "hit_target": hit,
        "blocked": blocked,
        "pointer": False,
    }


async def pointer_click_save(page: ClickPage) -> dict[str, JsonValue]:
    """Click the save-button center with the real mouse. Never evaluate-click."""

    delivery = await inspect_save_delivery(page)
    if delivery.get("blocked"):
        return delivery
    center = delivery.get("center")
    if not isinstance(center, list) or len(center) != 2:
        delivery["blocked"] = True
        return delivery
    x = center[0]
    y = center[1]
    if not isinstance(x, (int, float)) or not isinstance(y, (int, float)):
        delivery["blocked"] = True
        return delivery
    await page.mouse.click(float(x), float(y))
    delivery["pointer"] = True
    return delivery
