"""Reusable ticketed protocol for documented singular Billy API writes.

Resource leaves provide an operation specification during preview.  This module
keeps the resulting request server-side, so execution accepts only the opaque
confirmation ticket and can send exactly the previewed request once.
"""

from __future__ import annotations

import json
import threading
from collections.abc import Mapping
from dataclasses import dataclass
from datetime import UTC, datetime
from enum import StrEnum
from typing import cast
from urllib.parse import quote, urlsplit

from pydantic import BaseModel, ConfigDict, Field, JsonValue, field_validator, model_validator

from billy_mcp.client import BillyHttpClient, BillyResponse
from billy_mcp.confirmations import (
    ConfirmationBinding,
    ConfirmationFailure,
    ConfirmationStore,
    canonical_json,
)
from billy_mcp.models import StableErrorCode, ToolError


class WriteMethod(StrEnum):
    """The only documented singular write methods supported by this protocol."""

    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"


class WritePreviewResult(BaseModel):
    """The complete, non-mutating result returned by a resource preview tool."""

    model_config = ConfigDict(extra="forbid")

    summary: str = Field(min_length=1)
    canonical_request: dict[str, JsonValue]
    expected_effect_state: dict[str, JsonValue]
    confirmation_ticket: str = Field(min_length=1)
    expires_at: datetime

    @field_validator("expires_at")
    @classmethod
    def expires_at_is_utc(cls, value: datetime) -> datetime:
        """Keep the public expiry unambiguously represented in UTC."""

        if value.tzinfo is None:
            raise ValueError("expires_at must be timezone-aware")
        return value.astimezone(UTC)


class WriteExecuteInput(BaseModel):
    """The sole input accepted by every write execute tool."""

    model_config = ConfigDict(extra="forbid")

    confirmation_ticket: str = Field(min_length=1)


class WriteExecutionResult(BaseModel):
    """Mapped documented records changed by a successfully executed write."""

    model_config = ConfigDict(extra="forbid")

    changed_records: dict[str, list[dict[str, JsonValue]]]
    deleted_records: dict[str, list[str]] | None = None


class WriteOperationSpec(BaseModel):
    """Server-known details of one supported singular create, update, or delete."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    execute_tool_name: str = Field(min_length=1)
    method: WriteMethod
    collection_path: str = Field(min_length=1)
    singular_root: str = Field(min_length=1)
    plural_root: str = Field(min_length=1)
    additional_plural_roots: tuple[str, ...] = ()
    payload: dict[str, JsonValue] | None = None
    resource_id: str | None = None
    organization_id: str | None = None
    summary: str = Field(min_length=1)
    expected_effect_state: dict[str, JsonValue]

    @field_validator("collection_path")
    @classmethod
    def documented_relative_collection_path(cls, value: str) -> str:
        """Reject URL escape hatches before a resource leaf can prepare one."""

        parsed = urlsplit(value)
        if (
            parsed.scheme
            or parsed.netloc
            or parsed.query
            or parsed.fragment
            or not parsed.path.startswith("/")
            or parsed.path == "/v2"
            or parsed.path.startswith("/v2/")
            or ".." in parsed.path.split("/")
        ):
            raise ValueError("collection_path must be a relative Billy API collection path")
        return parsed.path.rstrip("/")

    @model_validator(mode="after")
    def operation_has_only_its_documented_shape(self) -> WriteOperationSpec:
        """Constrain the generic helper to the three frozen singular write shapes."""

        if self.method is WriteMethod.POST:
            if self.resource_id is not None or self.payload is None:
                raise ValueError("POST requires a payload and no resource_id")
        elif self.method is WriteMethod.PUT:
            if not self.resource_id or self.payload is None:
                raise ValueError("PUT requires a non-empty resource_id and payload")
        elif self.payload is not None or not self.resource_id:
            raise ValueError("DELETE requires a non-empty resource_id and no payload")
        declared_plural_roots = (self.plural_root, *self.additional_plural_roots)
        if any(not root for root in declared_plural_roots):
            raise ValueError("changed plural roots must be non-empty")
        if len(set(declared_plural_roots)) != len(declared_plural_roots):
            raise ValueError("changed plural roots must be unique")
        return self


@dataclass(frozen=True)
class _PreparedWrite:
    """The volatile authoritative operation retained between preview and execute."""

    method: WriteMethod
    path: str
    json_body: dict[str, JsonValue] | None
    binding: ConfirmationBinding
    plural_root: str
    additional_plural_roots: tuple[str, ...]


class WriteProtocolService:
    """Preview and execute documented singular writes without caller-controlled HTTP."""

    def __init__(self, client: BillyHttpClient, confirmations: ConfirmationStore) -> None:
        self._client = client
        self._confirmations = confirmations
        self._prepared_by_ticket: dict[str, _PreparedWrite] = {}
        self._prepared_lock = threading.Lock()

    def preview(self, specification: WriteOperationSpec) -> WritePreviewResult:
        """Issue a ticket for a canonical request without performing any HTTP request."""

        canonical_request = canonical_request_for(specification)
        expected_effect_state = _canonical_object(specification.expected_effect_state)
        binding = confirmation_binding_for(
            specification,
            canonical_request=canonical_request,
            expected_effect_state=expected_effect_state,
        )
        issued = self._confirmations.issue(binding)
        prepared = _PreparedWrite(
            method=specification.method,
            path=execution_path_for(specification),
            json_body=None if specification.method is WriteMethod.DELETE else canonical_request,
            binding=binding,
            plural_root=specification.plural_root,
            additional_plural_roots=specification.additional_plural_roots,
        )
        with self._prepared_lock:
            self._prepared_by_ticket[issued.value] = prepared
        return WritePreviewResult(
            summary=specification.summary,
            canonical_request=canonical_request,
            expected_effect_state=expected_effect_state,
            confirmation_ticket=issued.value,
            expires_at=issued.expires_at,
        )

    def execute(self, input: WriteExecuteInput) -> WriteExecutionResult | ToolError:
        """Consume a ticket and send its one retained request through the locked client."""

        with self._prepared_lock:
            prepared = self._prepared_by_ticket.get(input.confirmation_ticket)
        if prepared is None:
            return ToolError(
                code=StableErrorCode.CONFIRMATION_INVALID,
                message="Confirmation ticket is invalid.",
            )
        try:
            self._confirmations.consume(input.confirmation_ticket, prepared.binding)
        except ConfirmationFailure as failure:
            return failure.error
        response = self._client.request(
            prepared.method.value,
            prepared.path,
            json_body=prepared.json_body,
        )
        return _map_execution_response(response, prepared)


def canonical_request_for(specification: WriteOperationSpec) -> dict[str, JsonValue]:
    """Return the exact JSON-safe request object bound to a preview ticket."""

    raw_request: dict[str, object]
    if specification.method is WriteMethod.DELETE:
        raw_request = {"id": specification.resource_id}
    else:
        raw_request = {specification.singular_root: specification.payload}
    return _canonical_object(raw_request)


def execution_path_for(specification: WriteOperationSpec) -> str:
    """Build the one relative Billy API path allowed by an operation specification."""

    if specification.method is WriteMethod.POST:
        return specification.collection_path
    resource_id = specification.resource_id
    if resource_id is None:
        raise AssertionError("validated update or delete operation must have a resource_id")
    return f"{specification.collection_path}/{quote(resource_id, safe='')}"


def confirmation_binding_for(
    specification: WriteOperationSpec,
    *,
    canonical_request: dict[str, JsonValue] | None = None,
    expected_effect_state: dict[str, JsonValue] | None = None,
) -> ConfirmationBinding:
    """Build this cohort's full exact binding with no file or destination identity."""

    return ConfirmationBinding(
        tool=specification.execute_tool_name,
        organization_id=specification.organization_id,
        target=None if specification.method is WriteMethod.POST else specification.resource_id,
        request=canonical_request or canonical_request_for(specification),
        expected_effect_state=expected_effect_state
        or _canonical_object(specification.expected_effect_state),
        file_path=None,
        file_digest=None,
        destination_url=None,
    )


def _canonical_object(value: object) -> dict[str, JsonValue]:
    """Normalise recursively and deterministically before exposing or binding JSON."""

    canonical_value = json.loads(canonical_json(value))
    if not isinstance(canonical_value, dict):
        raise TypeError("Canonical write values must be JSON objects")
    return cast(dict[str, JsonValue], canonical_value)


def _map_execution_response(
    response: BillyResponse | ToolError, prepared: _PreparedWrite
) -> WriteExecutionResult | ToolError:
    """Map only declared changed-record roots and documented deleted-record metadata."""

    if isinstance(response, ToolError):
        return response
    data = _mapping(response.data)
    if data is None:
        return _invalid_success_response(prepared.plural_root)

    changed_records: dict[str, list[dict[str, JsonValue]]] = {}
    declared_plural_roots = (prepared.plural_root, *prepared.additional_plural_roots)
    for plural_root in declared_plural_roots:
        if plural_root not in data:
            if plural_root == prepared.plural_root and prepared.method is not WriteMethod.DELETE:
                return _invalid_success_response(prepared.plural_root)
            continue
        root_value = data[plural_root]
        if (
            root_value is None
            and plural_root == prepared.plural_root
            and prepared.method is WriteMethod.DELETE
        ):
            continue
        records = _records(root_value)
        if records is None:
            return _invalid_success_response(plural_root)
        changed_records[plural_root] = records

    deleted_records = _deleted_records(data, declared_plural_roots)
    if isinstance(deleted_records, ToolError):
        return deleted_records
    return WriteExecutionResult(
        changed_records=changed_records,
        deleted_records=deleted_records,
    )


def _mapping(value: object) -> dict[str, object] | None:
    if not isinstance(value, Mapping):
        return None
    mapping = cast(Mapping[object, object], value)
    return {str(key): item for key, item in mapping.items()}


def _records(value: object) -> list[dict[str, JsonValue]] | None:
    if not isinstance(value, list):
        return None
    records: list[dict[str, JsonValue]] = []
    for record in cast(list[object], value):
        mapping = _mapping(record)
        if mapping is None:
            return None
        try:
            records.append(cast(dict[str, JsonValue], json.loads(canonical_json(mapping))))
        except (TypeError, ValueError):
            return None
    return records


def _deleted_records(
    data: dict[str, object], declared_plural_roots: tuple[str, ...]
) -> dict[str, list[str]] | ToolError | None:
    meta = data.get("meta")
    if meta is None:
        return None
    meta_mapping = _mapping(meta)
    if meta_mapping is None:
        return _invalid_success_response("meta")
    deleted = meta_mapping.get("deletedRecords")
    if deleted is None:
        return None
    deleted_mapping = _mapping(deleted)
    if deleted_mapping is None:
        return _invalid_success_response("meta.deletedRecords")
    deleted_records: dict[str, list[str]] = {}
    for plural_root in declared_plural_roots:
        if plural_root not in deleted_mapping:
            continue
        resource_ids = deleted_mapping[plural_root]
        if not isinstance(resource_ids, list):
            return _invalid_success_response(f"meta.deletedRecords.{plural_root}")
        identifiers = cast(list[object], resource_ids)
        if not all(isinstance(item, str) for item in identifiers):
            return _invalid_success_response(f"meta.deletedRecords.{plural_root}")
        deleted_records[plural_root] = cast(list[str], identifiers)
    return deleted_records or None


def _invalid_success_response(root: str) -> ToolError:
    return ToolError(
        code=StableErrorCode.VALIDATION_ERROR,
        message=f"Billy write response did not contain a valid {root} root.",
    )
