from __future__ import annotations

import pytest

from billy_mcp.errors import translate_upstream_error
from billy_mcp.models import StableErrorCode
from billy_mcp.redaction import REDACTED, redact


def test_redaction_recurses_over_nested_authentication_values() -> None:
    result = redact(
        {
            "token": "api-secret",
            "nested": [{"Password": "password"}, {"totp_code": "123456"}],
            "headers": {"Authorization": "Bearer secret", "Cookie": "session=value"},
            "ticket": "opaque-ticket",
            "visible": "safe",
        }
    )

    assert result == {
        "token": REDACTED,
        "nested": [{"Password": REDACTED}, {"totp_code": REDACTED}],
        "headers": {"Authorization": REDACTED, "Cookie": REDACTED},
        "ticket": REDACTED,
        "visible": "safe",
    }


@pytest.mark.parametrize("upstream_code", ["AUTHENTICATION_REQUIRED", "OAUTH_INVALID_ACCESS_TOKEN"])
def test_known_401_codes_become_auth_required_with_sanitised_metadata(upstream_code: str) -> None:
    error = translate_upstream_error(
        401,
        {
            "errorCode": upstream_code,
            "errorMessage": "Invalid OAuth token",
            "helpUrl": "https://www.billy.dk/support/",
            "meta": {"statusCode": 401, "authorization": "Bearer secret"},
        },
    )

    assert error.code is StableErrorCode.AUTH_REQUIRED
    assert error.details["upstream"]["errorCode"] == upstream_code
    assert error.details["upstream"]["meta"]["authorization"] == REDACTED
