"""Ticketed UI file create tools. Preview binds path and digest; execute submits once."""

from __future__ import annotations

import hashlib
import stat
from dataclasses import dataclass
from pathlib import Path
from typing import Annotated, Protocol

from fastmcp import FastMCP
from pydantic import BaseModel, ConfigDict, Field, JsonValue, StrictStr, field_validator

from billy_mcp.config import AppConfig
from billy_mcp.models import StableErrorCode, ToolError
from billy_mcp.ui_writes.protocol import (
    UiWriteExecuteInput,
    UiWritePreviewResult,
    UiWriteProtocol,
)

_EXECUTE_TOOL_NAME = "ui_files_create_execute"
_HASH_CHUNK_SIZE = 64 * 1024
_ToolText = Annotated[StrictStr, Field(min_length=1)]
_ToolOptionalText = Annotated[StrictStr | None, Field(min_length=1)]


class UiFilesCreatePreviewInput(BaseModel):
    """Inputs that bind one local file without touching Billy."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    path: str = Field(min_length=1)
    filename: str = Field(min_length=1)
    organization_id: str | None = Field(default=None, min_length=1)

    @field_validator("path", "filename", "organization_id")
    @classmethod
    def non_blank(cls, value: str | None) -> str | None:
        if value is not None and not value.strip():
            raise ValueError("value must not be blank")
        return value


class UiFilesCreateExecuteSuccess(BaseModel):
    """Non-sensitive result of one UI file create execute."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    filename: str = Field(min_length=1)
    row_id: str | None = None
    deleted: bool = False


@dataclass(frozen=True, slots=True)
class _FileIdentity:
    """Exact local file attributes bound on preview and re-checked on execute."""

    path: Path
    digest: str
    size: int


class UiFileSubmitter(Protocol):
    """Submit the previewed file through the Billy interface, never the HTTP API."""

    def submit(
        self,
        *,
        filename: str,
        path: Path,
        digest: str,
        size: int,
        organization_id: str | None,
    ) -> UiFilesCreateExecuteSuccess | ToolError: ...


class _UnconfiguredUiFileSubmitter:
    """Fail closed when the process has no UI submitter (offline or held live)."""

    def submit(
        self,
        *,
        filename: str,
        path: Path,
        digest: str,
        size: int,
        organization_id: str | None,
    ) -> ToolError:
        del filename, path, digest, size, organization_id
        return ToolError(
            code=StableErrorCode.PLAN_UNAVAILABLE,
            message="UI file create submit is not configured for this process.",
        )


class UiFileWriteService:
    """Issue and consume UI file-create tickets, then submit only the bound file."""

    def __init__(
        self,
        protocol: UiWriteProtocol,
        submitter: UiFileSubmitter,
        upload_roots: tuple[Path, ...],
    ) -> None:
        self._protocol = protocol
        self._submitter = submitter
        self._upload_roots = tuple(root.expanduser().resolve(strict=False) for root in upload_roots)

    def preview(self, input: UiFilesCreatePreviewInput) -> UiWritePreviewResult | ToolError:
        """Bind the resolved path and digest. Does not submit."""

        identity = _resolve_identity(input.path, self._upload_roots)
        if isinstance(identity, ToolError):
            return identity
        canonical_request: dict[str, JsonValue] = {
            "filename": input.filename,
            "organization_id": input.organization_id,
            "file": {
                "path": str(identity.path),
                "sha256": identity.digest,
                "size": identity.size,
            },
        }
        expected_effect_state: dict[str, JsonValue] = {"action": "create", "resource": "file"}
        return self._protocol.preview(
            execute_tool_name=_EXECUTE_TOOL_NAME,
            organization_id=input.organization_id,
            target="files",
            canonical_request=canonical_request,
            expected_effect_state=expected_effect_state,
            summary="Create one Billy file in the interface.",
            file_path=identity.path,
            file_digest=identity.digest,
        )

    def execute(self, input: UiWriteExecuteInput) -> UiFilesCreateExecuteSuccess | ToolError:
        """Consume the ticket, reject a changed file, then submit once."""

        prepared = self._protocol.consume(input, execute_tool_name=_EXECUTE_TOOL_NAME)
        if isinstance(prepared, ToolError):
            return prepared
        bound_path = prepared.binding.file_path
        bound_digest = prepared.binding.file_digest
        if bound_path is None or bound_digest is None:
            return _file_changed()
        current = _resolve_identity(str(bound_path), self._upload_roots)
        if isinstance(current, ToolError):
            return _file_changed()
        if current.path != bound_path or current.digest != bound_digest:
            return _file_changed()
        filename = str(prepared.canonical_request.get("filename") or "")
        if not filename:
            return _file_changed()
        return self._submitter.submit(
            filename=filename,
            path=current.path,
            digest=current.digest,
            size=current.size,
            organization_id=prepared.binding.organization_id,
        )


def register_ui_file_write_tools(
    server: FastMCP,
    protocol: UiWriteProtocol,
    submitter: UiFileSubmitter | None = None,
    upload_roots: tuple[Path, ...] | None = None,
) -> None:
    """Register ui_files_create_preview and ui_files_create_execute."""

    roots = (
        upload_roots
        if upload_roots is not None
        else AppConfig.from_environment().allowed_upload_roots
    )
    service = UiFileWriteService(
        protocol,
        submitter if submitter is not None else _UnconfiguredUiFileSubmitter(),
        roots,
    )

    def ui_files_create_preview(
        path: _ToolText,
        filename: _ToolText,
        organization_id: _ToolOptionalText = None,
    ) -> UiWritePreviewResult | ToolError:
        """Preview one local file upload in the Billy interface without submitting."""

        return service.preview(
            UiFilesCreatePreviewInput(path=path, filename=filename, organization_id=organization_id)
        )

    def ui_files_create_execute(
        confirmation_ticket: _ToolText,
    ) -> UiFilesCreateExecuteSuccess | ToolError:
        """Execute exactly the previewed UI file create with its ticket."""

        return service.execute(UiWriteExecuteInput(confirmation_ticket=confirmation_ticket))

    server.tool(
        name="ui_files_create_preview",
        description="Preview one local Billy UI file create. Binds path and digest. No submit.",
    )(ui_files_create_preview)
    server.tool(
        name=_EXECUTE_TOOL_NAME,
        description="Execute exactly one previewed Billy UI file create with its ticket.",
    )(ui_files_create_execute)


def _resolve_identity(path_value: str, roots: tuple[Path, ...]) -> _FileIdentity | ToolError:
    """Resolve a regular file under a configured root and hash it without keeping bytes."""

    if not roots:
        return _file_not_allowed()
    raw = Path(path_value).expanduser()
    resolved: Path | None = None
    if raw.is_absolute():
        candidate = raw.resolve(strict=False)
        if any(candidate.is_relative_to(root) for root in roots):
            resolved = candidate
    else:
        for root in roots:
            candidate = (root / raw).resolve(strict=False)
            if candidate.is_relative_to(root):
                resolved = candidate
                break
    if resolved is None:
        return _file_not_allowed()
    try:
        metadata = resolved.stat()
    except OSError:
        return _file_not_allowed()
    if not stat.S_ISREG(metadata.st_mode):
        return _file_not_allowed()
    digest = hashlib.sha256()
    try:
        with resolved.open("rb") as source:
            while chunk := source.read(_HASH_CHUNK_SIZE):
                digest.update(chunk)
    except OSError:
        return _file_not_allowed()
    return _FileIdentity(path=resolved, digest=digest.hexdigest(), size=metadata.st_size)


def _file_not_allowed() -> ToolError:
    return ToolError(
        code=StableErrorCode.FILE_NOT_ALLOWED,
        message="File is not an allowed regular file beneath a configured upload root.",
    )


def _file_changed() -> ToolError:
    return ToolError(
        code=StableErrorCode.FILE_CHANGED,
        message="File changed after preview; create a new preview before submit.",
    )
