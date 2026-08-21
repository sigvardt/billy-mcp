"""Official invoice-list Opret faktura landing capture.

Never stores source, URLs, locators, ids, query values, or customer names.
"""

from __future__ import annotations

import asyncio
import re
from pathlib import Path
from typing import Protocol

from billy_mcp.ui_writes.invoices_customer_detail_prebind import (
    classify_heading,
    classify_href,
)
from billy_mcp.ui_writes.invoices_list_opret_faktura_keys import (
    HEADING_TOKENS,
    LIST_OPRET_FAKTURA_DUMP,
    REQUIRED_LIST_OPRET_FAKTURA_KEYS,
    apply_list_opret_faktura_dump,
    classify_list_path,
    empty_list_opret_faktura,
    list_opret_faktura_dump_is_delivered,
    list_opret_faktura_dump_json,
    list_opret_faktura_missing_keys,
    proved_bind_from,
    unique_action_from,
)

AriaExpandedToken = str
_OPRET = "Opret faktura"


class _CountLocator(Protocol):
    @property
    def first(self) -> _CountLocator: ...

    async def count(self) -> int: ...

    async def is_visible(self) -> bool: ...

    async def click(self) -> None: ...

    async def inner_text(self) -> str: ...

    async def get_attribute(self, name: str) -> str | None: ...

    async def input_value(self) -> str: ...


class _CountPage(Protocol):
    @property
    def url(self) -> str: ...

    def locator(self, selector: str) -> _CountLocator: ...

    def get_by_role(self, role: str, **kwargs: object) -> _CountLocator: ...


async def _visible_count(locator: _CountLocator) -> int:
    try:
        total = await locator.count()
    except (TimeoutError, RuntimeError, AttributeError):
        return 0
    if total < 1:
        return 0
    try:
        visible = await locator.first.is_visible()
    except (TimeoutError, RuntimeError, AttributeError):
        return 0
    return 1 if total == 1 and visible else total


async def _exact_role_count(page: _CountPage, role: str, label: str) -> int:
    return await _visible_count(page.get_by_role(role, name=re.compile(rf"^{re.escape(label)}$")))


async def _heading_token(page: _CountPage) -> str:
    heading = page.locator("h1")
    try:
        if await heading.count() < 1:
            return "none"
        token = classify_heading(await heading.first.inner_text())
    except (TimeoutError, RuntimeError, AttributeError):
        return "none"
    return token if token in HEADING_TOKENS else "none"


async def _contact_state(page: _CountPage, tag: str) -> tuple[bool, int, bool, AriaExpandedToken]:
    field = page.locator("input[name='contact']")
    try:
        if await field.count() < 1:
            return False, 0, False, "missing"
        value = await field.first.input_value()
        expanded = await field.first.get_attribute("aria-expanded")
    except (TimeoutError, RuntimeError, AttributeError):
        return False, 0, False, "missing"
    match expanded:
        case "true":
            token = "true"
        case "false":
            token = "false"
        case _:
            token = "missing"
    return True, len(value), value == tag, token


async def capture_list_opret_faktura(
    page: _CountPage,
    *,
    tag: str,
    dump_path: Path | None = None,
) -> dict[str, object]:
    """Inspect the official list Opret faktura. Clicks only when unique."""

    payload = empty_list_opret_faktura()
    payload["list_path_class"] = classify_list_path(page.url)
    button_count = await _exact_role_count(page, "button", _OPRET)
    link_count = await _exact_role_count(page, "link", _OPRET)
    if button_count == 1 and link_count == 0:
        payload["list_opret_faktura_role"] = "button"
        payload["exact_list_opret_faktura_count"] = 1
    elif link_count == 1 and button_count == 0:
        payload["list_opret_faktura_role"] = "link"
        payload["exact_list_opret_faktura_count"] = 1
    else:
        payload["list_opret_faktura_role"] = "none"
        payload["exact_list_opret_faktura_count"] = button_count + link_count
    if payload["exact_list_opret_faktura_count"] == 1:
        role = str(payload["list_opret_faktura_role"])
        control = page.get_by_role(role, name=re.compile(rf"^{re.escape(_OPRET)}$"))
        try:
            if await control.count() >= 1 and await control.first.is_visible():
                await control.first.click()
                payload["clicked_list_opret_faktura"] = True
                await asyncio.sleep(0.5)
        except (TimeoutError, RuntimeError, AttributeError):
            payload["clicked_list_opret_faktura"] = False
    if payload["clicked_list_opret_faktura"] is True:
        dest_path, dest_query = classify_href(page.url)
        payload["destination_path_class"] = dest_path
        payload["destination_query_token_class"] = dest_query
        payload["destination_heading_token"] = await _heading_token(page)
        present, value_len, matches, expanded = await _contact_state(page, tag)
        payload["contact_input_present"] = present
        payload["contact_input_value_len"] = value_len
        payload["contact_input_matches_tag"] = matches
        payload["aria_expanded_token"] = expanded
        payload["option_role_count"] = await _visible_count(page.get_by_role("option"))
    return apply_list_opret_faktura_dump(payload, dump_path=dump_path)


__all__ = [
    "LIST_OPRET_FAKTURA_DUMP",
    "REQUIRED_LIST_OPRET_FAKTURA_KEYS",
    "apply_list_opret_faktura_dump",
    "capture_list_opret_faktura",
    "classify_list_path",
    "empty_list_opret_faktura",
    "list_opret_faktura_dump_is_delivered",
    "list_opret_faktura_dump_json",
    "list_opret_faktura_missing_keys",
    "proved_bind_from",
    "unique_action_from",
]
