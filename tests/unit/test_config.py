from __future__ import annotations

from pathlib import Path

import pytest
from pydantic import ValidationError

from billy_mcp.config import API_BASE_URL, KEYRING_SERVICE, AppConfig


def test_configuration_locks_api_base_and_does_not_serialize_token() -> None:
    config = AppConfig.from_environment(
        {
            "BILLY_API_TOKEN": "environment-secret",
            "BILLY_ORGANIZATION_ID": "org-1",
            "BILLY_UPLOAD_ROOTS": f"/tmp/one:{Path('/tmp/two')}",
        }
    )

    assert config.api_base_url == API_BASE_URL
    assert (
        config.resolve_api_token({"BILLY_API_TOKEN": "environment-secret"}) == "environment-secret"
    )
    assert "environment-secret" not in config.model_dump_json()
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
