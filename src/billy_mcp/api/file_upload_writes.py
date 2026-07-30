"""Ticketed binary upload tools for the documented Billy files endpoint."""

from __future__ import annotations

import errno
import hashlib
import os
import stat
import threading
from collections.abc import Mapping
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Annotated, cast

from fastmcp import FastMCP
from pydantic import BaseModel, ConfigDict, Field, JsonValue, StrictBool, StrictStr, field_validator

from billy_mcp.client import BillyHttpClient, BillyResponse
from billy_mcp.config import AppConfig
from billy_mcp.confirmations import (
    ConfirmationBinding,
    ConfirmationFailure,
    ConfirmationStore,
)
from billy_mcp.models import StableErrorCode, ToolError
from billy_mcp.redaction import redact

_EXECUTE_TOOL_NAME = "api_files_upload_execute"
_HASH_CHUNK_SIZE = 64 * 1024
_ToolText = Annotated[StrictStr, Field(min_length=1)]
_ToolHeaderText = Annotated[StrictStr, Field(min_length=1, pattern=r"^[^\r\n]+$")]
_ToolOptionalHeaderText = Annotated[StrictStr | None, Field(min_length=1, pattern=r"^[^\r\n]+$")]


class _FileUploadInput(BaseModel):
    """Strict base schema for the intentionally small upload surface."""

    model_config = ConfigDict(extra="forbid", strict=True)


class FileUploadPreviewInput(_FileUploadInput):
    """Inputs that preview one approved local file without HTTP."""

    path: str = Field(min_length=1)
    filename: str = Field(min_length=1)
    content_type: str = Field(min_length=1)
    create_attachment: bool = False
    create_variants: bool = False
    organization_id: str | None = Field(default=None, min_length=1)
    should_scan: bool = False

    @field_validator("path", "filename", "content_type")
    @classmethod
    def non_blank_text(cls, value: str) -> str:
        """Reject blank caller input before any local resolution."""

        if not value.strip():
            raise ValueError("value must not be blank")
        return value

    @field_validator("filename", "content_type", "organization_id")
    @classmethod
    def safe_header_value(cls, value: str | None) -> str | None:
        """Reject values that could create a caller-controlled extra HTTP header."""

        if value is not None and ("\r" in value or "\n" in value):
            raise ValueError("header values must not contain CR or LF")
        if value is not None and not value.strip():
            raise ValueError("header values must not be blank")
        return value

    @field_validator("path")
    @classmethod
    def relative_path_only(cls, value: str) -> str:
        """Prevent callers from selecting an absolute host path."""

        if Path(value).is_absolute():
            raise ValueError("path must be relative to a configured upload root")
        return value


class FileUploadExecuteInput(_FileUploadInput):
    """The sole input accepted by the upload executor."""

    confirmation_ticket: str = Field(min_length=1)

    @field_validator("confirmation_ticket")
    @classmethod
    def non_blank_ticket(cls, value: str) -> str:
        """Keep whitespace-only opaque ticket values out of store lookups."""

        if not value.strip():
            raise ValueError("confirmation_ticket must not be blank")
        return value


class FileUploadPreviewSuccess(BaseModel):
    """Safe preview metadata for a pending binary file upload."""

    model_config = ConfigDict(extra="forbid")

    summary: str = Field(min_length=1)
    canonical_request: dict[str, JsonValue]
    expected_effect_state: dict[str, JsonValue]
    confirmation_ticket: str = Field(min_length=1)
    expires_at: datetime

    @field_validator("expires_at")
    @classmethod
    def utc_expiry(cls, value: datetime) -> datetime:
        """Expose ticket expiry with an unambiguous UTC timezone."""

        if value.tzinfo is None:
            raise ValueError("expires_at must be timezone-aware")
        return value.astimezone(UTC)


class FileUploadRecord(BaseModel):
    """Opaque Billy file or attachment data with recursive secret redaction."""

    model_config = ConfigDict(extra="allow")


class FileUploadExecuteSuccess(BaseModel):
    """Mapped documented response roots from a successful binary upload."""

    model_config = ConfigDict(extra="forbid")

    files: list[FileUploadRecord]
    attachments: list[FileUploadRecord] | None = None


@dataclass(frozen=True)
class _FileIdentity:
    """The exact file attributes that must survive preview to execution."""

    path: Path
    digest: str
    size: int
    mtime_ns: int


@dataclass(frozen=True)
class _PreparedUpload:
    """Volatile upload metadata retained without the file bytes."""

    identity: _FileIdentity
    filename: str
    content_type: str
    create_attachment: bool
    create_variants: bool
    organization_id: str | None
    should_scan: bool
    expires_at: datetime
    binding: ConfirmationBinding


class FileUploadService:
    """Preview and execute the one documented raw-binary Billy upload operation."""

    def __init__(
        self,
        client: BillyHttpClient,
        configuration: AppConfig,
        confirmations: ConfirmationStore,
    ) -> None:
        self._client = client
        self._configuration = configuration
        self._confirmations = confirmations
        self._prepared_by_ticket: dict[str, _PreparedUpload] = {}
        self._prepared_lock = threading.Lock()

    def preview(self, input: FileUploadPreviewInput) -> FileUploadPreviewSuccess | ToolError:
        """Validate and bind one local file without issuing an HTTP request."""

        identity_or_error = _resolve_file_identity(
            input.path, self._configuration.allowed_upload_roots
        )
        if isinstance(identity_or_error, ToolError):
            return identity_or_error
        identity = identity_or_error
        organization_id = input.organization_id or self._configuration.selected_organization
        canonical_request = _canonical_request(input, identity, organization_id)
        expected_effect_state: dict[str, JsonValue] = {
            "action": "upload",
            "resource": "file",
            "create_attachment": input.create_attachment,
            "create_variants": input.create_variants,
        }
        binding = ConfirmationBinding(
            tool=_EXECUTE_TOOL_NAME,
            organization_id=organization_id,
            target=None,
            request=canonical_request,
            expected_effect_state=expected_effect_state,
            file_path=identity.path,
            file_digest=identity.digest,
            destination_url=None,
        )
        issued = self._confirmations.issue(binding)
        prepared = _PreparedUpload(
            identity=identity,
            filename=input.filename,
            content_type=input.content_type,
            create_attachment=input.create_attachment,
            create_variants=input.create_variants,
            organization_id=organization_id,
            should_scan=input.should_scan,
            expires_at=issued.expires_at,
            binding=binding,
        )
        with self._prepared_lock:
            self._prune_prepared(self._confirmations.current_time())
            self._prepared_by_ticket[issued.value] = prepared
        return FileUploadPreviewSuccess(
            summary="Upload one approved local file to Billy.",
            canonical_request=canonical_request,
            expected_effect_state=expected_effect_state,
            confirmation_ticket=issued.value,
            expires_at=issued.expires_at,
        )

    def execute(
        self,
        input: FileUploadExecuteInput,
        *,
        execute_tool_name: str,
    ) -> FileUploadExecuteSuccess | ToolError:
        """Consume, revalidate, and upload only the exact previewed file once."""

        ticket = input.confirmation_ticket
        now = self._confirmations.current_time()
        with self._prepared_lock:
            self._prune_prepared(now, preserve_ticket=ticket)
            prepared = self._prepared_by_ticket.get(ticket)
        if prepared is None:
            terminal_error = self._confirmations.terminal_failure(ticket)
            if terminal_error is not None:
                return terminal_error
            return _invalid_ticket()
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

        current_or_error = _identity_beneath_roots(
            prepared.identity.path, self._configuration.allowed_upload_roots
        )
        if isinstance(current_or_error, ToolError):
            return current_or_error
        if current_or_error != prepared.identity:
            return ToolError(
                code=StableErrorCode.FILE_CHANGED,
                message="File changed after preview; create a new preview before upload.",
            )
        descriptor_or_error = _open_file_descriptor_beneath_roots(
            prepared.identity, self._configuration.allowed_upload_roots
        )
        if isinstance(descriptor_or_error, ToolError):
            return descriptor_or_error
        try:
            with os.fdopen(descriptor_or_error, "rb") as source:
                file_bytes = source.read()
        except OSError:
            return ToolError(
                code=StableErrorCode.FILE_CHANGED,
                message="File changed before upload; create a new preview before upload.",
            )
        if hashlib.sha256(file_bytes).hexdigest() != prepared.identity.digest:
            return ToolError(
                code=StableErrorCode.FILE_CHANGED,
                message="File changed after preview; create a new preview before upload.",
            )
        response = self._client.post_file(
            file_bytes=file_bytes,
            filename=prepared.filename,
            content_type=prepared.content_type,
            create_attachment=prepared.create_attachment,
            create_variants=prepared.create_variants,
            organization_id=prepared.organization_id,
            should_scan=prepared.should_scan,
        )
        return _map_upload_response(response)

    def _discard_prepared(self, ticket: str) -> None:
        """Drop metadata after a terminal execution attempt without touching store replay state."""

        with self._prepared_lock:
            self._prepared_by_ticket.pop(ticket, None)

    def _prune_prepared(self, now: datetime, *, preserve_ticket: str | None = None) -> None:
        """Discard expired metadata while allowing the store to report ticket expiry."""

        for ticket, prepared in tuple(self._prepared_by_ticket.items()):
            if ticket != preserve_ticket and now >= prepared.expires_at:
                del self._prepared_by_ticket[ticket]


def register_file_upload_tools(
    server: FastMCP,
    client: BillyHttpClient,
    configuration: AppConfig,
    confirmations: ConfirmationStore,
) -> None:
    """Register exactly the documented preview and execute upload tools."""

    service = FileUploadService(client, configuration, confirmations)

    def api_files_upload_preview(
        path: _ToolText,
        filename: _ToolHeaderText,
        content_type: _ToolHeaderText,
        create_attachment: StrictBool = False,
        create_variants: StrictBool = False,
        organization_id: _ToolOptionalHeaderText = None,
        should_scan: StrictBool = False,
    ) -> FileUploadPreviewSuccess | ToolError:
        """Preview one configured-root local file without uploading it."""

        return service.preview(
            FileUploadPreviewInput(
                path=path,
                filename=filename,
                content_type=content_type,
                create_attachment=create_attachment,
                create_variants=create_variants,
                organization_id=organization_id,
                should_scan=should_scan,
            )
        )

    def api_files_upload_execute(
        confirmation_ticket: _ToolText,
    ) -> FileUploadExecuteSuccess | ToolError:
        """Upload exactly the configured file identity in a preview ticket."""

        return service.execute(
            FileUploadExecuteInput(confirmation_ticket=confirmation_ticket),
            execute_tool_name=_EXECUTE_TOOL_NAME,
        )

    server.tool(
        name="api_files_upload_preview",
        description="Preview one configured-root Billy file upload without HTTP.",
    )(api_files_upload_preview)
    server.tool(
        name=_EXECUTE_TOOL_NAME,
        description="Execute exactly one previewed Billy file upload with its ticket.",
    )(api_files_upload_execute)


def _resolve_file_identity(path_value: str, roots: tuple[Path, ...]) -> _FileIdentity | ToolError:
    """Resolve a caller-relative path only beneath one configured upload root."""

    for root in roots:
        candidate = (root / path_value).resolve(strict=False)
        if candidate.is_relative_to(root):
            return _identity_for_path(candidate)
    return _file_not_allowed()


def _identity_for_path(path: Path) -> _FileIdentity | ToolError:
    """Calculate the regular-file identity without retaining its contents."""

    canonical_path = path.resolve(strict=False)
    try:
        metadata = canonical_path.stat()
    except OSError:
        return _file_not_allowed()
    if not stat.S_ISREG(metadata.st_mode):
        return _file_not_allowed()
    digest = hashlib.sha256()
    try:
        with canonical_path.open("rb") as source:
            while chunk := source.read(_HASH_CHUNK_SIZE):
                digest.update(chunk)
    except OSError:
        return _file_not_allowed()
    return _FileIdentity(
        path=canonical_path,
        digest=digest.hexdigest(),
        size=metadata.st_size,
        mtime_ns=metadata.st_mtime_ns,
    )


def _identity_beneath_roots(path: Path, roots: tuple[Path, ...]) -> _FileIdentity | ToolError:
    """Reject a post-preview symlink escape before opening any resulting file."""

    canonical_path = path.resolve(strict=False)
    if not any(canonical_path.is_relative_to(root) for root in roots):
        return _file_not_allowed()
    return _identity_for_path(canonical_path)


def _open_file_descriptor_beneath_roots(
    identity: _FileIdentity, roots: tuple[Path, ...]
) -> int | ToolError:
    """Open the previewed file once through no-follow configured-root descriptors."""

    for root in roots:
        try:
            relative_path = identity.path.relative_to(root)
        except ValueError:
            continue
        if not relative_path.parts:
            return _file_not_allowed()
        return _open_relative_file_descriptor(root, relative_path, identity)
    return _file_not_allowed()


def _open_relative_file_descriptor(
    root: Path, relative_path: Path, identity: _FileIdentity
) -> int | ToolError:
    """Return one verified descriptor without following a root, directory, or file symlink."""

    directory_descriptor: int | None = None
    file_descriptor: int | None = None
    try:
        directory_descriptor = _open_directory_descriptor(root)
        for component in relative_path.parts[:-1]:
            next_directory_descriptor = _open_directory_descriptor(
                component, dir_fd=directory_descriptor
            )
            _close_descriptor(directory_descriptor)
            directory_descriptor = next_directory_descriptor
        file_descriptor = os.open(
            relative_path.parts[-1],
            os.O_RDONLY | os.O_NOFOLLOW,
            dir_fd=directory_descriptor,
        )
        metadata = os.fstat(file_descriptor)
    except OSError as error:
        if file_descriptor is not None:
            _close_descriptor(file_descriptor)
        if error.errno in {errno.ELOOP, errno.ENOTDIR}:
            return _file_not_allowed()
        return ToolError(
            code=StableErrorCode.FILE_CHANGED,
            message="File changed before upload; create a new preview before upload.",
        )
    finally:
        if directory_descriptor is not None:
            _close_descriptor(directory_descriptor)

    if not stat.S_ISREG(metadata.st_mode):
        _close_descriptor(file_descriptor)
        return _file_not_allowed()
    if metadata.st_size != identity.size or metadata.st_mtime_ns != identity.mtime_ns:
        _close_descriptor(file_descriptor)
        return ToolError(
            code=StableErrorCode.FILE_CHANGED,
            message="File changed after preview; create a new preview before upload.",
        )
    return file_descriptor


def _open_directory_descriptor(path: str | Path, *, dir_fd: int | None = None) -> int:
    """Open and validate one directory without following a symlink."""

    descriptor = os.open(
        path,
        os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW,
        dir_fd=dir_fd,
    )
    try:
        if not stat.S_ISDIR(os.fstat(descriptor).st_mode):
            raise OSError("descriptor is not a directory")
    except OSError:
        _close_descriptor(descriptor)
        raise
    return descriptor


def _close_descriptor(descriptor: int) -> None:
    """Best-effort close for descriptors rejected before ownership transfers to the reader."""

    try:
        os.close(descriptor)
    except OSError:
        pass


def _canonical_request(
    input: FileUploadPreviewInput,
    identity: _FileIdentity,
    organization_id: str | None,
) -> dict[str, JsonValue]:
    """Return JSON-safe ticket data that contains identity but never file bytes."""

    return {
        "filename": input.filename,
        "content_type": input.content_type,
        "create_attachment": input.create_attachment,
        "create_variants": input.create_variants,
        "organization_id": organization_id,
        "should_scan": input.should_scan,
        "file": {
            "path": str(identity.path),
            "sha256": identity.digest,
            "size": identity.size,
            "mtime_ns": identity.mtime_ns,
        },
    }


def _map_upload_response(
    response: BillyResponse | ToolError,
) -> FileUploadExecuteSuccess | ToolError:
    """Map only the documented opaque success roots and redact download URLs."""

    if isinstance(response, ToolError):
        return response
    data = _mapping(response.data)
    if data is None:
        return _invalid_response("files")
    files = _records(data.get("files"))
    if files is None:
        return _invalid_response("files")
    attachments: list[FileUploadRecord] | None = None
    if "attachments" in data:
        attachments = _records(data["attachments"])
        if attachments is None:
            return _invalid_response("attachments")
    return FileUploadExecuteSuccess(files=files, attachments=attachments)


def _mapping(value: object) -> dict[str, object] | None:
    if not isinstance(value, Mapping):
        return None
    mapping = cast(Mapping[object, object], value)
    return {str(key): item for key, item in mapping.items()}


def _records(value: object) -> list[FileUploadRecord] | None:
    if not isinstance(value, list):
        return None
    records: list[FileUploadRecord] = []
    for value_item in cast(list[object], value):
        record = _mapping(value_item)
        if record is None:
            return None
        redacted_record = redact(record)
        if not isinstance(redacted_record, dict):
            return None
        try:
            records.append(FileUploadRecord.model_validate(redacted_record))
        except ValueError:
            return None
    return records


def _file_not_allowed() -> ToolError:
    return ToolError(
        code=StableErrorCode.FILE_NOT_ALLOWED,
        message="File is not an allowed regular file beneath a configured upload root.",
    )


def _invalid_ticket() -> ToolError:
    return ToolError(
        code=StableErrorCode.CONFIRMATION_INVALID,
        message="Confirmation ticket is invalid.",
    )


def _invalid_response(root: str) -> ToolError:
    return ToolError(
        code=StableErrorCode.BILLY_ERROR,
        message="Billy API response did not contain the documented files upload root.",
        details={"expected_root": root},
    )
