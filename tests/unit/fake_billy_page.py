"""In-memory Billy page used by UI write unit tests. Records route, fill, click."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Final, Self

_CHROME: Final[frozenset[str]] = frozenset(
    {
        "Gem",
        "Gem som kladde",
        "Gem ændringer",
        "Opret produkt",
        "Opret ny kassekladde",
        "Opret kontakt",
        "Upload filer",
        "Slet",
        "Mere",
        "Ret",
        "Slet kontakt",
        "Delete",
        "Bekræft",
        "OK",
    }
)


class FakeBillySession:
    """Shared store for one fake browser context. Mutable because it records."""

    def __init__(self, *, live_slug: str = "org-test") -> None:
        self.live_slug = live_slug
        self.starts = 0
        self.gotos: list[str] = []
        self.fills: list[tuple[str, str]] = []
        self.clicks: list[str] = []
        self.files: list[str] = []
        self.page_ids: list[int] = []
        self.records: set[str] = set()
        self.next_page = 0

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
        )

    def get_by_role(self, role: str, *, name: str | re.Pattern[str]) -> FakeBillyLocator:
        del role
        if isinstance(name, re.Pattern):
            label = name.pattern.strip("^$").replace(r"\ ", " ")
        else:
            label = name
        return FakeBillyLocator(self._session, f"role:{label}", click_name=label)

    def get_by_text(self, text: str, *, exact: bool = False) -> FakeBillyLocator:
        del exact
        return FakeBillyLocator(self._session, f"text={text}", query_text=text, click_name=text)

    async def close(self) -> None:
        return None

    async def wait_for_load_state(self, state: str, *, timeout: float | None = None) -> None:
        del state, timeout


class FakeBillyLocator:
    def __init__(
        self,
        session: FakeBillySession,
        selector: str,
        *,
        query_text: str | None = None,
        click_name: str | None = None,
    ) -> None:
        self._session = session
        self._selector = selector
        self._query_text = query_text
        self._click_name = click_name

    @property
    def first(self) -> Self:
        return self

    def nth(self, index: int) -> Self:
        del index
        return self

    async def count(self) -> int:
        if self._query_text is None or self._query_text in _CHROME:
            return 1
        return 1 if self._query_text in self._session.records else 0

    async def is_visible(self) -> bool:
        return True

    async def click(self) -> None:
        label = self._click_name or _click_label(self._selector)
        self._session.clicks.append(label)
        folded = label.casefold()
        if any(token in folded for token in ("gem", "opret", "upload")):
            for _name, value in self._session.fills:
                self._session.records.add(value)
            for path in self._session.files:
                self._session.records.add(Path(path).name)
        if any(token in folded for token in ("slet", "delete", "bekræft")):
            self._session.records.clear()

    async def inner_text(self) -> str:
        return self._click_name or self._query_text or ""

    async def fill(self, value: str) -> None:
        self._session.fills.append((_field_name(self._selector), value))
        self._session.records.add(value)

    async def evaluate(self, expression: str) -> object:
        del expression
        return None

    async def press(self, key: str) -> None:
        del key

    async def press_sequentially(self, text: str) -> None:
        self._session.fills.append((_field_name(self._selector), text))
        self._session.records.add(text)

    async def set_input_files(self, path: str | Path) -> None:
        resolved = str(path)
        self._session.files.append(resolved)
        self._session.records.add(Path(resolved).name)


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
