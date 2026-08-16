"""Ticketed UI organization update tools.

Preview binds a reversible company-phone change and issues a ticket. Execute
accepts only that ticket. This lane never calls the Billy HTTP API.
"""

from __future__ import annotations

import inspect
from collections.abc import Awaitable
from dataclasses import dataclass, field
from typing import Final, Protocol

from fastmcp import FastMCP
from pydantic import BaseModel, ConfigDict, Field, JsonValue, field_validator

from billy_mcp.browser import BrowserRuntime
from billy_mcp.models import StableErrorCode, ToolError
from billy_mcp.ui_writes.page_flow import FamilyWrite, perform_family_write
from billy_mcp.ui_writes.protocol import (
    UiWriteExecuteInput,
    UiWritePrepared,
    UiWritePreviewResult,
    UiWriteProtocol,
)

PREVIEW_TOOL_NAME: Final = "ui_organizations_update_preview"
EXECUTE_TOOL_NAME: Final = "ui_organizations_update_execute"
ALLOWED_COMPANY_FIELDS: Final[frozenset[str]] = frozenset({"phone"})
FORBIDDEN_COMPANY_FIELDS: Final[frozenset[str]] = frozenset(
    {
        "access_token",
        "access_tokens",
        "name",
        "owner",
        "owners",
        "payment",
        "payments",
        "registrationNo",
        "subscription",
        "user",
        "users",
        "vat",
    }
)


class OrganizationUpdatePreviewInput(BaseModel):
    """Allowlisted company-phone preview. Extra fields are forbidden."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    phone: str = Field(min_length=1)
    organization_id: str = Field(min_length=1)

    @field_validator("phone")
    @classmethod
    def phone_is_non_blank(cls, value: str) -> str:
        stripped = value.strip()
        if not stripped:
            raise ValueError("phone must not be blank")
        return stripped


class UiOrganizationUpdateResult(BaseModel):
    """Result of consuming a preview ticket and invoking the submit hook."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    submitted: bool
    canonical_request: dict[str, JsonValue]
    expected_effect_state: dict[str, JsonValue]


class OrganizationUiSubmitter(Protocol):
    """Applies a consumed organization-update ticket to the Billy interface."""

    def submit(
        self, prepared: UiWritePrepared
    ) -> (
        UiOrganizationUpdateResult | ToolError | Awaitable[UiOrganizationUpdateResult | ToolError]
    ): ...


class BrowserOrganizationSubmitter:
    """Default production submitter. Company phone only. Enters BrowserRuntime first."""

    def __init__(self, runtime: BrowserRuntime) -> None:
        self._runtime = runtime

    async def submit(self, prepared: UiWritePrepared) -> UiOrganizationUpdateResult | ToolError:
        phone = str(prepared.canonical_request.get("phone") or "")
        failed = await perform_family_write(
            self._runtime,
            FamilyWrite(
                write_path="settings",
                fills=(("phone", phone),),
                clicks=("Gem ændringer",),
                readback_path="settings",
                readback_text=phone,
            ),
        )
        if failed is not None:
            return failed
        return UiOrganizationUpdateResult(
            submitted=True,
            canonical_request=prepared.canonical_request,
            expected_effect_state=prepared.expected_effect_state,
        )


@dataclass(slots=True)
class RecordingOrganizationSubmitter:
    """In-memory submitter for offline tests. Mutable so tests can record calls."""

    calls: list[UiWritePrepared] = field(default_factory=list[UiWritePrepared])

    def submit(self, prepared: UiWritePrepared) -> UiOrganizationUpdateResult:
        """Record the bound request and report a local submit."""

        self.calls.append(prepared)
        return UiOrganizationUpdateResult(
            submitted=True,
            canonical_request=prepared.canonical_request,
            expected_effect_state=prepared.expected_effect_state,
        )


def register_ui_organization_write_tools(
    server: FastMCP,
    protocol: UiWriteProtocol,
    *,
    submitter: OrganizationUiSubmitter | None = None,
    runtime: BrowserRuntime | None = None,
) -> None:
    """Register UI organization update preview and execute tools."""

    if submitter is not None:
        actor: OrganizationUiSubmitter | None = submitter
    elif runtime is not None:
        actor = BrowserOrganizationSubmitter(runtime)
    else:
        actor = None

    def ui_organizations_update_preview(
        phone: str = Field(min_length=1),
        organization_id: str = Field(min_length=1),
    ) -> UiWritePreviewResult | ToolError:
        """Preview a company-phone update. Issues a ticket and writes nothing."""

        parsed = OrganizationUpdatePreviewInput(phone=phone, organization_id=organization_id)
        request: dict[str, JsonValue] = {"phone": parsed.phone}
        effect: dict[str, JsonValue] = {
            "action": "update",
            "resource": "organization",
            "surface": "settings_company",
            "field": "phone",
        }
        return protocol.preview(
            execute_tool_name=EXECUTE_TOOL_NAME,
            organization_id=parsed.organization_id,
            target="settings_company",
            canonical_request=request,
            expected_effect_state=effect,
            summary=(
                "Update the company phone on Billy Indstillinger. "
                "Does not touch users, access tokens, or subscription."
            ),
        )

    async def ui_organizations_update_execute(
        confirmation_ticket: str = Field(min_length=1),
    ) -> UiOrganizationUpdateResult | ToolError:
        """Execute the previewed company-phone update with its ticket only."""

        parsed = UiWriteExecuteInput(confirmation_ticket=confirmation_ticket)
        if actor is None:
            return ToolError(
                code=StableErrorCode.VALIDATION_ERROR,
                message="Interface submit hook is not attached.",
            )
        prepared = protocol.consume(parsed, execute_tool_name=EXECUTE_TOOL_NAME)
        if isinstance(prepared, ToolError):
            return prepared
        submitted = actor.submit(prepared)
        if inspect.isawaitable(submitted):
            return await submitted
        return submitted

    server.tool(
        name=PREVIEW_TOOL_NAME,
        description=(
            "Preview a reversible Billy company-phone update without submitting. "
            "Users, access tokens, and subscription are rejected."
        ),
    )(ui_organizations_update_preview)
    server.tool(
        name=EXECUTE_TOOL_NAME,
        description="Execute a previewed Billy company-phone update with its ticket.",
    )(ui_organizations_update_execute)
