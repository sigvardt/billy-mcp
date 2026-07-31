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
    UiBankAccountsListInput,
    UiBankAccountsListSuccess,
    UiClientsListInput,
    UiClientsListSuccess,
    UiInvoicesListInput,
    UiInvoicesListSuccess,
    UiProductsImportInput,
    UiProductsImportSuccess,
    UiProductsListInput,
    UiProductsListSuccess,
    UiQuotesListInput,
    UiQuotesListSuccess,
    UiRecurringInvoicesListInput,
    UiRecurringInvoicesListSuccess,
    UiSuppliersListInput,
    UiSuppliersListSuccess,
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
