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
    geo_na = generator.GEO_UI_NOT_APPLICABLE_ROW_COUNT
    # Prior 52 greened shells/parity + taxRates.list dual-count
    # (research158) = 53 live/vision rows without GEO NA.
    ui_shell_green = 53
    assert status["qualification"]["implemented_rows"] == (
        len(offline_evidence) + ui_shell_green + geo_na
    )
    assert status["qualification"]["contract_tested_rows"] == (
        len(offline_evidence) + ui_shell_green + geo_na
    )
    # API live remains 0 (out of scope); UI shell rows + geo NA dual-session freezes.
    assert status["qualification"]["live_tested_rows"] == ui_shell_green + geo_na
    assert status["qualification"]["vision_verified_rows"] == ui_shell_green + geo_na
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
    assert all(row["contract_tested"] is False for row in bulk_rows)
    assert all(row["live_tested"] is False for row in bulk_rows)

    saves = [row for row in bulk_rows if row["operation"] == "bulk_save"]
    deletes = [row for row in bulk_rows if row["operation"] == "bulk_delete"]
    assert len(saves) == 46
    assert len(deletes) == 46
    assert all(row["request_fields"] == ["json_object_root"] for row in saves)
    assert all(row["request_fields"] == ["ids[]"] for row in deletes)
    assert all(row["method_or_route"].startswith("AMBIGUOUS Supports: bulk save") for row in saves)
    assert all(
        row["method_or_route"].startswith("AMBIGUOUS Supports: bulk delete") for row in deletes
    )
    assert all(
        "offline shape PUT /v2/" in row["method_or_route"] and "/bulk" in row["method_or_route"]
        for row in saves
    )
    assert all(
        "offline shape DELETE /v2/" in row["method_or_route"] and "ids[]" in row["method_or_route"]
        for row in deletes
    )
    assert all("INVALID_REQUEST_BODY" in row["errors"] for row in saves)
    assert all("INVALID_DELETE_ID_ARRAY" in row["errors"] for row in deletes)
    assert all("research136 offline unauth shape freeze" in row["evidence"] for row in bulk_rows)
    assert all(
        "research137 official docs and versioned-asset exhaust" in row["evidence"]
        for row in bulk_rows
    )
    assert all("BULK_SCHEMA_UNSPECIFIED_OFFICIAL_DOCS" in row["evidence"] for row in bulk_rows)
    assert all(isinstance(row.get("qualification"), dict) for row in bulk_rows)
    assert all(row["qualification"]["kind"] == "external_contract_blocker" for row in bulk_rows)
    assert all(
        row["qualification"]["blocker_code"] == "BULK_SCHEMA_UNSPECIFIED_OFFICIAL_DOCS"
        for row in bulk_rows
    )
    assert all(row["qualification"]["live_api"] == "out_of_scope_by_user" for row in bulk_rows)
    assert all(row["qualification"]["tools_allowed"] is False for row in bulk_rows)
    # Shape hints must never look like a completed contract.
    assert all(row["response_fields"] == [] for row in bulk_rows)


def test_annual_reports_inaccessible_decision_rejects_not_applicable() -> None:
    """Dual Upsedasse keeps annual_reports red; not_applicable is rejected."""

    _, ui_manifest, _, status, _ = documents()
    annual = next(
        row for row in ui_manifest["workflows"] if row["id"] == "ui.discovery.annual_reports"
    )

    assert annual["tool_name"] == ""
    assert annual["discovered"] is False
    assert annual["implemented"] is False
    assert annual["contract_tested"] is False
    assert annual["live_tested"] is False
    assert annual["vision_verified"] is False
    assert annual["parity_status"] == "discovery_required"
    assert annual["parity_status"] != "not_applicable"
    assert "ANNUAL_REPORTS_ORG_INACCESSIBLE" in annual["evidence"]
    assert "not_applicable is rejected" in annual["evidence"]
    assert "Upsedasse" in annual["evidence"]
    assert "/:org_slug/annual_reports" in annual["method_or_route"]
    assert "ANNUAL_REPORTS_ORG_INACCESSIBLE" in annual["errors"]
    qual = annual["qualification"]
    assert qual["kind"] == "org_inaccessible"
    assert qual["blocker_code"] == "ANNUAL_REPORTS_ORG_INACCESSIBLE"
    assert qual["not_applicable_decision"] == "rejected"
    assert "non-Upsedasse" in qual["unlock_requirement"]
    assert "BULK_SCHEMA_UNSPECIFIED_OFFICIAL_DOCS" in status["qualification"]["blocker"]
    assert "external-contract" in status["qualification"]["blocker"].lower() or (
        "External-contract" in status["qualification"]["blocker"]
    )


def test_geo_ui_not_applicable_dual_session_freeze() -> None:
    """research138/139/142/143/144/147: dual-proved geo/reference UI parity is not_applicable."""

    _api_manifest, ui_manifest, _egress, status, _report = documents()
    na_rows = [
        row for row in ui_manifest["workflows"] if row.get("parity_status") == "not_applicable"
    ]
    assert len(na_rows) == generator.GEO_UI_NOT_APPLICABLE_ROW_COUNT
    expected_prefixes = generator.GEO_UI_NOT_APPLICABLE_API_PREFIXES
    for row in na_rows:
        api_id = row["api_row_id"]
        assert any(api_id.startswith(prefix) for prefix in expected_prefixes)
        assert row["tool_name"] == ""
        assert row["discovered"] is True
        assert row["implemented"] is True
        assert row["contract_tested"] is True
        assert row["live_tested"] is True
        assert row["vision_verified"] is True
        assert row["vision_evidence"] is None
        assert row["request_fields"] == []
        assert row["filters"] in ([], {})
        assert row["pagination"] is None
        qual = row["qualification"]
        assert qual["kind"] == "ui_not_applicable"
        assert qual["evidence_code"] == generator.GEO_UI_NOT_APPLICABLE_EVIDENCE_CODE
        assert qual["not_applicable_decision"] == "accepted"
        assert qual["sessions"] == "dual_independent_ephemeral"
        resource = api_id.split(".", 2)[1]
        if api_id in generator.GEO_UI_NOT_APPLICABLE_RESEARCH150_SPECIAL_IDS:
            assert "research150" in qual["evidence_ref"]
            assert "research150" in row["evidence"]
            assert "Levering af faktura pr. e-mail" in row["evidence"]
        elif resource in generator.GEO_UI_NOT_APPLICABLE_RESEARCH149_RESOURCES:
            assert "research149" in qual["evidence_ref"]
            assert "research149" in row["evidence"]
        elif resource in generator.GEO_UI_NOT_APPLICABLE_RESEARCH148_RESOURCES:
            assert "research148" in qual["evidence_ref"]
            assert "research148" in row["evidence"]
        elif resource in generator.GEO_UI_NOT_APPLICABLE_RESEARCH147_RESOURCES:
            assert "research147" in qual["evidence_ref"]
            assert "research147" in row["evidence"]
        elif resource in generator.GEO_UI_NOT_APPLICABLE_RESEARCH144_RESOURCES:
            assert "research144" in qual["evidence_ref"]
            assert "research144" in row["evidence"]
        elif resource in generator.GEO_UI_NOT_APPLICABLE_RESEARCH143_RESOURCES:
            assert "research143" in qual["evidence_ref"]
            assert "research143" in row["evidence"]
        elif resource in generator.GEO_UI_NOT_APPLICABLE_RESEARCH142_RESOURCES:
            assert "research142" in qual["evidence_ref"]
            assert "research142" in row["evidence"]
        elif resource in generator.GEO_UI_NOT_APPLICABLE_RESEARCH139_RESOURCES:
            assert "research139" in qual["evidence_ref"]
            assert "research139" in row["evidence"]
        else:
            assert "research138" in qual["evidence_ref"]
            assert "research138" in row["evidence"]
        assert generator.GEO_UI_NOT_APPLICABLE_EVIDENCE_CODE in row["evidence"]
        assert "not_applicable accepted" in row["method_or_route"]
        assert "ui_cities" not in row["tool_name"]
        assert "ui_currencies" not in row["tool_name"]
        assert "ui_locales" not in row["tool_name"]
        assert "ui_account_natures" not in row["tool_name"]
        assert "ui_balance_modifiers" not in row["tool_name"]
        assert "ui_account_groups" not in row["tool_name"]
        assert "ui_contact_balance_postings" not in row["tool_name"]
        assert "ui_contact_balance_payments" not in row["tool_name"]
        assert "ui_contact_persons" not in row["tool_name"]
        assert "ui_invoice_late_fees" not in row["tool_name"]
        assert "ui_invoice_reminder_associations" not in row["tool_name"]
        assert "ui_invoice_deliveries" not in row["tool_name"]
        assert "ui_invoice_logs" not in row["tool_name"]
        assert qual.get("deferred_families") in (None, [])
    # currencies/locales dual-proved (research139) — no longer discovery_required
    currency_locale = [
        row
        for row in ui_manifest["workflows"]
        if str(row.get("api_row_id") or "").startswith(("api.currencies.", "api.locales."))
    ]
    assert len(currency_locale) == 12
    assert all(row["parity_status"] == "not_applicable" for row in currency_locale)
    assert all(row["implemented"] is True for row in currency_locale)
    assert all(row["live_tested"] is True for row in currency_locale)
    assert all(row["tool_name"] == "" for row in currency_locale)
    # accountNatures/balanceModifiers dual-proved (research142)
    natures_modifiers = [
        row
        for row in ui_manifest["workflows"]
        if str(row.get("api_row_id") or "").startswith(
            ("api.accountNatures.", "api.balanceModifiers.")
        )
    ]
    assert len(natures_modifiers) == 12
    assert all(row["parity_status"] == "not_applicable" for row in natures_modifiers)
    assert all(row["implemented"] is True for row in natures_modifiers)
    assert all(row["live_tested"] is True for row in natures_modifiers)
    assert all(row["tool_name"] == "" for row in natures_modifiers)
    # accountGroups dual-proved (research143) — includes singular delete (7 ops)
    account_groups = [
        row
        for row in ui_manifest["workflows"]
        if str(row.get("api_row_id") or "").startswith("api.accountGroups.")
    ]
    assert len(account_groups) == 7
    assert all(row["parity_status"] == "not_applicable" for row in account_groups)
    assert all(row["implemented"] is True for row in account_groups)
    assert all(row["live_tested"] is True for row in account_groups)
    assert all(row["tool_name"] == "" for row in account_groups)
    # research144 join/meta package (6 + 7 + 6 = 19)
    join_meta = [
        row
        for row in ui_manifest["workflows"]
        if str(row.get("api_row_id") or "").startswith(
            (
                "api.contactBalancePostings.",
                "api.invoiceReminderAssociations.",
                "api.invoiceLateFees.",
            )
        )
    ]
    assert len(join_meta) == 19
    assert all(row["parity_status"] == "not_applicable" for row in join_meta)
    assert all(row["implemented"] is True for row in join_meta)
    assert all(row["live_tested"] is True for row in join_meta)
    assert all(row["tool_name"] == "" for row in join_meta)
    # research147 contactBalancePayments package (6 ops; not bankPayments)
    contact_balance_payments = [
        row
        for row in ui_manifest["workflows"]
        if str(row.get("api_row_id") or "").startswith("api.contactBalancePayments.")
    ]
    assert len(contact_balance_payments) == 6
    assert all(row["parity_status"] == "not_applicable" for row in contact_balance_payments)
    assert all(row["implemented"] is True for row in contact_balance_payments)
    assert all(row["live_tested"] is True for row in contact_balance_payments)
    assert all(row["vision_verified"] is True for row in contact_balance_payments)
    assert all(row["tool_name"] == "" for row in contact_balance_payments)
    assert all("research147" in (row.get("evidence") or "") for row in contact_balance_payments)
    # research148 contactPersons package (7 ops including singular delete)
    contact_persons = [
        row
        for row in ui_manifest["workflows"]
        if str(row.get("api_row_id") or "").startswith("api.contactPersons.")
    ]
    assert len(contact_persons) == 7
    assert all(row["parity_status"] == "not_applicable" for row in contact_persons)
    assert all(row["implemented"] is True for row in contact_persons)
    assert all(row["live_tested"] is True for row in contact_persons)
    assert all(row["vision_verified"] is True for row in contact_persons)
    assert all(row["tool_name"] == "" for row in contact_persons)
    assert all("research148" in (row.get("evidence") or "") for row in contact_persons)
    # research149 invoiceReminders package (5 ops; no singular update/delete)
    invoice_reminders = [
        row
        for row in ui_manifest["workflows"]
        if str(row.get("api_row_id") or "").startswith("api.invoiceReminders.")
    ]
    assert len(invoice_reminders) == 5
    assert all(row["parity_status"] == "not_applicable" for row in invoice_reminders)
    assert all(row["implemented"] is True for row in invoice_reminders)
    assert all(row["live_tested"] is True for row in invoice_reminders)
    assert all(row["vision_verified"] is True for row in invoice_reminders)
    assert all(row["tool_name"] == "" for row in invoice_reminders)
    assert all("research149" in (row.get("evidence") or "") for row in invoice_reminders)
    # research150 specials invoice_delivery + invoice_logs only (exact ids)
    specials_delivery_logs = [
        row
        for row in ui_manifest["workflows"]
        if str(row.get("api_row_id") or "")
        in generator.GEO_UI_NOT_APPLICABLE_RESEARCH150_SPECIAL_IDS
    ]
    assert len(specials_delivery_logs) == 2
    assert all(row["parity_status"] == "not_applicable" for row in specials_delivery_logs)
    assert all(row["implemented"] is True for row in specials_delivery_logs)
    assert all(row["live_tested"] is True for row in specials_delivery_logs)
    assert all(row["vision_verified"] is True for row in specials_delivery_logs)
    assert all(row["tool_name"] == "" for row in specials_delivery_logs)
    assert all("research150" in (row.get("evidence") or "") for row in specials_delivery_logs)
    assert all(
        "Levering af faktura pr. e-mail" in (row.get("evidence") or "")
        for row in specials_delivery_logs
    )
    # special.user_get dual-counted to settings Profil (research151); not NA
    user_get_parity = [
        row
        for row in ui_manifest["workflows"]
        if str(row.get("api_row_id") or "") == "api.special.user_get"
    ]
    assert len(user_get_parity) == 1
    assert user_get_parity[0]["parity_status"] == "shell_open_only"
    assert user_get_parity[0]["tool_name"] == "ui_settings_user_open"
    assert user_get_parity[0]["live_tested"] is True
    assert "research151" in (user_get_parity[0].get("evidence") or "")
    # special.files_upload dual-counted to Bilag upload surface (research155)
    files_upload_parity = [
        row
        for row in ui_manifest["workflows"]
        if str(row.get("api_row_id") or "") == "api.special.files_upload"
    ]
    assert len(files_upload_parity) == 1
    assert files_upload_parity[0]["parity_status"] == "list_shell_open_only"
    assert files_upload_parity[0]["tool_name"] == "ui_uploads_list"
    assert files_upload_parity[0]["live_tested"] is True
    assert "research155" in (files_upload_parity[0].get("evidence") or "")
    # sibling special invoice_email stays red (not greened by accidental special prefix)
    invoice_email_sibling = [
        row
        for row in ui_manifest["workflows"]
        if str(row.get("api_row_id") or "") == "api.special.invoice_email"
    ]
    assert len(invoice_email_sibling) == 1
    assert invoice_email_sibling[0].get("parity_status") != "not_applicable"
    assert invoice_email_sibling[0].get("live_tested") is not True
    # special.user_organizations dual-counted to Virksomheder shell (research152)
    user_orgs_parity = [
        row
        for row in ui_manifest["workflows"]
        if str(row.get("api_row_id") or "") == "api.special.user_organizations"
    ]
    assert len(user_orgs_parity) == 1
    assert user_orgs_parity[0]["parity_status"] == "shell_open_only"
    assert user_orgs_parity[0]["tool_name"] == "ui_settings_user_organizations_open"
    assert user_orgs_parity[0]["live_tested"] is True
    assert "research152" in (user_orgs_parity[0].get("evidence") or "")
    # associations remain NA green (research144) — separate resource
    reminder_assoc = [
        row
        for row in ui_manifest["workflows"]
        if str(row.get("api_row_id") or "").startswith("api.invoiceReminderAssociations.")
    ]
    assert len(reminder_assoc) == 7
    assert all(row["parity_status"] == "not_applicable" for row in reminder_assoc)
    # attachments stays red this slice (Bilag greened → reject pure NA)
    attachments = [
        row
        for row in ui_manifest["workflows"]
        if str(row.get("api_row_id") or "").startswith("api.attachments.")
    ]
    assert attachments
    assert all(row.get("parity_status") != "not_applicable" for row in attachments)
    assert all(row.get("live_tested") is not True for row in attachments)
    # productPrices must stay red this slice (research143/144/147/148/149 rejected NA)
    product_prices = [
        row
        for row in ui_manifest["workflows"]
        if str(row.get("api_row_id") or "").startswith("api.productPrices.")
    ]
    assert product_prices
    assert all(row.get("parity_status") != "not_applicable" for row in product_prices)
    assert all(row.get("live_tested") is not True for row in product_prices)
    # related-shell families must stay red (research144/147 rejected pure NA).
    # taxRates.list dual-counted to Momssatser shell (research158); residual
    # taxRates ops stay red below.
    for prefix in (
        "api.bankLineMatches.",
        "api.bankLineSubjectAssociations.",
        "api.bankPayments.",
        "api.daybookBalanceAccounts.",
        "api.postings.",
        "api.salesTaxRules.",
        "api.salesTaxRulesets.",
        "api.files.",
    ):
        related = [
            row
            for row in ui_manifest["workflows"]
            if str(row.get("api_row_id") or "").startswith(prefix)
        ]
        assert related, prefix
        assert all(row.get("parity_status") != "not_applicable" for row in related)
        assert all(row.get("live_tested") is not True for row in related)
    tax_rates_rows = [
        row
        for row in ui_manifest["workflows"]
        if str(row.get("api_row_id") or "").startswith("api.taxRates.")
    ]
    assert tax_rates_rows
    assert all(row.get("parity_status") != "not_applicable" for row in tax_rates_rows)
    tax_rates_list = [row for row in tax_rates_rows if row.get("api_row_id") == "api.taxRates.list"]
    tax_rates_residual = [
        row for row in tax_rates_rows if row.get("api_row_id") != "api.taxRates.list"
    ]
    assert len(tax_rates_list) == 1
    assert tax_rates_list[0].get("live_tested") is True
    assert tax_rates_list[0].get("tool_name") == "ui_settings_vat_open"
    assert all(row.get("live_tested") is not True for row in tax_rates_residual)
    assert status["complete"] is False
    assert (
        status["qualification"]["live_tested_rows"]
        == 53 + generator.GEO_UI_NOT_APPLICABLE_ROW_COUNT
    )
    assert status["qualification"]["live_tested_rows"] == 153
    assert generator.GEO_UI_NOT_APPLICABLE_ROW_COUNT == 100


def test_ui_parity_and_egress_are_complete_but_visibly_red() -> None:
    """UI discovery does not use unsupported not-applicable or frame evidence."""

    api_manifest, ui_manifest, browser_egress, status, _ = documents()
    workflows = ui_manifest["workflows"]
    parity_rows = [row for row in workflows if row["workflow_kind"] == "api_parity"]
    discovery_rows = [row for row in workflows if row["workflow_kind"] == "discovery"]
    qualified_ids = {
        "ui.discovery.invoices",
        "ui.parity.invoices.list",
        "ui.discovery.invoices_create",
        "ui.parity.invoices.create",
        "ui.discovery.products",
        "ui.parity.products.list",
        "ui.discovery.customers",
        "ui.parity.contacts.list",
        "ui.discovery.bank_accounts",
        "ui.discovery.quotes",
        "ui.discovery.recurring_invoices",
        "ui.discovery.product_import",
        "ui.discovery.suppliers",
        "ui.discovery.purchases",
        "ui.parity.bills.list",
        "ui.discovery.bills_create",
        "ui.parity.bills.create",
        "ui.discovery.debtor_balances",
        "ui.discovery.creditor_balances",
        "ui.discovery.uploads",
        "ui.parity.special.files_upload",
        "ui.discovery.receipt_inbox",
        "ui.discovery.bank_reconciliation",
        "ui.discovery.financing",
        "ui.discovery.daybooks",
        "ui.parity.daybooks.list",
        "ui.parity.daybooks.create",
        "ui.discovery.transactions",
        "ui.parity.transactions.list",
        "ui.discovery.reports",
        "ui.discovery.vat_declarations",
        "ui.parity.salesTaxReturns.list",
        "ui.discovery.exports",
        "ui.discovery.saft_exports",
        "ui.discovery.addons",
        "ui.discovery.integrations",
        "ui.discovery.inventory",
        "ui.discovery.settings_company",
        "ui.parity.organizations.list",
        "ui.discovery.settings_accounting",
        "ui.parity.accounts.list",
        "ui.discovery.settings_invoicing",
        "ui.discovery.settings_user",
        "ui.parity.special.user_get",
        "ui.discovery.settings_user_organizations",
        "ui.parity.special.user_organizations",
        "ui.discovery.settings_vat",
        "ui.parity.taxRates.list",
        "ui.discovery.settings_users",
        "ui.parity.users.list",
        "ui.discovery.settings_access_token",
        "ui.discovery.settings_beta",
        "ui.discovery.settings_subscription",
    }
    tool_by_id = {
        "ui.discovery.invoices": "ui_invoices_list",
        "ui.parity.invoices.list": "ui_invoices_list",
        "ui.discovery.invoices_create": "ui_invoices_create_open",
        "ui.parity.invoices.create": "ui_invoices_create_open",
        "ui.discovery.products": "ui_products_list",
        "ui.parity.products.list": "ui_products_list",
        "ui.discovery.customers": "ui_clients_list",
        "ui.parity.contacts.list": "ui_clients_list",
        "ui.discovery.bank_accounts": "ui_bank_accounts_list",
        "ui.discovery.quotes": "ui_quotes_list",
        "ui.discovery.recurring_invoices": "ui_recurring_invoices_list",
        "ui.discovery.product_import": "ui_products_import",
        "ui.discovery.suppliers": "ui_suppliers_list",
        "ui.discovery.purchases": "ui_bills_list",
        "ui.parity.bills.list": "ui_bills_list",
        "ui.discovery.bills_create": "ui_bills_create_open",
        "ui.parity.bills.create": "ui_bills_create_open",
        "ui.discovery.debtor_balances": "ui_debtor_balances_list",
        "ui.discovery.creditor_balances": "ui_creditor_balances_list",
        "ui.discovery.uploads": "ui_uploads_list",
        "ui.parity.special.files_upload": "ui_uploads_list",
        "ui.discovery.receipt_inbox": "ui_receipt_inbox_list",
        "ui.discovery.bank_reconciliation": "ui_bank_reconciliation_open",
        "ui.discovery.financing": "ui_financing_open",
        "ui.discovery.daybooks": "ui_daybooks_open",
        "ui.parity.daybooks.list": "ui_daybooks_open",
        "ui.parity.daybooks.create": "ui_daybooks_open",
        "ui.discovery.transactions": "ui_transactions_list",
        "ui.parity.transactions.list": "ui_transactions_list",
        "ui.discovery.reports": "ui_reports_open",
        "ui.discovery.vat_declarations": "ui_vat_declarations_list",
        "ui.parity.salesTaxReturns.list": "ui_vat_declarations_list",
        "ui.discovery.exports": "ui_exports_open",
        "ui.discovery.saft_exports": "ui_saft_exports_open",
        "ui.discovery.addons": "ui_addons_open",
        "ui.discovery.integrations": "ui_integrations_open",
        "ui.discovery.inventory": "ui_inventory_open",
        "ui.discovery.settings_company": "ui_settings_company_open",
        "ui.parity.organizations.list": "ui_settings_company_open",
        "ui.discovery.settings_accounting": "ui_settings_accounting_open",
        "ui.parity.accounts.list": "ui_settings_accounting_open",
        "ui.discovery.settings_invoicing": "ui_settings_invoicing_open",
        "ui.discovery.settings_user": "ui_settings_user_open",
        "ui.parity.special.user_get": "ui_settings_user_open",
        "ui.discovery.settings_user_organizations": "ui_settings_user_organizations_open",
        "ui.parity.special.user_organizations": "ui_settings_user_organizations_open",
        "ui.discovery.settings_vat": "ui_settings_vat_open",
        "ui.parity.taxRates.list": "ui_settings_vat_open",
        "ui.discovery.settings_users": "ui_settings_users_open",
        "ui.parity.users.list": "ui_settings_users_open",
        "ui.discovery.settings_access_token": "ui_settings_access_token_open",
        "ui.discovery.settings_beta": "ui_settings_beta_open",
        "ui.discovery.settings_subscription": "ui_settings_subscription_open",
    }
    geo_na_rows = [row for row in workflows if row.get("parity_status") == "not_applicable"]
    geo_na_ids = {row["id"] for row in geo_na_rows}
    remaining = [
        row for row in workflows if row["id"] not in qualified_ids and row["id"] not in geo_na_ids
    ]
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
    assert all(row["parity_status"] != "not_applicable" for row in remaining)
    assert all(row["parity_status"] != "not_applicable" for row in qualified)
    assert len(qualified) == 53
    assert len(geo_na_rows) == generator.GEO_UI_NOT_APPLICABLE_ROW_COUNT
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
        assert row["parity_status"] in {
            "list_shell_open_only",
            "shell_open_only",
            "form_open_only",
            "soft_empty_shell_observed",
        }
    invoices_parity = next(row for row in qualified if row["id"] == "ui.parity.invoices.list")
    assert "api.invoices.list" in invoices_parity["evidence"]
    assert "filters/sort/pagination UI not producted" in invoices_parity["evidence"]
    products_parity = next(row for row in qualified if row["id"] == "ui.parity.products.list")
    assert "api.products.list" in products_parity["evidence"]
    assert "filters/sort/pagination UI not producted" in products_parity["evidence"]
    contacts_parity = next(row for row in qualified if row["id"] == "ui.parity.contacts.list")
    assert "api.contacts.list" in contacts_parity["evidence"]
    assert "filters/sort/pagination UI not producted" in contacts_parity["evidence"]
    bills_parity = next(row for row in qualified if row["id"] == "ui.parity.bills.list")
    assert "api.bills.list" in bills_parity["evidence"]
    assert "filters/sort/pagination UI not producted" in bills_parity["evidence"]
    transactions_parity = next(
        row for row in qualified if row["id"] == "ui.parity.transactions.list"
    )
    assert "api.transactions.list" in transactions_parity["evidence"]
    assert "filters/sort/pagination UI not producted" in transactions_parity["evidence"]
    sales_tax_returns_parity = next(
        row for row in qualified if row["id"] == "ui.parity.salesTaxReturns.list"
    )
    assert sales_tax_returns_parity["api_row_id"] == "api.salesTaxReturns.list"
    assert sales_tax_returns_parity["tool_name"] == "ui_vat_declarations_list"
    assert "api.salesTaxReturns.list" in sales_tax_returns_parity["evidence"]
    assert "filters/sort/pagination UI not producted" in sales_tax_returns_parity["evidence"]
    assert "research140" in sales_tax_returns_parity["evidence"]
    for red_id in (
        "ui.parity.salesTaxReturns.get",
        "ui.parity.salesTaxReturns.update",
        "ui.parity.salesTaxReturns.bulk_save",
        "ui.parity.salesTaxReturns.bulk_delete",
    ):
        red_row = next(row for row in remaining if row["id"] == red_id)
        assert red_row["discovered"] is False
        assert red_row["live_tested"] is False
        assert red_row["parity_status"] == "discovery_required"
    users_parity = next(row for row in qualified if row["id"] == "ui.parity.users.list")
    assert users_parity["api_row_id"] == "api.users.list"
    assert users_parity["tool_name"] == "ui_settings_users_open"
    assert users_parity["parity_status"] == "shell_open_only"
    assert "api.users.list" in users_parity["evidence"]
    assert "filters/sort/pagination UI not producted" in users_parity["evidence"]
    assert "research141" in users_parity["evidence"]
    for red_id in (
        "ui.parity.users.get",
        "ui.parity.users.update",
        "ui.parity.users.bulk_save",
        "ui.parity.users.bulk_delete",
    ):
        red_row = next(row for row in remaining if row["id"] == red_id)
        assert red_row["discovered"] is False
        assert red_row["live_tested"] is False
        assert red_row["parity_status"] == "discovery_required"
    accounts_parity = next(row for row in qualified if row["id"] == "ui.parity.accounts.list")
    assert accounts_parity["api_row_id"] == "api.accounts.list"
    assert accounts_parity["tool_name"] == "ui_settings_accounting_open"
    assert accounts_parity["parity_status"] == "shell_open_only"
    assert "api.accounts.list" in accounts_parity["evidence"]
    assert "filters/sort/pagination UI not producted" in accounts_parity["evidence"]
    assert "research145" in accounts_parity["evidence"]
    for red_id in (
        "ui.parity.accounts.get",
        "ui.parity.accounts.create",
        "ui.parity.accounts.update",
        "ui.parity.accounts.delete",
        "ui.parity.accounts.bulk_save",
        "ui.parity.accounts.bulk_delete",
    ):
        red_row = next(row for row in remaining if row["id"] == red_id)
        assert red_row["discovered"] is False
        assert red_row["live_tested"] is False
        assert red_row["parity_status"] == "discovery_required"
    tax_rates_parity = next(row for row in qualified if row["id"] == "ui.parity.taxRates.list")
    assert tax_rates_parity["api_row_id"] == "api.taxRates.list"
    assert tax_rates_parity["tool_name"] == "ui_settings_vat_open"
    assert tax_rates_parity["parity_status"] == "shell_open_only"
    assert "api.taxRates.list" in tax_rates_parity["evidence"]
    assert "filters/sort/pagination UI not producted" in tax_rates_parity["evidence"]
    assert "research158" in tax_rates_parity["evidence"]
    for red_id in (
        "ui.parity.taxRates.get",
        "ui.parity.taxRates.create",
        "ui.parity.taxRates.update",
        "ui.parity.taxRates.delete",
        "ui.parity.taxRates.bulk_save",
        "ui.parity.taxRates.bulk_delete",
    ):
        red_row = next(row for row in remaining if row["id"] == red_id)
        assert red_row["discovered"] is False
        assert red_row["live_tested"] is False
        assert red_row["parity_status"] == "discovery_required"
    organizations_parity = next(
        row for row in qualified if row["id"] == "ui.parity.organizations.list"
    )
    assert organizations_parity["api_row_id"] == "api.organizations.list"
    assert organizations_parity["tool_name"] == "ui_settings_company_open"
    assert organizations_parity["parity_status"] == "shell_open_only"
    assert "api.organizations.list" in organizations_parity["evidence"]
    assert "filters/sort/pagination UI not producted" in organizations_parity["evidence"]
    assert "research146" in organizations_parity["evidence"]
    for red_id in (
        "ui.parity.organizations.get",
        "ui.parity.organizations.create",
        "ui.parity.organizations.update",
        "ui.parity.organizations.bulk_save",
        "ui.parity.organizations.bulk_delete",
    ):
        red_row = next(row for row in remaining if row["id"] == red_id)
        assert red_row["discovered"] is False
        assert red_row["live_tested"] is False
        assert red_row["parity_status"] == "discovery_required"
    daybooks_parity = next(row for row in qualified if row["id"] == "ui.parity.daybooks.list")
    assert daybooks_parity["api_row_id"] == "api.daybooks.list"
    assert daybooks_parity["tool_name"] == "ui_daybooks_open"
    assert daybooks_parity["parity_status"] == "shell_open_only"
    assert "api.daybooks.list" in daybooks_parity["evidence"]
    assert "filters/sort/pagination UI not producted" in daybooks_parity["evidence"]
    assert "research156" in daybooks_parity["evidence"]
    daybooks_create_parity = next(
        row for row in qualified if row["id"] == "ui.parity.daybooks.create"
    )
    assert daybooks_create_parity["api_row_id"] == "api.daybooks.create"
    assert daybooks_create_parity["tool_name"] == "ui_daybooks_open"
    assert daybooks_create_parity["parity_status"] == "form_open_only"
    assert "api.daybooks.create" in daybooks_create_parity["evidence"]
    assert "research157" in daybooks_create_parity["evidence"]
    assert daybooks_create_parity["sensitivity"] == "medium"
    daybooks_discovery = next(row for row in qualified if row["id"] == "ui.discovery.daybooks")
    assert daybooks_discovery["tool_name"] == "ui_daybooks_open"
    assert daybooks_discovery["api_row_id"] is None
    for red_id in (
        "ui.parity.daybooks.get",
        "ui.parity.daybooks.update",
        "ui.parity.daybooks.delete",
        "ui.parity.daybooks.bulk_save",
        "ui.parity.daybooks.bulk_delete",
    ):
        red_row = next(row for row in remaining if row["id"] == red_id)
        assert red_row["discovered"] is False
        assert red_row["live_tested"] is False
        assert red_row["parity_status"] == "discovery_required"
    user_get_special_parity = next(
        row for row in qualified if row["id"] == "ui.parity.special.user_get"
    )
    assert user_get_special_parity["api_row_id"] == "api.special.user_get"
    assert user_get_special_parity["tool_name"] == "ui_settings_user_open"
    assert user_get_special_parity["parity_status"] == "shell_open_only"
    assert "api.special.user_get" in user_get_special_parity["evidence"]
    assert "research151" in user_get_special_parity["evidence"]
    user_orgs_special_parity = next(
        row for row in qualified if row["id"] == "ui.parity.special.user_organizations"
    )
    assert user_orgs_special_parity["api_row_id"] == "api.special.user_organizations"
    assert user_orgs_special_parity["tool_name"] == "ui_settings_user_organizations_open"
    assert user_orgs_special_parity["parity_status"] == "shell_open_only"
    assert "api.special.user_organizations" in user_orgs_special_parity["evidence"]
    assert "research152" in user_orgs_special_parity["evidence"]
    invoices_create_parity = next(
        row for row in qualified if row["id"] == "ui.parity.invoices.create"
    )
    assert invoices_create_parity["api_row_id"] == "api.invoices.create"
    assert invoices_create_parity["tool_name"] == "ui_invoices_create_open"
    assert invoices_create_parity["parity_status"] == "form_open_only"
    assert "api.invoices.create" in invoices_create_parity["evidence"]
    assert "research153" in invoices_create_parity["evidence"]
    invoices_create_discovery = next(
        row for row in qualified if row["id"] == "ui.discovery.invoices_create"
    )
    assert invoices_create_discovery["tool_name"] == "ui_invoices_create_open"
    assert invoices_create_discovery["api_row_id"] is None
    bills_create_parity = next(row for row in qualified if row["id"] == "ui.parity.bills.create")
    assert bills_create_parity["api_row_id"] == "api.bills.create"
    assert bills_create_parity["tool_name"] == "ui_bills_create_open"
    assert bills_create_parity["parity_status"] == "form_open_only"
    assert "api.bills.create" in bills_create_parity["evidence"]
    assert "research154" in bills_create_parity["evidence"]
    bills_create_discovery = next(
        row for row in qualified if row["id"] == "ui.discovery.bills_create"
    )
    assert bills_create_discovery["tool_name"] == "ui_bills_create_open"
    assert bills_create_discovery["api_row_id"] is None
    files_upload_special_parity = next(
        row for row in qualified if row["id"] == "ui.parity.special.files_upload"
    )
    assert files_upload_special_parity["api_row_id"] == "api.special.files_upload"
    assert files_upload_special_parity["tool_name"] == "ui_uploads_list"
    assert files_upload_special_parity["parity_status"] == "list_shell_open_only"
    assert "api.special.files_upload" in files_upload_special_parity["evidence"]
    assert "research155" in files_upload_special_parity["evidence"]
    assert "file_input_present" in files_upload_special_parity["response_fields"]
    uploads_discovery = next(row for row in qualified if row["id"] == "ui.discovery.uploads")
    assert uploads_discovery["tool_name"] == "ui_uploads_list"
    assert uploads_discovery["api_row_id"] is None
    assert "file_input_present" in uploads_discovery["response_fields"]
    for red_id in (
        "ui.parity.invoices.get",
        "ui.parity.invoices.update",
        "ui.parity.invoices.delete",
        "ui.parity.invoices.bulk_save",
        "ui.parity.invoices.bulk_delete",
        "ui.parity.special.invoice_email",
        "ui.parity.files.get",
        "ui.parity.files.list",
        "ui.parity.files.create",
        "ui.parity.attachments.get",
        "ui.parity.attachments.list",
        "ui.parity.bills.get",
        "ui.parity.bills.update",
        "ui.parity.bills.delete",
        "ui.parity.bills.bulk_save",
        "ui.parity.bills.bulk_delete",
    ):
        red_row = next(row for row in remaining if row["id"] == red_id)
        assert red_row["discovered"] is False
        assert red_row["live_tested"] is False
        assert red_row["parity_status"] == "discovery_required"
    company_discovery = next(
        row for row in qualified if row["id"] == "ui.discovery.settings_company"
    )
    assert company_discovery["api_row_id"] is None
    settings_user_discovery = next(
        row for row in qualified if row["id"] == "ui.discovery.settings_user"
    )
    assert settings_user_discovery["api_row_id"] is None
    settings_user_organizations_discovery = next(
        row for row in qualified if row["id"] == "ui.discovery.settings_user_organizations"
    )
    assert settings_user_organizations_discovery["api_row_id"] is None
    assert settings_user_organizations_discovery["tool_name"] == (
        "ui_settings_user_organizations_open"
    )
    accounting_discovery = next(
        row for row in qualified if row["id"] == "ui.discovery.settings_accounting"
    )
    assert accounting_discovery["api_row_id"] is None
    transactions_discovery = next(
        row for row in qualified if row["id"] == "ui.discovery.transactions"
    )
    assert transactions_discovery["api_row_id"] is None
    purchases_discovery = next(row for row in qualified if row["id"] == "ui.discovery.purchases")
    assert purchases_discovery["api_row_id"] is None
    assert (
        "purchases maps to bills route" in purchases_discovery["evidence"]
        or "bills" in purchases_discovery["method_or_route"]
    )
    debtor_discovery = next(row for row in qualified if row["id"] == "ui.discovery.debtor_balances")
    assert debtor_discovery["api_row_id"] is None
    assert "debtorbalance" in debtor_discovery["method_or_route"]
    assert (
        "no invent api_debtor" in debtor_discovery["evidence"]
        or "api_debtor_balances" in debtor_discovery["evidence"]
    )
    creditor_discovery = next(
        row for row in qualified if row["id"] == "ui.discovery.creditor_balances"
    )
    assert creditor_discovery["api_row_id"] is None
    assert "creditorbalance" in creditor_discovery["method_or_route"]
    assert (
        "no invent api_creditor" in creditor_discovery["evidence"]
        or "api_creditor_balances" in creditor_discovery["evidence"]
    )
    uploads_discovery = next(row for row in qualified if row["id"] == "ui.discovery.uploads")
    assert uploads_discovery["api_row_id"] is None
    assert "uploads" in uploads_discovery["method_or_route"]
    assert (
        "no invent api_uploads" in uploads_discovery["evidence"]
        or "api_uploads" in uploads_discovery["evidence"]
        or "api_bilag" in uploads_discovery["evidence"]
    )
    assert "Upload filer" in uploads_discovery["evidence"] or "upload_action" in str(
        uploads_discovery["response_fields"]
    )
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
