"""In-memory Billy page used by UI write unit tests. Records route, fill, click."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Final, Self, cast

_CHROME: Final[frozenset[str]] = frozenset(
    {
        "Gem",
        "Gem produkt",
        "Gem som kladde",
        "Gem ændringer",
        "Opret produkt",
        "Opret ny kassekladde",
        "Opret kontakt",
        "Opret leverandør",
        "Upload filer",
        "Slet",
        "Mere",
        "Ret",
        "Slet kontakt",
        "Delete",
        "Bekræft",
        "OK",
        "Opdater",
    }
)


class FakeRequest:
    def __init__(self, method: str) -> None:
        self.method = method


class FakeResponse:
    def __init__(self, method: str, url: str, status: int = 200) -> None:
        self.method = method
        self.url = url
        self.status = status
        self.request = FakeRequest(method)

    def json(self) -> dict[str, object]:
        if self.method == "POST" and "/v2/bills" in self.url:
            return {"bills": [{"id": "fake-bill-id"}]}
        return {}


class FakeKeyboard:
    def __init__(self, session: FakeBillySession) -> None:
        self._session = session

    async def press(self, key: str) -> None:
        del key

    async def type(self, text: str) -> None:
        focused = self._session.focused
        if focused is not None:
            await focused.fill(text)


class FakeMouse:
    def __init__(self, session: FakeBillySession, page: FakeBillyPage) -> None:
        self._session = session
        self._page = page

    async def click(self, x: float, y: float) -> None:
        del x, y
        label = self._page.pending_save or "Gem som kladde"
        locator = FakeBillyLocator(
            self._session, f"role:{label}", query_text=label, click_name=label
        )
        await locator.click()


class FakeBillySession:
    """Shared store for one fake browser context. Mutable because it records."""

    def __init__(self, *, live_slug: str = "org-test", keep_modal_after_save: bool = False) -> None:
        self.live_slug = live_slug
        self.keep_modal_after_save = keep_modal_after_save
        self.starts = 0
        self.gotos: list[str] = []
        self.fills: list[tuple[str, str]] = []
        self.clicks: list[str] = []
        self.files: list[str] = []
        self.page_ids: list[int] = []
        self.records: set[str] = set()
        self.next_page = 0
        self.focused: FakeBillyLocator | None = None
        self.response_handlers: list[object] = []
        self.dropdown_options: list[str] = []
        self.modal_open = False

    async def start(self, *_args: object, **_kwargs: object) -> FakeBillyContext:
        self.starts += 1
        return FakeBillyContext(self)

    def has_route(self, fragment: str) -> bool:
        return any(fragment in url for url in self.gotos)

    def has_fill_value(self, value: str) -> bool:
        return any(recorded == value for _name, recorded in self.fills)

    def has_click(self, label: str) -> bool:
        return any(label in click for click in self.clicks)

    def readback_page_count(self) -> int:
        return max(0, len(self.page_ids) - 1)


class FakeBillyContext:
    def __init__(self, session: FakeBillySession) -> None:
        self._session = session

    async def new_page(self) -> FakeBillyPage:
        self._session.next_page += 1
        page_id = self._session.next_page
        self._session.page_ids.append(page_id)
        return FakeBillyPage(self._session, page_id)


class FakeBillyPage:
    def __init__(self, session: FakeBillySession, page_id: int) -> None:
        self._session = session
        self.page_id = page_id
        self.url = "about:blank"
        self.keyboard = FakeKeyboard(session)
        self.mouse = FakeMouse(session, self)
        self.pending_save: str | None = None

    async def goto(self, url: str, *, wait_until: str = "domcontentloaded") -> None:
        del wait_until
        if url.rstrip("/") in {"https://mit.billy.dk", "https://mit.billy.dk/"}:
            url = f"https://mit.billy.dk/{self._session.live_slug}/"
        self.url = url
        self._session.gotos.append(url)

    def locator(self, selector: str) -> FakeBillyLocator:
        if "type='search'" in selector or "placeholder" in selector:
            return FakeBillyLocator(self._session, selector, query_text="__no_search__")
        query = selector.removeprefix("text=") if selector.startswith("text=") else None
        return FakeBillyLocator(
            self._session,
            selector,
            query_text=query,
            click_name=query,
            scope=selector,
        )

    def on(self, event: str, handler: object) -> None:
        if event in {"response", "request", "requestfailed"}:
            self._session.response_handlers.append(handler)

    async def evaluate(self, expression: str, arg: object | None = None) -> object:
        del expression
        items = cast(list[object], arg) if isinstance(arg, list) else []
        if len(items) >= 3 and isinstance(items[2], str):
            self.pending_save = items[2]
            return "draft-save"
        return None

    def get_by_role(
        self,
        role: str,
        *,
        name: str | re.Pattern[str] | None = None,
        exact: bool = False,
    ) -> FakeBillyLocator:
        del exact
        if name is None:
            return FakeBillyLocator(self._session, f"role:{role}")
        if isinstance(name, re.Pattern):
            label = name.pattern.strip("^$").replace(r"\ ", " ")
        else:
            label = name
        if role == "heading" and label == "Opret produkt":
            return FakeBillyLocator(
                self._session,
                f"role:{label}",
                query_text=label,
                click_name=label,
                scope="dialog-heading",
            )
        return FakeBillyLocator(self._session, f"role:{label}", query_text=label, click_name=label)

    def get_by_text(self, text: str, *, exact: bool = False) -> FakeBillyLocator:
        del exact
        return FakeBillyLocator(self._session, f"text={text}", query_text=text, click_name=text)

    def get_by_label(self, text: str, *, exact: bool = False) -> FakeBillyLocator:
        del exact
        mapped = {
            "Leverandør": "input[name='vendor']",
            "Bilagsdato": "input[name='billDate']",
            "Kunde": "input[name='contactId']",
            "Enhedspris": "input[name='unitPrice']",
        }.get(text, f"label:{text}")
        return FakeBillyLocator(self._session, mapped)

    async def close(self) -> None:
        return None

    async def wait_for_load_state(self, state: str, *, timeout: float | None = None) -> None:
        del state, timeout

    async def screenshot(self, **kwargs: object) -> None:
        del kwargs


class FakeBillyLocator:
    def __init__(
        self,
        session: FakeBillySession,
        selector: str,
        *,
        query_text: str | None = None,
        click_name: str | None = None,
        scope: str | None = None,
    ) -> None:
        self._session = session
        self._selector = selector
        self._query_text = query_text
        self._click_name = click_name
        self._scope = scope

    @property
    def last(self) -> Self:
        return self

    @property
    def first(self) -> Self:
        return self

    def nth(self, index: int) -> Self:
        del index
        return self

    async def count(self) -> int:
        if "ds-moved-with-portal" in self._selector and "dropdown-list" not in self._selector:
            return 1 if self._session.modal_open else 0
        if "ModalWrapper" in self._selector or "role='dialog'" in self._selector:
            return 1 if self._session.modal_open else 0
        if self._scope == "dialog-heading":
            return 1 if self._session.modal_open else 0
        if self._query_text == "Gem":
            return 1 if self._session.modal_open else 0
        if (self._scope and _is_dropdown_scope(self._scope)) or _is_dropdown_scope(self._selector):
            if self._query_text is None:
                return 1 if self._session.dropdown_options else 0
            return 1 if self._query_text in self._session.dropdown_options else 0
        if self._query_text is None or self._query_text in _CHROME:
            return 1
        return 1 if self._query_text in self._session.records else 0

    async def is_visible(self) -> bool:
        return True

    async def is_disabled(self) -> bool:
        return False

    async def bounding_box(self) -> dict[str, float] | None:
        return {"x": 0.0, "y": 0.0, "width": 10.0, "height": 10.0}

    def locator(self, selector: str) -> FakeBillyLocator:
        click_name = None
        if "DropdownFooterWrapper" in selector:
            for option in self._session.dropdown_options:
                if option.startswith("Opret"):
                    click_name = option
                    break
        return FakeBillyLocator(self._session, selector, click_name=click_name)

    def filter(self, **_kwargs: object) -> FakeBillyLocator:
        return self

    def get_by_role(
        self, role: str, *, name: str | re.Pattern[str], exact: bool = False
    ) -> FakeBillyLocator:
        del exact
        return FakeBillyPage(self._session, 0).get_by_role(role, name=name)

    def get_by_text(self, text: str, *, exact: bool = False) -> FakeBillyLocator:
        del exact
        return FakeBillyLocator(
            self._session,
            f"{self._selector} >> text={text}",
            query_text=text,
            click_name=text,
            scope=self._selector,
        )

    async def click(self, **_kwargs: object) -> None:
        if "name='" in self._selector:
            self._session.focused = self
        label = self._click_name or _click_label(self._selector)
        self._session.clicks.append(label)
        folded = label.casefold()
        if "opret" in folded:
            self._session.modal_open = True
        if folded == "gem" or folded.startswith("gem "):
            if not self._session.keep_modal_after_save:
                self._session.modal_open = False
        if any(token in folded for token in ("gem", "opret", "upload", "opdater")):
            for _name, value in self._session.fills:
                self._session.records.add(value)
            for path in self._session.files:
                self._session.records.add(Path(path).name)
            for handler in list(self._session.response_handlers):
                if not callable(handler):
                    continue
                handler(FakeResponse("POST", "https://api.billysbilling.com/v2/bills"))
                handler(FakeResponse("GET", "https://api.billysbilling.com/v2/bills/fake-bill-id"))
                handler(FakeResponse("PUT", "https://api.billysbilling.com/v2/bills/fake-bill-id"))
                handler(FakeResponse("POST", "https://api.billysbilling.com/v2/invoices"))
                handler(
                    FakeResponse("PUT", "https://api.billysbilling.com/v2/invoices/fake-invoice-id")
                )
        if any(token in folded for token in ("slet", "delete", "bekræft")):
            self._session.records.clear()
            for handler in list(self._session.response_handlers):
                if callable(handler):
                    handler(
                        FakeResponse(
                            "DELETE", "https://api.billysbilling.com/v2/bills/fake-bill-id"
                        )
                    )

    async def inner_text(self) -> str:
        if self._selector == "h1":
            if any("/inventory" in url for url in self._session.gotos):
                return "Lagermodul"
            return ""
        if _is_dropdown_scope(self._selector) or (
            self._scope is not None and _is_dropdown_scope(self._scope)
        ):
            return "\n".join(self._session.dropdown_options)
        return self._click_name or self._query_text or ""

    async def input_value(self) -> str:
        name = _field_name(self._selector)
        for field, value in reversed(self._session.fills):
            if field == name:
                return value
        return ""

    async def get_attribute(self, name: str) -> str | None:
        if name == "name":
            found = _field_name(self._selector)
            return found if found and not found.startswith(("role:", "text=", "label:")) else None
        return None

    async def fill(self, value: str) -> None:
        self._session.fills.append((_field_name(self._selector), value))
        self._session.records.add(value)
        self._session.focused = self
        self._open_typeahead(value)

    async def evaluate(self, expression: str) -> object:
        del expression
        return None

    async def press(self, key: str) -> None:
        del key

    async def press_sequentially(self, text: str) -> None:
        self._session.fills.append((_field_name(self._selector), text))
        self._session.records.add(text)
        self._open_typeahead(text)

    def _open_typeahead(self, value: str) -> None:
        field = _field_name(self._selector)
        if field == "vendor":
            self._session.dropdown_options = [f'Opret "{value}"', "Opret leverandør"]
        if field in {"contactId", "contact"} or "data-testid='search'" in self._selector:
            self._session.dropdown_options = [value]

    async def set_input_files(self, path: str | Path) -> None:
        resolved = str(path)
        self._session.files.append(resolved)
        self._session.records.add(Path(resolved).name)


def _is_dropdown_scope(selector: str) -> bool:
    tokens = (
        ".ds-dropdown-list",
        "role='listbox'",
        "role='option'",
        '[role="listbox"]',
        '[role="option"]',
    )
    return any(token in selector for token in tokens)


def _click_label(selector: str) -> str:
    if selector.startswith("role:"):
        return selector.removeprefix("role:").strip("^$")
    if selector.startswith("text="):
        return selector.removeprefix("text=")
    return selector


def _field_name(selector: str) -> str:
    match = re.search(r"name='([^']+)'", selector)
    if match:
        return match.group(1)
    if selector.startswith("role:") or selector.startswith("text="):
        return selector
    return selector
