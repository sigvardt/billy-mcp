"""Shared typed contracts used by the server and coverage machinery."""

from __future__ import annotations

from enum import StrEnum
from typing import Any, Literal

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


class AuthStatusInput(BaseModel):
    """Empty, strict input boundary for the read-only browser session check."""

    model_config = ConfigDict(extra="forbid")


class AuthStatusSuccess(BaseModel):
    """The one browser-authentication state verified by the login signature."""

    model_config = ConfigDict(extra="forbid")

    status: Literal[StableErrorCode.AUTH_REQUIRED] = StableErrorCode.AUTH_REQUIRED


class AuthLoginStartInput(BaseModel):
    """Empty, strict input boundary for the fixed pre-submit transition."""

    model_config = ConfigDict(extra="forbid")


class AuthLoginStartSuccess(BaseModel):
    """The only positive result proved immediately after the internal submit action."""

    model_config = ConfigDict(extra="forbid")

    status: Literal["AUTHENTICATING"] = "AUTHENTICATING"


class AuthLoginWaitInput(BaseModel):
    """Empty, strict input boundary for observing post-login session state."""

    model_config = ConfigDict(extra="forbid")


class AuthLoginWaitSuccess(BaseModel):
    """Post-login observation: login still required, or authenticated shell READY."""

    model_config = ConfigDict(extra="forbid")

    status: Literal["AUTH_REQUIRED", "READY"]


class UiInvoicesListInput(BaseModel):
    """Empty, strict input boundary for the read-only invoices list shell tool."""

    model_config = ConfigDict(extra="forbid")


class UiInvoicesListSuccess(BaseModel):
    """Non-PII classification of the observed Billy invoices list shell."""

    model_config = ConfigDict(extra="forbid")

    path_class: Literal["/:org_slug/invoices"] = "/:org_slug/invoices"
    heading: Literal["Fakturaer"] = "Fakturaer"
    create_action_visible: bool
    shell_markers_present: bool


class UiProductsListInput(BaseModel):
    """Empty, strict input boundary for the read-only products list shell tool."""

    model_config = ConfigDict(extra="forbid")


class UiProductsListSuccess(BaseModel):
    """Non-PII classification of the observed Billy products list shell."""

    model_config = ConfigDict(extra="forbid")

    path_class: Literal["/:org_slug/products"] = "/:org_slug/products"
    heading: Literal["Produkter"] = "Produkter"
    search_control_visible: bool
    shell_markers_present: bool


class UiClientsListInput(BaseModel):
    """Empty, strict input boundary for the read-only clients list shell tool."""

    model_config = ConfigDict(extra="forbid")


class UiClientsListSuccess(BaseModel):
    """Non-PII classification of the observed Billy clients list shell."""

    model_config = ConfigDict(extra="forbid")

    path_class: Literal["/:org_slug/clients"] = "/:org_slug/clients"
    heading: Literal["Kunder"] = "Kunder"
    create_action_visible: bool
    shell_markers_present: bool


class UiBankAccountsListInput(BaseModel):
    """Empty, strict input boundary for the read-only bank accounts list shell tool."""

    model_config = ConfigDict(extra="forbid")


class UiBankAccountsListSuccess(BaseModel):
    """Non-PII classification of the observed Billy bank accounts list shell."""

    model_config = ConfigDict(extra="forbid")

    path_class: Literal["/:org_slug/bank-accounts"] = "/:org_slug/bank-accounts"
    heading: Literal["Bankkonti"] = "Bankkonti"
    connect_bank_action_visible: bool
    shell_markers_present: bool


class UiQuotesListInput(BaseModel):
    """Empty, strict input boundary for the read-only quotes list shell tool."""

    model_config = ConfigDict(extra="forbid")


class UiQuotesListSuccess(BaseModel):
    """Non-PII classification of the observed Billy quotes list shell."""

    model_config = ConfigDict(extra="forbid")

    path_class: Literal["/:org_slug/quotes"] = "/:org_slug/quotes"
    heading: Literal["Tilbud"] = "Tilbud"
    create_action_visible: bool
    shell_markers_present: bool


class UiRecurringInvoicesListInput(BaseModel):
    """Empty, strict input boundary for the read-only recurring invoices list shell tool."""

    model_config = ConfigDict(extra="forbid")


class UiRecurringInvoicesListSuccess(BaseModel):
    """Non-PII classification of the observed Billy recurring invoices list shell."""

    model_config = ConfigDict(extra="forbid")

    path_class: Literal["/:org_slug/recurring_invoices"] = "/:org_slug/recurring_invoices"
    heading: Literal["Abonnementer"] = "Abonnementer"
    create_action_visible: bool
    shell_markers_present: bool


class CoverageStatus(BaseModel):
    """The four required API states plus the UI-only visual verification state."""

    model_config = ConfigDict(extra="forbid")

    discovered: bool = False
    implemented: bool = False
    contract_tested: bool = False
    live_tested: bool = False
    vision_verified: bool | None = None
