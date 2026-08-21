"""Opaque browser credential references and their bounded resolver seam."""

from __future__ import annotations

from typing import Protocol

import keyring
from pydantic import BaseModel, ConfigDict, Field, field_validator

CREDENTIAL_STORE_SERVICE = "billy-mcp"


class CredentialReference(BaseModel):
    """A serialisable opaque locator; it never contains a resolved value."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    opaque_id: str = Field(min_length=1, max_length=256)

    @field_validator("opaque_id")
    @classmethod
    def require_nonblank_opaque_id(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("credential reference must not be blank")
        return value


class BrowserCredentialReferences(BaseModel):
    """The two opaque locators required by the only observed login transition."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    primary: CredentialReference | None = None
    secondary: CredentialReference | None = None

    def has_required_references(self) -> bool:
        """Return whether the bounded login transition can resolve its two inputs."""

        return self.primary is not None and self.secondary is not None


class CredentialResolver(Protocol):
    """Resolve one opaque locator only inside a bounded browser operation."""

    def resolve(self, reference: CredentialReference) -> str | None: ...


class KeyringCredentialResolver:
    """Resolve opaque locators from the operating-system credential store."""

    def resolve(self, reference: CredentialReference) -> str | None:
        """Return the value directly to the caller without storing or logging it."""

        return keyring.get_password(CREDENTIAL_STORE_SERVICE, reference.opaque_id)
