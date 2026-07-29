#!/usr/bin/env python3
"""Generate the immutable Phase 0 coverage inventories and their red-only report.

The ``.yaml`` artifacts are JSON documents, which is a valid YAML subset. This
keeps the inventory dependency-free while preserving a machine-readable YAML
contract for later tooling.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DOCS_URL = "https://www.billy.dk/api/"
DOCS_ETAG = "hsisik4g9p3603"
DOCS_MD5 = "c2efda0ee4cf9cf200e14910c5fc6996"
TEST_REFERENCE = "tests/coverage/test_coverage_inventory.py"
COMMON_ERRORS = ["AUTHENTICATION_REQUIRED", "OAUTH_INVALID_ACCESS_TOKEN"]
PAGING = {
    "parameters": ["page", "pageSize"],
    "page_size_default": 1000,
    "page_size_maximum": 1000,
    "response_fields": [
        "meta.paging.page",
        "meta.paging.pageCount",
        "meta.paging.pageSize",
        "meta.paging.total",
        "meta.paging.firstUrl",
        "meta.paging.previousUrl",
        "meta.paging.nextUrl",
        "meta.paging.lastUrl",
    ],
}

# The official Supports matrix frozen in the cited parent research brief. Every
# listed resource has get, list, bulk save, and bulk delete; the booleans are
# the only clear create/update/delete flags.
RESOURCE_SUPPORTS: tuple[tuple[str, bool, bool, bool], ...] = (
    ("accountGroups", True, True, True),
    ("accountNatures", True, True, False),
    ("accounts", True, True, True),
    ("attachments", True, True, True),
    ("balanceModifiers", True, True, False),
    ("bankLineMatches", True, True, True),
    ("bankLines", True, True, True),
    ("bankLineSubjectAssociations", True, True, True),
    ("bankPayments", True, True, True),
    ("billLines", True, True, True),
    ("bills", True, True, True),
    ("cities", True, True, False),
    ("contactBalancePayments", True, True, False),
    ("contactBalancePostings", True, True, False),
    ("contactPersons", True, True, True),
    ("contacts", True, True, True),
    ("countryGroups", True, True, False),
    ("countries", True, True, False),
    ("currencies", True, True, False),
    ("daybookBalanceAccounts", True, True, True),
    ("daybooks", True, True, True),
    ("daybookTransactionLines", True, True, True),
    ("daybookTransactions", True, True, True),
    ("files", True, False, False),
    ("invoiceLateFees", True, True, False),
    ("invoiceLines", True, True, True),
    ("invoiceReminderAssociations", True, True, True),
    ("invoiceReminders", True, False, False),
    ("invoices", True, True, True),
    ("locales", True, True, False),
    ("organizations", True, True, False),
    ("postings", True, True, False),
    ("productPrices", True, True, True),
    ("products", True, True, True),
    ("salesTaxAccounts", True, True, True),
    ("salesTaxMetaFields", True, True, True),
    ("salesTaxPayments", True, True, False),
    ("salesTaxReturns", False, True, False),
    ("salesTaxRules", True, True, True),
    ("salesTaxRulesets", True, True, True),
    ("states", True, True, False),
    ("taxRateDeductionComponents", True, True, True),
    ("taxRates", True, True, True),
    ("transactions", True, True, True),
    ("users", False, True, False),
    ("zipcodes", True, True, False),
)

INVOICE_FILTERS: dict[str, Any] = {
    "sortProperty": [
        "entryDate",
        "dueDate",
        "createdTime",
        "invoiceNo",
        "lineDescription",
        "amount",
        "grossAmount",
        "balance",
        "contact.name",
        "approvedTime",
        "orderNo",
    ],
    "sortDirection": ["ASC", "DESC"],
    "organizationId": "string",
    "contactId": "string",
    "creditedInvoiceId": "string",
    "state": ["draft", "approved", "voided"],
    "invoiceNo": "string",
    "externalId": "string",
    "minEntryDate": "date",
    "maxEntryDate": "date",
    "entryDatePeriod": [
        "all",
        "dates:A...B",
        "day:",
        "halfYear:",
        "month:",
        "quarter:",
        "year:",
        "fiscalYear:",
    ],
    "minApprovedTime": "date-time",
    "maxApprovedTime": "date-time",
    "approvedTimePeriod": [
        "all",
        "dates:…",
        "from:",
        "half:",
        "month:",
        "quarter:",
        "through:",
        "year:",
        "fiscalYear:",
    ],
    "minDueDate": "date",
    "maxDueDate": "date",
    "isPaid": "boolean",
    "currencyId": "string",
    "recurringInvoiceId": "string",
    "amount": "float",
    "quoteId": "string",
    "q": [
        "invoiceNo",
        "orderNo",
        "contact.name",
        "lineDescription",
        "amount",
        "amount+tax",
        "balance",
    ],
}

BILL_FILTERS: dict[str, Any] = {
    "sortProperty": [
        "entryDate",
        "dueDate",
        "createdTime",
        "lineDescription",
        "amount",
        "grossAmount",
        "balance",
        "contact.name",
        "voucherNo",
        "suppliersInvoiceNo",
        "attachments",
    ],
    "sortDirection": ["ASC", "DESC"],
    "organizationId": "string",
    "contactId": "string",
    "creditedBillId": "string",
    "minEntryDate": "date",
    "maxEntryDate": "date",
    "minDueDate": "date",
    "maxDueDate": "date",
    "isPaid": "boolean",
    "hasAttachments": "boolean",
    "state": ["draft", "approved", "voided"],
    "currencyId": "string",
    "suppliersInvoiceNo": "string",
    "isBare": "boolean",
    "amount": "float",
    "q": [
        "contact.name",
        "lineDescription",
        "voucherNo",
        "amount",
        "suppliersInvoiceNo",
        "balance",
    ],
}

DAYBOOK_TRANSACTION_FILTERS: dict[str, Any] = {
    "sortProperty": ["priority", "entryDate", "createdTime"],
    "sortDirection": ["ASC", "DESC"],
    "organizationId": "string",
    "daybookId": "string",
    "apiType": "string",
    "state": ["draft", "approved", "voided"],
    "minEntryDate": "date",
    "maxEntryDate": "date",
    "q": ["description", "extendedDescription", "voucherNo"],
}

LIST_FILTERS: dict[str, dict[str, Any]] = {
    "invoices": INVOICE_FILTERS,
    "bills": BILL_FILTERS,
    "daybookTransactions": DAYBOOK_TRANSACTION_FILTERS,
}

UI_DISCOVERY_FAMILIES: tuple[str, ...] = (
    "invoices",
    "quotes",
    "recurring_invoices",
    "products",
    "product_import",
    "customers",
    "debtor_balances",
    "creditor_balances",
    "uploads",
    "receipt_inbox",
    "purchases",
    "suppliers",
    "bank_accounts",
    "bank_reconciliation",
    "financing",
    "daybooks",
    "transactions",
    "reports",
    "vat_declarations",
    "annual_reports",
    "exports",
    "saft_exports",
    "addons",
    "integrations",
    "inventory",
    "settings_company",
    "settings_user",
    "settings_accounting",
    "settings_vat",
    "settings_invoicing",
    "settings_users",
    "settings_subscription",
    "settings_access_token",
    "settings_beta",
)


def snake_case(value: str) -> str:
    """Return a stable planned-tool segment from an official resource name."""

    return re.sub(r"(?<!^)([A-Z])", r"_\1", value).lower()


def singular(value: str) -> str:
    """Return the documented JSON root-key shape without claiming field schemas."""

    if value.endswith("ies"):
        return f"{value[:-3]}y"
    return value[:-1] if value.endswith("s") else value


def red_status(*, discovered: bool) -> dict[str, Any]:
    """Return the Phase 0 status fields shared by all inventory rows."""

    return {
        "discovered": discovered,
        "implemented": False,
        "contract_tested": False,
        "live_tested": False,
        "vision_verified": None,
        "vision_evidence": None,
    }


def sensitivity_for(side_effects: str) -> str:
    """Classify frozen risk without turning a red row into a live qualification."""

    if side_effects == "none":
        return "low"
    if side_effects.startswith("high:") or "not_recoverable" in side_effects:
        return "high"
    if side_effects.startswith("unknown"):
        return "unknown"
    return "medium"


def base_api_row(
    *,
    row_id: str,
    area: str,
    operation: str,
    method_or_route: str,
    request_fields: list[str],
    response_fields: list[str],
    filters: dict[str, Any] | list[Any],
    pagination: dict[str, Any] | None,
    side_effects: str,
    cleanup: str,
    tool_name: str,
    source_kind: str,
    contract_status: str = "documented",
) -> dict[str, Any]:
    """Build one documented API row with all §12.1 and freeze fields."""

    row: dict[str, Any] = {
        "id": row_id,
        "lane": "api",
        "area": area,
        "operation": operation,
        "method_or_route": method_or_route,
        "request_fields": request_fields,
        "response_fields": response_fields,
        "filters": filters,
        "pagination": pagination,
        "errors": COMMON_ERRORS,
        "sensitivity": sensitivity_for(side_effects),
        "side_effects": side_effects,
        "cleanup": cleanup,
        "tool_name": tool_name,
        "test_references": [TEST_REFERENCE],
        "evidence": f"{DOCS_URL} official API v2; docs etag {DOCS_ETAG}; MD5 {DOCS_MD5}",
        "source_kind": source_kind,
        "contract_status": contract_status,
    }
    row.update(red_status(discovered=True))
    return row


def standard_rows(resource: str, create: bool, update: bool, delete: bool) -> list[dict[str, Any]]:
    """Build clear conventional rows for one Supports resource."""

    area = snake_case(resource)
    singular_name = singular(resource)
    route = f"/v2/{resource}"
    list_filters = LIST_FILTERS.get(resource, {})
    list_request_fields = list(
        dict.fromkeys(
            ["page", "pageSize", "include", "sortProperty", "sortDirection", *list(list_filters)]
        )
    )
    rows = [
        base_api_row(
            row_id=f"api.{resource}.get",
            area=area,
            operation="get",
            method_or_route=f"GET {route}/:id",
            request_fields=["id", "include"],
            response_fields=[singular_name],
            filters=[],
            pagination=None,
            side_effects="none",
            cleanup="not_applicable",
            tool_name=f"api_{area}_get",
            source_kind="clear",
        ),
        base_api_row(
            row_id=f"api.{resource}.list",
            area=area,
            operation="list",
            method_or_route=f"GET {route}",
            request_fields=list_request_fields,
            response_fields=[f"{resource}[]", "meta.paging"],
            filters=list_filters,
            pagination=PAGING,
            side_effects="none",
            cleanup="not_applicable",
            tool_name=f"api_{area}_list",
            source_kind="clear",
        ),
    ]
    for operation, supported, method, side_effects, cleanup in (
        ("create", create, "POST", f"creates {singular_name}", "delete dedicated test resource"),
        ("update", update, "PUT", f"updates {singular_name}", "restore prior test state"),
        (
            "delete",
            delete,
            "DELETE",
            f"deletes {singular_name}",
            "not_recoverable; use disposable test data",
        ),
    ):
        if not supported:
            continue
        request_fields = [singular_name] if operation == "create" else ["id", singular_name]
        if operation == "delete":
            request_fields = ["id"]
        response_fields = ["changed_records[]", "meta.deletedRecords"]
        rows.append(
            base_api_row(
                row_id=f"api.{resource}.{operation}",
                area=area,
                operation=operation,
                method_or_route=f"{method} {route}" + ("/:id" if operation != "create" else ""),
                request_fields=request_fields,
                response_fields=response_fields,
                filters=[],
                pagination=None,
                side_effects=side_effects,
                cleanup=cleanup,
                tool_name=f"api_{area}_{operation}_preview",
                source_kind="clear",
            )
        )
    return rows


def bulk_rows(resource: str) -> list[dict[str, Any]]:
    """Build the two deliberately unimplemented bulk mentions for a resource."""

    area = snake_case(resource)
    route = f"/v2/{resource}"
    return [
        base_api_row(
            row_id=f"api.{resource}.bulk_save",
            area=area,
            operation="bulk_save",
            method_or_route=f"AMBIGUOUS Supports: bulk save {route}",
            request_fields=[],
            response_fields=[],
            filters=[],
            pagination=None,
            side_effects=(
                "unknown until method, body, partial failures, and limits are live-qualified"
            ),
            cleanup="unknown until the bulk contract is qualified on a non-production organisation",
            tool_name="",
            source_kind="ambiguous_bulk",
            contract_status="ambiguous_bulk",
        ),
        base_api_row(
            row_id=f"api.{resource}.bulk_delete",
            area=area,
            operation="bulk_delete",
            method_or_route=f"AMBIGUOUS Supports: bulk delete {route}",
            request_fields=[],
            response_fields=[],
            filters=[],
            pagination=None,
            side_effects=(
                "unknown until method, identifiers, partial failures, and limits are live-qualified"
            ),
            cleanup="unknown until the bulk contract is qualified on a non-production organisation",
            tool_name="",
            source_kind="ambiguous_bulk",
            contract_status="ambiguous_bulk",
        ),
    ]


def special_rows() -> list[dict[str, Any]]:
    """Build the six separately documented prose routes without inventing more."""

    return [
        base_api_row(
            row_id="api.special.files_upload",
            area="files",
            operation="upload",
            method_or_route="POST /v2/files",
            request_fields=[
                "file_bytes",
                "X-Access-Token",
                "X-Filename",
                "Content-Type",
                "x-create-attachment?",
                "x-create-variants?",
                "x-organizationid?",
                "x-should-scan?",
            ],
            response_fields=["files[]", "attachments?"],
            filters=[],
            pagination=None,
            side_effects="high: uploads file content and may create attachment variants",
            cleanup=(
                "delete only dedicated test attachments after live upload contract qualification"
            ),
            tool_name="api_files_upload_preview",
            source_kind="special",
        ),
        base_api_row(
            row_id="api.special.invoice_email",
            area="invoices",
            operation="send_email",
            method_or_route="POST /v2/invoices/:invoiceId/emails",
            request_fields=[
                "invoiceId",
                "email.contactPersonId",
                "email.emailBody",
                "email.emailSubject",
                "email.copyToUserId?",
            ],
            response_fields=["changed_records[]"],
            filters=[],
            pagination=None,
            side_effects="high: sends external email",
            cleanup="not_reversible; use a dedicated non-production destination",
            tool_name="api_invoices_send_email_preview",
            source_kind="special",
        ),
        base_api_row(
            row_id="api.special.invoice_delivery",
            area="invoice_deliveries",
            operation="create",
            method_or_route="POST /v2/invoiceDeliveries",
            request_fields=[
                "invoiceDelivery.invoiceId",
                "invoiceDelivery.organizationId",
                "invoiceDelivery.receiverIdType (gln|cvr)",
                "invoiceDelivery.receiverGln?",
                "invoiceDelivery.orderReference?",
                "invoiceDelivery.senderUserId",
            ],
            response_fields=["invoiceDelivery"],
            filters=[],
            pagination=None,
            side_effects="high: asynchronous external e-invoice delivery",
            cleanup=(
                "not_reversible; requires a supported sandbox or resettable dedicated organisation"
            ),
            tool_name="api_invoice_deliveries_create_preview",
            source_kind="special",
        ),
        base_api_row(
            row_id="api.special.invoice_logs",
            area="invoice_logs",
            operation="list",
            method_or_route="GET /v2/invoiceLogs",
            request_fields=["invoiceId", "organizationId", "sortProperty", "sortDirection"],
            response_fields=["invoiceLogs[]"],
            filters={"sortProperty": ["eventTime"], "sortDirection": ["DESC"]},
            pagination=None,
            side_effects="none",
            cleanup="not_applicable",
            tool_name="api_invoice_logs_list",
            source_kind="special",
        ),
        base_api_row(
            row_id="api.special.user_get",
            area="user",
            operation="get",
            method_or_route="GET /v2/user",
            request_fields=[],
            response_fields=["user"],
            filters=[],
            pagination=None,
            side_effects="none",
            cleanup="not_applicable",
            tool_name="api_user_get",
            source_kind="special",
        ),
        base_api_row(
            row_id="api.special.user_organizations",
            area="user_organizations",
            operation="list",
            method_or_route="GET /v2/user/organizations",
            request_fields=[],
            response_fields=["organizations[]"],
            filters=[],
            pagination=None,
            side_effects="none",
            cleanup="not_applicable",
            tool_name="api_user_list_organizations",
            source_kind="special",
        ),
    ]


def build_api_manifest() -> dict[str, Any]:
    """Return the complete 305-operation official snapshot."""

    operations: list[dict[str, Any]] = []
    for resource, create, update, delete in RESOURCE_SUPPORTS:
        operations.extend(standard_rows(resource, create, update, delete))
        operations.extend(bulk_rows(resource))
    operations.extend(special_rows())
    return {
        "manifest": "billy_api_v2_phase_0",
        "schema_version": 1,
        "official_docs": {"url": DOCS_URL, "etag": DOCS_ETAG, "md5": DOCS_MD5},
        "operations": operations,
    }


def build_ui_manifest(api_manifest: dict[str, Any]) -> dict[str, Any]:
    """Return red UI route seeds and an explicit parity map for every API row."""

    workflows: list[dict[str, Any]] = []
    for family in UI_DISCOVERY_FAMILIES:
        row: dict[str, Any] = {
            "id": f"ui.discovery.{family}",
            "lane": "ui",
            "area": family,
            "operation": "discovery",
            "method_or_route": f"DISCOVERY REQUIRED: mit.billy.dk route family {family}",
            "request_fields": [],
            "response_fields": [],
            "filters": [],
            "pagination": None,
            "errors": ["AUTH_INTERACTION_REQUIRED", "UI_CHANGED"],
            "sensitivity": "unknown",
            "side_effects": "unknown until a headless typed workflow is verified",
            "cleanup": "not_applicable for route discovery; no records may be created",
            "tool_name": "",
            "test_references": [TEST_REFERENCE],
            "evidence": (
                "Approved design §10.3 route-family discovery seed; no headless qualification yet"
            ),
            "workflow_kind": "discovery",
            "parity_status": "discovery_required",
            "api_row_id": None,
        }
        row.update(red_status(discovered=False))
        row["vision_verified"] = False
        workflows.append(row)

    for api_row in api_manifest["operations"]:
        row = {
            "id": f"ui.parity.{api_row['id'][4:]}",
            "lane": "ui",
            "area": api_row["area"],
            "operation": "api_parity",
            "method_or_route": f"PARITY DISCOVERY REQUIRED for {api_row['id']}",
            "request_fields": api_row["request_fields"],
            "response_fields": api_row["response_fields"],
            "filters": api_row["filters"],
            "pagination": api_row["pagination"],
            "errors": ["AUTH_INTERACTION_REQUIRED", "UI_CHANGED"],
            "sensitivity": api_row["sensitivity"],
            "side_effects": api_row["side_effects"],
            "cleanup": api_row["cleanup"],
            "tool_name": "",
            "test_references": [TEST_REFERENCE],
            "evidence": (
                f"API parity required by approved design §10.2; mapped from {api_row['id']}"
            ),
            "workflow_kind": "api_parity",
            "parity_status": "discovery_required",
            "api_row_id": api_row["id"],
        }
        row.update(red_status(discovered=False))
        row["vision_verified"] = False
        workflows.append(row)

    return {
        "manifest": "billy_ui_workflows_phase_0",
        "schema_version": 1,
        "workflows": workflows,
    }


def build_browser_egress() -> dict[str, Any]:
    """Return the deliberately minimal browser policy from the frozen brief."""

    return {
        "manifest": "billy_browser_egress_phase_0",
        "schema_version": 1,
        "default_action": "deny",
        "hosts": [
            {
                "host": "mit.billy.dk",
                "browser_action": "allow",
                "api_client_action": "deny",
                "owner": "ui_auth",
                "purpose": "Billy web interface and headless authentication only",
                "condition": "typed UI/auth workflow",
                "evidence": "Frozen brief §10.3: official app host",
                "test_references": [TEST_REFERENCE],
            },
            {
                "host": "download.billy.dk",
                "browser_action": "allow",
                "api_client_action": "deny",
                "owner": "future_typed_download",
                "purpose": "Typed Billy file download handling only",
                "condition": "future verified typed download workflow; not general navigation",
                "evidence": "Frozen brief §10.3: files downloadUrl host",
                "test_references": [TEST_REFERENCE],
            },
            {
                "host": "api.billysbilling.com",
                "browser_action": "deny",
                "api_client_action": "exclusive_allow",
                "owner": "api_client",
                "purpose": "Locked official API client destination",
                "condition": "not available to browser lane",
                "evidence": "Approved design §11.1 and frozen brief §3",
                "test_references": [TEST_REFERENCE],
            },
            {
                "host": "api.billy.dk",
                "browser_action": "deny",
                "api_client_action": "deny",
                "owner": "none",
                "purpose": "Denied API alias",
                "condition": "never permitted",
                "evidence": "Frozen brief §2.3 and §10.3 alias-host denial",
                "test_references": [TEST_REFERENCE],
            },
        ],
    }


def count_by(items: list[dict[str, Any]], key: str) -> dict[str, int]:
    """Count non-empty string values in a list of manifest records."""

    counts: dict[str, int] = {}
    for item in items:
        value = item.get(key)
        if isinstance(value, str):
            counts[value] = counts.get(value, 0) + 1
    return dict(sorted(counts.items()))


def build_status(api_manifest: dict[str, Any], ui_manifest: dict[str, Any]) -> dict[str, Any]:
    """Return the only generated completeness source, which is false in Phase 0."""

    api_rows = api_manifest["operations"]
    ui_rows = ui_manifest["workflows"]
    rows = api_rows + ui_rows
    return {
        "schema_version": 1,
        "complete": False,
        "phase": "phase_0_inventory",
        "official_docs": {"etag": DOCS_ETAG, "md5": DOCS_MD5},
        "source_counts": {
            "api_clear": count_by(api_rows, "source_kind").get("clear", 0),
            "api_ambiguous_bulk": count_by(api_rows, "source_kind").get("ambiguous_bulk", 0),
            "api_special": count_by(api_rows, "source_kind").get("special", 0),
            "api_total": len(api_rows),
            "ui_discovery": count_by(ui_rows, "workflow_kind").get("discovery", 0),
            "ui_api_parity": count_by(ui_rows, "workflow_kind").get("api_parity", 0),
            "ui_total": len(ui_rows),
            "all_rows": len(rows),
        },
        "qualification": {
            "implemented_rows": sum(bool(row["implemented"]) for row in rows),
            "contract_tested_rows": sum(bool(row["contract_tested"]) for row in rows),
            "live_tested_rows": sum(bool(row["live_tested"]) for row in rows),
            "vision_verified_rows": sum(bool(row["vision_verified"]) for row in ui_rows),
            "blocker": "BILLY_API_TOKEN is unavailable; no live or UI qualification is claimed",
        },
    }


def render_report(status: dict[str, Any]) -> str:
    """Render a deterministic human-readable companion to status.json."""

    counts = status["source_counts"]
    qualification = status["qualification"]
    return "\n".join(
        [
            "# Phase 0 coverage status",
            "",
            "This generated inventory is deliberately incomplete. It freezes the official-doc",
            "snapshot without asserting implementation, contract testing, live testing, or vision",
            "verification.",
            "",
            "| Source | Count |",
            "| --- | ---: |",
            f"| Clear API operations | {counts['api_clear']} |",
            f"| Ambiguous bulk mentions | {counts['api_ambiguous_bulk']} |",
            f"| Documented special routes | {counts['api_special']} |",
            f"| API snapshot total | {counts['api_total']} |",
            f"| UI discovery seeds | {counts['ui_discovery']} |",
            f"| UI API-parity mappings | {counts['ui_api_parity']} |",
            "",
            f"Complete: `{str(status['complete']).lower()}`",
            "",
            f"Blocker: {qualification['blocker']}",
            "",
        ]
    )


def write_json(path: Path, payload: dict[str, Any]) -> None:
    """Write stable JSON text, valid YAML, with a final newline."""

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def generate(root: Path) -> dict[str, Any]:
    """Write every generated Phase 0 inventory artifact below ``root``."""

    api_manifest = build_api_manifest()
    ui_manifest = build_ui_manifest(api_manifest)
    status = build_status(api_manifest, ui_manifest)
    coverage = root / "coverage"
    write_json(coverage / "api_v2_manifest.yaml", api_manifest)
    write_json(coverage / "ui_workflows_manifest.yaml", ui_manifest)
    write_json(coverage / "browser_egress.yaml", build_browser_egress())
    write_json(coverage / "status.json", status)
    (coverage / "report.md").write_text(render_report(status), encoding="utf-8")
    return status


def main() -> int:
    """Generate the checked-in artifacts when explicitly requested."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="write coverage artifacts")
    args = parser.parse_args()
    if not args.write:
        parser.error("pass --write to generate coverage artifacts")
    status = generate(ROOT)
    print(
        "Generated Phase 0 coverage: "
        f"{status['source_counts']['api_total']} API rows, "
        f"{status['source_counts']['ui_total']} UI rows, complete={status['complete']}."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
