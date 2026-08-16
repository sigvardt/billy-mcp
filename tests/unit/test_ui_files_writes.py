"""Offline FastMCP ticket tests for UI files create preview and execute."""

from __future__ import annotations

import asyncio
import hashlib
from datetime import UTC, datetime, timedelta
from pathlib import Path

from fastmcp import FastMCP

from billy_mcp.confirmations import MAX_TICKET_TTL, ConfirmationStore
from billy_mcp.models import StableErrorCode
from billy_mcp.ui_writes.files import (
    UiFilesCreateExecuteSuccess,
    register_ui_file_write_tools,
)
from billy_mcp.ui_writes.protocol import UiWriteProtocol


class Clock:
    """Controllable clock used only by local confirmation-expiry tests."""

    def __init__(self) -> None:
        self.now = datetime(2026, 8, 16, tzinfo=UTC)

    def __call__(self) -> datetime:
        return self.now


class RecordingSubmitter:
    """In-memory UI submitter. Records calls and never opens a browser."""

    def __init__(self) -> None:
        self.calls: list[tuple[str, str, int]] = []

    def submit(
        self,
        *,
        filename: str,
        path: Path,
        digest: str,
        size: int,
        organization_id: str | None,
    ) -> UiFilesCreateExecuteSuccess:
        del organization_id
        self.calls.append((filename, digest, size))
        return UiFilesCreateExecuteSuccess(filename=filename, deleted=False)


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _write_fixture(
    root: Path, name: str = "safe.txt", content: bytes = b"safe local bytes"
) -> Path:
    path = root / name
    path.write_bytes(content)
    return path


def make_server(
    root: Path,
    *,
    clock: Clock | None = None,
    submitter: RecordingSubmitter | None = None,
) -> tuple[FastMCP, UiWriteProtocol, RecordingSubmitter]:
    recorder = submitter or RecordingSubmitter()
    protocol = UiWriteProtocol(ConfirmationStore(clock=clock or Clock()))
    server = FastMCP("ui-files-write-contract-test")
    register_ui_file_write_tools(
        server,
        protocol,
        submitter=recorder,
        upload_roots=(root.resolve(),),
    )
    return server, protocol, recorder


def call_tool(server: FastMCP, tool_name: str, arguments: dict[str, object]) -> dict[str, object]:
    result = asyncio.run(server.call_tool(tool_name, arguments))
    structured_content = result.structured_content
    assert isinstance(structured_content, dict)
    payload = structured_content.get("result", structured_content)
    assert isinstance(payload, dict)
    return payload


def preview_arguments(
    path: str = "safe.txt",
    filename: str = "MCP-TEST-ui-files-safe.txt",
) -> dict[str, object]:
    return {"path": path, "filename": filename}


def test_registers_exactly_two_flat_typed_ui_file_write_tools(tmp_path: Path) -> None:
    server, _, _ = make_server(tmp_path)

    by_name = {tool.name: tool for tool in asyncio.run(server.list_tools())}

    assert set(by_name) == {"ui_files_create_preview", "ui_files_create_execute"}
    preview_schema = by_name["ui_files_create_preview"].parameters
    assert preview_schema["additionalProperties"] is False
    assert set(preview_schema["properties"]) == {"path", "filename", "organization_id"}
    execute_schema = by_name["ui_files_create_execute"].parameters
    assert execute_schema["additionalProperties"] is False
    assert set(execute_schema["properties"]) == {"confirmation_ticket"}


def test_preview_binds_resolved_path_and_digest_without_submit(tmp_path: Path) -> None:
    content = b"safe local bytes"
    file_path = _write_fixture(tmp_path, content=content)
    server, _, recorder = make_server(tmp_path)

    preview = call_tool(server, "ui_files_create_preview", preview_arguments())

    request = preview["canonical_request"]
    assert isinstance(request, dict)
    file_identity = request["file"]
    assert isinstance(file_identity, dict)
    assert file_identity["path"] == str(file_path.resolve())
    assert file_identity["sha256"] == _sha256(content)
    assert file_identity["size"] == len(content)
    assert request["filename"] == "MCP-TEST-ui-files-safe.txt"
    assert "file_bytes" not in request
    assert preview["confirmation_ticket"]
    assert recorder.calls == []


def test_execute_submits_once_then_replay_is_consumed(tmp_path: Path) -> None:
    content = b"safe local bytes"
    _write_fixture(tmp_path, content=content)
    server, _, recorder = make_server(tmp_path)
    preview = call_tool(server, "ui_files_create_preview", preview_arguments())

    first = call_tool(
        server,
        "ui_files_create_execute",
        {"confirmation_ticket": preview["confirmation_ticket"]},
    )
    replay = call_tool(
        server,
        "ui_files_create_execute",
        {"confirmation_ticket": preview["confirmation_ticket"]},
    )

    assert first["filename"] == "MCP-TEST-ui-files-safe.txt"
    assert first["deleted"] is False
    assert recorder.calls == [("MCP-TEST-ui-files-safe.txt", _sha256(content), len(content))]
    assert replay["code"] == StableErrorCode.CONFIRMATION_CONSUMED
    assert recorder.calls == [("MCP-TEST-ui-files-safe.txt", _sha256(content), len(content))]


def test_execute_rejects_expired_ticket_without_submit(tmp_path: Path) -> None:
    _write_fixture(tmp_path)
    clock = Clock()
    server, _, recorder = make_server(tmp_path, clock=clock)
    preview = call_tool(server, "ui_files_create_preview", preview_arguments())
    clock.now = clock.now + MAX_TICKET_TTL + timedelta(seconds=1)

    expired = call_tool(
        server,
        "ui_files_create_execute",
        {"confirmation_ticket": preview["confirmation_ticket"]},
    )

    assert expired["code"] == StableErrorCode.CONFIRMATION_EXPIRED
    assert recorder.calls == []


def test_execute_rejects_wrong_tool_ticket_without_submit(tmp_path: Path) -> None:
    _write_fixture(tmp_path)
    server, protocol, recorder = make_server(tmp_path)
    foreign = protocol.preview(
        execute_tool_name="ui_clients_create_execute",
        organization_id=None,
        target="files",
        canonical_request={"filename": "foreign.txt"},
        expected_effect_state={"action": "create"},
        summary="Foreign ticket for mismatch.",
    )

    mismatch = call_tool(
        server,
        "ui_files_create_execute",
        {"confirmation_ticket": foreign.confirmation_ticket},
    )

    assert mismatch["code"] == StableErrorCode.CONFIRMATION_MISMATCH
    assert recorder.calls == []


def test_execute_rejects_changed_digest_without_submit(tmp_path: Path) -> None:
    target = _write_fixture(tmp_path, content=b"original")
    server, _, recorder = make_server(tmp_path)
    preview = call_tool(server, "ui_files_create_preview", preview_arguments())
    target.write_bytes(b"changed-bytes")

    changed = call_tool(
        server,
        "ui_files_create_execute",
        {"confirmation_ticket": preview["confirmation_ticket"]},
    )

    assert changed["code"] == StableErrorCode.FILE_CHANGED
    assert recorder.calls == []


def test_preview_rejects_missing_and_outside_paths_without_submit(tmp_path: Path) -> None:
    outside = tmp_path.parent / "outside.txt"
    outside.write_bytes(b"outside")
    server, _, recorder = make_server(tmp_path)

    missing = call_tool(server, "ui_files_create_preview", preview_arguments("missing.txt"))
    foreign = call_tool(
        server,
        "ui_files_create_preview",
        preview_arguments(str(outside.resolve())),
    )

    assert missing["code"] == StableErrorCode.FILE_NOT_ALLOWED
    assert foreign["code"] == StableErrorCode.FILE_NOT_ALLOWED
    assert recorder.calls == []


def test_default_submitter_is_fail_closed_and_does_not_submit(tmp_path: Path) -> None:
    _write_fixture(tmp_path)
    protocol = UiWriteProtocol(ConfirmationStore(clock=Clock()))
    server = FastMCP("ui-files-default-submitter-test")
    register_ui_file_write_tools(server, protocol, upload_roots=(tmp_path.resolve(),))
    preview = call_tool(server, "ui_files_create_preview", preview_arguments())

    held = call_tool(
        server,
        "ui_files_create_execute",
        {"confirmation_ticket": preview["confirmation_ticket"]},
    )

    assert held["code"] == StableErrorCode.PLAN_UNAVAILABLE


def test_execute_rejects_changed_path_without_submit(tmp_path: Path) -> None:
    target = _write_fixture(tmp_path, content=b"original")
    server, _, recorder = make_server(tmp_path)
    preview = call_tool(server, "ui_files_create_preview", preview_arguments())
    target.unlink()
    replacement = tmp_path / "other.txt"
    replacement.write_bytes(b"original")
    target.symlink_to(replacement.name)

    changed = call_tool(
        server,
        "ui_files_create_execute",
        {"confirmation_ticket": preview["confirmation_ticket"]},
    )

    assert changed["code"] == StableErrorCode.FILE_CHANGED
    assert recorder.calls == []
