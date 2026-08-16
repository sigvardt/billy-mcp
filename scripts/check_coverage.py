#!/usr/bin/env python3
"""Validate the generated coverage inventory and status artifacts."""

from __future__ import annotations

import argparse
import ast
import json
import sys
from pathlib import Path
from typing import Any

from generate_coverage_report import (
    API_QUALIFICATION_FIELDS,
    BILL_FILTERS,
    COMMON_ERRORS,
    DAYBOOK_TRANSACTION_FILTERS,
    FILES_UPLOAD_ALIAS,
    FILES_UPLOAD_REQUEST_FIELDS,
    FILES_UPLOAD_TOOL_NAME,
    INVOICE_FILTERS,
    PAGING,
    UI_QUALIFICATION_FIELDS,
    build_api_manifest,
    build_status,
    coverage_is_complete,
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
    """Return missing fields and invalid status types for a manifest lane."""

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
        for field in API_QUALIFICATION_FIELDS:
            if not isinstance(row[field], bool):
                errors.append(f"{row_id}: {field} must be a boolean")
        if lane == "ui":
            if not isinstance(row["vision_verified"], bool):
                errors.append(f"{row_id}: UI vision_verified must be a boolean")
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
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                for decorator in node.decorator_list:
                    tool_name = _tool_decorator_name(decorator, node.name)
                    if tool_name is not None:
                        tools.add(tool_name)
            if isinstance(node, ast.Call):
                tool_name = _imperative_tool_name(node)
                if tool_name is not None:
                    tools.add(tool_name)
    return tools


def _tool_decorator_name(decorator: ast.expr, default_name: str) -> str | None:
    """Return an API/UI name from a direct ``@server.tool`` decorator."""

    if not isinstance(decorator, ast.Call):
        return None
    function = decorator.func
    if not isinstance(function, ast.Attribute) or function.attr != "tool":
        return None
    tool_name = default_name
    for keyword in decorator.keywords:
        if keyword.arg == "name" and isinstance(keyword.value, ast.Constant):
            if isinstance(keyword.value.value, str):
                tool_name = keyword.value.value
    return tool_name if tool_name.startswith(("api_", "ui_")) else None


def _imperative_tool_name(call: ast.Call) -> str | None:
    """Return an API/UI name from ``server.tool(name=...)(handler)`` registration."""

    factory = call.func
    if not isinstance(factory, ast.Call):
        return None
    attribute = factory.func
    if not isinstance(attribute, ast.Attribute) or attribute.attr != "tool":
        return None
    for keyword in factory.keywords:
        if keyword.arg == "name" and isinstance(keyword.value, ast.Constant):
            name = keyword.value.value
            if isinstance(name, str) and name.startswith(("api_", "ui_")):
                return name
    return None


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

    expected_by_id = {row["id"]: row for row in expected_rows}
    kind_counts: dict[str, int] = {}
    planned_tools: set[str] = set()
    for row in api_rows:
        kind = row.get("source_kind")
        if isinstance(kind, str):
            kind_counts[kind] = kind_counts.get(kind, 0) + 1
        row_id = str(row.get("id", "<missing-id>"))
        expected = expected_by_id.get(row_id)
        if expected is not None:
            for field in ("implemented", "contract_tested", "live_tested", "test_references"):
                if row.get(field) != expected[field]:
                    errors.append(
                        f"{row_id}: generated offline qualification evidence does not match source"
                    )
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
            if any(
                row.get(field) is True
                for field in ("implemented", "contract_tested", "live_tested")
            ):
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
    files_create = by_id.get("api.files.create", {})
    files_upload = by_id.get(FILES_UPLOAD_ALIAS, {})
    if files_create.get("alias_of") != FILES_UPLOAD_ALIAS:
        errors.append("api.files.create: must alias the documented raw-binary upload row")
    if files_create.get("tool_name") != "":
        errors.append("api.files.create: must not plan a separate files-create tool")
    if files_create.get("request_fields") != FILES_UPLOAD_REQUEST_FIELDS:
        errors.append("api.files.create: must preserve documented raw-binary upload headers")
    if files_upload.get("tool_name") != FILES_UPLOAD_TOOL_NAME:
        errors.append("api.special.files_upload: must own the upload preview tool family")
    if files_upload.get("request_fields") != FILES_UPLOAD_REQUEST_FIELDS:
        errors.append(
            "api.special.files_upload: must preserve documented raw-binary upload headers"
        )
    if any(tool_name.startswith("api_files_create") for tool_name in planned_tools):
        errors.append("files upload coverage must not invent an api_files_create tool")
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
            errors.extend(not_applicable_ui_errors(row, row_id))
        if row.get("vision_evidence") is not None:
            errors.append(f"{row_id}: UI frame evidence must not be retained")
    return errors


def not_applicable_ui_errors(row: dict[str, Any], row_id: str) -> list[str]:
    """Require dual-session machine-readable evidence for UI not_applicable rows."""

    errors: list[str] = []
    qual = row.get("qualification")
    if not isinstance(qual, dict):
        errors.append(f"{row_id}: not_applicable requires a qualification object")
        return errors
    if qual.get("not_applicable_decision") != "accepted":
        errors.append(
            f"{row_id}: not_applicable requires qualification.not_applicable_decision=accepted"
        )
    if not isinstance(qual.get("evidence_code"), str) or not str(qual.get("evidence_code")).strip():
        errors.append(f"{row_id}: not_applicable requires qualification.evidence_code")
    if qual.get("sessions") != "dual_independent_ephemeral":
        errors.append(
            f"{row_id}: not_applicable requires dual_independent_ephemeral sessions evidence"
        )
    if not isinstance(qual.get("evidence_ref"), str) or not str(qual.get("evidence_ref")).strip():
        errors.append(f"{row_id}: not_applicable requires qualification.evidence_ref")
    for field in (
        "discovered",
        "implemented",
        "contract_tested",
        "live_tested",
        "vision_verified",
    ):
        if row.get(field) is not True:
            errors.append(f"{row_id}: not_applicable requires {field}=true")
    if row.get("tool_name"):
        errors.append(f"{row_id}: not_applicable rows must not register a tool_name")
    if row.get("vision_evidence") is not None:
        errors.append(f"{row_id}: not_applicable must not retain vision_evidence frames")
    if not isinstance(row.get("evidence"), str) or len(str(row.get("evidence")).strip()) < 40:
        errors.append(f"{row_id}: not_applicable requires non-empty dual-session evidence text")
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
    api_browser_action = api_host.get("browser_action")
    path_allows = api_host.get("browser_path_allows")
    if api_host.get("api_client_action") != "exclusive_allow":
        errors.append("api.billysbilling.com must remain exclusive_allow for the API client")
    if api_browser_action == "allow":
        errors.append("api.billysbilling.com must not be fully open to the browser lane")
    elif api_browser_action == "path_allow":
        if not isinstance(path_allows, list) or not path_allows:
            errors.append("api.billysbilling.com path_allow requires browser_path_allows rules")
        else:
            has_login = any(
                isinstance(rule, dict)
                and rule.get("match") == "exact"
                and rule.get("path") == "/v2/user/login"
                and "POST" in (rule.get("methods") or [])
                for rule in path_allows
            )
            if not has_login:
                errors.append(
                    "api.billysbilling.com path_allow must include exact POST /v2/user/login"
                )
    elif api_browser_action != "deny":
        errors.append("api.billysbilling.com browser_action must be deny or path_allow")
    alias = by_host["api.billy.dk"]
    if alias.get("browser_action") != "deny" or alias.get("api_client_action") != "deny":
        errors.append("api.billy.dk must be denied")
    return errors


def false_completeness_errors(
    api_rows: list[dict[str, Any]], ui_rows: list[dict[str, Any]], status: dict[str, Any]
) -> list[str]:
    """Reject a green status claim that its manifest evidence cannot support."""

    if status.get("complete") is True and not coverage_is_complete(api_rows, ui_rows):
        return ["coverage/status.json falsely claims complete without qualifying manifest rows"]
    return []


def require_complete_errors(
    api_rows: list[dict[str, Any]], ui_rows: list[dict[str, Any]], status: dict[str, Any]
) -> list[str]:
    """Return the full-qualification failures required by the release gate."""

    errors: list[str] = []
    if status.get("complete") is not True:
        errors.append("--require-complete requires coverage/status.json complete=true")
    ambiguous_rows = [row for row in api_rows if row.get("source_kind") == "ambiguous_bulk"]
    if ambiguous_rows:
        errors.append(
            f"--require-complete requires no ambiguous_bulk rows ({len(ambiguous_rows)} remain)"
        )
    incomplete_api = [
        str(row.get("id", "<missing-id>"))
        for row in api_rows
        if not all(row.get(field) is True for field in API_QUALIFICATION_FIELDS)
    ]
    if incomplete_api:
        errors.append(
            "--require-complete requires discovered, implemented, contract_tested, and "
            f"live_tested for every API row ({len(incomplete_api)} incomplete)"
        )
    incomplete_ui = [
        str(row.get("id", "<missing-id>"))
        for row in ui_rows
        if not all(row.get(field) is True for field in UI_QUALIFICATION_FIELDS)
    ]
    if incomplete_ui:
        errors.append(
            "--require-complete requires all API qualification states and vision_verified "
            f"for every UI row ({len(incomplete_ui)} incomplete)"
        )
    return errors


def execute_twin_names(planned_tools: set[str]) -> set[str]:
    """Return non-inventory execute companions for documented write previews."""

    return {
        f"{tool_name.removesuffix('_preview')}_execute"
        for tool_name in planned_tools
        if tool_name.startswith(("api_", "ui_")) and tool_name.endswith("_preview")
    }


def validate_documents(
    api_manifest: dict[str, Any],
    ui_manifest: dict[str, Any],
    browser_egress: dict[str, Any],
    status: dict[str, Any],
    report: str,
    root: Path,
    *,
    reject_false_completeness: bool = False,
    require_complete: bool = False,
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
    if reject_false_completeness:
        errors.extend(false_completeness_errors(api_rows, ui_rows, status))
    if require_complete:
        errors.extend(require_complete_errors(api_rows, ui_rows, status))
    if report != render_report(expected_status):
        errors.append("coverage/report.md is stale or non-deterministic")

    planned_tools = {
        row["tool_name"]
        for row in api_rows + ui_rows
        if isinstance(row.get("tool_name"), str) and row["tool_name"]
    }
    allowed_registered_tools = planned_tools | execute_twin_names(planned_tools)
    for tool_name in sorted(registered_domain_tools(root) - allowed_registered_tools):
        errors.append(f"registered domain tool lacks a coverage row: {tool_name}")
    return errors


def validate_root(
    root: Path,
    *,
    reject_false_completeness: bool = False,
    require_complete: bool = False,
) -> list[str]:
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
    return validate_documents(
        api_manifest,
        ui_manifest,
        browser_egress,
        status,
        report,
        root,
        reject_false_completeness=reject_false_completeness,
        require_complete=require_complete,
    )


def main() -> int:
    """Print validation failures suitable for local and CI use."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--reject-false-completeness",
        action="store_true",
        help="reject a true completeness claim that red manifest evidence cannot support",
    )
    parser.add_argument(
        "--require-complete",
        action="store_true",
        help="require a fully qualified manifest for a full test or release gate",
    )
    args = parser.parse_args()
    errors = validate_root(
        ROOT,
        reject_false_completeness=args.reject_false_completeness,
        require_complete=args.require_complete,
    )
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
