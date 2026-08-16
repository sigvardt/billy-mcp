"""Ticketed UI bill write tools. Draft-only. Never pays a bill."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Final, Protocol, assert_never

from fastmcp import FastMCP
from pydantic import BaseModel, ConfigDict, Field, JsonValue

from billy_mcp.models import StableErrorCode, ToolError
from billy_mcp.ui_writes.protocol import (
    UiWriteExecuteInput,
    UiWritePrepared,
    UiWritePreviewResult,
    UiWriteProtocol,
)

LIVE_SLOT_BLOCKER_MESSAGE: Final[str] = (
    "Live UI bill submit waits for root radio go-ahead (9F2EC46E). "
    "Contacts family holds the live slot."
)


class BillUiWriteAction(StrEnum):
    """The three draft-only interface actions this family may preview."""

    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"


class BillUiCreatePreviewInput(BaseModel):
    """Input for previewing a tagged draft bill create."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    unique_tag: str = Field(min_length=1)


class BillUiUpdatePreviewInput(BaseModel):
    """Input for previewing a tagged draft bill update."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    id: str = Field(min_length=1)
    unique_tag: str = Field(min_length=1)


class BillUiDeletePreviewInput(BaseModel):
    """Input for previewing a tagged draft bill delete."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    id: str = Field(min_length=1)
    unique_tag: str = Field(min_length=1)


class UiBillWriteExecuteResult(BaseModel):
    """Result of a consumed UI bill execute after the submitter runs."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    submitted: bool
    action: BillUiWriteAction
    unique_tag: str = Field(min_length=1)


class BillUiSubmitter(Protocol):
    """Performs the previewed interface action, or refuses it."""

    def submit(self, prepared: UiWritePrepared) -> UiBillWriteExecuteResult | ToolError:
        """Submit the bound draft bill action without calling the Billy HTTP API."""


class LiveSlotBlockedSubmitter:
    """Default submitter: consume is allowed, live mutation is not."""

    def submit(self, prepared: UiWritePrepared) -> ToolError:
        del prepared
        return ToolError(
            code=StableErrorCode.VALIDATION_ERROR,
            message=LIVE_SLOT_BLOCKER_MESSAGE,
        )


@dataclass(slots=True)
class RecordingBillUiSubmitter:
    """Offline recorder. Mutation is the purpose: it stores each submit call."""

    submissions: list[UiWritePrepared] = field(default_factory=list)

    def submit(self, prepared: UiWritePrepared) -> UiBillWriteExecuteResult:
        self.submissions.append(prepared)
        return UiBillWriteExecuteResult(
            submitted=True,
            action=_action_from_prepared(prepared),
            unique_tag=_tag_from_prepared(prepared),
        )


def register_ui_bill_write_tools(
    server: FastMCP,
    protocol: UiWriteProtocol,
    submitter: BillUiSubmitter | None = None,
) -> None:
    """Register the six UI bill preview and execute tools."""

    actor = submitter if submitter is not None else LiveSlotBlockedSubmitter()

    def ui_bills_create_preview(unique_tag: str = Field(min_length=1)) -> UiWritePreviewResult:
        """Preview a tagged draft bill create. Writes nothing."""

        parsed = BillUiCreatePreviewInput(unique_tag=unique_tag)
        return _preview(protocol, action=BillUiWriteAction.CREATE, unique_tag=parsed.unique_tag)

    def ui_bills_create_execute(
        confirmation_ticket: str = Field(min_length=1),
    ) -> UiBillWriteExecuteResult | ToolError:
        """Execute the exact previewed draft bill create."""

        return _execute(
            protocol,
            actor,
            execute_tool_name="ui_bills_create_execute",
            confirmation_ticket=confirmation_ticket,
        )

    def ui_bills_update_preview(
        unique_tag: str = Field(min_length=1),
        id: str = Field(min_length=1),
    ) -> UiWritePreviewResult:
        """Preview a tagged draft bill update. Writes nothing."""

        parsed = BillUiUpdatePreviewInput(id=id, unique_tag=unique_tag)
        return _preview(
            protocol,
            action=BillUiWriteAction.UPDATE,
            unique_tag=parsed.unique_tag,
            bill_id=parsed.id,
        )

    def ui_bills_update_execute(
        confirmation_ticket: str = Field(min_length=1),
    ) -> UiBillWriteExecuteResult | ToolError:
        """Execute the exact previewed draft bill update."""

        return _execute(
            protocol,
            actor,
            execute_tool_name="ui_bills_update_execute",
            confirmation_ticket=confirmation_ticket,
        )

    def ui_bills_delete_preview(
        unique_tag: str = Field(min_length=1),
        id: str = Field(min_length=1),
    ) -> UiWritePreviewResult:
        """Preview a tagged draft bill delete. Writes nothing."""

        parsed = BillUiDeletePreviewInput(id=id, unique_tag=unique_tag)
        return _preview(
            protocol,
            action=BillUiWriteAction.DELETE,
            unique_tag=parsed.unique_tag,
            bill_id=parsed.id,
        )

    def ui_bills_delete_execute(
        confirmation_ticket: str = Field(min_length=1),
    ) -> UiBillWriteExecuteResult | ToolError:
        """Execute the exact previewed draft bill delete."""

        return _execute(
            protocol,
            actor,
            execute_tool_name="ui_bills_delete_execute",
            confirmation_ticket=confirmation_ticket,
        )

    server.tool(
        name="ui_bills_create_preview",
        description="Preview a tagged draft Billy bill create without submitting.",
    )(ui_bills_create_preview)
    server.tool(
        name="ui_bills_create_execute",
        description="Execute a previewed draft Billy bill create with its ticket.",
    )(ui_bills_create_execute)
    server.tool(
        name="ui_bills_update_preview",
        description="Preview a tagged draft Billy bill update without submitting.",
    )(ui_bills_update_preview)
    server.tool(
        name="ui_bills_update_execute",
        description="Execute a previewed draft Billy bill update with its ticket.",
    )(ui_bills_update_execute)
    server.tool(
        name="ui_bills_delete_preview",
        description="Preview a tagged draft Billy bill delete without submitting.",
    )(ui_bills_delete_preview)
    server.tool(
        name="ui_bills_delete_execute",
        description="Execute a previewed draft Billy bill delete with its ticket.",
    )(ui_bills_delete_execute)


def _preview(
    protocol: UiWriteProtocol,
    *,
    action: BillUiWriteAction,
    unique_tag: str,
    bill_id: str | None = None,
) -> UiWritePreviewResult:
    canonical: dict[str, JsonValue] = {
        "action": action.value,
        "resource": "bill",
        "unique_tag": unique_tag,
        "draft_only": True,
    }
    expected: dict[str, JsonValue] = {
        "action": action.value,
        "resource": "bill",
        "draft_only": True,
    }
    if bill_id is not None:
        canonical["id"] = bill_id
        expected["id"] = bill_id
    match action:
        case BillUiWriteAction.CREATE:
            summary = "Create one draft Billy bill in the interface."
        case BillUiWriteAction.UPDATE:
            summary = "Update one draft Billy bill in the interface."
        case BillUiWriteAction.DELETE:
            summary = "Delete one draft Billy bill in the interface."
        case unreachable:
            assert_never(unreachable)
    return protocol.preview(
        execute_tool_name=f"ui_bills_{action.value}_execute",
        organization_id=None,
        target="bills",
        canonical_request=canonical,
        expected_effect_state=expected,
        summary=summary,
    )


def _execute(
    protocol: UiWriteProtocol,
    submitter: BillUiSubmitter,
    *,
    execute_tool_name: str,
    confirmation_ticket: str,
) -> UiBillWriteExecuteResult | ToolError:
    prepared = protocol.consume(
        UiWriteExecuteInput(confirmation_ticket=confirmation_ticket),
        execute_tool_name=execute_tool_name,
    )
    match prepared:
        case ToolError():
            return prepared
        case UiWritePrepared():
            return submitter.submit(prepared)
        case unreachable:
            assert_never(unreachable)


def _action_from_prepared(prepared: UiWritePrepared) -> BillUiWriteAction:
    return BillUiWriteAction(str(prepared.expected_effect_state["action"]))


def _tag_from_prepared(prepared: UiWritePrepared) -> str:
    return str(prepared.canonical_request["unique_tag"])
