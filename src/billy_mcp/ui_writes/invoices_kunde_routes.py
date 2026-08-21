"""Invoice Kunde sanitized /v2/ bootstrap route keys (F12B607E)."""

from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Final, Literal, cast

from billy_mcp.ui_writes.invoices_kunde_route_class import (
    COARSE_ROUTE_CLASSES,
    OFFICIAL_V2_RESOURCES,
    ROUTE_PHASES,
    TIMING_BUCKETS,
    RoutePhase,
    is_contact_adjacent_class,
    owner_template_from_url,
    route_class_for_url,
)
from billy_mcp.ui_writes.invoices_kunde_route_class import (
    route_class_for as route_class_for,
)
from billy_mcp.ui_writes.invoices_kunde_route_class import (
    sanitize_v2_route_template as sanitize_v2_route_template,
)
from billy_mcp.ui_writes.invoices_kunde_route_class import (
    timing_bucket_for as timing_bucket_for,
)
from billy_mcp.ui_writes.invoices_kunde_trace import request_url_class

RouteKey = Literal["route_class", "timing_bucket", "phase"]

REQUIRED_KUNDE_ROUTE_KEYS: Final[tuple[RouteKey, ...]] = (
    "route_class",
    "timing_bucket",
    "phase",
)
KUNDE_ROUTE_TEMPLATE_DUMP: Final = (
    Path.home() / ".local" / "share" / "billy-mcp" / "inspect-live-invoices-kunde-routes.json"
)


def empty_kunde_route_row() -> dict[str, object]:
    """Structurally complete F12B607E request keys."""

    return {
        "method": "GET",
        "path_class": "other_v2",
        "status": 0,
        "timing_ms": 0,
        "route_class": "other_v2",
        "timing_bucket": "0_49",
        "phase": "at_rest",
    }


def _as_str_map(value: object) -> dict[str, object] | None:
    if not isinstance(value, dict):
        return None
    return dict(cast(dict[str, object], value))


def _row_missing_keys(row: Mapping[str, object]) -> list[str]:
    missing: list[str] = []
    route_class = row.get("route_class")
    if not isinstance(route_class, str) or (
        route_class not in OFFICIAL_V2_RESOURCES and route_class not in COARSE_ROUTE_CLASSES
    ):
        missing.append("route_class")
    if row.get("timing_bucket") not in TIMING_BUCKETS:
        missing.append("timing_bucket")
    if row.get("phase") not in ROUTE_PHASES:
        missing.append("phase")
    return missing


def kunde_route_missing_keys(rows: Sequence[object]) -> list[str]:
    """Keys F12B607E requires on each other_v2 request row."""

    found: list[str] = []
    for item in rows:
        row = _as_str_map(item)
        if row is None:
            return list(REQUIRED_KUNDE_ROUTE_KEYS)
        if row.get("path_class") != "other_v2":
            continue
        for key in _row_missing_keys(row):
            if key not in found:
                found.append(key)
    return found


def contact_dataset_preloaded(rows: Sequence[object]) -> bool:
    """True when a contact-adjacent route was first seen at rest."""

    for item in rows:
        row = _as_str_map(item)
        if row is None:
            continue
        route_class = row.get("route_class")
        if not isinstance(route_class, str):
            continue
        if row.get("phase") == "at_rest" and is_contact_adjacent_class(route_class):
            return True
    return False


def committed_route_row(
    *,
    method: str,
    path_class: str,
    status: int,
    timing_ms: int,
    route_class: str,
    phase: str,
) -> dict[str, object]:
    """Committed request row. Never stores URL, query, or template."""

    verb = method.strip().upper() or "OTHER"
    classified = path_class if path_class in COARSE_ROUTE_CLASSES else "denied"
    match phase:
        case "at_rest" | "after_click" | "after_type":
            phase_token: RoutePhase = phase
        case _:
            phase_token = "at_rest"
    allowed_class = (
        route_class
        if route_class in OFFICIAL_V2_RESOURCES or route_class in COARSE_ROUTE_CLASSES
        else "other_v2"
    )
    return {
        "method": verb,
        "path_class": classified,
        "status": max(0, status),
        "timing_ms": max(0, timing_ms),
        "route_class": allowed_class,
        "timing_bucket": timing_bucket_for(max(0, timing_ms)),
        "phase": phase_token,
    }


def redact_route_request(
    *,
    method: str,
    path_class: str,
    status: int,
    timing_ms: int,
    url: str,
    phase: str,
) -> dict[str, object]:
    """Classify a live URL into a committed row. Drops the URL."""

    return committed_route_row(
        method=method,
        path_class=path_class,
        status=status,
        timing_ms=timing_ms,
        route_class=route_class_for_url(url),
        phase=phase,
    )


def write_owner_route_templates(
    templates: Sequence[str],
    *,
    path: Path | None = None,
) -> Path:
    """Write owner-only sanitized templates. Isolated tests pass path."""

    target = path if path is not None else KUNDE_ROUTE_TEMPLATE_DUMP
    target.parent.mkdir(parents=True, exist_ok=True)
    payload = [{"route_template": item} for item in templates]
    target.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return target


def pending_from_url(method: str, url: str) -> dict[str, object]:
    """Pending sink fields. Template is sanitized; raw URL is dropped."""

    return {
        "method": method,
        "path_class": request_url_class(url),
        "route_class": route_class_for_url(url),
        "template": owner_template_from_url(url),
    }


def row_from_pending(
    pending: Mapping[str, object],
    *,
    status: int,
    timing_ms: int,
    phase: str,
) -> dict[str, object]:
    """Build a committed row from pending fields. Never copies a URL."""

    route_class = pending.get("route_class")
    class_token = route_class if isinstance(route_class, str) else "denied"
    return committed_route_row(
        method=str(pending.get("method") or "OTHER"),
        path_class=str(pending.get("path_class") or "denied"),
        status=status,
        timing_ms=timing_ms,
        route_class=class_token,
        phase=phase,
    )


def apply_kunde_route_dump(
    result: dict[str, object],
    templates: Sequence[str],
    *,
    template_path: Path | None = None,
) -> dict[str, object]:
    """Attach F12B607E flags and write owner-only templates."""

    at_rest = _as_str_map(result.get("at_rest"))
    requests: list[object] = []
    if at_rest is not None:
        raw = at_rest.get("requests")
        if isinstance(raw, list):
            requests = cast(list[object], raw)
    result["contact_dataset_preloaded"] = contact_dataset_preloaded(requests)
    result["kunde_route_missing_keys"] = kunde_route_missing_keys(requests)
    write_owner_route_templates(templates, path=template_path)
    if result.get("contact_dataset_preloaded") is True:
        result["named_next_action"] = True
    if template_path is None:
        from billy_mcp.ui_writes.invoices_form_observe import dump_kunde_trace

        dump_kunde_trace(result)
    return result
