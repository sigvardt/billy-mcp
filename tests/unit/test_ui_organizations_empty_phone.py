"""Given the organization preview, When phone is empty, Then it is a clear."""

from __future__ import annotations

from pathlib import Path

import pytest
from pydantic import ValidationError

from billy_mcp.ui_writes.organizations import (
    OrganizationUpdatePreviewInput,
    register_ui_organization_write_tools,
)
from billy_mcp.ui_writes.organizations_phone import (
    named_input_matches,
    phone_action_from,
)
from tests.unit.test_ui_organizations_writes import call_tool, make_server


def test_preview_input_accepts_exact_empty_phone() -> None:
    parsed = OrganizationUpdatePreviewInput.model_validate(
        {"phone": "", "organization_id": "org-test"}
    )
    assert parsed.phone == ""
    assert parsed.organization_id == "org-test"


def test_preview_input_rejects_whitespace_only_phone() -> None:
    with pytest.raises(ValidationError):
        OrganizationUpdatePreviewInput.model_validate(
            {"phone": "   ", "organization_id": "org-test"}
        )


def test_preview_input_trims_non_empty_phone() -> None:
    parsed = OrganizationUpdatePreviewInput.model_validate(
        {"phone": "  +4500abcd1234  ", "organization_id": "org-test"}
    )
    assert parsed.phone == "+4500abcd1234"


def test_preview_empty_phone_is_clear_and_does_not_submit() -> None:
    server, _, submitter = make_server()
    assert submitter is not None

    preview = call_tool(
        server,
        "ui_organizations_update_preview",
        {"phone": "", "organization_id": "org-test"},
    )

    assert submitter.calls == []
    assert preview["canonical_request"] == {"phone": ""}
    effect = preview["expected_effect_state"]
    assert isinstance(effect, dict)
    assert effect["phone_action"] == "clear"
    assert "clear" in str(preview["summary"]).casefold()
    assert preview["confirmation_ticket"]


def test_preview_non_empty_phone_is_set() -> None:
    server, _, submitter = make_server()
    assert submitter is not None

    preview = call_tool(
        server,
        "ui_organizations_update_preview",
        {"phone": "+4500abcd1234", "organization_id": "org-test"},
    )

    assert submitter.calls == []
    assert preview["canonical_request"] == {"phone": "+4500abcd1234"}
    effect = preview["expected_effect_state"]
    assert isinstance(effect, dict)
    assert effect["phone_action"] == "set"
    assert "set" in str(preview["summary"]).casefold()


def test_named_input_readback_compares_exact_phone_including_empty() -> None:
    assert named_input_matches("", "") is True
    assert named_input_matches("+4500abcd1234", "+4500abcd1234") is True
    assert named_input_matches("", "+4500abcd1234") is False
    assert named_input_matches("+4500abcd1234", "") is False
    assert phone_action_from("") == "clear"
    assert phone_action_from("+4500abcd1234") == "set"


def test_live_org_write_names_four_state_frames() -> None:
    live = (
        Path(__file__).resolve().parents[2] / "tests" / "live" / "test_ui_organizations_writes.py"
    )
    body = live.read_text(encoding="utf-8")
    assert "01_initial.png" in body
    assert "02_before_submit.png" in body
    assert "03_after_set.png" in body
    assert "04_restored.png" in body
    assert "screenshot" in body


def test_organization_submit_does_not_use_page_wide_text_readback() -> None:
    root = Path(register_ui_organization_write_tools.__code__.co_filename).parent
    bodies = [
        (root / "organizations.py").read_text(encoding="utf-8"),
        (root / "organizations_phone.py").read_text(encoding="utf-8"),
        (root / "organizations_submit.py").read_text(encoding="utf-8"),
    ]
    joined = "\n".join(bodies)
    assert "prove_text_on_fresh_page" not in joined
    assert "named_input_matches" in joined
    assert "prove_phone_input_on_fresh_page" in joined
    assert "PHONE_INPUT_NAME" in joined
    assert "_PHONE_LOCATOR" in joined
    assert "input_value()" in joined
