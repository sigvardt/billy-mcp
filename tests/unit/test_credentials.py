from __future__ import annotations

import pytest
from pydantic import ValidationError

from billy_mcp.credentials import (
    CREDENTIAL_STORE_SERVICE,
    BrowserCredentialReferences,
    CredentialReference,
    KeyringCredentialResolver,
)


def test_browser_credential_references_are_opaque_and_require_two_locators() -> None:
    references = BrowserCredentialReferences(
        primary=CredentialReference(opaque_id="opaque-primary-ref"),
        secondary=CredentialReference(opaque_id="opaque-secondary-ref"),
    )

    assert references.has_required_references()
    assert set(references.model_dump()) == {"primary", "secondary"}
    assert set(BrowserCredentialReferences.model_json_schema()["properties"]) == {
        "primary",
        "secondary",
    }


@pytest.mark.parametrize("opaque_id", ["", "   "])
def test_credential_reference_rejects_empty_locator(opaque_id: str) -> None:
    with pytest.raises(
        ValidationError, match="credential reference must not be blank|String should"
    ):
        CredentialReference(opaque_id=opaque_id)


def test_keyring_resolver_receives_only_the_opaque_locator(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    observed: list[tuple[str, str]] = []

    def get_password(service: str, account: str) -> str:
        observed.append((service, account))
        return "resolved-placeholder"

    monkeypatch.setattr("billy_mcp.credentials.keyring.get_password", get_password)

    result = KeyringCredentialResolver().resolve(CredentialReference(opaque_id="opaque-ref"))

    assert result == "resolved-placeholder"
    assert observed == [(CREDENTIAL_STORE_SERVICE, "opaque-ref")]
