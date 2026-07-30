"""Offline contract tests for the bounded raw-binary Billy files upload tools."""

from __future__ import annotations

import asyncio
import os
from collections.abc import Callable
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import cast

import httpx
import pytest
from fastmcp import FastMCP
from fastmcp.exceptions import ValidationError as FastMCPValidationError
from pydantic import ValidationError

import billy_mcp.api.file_upload_writes as file_upload_writes
from billy_mcp.api.file_upload_writes import (
    FileUploadExecuteInput,
    FileUploadExecuteSuccess,
    FileUploadPreviewInput,
    FileUploadPreviewSuccess,
    FileUploadService,
    register_file_upload_tools,
)
from billy_mcp.client import BillyHttpClient
from billy_mcp.config import AppConfig
from billy_mcp.confirmations import ConfirmationStore
from billy_mcp.models import StableErrorCode, ToolError

MockHandler = Callable[[httpx.Request], httpx.Response]


class Clock:
    """Controllable clock used only for opaque-ticket expiry tests."""

    def __init__(self) -> None:
        self.now = datetime(2026, 7, 30, tzinfo=UTC)

    def __call__(self) -> datetime:
        return self.now


def make_server(
    root: Path,
    handler: MockHandler,
    *,
    clock: Clock | None = None,
    token: str | None = "upload-contract-test-token",
    organization_id: str | None = "configured-organization",
) -> tuple[FastMCP, list[httpx.Request]]:
    """Create a local typed upload server with a recording transport."""

    requests: list[httpx.Request] = []

    def recording_handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return handler(request)

    client = BillyHttpClient(lambda: token, transport=httpx.MockTransport(recording_handler))
    configuration = AppConfig(
        selected_organization=organization_id,
        allowed_upload_roots=(root,),
    )
    server = FastMCP("file-upload-contract-test")
    register_file_upload_tools(
        server,
        client,
        configuration,
        ConfirmationStore(clock),
    )
    return server, requests


def call_tool(server: FastMCP, tool_name: str, arguments: dict[str, object]) -> dict[str, object]:
    """Call a typed FastMCP tool and return its structured result object."""

    result = asyncio.run(server.call_tool(tool_name, arguments))
    structured_content = result.structured_content
    assert isinstance(structured_content, dict)
    payload = structured_content.get("result", structured_content)
    assert isinstance(payload, dict)
    return cast(dict[str, object], payload)


def preview_arguments(path: str = "safe.txt") -> dict[str, object]:
    """Return the complete innocent preview surface used by local tests."""

    return {
        "path": path,
        "filename": "safe.txt",
        "content_type": "text/plain",
    }


def write_safe_file(root: Path, content: bytes = b"safe local bytes") -> Path:
    """Write an innocuous test file under the configured temporary root."""

    path = root / "safe.txt"
    path.write_bytes(content)
    return path


def test_registers_exactly_two_flat_typed_upload_tools(tmp_path: Path) -> None:
    server, _ = make_server(tmp_path, lambda request: httpx.Response(200, json={"files": []}))

    by_name = {tool.name: tool for tool in asyncio.run(server.list_tools())}

    assert set(by_name) == {"api_files_upload_preview", "api_files_upload_execute"}
    preview_schema = by_name["api_files_upload_preview"].parameters
    preview_properties = cast(dict[str, object], preview_schema["properties"])
    assert preview_schema["additionalProperties"] is False
    assert set(preview_properties) == {
        "path",
        "filename",
        "content_type",
        "create_attachment",
        "create_variants",
        "organization_id",
        "should_scan",
    }
    execute_schema = by_name["api_files_upload_execute"].parameters
    assert execute_schema["additionalProperties"] is False
    assert set(cast(dict[str, object], execute_schema["properties"])) == {"confirmation_ticket"}


@pytest.mark.parametrize(
    "arguments",
    [
        {**preview_arguments(), "create_attachment": "true"},
        {**preview_arguments(), "path": 7},
        {**preview_arguments(), "filename": "safe.txt\r\nX-Injected: value"},
        {**preview_arguments(), "content_type": "text/plain\r\nX-Injected: value"},
        {**preview_arguments(), "organization_id": "org\r\nX-Injected: value"},
        {**preview_arguments(), "unknown": "forbidden"},
    ],
)
def test_registered_preview_rejects_non_strict_or_header_injecting_inputs_before_http(
    tmp_path: Path, arguments: dict[str, object]
) -> None:
    write_safe_file(tmp_path)
    server, requests = make_server(
        tmp_path, lambda request: pytest.fail(f"invalid preview attempted HTTP: {request.url}")
    )

    with pytest.raises(FastMCPValidationError):
        call_tool(server, "api_files_upload_preview", arguments)

    assert requests == []


def test_registered_execute_rejects_non_string_ticket_before_http(tmp_path: Path) -> None:
    server, requests = make_server(
        tmp_path, lambda request: pytest.fail(f"invalid execute attempted HTTP: {request.url}")
    )

    with pytest.raises(FastMCPValidationError):
        call_tool(server, "api_files_upload_execute", {"confirmation_ticket": 7})

    assert requests == []


@pytest.mark.parametrize(
    ("input_model", "payload"),
    [
        (
            FileUploadPreviewInput,
            {**preview_arguments(), "unknown": "forbidden"},
        ),
        (
            FileUploadPreviewInput,
            {**preview_arguments(), "path": "/tmp/foreign.txt"},
        ),
        (
            FileUploadPreviewInput,
            {**preview_arguments(), "path": "   "},
        ),
        (
            FileUploadPreviewInput,
            {**preview_arguments(), "create_attachment": "true"},
        ),
        (
            FileUploadPreviewInput,
            {**preview_arguments(), "filename": "safe.txt\r\nX-Injected: value"},
        ),
        (
            FileUploadPreviewInput,
            {**preview_arguments(), "organization_id": "org\r\nX-Injected: value"},
        ),
        (
            FileUploadExecuteInput,
            {"confirmation_ticket": "ticket", "path": "safe.txt"},
        ),
        (FileUploadExecuteInput, {"confirmation_ticket": "   "}),
    ],
)
def test_upload_input_models_are_strict_and_reject_foreign_absolute_paths(
    input_model: type[FileUploadPreviewInput] | type[FileUploadExecuteInput],
    payload: dict[str, object],
) -> None:
    with pytest.raises(ValidationError):
        input_model.model_validate(payload)


def test_preview_issues_path_digest_size_and_mtime_ticket_without_http(tmp_path: Path) -> None:
    file_path = write_safe_file(tmp_path, b"safe local bytes")
    server, requests = make_server(
        tmp_path, lambda request: pytest.fail(f"preview attempted HTTP: {request.url}")
    )

    preview = call_tool(server, "api_files_upload_preview", preview_arguments())

    request = cast(dict[str, object], preview["canonical_request"])
    file_identity = cast(dict[str, object], request["file"])
    assert request["organization_id"] == "configured-organization"
    assert file_identity["path"] == str(file_path.resolve())
    assert file_identity["size"] == len(b"safe local bytes")
    assert isinstance(file_identity["sha256"], str)
    assert len(file_identity["sha256"]) == 64
    assert isinstance(file_identity["mtime_ns"], int)
    assert "file_bytes" not in request
    assert requests == []


@pytest.mark.parametrize("path", ["missing.txt", "folder", "../outside.txt"])
def test_preview_rejects_missing_nonregular_and_outside_paths_without_http(
    tmp_path: Path, path: str
) -> None:
    (tmp_path / "folder").mkdir()
    outside = tmp_path.parent / "outside.txt"
    outside.write_text("outside", encoding="utf-8")
    server, requests = make_server(
        tmp_path, lambda request: pytest.fail(f"invalid preview attempted HTTP: {request.url}")
    )

    result = call_tool(server, "api_files_upload_preview", preview_arguments(path))

    assert result["code"] == StableErrorCode.FILE_NOT_ALLOWED
    assert requests == []


def test_preview_rejects_symlink_escape_without_http(tmp_path: Path) -> None:
    outside = tmp_path.parent / "outside.txt"
    outside.write_text("outside", encoding="utf-8")
    (tmp_path / "escape.txt").symlink_to(outside)
    server, requests = make_server(
        tmp_path, lambda request: pytest.fail(f"symlink preview attempted HTTP: {request.url}")
    )

    result = call_tool(server, "api_files_upload_preview", preview_arguments("escape.txt"))

    assert result["code"] == StableErrorCode.FILE_NOT_ALLOWED
    assert requests == []


def test_execute_sends_exact_binary_body_headers_and_redacts_download_url(tmp_path: Path) -> None:
    body = b"safe local bytes"
    write_safe_file(tmp_path, body)
    server, requests = make_server(
        tmp_path,
        lambda request: httpx.Response(
            200,
            json={
                "files": [{"id": "file-1", "downloadUrl": "https://download.billy.dk/token"}],
                "attachments": [{"id": "attachment-1"}],
            },
        ),
    )
    arguments = {
        **preview_arguments(),
        "create_attachment": True,
        "create_variants": True,
        "organization_id": "request-organization",
        "should_scan": True,
    }
    preview = call_tool(server, "api_files_upload_preview", arguments)

    execution = call_tool(
        server,
        "api_files_upload_execute",
        {"confirmation_ticket": preview["confirmation_ticket"]},
    )

    assert len(requests) == 1
    request = requests[0]
    assert request.method == "POST"
    assert str(request.url) == "https://api.billysbilling.com/v2/files"
    assert request.content == body
    assert request.headers["x-filename"] == "safe.txt"
    assert request.headers["content-type"] == "text/plain"
    assert request.headers["x-create-attachment"] == "true"
    assert request.headers["x-create-variants"] == "true"
    assert request.headers["x-organizationid"] == "request-organization"
    assert request.headers["x-should-scan"] == "true"
    files = cast(list[dict[str, object]], execution["files"])
    assert files[0]["downloadUrl"] == "[REDACTED]"
    assert execution["attachments"] == [{"id": "attachment-1"}]


def test_execute_omits_optional_headers_and_does_not_retry(tmp_path: Path) -> None:
    write_safe_file(tmp_path)
    server, requests = make_server(
        tmp_path,
        lambda request: httpx.Response(503, json={"errorCode": "TEMPORARY"}),
        organization_id=None,
    )
    preview = call_tool(server, "api_files_upload_preview", preview_arguments())

    result = call_tool(
        server,
        "api_files_upload_execute",
        {"confirmation_ticket": preview["confirmation_ticket"]},
    )

    assert result["code"] == StableErrorCode.BILLY_ERROR
    assert len(requests) == 1
    headers = requests[0].headers
    assert "x-create-attachment" not in headers
    assert "x-create-variants" not in headers
    assert "x-organizationid" not in headers
    assert "x-should-scan" not in headers


@pytest.mark.parametrize("change", ["contents", "size", "mtime", "path"])
def test_execute_rejects_every_bound_file_identity_change(tmp_path: Path, change: str) -> None:
    target = write_safe_file(tmp_path, b"original")
    server, requests = make_server(
        tmp_path, lambda request: pytest.fail(f"changed file attempted HTTP: {request.url}")
    )
    preview = call_tool(server, "api_files_upload_preview", preview_arguments())

    if change == "contents":
        target.write_bytes(b"changed!")
    elif change == "size":
        target.write_bytes(b"a longer changed file")
    elif change == "mtime":
        original = target.stat()
        os.utime(target, ns=(original.st_atime_ns, original.st_mtime_ns + 1_000_000))
    else:
        replacement = tmp_path / "replacement.txt"
        replacement.write_bytes(b"original")
        target.unlink()
        target.symlink_to(replacement.name)

    result = call_tool(
        server,
        "api_files_upload_execute",
        {"confirmation_ticket": preview["confirmation_ticket"]},
    )

    assert result["code"] == StableErrorCode.FILE_CHANGED
    assert requests == []


def test_execute_rejects_changed_bytes_between_identity_check_and_descriptor_open(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    target = write_safe_file(tmp_path, b"original")
    server, requests = make_server(
        tmp_path, lambda request: pytest.fail(f"replaced file attempted HTTP: {request.url}")
    )
    preview = call_tool(server, "api_files_upload_preview", preview_arguments())
    original_open = file_upload_writes.os.open
    replaced = False

    def replace_before_terminal_open(
        path: str | Path,
        flags: int,
        mode: int = 0o777,
        *,
        dir_fd: int | None = None,
    ) -> int:
        nonlocal replaced
        if path == target.name and dir_fd is not None:
            target.write_bytes(b"replacement")
            replaced = True
        return original_open(path, flags, mode, dir_fd=dir_fd)

    monkeypatch.setattr(file_upload_writes.os, "open", replace_before_terminal_open)

    result = call_tool(
        server,
        "api_files_upload_execute",
        {"confirmation_ticket": preview["confirmation_ticket"]},
    )

    assert replaced
    assert result["code"] == StableErrorCode.FILE_CHANGED
    assert requests == []


def test_execute_rejects_same_digest_outside_symlink_between_identity_and_descriptor_open(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    body = b"same digest bytes"
    target = write_safe_file(tmp_path, body)
    outside = tmp_path.parent / f"{tmp_path.name}-outside.txt"
    outside.write_bytes(body)
    server, requests = make_server(
        tmp_path, lambda request: pytest.fail(f"symlink escape attempted HTTP: {request.url}")
    )
    preview = call_tool(server, "api_files_upload_preview", preview_arguments())
    original_open = file_upload_writes.os.open
    replaced = False

    def replace_before_terminal_open(
        path: str | Path,
        flags: int,
        mode: int = 0o777,
        *,
        dir_fd: int | None = None,
    ) -> int:
        nonlocal replaced
        if path == target.name and dir_fd is not None:
            target.unlink()
            target.symlink_to(outside)
            replaced = True
        return original_open(path, flags, mode, dir_fd=dir_fd)

    monkeypatch.setattr(file_upload_writes.os, "open", replace_before_terminal_open)

    result = call_tool(
        server,
        "api_files_upload_execute",
        {"confirmation_ticket": preview["confirmation_ticket"]},
    )

    assert replaced
    assert result["code"] == StableErrorCode.FILE_NOT_ALLOWED
    assert requests == []


def test_execute_rejects_intermediate_symlink_race_before_descriptor_open(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    body = b"same digest bytes"
    nested = tmp_path / "nested"
    nested.mkdir()
    target = nested / "safe.txt"
    target.write_bytes(body)
    outside_directory = tmp_path.parent / f"{tmp_path.name}-outside"
    outside_directory.mkdir()
    (outside_directory / target.name).write_bytes(body)
    server, requests = make_server(
        tmp_path, lambda request: pytest.fail(f"intermediate symlink attempted HTTP: {request.url}")
    )
    preview = call_tool(server, "api_files_upload_preview", preview_arguments("nested/safe.txt"))
    original_open = file_upload_writes.os.open
    replaced = False

    def replace_before_directory_open(
        path: str | Path,
        flags: int,
        mode: int = 0o777,
        *,
        dir_fd: int | None = None,
    ) -> int:
        nonlocal replaced
        if path == nested.name and dir_fd is not None:
            target.unlink()
            nested.rmdir()
            nested.symlink_to(outside_directory, target_is_directory=True)
            replaced = True
        return original_open(path, flags, mode, dir_fd=dir_fd)

    monkeypatch.setattr(file_upload_writes.os, "open", replace_before_directory_open)

    result = call_tool(
        server,
        "api_files_upload_execute",
        {"confirmation_ticket": preview["confirmation_ticket"]},
    )

    assert replaced
    assert result["code"] == StableErrorCode.FILE_NOT_ALLOWED
    assert requests == []


def test_execute_reports_nonregular_replacement_as_not_allowed(tmp_path: Path) -> None:
    target = write_safe_file(tmp_path)
    server, requests = make_server(
        tmp_path, lambda request: pytest.fail(f"invalid replacement attempted HTTP: {request.url}")
    )
    preview = call_tool(server, "api_files_upload_preview", preview_arguments())
    target.unlink()
    target.mkdir()

    result = call_tool(
        server,
        "api_files_upload_execute",
        {"confirmation_ticket": preview["confirmation_ticket"]},
    )

    assert result["code"] == StableErrorCode.FILE_NOT_ALLOWED
    assert requests == []


def test_execute_rejects_post_preview_symlink_escape_before_reading(tmp_path: Path) -> None:
    target = write_safe_file(tmp_path)
    outside = tmp_path.parent / "outside.txt"
    outside.write_text("outside", encoding="utf-8")
    server, requests = make_server(
        tmp_path, lambda request: pytest.fail(f"symlink escape attempted HTTP: {request.url}")
    )
    preview = call_tool(server, "api_files_upload_preview", preview_arguments())
    target.unlink()
    target.symlink_to(outside)

    result = call_tool(
        server,
        "api_files_upload_execute",
        {"confirmation_ticket": preview["confirmation_ticket"]},
    )

    assert result["code"] == StableErrorCode.FILE_NOT_ALLOWED
    assert requests == []


def test_ticket_expiry_replay_tampering_and_cross_executor_never_write(tmp_path: Path) -> None:
    write_safe_file(tmp_path)
    clock = Clock()
    server, requests = make_server(
        tmp_path,
        lambda request: httpx.Response(200, json={"files": [{"id": "file-1"}]}),
        clock=clock,
    )
    preview = call_tool(server, "api_files_upload_preview", preview_arguments())
    ticket = cast(str, preview["confirmation_ticket"])

    tampered = call_tool(
        server,
        "api_files_upload_execute",
        {"confirmation_ticket": f"{ticket}x"},
    )
    assert tampered["code"] == StableErrorCode.CONFIRMATION_INVALID
    assert requests == []

    clock.now += timedelta(minutes=6)
    expired = call_tool(
        server,
        "api_files_upload_execute",
        {"confirmation_ticket": ticket},
    )
    assert expired["code"] == StableErrorCode.CONFIRMATION_EXPIRED
    assert requests == []

    clock.now -= timedelta(minutes=6)
    replay_preview = call_tool(server, "api_files_upload_preview", preview_arguments())
    replay_ticket = cast(str, replay_preview["confirmation_ticket"])
    first = call_tool(
        server,
        "api_files_upload_execute",
        {"confirmation_ticket": replay_ticket},
    )
    replay = call_tool(
        server,
        "api_files_upload_execute",
        {"confirmation_ticket": replay_ticket},
    )
    assert first["files"] == [{"id": "file-1"}]
    assert replay["code"] == StableErrorCode.CONFIRMATION_CONSUMED
    assert len(requests) == 1


def test_service_rejects_wrong_executor_without_consuming_ticket(tmp_path: Path) -> None:
    write_safe_file(tmp_path)
    requests: list[httpx.Request] = []
    client = BillyHttpClient(
        lambda: "token",
        transport=httpx.MockTransport(
            lambda request: requests.append(request) or httpx.Response(200, json={"files": []})
        ),
    )
    service = FileUploadService(
        client,
        AppConfig(allowed_upload_roots=(tmp_path,)),
        ConfirmationStore(),
    )
    preview = service.preview(FileUploadPreviewInput.model_validate(preview_arguments()))
    assert isinstance(preview, FileUploadPreviewSuccess)
    ticket = preview.confirmation_ticket

    mismatch = service.execute(
        FileUploadExecuteInput(confirmation_ticket=ticket),
        execute_tool_name="api_other_execute",
    )
    assert isinstance(mismatch, ToolError)
    assert mismatch.code is StableErrorCode.CONFIRMATION_MISMATCH
    assert requests == []

    success = service.execute(
        FileUploadExecuteInput(confirmation_ticket=ticket),
        execute_tool_name="api_files_upload_execute",
    )
    assert isinstance(success, FileUploadExecuteSuccess)
    assert success.files == []
    assert len(requests) == 1


@pytest.mark.parametrize(
    "response",
    [
        {},
        {"files": {"id": "file-1"}},
        {"files": ["not-an-object"]},
        {"files": [], "attachments": {"id": "attachment-1"}},
    ],
)
def test_execute_rejects_malformed_success_roots(
    tmp_path: Path, response: dict[str, object]
) -> None:
    write_safe_file(tmp_path)
    server, requests = make_server(tmp_path, lambda request: httpx.Response(200, json=response))
    preview = call_tool(server, "api_files_upload_preview", preview_arguments())

    result = call_tool(
        server,
        "api_files_upload_execute",
        {"confirmation_ticket": preview["confirmation_ticket"]},
    )

    assert result["code"] == StableErrorCode.BILLY_ERROR
    assert len(requests) == 1
