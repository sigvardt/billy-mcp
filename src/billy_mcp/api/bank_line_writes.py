"""Ticketed FastMCP tools for singular Billy bank-line writes."""

from __future__ import annotations

from collections.abc import Callable

from fastmcp import FastMCP
from pydantic import BaseModel, ConfigDict, Field, JsonValue, model_validator

from billy_mcp.api.write_protocol import (
    WriteExecuteInput,
    WriteExecutionResult,
    WriteMethod,
    WriteOperationSpec,
    WritePreviewResult,
    WriteProtocolService,
)
from billy_mcp.client import BillyHttpClient
from billy_mcp.models import ToolError


class _BankLineWritePreviewInput(BaseModel):
    """Forbid undeclared outer fields while preserving opaque resource payloads."""

    model_config = ConfigDict(extra="forbid")


class BankLineMatchCreatePreviewInput(_BankLineWritePreviewInput):
    """Input for previewing creation of one Billy bank-line match."""

    bankLineMatch: dict[str, JsonValue]


class BankLineMatchUpdatePreviewInput(BankLineMatchCreatePreviewInput):
    """Input for previewing a partial update to one Billy bank-line match."""

    id: str = Field(min_length=1)

    @model_validator(mode="after")
    def payload_id_matches_route_id(self) -> BankLineMatchUpdatePreviewInput:
        """Reject an explicit payload id that disagrees with the route id."""

        if "id" in self.bankLineMatch and self.bankLineMatch["id"] != self.id:
            raise ValueError("bankLineMatch.id must match id")
        return self


class BankLineMatchDeletePreviewInput(_BankLineWritePreviewInput):
    """Input for previewing deletion of one Billy bank-line match."""

    id: str = Field(min_length=1)


class BankLineCreatePreviewInput(_BankLineWritePreviewInput):
    """Input for previewing creation of one Billy bank line."""

    bankLine: dict[str, JsonValue]


class BankLineUpdatePreviewInput(BankLineCreatePreviewInput):
    """Input for previewing a partial update to one Billy bank line."""

    id: str = Field(min_length=1)

    @model_validator(mode="after")
    def payload_id_matches_route_id(self) -> BankLineUpdatePreviewInput:
        """Reject an explicit payload id that disagrees with the route id."""

        if "id" in self.bankLine and self.bankLine["id"] != self.id:
            raise ValueError("bankLine.id must match id")
        return self


class BankLineDeletePreviewInput(_BankLineWritePreviewInput):
    """Input for previewing deletion of one Billy bank line."""

    id: str = Field(min_length=1)


class BankLineSubjectAssociationCreatePreviewInput(_BankLineWritePreviewInput):
    """Input for previewing creation of one bank-line subject association."""

    bankLineSubjectAssociation: dict[str, JsonValue]


class BankLineSubjectAssociationUpdatePreviewInput(BankLineSubjectAssociationCreatePreviewInput):
    """Input for previewing a partial update to one bank-line subject association."""

    id: str = Field(min_length=1)

    @model_validator(mode="after")
    def payload_id_matches_route_id(self) -> BankLineSubjectAssociationUpdatePreviewInput:
        """Reject an explicit payload id that disagrees with the route id."""

        if (
            "id" in self.bankLineSubjectAssociation
            and self.bankLineSubjectAssociation["id"] != self.id
        ):
            raise ValueError("bankLineSubjectAssociation.id must match id")
        return self


class BankLineSubjectAssociationDeletePreviewInput(_BankLineWritePreviewInput):
    """Input for previewing deletion of one bank-line subject association."""

    id: str = Field(min_length=1)


def register_bank_line_write_tools(
    server: FastMCP,
    client: BillyHttpClient,
    write_protocol: WriteProtocolService,
) -> None:
    """Register exactly the eighteen frozen bank-line write tools."""

    del client

    def api_bank_line_matches_create_preview(
        bankLineMatch: dict[str, JsonValue],
    ) -> WritePreviewResult:
        """Preview creation of one Billy bank-line match without a mutation."""

        input = BankLineMatchCreatePreviewInput(bankLineMatch=bankLineMatch)
        return write_protocol.preview(
            _bank_line_match_specification(
                execute_tool_name="api_bank_line_matches_create_execute",
                method=WriteMethod.POST,
                payload=input.bankLineMatch,
                resource_id=None,
            )
        )

    def api_bank_line_matches_create_execute(
        confirmation_ticket: str = Field(min_length=1),
    ) -> WriteExecutionResult | ToolError:
        """Execute the exact bank-line match creation in a confirmation ticket."""

        return write_protocol.execute(
            WriteExecuteInput(confirmation_ticket=confirmation_ticket),
            execute_tool_name="api_bank_line_matches_create_execute",
        )

    def api_bank_line_matches_update_preview(
        bankLineMatch: dict[str, JsonValue],
        id: str = Field(min_length=1),
    ) -> WritePreviewResult:
        """Preview an update to one Billy bank-line match without a mutation."""

        input = BankLineMatchUpdatePreviewInput(id=id, bankLineMatch=bankLineMatch)
        return write_protocol.preview(
            _bank_line_match_specification(
                execute_tool_name="api_bank_line_matches_update_execute",
                method=WriteMethod.PUT,
                payload=input.bankLineMatch,
                resource_id=input.id,
            )
        )

    def api_bank_line_matches_update_execute(
        confirmation_ticket: str = Field(min_length=1),
    ) -> WriteExecutionResult | ToolError:
        """Execute the exact bank-line match update in a confirmation ticket."""

        return write_protocol.execute(
            WriteExecuteInput(confirmation_ticket=confirmation_ticket),
            execute_tool_name="api_bank_line_matches_update_execute",
        )

    def api_bank_line_matches_delete_preview(
        id: str = Field(min_length=1),
    ) -> WritePreviewResult:
        """Preview deletion of one Billy bank-line match without a mutation."""

        input = BankLineMatchDeletePreviewInput(id=id)
        return write_protocol.preview(
            _bank_line_match_specification(
                execute_tool_name="api_bank_line_matches_delete_execute",
                method=WriteMethod.DELETE,
                payload=None,
                resource_id=input.id,
            )
        )

    def api_bank_line_matches_delete_execute(
        confirmation_ticket: str = Field(min_length=1),
    ) -> WriteExecutionResult | ToolError:
        """Execute the exact bank-line match deletion in a confirmation ticket."""

        return write_protocol.execute(
            WriteExecuteInput(confirmation_ticket=confirmation_ticket),
            execute_tool_name="api_bank_line_matches_delete_execute",
        )

    def api_bank_lines_create_preview(
        bankLine: dict[str, JsonValue],
    ) -> WritePreviewResult:
        """Preview creation of one Billy bank line without a mutation."""

        input = BankLineCreatePreviewInput(bankLine=bankLine)
        return write_protocol.preview(
            _bank_line_specification(
                execute_tool_name="api_bank_lines_create_execute",
                method=WriteMethod.POST,
                payload=input.bankLine,
                resource_id=None,
            )
        )

    def api_bank_lines_create_execute(
        confirmation_ticket: str = Field(min_length=1),
    ) -> WriteExecutionResult | ToolError:
        """Execute the exact bank-line creation in a confirmation ticket."""

        return write_protocol.execute(
            WriteExecuteInput(confirmation_ticket=confirmation_ticket),
            execute_tool_name="api_bank_lines_create_execute",
        )

    def api_bank_lines_update_preview(
        bankLine: dict[str, JsonValue],
        id: str = Field(min_length=1),
    ) -> WritePreviewResult:
        """Preview an update to one Billy bank line without a mutation."""

        input = BankLineUpdatePreviewInput(id=id, bankLine=bankLine)
        return write_protocol.preview(
            _bank_line_specification(
                execute_tool_name="api_bank_lines_update_execute",
                method=WriteMethod.PUT,
                payload=input.bankLine,
                resource_id=input.id,
            )
        )

    def api_bank_lines_update_execute(
        confirmation_ticket: str = Field(min_length=1),
    ) -> WriteExecutionResult | ToolError:
        """Execute the exact bank-line update in a confirmation ticket."""

        return write_protocol.execute(
            WriteExecuteInput(confirmation_ticket=confirmation_ticket),
            execute_tool_name="api_bank_lines_update_execute",
        )

    def api_bank_lines_delete_preview(
        id: str = Field(min_length=1),
    ) -> WritePreviewResult:
        """Preview deletion of one Billy bank line without a mutation."""

        input = BankLineDeletePreviewInput(id=id)
        return write_protocol.preview(
            _bank_line_specification(
                execute_tool_name="api_bank_lines_delete_execute",
                method=WriteMethod.DELETE,
                payload=None,
                resource_id=input.id,
            )
        )

    def api_bank_lines_delete_execute(
        confirmation_ticket: str = Field(min_length=1),
    ) -> WriteExecutionResult | ToolError:
        """Execute the exact bank-line deletion in a confirmation ticket."""

        return write_protocol.execute(
            WriteExecuteInput(confirmation_ticket=confirmation_ticket),
            execute_tool_name="api_bank_lines_delete_execute",
        )

    def api_bank_line_subject_associations_create_preview(
        bankLineSubjectAssociation: dict[str, JsonValue],
    ) -> WritePreviewResult:
        """Preview creation of one bank-line subject association without a mutation."""

        input = BankLineSubjectAssociationCreatePreviewInput(
            bankLineSubjectAssociation=bankLineSubjectAssociation
        )
        return write_protocol.preview(
            _bank_line_subject_association_specification(
                execute_tool_name="api_bank_line_subject_associations_create_execute",
                method=WriteMethod.POST,
                payload=input.bankLineSubjectAssociation,
                resource_id=None,
            )
        )

    def api_bank_line_subject_associations_create_execute(
        confirmation_ticket: str = Field(min_length=1),
    ) -> WriteExecutionResult | ToolError:
        """Execute the exact association creation in a confirmation ticket."""

        return write_protocol.execute(
            WriteExecuteInput(confirmation_ticket=confirmation_ticket),
            execute_tool_name="api_bank_line_subject_associations_create_execute",
        )

    def api_bank_line_subject_associations_update_preview(
        bankLineSubjectAssociation: dict[str, JsonValue],
        id: str = Field(min_length=1),
    ) -> WritePreviewResult:
        """Preview an association update without a mutation."""

        input = BankLineSubjectAssociationUpdatePreviewInput(
            id=id,
            bankLineSubjectAssociation=bankLineSubjectAssociation,
        )
        return write_protocol.preview(
            _bank_line_subject_association_specification(
                execute_tool_name="api_bank_line_subject_associations_update_execute",
                method=WriteMethod.PUT,
                payload=input.bankLineSubjectAssociation,
                resource_id=input.id,
            )
        )

    def api_bank_line_subject_associations_update_execute(
        confirmation_ticket: str = Field(min_length=1),
    ) -> WriteExecutionResult | ToolError:
        """Execute the exact association update in a confirmation ticket."""

        return write_protocol.execute(
            WriteExecuteInput(confirmation_ticket=confirmation_ticket),
            execute_tool_name="api_bank_line_subject_associations_update_execute",
        )

    def api_bank_line_subject_associations_delete_preview(
        id: str = Field(min_length=1),
    ) -> WritePreviewResult:
        """Preview deletion of one bank-line subject association without a mutation."""

        input = BankLineSubjectAssociationDeletePreviewInput(id=id)
        return write_protocol.preview(
            _bank_line_subject_association_specification(
                execute_tool_name="api_bank_line_subject_associations_delete_execute",
                method=WriteMethod.DELETE,
                payload=None,
                resource_id=input.id,
            )
        )

    def api_bank_line_subject_associations_delete_execute(
        confirmation_ticket: str = Field(min_length=1),
    ) -> WriteExecutionResult | ToolError:
        """Execute the exact association deletion in a confirmation ticket."""

        return write_protocol.execute(
            WriteExecuteInput(confirmation_ticket=confirmation_ticket),
            execute_tool_name="api_bank_line_subject_associations_delete_execute",
        )

    _register_tools(
        server,
        (
            (
                "api_bank_line_matches_create_preview",
                api_bank_line_matches_create_preview,
                "Preview creation of one Billy bank-line match without a mutation.",
            ),
            (
                "api_bank_line_matches_create_execute",
                api_bank_line_matches_create_execute,
                "Execute a previewed Billy bank-line match creation with its ticket.",
            ),
            (
                "api_bank_line_matches_update_preview",
                api_bank_line_matches_update_preview,
                "Preview an update to one Billy bank-line match without a mutation.",
            ),
            (
                "api_bank_line_matches_update_execute",
                api_bank_line_matches_update_execute,
                "Execute a previewed Billy bank-line match update with its ticket.",
            ),
            (
                "api_bank_line_matches_delete_preview",
                api_bank_line_matches_delete_preview,
                "Preview deletion of one Billy bank-line match without a mutation.",
            ),
            (
                "api_bank_line_matches_delete_execute",
                api_bank_line_matches_delete_execute,
                "Execute a previewed Billy bank-line match deletion with its ticket.",
            ),
            (
                "api_bank_lines_create_preview",
                api_bank_lines_create_preview,
                "Preview creation of one Billy bank line without a mutation.",
            ),
            (
                "api_bank_lines_create_execute",
                api_bank_lines_create_execute,
                "Execute a previewed Billy bank-line creation with its ticket.",
            ),
            (
                "api_bank_lines_update_preview",
                api_bank_lines_update_preview,
                "Preview an update to one Billy bank line without a mutation.",
            ),
            (
                "api_bank_lines_update_execute",
                api_bank_lines_update_execute,
                "Execute a previewed Billy bank-line update with its ticket.",
            ),
            (
                "api_bank_lines_delete_preview",
                api_bank_lines_delete_preview,
                "Preview deletion of one Billy bank line without a mutation.",
            ),
            (
                "api_bank_lines_delete_execute",
                api_bank_lines_delete_execute,
                "Execute a previewed Billy bank-line deletion with its ticket.",
            ),
            (
                "api_bank_line_subject_associations_create_preview",
                api_bank_line_subject_associations_create_preview,
                "Preview creation of one bank-line subject association without a mutation.",
            ),
            (
                "api_bank_line_subject_associations_create_execute",
                api_bank_line_subject_associations_create_execute,
                "Execute a previewed bank-line subject-association creation with its ticket.",
            ),
            (
                "api_bank_line_subject_associations_update_preview",
                api_bank_line_subject_associations_update_preview,
                "Preview an update to one bank-line subject association without a mutation.",
            ),
            (
                "api_bank_line_subject_associations_update_execute",
                api_bank_line_subject_associations_update_execute,
                "Execute a previewed bank-line subject-association update with its ticket.",
            ),
            (
                "api_bank_line_subject_associations_delete_preview",
                api_bank_line_subject_associations_delete_preview,
                "Preview deletion of one bank-line subject association without a mutation.",
            ),
            (
                "api_bank_line_subject_associations_delete_execute",
                api_bank_line_subject_associations_delete_execute,
                "Execute a previewed bank-line subject-association deletion with its ticket.",
            ),
        ),
    )


def _register_tools(
    server: FastMCP,
    tools: tuple[tuple[str, Callable[..., object], str], ...],
) -> None:
    """Register fixed public names without exposing a dynamic request shape."""

    for name, handler, description in tools:
        server.tool(name=name, description=description)(handler)


def _bank_line_match_specification(
    *,
    execute_tool_name: str,
    method: WriteMethod,
    payload: dict[str, JsonValue] | None,
    resource_id: str | None,
) -> WriteOperationSpec:
    """Build the fixed shape for one bank-line match CUD operation."""

    return _bank_line_write_specification(
        execute_tool_name=execute_tool_name,
        method=method,
        collection_path="/bankLineMatches",
        singular_root="bankLineMatch",
        plural_root="bankLineMatches",
        additional_plural_roots=("bankLines", "bankLineSubjectAssociations"),
        payload=payload,
        resource_id=resource_id,
        resource="bankLineMatch",
        display_resource="bank-line match",
    )


def _bank_line_specification(
    *,
    execute_tool_name: str,
    method: WriteMethod,
    payload: dict[str, JsonValue] | None,
    resource_id: str | None,
) -> WriteOperationSpec:
    """Build the fixed shape for one bank-line CUD operation."""

    return _bank_line_write_specification(
        execute_tool_name=execute_tool_name,
        method=method,
        collection_path="/bankLines",
        singular_root="bankLine",
        plural_root="bankLines",
        additional_plural_roots=(),
        payload=payload,
        resource_id=resource_id,
        resource="bankLine",
        display_resource="bank line",
    )


def _bank_line_subject_association_specification(
    *,
    execute_tool_name: str,
    method: WriteMethod,
    payload: dict[str, JsonValue] | None,
    resource_id: str | None,
) -> WriteOperationSpec:
    """Build the fixed shape for one bank-line subject-association CUD operation."""

    return _bank_line_write_specification(
        execute_tool_name=execute_tool_name,
        method=method,
        collection_path="/bankLineSubjectAssociations",
        singular_root="bankLineSubjectAssociation",
        plural_root="bankLineSubjectAssociations",
        additional_plural_roots=(),
        payload=payload,
        resource_id=resource_id,
        resource="bankLineSubjectAssociation",
        display_resource="bank-line subject association",
    )


def _bank_line_write_specification(
    *,
    execute_tool_name: str,
    method: WriteMethod,
    collection_path: str,
    singular_root: str,
    plural_root: str,
    additional_plural_roots: tuple[str, ...],
    payload: dict[str, JsonValue] | None,
    resource_id: str | None,
    resource: str,
    display_resource: str,
) -> WriteOperationSpec:
    """Build one complete server-known write specification."""

    action = {
        WriteMethod.POST: "create",
        WriteMethod.PUT: "update",
        WriteMethod.DELETE: "delete",
    }[method]
    expected_effect_state: dict[str, JsonValue] = {"action": action, "resource": resource}
    if resource_id is not None:
        expected_effect_state["id"] = resource_id
    return WriteOperationSpec(
        execute_tool_name=execute_tool_name,
        method=method,
        collection_path=collection_path,
        singular_root=singular_root,
        plural_root=plural_root,
        additional_plural_roots=additional_plural_roots,
        payload=payload,
        resource_id=resource_id,
        organization_id=None,
        summary=f"{action.capitalize()} one Billy {display_resource}.",
        expected_effect_state=expected_effect_state,
    )
