"""Persist isolate for Billy customer rename. No API-token client."""

from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable
from typing import Protocol
from urllib.parse import urlsplit

from pydantic import JsonValue

from billy_mcp.models import StableErrorCode, ToolError
from billy_mcp.ui_writes.contacts_click import listen_console_errors, pointer_click_save

_NAME = "input[name='name']"
_SAVE = "button[data-cy='save-button']"
_ERROR_SELECTORS = ("[role='alert']", ".error", ".form-error", ".validation-error")


class _ValueLocator(Protocol):
    @property
    def first(self) -> _ValueLocator: ...

    async def count(self) -> int: ...

    async def is_visible(self) -> bool: ...

    async def click(self) -> None: ...

    async def press(self, key: str) -> None: ...

    async def input_value(self) -> str: ...

    async def is_disabled(self) -> bool: ...

    async def inner_text(self) -> str: ...

    async def bounding_box(self) -> dict[str, float] | None: ...


class _Keyboard(Protocol):
    async def press(self, key: str) -> None: ...

    async def type(self, text: str) -> None: ...


class _Mouse(Protocol):
    async def click(self, x: float, y: float) -> None: ...


class PersistPage(Protocol):
    @property
    def url(self) -> str: ...

    def locator(self, selector: str) -> _ValueLocator: ...

    def on(self, event: str, handler: Callable[[object], None]) -> None: ...

    async def evaluate(self, expression: str, arg: object | None = None) -> object: ...

    @property
    def keyboard(self) -> _Keyboard: ...

    @property
    def mouse(self) -> _Mouse: ...


def _watchable_url(url: str) -> bool:
    if "api.billysbilling.com" in url:
        return True
    return "mit.billy.dk" in url and ("/v2/" in url or "/contacts" in url)


def watch_contact_responses(page: PersistPage) -> list[object]:
    """Record Billy browser traffic. No token. No body values."""

    seen: list[object] = []

    def _on(event: object) -> None:
        url = getattr(event, "url", "")
        if isinstance(url, str) and _watchable_url(url):
            seen.append(event)

    page.on("response", _on)
    page.on("request", _on)
    page.on("requestfailed", _on)
    return seen


async def name_field_value(page: PersistPage) -> str | None:
    field = page.locator(_NAME)
    if await field.count() < 1 or not await field.first.is_visible():
        return None
    return await field.first.input_value()


async def save_button_disabled(page: PersistPage) -> bool | None:
    button = page.locator(_SAVE)
    if await button.count() < 1 or not await button.first.is_visible():
        return None
    return await button.first.is_disabled()


async def visible_error_text(page: PersistPage) -> str | None:
    for selector in _ERROR_SELECTORS:
        node = page.locator(selector)
        if await node.count() < 1 or not await node.first.is_visible():
            continue
        text = (await node.first.inner_text()).strip()
        if text:
            return text
    return None


async def persist_snapshot(page: PersistPage) -> dict[str, JsonValue]:
    return {
        "name_value": await name_field_value(page),
        "save_disabled": await save_button_disabled(page),
        "visible_error": await visible_error_text(page),
    }


async def keyboard_set_name(page: PersistPage, value: str) -> bool:
    """Select-all, type, and blur. Used only when the DOM value is wrong."""

    field = page.locator(_NAME)
    if await field.count() < 1 or not await field.first.is_visible():
        return False
    target = field.first
    await target.click()
    await page.keyboard.press("Meta+A")
    await page.keyboard.type(value)
    await target.press("Tab")
    return await name_field_value(page) == value


async def ensure_name_value(page: PersistPage, expected: str) -> bool:
    if await name_field_value(page) == expected:
        return True
    return await keyboard_set_name(page, expected)


async def execute_rename_save(
    page: PersistPage,
    *,
    old_name: str,
    new_name: str,
    settle: Callable[[], Awaitable[None]],
) -> ToolError | dict[str, JsonValue]:
    """Type if needed, click save-button once, return error or traffic on 2xx."""

    if not await ensure_name_value(page, new_name):
        before = await persist_snapshot(page)
        return persist_error(
            "Billy customer name field did not keep the typed value.",
            before=before,
            after=before,
            traffic=summarize_contact_responses([], old_name=old_name, new_name=new_name),
        )
    console_errors = listen_console_errors(page)
    traffic_responses = watch_contact_responses(page)
    before = await persist_snapshot(page)
    delivery = await pointer_click_save(page)
    delivery["console_errors"] = list(console_errors)
    if delivery.get("blocked") or not delivery.get("pointer"):
        after = await persist_snapshot(page)
        return persist_error(
            "Billy save control is not pointer-reachable.",
            before=before,
            after=after,
            traffic=summarize_contact_responses(
                traffic_responses, old_name=old_name, new_name=new_name
            ),
            extra={"click_delivery": delivery},
        )
    await settle()
    traffic = await wait_for_contact_traffic(
        traffic_responses, old_name=old_name, new_name=new_name
    )
    after = await persist_snapshot(page)
    if persist_failed(after=after, traffic=traffic):
        return persist_error(
            "Billy customer rename did not persist.",
            before=before,
            after=after,
            traffic=traffic,
            extra={"click_delivery": delivery},
        )
    return {"before": before, "after": after, "click_delivery": delivery, **traffic}


async def click_update_save(page: PersistPage) -> bool:
    """Click only the Ember save-button with a real pointer. Never evaluate-click."""

    delivery = await pointer_click_save(page)
    return delivery.get("pointer") is True


def summarize_contact_responses(
    responses: list[object], *, old_name: str, new_name: str
) -> dict[str, JsonValue]:
    if not responses:
        return {
            "interface_status": None,
            "interface_method": None,
            "interface_path_class": None,
            "name_in_request": None,
            "failure_class": None,
        }
    event = _preferred_traffic(responses)
    url = str(getattr(event, "url", "") or "")
    request = getattr(event, "request", event)
    method = getattr(request, "method", None) or getattr(event, "method", None)
    post_data = getattr(request, "post_data", None)
    name_in_request: str | None = None
    if isinstance(post_data, str):
        if new_name in post_data:
            name_in_request = "new"
        elif old_name in post_data:
            name_in_request = "old"
        else:
            name_in_request = "absent"
    status = getattr(event, "status", None)
    return {
        "interface_status": status if isinstance(status, int) else None,
        "interface_method": method if isinstance(method, str) else None,
        "interface_path_class": _path_class(url) if url else None,
        "name_in_request": name_in_request,
        "failure_class": _failure_class(event),
    }


def _preferred_traffic(events: list[object]) -> object:
    for event in reversed(events):
        if isinstance(getattr(event, "status", None), int):
            return event
    return events[-1]


def _failure_class(event: object) -> str | None:
    raw = getattr(event, "failure", None)
    if raw is None:
        raw = getattr(getattr(event, "request", None), "failure", None)
    text = raw if isinstance(raw, str) else str(getattr(raw, "error_text", "") or "")
    folded = text.lower()
    if "blocked" in folded:
        return "blockedbyclient"
    if text:
        return "requestfailed"
    return None


async def wait_for_contact_traffic(
    responses: list[object],
    *,
    old_name: str,
    new_name: str,
    attempts: int = 40,
    idle_stop: int = 20,
) -> dict[str, JsonValue]:
    """Wait for a PUT response or a failure after the pointer click."""

    traffic = summarize_contact_responses(responses, old_name=old_name, new_name=new_name)
    for attempt in range(attempts):
        if isinstance(traffic.get("interface_status"), int) or traffic.get("failure_class"):
            return traffic
        await asyncio.sleep(0.25)
        traffic = summarize_contact_responses(responses, old_name=old_name, new_name=new_name)
        if attempt + 1 >= idle_stop and traffic.get("interface_method") is None:
            return traffic
    return traffic


def persist_failed(
    *,
    after: dict[str, JsonValue],
    traffic: dict[str, JsonValue],
) -> bool:
    if after.get("visible_error"):
        return True
    status = traffic.get("interface_status")
    if not isinstance(status, int) or status < 200 or status >= 300:
        return True
    if traffic.get("name_in_request") == "old":
        return True
    return False


def persist_error_from_isolate(message: str, isolated: dict[str, JsonValue]) -> ToolError:
    before = isolated.get("before")
    after = isolated.get("after")
    traffic = {key: value for key, value in isolated.items() if key not in {"before", "after"}}
    return persist_error(
        message,
        before=before if isinstance(before, dict) else {},
        after=after if isinstance(after, dict) else {},
        traffic=traffic,
    )


def persist_error(
    message: str,
    *,
    before: dict[str, JsonValue],
    after: dict[str, JsonValue],
    traffic: dict[str, JsonValue],
    extra: dict[str, JsonValue] | None = None,
) -> ToolError:
    details: dict[str, JsonValue] = {"before": before, "after": after, **traffic}
    if extra:
        details.update(extra)
    return ToolError(
        code=StableErrorCode.UI_CHANGED,
        message=message,
        details=details,
    )


def _path_class(url: str) -> str:
    path = urlsplit(url).path or ""
    parts = [part for part in path.split("/") if part]
    classified: list[str] = []
    for part in parts:
        if part in {"v2", "contacts"}:
            classified.append(part)
        else:
            classified.append("id")
    return "/" + "/".join(classified)
