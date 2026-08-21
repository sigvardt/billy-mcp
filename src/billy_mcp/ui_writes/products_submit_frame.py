"""Owner-only filled-form capture for product create. Production writes nothing."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Protocol

from billy_mcp.models import StableErrorCode, ToolError
from billy_mcp.vision_evidence import live_allowed_vision_frame_dir

_FRAME_NAME: str = "02_before_submit.png"
_PRICE_LABEL: str = "Enhedspris"
_MISSING: str = "Filled product form frame was not captured before submit."
_NAME_MISMATCH: str = "Filled product name is not visible before submit."
_PRICE_MISMATCH: str = "Filled product Enhedspris is not the bound unit price."


class ProductCreateField(Protocol):
    """Visible name or Enhedspris locator used before screenshot."""

    @property
    def first(self) -> ProductCreateField: ...

    async def count(self) -> int: ...

    async def is_visible(self) -> bool: ...

    async def input_value(self) -> str: ...


class ProductCreateFormPage(Protocol):
    """The fill-and-capture surface: name, Enhedspris, and screenshot."""

    def locator(self, selector: str) -> ProductCreateField: ...

    def get_by_label(self, text: str, *, exact: bool = False) -> ProductCreateField: ...


def product_price_matches(shown: str, expected: str) -> bool:
    """True when a visible price field holds the bound unit-price text."""

    left = _numeric_price(shown)
    right = _numeric_price(expected)
    if left is None or right is None:
        return False
    return abs(left - right) < 0.001


def _numeric_price(raw: str) -> float | None:
    text = raw.strip().replace(" ", "").replace("DKK", "").replace("kr.", "")
    text = text.replace(",", ".")
    try:
        return float(text)
    except ValueError:
        return None


async def capture_filled_create_form(
    page: ProductCreateFormPage, *, name: str, price: str
) -> ToolError | None:
    """Write 02_before_submit.png when live-test mode and a pytest /live/ context allow it."""

    dest = live_allowed_vision_frame_dir(os.environ.get("BILLY_VISION_FRAME_DIR", ""))
    if dest is None:
        return None
    name_field = page.locator("input[name='name']")
    shown_name = ""
    if await name_field.count() >= 1:
        shown_name = (await name_field.first.input_value()).strip()
    if shown_name != name:
        return ToolError(code=StableErrorCode.UI_CHANGED, message=_NAME_MISMATCH)
    shown_price = await _read_filled_price(page)
    if not product_price_matches(shown_price, price):
        return ToolError(code=StableErrorCode.UI_CHANGED, message=_PRICE_MISMATCH)
    shot = Path(dest) / _FRAME_NAME
    capture = getattr(page, "screenshot", None)
    if capture is None:
        return ToolError(code=StableErrorCode.UI_CHANGED, message=_MISSING)
    await capture(path=str(shot), full_page=False)
    if not shot.is_file() or shot.stat().st_size <= 0:
        return ToolError(code=StableErrorCode.UI_CHANGED, message=_MISSING)
    return None


async def _read_filled_price(page: ProductCreateFormPage) -> str:
    """Read Enhedspris through the same labeled then named path used to fill it."""

    labeled = page.get_by_label(_PRICE_LABEL, exact=True)
    shown = await _visible_value(labeled)
    if shown is not None:
        return shown
    labeled = page.get_by_label(_PRICE_LABEL)
    shown = await _visible_value(labeled)
    if shown is not None:
        return shown
    named = page.locator("input[name='unitPrice']")
    shown = await _visible_value(named)
    if shown is not None:
        return shown
    return ""


async def _visible_value(control: ProductCreateField) -> str | None:
    if await control.count() < 1:
        return None
    if not await control.first.is_visible():
        return None
    return (await control.first.input_value()).strip()
