"""Exact visible-text clicks for contact Ret and Slet. Substring Ret is Opret."""

# pyright: reportPrivateUsage=false

from __future__ import annotations

import asyncio
import re
from typing import Self

from billy_mcp.ui_writes import contacts


class _Button:
    def __init__(self, text: str, *, visible: bool = True) -> None:
        self.text = text
        self.visible = visible


class ContactDetailFake:
    """Models the live overview: Opret, Ret, Mere, Gem kommentar. Name hidden."""

    def __init__(self) -> None:
        self.buttons = [
            _Button("Opret"),
            _Button("Ret"),
            _Button("Mere"),
            _Button("Gem kommentar"),
        ]
        self.links: list[_Button] = []
        self.clicks: list[str] = []
        self.name_visible = False
        self.slet_kontakt_visible = False
        self.confirm_slet_visible = False
        self.url = "https://mit.billy.dk/org-test/contacts/id/customer"

    def locator(self, selector: str) -> _Locator:
        if selector.startswith("text="):
            needle = selector.removeprefix("text=")
            return _Locator(self, substring=needle)
        if "name='name'" in selector:
            return _Locator(self, name_field=True)
        return _Locator(self, missing=True)

    def get_by_role(self, role: str, *, name: str | re.Pattern[str]) -> _Locator:
        pool = self.links if role == "link" else self.buttons
        return _Locator(self, role_name=name, pool=pool)

    def get_by_text(self, text: str, *, exact: bool = False) -> _Locator:
        return _Locator(self, substring=text, exact=exact, pool=[*self.buttons, *self.links])

    async def goto(self, url: str, *, wait_until: str) -> None:
        del wait_until
        self.url = url

    async def close(self) -> None:
        return None

    async def wait_for_load_state(self, state: str, *, timeout: float | None = None) -> None:
        del state, timeout


class _Locator:
    def __init__(
        self,
        page: ContactDetailFake,
        *,
        role_name: str | re.Pattern[str] | None = None,
        substring: str | None = None,
        exact: bool = False,
        name_field: bool = False,
        missing: bool = False,
        matches: list[_Button] | None = None,
        pool: list[_Button] | None = None,
    ) -> None:
        self._page = page
        self._name_field = name_field
        self._missing = missing
        source = pool if pool is not None else page.buttons
        if matches is not None:
            self._matches = matches
        elif name_field or missing:
            self._matches = []
        elif isinstance(role_name, re.Pattern):
            self._matches = [item for item in source if role_name.search(item.text)]
        elif isinstance(role_name, str):
            folded = role_name.casefold()
            self._matches = [item for item in source if folded in item.text.casefold()]
        elif substring is not None and exact:
            self._matches = [item for item in source if item.text == substring]
        elif substring is not None:
            folded = substring.casefold()
            self._matches = [item for item in source if folded in item.text.casefold()]
        else:
            self._matches = []

    @property
    def first(self) -> Self:
        return self

    def nth(self, index: int) -> _Locator:
        if index < 0 or index >= len(self._matches):
            return _Locator(self._page, missing=True)
        return _Locator(self._page, matches=[self._matches[index]])

    async def count(self) -> int:
        if self._name_field:
            return 1 if self._page.name_visible else 0
        if self._missing:
            return 0
        return len(self._matches)

    async def is_visible(self) -> bool:
        if self._name_field:
            return self._page.name_visible
        if self._missing or not self._matches:
            return False
        return self._matches[0].visible

    async def click(self) -> None:
        if self._missing or not self._matches:
            return
        label = self._matches[0].text
        self._page.clicks.append(label)
        if label.startswith("MCP-UI-C-"):
            self._page.url = "https://mit.billy.dk/org-test/contacts/id/customer"
        elif label == "Ret":
            self._page.name_visible = not self._page.name_visible
        elif label == "Opret":
            pass
        elif label == "Mere":
            self._page.slet_kontakt_visible = True
            self._page.links.append(_Button("Slet kontakt"))
        elif label == "Slet kontakt":
            self._page.confirm_slet_visible = True
            self._page.buttons.append(_Button("Ja, slet"))
        elif label in {"Slet", "Ja, slet"}:
            self._page.confirm_slet_visible = False

    async def fill(self, value: str) -> None:
        del value

    async def evaluate(self, expression: str) -> object:
        del expression
        return None

    async def press(self, key: str) -> None:
        del key

    async def inner_text(self) -> str:
        if not self._matches:
            return ""
        return self._matches[0].text


def test_substring_text_ret_clicks_opret() -> None:
    page = ContactDetailFake()
    locator = page.locator("text=Ret")
    assert asyncio.run(locator.count()) >= 1
    asyncio.run(locator.first.click())
    assert page.clicks == ["Opret"]
    assert page.name_visible is False


def test_click_named_ret_falls_back_to_opret_when_role_misses() -> None:
    page = ContactDetailFake()
    original_get = page.get_by_role

    def _role_miss(role: str, *, name: str | re.Pattern[str]) -> _Locator:
        if isinstance(name, re.Pattern) and name.pattern == r"^Ret$":
            return _Locator(page, missing=True)
        return original_get(role, name=name)

    page.get_by_role = _role_miss  # type: ignore[method-assign]
    clicked = asyncio.run(contacts._click_named(page, contacts._RET))
    assert clicked is True
    assert page.clicks[0] == "Opret"
    assert page.name_visible is False


def test_exact_ret_opens_name_field() -> None:
    page = ContactDetailFake()
    opened = asyncio.run(contacts._click_exact_label(page, "Ret"))
    assert opened is True
    assert page.clicks == ["Ret"]
    assert page.name_visible is True


def test_update_clicks_ret_only_once_after_name_visible() -> None:
    page = ContactDetailFake()
    asyncio.run(contacts._open_edit_name(page, "MCP-UI-C-NEW"))
    assert page.clicks.count("Ret") == 1
    assert page.name_visible is True


def test_open_named_customer_skips_search_box_and_opens_detail() -> None:
    page = ContactDetailFake()
    page.url = "https://mit.billy.dk/org-test/clients"
    page.buttons.append(_Button("MCP-UI-C-ROW"))
    page.links.append(_Button("MCP-UI-C-ROW"))
    opened = asyncio.run(contacts._open_named_customer(page, "MCP-UI-C-ROW"))
    assert opened is True
    assert "/contacts/" in page.url


def test_exact_gem_does_not_click_gem_kommentar() -> None:
    page = ContactDetailFake()
    page.buttons.append(_Button("Gem"))
    clicked = asyncio.run(contacts._click_exact_label(page, "Gem"))
    assert clicked is True
    assert page.clicks == ["Gem"]


def test_save_clicks_last_exact_gem() -> None:
    page = ContactDetailFake()
    page.buttons.append(_Button("Gem"))
    page.buttons.append(_Button("Gem"))
    clicked = asyncio.run(contacts._click_save(page))
    assert clicked is True
    assert page.clicks == ["Gem"]
    assert page.clicks[-1] == "Gem"


def test_exact_slet_runs_after_slet_kontakt() -> None:
    page = ContactDetailFake()
    deleted = asyncio.run(contacts._confirm_delete_customer(page))
    assert deleted is True
    assert page.clicks == ["Mere", "Slet kontakt", "Ja, slet"]
