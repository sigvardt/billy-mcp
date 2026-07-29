from __future__ import annotations

import pytest

from billy_mcp.errors import translate_upstream_error
from billy_mcp.models import StableErrorCode
from billy_mcp.redaction import REDACTED, redact

ORGANIZATION_SUBSCRIPTION_FIXTURE = {
    "organization": {
        "subscriptionCardType": "visa",
        "subscriptionCardNumber": "test-card-number",
        "subscriptionCardExpires": "2099-01",
        "subscriptionTransaction": {"id": "subscription-transaction"},
        "isSubscriptionBankPayer": True,
        "subscriptionPrice": 123.45,
        "subscriptionPeriod": "monthly",
        "subscriptionDiscount": 10.0,
        "subscriptionExpires": "2099-12-31",
        "paymentTermsMode": "net",
        "paymentTermsDays": 30,
        "defaultInvoiceBankAccount": {"id": "invoice-bank-account"},
        "defaultBankFeeAccount": {"id": "fee-bank-account"},
        "defaultBillBankAccount": {"id": "bill-bank-account"},
    },
    "nested": [{"subscription_card_number": "nested-card-number"}],
}


def test_redaction_recursively_removes_organization_subscription_and_payment_values() -> None:
    result = redact(ORGANIZATION_SUBSCRIPTION_FIXTURE)

    assert result == {
        "organization": {
            "subscriptionCardType": REDACTED,
            "subscriptionCardNumber": REDACTED,
            "subscriptionCardExpires": REDACTED,
            "subscriptionTransaction": REDACTED,
            "isSubscriptionBankPayer": REDACTED,
            "subscriptionPrice": REDACTED,
            "subscriptionPeriod": REDACTED,
            "subscriptionDiscount": REDACTED,
            "subscriptionExpires": REDACTED,
            "paymentTermsMode": REDACTED,
            "paymentTermsDays": REDACTED,
            "defaultInvoiceBankAccount": REDACTED,
            "defaultBankFeeAccount": REDACTED,
            "defaultBillBankAccount": REDACTED,
        },
        "nested": [{"subscription_card_number": REDACTED}],
    }


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


def test_redaction_removes_wave_three_read_sensitive_values() -> None:
    result = redact(
        {
            "contactPerson": {"email": "customer@example.test", "name": "Visible name"},
            "account": {
                "bankName": "Test Bank",
                "bankRoutingNo": "12345678",
                "bankAccountNo": "1234567890",
                "bankSwift": "TESTDKKK",
                "bankIban": "DK5000400440116243",
            },
            "file": {
                "downloadUrl": "https://download.billy.dk/file?token=download-secret",
                "fileName": "visible.pdf",
            },
        }
    )

    assert result == {
        "contactPerson": {"email": REDACTED, "name": "Visible name"},
        "account": {
            "bankName": REDACTED,
            "bankRoutingNo": REDACTED,
            "bankAccountNo": REDACTED,
            "bankSwift": REDACTED,
            "bankIban": REDACTED,
        },
        "file": {"downloadUrl": REDACTED, "fileName": "visible.pdf"},
    }


def test_redaction_removes_wave_four_reminder_and_user_contact_values() -> None:
    result = redact(
        {
            "invoiceReminder": {
                "emailSubject": "Overdue invoice for Acme",
                "emailBody": "Payment is overdue for customer@example.test.",
                "downloadUrl": "https://download.billy.dk/reminder?token=download-secret",
                "createdTime": "2026-07-29T12:00:00Z",
            },
            "user": {"email": "operator@example.test", "phone": "+4512345678"},
        }
    )

    assert result == {
        "invoiceReminder": {
            "emailSubject": REDACTED,
            "emailBody": REDACTED,
            "downloadUrl": REDACTED,
            "createdTime": "2026-07-29T12:00:00Z",
        },
        "user": {"email": REDACTED, "phone": REDACTED},
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


def test_upstream_errors_do_not_echo_subscription_or_payment_fixture_values() -> None:
    payload = {
        **ORGANIZATION_SUBSCRIPTION_FIXTURE,
        "errorCode": "INVALID_SUBSCRIPTION",
        "errorMessage": "test-card-number could not be charged",
    }

    error = translate_upstream_error(422, payload)
    rendered_error = str(error.model_dump())

    assert error.message == "Billy API request failed."
    assert "errorMessage" not in error.details["upstream"]
    for value in (
        "test-card-number",
        "2099-01",
        "subscription-transaction",
        "invoice-bank-account",
        "fee-bank-account",
        "bill-bank-account",
        "nested-card-number",
    ):
        assert value not in rendered_error
