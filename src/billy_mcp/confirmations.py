"""Opaque, short-lived, single-use bindings for future write execution tools."""

from __future__ import annotations

import json
import secrets
import threading
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import cast
from urllib.parse import SplitResult, urlsplit, urlunsplit

from pydantic import BaseModel, ConfigDict, Field, field_validator

from billy_mcp.models import StableErrorCode, ToolError

MAX_TICKET_TTL = timedelta(minutes=5)
TICKET_RANDOM_BYTES = 32


def normalize_destination_url(value: str) -> str:
    """Canonicalise destination identity, including scheme, host, port, path and query."""

    parsed = urlsplit(value)
    if parsed.scheme not in {"http", "https"} or not parsed.hostname:
        raise ValueError("Destination must be an absolute HTTP(S) URL")
    if parsed.username is not None or parsed.password is not None or parsed.fragment:
        raise ValueError("Destination must not include credentials or a fragment")
    host = parsed.hostname.lower()
    default_port = 443 if parsed.scheme == "https" else 80
    port = parsed.port
    netloc = host if port is None or port == default_port else f"{host}:{port}"
    path = parsed.path or "/"
    return urlunsplit(SplitResult(parsed.scheme.lower(), netloc, path, parsed.query, ""))


def _normalise_json(value: object) -> object:
    if value is None or isinstance(value, str | int | float | bool):
        return value
    if isinstance(value, Path):
        return str(value.expanduser().resolve(strict=False))
    if isinstance(value, Mapping):
        mapping = cast(Mapping[object, object], value)
        return {str(key): _normalise_json(item) for key, item in mapping.items()}
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        sequence = cast(Sequence[object], value)
        return [_normalise_json(item) for item in sequence]
    raise TypeError(f"Unsupported canonical JSON value: {type(value).__name__}")


def canonical_json(value: object) -> str:
    """Produce deterministic JSON suitable for exact ticket binding comparisons."""

    return json.dumps(
        _normalise_json(value),
        allow_nan=False,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    )


class ConfirmationBinding(BaseModel):
    """All exact values that a preview binds for its matching execute call."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    tool: str = Field(min_length=1)
    organization_id: str | None = None
    target: object = None
    request: object = None
    expected_effect_state: object = None
    file_path: Path | None = None
    file_digest: str | None = None
    destination_url: str | None = None

    @field_validator("file_path", mode="after")
    @classmethod
    def canonical_file_path(cls, value: Path | None) -> Path | None:
        return None if value is None else value.expanduser().resolve(strict=False)

    @field_validator("destination_url", mode="after")
    @classmethod
    def canonical_destination(cls, value: str | None) -> str | None:
        return None if value is None else normalize_destination_url(value)

    def canonical(self) -> str:
        return canonical_json(self.model_dump(mode="json"))


@dataclass(frozen=True)
class ConfirmationTicket:
    """The opaque secret issued by a preview; it contains no binding data itself."""

    value: str
    expires_at: datetime


@dataclass(frozen=True)
class _TicketRecord:
    binding: ConfirmationBinding
    expires_at: datetime


class ConfirmationFailure(Exception):
    """A stable confirmation failure suitable for direct tool translation."""

    def __init__(self, code: StableErrorCode, message: str) -> None:
        self.error = ToolError(code=code, message=message)
        super().__init__(message)


class ConfirmationStore:
    """Thread-safe volatile storage; restarting the process discards all tickets."""

    def __init__(self, clock: Callable[[], datetime] | None = None) -> None:
        self._clock = clock or (lambda: datetime.now(UTC))
        self._records: dict[str, _TicketRecord] = {}
        self._consumed: set[str] = set()
        self._lock = threading.Lock()

    def issue(
        self,
        binding: ConfirmationBinding,
        *,
        ttl: timedelta = MAX_TICKET_TTL,
    ) -> ConfirmationTicket:
        """Create an opaque ticket using 256 bits of cryptographic entropy."""

        if ttl <= timedelta() or ttl > MAX_TICKET_TTL:
            raise ValueError("Ticket TTL must be greater than zero and at most five minutes")
        now = self._now()
        ticket = secrets.token_urlsafe(TICKET_RANDOM_BYTES)
        expires_at = now + ttl
        with self._lock:
            self._records[ticket] = _TicketRecord(binding=binding, expires_at=expires_at)
        return ConfirmationTicket(value=ticket, expires_at=expires_at)

    def consume(self, ticket: str, binding: ConfirmationBinding) -> ConfirmationBinding:
        """Validate then atomically consume a ticket for the exact canonical binding."""

        now = self._now()
        with self._lock:
            if ticket in self._consumed:
                raise ConfirmationFailure(
                    StableErrorCode.CONFIRMATION_CONSUMED,
                    "Confirmation ticket has already been consumed.",
                )
            record = self._records.get(ticket)
            if record is None:
                raise ConfirmationFailure(
                    StableErrorCode.CONFIRMATION_INVALID,
                    "Confirmation ticket is invalid.",
                )
            if now >= record.expires_at:
                del self._records[ticket]
                raise ConfirmationFailure(
                    StableErrorCode.CONFIRMATION_EXPIRED,
                    "Confirmation ticket has expired.",
                )
            if record.binding.canonical() != binding.canonical():
                raise ConfirmationFailure(
                    StableErrorCode.CONFIRMATION_MISMATCH,
                    "Confirmation ticket does not match this operation.",
                )
            del self._records[ticket]
            self._consumed.add(ticket)
            return record.binding

    def _now(self) -> datetime:
        now = self._clock()
        return now if now.tzinfo is not None else now.replace(tzinfo=UTC)
