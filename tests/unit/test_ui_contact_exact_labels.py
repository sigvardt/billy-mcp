"""Exact visible-text clicks for contact Ret and Slet. Substring Ret is Opret."""

# pyright: reportPrivateUsage=false

from __future__ import annotations

import asyncio
import re
from typing import Self

from billy_mcp.ui_writes import contacts
from billy_mcp.ui_writes.contacts_persist import click_update_save, wait_for_contact_traffic


class _BlockedPut:
    url = "https://api.billysbilling.com/v2/contacts/abc"
    method = "PUT"
    failure = "blockedbyclient"

    @property
    def request(self) -> _BlockedPut:
        return self


class _Button:
    def __init__(
        self,
        text: str,
        *,
        visible: bool = True,
        near_name: bool = False,
        decoy: bool = False,
        save_button: bool = False,
    ) -> None:
        self.text = text
        self.visible = visible
        self.near_name = near_name
        self.decoy = decoy
        self.save_button = save_button

    @property
    def click_id(self) -> str:
        if self.save_button:
            return "Gem-save-button"
        if self.near_name:
            return "Gem-form"
        if self.decoy:
            return "Gem-decoy"
        return self.text


class _Keyboard:
    def __init__(self, page: ContactDetailFake) -> None:
        self._page = page

    async def press(self, key: str) -> None:
        del key

    async def type(self, text: str) -> None:
        self._page.name_value = text


class _Mouse:
    def __init__(self, page: ContactDetailFake) -> None:
        self._page = page

    async def click(self, x: float, y: float) -> None:
        self._page.pointer_clicks.append((x, y))
        if self._page.hit_target != "save-button":
            return
        for button in self._page.buttons:
            if button.save_button:
                self._page.clicks.append(button.click_id)
                if self._page.blocked_put:
                    self._page.emit_blocked_put()
                return


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
        self.name_value: str | None = None
        self.visible_error: str | None = None
        self.save_disabled = False
        self.slet_kontakt_visible = False
        self.confirm_slet_visible = False
        self.url = "https://mit.billy.dk/org-test/contacts/id/customer"
        self.keyboard = _Keyboard(self)
        self.mouse = _Mouse(self)
        self.pointer_clicks: list[tuple[float, float]] = []
        self.hit_target = "save-button"
        self._response_handlers: list[object] = []
        self._request_handlers: list[object] = []
        self._requestfailed_handlers: list[object] = []
        self.blocked_put = False

    async def evaluate(self, expression: str, arg: object | None = None) -> object:
        del expression, arg
        return self.hit_target

    def locator(self, selector: str) -> _Locator:
        if selector.startswith("text="):
            needle = selector.removeprefix("text=")
            return _Locator(self, substring=needle)
        if "name='name'" in selector and not selector.startswith("xpath"):
            return _Locator(self, name_field=True)
        if "data-cy" in selector and "save-button" in selector:
            return _Locator(self, pool=[item for item in self.buttons if item.save_button])
        if selector in {"[role='alert']", "[role=alert]", ".error", ".form-error"}:
            return _Locator(self, alert=True)
        return _Locator(self, missing=True)

    def on(self, event: str, handler: object) -> None:
        if event == "response":
            self._response_handlers.append(handler)
        elif event == "request":
            self._request_handlers.append(handler)
        elif event == "requestfailed":
            self._requestfailed_handlers.append(handler)

    def emit_blocked_put(self) -> None:
        failed = _BlockedPut()
        for handler in self._request_handlers:
            if callable(handler):
                handler(failed)
        for handler in self._requestfailed_handlers:
            if callable(handler):
                handler(failed)

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
        alert: bool = False,
        matches: list[_Button] | None = None,
        pool: list[_Button] | None = None,
    ) -> None:
        self._page = page
        self._name_field = name_field
        self._missing = missing
        self._alert = alert
        source = pool if pool is not None else page.buttons
        if matches is not None:
            self._matches = matches
        elif name_field or missing:
            self._matches = []
        elif pool is not None and role_name is None and substring is None:
            self._matches = list(pool)
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
        if self._alert:
            return 1 if self._page.visible_error else 0
        if self._missing:
            return 0
        return len(self._matches)

    async def is_visible(self) -> bool:
        if self._name_field:
            return self._page.name_visible
        if self._alert:
            return bool(self._page.visible_error)
        if self._missing or not self._matches:
            return False
        return self._matches[0].visible

    async def input_value(self) -> str:
        if self._name_field:
            return self._page.name_value or ""
        return ""

    async def is_disabled(self) -> bool:
        return self._page.save_disabled

    async def bounding_box(self) -> dict[str, float] | None:
        if self._missing or not self._matches:
            return None
        if not self._matches[0].save_button or not self._matches[0].visible:
            return None
        return {"x": 10.0, "y": 20.0, "width": 80.0, "height": 24.0}

    async def get_attribute(self, name: str) -> str | None:
        if name in {"disabled", "aria-disabled"} and self._matches:
            return "true" if self._page.save_disabled else None
        return None

    async def click(self) -> None:
        if self._missing or not self._matches:
            return
        label = self._matches[0].text
        self._page.clicks.append(self._matches[0].click_id)
        if label.startswith("MCP-UI-C-"):
            self._page.url = "https://mit.billy.dk/org-test/contacts/id/customer"
        elif label == "Ret":
            self._page.name_visible = not self._page.name_visible
            if self._page.name_value is None:
                self._page.name_value = "MCP-UI-C-AAAA"
        elif self._matches[0].save_button and self._page.visible_error is None:
            pass
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
        if self._name_field and "parentElement" in expression and "Gem" in expression:
            for button in self._page.buttons:
                if button.near_name and button.text in {"Gem", "Gem ændringer"}:
                    self._page.clicks.append(button.click_id)
                    return True
            return False
        return None

    async def press(self, key: str) -> None:
        del key

    async def press_sequentially(self, text: str) -> None:
        del text

    async def inner_text(self) -> str:
        if self._alert:
            return self._page.visible_error or ""
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
    clicked = asyncio.run(contacts._click_dialog_save(page))
    assert clicked is True
    assert page.clicks == ["Gem"]
    assert page.clicks[-1] == "Gem"


def test_exact_slet_runs_after_slet_kontakt() -> None:
    page = ContactDetailFake()
    deleted = asyncio.run(contacts._confirm_delete_customer(page))
    assert deleted is True
    assert page.clicks == ["Mere", "Slet kontakt", "Ja, slet"]


def _edit_page_with_decoy_last_gem(*, near_name: bool) -> ContactDetailFake:
    page = ContactDetailFake()
    page.name_visible = True
    page.buttons.append(_Button("Virksomhed"))
    if near_name:
        page.buttons.append(_Button("Gem", near_name=True))
    page.buttons.append(_Button("Gem", decoy=True))
    return page


def test_save_clicks_name_field_gem_not_last_decoy() -> None:
    page = _edit_page_with_decoy_last_gem(near_name=True)
    clicked = asyncio.run(click_update_save(page))
    assert clicked is False
    assert page.clicks == []


def test_save_clicks_data_cy_save_button_not_last_decoy() -> None:
    page = ContactDetailFake()
    page.name_visible = True
    page.buttons.append(_Button("Gem", save_button=True))
    page.buttons.append(_Button("Gem", decoy=True))
    clicked = asyncio.run(click_update_save(page))
    assert clicked is True
    assert page.clicks == ["Gem-save-button"]


def test_update_returns_not_found_when_rename_missing_from_list() -> None:
    page = ContactDetailFake()
    page.url = "https://mit.billy.dk/org-test/clients"
    page.buttons.append(_Button("MCP-UI-C-AAAA"))
    page.links.append(_Button("MCP-UI-C-AAAA"))
    page.buttons.append(_Button("Virksomhed"))
    page.buttons.append(_Button("Gem", decoy=True))
    result = asyncio.run(
        contacts._update_customer(page, "org-test", "MCP-UI-C-AAAA", "MCP-UI-C-AAAA-U")
    )
    assert isinstance(result, contacts.ToolError)
    assert result.code == contacts.StableErrorCode.UI_CHANGED
    assert "pointer-reachable" in result.message


def _persist_edit_page(*, save_button: bool, xpath_gem: bool) -> ContactDetailFake:
    page = ContactDetailFake()
    page.url = "https://mit.billy.dk/org-test/clients"
    page.name_value = "MCP-UI-C-AAAA"
    page.buttons.append(_Button("MCP-UI-C-AAAA"))
    page.links.append(_Button("MCP-UI-C-AAAA"))
    page.buttons.append(_Button("Virksomhed"))
    if save_button:
        page.buttons.append(_Button("Gem", save_button=True))
    if xpath_gem:
        page.buttons.append(_Button("Gem", near_name=True))
    return page


def test_update_sets_name_with_keyboard_before_save_when_fill_does_not_stick() -> None:
    page = _persist_edit_page(save_button=True, xpath_gem=False)
    result = asyncio.run(
        contacts._update_customer(page, "org-test", "MCP-UI-C-AAAA", "MCP-UI-C-AAAA-U")
    )
    assert page.name_value == "MCP-UI-C-AAAA-U"
    assert page.clicks.count("Gem-save-button") == 1
    assert isinstance(result, contacts.ToolError)
    assert result.code == contacts.StableErrorCode.UI_CHANGED
    assert "interface_status" in result.details
    assert result.details["interface_status"] is None


def test_update_clicks_only_data_cy_save_button() -> None:
    page = _persist_edit_page(save_button=True, xpath_gem=True)
    asyncio.run(contacts._update_customer(page, "org-test", "MCP-UI-C-AAAA", "MCP-UI-C-AAAA-U"))
    assert "Gem-form" not in page.clicks
    assert "Gem-decoy" not in page.clicks
    assert page.clicks.count("Gem-save-button") == 1


def test_update_returns_ui_changed_when_visible_error_after_save() -> None:
    page = _persist_edit_page(save_button=True, xpath_gem=False)
    page.visible_error = "Navn er ugyldigt"
    result = asyncio.run(
        contacts._update_customer(page, "org-test", "MCP-UI-C-AAAA", "MCP-UI-C-AAAA-U")
    )
    assert isinstance(result, contacts.ToolError)
    assert result.code == contacts.StableErrorCode.UI_CHANGED
    assert result.details["after"]["visible_error"] == "Navn er ugyldigt"
    assert result.details["before"]["name_value"] == "MCP-UI-C-AAAA-U"


def test_update_returns_ui_changed_when_contact_xhr_missing() -> None:
    page = _persist_edit_page(save_button=True, xpath_gem=False)
    result = asyncio.run(
        contacts._update_customer(page, "org-test", "MCP-UI-C-AAAA", "MCP-UI-C-AAAA-U")
    )
    assert isinstance(result, contacts.ToolError)
    assert result.code == contacts.StableErrorCode.UI_CHANGED
    assert result.details.get("interface_status") is None
    assert "/clients" not in page.url or "contacts" in page.url


def test_wait_for_contact_traffic_sees_late_put_response() -> None:
    events: list[object] = []

    class _OkPut:
        url = "https://api.billysbilling.com/v2/contacts/abc"
        status = 200
        request = type("Req", (), {"method": "PUT", "post_data": "MCP-UI-C-AAAA-U"})()

    async def _run() -> object:
        async def _arrive() -> None:
            await asyncio.sleep(0.05)
            events.append(_OkPut())

        asyncio.create_task(_arrive())
        return await wait_for_contact_traffic(
            events, old_name="MCP-UI-C-AAAA", new_name="MCP-UI-C-AAAA-U", attempts=20
        )

    traffic = asyncio.run(_run())
    assert isinstance(traffic, dict)
    assert traffic["interface_status"] == 200
    assert traffic["interface_method"] == "PUT"
    assert traffic["name_in_request"] == "new"


def test_update_records_blocked_put_when_no_response() -> None:
    page = _persist_edit_page(save_button=True, xpath_gem=False)
    page.blocked_put = True
    result = asyncio.run(
        contacts._update_customer(page, "org-test", "MCP-UI-C-AAAA", "MCP-UI-C-AAAA-U")
    )
    assert isinstance(result, contacts.ToolError)
    assert result.code == contacts.StableErrorCode.UI_CHANGED
    assert result.details.get("interface_method") == "PUT"
    assert result.details.get("interface_path_class") == "/v2/contacts/id"
    assert result.details.get("failure_class") == "blockedbyclient"


def test_update_uses_pointer_click_not_locator_click() -> None:
    page = _persist_edit_page(save_button=True, xpath_gem=False)
    asyncio.run(contacts._update_customer(page, "org-test", "MCP-UI-C-AAAA", "MCP-UI-C-AAAA-U"))
    assert page.pointer_clicks == [(50.0, 32.0)]
    assert page.clicks.count("Gem-save-button") == 1


def test_update_fails_closed_when_overlay_covers_save_button() -> None:
    page = _persist_edit_page(save_button=True, xpath_gem=False)
    page.hit_target = "DIV.overlay"
    result = asyncio.run(
        contacts._update_customer(page, "org-test", "MCP-UI-C-AAAA", "MCP-UI-C-AAAA-U")
    )
    assert page.pointer_clicks == []
    assert "Gem-save-button" not in page.clicks
    assert isinstance(result, contacts.ToolError)
    assert result.code == contacts.StableErrorCode.UI_CHANGED
    assert result.details["click_delivery"]["hit_target"] == "DIV.overlay"
