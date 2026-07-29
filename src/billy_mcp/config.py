"""Runtime configuration and non-serialisable credential resolution."""

from __future__ import annotations

import os
from collections.abc import Mapping
from pathlib import Path
from typing import Literal

import keyring
from pydantic import BaseModel, ConfigDict, Field, field_validator

API_BASE_URL = "https://api.billysbilling.com/v2"
KEYRING_SERVICE = "billy-mcp"


def default_browser_profile(home: Path) -> Path:
    """Return the MCP-owned profile location for one operating-system account."""

    return home / ".local" / "share" / "billy-mcp" / "chrome-profile"


# The persistent profile belongs to the account running the MCP server.  It is
# deliberately not a project-relative directory: browser state must survive
# deployments and must never be checked into the repository.
DEFAULT_BROWSER_PROFILE = default_browser_profile(Path.home())


class AppConfig(BaseModel):
    """Safe, serialisable runtime settings; credentials are resolved separately."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    api_base_url: Literal["https://api.billysbilling.com/v2"] = API_BASE_URL
    selected_organization: str | None = Field(default=None, min_length=1)
    browser_profile: Path = DEFAULT_BROWSER_PROFILE
    allowed_upload_roots: tuple[Path, ...] = ()

    @field_validator("browser_profile", mode="after")
    @classmethod
    def canonical_browser_profile(cls, value: Path) -> Path:
        return value.expanduser().resolve(strict=False)

    @field_validator("allowed_upload_roots", mode="after")
    @classmethod
    def canonical_upload_roots(cls, value: tuple[Path, ...]) -> tuple[Path, ...]:
        return tuple(root.expanduser().resolve(strict=False) for root in value)

    @classmethod
    def from_environment(cls, environment: Mapping[str, str] | None = None) -> AppConfig:
        """Load safe settings without ever retaining the API token in this model."""

        source = os.environ if environment is None else environment
        profile = Path(source.get("BILLY_BROWSER_PROFILE", str(DEFAULT_BROWSER_PROFILE)))
        roots_value = source.get("BILLY_UPLOAD_ROOTS", "")
        roots = tuple(Path(root) for root in roots_value.split(os.pathsep) if root)
        return cls(
            selected_organization=source.get("BILLY_ORGANIZATION_ID") or None,
            browser_profile=profile,
            allowed_upload_roots=roots,
        )

    def resolve_api_token(self, environment: Mapping[str, str] | None = None) -> str | None:
        """Resolve a token for internal use, preferring the process environment."""

        source = os.environ if environment is None else environment
        token = source.get("BILLY_API_TOKEN")
        if token:
            return token
        account = (
            f"organization:{self.selected_organization}"
            if self.selected_organization
            else "default"
        )
        return keyring.get_password(KEYRING_SERVICE, account)
