"""Volatile preview/execute tickets for Billy interface writes.

Preview issues a confirmation ticket and performs no Billy mutation. Execute
accepts only that ticket and returns the bound request so a family module can
submit the exact previewed interface action once. This lane never calls the
Billy HTTP API.
"""

from __future__ import annotations

import threading
from datetime import UTC, datetime
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field, JsonValue, field_validator

from billy_mcp.confirmations import (
    ConfirmationBinding,
    ConfirmationFailure,
    ConfirmationStore,
    canonical_json,
)
from billy_mcp.models import StableErrorCode, ToolError


class UiWritePreviewResult(BaseModel):
    """Non-mutating result of a UI write preview."""

    model_config = ConfigDict(extra="forbid")

    summary: str = Field(min_length=1)
    canonical_request: dict[str, JsonValue]
    expected_effect_state: dict[str, JsonValue]
    confirmation_ticket: str = Field(min_length=1)
    expires_at: datetime

    @field_validator("expires_at")
    @classmethod
    def expires_at_is_utc(cls, value: datetime) -> datetime:
        if value.tzinfo is None:
            raise ValueError("expires_at must be timezone-aware")
        return value.astimezone(UTC)


class UiWriteExecuteInput(BaseModel):
    """The sole input accepted by a UI write execute tool."""

    model_config = ConfigDict(extra="forbid")

    confirmation_ticket: str = Field(min_length=1)


class UiWritePrepared(BaseModel):
    """Server-held preview payload restored at execute time."""

    model_config = ConfigDict(extra="forbid")

    binding: ConfirmationBinding
    canonical_request: dict[str, JsonValue]
    expected_effect_state: dict[str, JsonValue]
    summary: str


class UiWriteProtocol:
    """Issue and consume UI write tickets without performing a mutation."""

    def __init__(self, confirmations: ConfirmationStore) -> None:
        self._confirmations = confirmations
        self._prepared: dict[str, UiWritePrepared] = {}
        self._lock = threading.Lock()

    def preview(
        self,
        *,
        execute_tool_name: str,
        organization_id: str | None,
        target: object,
        canonical_request: dict[str, JsonValue],
        expected_effect_state: dict[str, JsonValue],
        summary: str,
        file_path: Path | None = None,
        file_digest: str | None = None,
        destination_url: str | None = None,
    ) -> UiWritePreviewResult | ToolError:
        """Bind the exact UI write and return a ticket. Does not submit."""

        if organization_id is None or not organization_id.strip():
            return ToolError(
                code=StableErrorCode.ORGANIZATION_REQUIRED,
                message="A proven Billy organisation id is required.",
            )
        organization_id = organization_id.strip()
        binding = ConfirmationBinding(
            tool=execute_tool_name,
            organization_id=organization_id,
            target=target,
            request=canonical_request,
            expected_effect_state=expected_effect_state,
            file_path=file_path,
            file_digest=file_digest,
            destination_url=destination_url,
        )
        issued = self._confirmations.issue(binding)
        prepared = UiWritePrepared(
            binding=binding,
            canonical_request=canonical_request,
            expected_effect_state=expected_effect_state,
            summary=summary,
        )
        with self._lock:
            self._prepared[issued.value] = prepared
        return UiWritePreviewResult(
            summary=summary,
            canonical_request=canonical_request,
            expected_effect_state=expected_effect_state,
            confirmation_ticket=issued.value,
            expires_at=issued.expires_at,
        )

    def consume(
        self,
        input: UiWriteExecuteInput,
        *,
        execute_tool_name: str,
    ) -> UiWritePrepared | ToolError:
        """Consume the ticket for the exact execute tool. Caller then submits."""

        with self._lock:
            prepared = self._prepared.get(input.confirmation_ticket)
        if prepared is None:
            terminal = self._confirmations.terminal_failure(input.confirmation_ticket)
            if terminal is not None:
                return terminal
            return ToolError(
                code=StableErrorCode.CONFIRMATION_INVALID,
                message="Confirmation ticket is invalid.",
            )
        if prepared.binding.tool != execute_tool_name:
            return ToolError(
                code=StableErrorCode.CONFIRMATION_MISMATCH,
                message="Confirmation ticket is not valid for this execute tool.",
            )
        try:
            self._confirmations.consume(input.confirmation_ticket, prepared.binding)
        except ConfirmationFailure as failure:
            return failure.error
        with self._lock:
            self._prepared.pop(input.confirmation_ticket, None)
        return prepared


def request_fingerprint(value: object) -> str:
    """Deterministic binding fingerprint for tests and logs (no secrets)."""

    return canonical_json(value)
