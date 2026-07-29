"""Tests for root-owned typed contracts shared by Phase 0 modules."""

from billy_mcp.models import CoverageStatus, StableErrorCode, ToolError


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
