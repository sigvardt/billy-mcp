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
    UiInvoicesListInput,
    UiInvoicesListSuccess,
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
