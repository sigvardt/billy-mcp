"""Stable translation of Billy responses into public MCP errors."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any, cast

from billy_mcp.models import StableErrorCode, ToolError
from billy_mcp.redaction import redact

_AUTHENTICATION_CODES = {"AUTHENTICATION_REQUIRED", "OAUTH_INVALID_ACCESS_TOKEN"}


def translate_upstream_error(status_code: int, payload: object) -> ToolError:
    """Map a sanitised Billy error envelope without exposing credential material."""

    envelope: dict[str, object] = {}
    if isinstance(payload, Mapping):
        mapping = cast(Mapping[object, object], payload)
        envelope = {str(key): value for key, value in mapping.items()}
    error_code = envelope.get("errorCode")
    sanitised_envelope = {key: value for key, value in envelope.items() if key != "errorMessage"}
    details: dict[str, Any] = {
        "upstream_status": status_code,
        "upstream": redact(sanitised_envelope),
    }
    if isinstance(error_code, str) and error_code in _AUTHENTICATION_CODES:
        return ToolError(
            code=StableErrorCode.AUTH_REQUIRED,
            message="Billy API authentication is required.",
            details=details,
        )
    if status_code == 404:
        code = StableErrorCode.NOT_FOUND
    elif status_code == 409:
        code = StableErrorCode.CONFLICT
    elif status_code == 429:
        code = StableErrorCode.RATE_LIMITED
    else:
        code = StableErrorCode.BILLY_ERROR
    return ToolError(code=code, message="Billy API request failed.", details=details)


def unavailable_coverage_error(missing: list[str]) -> ToolError:
    """Describe absent generated coverage data without manufacturing a status."""

    return ToolError(
        code=StableErrorCode.NOT_FOUND,
        message="Coverage manifests are unavailable.",
        details={"missing": missing},
    )
