"""Tests for root-owned typed contracts shared by Phase 0 modules."""

import pytest
from pydantic import ValidationError

from billy_mcp.models import (
    AuthLoginStartInput,
    AuthLoginStartSuccess,
    AuthLoginWaitInput,
    AuthLoginWaitSuccess,
    AuthStatusInput,
    AuthStatusSuccess,
    CoverageStatus,
    StableErrorCode,
    ToolError,
    UiAddonsOpenInput,
    UiAddonsOpenSuccess,
    UiBankAccountsListInput,
    UiBankAccountsListSuccess,
    UiBankReconciliationOpenInput,
    UiBankReconciliationOpenSuccess,
    UiBillsCreateOpenInput,
    UiBillsCreateOpenSuccess,
    UiBillsListInput,
    UiBillsListSuccess,
    UiClientsCreateOpenInput,
    UiClientsCreateOpenSuccess,
    UiClientsListInput,
    UiClientsListSuccess,
    UiCreditorBalancesListInput,
    UiCreditorBalancesListSuccess,
    UiDaybooksOpenInput,
    UiDaybooksOpenSuccess,
    UiDebtorBalancesListInput,
    UiDebtorBalancesListSuccess,
    UiExportsOpenInput,
    UiExportsOpenSuccess,
    UiFinancingOpenInput,
    UiFinancingOpenSuccess,
    UiIntegrationsOpenInput,
    UiIntegrationsOpenSuccess,
    UiInventoryOpenInput,
    UiInventoryOpenSuccess,
    UiInvoicesCreateOpenInput,
    UiInvoicesCreateOpenSuccess,
    UiInvoicesListInput,
    UiInvoicesListSuccess,
    UiProductsImportInput,
    UiProductsImportSuccess,
    UiProductsListInput,
    UiProductsListSuccess,
    UiQuotesListInput,
    UiQuotesListSuccess,
    UiReceiptInboxListInput,
    UiReceiptInboxListSuccess,
    UiRecurringInvoicesListInput,
    UiRecurringInvoicesListSuccess,
    UiReportsOpenInput,
    UiReportsOpenSuccess,
    UiSaftExportsOpenInput,
    UiSaftExportsOpenSuccess,
    UiSettingsAccessTokenOpenInput,
    UiSettingsAccessTokenOpenSuccess,
    UiSettingsAccountingOpenInput,
    UiSettingsAccountingOpenSuccess,
    UiSettingsBetaOpenInput,
    UiSettingsBetaOpenSuccess,
    UiSettingsCompanyOpenInput,
    UiSettingsCompanyOpenSuccess,
    UiSettingsInvoicingOpenInput,
    UiSettingsInvoicingOpenSuccess,
    UiSettingsSubscriptionOpenInput,
    UiSettingsSubscriptionOpenSuccess,
    UiSettingsUserOpenInput,
    UiSettingsUserOpenSuccess,
    UiSettingsUserOrganizationsOpenInput,
    UiSettingsUserOrganizationsOpenSuccess,
    UiSettingsUsersOpenInput,
    UiSettingsUsersOpenSuccess,
    UiSettingsVatOpenInput,
    UiSettingsVatOpenSuccess,
    UiSuppliersCreateOpenInput,
    UiSuppliersCreateOpenSuccess,
    UiSuppliersListInput,
    UiSuppliersListSuccess,
    UiTransactionsListInput,
    UiTransactionsListSuccess,
    UiUploadsListInput,
    UiUploadsListSuccess,
    UiVatDeclarationsListInput,
    UiVatDeclarationsListSuccess,
)


def test_tool_error_uses_stable_machine_code() -> None:
    error = ToolError(code=StableErrorCode.AUTH_REQUIRED, message="Token is unavailable")

    assert error.model_dump() == {
        "code": "AUTH_REQUIRED",
        "message": "Token is unavailable",
        "details": {},
    }


def test_coverage_status_is_red_by_default() -> None:
    status = CoverageStatus()

    assert status.discovered is False
    assert status.implemented is False
    assert status.contract_tested is False
    assert status.live_tested is False
    assert status.vision_verified is None


def test_auth_status_contract_has_no_caller_controls_and_only_the_verified_state() -> None:
    assert AuthStatusInput().model_dump() == {}
    assert AuthStatusSuccess().model_dump() == {"status": StableErrorCode.AUTH_REQUIRED}

    with pytest.raises(ValidationError):
        AuthStatusInput.model_validate({"url": "https://untrusted.example"})


def test_login_tool_models_have_empty_inputs_and_no_secret_bearing_schema() -> None:
    assert AuthLoginStartInput().model_dump() == {}
    assert AuthLoginWaitInput().model_dump() == {}
    assert AuthLoginStartSuccess().model_dump() == {"status": "AUTHENTICATING"}
    assert AuthLoginWaitSuccess(status="READY").model_dump() == {"status": "READY"}
    assert AuthLoginWaitSuccess(status="AUTH_REQUIRED").model_dump() == {"status": "AUTH_REQUIRED"}

    for model in (
        AuthLoginStartInput,
        AuthLoginWaitInput,
        AuthLoginStartSuccess,
        AuthLoginWaitSuccess,
    ):
        properties = model.model_json_schema().get("properties", {})
        assert not ({"email", "password", "totp", "cookie", "token", "org_slug"} & set(properties))

    with pytest.raises(ValidationError):
        AuthLoginStartInput.model_validate({"selector": "button"})
    with pytest.raises(ValidationError):
        AuthLoginWaitInput.model_validate({"url": "https://untrusted.example"})
    with pytest.raises(ValidationError):
        AuthLoginWaitSuccess.model_validate({"status": "AUTHENTICATING"})


def test_ui_invoices_list_models_are_empty_input_and_non_pii_success() -> None:
    assert UiInvoicesListInput().model_dump() == {}
    success = UiInvoicesListSuccess(create_action_visible=True, shell_markers_present=True)
    assert success.model_dump() == {
        "path_class": "/:org_slug/invoices",
        "heading": "Fakturaer",
        "create_action_visible": True,
        "shell_markers_present": True,
    }
    properties = UiInvoicesListSuccess.model_json_schema().get("properties", {})
    assert not (
        {"email", "password", "totp", "cookie", "token", "org_slug", "url", "selector"}
        & set(properties)
    )
    with pytest.raises(ValidationError):
        UiInvoicesListInput.model_validate({"url": "https://untrusted.example"})
    with pytest.raises(ValidationError):
        UiInvoicesListSuccess.model_validate(
            {
                "path_class": "/:org_slug/invoices",
                "heading": "Fakturaer",
                "create_action_visible": True,
                "shell_markers_present": True,
                "org_slug": "secret",
            }
        )


def test_ui_invoices_create_open_models_are_empty_input_and_non_pii_success() -> None:
    assert UiInvoicesCreateOpenInput().model_dump() == {}
    success = UiInvoicesCreateOpenSuccess(
        draft_save_chrome_visible=True,
        line_chrome_visible=True,
        shell_markers_present=True,
    )
    assert success.path_class == "/:org_slug/invoices/new"
    assert success.heading == "Opret faktura"
    assert success.shell_kind == "invoices_create"
    properties = UiInvoicesCreateOpenSuccess.model_json_schema().get("properties", {})
    assert not ({"email", "password", "totp", "cookie", "token", "org_slug"} & set(properties))
    try:
        UiInvoicesCreateOpenInput.model_validate({"url": "https://untrusted.example"})
        raise AssertionError("extra fields must be forbidden")
    except Exception:
        pass
    try:
        UiInvoicesCreateOpenSuccess.model_validate(
            {
                "path_class": "/:org_slug/invoices/new",
                "heading": "Opret faktura",
                "shell_kind": "invoices_create",
                "draft_save_chrome_visible": True,
                "line_chrome_visible": True,
                "shell_markers_present": True,
                "org_slug": "secret",
            }
        )
        raise AssertionError("extra fields must be forbidden")
    except Exception:
        pass


def test_ui_bills_create_open_models_are_empty_input_and_non_pii_success() -> None:
    assert UiBillsCreateOpenInput().model_dump() == {}
    success = UiBillsCreateOpenSuccess(
        draft_save_chrome_visible=True,
        line_chrome_visible=True,
        shell_markers_present=True,
    )
    assert success.path_class == "/:org_slug/bills/new"
    assert success.heading == "Opret køb"
    assert success.shell_kind == "bills_create"
    properties = UiBillsCreateOpenSuccess.model_json_schema().get("properties", {})
    assert not ({"email", "password", "totp", "cookie", "token", "org_slug"} & set(properties))
    try:
        UiBillsCreateOpenInput.model_validate({"url": "https://untrusted.example"})
        raise AssertionError("extra fields must be forbidden")
    except Exception:
        pass
    try:
        UiBillsCreateOpenSuccess.model_validate(
            {
                "path_class": "/:org_slug/bills/new",
                "heading": "Opret køb",
                "shell_kind": "bills_create",
                "draft_save_chrome_visible": True,
                "line_chrome_visible": True,
                "shell_markers_present": True,
                "org_slug": "secret",
            }
        )
        raise AssertionError("extra fields must be forbidden")
    except Exception:
        pass


def test_ui_clients_create_open_models_are_empty_input_and_non_pii_success() -> None:
    assert UiClientsCreateOpenInput().model_dump() == {}
    success = UiClientsCreateOpenSuccess(
        create_dialog_open=True,
        name_field_visible=True,
        registration_no_field_present=True,
        address_or_person_fields_present=True,
        shell_markers_present=True,
    )
    assert success.path_class == "/:org_slug/clients"
    assert success.heading == "Kunder"
    assert success.shell_kind == "clients_create"
    properties = UiClientsCreateOpenSuccess.model_json_schema().get("properties", {})
    assert not ({"email", "password", "totp", "cookie", "token", "org_slug"} & set(properties))
    try:
        UiClientsCreateOpenInput.model_validate({"url": "https://untrusted.example"})
        raise AssertionError("extra fields must be forbidden")
    except Exception:
        pass
    try:
        UiClientsCreateOpenSuccess.model_validate(
            {
                "path_class": "/:org_slug/clients",
                "heading": "Kunder",
                "shell_kind": "clients_create",
                "create_dialog_open": True,
                "name_field_visible": True,
                "registration_no_field_present": True,
                "address_or_person_fields_present": True,
                "shell_markers_present": True,
                "org_slug": "secret",
            }
        )
        raise AssertionError("extra fields must be forbidden")
    except Exception:
        pass


def test_ui_suppliers_create_open_models_are_empty_input_and_non_pii_success() -> None:
    assert UiSuppliersCreateOpenInput().model_dump() == {}
    success = UiSuppliersCreateOpenSuccess(
        create_dialog_open=True,
        name_field_visible=True,
        registration_no_field_present=True,
        address_or_person_fields_present=True,
        shell_markers_present=True,
    )
    assert success.path_class == "/:org_slug/suppliers"
    assert success.heading == "Leverandører"
    assert success.shell_kind == "suppliers_create"
    properties = UiSuppliersCreateOpenSuccess.model_json_schema().get("properties", {})
    assert not ({"email", "password", "totp", "cookie", "token", "org_slug"} & set(properties))
    try:
        UiSuppliersCreateOpenInput.model_validate({"url": "https://untrusted.example"})
        raise AssertionError("extra fields must be forbidden")
    except Exception:
        pass
    try:
        UiSuppliersCreateOpenSuccess.model_validate(
            {
                "path_class": "/:org_slug/suppliers",
                "heading": "Leverandører",
                "shell_kind": "suppliers_create",
                "create_dialog_open": True,
                "name_field_visible": True,
                "registration_no_field_present": True,
                "address_or_person_fields_present": True,
                "shell_markers_present": True,
                "org_slug": "secret",
            }
        )
        raise AssertionError("extra fields must be forbidden")
    except Exception:
        pass


def test_ui_products_list_models_are_empty_input_and_non_pii_success() -> None:
    assert UiProductsListInput().model_dump() == {}
    success = UiProductsListSuccess(search_control_visible=True, shell_markers_present=True)
    assert success.model_dump() == {
        "path_class": "/:org_slug/products",
        "heading": "Produkter",
        "search_control_visible": True,
        "shell_markers_present": True,
    }
    properties = UiProductsListSuccess.model_json_schema().get("properties", {})
    for forbidden in ("email", "password", "token", "org_slug", "url", "product_name"):
        assert forbidden not in properties
    with pytest.raises(ValidationError):
        UiProductsListInput.model_validate({"url": "https://untrusted.example"})
    with pytest.raises(ValidationError):
        UiProductsListSuccess.model_validate(
            {
                "path_class": "/:org_slug/products",
                "heading": "Produkter",
                "search_control_visible": True,
                "shell_markers_present": True,
                "product_name": "secret",
            }
        )


def test_ui_clients_list_models_are_empty_input_and_non_pii_success() -> None:
    assert UiClientsListInput().model_dump() == {}
    success = UiClientsListSuccess(create_action_visible=True, shell_markers_present=True)
    assert success.model_dump() == {
        "path_class": "/:org_slug/clients",
        "heading": "Kunder",
        "create_action_visible": True,
        "shell_markers_present": True,
    }
    properties = UiClientsListSuccess.model_json_schema().get("properties", {})
    for forbidden in (
        "email",
        "password",
        "token",
        "org_slug",
        "url",
        "contact_name",
        "selector",
    ):
        assert forbidden not in properties
    with pytest.raises(ValidationError):
        UiClientsListInput.model_validate({"url": "https://untrusted.example"})
    with pytest.raises(ValidationError):
        UiClientsListSuccess.model_validate(
            {
                "path_class": "/:org_slug/clients",
                "heading": "Kunder",
                "create_action_visible": True,
                "shell_markers_present": True,
                "contact_name": "secret",
            }
        )


def test_ui_bank_accounts_list_models_are_empty_input_and_non_pii_success() -> None:
    assert UiBankAccountsListInput().model_dump() == {}
    success = UiBankAccountsListSuccess(
        connect_bank_action_visible=True,
        shell_markers_present=True,
    )
    assert success.model_dump() == {
        "path_class": "/:org_slug/bank-accounts",
        "heading": "Bankkonti",
        "connect_bank_action_visible": True,
        "shell_markers_present": True,
    }
    properties = UiBankAccountsListSuccess.model_json_schema().get("properties", {})
    for forbidden in (
        "email",
        "password",
        "token",
        "org_slug",
        "url",
        "account_number",
        "iban",
        "selector",
    ):
        assert forbidden not in properties
    with pytest.raises(ValidationError):
        UiBankAccountsListInput.model_validate({"url": "https://untrusted.example"})
    with pytest.raises(ValidationError):
        UiBankAccountsListSuccess.model_validate(
            {
                "path_class": "/:org_slug/bank-accounts",
                "heading": "Bankkonti",
                "connect_bank_action_visible": True,
                "shell_markers_present": True,
                "iban": "secret",
            }
        )


def test_ui_quotes_list_models_are_empty_input_and_non_pii_success() -> None:
    assert UiQuotesListInput().model_dump() == {}
    success = UiQuotesListSuccess(
        create_action_visible=True,
        shell_markers_present=True,
    )
    assert success.model_dump() == {
        "path_class": "/:org_slug/quotes",
        "heading": "Tilbud",
        "create_action_visible": True,
        "shell_markers_present": True,
    }
    properties = UiQuotesListSuccess.model_json_schema().get("properties", {})
    for forbidden in (
        "email",
        "password",
        "token",
        "org_slug",
        "url",
        "quote_id",
        "customer",
        "selector",
    ):
        assert forbidden not in properties
    with pytest.raises(ValidationError):
        UiQuotesListInput.model_validate({"url": "https://untrusted.example"})
    with pytest.raises(ValidationError):
        UiQuotesListSuccess.model_validate(
            {
                "path_class": "/:org_slug/quotes",
                "heading": "Tilbud",
                "create_action_visible": True,
                "shell_markers_present": True,
                "customer": "secret",
            }
        )


def test_ui_recurring_invoices_list_models_are_empty_input_and_non_pii_success() -> None:
    assert UiRecurringInvoicesListInput().model_dump() == {}
    success = UiRecurringInvoicesListSuccess(
        create_action_visible=True,
        shell_markers_present=True,
    )
    assert success.model_dump() == {
        "path_class": "/:org_slug/recurring_invoices",
        "heading": "Abonnementer",
        "create_action_visible": True,
        "shell_markers_present": True,
    }
    properties = UiRecurringInvoicesListSuccess.model_json_schema().get("properties", {})
    for forbidden in (
        "email",
        "password",
        "token",
        "org_slug",
        "url",
        "recurring_invoice_id",
        "customer",
        "selector",
    ):
        assert forbidden not in properties
    with pytest.raises(ValidationError):
        UiRecurringInvoicesListInput.model_validate({"url": "https://untrusted.example"})
    with pytest.raises(ValidationError):
        UiRecurringInvoicesListSuccess.model_validate(
            {
                "path_class": "/:org_slug/recurring_invoices",
                "heading": "Abonnementer",
                "create_action_visible": True,
                "shell_markers_present": True,
                "customer": "secret",
            }
        )


def test_ui_products_import_models_are_empty_input_and_non_pii_success() -> None:
    assert UiProductsImportInput().model_dump() == {}
    success = UiProductsImportSuccess(
        choose_csv_action_visible=True,
        shell_markers_present=True,
    )
    assert success.model_dump() == {
        "path_class": "/:org_slug/products/import",
        "heading": "Import af produkter",
        "choose_csv_action_visible": True,
        "shell_markers_present": True,
    }
    properties = UiProductsImportSuccess.model_json_schema().get("properties", {})
    for forbidden in (
        "email",
        "password",
        "token",
        "org_slug",
        "url",
        "file_path",
        "digest",
        "customer",
        "selector",
    ):
        assert forbidden not in properties
    with pytest.raises(ValidationError):
        UiProductsImportInput.model_validate({"url": "https://untrusted.example"})
    with pytest.raises(ValidationError):
        UiProductsImportSuccess.model_validate(
            {
                "path_class": "/:org_slug/products/import",
                "heading": "Import af produkter",
                "choose_csv_action_visible": True,
                "shell_markers_present": True,
                "customer": "secret",
            }
        )


def test_ui_suppliers_list_models_are_empty_input_and_non_pii_success() -> None:
    assert UiSuppliersListInput().model_dump() == {}
    success = UiSuppliersListSuccess(create_action_visible=True, shell_markers_present=True)
    assert success.model_dump() == {
        "path_class": "/:org_slug/suppliers",
        "heading": "Leverandører",
        "create_action_visible": True,
        "shell_markers_present": True,
    }
    properties = UiSuppliersListSuccess.model_json_schema().get("properties", {})
    for forbidden in (
        "email",
        "password",
        "token",
        "org_slug",
        "url",
        "contact_name",
        "supplier_name",
        "selector",
    ):
        assert forbidden not in properties
    with pytest.raises(ValidationError):
        UiSuppliersListInput.model_validate({"url": "https://untrusted.example"})
    with pytest.raises(ValidationError):
        UiSuppliersListSuccess.model_validate(
            {
                "path_class": "/:org_slug/suppliers",
                "heading": "Leverandører",
                "create_action_visible": True,
                "shell_markers_present": True,
                "contact_name": "secret",
            }
        )


def test_ui_debtor_balances_list_models_are_empty_input_and_non_pii_success() -> None:
    assert UiDebtorBalancesListInput().model_dump() == {}
    success = UiDebtorBalancesListSuccess(create_action_visible=True, shell_markers_present=True)
    assert success.path_class == "/:org_slug/debtorbalance"
    assert success.heading == "Tilgodehavender"
    assert success.create_action_visible is True
    assert success.shell_markers_present is True
    properties = UiDebtorBalancesListSuccess.model_json_schema().get("properties", {})
    assert set(properties) == {
        "path_class",
        "heading",
        "create_action_visible",
        "shell_markers_present",
    }
    try:
        UiDebtorBalancesListInput.model_validate({"url": "https://untrusted.example"})
        raise AssertionError("expected validation error")
    except Exception:
        pass
    try:
        UiDebtorBalancesListSuccess.model_validate(
            {
                "path_class": "/:org_slug/other",
                "heading": "X",
                "create_action_visible": True,
                "shell_markers_present": True,
            }
        )
        raise AssertionError("expected validation error")
    except Exception:
        pass


def test_ui_creditor_balances_list_models_are_empty_input_and_non_pii_success() -> None:
    assert UiCreditorBalancesListInput().model_dump() == {}
    success = UiCreditorBalancesListSuccess(create_action_visible=True, shell_markers_present=True)
    assert success.path_class == "/:org_slug/creditorbalance"
    assert success.heading == "Skyldige udgifter"
    assert success.create_action_visible is True
    assert success.shell_markers_present is True
    properties = UiCreditorBalancesListSuccess.model_json_schema().get("properties", {})
    assert set(properties) == {
        "path_class",
        "heading",
        "create_action_visible",
        "shell_markers_present",
    }
    try:
        UiCreditorBalancesListInput.model_validate({"url": "https://untrusted.example"})
        raise AssertionError("expected validation error")
    except Exception:
        pass
    try:
        UiCreditorBalancesListSuccess.model_validate(
            {
                "path_class": "/:org_slug/other",
                "heading": "X",
                "create_action_visible": True,
                "shell_markers_present": True,
            }
        )
        raise AssertionError("expected validation error")
    except Exception:
        pass


def test_ui_uploads_list_models_are_empty_input_and_non_pii_success() -> None:
    assert UiUploadsListInput().model_dump() == {}
    success = UiUploadsListSuccess(
        upload_action_visible=True,
        file_input_present=True,
        shell_markers_present=True,
    )
    assert success.path_class == "/:org_slug/uploads"
    assert success.heading == "Bilag"
    assert success.upload_action_visible is True
    assert success.file_input_present is True
    assert success.shell_markers_present is True
    properties = UiUploadsListSuccess.model_json_schema().get("properties", {})
    assert set(properties) == {
        "path_class",
        "heading",
        "upload_action_visible",
        "file_input_present",
        "shell_markers_present",
    }
    try:
        UiUploadsListInput.model_validate({"file_path": "/tmp/x.pdf"})
        raise AssertionError("expected validation error")
    except Exception:
        pass
    try:
        UiUploadsListInput.model_validate({"digest": "abc"})
        raise AssertionError("expected validation error")
    except Exception:
        pass
    try:
        UiUploadsListSuccess.model_validate(
            {
                "path_class": "/:org_slug/other",
                "heading": "X",
                "upload_action_visible": True,
                "file_input_present": True,
                "shell_markers_present": True,
            }
        )
        raise AssertionError("expected validation error")
    except Exception:
        pass


def test_ui_receipt_inbox_list_models_are_empty_input_and_non_pii_success() -> None:
    assert UiReceiptInboxListInput().model_dump() == {}
    success = UiReceiptInboxListSuccess(file_control_present=True, shell_markers_present=True)
    assert success.path_class == "/:org_slug/vouchers"
    assert success.heading == "Bilagsindbakke"
    assert success.file_control_present is True
    assert success.shell_markers_present is True
    properties = UiReceiptInboxListSuccess.model_json_schema().get("properties", {})
    assert set(properties) == {
        "path_class",
        "heading",
        "file_control_present",
        "shell_markers_present",
    }
    try:
        UiReceiptInboxListInput.model_validate({"file_path": "/tmp/x.pdf"})
        raise AssertionError("expected validation error")
    except Exception:
        pass
    try:
        UiReceiptInboxListInput.model_validate({"url": "https://mit.billy.dk/x/vouchers"})
        raise AssertionError("expected validation error")
    except Exception:
        pass
    try:
        UiReceiptInboxListSuccess.model_validate(
            {
                "path_class": "/:org_slug/uploads",
                "heading": "Bilag",
                "file_control_present": True,
                "shell_markers_present": True,
            }
        )
        raise AssertionError("expected validation error")
    except Exception:
        pass


def test_ui_bank_reconciliation_open_models_are_empty_input_and_non_pii_success() -> None:
    assert UiBankReconciliationOpenInput().model_dump() == {}
    success = UiBankReconciliationOpenSuccess(
        empty_content_shell=True,
        afstemning_nav_visible=True,
        shell_markers_present=True,
    )
    assert success.path_class == "/:org_slug/bank_accounts/:id/sync"
    assert success.heading == ""
    assert success.empty_content_shell is True
    assert success.afstemning_nav_visible is True
    assert success.shell_markers_present is True
    properties = UiBankReconciliationOpenSuccess.model_json_schema().get("properties", {})
    assert set(properties) == {
        "path_class",
        "heading",
        "empty_content_shell",
        "afstemning_nav_visible",
        "shell_markers_present",
    }
    try:
        UiBankReconciliationOpenInput.model_validate({"account_id": "x"})
        raise AssertionError("expected validation error")
    except Exception:
        pass
    try:
        UiBankReconciliationOpenInput.model_validate(
            {"url": "https://mit.billy.dk/x/bank_accounts/y/sync"}
        )
        raise AssertionError("expected validation error")
    except Exception:
        pass
    try:
        UiBankReconciliationOpenSuccess.model_validate(
            {
                "path_class": "/:org_slug/bank-accounts",
                "heading": "Bankkonti",
                "empty_content_shell": False,
                "afstemning_nav_visible": True,
                "shell_markers_present": True,
            }
        )
        raise AssertionError("expected validation error")
    except Exception:
        pass


def test_ui_financing_open_models_are_empty_input_and_non_pii_success() -> None:
    assert UiFinancingOpenInput().model_dump() == {}
    success = UiFinancingOpenSuccess(apply_cta_observed=True, shell_markers_present=True)
    assert success.path_class == "/:org_slug/financing"
    assert success.heading == "Ansøg om erhvervslån"
    assert success.apply_cta_observed is True
    assert success.shell_markers_present is True
    properties = UiFinancingOpenSuccess.model_json_schema().get("properties", {})
    assert set(properties) == {
        "path_class",
        "heading",
        "apply_cta_observed",
        "shell_markers_present",
    }
    try:
        UiFinancingOpenInput.model_validate({"url": "https://mit.billy.dk/x/financing"})
        raise AssertionError("expected validation error")
    except Exception:
        pass
    try:
        UiFinancingOpenInput.model_validate({"apply": True})
        raise AssertionError("expected validation error")
    except Exception:
        pass
    try:
        UiFinancingOpenSuccess.model_validate(
            {
                "path_class": "/:org_slug/bank-accounts",
                "heading": "Bankkonti",
                "apply_cta_observed": False,
                "shell_markers_present": True,
            }
        )
        raise AssertionError("expected validation error")
    except Exception:
        pass


def test_ui_daybooks_open_models_are_empty_input_and_non_pii_success() -> None:
    assert UiDaybooksOpenInput().model_dump() == {}
    success = UiDaybooksOpenSuccess(editor_markers_present=True, shell_markers_present=True)
    assert success.path_class == "/:org_slug/daybooks/new"
    assert success.heading == ""
    assert success.editor_markers_present is True
    assert success.shell_markers_present is True
    properties = UiDaybooksOpenSuccess.model_json_schema().get("properties", {})
    assert set(properties) == {
        "path_class",
        "heading",
        "editor_markers_present",
        "shell_markers_present",
    }
    try:
        UiDaybooksOpenInput.model_validate({"url": "https://mit.billy.dk/x/daybooks/new"})
        raise AssertionError("expected validation error")
    except Exception:
        pass
    try:
        UiDaybooksOpenInput.model_validate({"create": True})
        raise AssertionError("expected validation error")
    except Exception:
        pass
    try:
        UiDaybooksOpenSuccess.model_validate(
            {
                "path_class": "/:org_slug/daybooks",
                "editor_markers_present": True,
                "shell_markers_present": True,
            }
        )
        raise AssertionError("expected validation error")
    except Exception:
        pass


def test_ui_bills_list_models_are_empty_input_and_non_pii_success() -> None:
    assert UiBillsListInput().model_dump() == {}
    success = UiBillsListSuccess(create_action_visible=True, shell_markers_present=True)
    assert success.model_dump() == {
        "path_class": "/:org_slug/bills",
        "heading": "Køb",
        "create_action_visible": True,
        "shell_markers_present": True,
    }
    properties = UiBillsListSuccess.model_json_schema().get("properties", {})
    for forbidden in (
        "email",
        "password",
        "token",
        "org_slug",
        "url",
        "bill_number",
        "supplier_name",
        "voucher_no",
        "selector",
    ):
        assert forbidden not in properties
    with pytest.raises(ValidationError):
        UiBillsListInput.model_validate({"url": "https://untrusted.example"})
    with pytest.raises(ValidationError):
        UiBillsListSuccess.model_validate(
            {
                "path_class": "/:org_slug/bills",
                "heading": "Køb",
                "create_action_visible": True,
                "shell_markers_present": True,
                "supplier_name": "secret",
            }
        )


def test_ui_transactions_list_models_are_empty_input_and_non_pii_success() -> None:
    assert UiTransactionsListInput().model_dump() == {}
    success = UiTransactionsListSuccess(
        create_action_visible=True,
        shell_markers_present=True,
    )
    assert success.model_dump() == {
        "path_class": "/:org_slug/transactions",
        "heading": "Posteringer",
        "create_action_visible": True,
        "shell_markers_present": True,
    }
    properties = UiTransactionsListSuccess.model_json_schema().get("properties", {})
    for forbidden in (
        "email",
        "password",
        "token",
        "org_slug",
        "url",
        "transaction_no",
        "voucher_no",
        "selector",
        "period",
    ):
        assert forbidden not in properties
    with pytest.raises(ValidationError):
        UiTransactionsListInput.model_validate({"url": "https://untrusted.example"})
    with pytest.raises(ValidationError):
        UiTransactionsListSuccess.model_validate(
            {
                "path_class": "/:org_slug/transactions",
                "heading": "Posteringer",
                "create_action_visible": True,
                "shell_markers_present": True,
                "transaction_no": "secret",
            }
        )
    with pytest.raises(ValidationError):
        UiTransactionsListSuccess.model_validate(
            {
                "path_class": "/:org_slug/transactions/new",
                "heading": "Posteringer",
                "create_action_visible": True,
                "shell_markers_present": True,
            }
        )


def test_ui_reports_open_models_are_empty_input_and_non_pii_success() -> None:
    assert UiReportsOpenInput().model_dump() == {}
    success = UiReportsOpenSuccess(
        export_action_visible=True,
        shell_markers_present=True,
    )
    assert success.model_dump() == {
        "path_class": "/:org_slug/reports-all",
        "heading": "Rapporter",
        "export_action_visible": True,
        "shell_markers_present": True,
    }
    properties = UiReportsOpenSuccess.model_json_schema().get("properties", {})
    for forbidden in (
        "email",
        "password",
        "token",
        "org_slug",
        "url",
        "period",
        "amount",
        "selector",
        "account",
    ):
        assert forbidden not in properties
    with pytest.raises(ValidationError):
        UiReportsOpenInput.model_validate({"url": "https://untrusted.example"})
    with pytest.raises(ValidationError):
        UiReportsOpenSuccess.model_validate(
            {
                "path_class": "/:org_slug/reports-all",
                "heading": "Rapporter",
                "export_action_visible": True,
                "shell_markers_present": True,
                "period": "secret",
            }
        )
    with pytest.raises(ValidationError):
        UiReportsOpenSuccess.model_validate(
            {
                "path_class": "/:org_slug/reports",
                "heading": "Rapporter",
                "export_action_visible": True,
                "shell_markers_present": True,
            }
        )


def test_ui_vat_declarations_list_models_are_empty_input_and_non_pii_success() -> None:
    assert UiVatDeclarationsListInput().model_dump() == {}
    success = UiVatDeclarationsListSuccess(
        period_column_visible=True,
        shell_markers_present=True,
    )
    assert success.model_dump() == {
        "path_class": "/:org_slug/vat-declarations",
        "heading": "Momsangivelser",
        "period_column_visible": True,
        "shell_markers_present": True,
    }
    properties = UiVatDeclarationsListSuccess.model_json_schema().get("properties", {})
    for forbidden in (
        "email",
        "password",
        "token",
        "org_slug",
        "url",
        "period",
        "amount",
        "selector",
        "account",
    ):
        assert forbidden not in properties
    with pytest.raises(ValidationError):
        UiVatDeclarationsListInput.model_validate({"url": "https://untrusted.example"})
    with pytest.raises(ValidationError):
        UiVatDeclarationsListSuccess.model_validate(
            {
                "path_class": "/:org_slug/vat-declarations",
                "heading": "Momsangivelser",
                "period_column_visible": True,
                "shell_markers_present": True,
                "period": "secret",
            }
        )
    with pytest.raises(ValidationError):
        UiVatDeclarationsListSuccess.model_validate(
            {
                "path_class": "/:org_slug/vat",
                "heading": "Momsangivelser",
                "period_column_visible": True,
                "shell_markers_present": True,
            }
        )


def test_ui_exports_open_models_are_empty_input_and_non_pii_success() -> None:
    assert UiExportsOpenInput().model_dump() == {}
    success = UiExportsOpenSuccess(
        saft_export_cta_observed=True,
        shell_markers_present=True,
    )
    assert success.model_dump() == {
        "path_class": "/:org_slug/exports",
        "heading": "Eksportér data",
        "saft_export_cta_observed": True,
        "shell_markers_present": True,
    }
    properties = UiExportsOpenSuccess.model_json_schema().get("properties", {})
    for forbidden in (
        "email",
        "password",
        "token",
        "org_slug",
        "url",
        "selector",
        "download",
        "file",
    ):
        assert forbidden not in properties
    with pytest.raises(ValidationError):
        UiExportsOpenInput.model_validate({"url": "https://untrusted.example"})
    with pytest.raises(ValidationError):
        UiExportsOpenSuccess.model_validate(
            {
                "path_class": "/:org_slug/exports",
                "heading": "Eksportér data",
                "saft_export_cta_observed": True,
                "shell_markers_present": True,
                "download_url": "secret",
            }
        )
    with pytest.raises(ValidationError):
        UiExportsOpenSuccess.model_validate(
            {
                "path_class": "/:org_slug/export",
                "heading": "Eksportér data",
                "saft_export_cta_observed": True,
                "shell_markers_present": True,
            }
        )


def test_ui_saft_exports_open_models_require_saft_cta() -> None:
    assert UiSaftExportsOpenInput().model_dump() == {}
    success = UiSaftExportsOpenSuccess(shell_markers_present=True)
    assert success.model_dump() == {
        "path_class": "/:org_slug/exports",
        "heading": "Eksportér data",
        "saft_export_cta_observed": True,
        "shell_markers_present": True,
    }
    properties = UiSaftExportsOpenSuccess.model_json_schema().get("properties", {})
    for forbidden in (
        "email",
        "password",
        "token",
        "org_slug",
        "url",
        "selector",
        "download",
        "file",
    ):
        assert forbidden not in properties
    with pytest.raises(ValidationError):
        UiSaftExportsOpenInput.model_validate({"url": "https://untrusted.example"})
    with pytest.raises(ValidationError):
        UiSaftExportsOpenSuccess.model_validate(
            {
                "path_class": "/:org_slug/exports",
                "heading": "Eksportér data",
                "saft_export_cta_observed": False,
                "shell_markers_present": True,
            }
        )
    with pytest.raises(ValidationError):
        UiSaftExportsOpenSuccess.model_validate(
            {
                "path_class": "/:org_slug/saft",
                "heading": "Eksportér data",
                "saft_export_cta_observed": True,
                "shell_markers_present": True,
            }
        )


def test_ui_addons_open_models_fordele_shell() -> None:
    assert UiAddonsOpenInput().model_dump() == {}
    success = UiAddonsOpenSuccess(shell_markers_present=True)
    assert success.model_dump() == {
        "path_class": "/:org_slug/add-ons",
        "heading": "Fordele",
        "shell_markers_present": True,
    }
    properties = UiAddonsOpenSuccess.model_json_schema().get("properties", {})
    for forbidden in (
        "email",
        "password",
        "token",
        "org_slug",
        "url",
        "selector",
        "partner",
        "file",
    ):
        assert forbidden not in properties
    with pytest.raises(ValidationError):
        UiAddonsOpenInput.model_validate({"url": "https://untrusted.example"})
    with pytest.raises(ValidationError):
        UiAddonsOpenSuccess.model_validate(
            {
                "path_class": "/:org_slug/addons",
                "heading": "Fordele",
                "shell_markers_present": True,
            }
        )
    with pytest.raises(ValidationError):
        UiAddonsOpenSuccess.model_validate(
            {
                "path_class": "/:org_slug/add-ons",
                "heading": "Integrationer",
                "shell_markers_present": True,
            }
        )


def test_ui_integrations_open_models_soft_empty_shell() -> None:
    assert UiIntegrationsOpenInput().model_dump() == {}
    success = UiIntegrationsOpenSuccess(shell_markers_present=True)
    assert success.model_dump() == {
        "path_class": "/:org_slug/integrations",
        "shell_kind": "soft_empty",
        "dedicated_shell": False,
        "same_shell_as_addons": False,
        "heading": "",
        "shell_markers_present": True,
    }
    properties = UiIntegrationsOpenSuccess.model_json_schema().get("properties", {})
    for forbidden in (
        "email",
        "password",
        "token",
        "org_slug",
        "url",
        "selector",
        "partner",
        "file",
    ):
        assert forbidden not in properties
    with pytest.raises(ValidationError):
        UiIntegrationsOpenInput.model_validate({"url": "https://untrusted.example"})
    with pytest.raises(ValidationError):
        UiIntegrationsOpenSuccess.model_validate(
            {
                "path_class": "/:org_slug/add-ons",
                "shell_kind": "soft_empty",
                "dedicated_shell": False,
                "same_shell_as_addons": False,
                "heading": "",
                "shell_markers_present": True,
            }
        )
    with pytest.raises(ValidationError):
        UiIntegrationsOpenSuccess.model_validate(
            {
                "path_class": "/:org_slug/integrations",
                "shell_kind": "soft_empty",
                "dedicated_shell": True,
                "same_shell_as_addons": False,
                "heading": "",
                "shell_markers_present": True,
            }
        )
    with pytest.raises(ValidationError):
        UiIntegrationsOpenSuccess.model_validate(
            {
                "path_class": "/:org_slug/integrations",
                "shell_kind": "soft_empty",
                "dedicated_shell": False,
                "same_shell_as_addons": False,
                "heading": "Fordele",
                "shell_markers_present": True,
            }
        )


def test_ui_inventory_open_models_lagermodul_shell() -> None:
    assert UiInventoryOpenInput().model_dump() == {}
    success = UiInventoryOpenSuccess(create_cta_markers_present=True)
    assert success.model_dump() == {
        "path_class": "/:org_slug/inventory",
        "heading": "Lagermodul",
        "shell_kind": "lagermodul",
        "create_cta_markers_present": True,
    }
    properties = UiInventoryOpenSuccess.model_json_schema().get("properties", {})
    for forbidden in (
        "email",
        "password",
        "token",
        "org_slug",
        "url",
        "selector",
        "partner",
        "file",
    ):
        assert forbidden not in properties
    with pytest.raises(ValidationError):
        UiInventoryOpenInput.model_validate({"url": "https://untrusted.example"})
    with pytest.raises(ValidationError):
        UiInventoryOpenSuccess.model_validate(
            {
                "path_class": "/:org_slug/products",
                "heading": "Lagermodul",
                "shell_kind": "lagermodul",
                "create_cta_markers_present": True,
            }
        )
    with pytest.raises(ValidationError):
        UiInventoryOpenSuccess.model_validate(
            {
                "path_class": "/:org_slug/inventory",
                "heading": "Produkter",
                "shell_kind": "lagermodul",
                "create_cta_markers_present": True,
            }
        )
    with pytest.raises(ValidationError):
        UiInventoryOpenSuccess.model_validate(
            {
                "path_class": "/:org_slug/inventory",
                "heading": "Lagermodul",
                "shell_kind": "soft_empty",
                "create_cta_markers_present": True,
            }
        )


def test_ui_settings_company_open_models_company_shell() -> None:
    assert UiSettingsCompanyOpenInput().model_dump() == {}
    success = UiSettingsCompanyOpenSuccess(company_panel_markers_present=True)
    assert success.model_dump() == {
        "path_class": "/:org_slug/settings",
        "heading": "Indstillinger",
        "shell_kind": "settings_company",
        "company_panel_markers_present": True,
    }
    properties = UiSettingsCompanyOpenSuccess.model_json_schema().get("properties", {})
    for forbidden in (
        "email",
        "password",
        "token",
        "org_slug",
        "url",
        "selector",
        "partner",
        "file",
    ):
        assert forbidden not in properties
    with pytest.raises(ValidationError):
        UiSettingsCompanyOpenInput.model_validate({"url": "https://untrusted.example"})
    with pytest.raises(ValidationError):
        UiSettingsCompanyOpenSuccess.model_validate(
            {
                "path_class": "/:org_slug/settings/company",
                "heading": "Indstillinger",
                "shell_kind": "settings_company",
                "company_panel_markers_present": True,
            }
        )
    with pytest.raises(ValidationError):
        UiSettingsCompanyOpenSuccess.model_validate(
            {
                "path_class": "/:org_slug/settings",
                "heading": "Settings",
                "shell_kind": "settings_company",
                "company_panel_markers_present": True,
            }
        )
    with pytest.raises(ValidationError):
        UiSettingsCompanyOpenSuccess.model_validate(
            {
                "path_class": "/:org_slug/settings",
                "heading": "Indstillinger",
                "shell_kind": "soft_empty",
                "company_panel_markers_present": True,
            }
        )


def test_ui_settings_accounting_open_models_accounting_shell() -> None:
    assert UiSettingsAccountingOpenInput().model_dump() == {}
    success = UiSettingsAccountingOpenSuccess(accounting_panel_markers_present=True)
    assert success.model_dump() == {
        "path_class": "/:org_slug/settings",
        "heading": "Indstillinger",
        "shell_kind": "settings_accounting",
        "accounting_panel_markers_present": True,
    }
    properties = UiSettingsAccountingOpenSuccess.model_json_schema().get("properties", {})
    for forbidden in (
        "email",
        "password",
        "token",
        "org_slug",
        "url",
        "selector",
        "partner",
        "file",
    ):
        assert forbidden not in properties
    with pytest.raises(ValidationError):
        UiSettingsAccountingOpenInput.model_validate({"url": "https://untrusted.example"})
    with pytest.raises(ValidationError):
        UiSettingsAccountingOpenSuccess.model_validate(
            {
                "path_class": "/:org_slug/settings/accounting",
                "heading": "Indstillinger",
                "shell_kind": "settings_accounting",
                "accounting_panel_markers_present": True,
            }
        )
    with pytest.raises(ValidationError):
        UiSettingsAccountingOpenSuccess.model_validate(
            {
                "path_class": "/:org_slug/settings",
                "heading": "Indstillinger",
                "shell_kind": "settings_company",
                "accounting_panel_markers_present": True,
            }
        )


def test_ui_settings_invoicing_open_models_invoicing_shell() -> None:
    assert UiSettingsInvoicingOpenInput().model_dump() == {}
    success = UiSettingsInvoicingOpenSuccess(invoicing_panel_markers_present=True)
    assert success.model_dump() == {
        "path_class": "/:org_slug/settings",
        "heading": "Indstillinger",
        "shell_kind": "settings_invoicing",
        "invoicing_panel_markers_present": True,
    }
    properties = UiSettingsInvoicingOpenSuccess.model_json_schema().get("properties", {})
    assert "org_slug" not in properties
    assert "email" not in str(properties).lower()
    with pytest.raises(ValidationError):
        UiSettingsInvoicingOpenInput.model_validate({"url": "https://untrusted.example"})
    with pytest.raises(ValidationError):
        UiSettingsInvoicingOpenSuccess.model_validate(
            {
                "path_class": "/:org_slug/settings",
                "heading": "Indstillinger",
                "shell_kind": "settings_invoicing",
            }
        )
    with pytest.raises(ValidationError):
        UiSettingsInvoicingOpenSuccess.model_validate(
            {
                "path_class": "/:org_slug/other",
                "heading": "Indstillinger",
                "shell_kind": "settings_invoicing",
                "invoicing_panel_markers_present": True,
            }
        )


def test_ui_settings_user_open_models_user_shell() -> None:
    assert UiSettingsUserOpenInput().model_dump() == {}
    success = UiSettingsUserOpenSuccess(user_panel_markers_present=True)
    assert success.model_dump() == {
        "path_class": "/:org_slug/settings",
        "heading": "Indstillinger",
        "shell_kind": "settings_user",
        "user_panel_markers_present": True,
    }
    properties = UiSettingsUserOpenSuccess.model_json_schema().get("properties", {})
    assert "org_slug" not in properties
    assert "email" not in str(properties).lower()
    with pytest.raises(ValidationError):
        UiSettingsUserOpenInput.model_validate({"url": "https://untrusted.example"})
    with pytest.raises(ValidationError):
        UiSettingsUserOpenSuccess.model_validate(
            {
                "path_class": "/:org_slug/settings",
                "heading": "Indstillinger",
                "shell_kind": "settings_user",
            }
        )
    with pytest.raises(ValidationError):
        UiSettingsUserOpenSuccess.model_validate(
            {
                "path_class": "/:org_slug/other",
                "heading": "Indstillinger",
                "shell_kind": "settings_user",
                "user_panel_markers_present": True,
            }
        )


def test_ui_settings_user_organizations_open_models_user_orgs_shell() -> None:
    assert UiSettingsUserOrganizationsOpenInput().model_dump() == {}
    success = UiSettingsUserOrganizationsOpenSuccess(user_organizations_panel_markers_present=True)
    assert success.model_dump() == {
        "path_class": "/:org_slug/settings",
        "heading": "Indstillinger",
        "shell_kind": "settings_user_organizations",
        "user_organizations_panel_markers_present": True,
    }
    properties = UiSettingsUserOrganizationsOpenSuccess.model_json_schema().get("properties", {})
    assert "user_organizations_panel_markers_present" in properties
    with pytest.raises(ValidationError):
        UiSettingsUserOrganizationsOpenInput.model_validate({"url": "https://untrusted.example"})
    with pytest.raises(ValidationError):
        UiSettingsUserOrganizationsOpenSuccess.model_validate(
            {
                "path_class": "/:org_slug/settings",
                "heading": "Indstillinger",
                "shell_kind": "settings_user",
                "user_organizations_panel_markers_present": True,
            }
        )
    with pytest.raises(ValidationError):
        UiSettingsUserOrganizationsOpenSuccess.model_validate(
            {
                "path_class": "/:org_slug/other",
                "heading": "Indstillinger",
                "shell_kind": "settings_user_organizations",
                "user_organizations_panel_markers_present": True,
            }
        )


def test_ui_settings_vat_open_models_vat_shell() -> None:
    assert UiSettingsVatOpenInput().model_dump() == {}
    success = UiSettingsVatOpenSuccess(vat_panel_markers_present=True)
    assert success.model_dump() == {
        "path_class": "/:org_slug/settings",
        "heading": "Indstillinger",
        "shell_kind": "settings_vat",
        "vat_panel_markers_present": True,
    }
    properties = UiSettingsVatOpenSuccess.model_json_schema().get("properties", {})
    assert "org_slug" not in properties
    assert "email" not in str(properties).lower()
    with pytest.raises(ValidationError):
        UiSettingsVatOpenInput.model_validate({"url": "https://untrusted.example"})
    with pytest.raises(ValidationError):
        UiSettingsVatOpenSuccess.model_validate(
            {
                "path_class": "/:org_slug/settings",
                "heading": "Indstillinger",
                "shell_kind": "settings_vat",
            }
        )
    with pytest.raises(ValidationError):
        UiSettingsVatOpenSuccess.model_validate(
            {
                "path_class": "/:org_slug/other",
                "heading": "Indstillinger",
                "shell_kind": "settings_vat",
                "vat_panel_markers_present": True,
            }
        )


def test_ui_settings_users_open_models_users_shell() -> None:
    assert UiSettingsUsersOpenInput().model_dump() == {}
    success = UiSettingsUsersOpenSuccess(users_panel_markers_present=True)
    assert success.model_dump() == {
        "path_class": "/:org_slug/settings",
        "heading": "Indstillinger",
        "shell_kind": "settings_users",
        "users_panel_markers_present": True,
    }
    properties = UiSettingsUsersOpenSuccess.model_json_schema().get("properties", {})
    assert "org_slug" not in properties
    assert "email" not in str(properties).lower()
    with pytest.raises(ValidationError):
        UiSettingsUsersOpenInput.model_validate({"url": "https://untrusted.example"})
    with pytest.raises(ValidationError):
        UiSettingsUsersOpenSuccess.model_validate(
            {
                "path_class": "/:org_slug/settings",
                "heading": "Indstillinger",
                "shell_kind": "settings_users",
            }
        )
    with pytest.raises(ValidationError):
        UiSettingsUsersOpenSuccess.model_validate(
            {
                "path_class": "/:org_slug/other",
                "heading": "Indstillinger",
                "shell_kind": "settings_users",
                "users_panel_markers_present": True,
            }
        )


def test_ui_settings_access_token_open_models_access_token_shell() -> None:
    assert UiSettingsAccessTokenOpenInput().model_dump() == {}
    success = UiSettingsAccessTokenOpenSuccess(access_token_panel_markers_present=True)
    assert success.model_dump() == {
        "path_class": "/:org_slug/settings",
        "heading": "Indstillinger",
        "shell_kind": "settings_access_token",
        "access_token_panel_markers_present": True,
    }
    properties = UiSettingsAccessTokenOpenSuccess.model_json_schema().get("properties", {})
    assert "path_class" in properties
    with pytest.raises(ValidationError):
        UiSettingsAccessTokenOpenInput.model_validate({"url": "https://untrusted.example"})
    with pytest.raises(ValidationError):
        UiSettingsAccessTokenOpenSuccess.model_validate(
            {
                "path_class": "/:org_slug/settings",
                "heading": "Indstillinger",
                "shell_kind": "settings_users",
                "access_token_panel_markers_present": True,
            }
        )
    with pytest.raises(ValidationError):
        UiSettingsAccessTokenOpenSuccess.model_validate(
            {
                "path_class": "/:org_slug/other",
                "heading": "Indstillinger",
                "shell_kind": "settings_access_token",
                "access_token_panel_markers_present": True,
            }
        )


def test_ui_settings_beta_open_models_beta_shell() -> None:
    assert UiSettingsBetaOpenInput().model_dump() == {}
    success = UiSettingsBetaOpenSuccess(beta_panel_markers_present=True)
    assert success.model_dump() == {
        "path_class": "/:org_slug/settings",
        "heading": "Indstillinger",
        "shell_kind": "settings_beta",
        "beta_panel_markers_present": True,
    }
    properties = UiSettingsBetaOpenSuccess.model_json_schema().get("properties", {})
    assert "path_class" in properties
    with pytest.raises(ValidationError):
        UiSettingsBetaOpenInput.model_validate({"url": "https://untrusted.example"})
    with pytest.raises(ValidationError):
        UiSettingsBetaOpenSuccess.model_validate(
            {
                "path_class": "/:org_slug/settings",
                "heading": "Indstillinger",
                "shell_kind": "settings_access_token",
                "beta_panel_markers_present": True,
            }
        )
    with pytest.raises(ValidationError):
        UiSettingsBetaOpenSuccess.model_validate(
            {
                "path_class": "/:org_slug/other",
                "heading": "Indstillinger",
                "shell_kind": "settings_beta",
                "beta_panel_markers_present": True,
            }
        )


def test_ui_settings_subscription_open_models_empty_panel_shell() -> None:
    assert UiSettingsSubscriptionOpenInput().model_dump() == {}
    success = UiSettingsSubscriptionOpenSuccess(empty_panel=True)
    assert success.model_dump() == {
        "path_class": "/:org_slug/settings",
        "heading": "Indstillinger",
        "shell_kind": "settings_subscription",
        "empty_panel": True,
    }
    properties = UiSettingsSubscriptionOpenSuccess.model_json_schema().get("properties", {})
    assert "url" not in properties
    with pytest.raises(ValidationError):
        UiSettingsSubscriptionOpenInput.model_validate({"url": "https://untrusted.example"})
    with pytest.raises(ValidationError):
        UiSettingsSubscriptionOpenSuccess.model_validate(
            {
                "path_class": "/:org_slug/settings",
                "heading": "Indstillinger",
                "shell_kind": "settings_beta",
                "empty_panel": True,
            }
        )
    with pytest.raises(ValidationError):
        UiSettingsSubscriptionOpenSuccess.model_validate(
            {
                "path_class": "/:org_slug/settings",
                "heading": "Indstillinger",
                "shell_kind": "settings_subscription",
            }
        )
