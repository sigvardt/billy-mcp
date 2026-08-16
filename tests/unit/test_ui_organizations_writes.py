"""Offline FastMCP ticket contract for UI organization update writes."""

from __future__ import annotations

import asyncio
from datetime import UTC, datetime, timedelta
from typing import cast

import pytest
from fastmcp import FastMCP
from pydantic import ValidationError

from billy_mcp.confirmations import MAX_TICKET_TTL, ConfirmationStore
from billy_mcp.models import StableErrorCode
from billy_mcp.ui_writes.organizations import (
    ALLOWED_COMPANY_FIELDS,
    FORBIDDEN_COMPANY_FIELDS,
    OrganizationUpdatePreviewInput,
    RecordingOrganizationSubmitter,
    register_ui_organization_write_tools,
)
from billy_mcp.ui_writes.protocol import (
    UiWriteExecuteInput,
    UiWritePreviewResult,
    UiWriteProtocol,
)


class Clock:
    """Controllable clock used only by local confirmation-expiry tests."""

    def __init__(self) -> None:
        self.now = datetime(2026, 8, 16, tzinfo=UTC)

    def __call__(self) -> datetime:
        return self.now


def make_server(
    *,
    submitter: RecordingOrganizationSubmitter | None = None,
    clock: Clock | None = None,
    protocol: UiWriteProtocol | None = None,
    attach_submitter: bool = True,
) -> tuple[FastMCP, UiWriteProtocol, RecordingOrganizationSubmitter | None]:
    """Isolated FastMCP server that registers only this family."""

    store = ConfirmationStore(clock=clock or Clock())
    write_protocol = protocol or UiWriteProtocol(store)
    resolved: RecordingOrganizationSubmitter | None
    if not attach_submitter:
        resolved = None
    elif submitter is None:
        resolved = RecordingOrganizationSubmitter()
    else:
        resolved = submitter
    server = FastMCP("ui-organization-write-contract-test")
    register_ui_organization_write_tools(server, write_protocol, submitter=resolved)
    return server, write_protocol, resolved


def call_tool(server: FastMCP, tool_name: str, arguments: dict[str, object]) -> dict[str, object]:
    """Call a typed tool and return its structured payload."""

    result = asyncio.run(server.call_tool(tool_name, arguments))
    structured_content = result.structured_content
    assert isinstance(structured_content, dict)
    payload = structured_content.get("result", structured_content)
    assert isinstance(payload, dict)
    return cast(dict[str, object], payload)


def test_registers_exactly_two_flat_typed_organization_update_tools() -> None:
    server, _, _ = make_server()

    by_name = {tool.name: tool for tool in asyncio.run(server.list_tools())}
    expected_properties = {
        "ui_organizations_update_preview": {"phone", "organization_id"},
        "ui_organizations_update_execute": {"confirmation_ticket"},
    }
    assert set(by_name) == set(expected_properties)
    for name, fields in expected_properties.items():
        schema = by_name[name].parameters
        properties = cast(dict[str, dict[str, object]], schema["properties"])
        assert schema["additionalProperties"] is False
        assert set(properties) == fields
        assert "input" not in properties
        for field in fields:
            assert properties[field]["minLength"] == 1


@pytest.mark.parametrize(
    "payload",
    [
        {"phone": "123", "extra": True},
        {"phone": ""},
        {"phone": "   "},
        {"name": "Acme"},
        {"users": "1"},
        {"subscription": "pro"},
        {"access_token": "tok"},
        {"confirmation_ticket": "ticket", "phone": "123"},
        {},
    ],
)
def test_preview_input_forbids_empty_extras_and_closed_fields(
    payload: dict[str, object],
) -> None:
    with pytest.raises(ValidationError):
        OrganizationUpdatePreviewInput.model_validate(payload)


def test_execute_input_accepts_only_confirmation_ticket() -> None:
    with pytest.raises(ValidationError):
        UiWriteExecuteInput.model_validate({"confirmation_ticket": "ticket", "phone": "123"})
    with pytest.raises(ValidationError):
        UiWriteExecuteInput.model_validate({"confirmation_ticket": ""})


def test_preview_issues_ticket_and_does_not_submit() -> None:
    server, _, submitter = make_server()
    assert submitter is not None

    preview = call_tool(
        server,
        "ui_organizations_update_preview",
        {"phone": "+4511111111", "organization_id": "org-test"},
    )

    assert submitter.calls == []
    assert preview["canonical_request"] == {"phone": "+4511111111"}
    assert preview["expected_effect_state"] == {
        "action": "update",
        "resource": "organization",
        "surface": "settings_company",
        "field": "phone",
    }
    assert isinstance(preview["confirmation_ticket"], str)
    assert preview["confirmation_ticket"]
    assert ALLOWED_COMPANY_FIELDS == frozenset({"phone"})
    assert "users" in FORBIDDEN_COMPANY_FIELDS
    assert "subscription" in FORBIDDEN_COMPANY_FIELDS
    assert "access_token" in FORBIDDEN_COMPANY_FIELDS


def test_execute_submits_once_and_replay_is_consumed() -> None:
    server, _, submitter = make_server()
    assert submitter is not None
    preview = call_tool(
        server,
        "ui_organizations_update_preview",
        {"phone": "+4522222222", "organization_id": "org-test"},
    )
    ticket = preview["confirmation_ticket"]

    first = call_tool(
        server,
        "ui_organizations_update_execute",
        {"confirmation_ticket": ticket},
    )
    replay = call_tool(
        server,
        "ui_organizations_update_execute",
        {"confirmation_ticket": ticket},
    )

    assert first["submitted"] is True
    assert first["canonical_request"] == {"phone": "+4522222222"}
    assert len(submitter.calls) == 1
    assert submitter.calls[0].canonical_request == {"phone": "+4522222222"}
    assert replay["code"] == StableErrorCode.CONFIRMATION_CONSUMED
    assert len(submitter.calls) == 1


def test_execute_rejects_wrong_tool_without_submit() -> None:
    clock = Clock()
    store = ConfirmationStore(clock=clock)
    protocol = UiWriteProtocol(store)
    submitter = RecordingOrganizationSubmitter()
    server = FastMCP("ui-organization-wrong-tool-test")
    register_ui_organization_write_tools(server, protocol, submitter=submitter)

    foreign = protocol.preview(
        execute_tool_name="ui_clients_create_execute",
        organization_id="org-test",
        target="clients",
        canonical_request={"name": "MCP-TEST"},
        expected_effect_state={"action": "create", "resource": "contact"},
        summary="Create one Billy customer in the interface.",
    )
    assert isinstance(foreign, UiWritePreviewResult)
    mismatch = call_tool(
        server,
        "ui_organizations_update_execute",
        {"confirmation_ticket": foreign.confirmation_ticket},
    )

    assert mismatch["code"] == StableErrorCode.CONFIRMATION_MISMATCH
    assert submitter.calls == []


def test_execute_rejects_expired_ticket_without_submit() -> None:
    clock = Clock()
    server, _, submitter = make_server(clock=clock)
    assert submitter is not None
    preview = call_tool(
        server,
        "ui_organizations_update_preview",
        {"phone": "+4533333333", "organization_id": "org-test"},
    )
    clock.now = clock.now + MAX_TICKET_TTL + timedelta(seconds=1)

    expired = call_tool(
        server,
        "ui_organizations_update_execute",
        {"confirmation_ticket": preview["confirmation_ticket"]},
    )

    assert expired["code"] == StableErrorCode.CONFIRMATION_EXPIRED
    assert submitter.calls == []


def test_missing_submitter_does_not_consume_ticket() -> None:
    clock = Clock()
    store = ConfirmationStore(clock=clock)
    protocol = UiWriteProtocol(store)
    bare = FastMCP("ui-organization-no-submitter-test")
    register_ui_organization_write_tools(bare, protocol, submitter=None)
    preview = call_tool(
        bare,
        "ui_organizations_update_preview",
        {"phone": "+4544444444", "organization_id": "org-test"},
    )
    ticket = preview["confirmation_ticket"]

    missing = call_tool(
        bare,
        "ui_organizations_update_execute",
        {"confirmation_ticket": ticket},
    )
    assert missing["code"] == StableErrorCode.VALIDATION_ERROR
    assert "submit" in str(missing["message"]).lower()

    armed = FastMCP("ui-organization-late-submitter-test")
    submitter = RecordingOrganizationSubmitter()
    register_ui_organization_write_tools(armed, protocol, submitter=submitter)
    first = call_tool(
        armed,
        "ui_organizations_update_execute",
        {"confirmation_ticket": ticket},
    )
    assert first["submitted"] is True
    assert len(submitter.calls) == 1
