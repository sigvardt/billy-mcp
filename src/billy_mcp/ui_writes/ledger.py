"""Ticketed UI ledger write tools. Preview binds a ticket. Execute does not submit."""

from __future__ import annotations

from typing import Final, Literal, assert_never

from fastmcp import FastMCP
from pydantic import BaseModel, ConfigDict, Field, JsonValue

from billy_mcp.models import ToolError
from billy_mcp.ui_writes.protocol import (
    UiWriteExecuteInput,
    UiWritePrepared,
    UiWritePreviewResult,
    UiWriteProtocol,
)

LEDGER_SUBMIT_BLOCKER: Final[str] = (
    "UI ledger execute consumed the ticket and did not submit. "
    "register_ui_ledger_write_tools has no browser or HTTP submitter. "
    "Parent hold 7696B03D: contacts has the live slot. "
    "Daybook transaction and Posteringer create stay unsubmitted until a delete path is proven."
)


class DaybookCreatePreviewInput(BaseModel):
    """Flat input for previewing one tagged Billy daybook create."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    name: str = Field(min_length=1)


class DaybookDeletePreviewInput(BaseModel):
    """Flat input for previewing deletion of one Billy daybook."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    id: str = Field(min_length=1)


class DaybookTransactionCreatePreviewInput(BaseModel):
    """Flat input for previewing one daybook line create."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    daybook_id: str = Field(min_length=1)
    text: str = Field(min_length=1)


class TransactionCreatePreviewInput(BaseModel):
    """Flat input for previewing one Posteringer create."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    text: str = Field(min_length=1)


class UiLedgerExecuteResult(BaseModel):
    """Ticket consume result. Mutation is refused until a submitter exists."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    submitted: Literal[False] = False
    summary: str = Field(min_length=1)
    canonical_request: dict[str, JsonValue]
    expected_effect_state: dict[str, JsonValue]
    blocker: str = Field(min_length=1)


def register_ui_ledger_write_tools(server: FastMCP, protocol: UiWriteProtocol) -> None:
    """Register the eight UI ledger preview and execute tools."""

    def ui_daybooks_create_preview(name: str = Field(min_length=1)) -> UiWritePreviewResult:
        """Preview one tagged daybook create. Does not submit."""

        parsed = DaybookCreatePreviewInput(name=name)
        return protocol.preview(
            execute_tool_name="ui_daybooks_create_execute",
            organization_id=None,
            target="daybooks",
            canonical_request={"name": parsed.name},
            expected_effect_state={"action": "create", "resource": "daybook"},
            summary="Create one Billy daybook in the interface.",
        )

    def ui_daybooks_delete_preview(id: str = Field(min_length=1)) -> UiWritePreviewResult:
        """Preview deletion of one daybook. Does not submit."""

        parsed = DaybookDeletePreviewInput(id=id)
        return protocol.preview(
            execute_tool_name="ui_daybooks_delete_execute",
            organization_id=None,
            target="daybooks",
            canonical_request={"id": parsed.id},
            expected_effect_state={"action": "delete", "resource": "daybook", "id": parsed.id},
            summary="Delete one Billy daybook in the interface.",
        )

    def ui_daybook_transactions_create_preview(
        daybook_id: str = Field(min_length=1),
        text: str = Field(min_length=1),
    ) -> UiWritePreviewResult:
        """Preview one daybook line create. Does not submit."""

        parsed = DaybookTransactionCreatePreviewInput(daybook_id=daybook_id, text=text)
        return protocol.preview(
            execute_tool_name="ui_daybook_transactions_create_execute",
            organization_id=None,
            target="daybookTransactions",
            canonical_request={"daybook_id": parsed.daybook_id, "text": parsed.text},
            expected_effect_state={"action": "create", "resource": "daybookTransaction"},
            summary="Create one Billy daybook transaction in the interface.",
        )

    def ui_transactions_create_preview(text: str = Field(min_length=1)) -> UiWritePreviewResult:
        """Preview one Posteringer create. Does not submit."""

        parsed = TransactionCreatePreviewInput(text=text)
        return protocol.preview(
            execute_tool_name="ui_transactions_create_execute",
            organization_id=None,
            target="transactions",
            canonical_request={"text": parsed.text},
            expected_effect_state={"action": "create", "resource": "transaction"},
            summary="Create one Billy posting in the interface.",
        )

    def ui_daybooks_create_execute(
        confirmation_ticket: str = Field(min_length=1),
    ) -> UiLedgerExecuteResult | ToolError:
        """Consume a daybook-create ticket. Does not submit."""

        return _consume(protocol, confirmation_ticket, "ui_daybooks_create_execute")

    def ui_daybooks_delete_execute(
        confirmation_ticket: str = Field(min_length=1),
    ) -> UiLedgerExecuteResult | ToolError:
        """Consume a daybook-delete ticket. Does not submit."""

        return _consume(protocol, confirmation_ticket, "ui_daybooks_delete_execute")

    def ui_daybook_transactions_create_execute(
        confirmation_ticket: str = Field(min_length=1),
    ) -> UiLedgerExecuteResult | ToolError:
        """Consume a daybook-transaction-create ticket. Does not submit."""

        return _consume(protocol, confirmation_ticket, "ui_daybook_transactions_create_execute")

    def ui_transactions_create_execute(
        confirmation_ticket: str = Field(min_length=1),
    ) -> UiLedgerExecuteResult | ToolError:
        """Consume a Posteringer-create ticket. Does not submit."""

        return _consume(protocol, confirmation_ticket, "ui_transactions_create_execute")

    server.tool(
        name="ui_daybooks_create_preview",
        description="Preview creation of one Billy daybook without submitting.",
    )(ui_daybooks_create_preview)
    server.tool(
        name="ui_daybooks_create_execute",
        description="Consume a previewed Billy daybook creation ticket without submitting.",
    )(ui_daybooks_create_execute)
    server.tool(
        name="ui_daybooks_delete_preview",
        description="Preview deletion of one Billy daybook without submitting.",
    )(ui_daybooks_delete_preview)
    server.tool(
        name="ui_daybooks_delete_execute",
        description="Consume a previewed Billy daybook deletion ticket without submitting.",
    )(ui_daybooks_delete_execute)
    server.tool(
        name="ui_daybook_transactions_create_preview",
        description="Preview creation of one Billy daybook transaction without submitting.",
    )(ui_daybook_transactions_create_preview)
    server.tool(
        name="ui_daybook_transactions_create_execute",
        description="Consume a previewed daybook-transaction ticket without submitting.",
    )(ui_daybook_transactions_create_execute)
    server.tool(
        name="ui_transactions_create_preview",
        description="Preview creation of one Billy posting without submitting.",
    )(ui_transactions_create_preview)
    server.tool(
        name="ui_transactions_create_execute",
        description="Consume a previewed posting ticket without submitting.",
    )(ui_transactions_create_execute)


def _consume(
    protocol: UiWriteProtocol,
    confirmation_ticket: str,
    execute_tool_name: str,
) -> UiLedgerExecuteResult | ToolError:
    """Consume the bound ticket and refuse Billy mutation."""

    prepared = protocol.consume(
        UiWriteExecuteInput(confirmation_ticket=confirmation_ticket),
        execute_tool_name=execute_tool_name,
    )
    match prepared:
        case ToolError():
            return prepared
        case UiWritePrepared():
            return UiLedgerExecuteResult(
                submitted=False,
                summary=prepared.summary,
                canonical_request=prepared.canonical_request,
                expected_effect_state=prepared.expected_effect_state,
                blocker=LEDGER_SUBMIT_BLOCKER,
            )
        case unreachable:
            assert_never(unreachable)
