"""Source lock: live product CUD captures four write frames before pending record."""

from __future__ import annotations

from pathlib import Path

import pytest


def test_live_product_cud_captures_four_write_frames() -> None:
    """Design 10.4: initial, filled form, create result, restored empty list."""

    live = Path("tests/live/test_ui_products_writes.py").read_text(encoding="utf-8")
    form = Path("src/billy_mcp/ui_writes/products_submit.py").read_text(encoding="utf-8")
    start = live.index("async def test_ui_products_create_delete_via_call_tool")
    body = live[start:]
    mode = body.index('BILLY_TEST_MODE", "ui-full"')
    env = body.index("BILLY_VISION_FRAME_DIR")
    before = body.index('frame_dir / "01_before.png"')
    create_exec = body.index("ui_products_create_execute")
    before_submit = body.index("02_before_submit.png")
    after_create = body.index('frame_dir / "03_after_create.png"')
    delete_preview = body.index("ui_products_delete_preview")
    after_delete = body.index('frame_dir / "04_after_delete.png"')
    vision = body.index("write_live_pending_unless_accepted")
    assert mode < env < before < create_exec
    assert create_exec < before_submit
    assert create_exec < after_create < delete_preview
    assert delete_preview < after_delete < vision
    assert 'assert (frame_dir / "02_before_submit.png").is_file()' in body
    assert "write_vision_record" not in body
    assert 'reviewer_verdict="pending_review"' not in body
    assert 'author="live_test"' not in body
    fill_fn = form.index("async def _fill_and_save")
    fill_body = form[fill_fn:]
    fill = fill_body.index("if not await _fill_price")
    shot = fill_body.index("capture_filled_create_form")
    gem = fill_body.index("if not await _click_visible(page, _GEM)")
    assert fill < shot < gem
    assert "price=price" in fill_body[shot : shot + 80]


class _FakeControl:
    def __init__(self, value: str) -> None:
        self._value = value
        self.first = self

    async def count(self) -> int:
        return 0 if self._value == "__missing__" else 1

    async def is_visible(self) -> bool:
        return self._value != "__missing__"

    async def input_value(self) -> str:
        return self._value


class _FakePage:
    def __init__(self, *, name: str, price: str) -> None:
        self._name = name
        self._price = price
        self.wrote: Path | None = None

    def locator(self, selector: str) -> _FakeControl:
        if selector == "input[name='name']":
            return _FakeControl(self._name)
        if selector == "input[name='unitPrice']":
            return _FakeControl(self._price)
        return _FakeControl("__missing__")

    def get_by_label(self, text: str, *, exact: bool = False) -> _FakeControl:
        del exact
        if text == "Enhedspris":
            return _FakeControl(self._price)
        return _FakeControl("__missing__")

    async def screenshot(self, *, path: str, full_page: bool) -> None:
        del full_page
        Path(path).write_bytes(b"png")
        self.wrote = Path(path)


def _allow_dest(monkeypatch: pytest.MonkeyPatch, dest: Path) -> None:
    def _allowed(raw: str, *, base: Path | None = None) -> Path | None:
        del raw, base
        return dest

    monkeypatch.setattr(
        "billy_mcp.ui_writes.products_submit_frame.live_allowed_vision_frame_dir",
        _allowed,
    )


@pytest.mark.asyncio
async def test_capture_rejects_wrong_price_without_screenshot(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Owner 94A4C844: name match is not enough. Empty price must not screenshot."""

    from billy_mcp.models import StableErrorCode
    from billy_mcp.ui_writes.products_submit_frame import capture_filled_create_form

    dest = tmp_path / "run-price"
    dest.mkdir()
    _allow_dest(monkeypatch, dest)
    page = _FakePage(name="MCP-UI-PRD-AAAA1111", price="")
    result = await capture_filled_create_form(page, name="MCP-UI-PRD-AAAA1111", price="1")
    assert result is not None
    assert result.code == StableErrorCode.UI_CHANGED
    assert (dest / "02_before_submit.png").exists() is False
    assert page.wrote is None


@pytest.mark.asyncio
async def test_capture_accepts_normalized_enhedspris(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Bound price 1 matches visible 1,00 before Gem produkt."""

    from billy_mcp.ui_writes.products_submit_frame import capture_filled_create_form

    dest = tmp_path / "run-ok"
    dest.mkdir()
    _allow_dest(monkeypatch, dest)
    page = _FakePage(name="MCP-UI-PRD-BBBB2222", price="1,00")
    result = await capture_filled_create_form(page, name="MCP-UI-PRD-BBBB2222", price="1")
    assert result is None
    shot = dest / "02_before_submit.png"
    assert shot.is_file() and shot.stat().st_size > 0
