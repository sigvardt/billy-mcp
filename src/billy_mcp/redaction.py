"""Recursive redaction for secrets that must never reach logs or tool errors."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import cast

REDACTED = "[REDACTED]"
_SENSITIVE_PARTS = ("token", "password", "totp", "cookie", "ticket", "authorization")
_SENSITIVE_ORGANIZATION_PAYMENT_KEYS = frozenset(
    {
        "subscriptioncardtype",
        "subscriptioncardnumber",
        "subscriptioncardexpires",
        "subscriptiontransaction",
        "issubscriptionbankpayer",
        "subscriptionprice",
        "subscriptionperiod",
        "subscriptiondiscount",
        "subscriptionexpires",
        "defaultinvoicebankaccount",
        "defaultbankfeeaccount",
        "defaultbillbankaccount",
        "paymenttermsmode",
        "paymenttermsdays",
    }
)
_SENSITIVE_READ_KEYS = frozenset(
    {
        "email",
        "bankname",
        "bankroutingno",
        "bankaccountno",
        "bankswift",
        "bankiban",
        "downloadurl",
    }
)

type RedactedValue = (
    str | int | float | bool | None | list["RedactedValue"] | dict[str, "RedactedValue"]
)


def is_sensitive_key(key: str) -> bool:
    """Return whether a structured field name could contain protected data."""

    normalized = key.lower().replace("-", "").replace("_", "")
    return (
        normalized in _SENSITIVE_ORGANIZATION_PAYMENT_KEYS
        or normalized in _SENSITIVE_READ_KEYS
        or any(part in normalized for part in _SENSITIVE_PARTS)
    )


def redact(value: object) -> RedactedValue:
    """Copy nested structures while replacing values associated with secret-bearing keys."""

    if isinstance(value, Mapping):
        mapping = cast(Mapping[object, object], value)
        result: dict[str, RedactedValue] = {}
        for key, item in mapping.items():
            string_key = str(key)
            result[string_key] = REDACTED if is_sensitive_key(string_key) else redact(item)
        return result
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        sequence = cast(Sequence[object], value)
        return [redact(item) for item in sequence]
    if isinstance(value, bytes | bytearray):
        return REDACTED
    if value is None or isinstance(value, str | int | float | bool):
        return value
    return str(value)
