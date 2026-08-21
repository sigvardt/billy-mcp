from __future__ import annotations

from pathlib import Path

import pytest
from pydantic import ValidationError

from billy_mcp.config import (
    API_BASE_URL,
    DEFAULT_BROWSER_PROFILE,
    KEYRING_SERVICE,
    AppConfig,
    default_browser_profile,
)


def test_configuration_locks_api_base_and_does_not_serialize_token() -> None:
    config = AppConfig.from_environment(
        {
            "BILLY_API_TOKEN": "environment-secret",
            "BILLY_ORGANIZATION_ID": "org-1",
            "BILLY_UPLOAD_ROOTS": f"/tmp/one:{Path('/tmp/two')}",
            "BILLY_BROWSER_PRIMARY_REFERENCE": "opaque-primary-ref",
            "BILLY_BROWSER_SECONDARY_REFERENCE": "opaque-secondary-ref",
        }
    )

    assert config.api_base_url == API_BASE_URL
    assert (
        config.resolve_api_token({"BILLY_API_TOKEN": "environment-secret"}) == "environment-secret"
    )
    assert "environment-secret" not in config.model_dump_json()
    assert config.browser_credentials.model_dump() == {
        "primary": {"opaque_id": "opaque-primary-ref"},
        "secondary": {"opaque_id": "opaque-secondary-ref"},
    }
    assert config.allowed_upload_roots == (Path("/tmp/one").resolve(), Path("/tmp/two").resolve())
    with pytest.raises(ValidationError):
        AppConfig.model_validate({"api_base_url": "https://api.billy.dk/v2"})


def test_keyring_token_resolution_follows_environment_precedence(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    seen: list[tuple[str, str]] = []

    def get_password(service: str, account: str) -> str:
        seen.append((service, account))
        return "keyring-secret"

    monkeypatch.setattr("billy_mcp.config.keyring.get_password", get_password)
    config = AppConfig(selected_organization="org-42")

    assert (
        config.resolve_api_token({"BILLY_API_TOKEN": "environment-secret"}) == "environment-secret"
    )
    assert seen == []
    assert config.resolve_api_token({}) == "keyring-secret"
    assert seen == [(KEYRING_SERVICE, "organization:org-42")]


def test_default_browser_profile_is_owned_by_the_running_account() -> None:
    expected_suffix = Path(".local/share/billy-mcp/chrome-profile")
    assert (
        default_browser_profile(Path("/tmp/mcp-account"))
        == Path("/tmp/mcp-account") / expected_suffix
    )
    assert DEFAULT_BROWSER_PROFILE == default_browser_profile(Path.home())


def test_configuration_treats_blank_browser_references_as_missing() -> None:
    config = AppConfig.from_environment(
        {
            "BILLY_BROWSER_PRIMARY_REFERENCE": "   ",
            "BILLY_BROWSER_SECONDARY_REFERENCE": "",
        }
    )

    assert config.browser_credentials.model_dump() == {
        "primary": None,
        "secondary": None,
    }
