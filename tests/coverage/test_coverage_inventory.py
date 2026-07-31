"""Tests for the fail-closed generated coverage inventory."""

from __future__ import annotations

import copy
import importlib.util
import json
import subprocess
import sys
from collections import Counter
from pathlib import Path
from types import ModuleType
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))


def load_script_module(name: str) -> ModuleType:
    """Load an owned script module so its public helpers are testable."""

    spec = importlib.util.spec_from_file_location(name, SCRIPTS / f"{name}.py")
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


generator = load_script_module("generate_coverage_report")
checker = load_script_module("check_coverage")


def documents() -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any], str]:
    """Load the checked-in generated artifacts once per assertion group."""

    coverage = ROOT / "coverage"
    return (
        checker.load_document(coverage / "api_v2_manifest.yaml"),
        checker.load_document(coverage / "ui_workflows_manifest.yaml"),
        checker.load_document(coverage / "browser_egress.yaml"),
        checker.load_document(coverage / "status.json"),
        (coverage / "report.md").read_text(encoding="utf-8"),
    )


def validation_errors(
    api_manifest: dict[str, Any],
    ui_manifest: dict[str, Any],
    browser_egress: dict[str, Any],
    status: dict[str, Any],
    report: str,
    *,
    root: Path = ROOT,
    reject_false_completeness: bool = False,
    require_complete: bool = False,
) -> list[str]:
    """Validate in-memory copies without changing generated repository files."""

    return checker.validate_documents(
        api_manifest,
        ui_manifest,
        browser_egress,
        status,
        report,
        root,
        reject_false_completeness=reject_false_completeness,
        require_complete=require_complete,
    )


def test_generated_inventory_passes_its_self_check() -> None:
    """The checked-in manifests, report, and status agree exactly."""

    assert checker.validate_root(ROOT) == []


def test_write_response_root_overrides_are_scoped() -> None:
    """Preserve the frozen root without changing conventional write rows."""

    operations = generator.build_api_manifest()["operations"]
    by_id = {row["id"]: row for row in operations}

    assert by_id["api.invoiceReminders.create"]["response_fields"] == ["invoiceReminders[]"]
    assert by_id["api.organizations.create"]["response_fields"] == ["organizations[]"]
    assert by_id["api.invoiceLateFees.create"]["response_fields"] == [
        "changed_records[]",
        "meta.deletedRecords",
    ]


def test_api_source_arithmetic_and_documented_contracts_are_frozen() -> None:
    """The 207/92/6 research snapshot retains its protected API details."""

    api_manifest, _, _, status, _ = documents()
    operations = api_manifest["operations"]
    by_id = {row["id"]: row for row in operations}

    assert Counter(row["source_kind"] for row in operations) == {
        "clear": 207,
        "ambiguous_bulk": 92,
        "special": 6,
    }
    assert len(operations) == 305
    assert by_id["api.invoices.list"]["filters"] == generator.INVOICE_FILTERS
    assert by_id["api.bills.list"]["filters"] == generator.BILL_FILTERS
    assert by_id["api.daybookTransactions.list"]["filters"] == generator.DAYBOOK_TRANSACTION_FILTERS
    for resource in ("cities", "states", "zipcodes"):
        row = by_id[f"api.{resource}.list"]
        assert row["filters"] == {"countryId": {"type": "string", "required": True}}
        assert row["request_fields"] == [
            "page",
            "pageSize",
            "include",
            "sortProperty",
            "sortDirection",
            "countryId",
        ]
        assert row["contract_status"] == "documented_plus_live_observation"
        assert "without a non-empty countryId" in row["evidence"]
    assert by_id["api.files.create"]["alias_of"] == generator.FILES_UPLOAD_ALIAS
    assert by_id["api.files.create"]["tool_name"] == ""
    assert by_id["api.files.create"]["request_fields"] == generator.FILES_UPLOAD_REQUEST_FIELDS
    assert by_id[generator.FILES_UPLOAD_ALIAS]["tool_name"] == generator.FILES_UPLOAD_TOOL_NAME
    assert (
        by_id[generator.FILES_UPLOAD_ALIAS]["request_fields"]
        == generator.FILES_UPLOAD_REQUEST_FIELDS
    )
    upload_evidence = (
        "tests/api/test_file_upload_writes.py",
        generator.SERVER_REGISTRY_TEST_REFERENCE,
    )
    assert generator.OFFLINE_API_IMPLEMENTATION_EVIDENCE["api.files.create"] == upload_evidence
    assert generator.OFFLINE_API_IMPLEMENTATION_EVIDENCE[generator.FILES_UPLOAD_ALIAS] == (
        upload_evidence
    )
    for row_id in ("api.files.create", generator.FILES_UPLOAD_ALIAS):
        assert by_id[row_id]["test_references"] == [generator.TEST_REFERENCE, *upload_evidence]
        assert by_id[row_id]["implemented"] is True
        assert by_id[row_id]["contract_tested"] is True
    assert by_id["api.bankLineMatches.get"]["response_fields"] == ["bankLineMatch"]
    for row_id in (
        "api.salesTaxPayments.create",
        "api.contactBalancePayments.create",
        "api.invoiceLateFees.create",
    ):
        assert by_id[row_id]["cleanup"] == (
            "live non-production cleanup strategy unqualified; singular DELETE is unsupported"
        )
    assert by_id["api.users.update"]["sensitivity"] == "high"
    assert by_id["api.users.update"]["side_effects"] == (
        "high: updates user PII and privilege flags"
    )
    assert by_id["api.users.update"]["cleanup"] == (
        "must read and restore prior non-production user state via PUT before "
        "greening; singular DELETE is method-closed (405)"
    )

    offline_evidence = generator.OFFLINE_API_IMPLEMENTATION_EVIDENCE
    for row in operations:
        assert set(generator.COMMON_ERRORS).issubset(row["errors"])
        expected_offline_evidence = offline_evidence.get(row["id"], ())
        assert row["implemented"] is bool(expected_offline_evidence)
        assert row["contract_tested"] is bool(expected_offline_evidence)
        assert row["live_tested"] is False
        assert row["test_references"] == [generator.TEST_REFERENCE, *expected_offline_evidence]
        if row["operation"] == "list" and row["source_kind"] == "clear":
            assert row["pagination"] == generator.PAGING
            assert "offset" not in row["request_fields"]
    assert status["complete"] is False
    assert status["phase"] == generator.CURRENT_COVERAGE_PHASE
    assert status["source_counts"]["api_total"] == 305
    assert status["qualification"]["implemented_rows"] == len(offline_evidence) + 10
    assert status["qualification"]["contract_tested_rows"] == len(offline_evidence) + 10
    # API live remains 0 (out of scope); ten UI shell rows are live-qualified.
    assert status["qualification"]["live_tested_rows"] == 10
    assert status["qualification"]["vision_verified_rows"] == 10
    assert '"bankLineMatche"' not in json.dumps(api_manifest)


def test_status_completeness_is_derived_from_row_evidence() -> None:
    """A future green claim depends on every lane state and resolved bulk rows."""

    green_api = [
        {
            "source_kind": "clear",
            "discovered": True,
            "implemented": True,
            "contract_tested": True,
            "live_tested": True,
        }
    ]
    green_ui = [
        {
            "workflow_kind": "api_parity",
            "discovered": True,
            "implemented": True,
            "contract_tested": True,
            "live_tested": True,
            "vision_verified": True,
        }
    ]

    assert (
        generator.build_status({"operations": green_api}, {"workflows": green_ui})["complete"]
        is True
    )
    assert (
        generator.build_status(
            {"operations": [{**green_api[0], "source_kind": "ambiguous_bulk"}]},
            {"workflows": green_ui},
        )["complete"]
        is False
    )


def test_require_complete_checks_each_row_state_and_bulk_resolution() -> None:
    """The full gate has no shortcut around API, UI, or bulk qualification."""

    qualified_api = [
        {
            "id": "api.products.list",
            "source_kind": "clear",
            "discovered": True,
            "implemented": True,
            "contract_tested": True,
            "live_tested": True,
        }
    ]
    qualified_ui = [
        {
            "id": "ui.parity.products.list",
            "workflow_kind": "api_parity",
            "discovered": True,
            "implemented": True,
            "contract_tested": True,
            "live_tested": True,
            "vision_verified": True,
        }
    ]
    complete_status = {"complete": True}

    assert checker.require_complete_errors(qualified_api, qualified_ui, complete_status) == []

    incomplete_api = copy.deepcopy(qualified_api)
    incomplete_api[0]["contract_tested"] = False
    assert any(
        "for every API row" in error
        for error in checker.require_complete_errors(incomplete_api, qualified_ui, complete_status)
    )

    incomplete_ui = copy.deepcopy(qualified_ui)
    incomplete_ui[0]["vision_verified"] = False
    assert any(
        "for every UI row" in error
        for error in checker.require_complete_errors(qualified_api, incomplete_ui, complete_status)
    )

    unresolved_bulk = [{**qualified_api[0], "source_kind": "ambiguous_bulk"}]
    assert any(
        "no ambiguous_bulk rows" in error
        for error in checker.require_complete_errors(unresolved_bulk, qualified_ui, complete_status)
    )


def test_files_create_remains_a_raw_binary_alias_without_a_second_tool() -> None:
    """The Supports create flag must not invent a JSON files-create contract."""

    api_manifest, ui_manifest, browser_egress, status, report = documents()
    duplicate_tool = copy.deepcopy(api_manifest)
    files_create = next(
        row for row in duplicate_tool["operations"] if row["id"] == "api.files.create"
    )
    files_create["tool_name"] = "api_files_create_preview"

    assert any(
        "must not plan a separate files-create tool" in error
        for error in validation_errors(duplicate_tool, ui_manifest, browser_egress, status, report)
    )
    assert any(
        "must not invent an api_files_create tool" in error
        for error in validation_errors(duplicate_tool, ui_manifest, browser_egress, status, report)
    )

    missing_header = copy.deepcopy(api_manifest)
    files_upload = next(
        row for row in missing_header["operations"] if row["id"] == generator.FILES_UPLOAD_ALIAS
    )
    files_upload["request_fields"] = ["file_bytes"]
    assert any(
        "api.special.files_upload: must preserve documented raw-binary upload headers" in error
        for error in validation_errors(missing_header, ui_manifest, browser_egress, status, report)
    )


def test_bulk_rows_remain_ambiguous_and_toolless() -> None:
    """No historical bulk shape can accidentally become a planned tool."""

    api_manifest, _, _, _, _ = documents()
    bulk_rows = [
        row for row in api_manifest["operations"] if row["source_kind"] == "ambiguous_bulk"
    ]

    assert len(bulk_rows) == 92
    assert all(row["contract_status"] == "ambiguous_bulk" for row in bulk_rows)
    assert all(row["tool_name"] == "" for row in bulk_rows)
    assert all(row["implemented"] is False for row in bulk_rows)


def test_ui_parity_and_egress_are_complete_but_visibly_red() -> None:
    """UI discovery does not use unsupported not-applicable or frame evidence."""

    api_manifest, ui_manifest, browser_egress, status, _ = documents()
    workflows = ui_manifest["workflows"]
    parity_rows = [row for row in workflows if row["workflow_kind"] == "api_parity"]
    discovery_rows = [row for row in workflows if row["workflow_kind"] == "discovery"]
    qualified_ids = {
        "ui.discovery.invoices",
        "ui.parity.invoices.list",
        "ui.discovery.products",
        "ui.parity.products.list",
        "ui.discovery.customers",
        "ui.parity.contacts.list",
        "ui.discovery.bank_accounts",
        "ui.discovery.quotes",
        "ui.discovery.recurring_invoices",
        "ui.discovery.product_import",
    }
    tool_by_id = {
        "ui.discovery.invoices": "ui_invoices_list",
        "ui.parity.invoices.list": "ui_invoices_list",
        "ui.discovery.products": "ui_products_list",
        "ui.parity.products.list": "ui_products_list",
        "ui.discovery.customers": "ui_clients_list",
        "ui.parity.contacts.list": "ui_clients_list",
        "ui.discovery.bank_accounts": "ui_bank_accounts_list",
        "ui.discovery.quotes": "ui_quotes_list",
        "ui.discovery.recurring_invoices": "ui_recurring_invoices_list",
        "ui.discovery.product_import": "ui_products_import",
    }
    remaining = [row for row in workflows if row["id"] not in qualified_ids]
    qualified = [row for row in workflows if row["id"] in qualified_ids]

    assert {row["api_row_id"] for row in parity_rows} == {
        row["id"] for row in api_manifest["operations"]
    }
    assert {row["area"] for row in discovery_rows} == set(generator.UI_DISCOVERY_FAMILIES)
    assert all(row["vision_verified"] is False for row in remaining)
    assert all(row["implemented"] is False for row in remaining)
    assert all(row["contract_tested"] is False for row in remaining)
    assert all(row["live_tested"] is False for row in remaining)
    assert all(row["vision_evidence"] is None for row in workflows)
    assert all(row["parity_status"] != "not_applicable" for row in workflows)
    assert len(qualified) == 10
    for row in qualified:
        assert row["tool_name"] == tool_by_id[row["id"]]
        assert row["discovered"] is True
        assert row["implemented"] is True
        assert row["contract_tested"] is True
        assert row["live_tested"] is True
        assert row["vision_verified"] is True
        assert row["vision_evidence"] is None
        # Shell-open only: must not claim full API list filters (IR 186.3 R1).
        assert row["request_fields"] == []
        assert row["filters"] in ([], {})
        assert row["pagination"] is None
        assert row["parity_status"] == "list_shell_open_only"
    invoices_parity = next(row for row in qualified if row["id"] == "ui.parity.invoices.list")
    assert "api.invoices.list" in invoices_parity["evidence"]
    assert "filters/sort/pagination UI not producted" in invoices_parity["evidence"]
    products_parity = next(row for row in qualified if row["id"] == "ui.parity.products.list")
    assert "api.products.list" in products_parity["evidence"]
    assert "filters/sort/pagination UI not producted" in products_parity["evidence"]
    contacts_parity = next(row for row in qualified if row["id"] == "ui.parity.contacts.list")
    assert "api.contacts.list" in contacts_parity["evidence"]
    assert "filters/sort/pagination UI not producted" in contacts_parity["evidence"]
    bank_discovery = next(row for row in qualified if row["id"] == "ui.discovery.bank_accounts")
    assert bank_discovery["api_row_id"] is None
    assert "no bankAccounts API resource" in bank_discovery["evidence"]
    assert "api_bank_accounts" in bank_discovery["evidence"]
    assert checker.raw_evidence_errors(ui_manifest) == []
    assert status["source_counts"]["ui_api_parity"] == 305
    assert status["complete"] is False
    assert '"bankLineMatche"' not in json.dumps(ui_manifest)

    by_host = {rule["host"]: rule for rule in browser_egress["hosts"]}
    assert browser_egress["default_action"] == "deny"
    assert by_host["mit.billy.dk"]["browser_action"] == "allow"
    assert by_host["download.billy.dk"]["owner"] == "future_typed_download"
    assert by_host["api.billysbilling.com"]["api_client_action"] == "exclusive_allow"
    assert by_host["api.billysbilling.com"]["browser_action"] == "path_allow"
    assert any(
        rule.get("path") == "/v2/user/login" and "POST" in rule.get("methods", [])
        for rule in by_host["api.billysbilling.com"]["browser_path_allows"]
    )
    assert by_host["api.billy.dk"]["browser_action"] == "deny"


def test_checker_rejects_missing_fields_false_completeness_green_bulk_and_frames() -> None:
    """The contract checker permits red rows but rejects unsupported green claims."""

    api_manifest, ui_manifest, browser_egress, status, report = documents()

    missing_field = copy.deepcopy(api_manifest)
    del missing_field["operations"][0]["evidence"]
    assert any(
        "missing required fields evidence" in error
        for error in validation_errors(missing_field, ui_manifest, browser_egress, status, report)
    )

    false_complete = copy.deepcopy(status)
    false_complete["complete"] = True
    assert any(
        "falsely claims complete" in error
        for error in validation_errors(
            api_manifest,
            ui_manifest,
            browser_egress,
            false_complete,
            report,
            reject_false_completeness=True,
        )
    )

    green_bulk = copy.deepcopy(api_manifest)
    bulk = next(row for row in green_bulk["operations"] if row["source_kind"] == "ambiguous_bulk")
    bulk["implemented"] = True
    assert any(
        "ambiguous bulk row must stay red" in error
        for error in validation_errors(green_bulk, ui_manifest, browser_egress, status, report)
    )

    raw_frame = copy.deepcopy(ui_manifest)
    raw_frame["workflows"][0]["raw_frame_path"] = "rendered-frames/route.png"
    assert any(
        "raw browser evidence" in error
        for error in validation_errors(api_manifest, raw_frame, browser_egress, status, report)
    )

    false_report = report.replace("Complete: `false`", "Complete: `true`")
    assert any(
        "coverage/report.md is stale" in error
        for error in validation_errors(
            api_manifest,
            ui_manifest,
            browser_egress,
            status,
            false_report,
            reject_false_completeness=True,
        )
    )


def test_checker_cli_allows_offline_red_inventory_but_rejects_full_qualification() -> None:
    """Root lint can validate red inventory, while the full gate fails closed."""

    checker_path = SCRIPTS / "check_coverage.py"
    lint_result = subprocess.run(
        [sys.executable, str(checker_path), "--reject-false-completeness"],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    assert lint_result.returncode == 0, lint_result.stdout + lint_result.stderr

    complete_result = subprocess.run(
        [sys.executable, str(checker_path), "--require-complete"],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    assert complete_result.returncode == 1
    assert (
        "--require-complete requires coverage/status.json complete=true" in complete_result.stdout
    )
    assert (
        "--require-complete requires no ambiguous_bulk rows (92 remain)" in complete_result.stdout
    )


def test_checker_rejects_imperatively_registered_domain_tool_without_coverage_row(
    tmp_path: Path,
) -> None:
    """AST scanning catches the FastMCP registration form used by the real server."""

    source = tmp_path / "src" / "billy_mcp" / "server.py"
    source.parent.mkdir(parents=True)
    source.write_text(
        'mcp.tool(name="api_uninventoried_resource")(handler)\n',
        encoding="utf-8",
    )
    api_manifest, ui_manifest, browser_egress, status, report = documents()

    assert any(
        "registered domain tool lacks a coverage row: api_uninventoried_resource" in error
        for error in validation_errors(
            api_manifest, ui_manifest, browser_egress, status, report, root=tmp_path
        )
    )


def test_checker_allows_exact_execute_twin_but_rejects_unpaired_execute_tool(
    tmp_path: Path,
) -> None:
    """Execute companions are derived from preview inventory rows, never added as rows."""

    source = tmp_path / "src" / "billy_mcp" / "server.py"
    source.parent.mkdir(parents=True)
    api_manifest, ui_manifest, browser_egress, status, report = documents()

    source.write_text(
        'mcp.tool(name="api_contacts_create_execute")(handler)\n',
        encoding="utf-8",
    )
    assert (
        validation_errors(api_manifest, ui_manifest, browser_egress, status, report, root=tmp_path)
        == []
    )

    source.write_text(
        'mcp.tool(name="api_contacts_create_execute_extra")(handler)\n',
        encoding="utf-8",
    )
    assert any(
        "registered domain tool lacks a coverage row: api_contacts_create_execute_extra" in error
        for error in validation_errors(
            api_manifest, ui_manifest, browser_egress, status, report, root=tmp_path
        )
    )


def test_report_is_deterministic_and_json_yaml_has_no_offset_contract() -> None:
    """Generation is reproducible and the YAML-subset source never exposes offset paging."""

    _, _, _, status, report = documents()

    assert report == generator.render_report(status)
    api_text = (ROOT / "coverage" / "api_v2_manifest.yaml").read_text(encoding="utf-8")
    assert "offset" not in json.dumps(json.loads(api_text)).lower()
