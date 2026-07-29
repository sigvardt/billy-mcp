#!/usr/bin/env python3
"""Validate the Phase 0 coverage inventory and generated status artifacts."""

from __future__ import annotations

import ast
import json
import sys
from pathlib import Path
from typing import Any

from generate_coverage_report import (
    BILL_FILTERS,
    COMMON_ERRORS,
    DAYBOOK_TRANSACTION_FILTERS,
    INVOICE_FILTERS,
    PAGING,
    build_api_manifest,
    build_status,
    render_report,
)

ROOT = Path(__file__).resolve().parents[1]
REQUIRED_ROW_FIELDS = {
    "id",
    "lane",
    "area",
    "operation",
    "method_or_route",
    "request_fields",
    "response_fields",
    "filters",
    "pagination",
    "errors",
    "sensitivity",
    "side_effects",
    "cleanup",
    "tool_name",
    "test_references",
    "discovered",
    "implemented",
    "contract_tested",
    "live_tested",
    "vision_verified",
    "vision_evidence",
    "evidence",
}
PHASE_ZERO_FALSE_FIELDS = ("implemented", "contract_tested", "live_tested")
RAW_EVIDENCE_PARTS = ("frame", "screenshot", "rendered", "vision-evidence")
RAW_EVIDENCE_SUFFIXES = (".png", ".jpg", ".jpeg", ".webp", ".gif", ".har", ".trace.zip")


def load_document(path: Path) -> dict[str, Any]:
    """Load a JSON document saved with a YAML extension."""

    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ValueError(f"cannot load {path}: {error}") from error
    if not isinstance(payload, dict):
        raise ValueError(f"{path} must contain a mapping")
    return payload


def document_rows(document: dict[str, Any], field: str, label: str) -> list[dict[str, Any]]:
    """Return a typed manifest row list or one structural error."""

    rows = document.get(field)
    if not isinstance(rows, list) or not all(isinstance(row, dict) for row in rows):
        raise ValueError(f"{label} must contain a list of mapping rows named {field}")
    return rows


def row_errors(rows: list[dict[str, Any]], lane: str) -> list[str]:
    """Return missing fields and forbidden green states for a manifest lane."""

    errors: list[str] = []
    seen_ids: set[str] = set()
    for row in rows:
        row_id = str(row.get("id", "<missing-id>"))
        missing = sorted(REQUIRED_ROW_FIELDS - set(row))
        if missing:
            errors.append(f"{row_id}: missing required fields {', '.join(missing)}")
            continue
        if row_id in seen_ids:
            errors.append(f"duplicate coverage row id: {row_id}")
        seen_ids.add(row_id)
        if row["lane"] != lane:
            errors.append(f"{row_id}: lane must be {lane}")
        for field in PHASE_ZERO_FALSE_FIELDS:
            if row[field] is not False:
                errors.append(f"{row_id}: Phase 0 {field} must be false")
        if lane == "ui":
            if row["vision_verified"] is not False:
                errors.append(f"{row_id}: UI vision_verified must be false")
        elif row["vision_verified"] is not None:
            errors.append(f"{row_id}: API vision_verified must be null")
        if row["vision_evidence"] is not None:
            errors.append(f"{row_id}: raw or durable vision evidence is not allowed in Phase 0")
        if not isinstance(row["request_fields"], list) or not isinstance(
            row["response_fields"], list
        ):
            errors.append(f"{row_id}: request_fields and response_fields must be lists")
        if not isinstance(row["test_references"], list) or not row["test_references"]:
            errors.append(f"{row_id}: test_references must name focused tests")
    return errors


def raw_evidence_errors(value: Any, location: str = "manifest") -> list[str]:
    """Reject retained browser-frame paths or binary evidence references."""

    errors: list[str] = []
    if isinstance(value, dict):
        for key, item in value.items():
            key_location = f"{location}.{key}"
            lower_key = key.lower()
            if any(part in lower_key for part in RAW_EVIDENCE_PARTS) and item is not None:
                errors.append(f"raw browser evidence field is present: {key_location}")
            errors.extend(raw_evidence_errors(item, key_location))
    elif isinstance(value, list):
        for index, item in enumerate(value):
            errors.extend(raw_evidence_errors(item, f"{location}[{index}]"))
    elif isinstance(value, str):
        lower_value = value.lower()
        if lower_value.endswith(RAW_EVIDENCE_SUFFIXES) or "/rendered-frames/" in lower_value:
            errors.append(f"raw browser evidence path is present: {location}")
    return errors


def registered_domain_tools(root: Path) -> set[str]:
    """Find registered API/UI tool names without importing application code."""

    tools: set[str] = set()
    source_root = root / "src"
    if not source_root.is_dir():
        return tools
    for source in source_root.rglob("*.py"):
        try:
            module = ast.parse(source.read_text(encoding="utf-8"), filename=str(source))
        except (OSError, SyntaxError):
            continue
        for node in ast.walk(module):
            if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            for decorator in node.decorator_list:
                if not isinstance(decorator, ast.Call):
                    continue
                function = decorator.func
                if not isinstance(function, ast.Attribute) or function.attr != "tool":
                    continue
                tool_name = node.name
                for keyword in decorator.keywords:
                    if keyword.arg == "name" and isinstance(keyword.value, ast.Constant):
                        if isinstance(keyword.value.value, str):
                            tool_name = keyword.value.value
                if tool_name.startswith(("api_", "ui_")):
                    tools.add(tool_name)
    return tools


def api_errors(api_rows: list[dict[str, Any]]) -> list[str]:
    """Validate frozen official arithmetic, ambiguities, and documented details."""

    errors = row_errors(api_rows, "api")
    expected_rows = build_api_manifest()["operations"]
    expected_ids = {row["id"] for row in expected_rows}
    actual_ids = {str(row.get("id", "")) for row in api_rows}
    if actual_ids != expected_ids:
        missing = sorted(expected_ids - actual_ids)
        unexpected = sorted(actual_ids - expected_ids)
        if missing:
            errors.append(f"official API rows missing: {', '.join(missing)}")
        if unexpected:
            errors.append(f"invented or unsupported API rows: {', '.join(unexpected)}")

    kind_counts: dict[str, int] = {}
    planned_tools: set[str] = set()
    for row in api_rows:
        kind = row.get("source_kind")
        if isinstance(kind, str):
            kind_counts[kind] = kind_counts.get(kind, 0) + 1
        row_id = str(row.get("id", "<missing-id>"))
        method_or_route = str(row.get("method_or_route", ""))
        tool_name = row.get("tool_name")
        if "/v2/documents" in method_or_route or "webhook" in method_or_route.lower():
            errors.append(f"{row_id}: invented documents or webhook route")
        if isinstance(tool_name, str) and tool_name:
            if any(
                fragment in tool_name for fragment in ("bulk", "webhook", "singular_organization")
            ):
                errors.append(f"{row_id}: forbidden planned tool {tool_name}")
            if tool_name in planned_tools:
                errors.append(f"{row_id}: duplicate planned tool {tool_name}")
            planned_tools.add(tool_name)
        if kind == "ambiguous_bulk":
            if row.get("contract_status") != "ambiguous_bulk":
                errors.append(f"{row_id}: bulk row must declare contract_status ambiguous_bulk")
            if tool_name != "":
                errors.append(f"{row_id}: ambiguous bulk row must not plan a tool")
            if not method_or_route.startswith("AMBIGUOUS Supports:"):
                errors.append(f"{row_id}: ambiguous bulk route must remain explicitly ambiguous")
            if any(row.get(field) is not False for field in PHASE_ZERO_FALSE_FIELDS):
                errors.append(f"{row_id}: ambiguous bulk row must stay red")
        if kind == "clear" and row.get("discovered") is not True:
            errors.append(f"{row_id}: documented clear operation must be discovered")
        if not set(COMMON_ERRORS).issubset(set(row.get("errors", []))):
            errors.append(f"{row_id}: both documented 401 error codes are required")
        if row.get("pagination") is not None:
            pagination = row["pagination"]
            if pagination != PAGING:
                errors.append(f"{row_id}: pagination must preserve page/pageSize only")
            if "offset" in json.dumps(pagination).lower():
                errors.append(f"{row_id}: offset is not a documented paging parameter")

    if kind_counts != {"ambiguous_bulk": 92, "clear": 207, "special": 6}:
        errors.append(f"wrong frozen API arithmetic: {kind_counts}")
    if len(api_rows) != 305:
        errors.append(f"wrong API snapshot total: {len(api_rows)}")

    by_id = {row["id"]: row for row in api_rows if isinstance(row.get("id"), str)}
    for row_id, filters in (
        ("api.invoices.list", INVOICE_FILTERS),
        ("api.bills.list", BILL_FILTERS),
        ("api.daybookTransactions.list", DAYBOOK_TRANSACTION_FILTERS),
    ):
        if by_id.get(row_id, {}).get("filters") != filters:
            errors.append(f"{row_id}: documented filter table changed or incomplete")
    return errors


def ui_errors(ui_rows: list[dict[str, Any]], api_rows: list[dict[str, Any]]) -> list[str]:
    """Validate red discovery seeds and one explicit parity map per API row."""

    errors = row_errors(ui_rows, "ui")
    parity_rows = [row for row in ui_rows if row.get("workflow_kind") == "api_parity"]
    discovery_rows = [row for row in ui_rows if row.get("workflow_kind") == "discovery"]
    expected_api_ids = {row["id"] for row in api_rows}
    mapped_api_ids = {row.get("api_row_id") for row in parity_rows}
    if mapped_api_ids != expected_api_ids:
        errors.append("UI parity map must include every API business capability exactly once")
    if len(parity_rows) != len(mapped_api_ids):
        errors.append("UI parity map contains duplicate API capability mappings")
    if not discovery_rows:
        errors.append("UI discovery route-family rows are required")
    for row in ui_rows:
        row_id = str(row.get("id", "<missing-id>"))
        if row.get("parity_status") == "not_applicable":
            errors.append(f"{row_id}: not_applicable requires verified UI evidence")
        if row.get("vision_evidence") is not None:
            errors.append(f"{row_id}: UI frame evidence must not be retained")
    return errors


def egress_errors(egress: dict[str, Any]) -> list[str]:
    """Validate the exact, minimal deny-by-default host policy."""

    errors: list[str] = []
    if egress.get("default_action") != "deny":
        errors.append("browser egress must deny by default")
    hosts = egress.get("hosts")
    if not isinstance(hosts, list):
        return [*errors, "browser egress hosts must be a list"]
    by_host = {entry.get("host"): entry for entry in hosts if isinstance(entry, dict)}
    expected_hosts = {"mit.billy.dk", "download.billy.dk", "api.billysbilling.com", "api.billy.dk"}
    if set(by_host) != expected_hosts:
        errors.append("browser egress must contain only the four frozen host rules")
        return errors
    if by_host["mit.billy.dk"].get("browser_action") != "allow":
        errors.append("mit.billy.dk must be allowed for UI/auth")
    download = by_host["download.billy.dk"]
    if (
        download.get("browser_action") != "allow"
        or download.get("owner") != "future_typed_download"
    ):
        errors.append("download.billy.dk must be limited to future typed download handling")
    api_host = by_host["api.billysbilling.com"]
    if (
        api_host.get("browser_action") != "deny"
        or api_host.get("api_client_action") != "exclusive_allow"
    ):
        errors.append("api.billysbilling.com must be exclusive to the API client")
    alias = by_host["api.billy.dk"]
    if alias.get("browser_action") != "deny" or alias.get("api_client_action") != "deny":
        errors.append("api.billy.dk must be denied")
    return errors


def validate_documents(
    api_manifest: dict[str, Any],
    ui_manifest: dict[str, Any],
    browser_egress: dict[str, Any],
    status: dict[str, Any],
    report: str,
    root: Path,
) -> list[str]:
    """Return all structural and status failures without changing checked-in data."""

    try:
        api_rows = document_rows(api_manifest, "operations", "API manifest")
        ui_rows = document_rows(ui_manifest, "workflows", "UI manifest")
    except ValueError as error:
        return [str(error)]
    errors = [*api_errors(api_rows), *ui_errors(ui_rows, api_rows), *egress_errors(browser_egress)]
    errors.extend(raw_evidence_errors(api_manifest, "api_manifest"))
    errors.extend(raw_evidence_errors(ui_manifest, "ui_manifest"))
    errors.extend(raw_evidence_errors(browser_egress, "browser_egress"))

    expected_status = build_status(api_manifest, ui_manifest)
    if status != expected_status:
        errors.append("coverage/status.json is stale or does not match generated source arithmetic")
    if status.get("complete") is not False:
        errors.append("coverage/status.json complete must be false while rows remain red")
    if report != render_report(expected_status):
        errors.append("coverage/report.md is stale or non-deterministic")

    planned_tools = {
        row["tool_name"]
        for row in api_rows + ui_rows
        if isinstance(row.get("tool_name"), str) and row["tool_name"]
    }
    for tool_name in sorted(registered_domain_tools(root) - planned_tools):
        errors.append(f"registered domain tool lacks a coverage row: {tool_name}")
    return errors


def validate_root(root: Path) -> list[str]:
    """Load and validate every checked-in artifact under a repository root."""

    coverage = root / "coverage"
    try:
        api_manifest = load_document(coverage / "api_v2_manifest.yaml")
        ui_manifest = load_document(coverage / "ui_workflows_manifest.yaml")
        browser_egress = load_document(coverage / "browser_egress.yaml")
        status = load_document(coverage / "status.json")
        report = (coverage / "report.md").read_text(encoding="utf-8")
    except (OSError, ValueError) as error:
        return [str(error)]
    return validate_documents(api_manifest, ui_manifest, browser_egress, status, report, root)


def main() -> int:
    """Print validation failures suitable for local and CI use."""

    errors = validate_root(ROOT)
    if errors:
        print("Coverage inventory checks failed:")
        print("\n".join(f"- {error}" for error in errors))
        return 1
    api_manifest = load_document(ROOT / "coverage" / "api_v2_manifest.yaml")
    ui_manifest = load_document(ROOT / "coverage" / "ui_workflows_manifest.yaml")
    print(
        "Coverage inventory checks passed: "
        f"{len(api_manifest['operations'])} API rows, {len(ui_manifest['workflows'])} UI rows."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
