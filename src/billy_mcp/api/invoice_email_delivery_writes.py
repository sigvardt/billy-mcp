"""Ticketed Billy invoice email and electronic-delivery special operations."""

from __future__ import annotations

import threading
from collections.abc import Mapping
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Annotated, Literal, cast

from fastmcp import FastMCP
from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    JsonValue,
    StrictStr,
    ValidationError,
    field_validator,
    model_validator,
)

from billy_mcp.client import BillyHttpClient, BillyResponse
from billy_mcp.config import AppConfig
from billy_mcp.confirmations import ConfirmationBinding, ConfirmationFailure, ConfirmationStore
from billy_mcp.models import StableErrorCode, ToolError
from billy_mcp.redaction import redact

_EMAIL_EXECUTE_TOOL_NAME = "api_invoices_send_email_execute"
_DELIVERY_EXECUTE_TOOL_NAME = "api_invoice_deliveries_create_execute"
_ToolText = Annotated[StrictStr, Field(min_length=1)]
_ToolOptionalText = Annotated[StrictStr | None, Field(min_length=1)]


class _StrictInput(BaseModel):
    """Reject coercion and undeclared fields at every public input boundary."""

    model_config = ConfigDict(extra="forbid", strict=True)


class InvoiceEmailPreviewInput(_StrictInput):
    """The complete bounded input for one invoice email preview."""

    invoiceId: str = Field(min_length=1)
    contactPersonId: str = Field(min_length=1)
    emailBody: str = Field(min_length=1)
    emailSubject: str = Field(min_length=1)
    copyToUserId: str | None = Field(default=None, min_length=1)

    @field_validator("invoiceId", "contactPersonId", "emailBody", "emailSubject", "copyToUserId")
    @classmethod
    def meaningful_text(cls, value: str | None) -> str | None:
        """Reject blank values without mutating the exact request selected by the caller."""

        if value is not None and not value.strip():
            raise ValueError("value must not be blank")
        return value


class InvoiceDeliveryPreviewInput(_StrictInput):
    """The complete bounded input for one electronic invoice-delivery preview."""

    invoiceId: str = Field(min_length=1)
    organizationId: str = Field(min_length=1)
    receiverIdType: Literal["gln", "cvr"]
    senderUserId: str = Field(min_length=1)
    receiverGln: str | None = Field(default=None, min_length=1)
    orderReference: str | None = Field(default=None, min_length=1)

    @field_validator("invoiceId", "organizationId", "senderUserId", "receiverGln", "orderReference")
    @classmethod
    def meaningful_text(cls, value: str | None) -> str | None:
        """Reject blank identifiers and optional values before a ticket is created."""

        if value is not None and not value.strip():
            raise ValueError("value must not be blank")
        return value

    @model_validator(mode="after")
    def validate_receiver(self) -> InvoiceDeliveryPreviewInput:
        """Bind a GLN only to the documented GLN receiver identifier type."""

        if self.receiverIdType == "gln":
            if (
                self.receiverGln is None
                or len(self.receiverGln) != 13
                or not self.receiverGln.isdigit()
            ):
                raise ValueError("receiverGln must be exactly 13 digits when receiverIdType is gln")
        elif self.receiverGln is not None:
            raise ValueError("receiverGln is only permitted when receiverIdType is gln")
        return self


class InvoiceEmailDeliveryExecuteInput(_StrictInput):
    """The ticket-only input shared by both external-send executors."""

    confirmation_ticket: str = Field(min_length=1)

    @field_validator("confirmation_ticket")
    @classmethod
    def meaningful_ticket(cls, value: str) -> str:
        """Reject whitespace-only opaque ticket values before store lookup."""

        if not value.strip():
            raise ValueError("confirmation_ticket must not be blank")
        return value


class InvoiceEmailDeliveryPreviewSuccess(BaseModel):
    """A typed, non-mutating external-send confirmation preview."""

    model_config = ConfigDict(extra="forbid", strict=True)

    summary: str = Field(min_length=1)
    canonical_request: dict[str, JsonValue]
    expected_effect_state: dict[str, JsonValue]
    confirmation_ticket: str = Field(min_length=1)
    expires_at: datetime

    @field_validator("summary", "confirmation_ticket")
    @classmethod
    def meaningful_text(cls, value: str) -> str:
        """Keep every public success string meaningful."""

        if not value.strip():
            raise ValueError("value must not be blank")
        return value

    @field_validator("expires_at")
    @classmethod
    def utc_expiry(cls, value: datetime) -> datetime:
        """Expose expiry in one unambiguous timezone."""

        if value.tzinfo is None:
            raise ValueError("expires_at must be timezone-aware")
        return value.astimezone(UTC)


class InvoiceEmailExecuteSuccess(BaseModel):
    """The frozen provisional email success root, with sensitive values redacted."""

    model_config = ConfigDict(extra="forbid", strict=True)

    changed_records: list[dict[str, JsonValue]]


class InvoiceDeliveryExecuteSuccess(BaseModel):
    """The frozen provisional invoice-delivery success root."""

    model_config = ConfigDict(extra="forbid", strict=True)

    invoiceDelivery: dict[str, JsonValue]


@dataclass(frozen=True)
class _PreparedOperation:
    """The one volatile request retained for an issued confirmation ticket."""

    binding: ConfirmationBinding
    expires_at: datetime
    path: str
    json_body: dict[str, JsonValue]


class InvoiceEmailDeliveryService:
    """Issue and consume exact one-use bindings for the two high-impact specials."""

    def __init__(
        self,
        client: BillyHttpClient,
        confirmations: ConfirmationStore,
        *,
        selected_organization: str | None,
    ) -> None:
        self._client = client
        self._confirmations = confirmations
        self._selected_organization = selected_organization
        self._prepared_by_ticket: dict[str, _PreparedOperation] = {}
        self._prepared_lock = threading.Lock()

    def preview_email(self, input: InvoiceEmailPreviewInput) -> InvoiceEmailDeliveryPreviewSuccess:
        """Prepare one documented nested invoice-email POST without HTTP."""

        email: dict[str, JsonValue] = {
            "contactPersonId": input.contactPersonId,
            "emailBody": input.emailBody,
            "emailSubject": input.emailSubject,
        }
        if input.copyToUserId is not None:
            email["copyToUserId"] = input.copyToUserId
        request: dict[str, JsonValue] = {
            "invoiceId": input.invoiceId,
            "organizationId": self._selected_organization,
            "email": email,
        }
        effect: dict[str, JsonValue] = {
            "action": "send_email",
            "resource": "invoice",
            "invoiceId": input.invoiceId,
        }
        return self._issue(
            tool=_EMAIL_EXECUTE_TOOL_NAME,
            organization_id=self._selected_organization,
            target=input.invoiceId,
            canonical_request=request,
            expected_effect_state=effect,
            path=f"/invoices/{input.invoiceId}/emails",
            json_body={"email": email},
            summary="Send one Billy invoice email to its selected contact person.",
        )

    def preview_delivery(
        self, input: InvoiceDeliveryPreviewInput
    ) -> InvoiceEmailDeliveryPreviewSuccess:
        """Prepare one documented invoice-delivery POST without HTTP."""

        delivery: dict[str, JsonValue] = {
            "invoiceId": input.invoiceId,
            "organizationId": input.organizationId,
            "receiverIdType": input.receiverIdType,
            "senderUserId": input.senderUserId,
        }
        if input.receiverGln is not None:
            delivery["receiverGln"] = input.receiverGln
        if input.orderReference is not None:
            delivery["orderReference"] = input.orderReference
        request: dict[str, JsonValue] = {"invoiceDelivery": delivery}
        effect: dict[str, JsonValue] = {
            "action": "create_invoice_delivery",
            "resource": "invoiceDelivery",
            "invoiceId": input.invoiceId,
        }
        return self._issue(
            tool=_DELIVERY_EXECUTE_TOOL_NAME,
            organization_id=input.organizationId,
            target=input.invoiceId,
            canonical_request=request,
            expected_effect_state=effect,
            path="/invoiceDeliveries",
            json_body=request,
            summary="Create one Billy electronic invoice delivery.",
        )

    def execute_email(
        self, input: InvoiceEmailDeliveryExecuteInput, *, execute_tool_name: str
    ) -> InvoiceEmailExecuteSuccess | ToolError:
        """Consume one email ticket, then make exactly one documented POST."""

        prepared_or_error = self._consume(input.confirmation_ticket, execute_tool_name)
        if isinstance(prepared_or_error, ToolError):
            return prepared_or_error
        return _map_email_response(
            self._client.request(
                "POST", prepared_or_error.path, json_body=prepared_or_error.json_body
            )
        )

    def execute_delivery(
        self, input: InvoiceEmailDeliveryExecuteInput, *, execute_tool_name: str
    ) -> InvoiceDeliveryExecuteSuccess | ToolError:
        """Consume one delivery ticket, then make exactly one documented POST."""

        prepared_or_error = self._consume(input.confirmation_ticket, execute_tool_name)
        if isinstance(prepared_or_error, ToolError):
            return prepared_or_error
        return _map_delivery_response(
            self._client.request(
                "POST", prepared_or_error.path, json_body=prepared_or_error.json_body
            )
        )

    def _issue(
        self,
        *,
        tool: str,
        organization_id: str | None,
        target: str,
        canonical_request: dict[str, JsonValue],
        expected_effect_state: dict[str, JsonValue],
        path: str,
        json_body: dict[str, JsonValue],
        summary: str,
    ) -> InvoiceEmailDeliveryPreviewSuccess:
        binding = ConfirmationBinding(
            tool=tool,
            organization_id=organization_id,
            target=target,
            request=canonical_request,
            expected_effect_state=expected_effect_state,
            file_path=None,
            file_digest=None,
            destination_url=None,
        )
        issued = self._confirmations.issue(binding)
        prepared = _PreparedOperation(
            binding=binding,
            expires_at=issued.expires_at,
            path=path,
            json_body=json_body,
        )
        with self._prepared_lock:
            self._prune_prepared(self._confirmations.current_time())
            self._prepared_by_ticket[issued.value] = prepared
        return InvoiceEmailDeliveryPreviewSuccess(
            summary=summary,
            canonical_request=canonical_request,
            expected_effect_state=expected_effect_state,
            confirmation_ticket=issued.value,
            expires_at=issued.expires_at,
        )

    def _consume(self, ticket: str, execute_tool_name: str) -> _PreparedOperation | ToolError:
        """Atomically validate the exact binding before any externally visible write."""

        now = self._confirmations.current_time()
        with self._prepared_lock:
            self._prune_prepared(now, preserve_ticket=ticket)
            prepared = self._prepared_by_ticket.get(ticket)
        if prepared is None:
            terminal_error = self._confirmations.terminal_failure(ticket)
            return terminal_error or _invalid_ticket()
        if prepared.binding.tool != execute_tool_name:
            return ToolError(
                code=StableErrorCode.CONFIRMATION_MISMATCH,
                message="Confirmation ticket is not valid for this execute tool.",
            )
        try:
            self._confirmations.consume(ticket, prepared.binding)
        except ConfirmationFailure as failure:
            if failure.error.code is not StableErrorCode.CONFIRMATION_MISMATCH:
                self._discard_prepared(ticket)
            return failure.error
        self._discard_prepared(ticket)
        return prepared

    def _discard_prepared(self, ticket: str) -> None:
        """Remove sensitive prepared request metadata after a terminal outcome."""

        with self._prepared_lock:
            self._prepared_by_ticket.pop(ticket, None)

    def _prune_prepared(self, now: datetime, *, preserve_ticket: str | None = None) -> None:
        """Drop expired request metadata while preserving the store's expiry error."""

        for ticket, prepared in tuple(self._prepared_by_ticket.items()):
            if ticket != preserve_ticket and now >= prepared.expires_at:
                del self._prepared_by_ticket[ticket]


def register_invoice_email_delivery_write_tools(
    server: FastMCP,
    client: BillyHttpClient,
    configuration: AppConfig,
    confirmations: ConfirmationStore,
) -> None:
    """Register only the two documented preview/execute special-operation pairs."""

    service = InvoiceEmailDeliveryService(
        client,
        confirmations,
        selected_organization=configuration.selected_organization,
    )

    def api_invoices_send_email_preview(
        invoiceId: _ToolText,
        contactPersonId: _ToolText,
        emailBody: _ToolText,
        emailSubject: _ToolText,
        copyToUserId: _ToolOptionalText = None,
    ) -> InvoiceEmailDeliveryPreviewSuccess:
        """Preview one invoice email without making an HTTP request."""

        return service.preview_email(
            InvoiceEmailPreviewInput(
                invoiceId=invoiceId,
                contactPersonId=contactPersonId,
                emailBody=emailBody,
                emailSubject=emailSubject,
                copyToUserId=copyToUserId,
            )
        )

    def api_invoices_send_email_execute(
        confirmation_ticket: _ToolText,
    ) -> InvoiceEmailExecuteSuccess | ToolError:
        """Send exactly the previewed invoice email once."""

        return service.execute_email(
            InvoiceEmailDeliveryExecuteInput(confirmation_ticket=confirmation_ticket),
            execute_tool_name=_EMAIL_EXECUTE_TOOL_NAME,
        )

    def api_invoice_deliveries_create_preview(
        invoiceId: _ToolText,
        organizationId: _ToolText,
        receiverIdType: Literal["gln", "cvr"],
        senderUserId: _ToolText,
        receiverGln: _ToolOptionalText = None,
        orderReference: _ToolOptionalText = None,
    ) -> InvoiceEmailDeliveryPreviewSuccess:
        """Preview one electronic invoice delivery without making an HTTP request."""

        return service.preview_delivery(
            InvoiceDeliveryPreviewInput(
                invoiceId=invoiceId,
                organizationId=organizationId,
                receiverIdType=receiverIdType,
                senderUserId=senderUserId,
                receiverGln=receiverGln,
                orderReference=orderReference,
            )
        )

    def api_invoice_deliveries_create_execute(
        confirmation_ticket: _ToolText,
    ) -> InvoiceDeliveryExecuteSuccess | ToolError:
        """Create exactly the previewed electronic invoice delivery once."""

        return service.execute_delivery(
            InvoiceEmailDeliveryExecuteInput(confirmation_ticket=confirmation_ticket),
            execute_tool_name=_DELIVERY_EXECUTE_TOOL_NAME,
        )

    server.tool(
        name="api_invoices_send_email_preview",
        description="Preview one Billy invoice email without HTTP.",
    )(api_invoices_send_email_preview)
    server.tool(
        name=_EMAIL_EXECUTE_TOOL_NAME,
        description="Send exactly one previewed Billy invoice email with its ticket.",
    )(api_invoices_send_email_execute)
    server.tool(
        name="api_invoice_deliveries_create_preview",
        description="Preview one Billy electronic invoice delivery without HTTP.",
    )(api_invoice_deliveries_create_preview)
    server.tool(
        name=_DELIVERY_EXECUTE_TOOL_NAME,
        description="Create exactly one previewed Billy invoice delivery with its ticket.",
    )(api_invoice_deliveries_create_execute)


def _map_email_response(
    response: BillyResponse | ToolError,
) -> InvoiceEmailExecuteSuccess | ToolError:
    """Map only the frozen provisional ``changed_records`` email response root."""

    if isinstance(response, ToolError):
        return response
    data = _mapping(response.data)
    if data is None:
        return _invalid_response("changed_records")
    records = _records(data.get("changed_records"))
    if records is None:
        return _invalid_response("changed_records")
    try:
        return InvoiceEmailExecuteSuccess(changed_records=records)
    except ValidationError:
        return _invalid_response("changed_records")


def _map_delivery_response(
    response: BillyResponse | ToolError,
) -> InvoiceDeliveryExecuteSuccess | ToolError:
    """Map only the frozen provisional singular ``invoiceDelivery`` response root."""

    if isinstance(response, ToolError):
        return response
    data = _mapping(response.data)
    if data is None:
        return _invalid_response("invoiceDelivery")
    delivery = _record(data.get("invoiceDelivery"))
    if delivery is None:
        return _invalid_response("invoiceDelivery")
    try:
        return InvoiceDeliveryExecuteSuccess(invoiceDelivery=delivery)
    except ValidationError:
        return _invalid_response("invoiceDelivery")


def _mapping(value: object) -> dict[str, object] | None:
    if not isinstance(value, Mapping):
        return None
    return {str(key): item for key, item in cast(Mapping[object, object], value).items()}


def _record(value: object) -> dict[str, JsonValue] | None:
    mapping = _mapping(value)
    if mapping is None:
        return None
    sanitised = redact(mapping)
    if not isinstance(sanitised, dict):
        return None
    try:
        return json_value_object(sanitised)
    except (TypeError, ValidationError):
        return None


def _records(value: object) -> list[dict[str, JsonValue]] | None:
    if not isinstance(value, list):
        return None
    records: list[dict[str, JsonValue]] = []
    for item in cast(list[object], value):
        record = _record(item)
        if record is None:
            return None
        records.append(record)
    return records


class _JsonObject(BaseModel):
    """Validate a response record is recursively JSON-safe after redaction."""

    model_config = ConfigDict(extra="forbid", strict=True)

    value: dict[str, JsonValue]


def json_value_object(value: Mapping[str, object]) -> dict[str, JsonValue]:
    """Return a typed JSON object or raise a Pydantic validation failure."""

    return _JsonObject.model_validate({"value": value}).value


def _invalid_ticket() -> ToolError:
    return ToolError(
        code=StableErrorCode.CONFIRMATION_INVALID,
        message="Confirmation ticket is invalid.",
    )


def _invalid_response(expected_root: str) -> ToolError:
    return ToolError(
        code=StableErrorCode.BILLY_ERROR,
        message=(
            "Billy API response did not contain the documented special-operation response root."
        ),
        details={"expected_root": expected_root},
    )
