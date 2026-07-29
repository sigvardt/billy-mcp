"""Shared typed contracts used by the server and coverage machinery."""

from __future__ import annotations

from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class StableErrorCode(StrEnum):
    """Public errors defined by the approved Billy MCP design."""

    AUTH_REQUIRED = "AUTH_REQUIRED"
    AUTH_EXPIRED = "AUTH_EXPIRED"
    AUTH_INTERACTION_REQUIRED = "AUTH_INTERACTION_REQUIRED"
    ORGANIZATION_REQUIRED = "ORGANIZATION_REQUIRED"
    ORGANIZATION_MISMATCH = "ORGANIZATION_MISMATCH"
    VALIDATION_ERROR = "VALIDATION_ERROR"
    NOT_FOUND = "NOT_FOUND"
    CONFLICT = "CONFLICT"
    CONFIRMATION_INVALID = "CONFIRMATION_INVALID"
    CONFIRMATION_EXPIRED = "CONFIRMATION_EXPIRED"
    CONFIRMATION_CONSUMED = "CONFIRMATION_CONSUMED"
    CONFIRMATION_MISMATCH = "CONFIRMATION_MISMATCH"
    FILE_NOT_ALLOWED = "FILE_NOT_ALLOWED"
    FILE_CHANGED = "FILE_CHANGED"
    PLAN_UNAVAILABLE = "PLAN_UNAVAILABLE"
    UI_CHANGED = "UI_CHANGED"
    EGRESS_DENIED = "EGRESS_DENIED"
    RATE_LIMITED = "RATE_LIMITED"
    BILLY_ERROR = "BILLY_ERROR"
    CLEANUP_FAILED = "CLEANUP_FAILED"


class ToolError(BaseModel):
    """Stable, serialisable failure returned by any registered MCP tool."""

    model_config = ConfigDict(extra="forbid")

    code: StableErrorCode
    message: str
    details: dict[str, Any] = Field(default_factory=dict)


class CoverageStatus(BaseModel):
    """The four required API states plus the UI-only visual verification state."""

    model_config = ConfigDict(extra="forbid")

    discovered: bool = False
    implemented: bool = False
    contract_tested: bool = False
    live_tested: bool = False
    vision_verified: bool | None = None
