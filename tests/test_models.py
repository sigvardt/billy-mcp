"""Tests for root-owned typed contracts shared by Phase 0 modules."""

import pytest
from pydantic import ValidationError

from billy_mcp.models import (
    AuthStatusInput,
    AuthStatusSuccess,
    CoverageStatus,
    StableErrorCode,
    ToolError,
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
