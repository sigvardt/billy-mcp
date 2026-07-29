"""Contract tests for ticketed singular Billy attachment JSON write tools."""

from __future__ import annotations

import asyncio
import json
from collections.abc import Callable
from datetime import UTC, datetime, timedelta
from typing import cast

import httpx
import pytest
from fastmcp import FastMCP
from pydantic import ValidationError

from billy_mcp.api.attachment_writes import (
    AttachmentCreatePreviewInput,
    AttachmentDeletePreviewInput,
    AttachmentUpdatePreviewInput,
    register_attachment_write_tools,
)
from billy_mcp.api.write_protocol import (
    WriteExecuteInput,
    WriteMethod,
    WriteOperationSpec,
    WriteProtocolService,
    confirmation_binding_for,
)
from billy_mcp.client import BillyHttpClient
from billy_mcp.confirmations import ConfirmationFailure, ConfirmationStore
from billy_mcp.models import StableErrorCode

MockHandler = Callable[[httpx.Request], httpx.Response]


class Clock:
    """Controllable clock used only by local confirmation-expiry tests."""

    def __init__(self) -> None:
        self.now = datetime(2026, 7, 29, tzinfo=UTC)

    def __call__(self) -> datetime:
        return self.now


def make_server(
    handler: MockHandler,
    *,
    token: str | None = "attachment-write-test-token",
    confirmations: ConfirmationStore | None = None,
) -> tuple[FastMCP, list[httpx.Request]]:
    """Create a fully local FastMCP server with a recording locked client."""

    requests: list[httpx.Request] = []

    def recording_handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return handler(request)

    client = BillyHttpClient(lambda: token, transport=httpx.MockTransport(recording_handler))
    server = FastMCP("attachment-write-contract-test")
    register_attachment_write_tools(
        server,
        client,
        WriteProtocolService(client, confirmations or ConfirmationStore()),
    )
    return server, requests


def call_tool(server: FastMCP, tool_name: str, arguments: dict[str, object]) -> dict[str, object]:
    """Call a typed tool and return its structured payload."""

    result = asyncio.run(server.call_tool(tool_name, arguments))
    structured_content = result.structured_content
    assert isinstance(structured_content, dict)
    payload = structured_content.get("result", structured_content)
    assert isinstance(payload, dict)
    return cast(dict[str, object], payload)


def test_registers_exactly_six_flat_typed_attachment_write_tools() -> None:
    server, _ = make_server(lambda request: httpx.Response(200, json={}))

    by_name = {tool.name: tool for tool in asyncio.run(server.list_tools())}
    expected_properties = {
        "api_attachments_create_preview": {"attachment"},
        "api_attachments_create_execute": {"confirmation_ticket"},
        "api_attachments_update_preview": {"id", "attachment"},
        "api_attachments_update_execute": {"confirmation_ticket"},
        "api_attachments_delete_preview": {"id"},
        "api_attachments_delete_execute": {"confirmation_ticket"},
    }
    assert set(by_name) == set(expected_properties)
    for name, fields in expected_properties.items():
        schema = by_name[name].parameters
        properties = cast(dict[str, dict[str, object]], schema["properties"])
        assert schema["additionalProperties"] is False
        assert set(properties) == fields
        assert "input" not in properties
        for field in fields & {"id", "confirmation_ticket"}:
            assert properties[field]["minLength"] == 1


@pytest.mark.parametrize(
    ("input_model", "payload"),
    [
        (AttachmentCreatePreviewInput, {"attachment": {}, "extra": True}),
        (AttachmentUpdatePreviewInput, {"id": "attachment-1", "attachment": {}, "extra": True}),
        (AttachmentDeletePreviewInput, {"id": "attachment-1", "extra": True}),
        (AttachmentUpdatePreviewInput, {"id": "", "attachment": {}}),
        (AttachmentDeletePreviewInput, {"id": ""}),
        (AttachmentUpdatePreviewInput, {"id": "attachment-1", "attachment": {"id": "other"}}),
        (WriteExecuteInput, {"confirmation_ticket": "ticket", "attachment": {}}),
    ],
)
def test_outer_inputs_forbid_extras_empty_ids_and_mismatched_body_ids(
    input_model: type[AttachmentCreatePreviewInput]
    | type[AttachmentUpdatePreviewInput]
    | type[AttachmentDeletePreviewInput]
    | type[WriteExecuteInput],
    payload: dict[str, object],
) -> None:
    with pytest.raises(ValidationError):
        input_model.model_validate(payload)


def test_opaque_attachment_preserves_unknown_fields_and_matching_inner_id() -> None:
    input = AttachmentUpdatePreviewInput.model_validate(
        {
            "id": "attachment-1",
            "attachment": {"id": "attachment-1", "futureField": {"rank": 2}},
        }
    )

    assert input.attachment["futureField"] == {"rank": 2}


@pytest.mark.parametrize(
    ("tool_name", "arguments", "expected_request", "expected_effect"),
    [
        (
            "api_attachments_create_preview",
            {"attachment": {"unknown": {"rank": 2}}},
            {"attachment": {"unknown": {"rank": 2}}},
            {"action": "create", "resource": "attachment"},
        ),
        (
            "api_attachments_update_preview",
            {"id": "attachment-1", "attachment": {"priority": 2}},
            {"attachment": {"priority": 2}},
            {"action": "update", "resource": "attachment", "id": "attachment-1"},
        ),
        (
            "api_attachments_delete_preview",
            {"id": "attachment-1"},
            {"id": "attachment-1"},
            {"action": "delete", "resource": "attachment", "id": "attachment-1"},
        ),
    ],
)
def test_previews_are_mutation_free_and_bind_exact_attachment_requests(
    tool_name: str,
    arguments: dict[str, object],
    expected_request: dict[str, object],
    expected_effect: dict[str, object],
) -> None:
    server, requests = make_server(
        lambda request: pytest.fail(f"preview made HTTP request: {request.method} {request.url}")
    )

    preview = call_tool(server, tool_name, arguments)

    assert requests == []
    assert preview["canonical_request"] == expected_request
    assert preview["expected_effect_state"] == expected_effect


@pytest.mark.parametrize(
    ("preview_name", "execute_name", "arguments", "response", "method", "path", "body"),
    [
        (
            "api_attachments_create_preview",
            "api_attachments_create_execute",
            {"attachment": {"unrecognised": {"rank": 2}}},
            {"attachments": [{"id": "attachment-1"}], "files": [{"id": "file-1"}]},
            "POST",
            "/v2/attachments",
            {"attachment": {"unrecognised": {"rank": 2}}},
        ),
        (
            "api_attachments_update_preview",
            "api_attachments_update_execute",
            {"id": "attachment /?", "attachment": {"priority": 2}},
            {"attachments": [{"id": "attachment /?", "priority": 2}]},
            "PUT",
            "/v2/attachments/attachment%20%2F%3F",
            {"attachment": {"priority": 2}},
        ),
        (
            "api_attachments_delete_preview",
            "api_attachments_delete_execute",
            {"id": "attachment /?"},
            {"meta": {"deletedRecords": {"attachments": ["attachment /?"]}}},
            "DELETE",
            "/v2/attachments/attachment%20%2F%3F",
            None,
        ),
    ],
)
def test_execute_sends_exact_attachment_cud_shapes_once(
    preview_name: str,
    execute_name: str,
    arguments: dict[str, object],
    response: dict[str, object],
    method: str,
    path: str,
    body: dict[str, object] | None,
) -> None:
    server, requests = make_server(lambda request: httpx.Response(200, json=response))

    preview = call_tool(server, preview_name, arguments)
    execution = call_tool(
        server,
        execute_name,
        {"confirmation_ticket": preview["confirmation_ticket"]},
    )

    assert len(requests) == 1
    request = requests[0]
    assert request.method == method
    assert request.url.raw_path.decode() == path
    if body is None:
        assert request.content == b""
        assert execution == {
            "changed_records": {},
            "deleted_records": {"attachments": ["attachment /?"]},
        }
    else:
        assert json.loads(request.content) == body
        assert execution == {
            "changed_records": {"attachments": response["attachments"]},
            "deleted_records": None,
        }
        assert "files" not in cast(dict[str, object], execution["changed_records"])


@pytest.mark.parametrize(
    "response",
    [
        {"files": [{"id": "file-1"}]},
        {"attachments": {"id": "attachment-1"}},
        {"attachments": [{"id": "attachment-1"}], "meta": {"deletedRecords": {"files": ["x"]}}},
    ],
)
def test_create_rejects_missing_or_malformed_attachment_roots_without_mapping_files(
    response: dict[str, object],
) -> None:
    server, _ = make_server(lambda request: httpx.Response(200, json=response))

    preview = call_tool(server, "api_attachments_create_preview", {"attachment": {"priority": 2}})
    execution = call_tool(
        server,
        "api_attachments_create_execute",
        {"confirmation_ticket": preview["confirmation_ticket"]},
    )

    if "attachments" not in response or not isinstance(response["attachments"], list):
        assert execution["code"] == StableErrorCode.VALIDATION_ERROR
    else:
        assert execution["changed_records"] == {"attachments": [{"id": "attachment-1"}]}
        assert execution["deleted_records"] is None


def test_delete_does_not_invent_absent_attachment_roots_or_deleted_metadata() -> None:
    server, _ = make_server(lambda request: httpx.Response(200, json={"meta": {}}))

    preview = call_tool(server, "api_attachments_delete_preview", {"id": "attachment-1"})
    execution = call_tool(
        server,
        "api_attachments_delete_execute",
        {"confirmation_ticket": preview["confirmation_ticket"]},
    )

    assert execution == {"changed_records": {}, "deleted_records": None}


def test_tampered_expired_replayed_and_wrong_executor_tickets_never_make_extra_writes() -> None:
    clock = Clock()
    server, requests = make_server(
        lambda request: httpx.Response(200, json={"attachments": [{"id": "attachment-1"}]}),
        confirmations=ConfirmationStore(clock),
    )
    preview = call_tool(server, "api_attachments_create_preview", {"attachment": {"priority": 2}})
    ticket = cast(str, preview["confirmation_ticket"])

    tampered = call_tool(
        server,
        "api_attachments_create_execute",
        {"confirmation_ticket": f"{ticket}x"},
    )
    wrong_executor = call_tool(
        server,
        "api_attachments_delete_execute",
        {"confirmation_ticket": ticket},
    )
    assert tampered["code"] == StableErrorCode.CONFIRMATION_INVALID
    assert wrong_executor["code"] == StableErrorCode.CONFIRMATION_MISMATCH
    assert requests == []

    clock.now += timedelta(minutes=6)
    expired = call_tool(
        server,
        "api_attachments_create_execute",
        {"confirmation_ticket": ticket},
    )
    assert expired["code"] == StableErrorCode.CONFIRMATION_EXPIRED
    assert requests == []

    replay_preview = call_tool(
        server,
        "api_attachments_create_preview",
        {"attachment": {"priority": 2}},
    )
    replay_ticket = cast(str, replay_preview["confirmation_ticket"])
    first = call_tool(
        server,
        "api_attachments_create_execute",
        {"confirmation_ticket": replay_ticket},
    )
    replay = call_tool(
        server,
        "api_attachments_create_execute",
        {"confirmation_ticket": replay_ticket},
    )
    assert first["changed_records"] == {"attachments": [{"id": "attachment-1"}]}
    assert replay["code"] == StableErrorCode.CONFIRMATION_CONSUMED
    assert len(requests) == 1


@pytest.mark.parametrize(
    "changes",
    [
        {"execute_tool_name": "api_attachments_other_execute"},
        {"organization_id": "other-organisation"},
        {"resource_id": "other-attachment"},
        {"payload": {"priority": 3}},
        {"expected_effect_state": {"action": "other"}},
    ],
)
def test_attachment_ticket_binding_rejects_executor_organisation_target_payload_and_effect_changes(
    changes: dict[str, object],
) -> None:
    specification = WriteOperationSpec(
        execute_tool_name="api_attachments_update_execute",
        method=WriteMethod.PUT,
        collection_path="/attachments",
        singular_root="attachment",
        plural_root="attachments",
        payload={"priority": 2},
        resource_id="attachment-1",
        organization_id=None,
        summary="Update one Billy attachment.",
        expected_effect_state={"action": "update", "resource": "attachment", "id": "attachment-1"},
    )
    store = ConfirmationStore()
    ticket = store.issue(confirmation_binding_for(specification))

    with pytest.raises(ConfirmationFailure) as failure:
        store.consume(
            ticket.value, confirmation_binding_for(specification.model_copy(update=changes))
        )

    assert failure.value.error.code is StableErrorCode.CONFIRMATION_MISMATCH


@pytest.mark.parametrize(
    ("status", "response", "preview_name", "arguments", "execute_name", "expected_code"),
    [
        (
            401,
            {"errorCode": "AUTHENTICATION_REQUIRED"},
            "api_attachments_create_preview",
            {"attachment": {"priority": 2}},
            "api_attachments_create_execute",
            StableErrorCode.AUTH_REQUIRED,
        ),
        (
            404,
            {"errorCode": "RECORD_NOT_FOUND"},
            "api_attachments_update_preview",
            {"id": "missing", "attachment": {"priority": 2}},
            "api_attachments_update_execute",
            StableErrorCode.NOT_FOUND,
        ),
    ],
)
def test_typed_authentication_and_not_found_errors_propagate(
    status: int,
    response: dict[str, str],
    preview_name: str,
    arguments: dict[str, object],
    execute_name: str,
    expected_code: StableErrorCode,
) -> None:
    server, requests = make_server(lambda request: httpx.Response(status, json=response))
    preview = call_tool(server, preview_name, arguments)
    error = call_tool(
        server,
        execute_name,
        {"confirmation_ticket": preview["confirmation_ticket"]},
    )

    assert error["code"] == expected_code
    assert len(requests) == 1


def test_empty_token_returns_auth_required_without_network_activity() -> None:
    server, requests = make_server(
        lambda request: pytest.fail(f"missing token attempted HTTP request: {request.url}"),
        token="",
    )
    preview = call_tool(server, "api_attachments_create_preview", {"attachment": {"priority": 2}})
    error = call_tool(
        server,
        "api_attachments_create_execute",
        {"confirmation_ticket": preview["confirmation_ticket"]},
    )

    assert error["code"] == StableErrorCode.AUTH_REQUIRED
    assert requests == []


def test_attachment_write_failure_is_not_retried() -> None:
    server, requests = make_server(
        lambda request: httpx.Response(500, json={"errorCode": "INTERNAL_SERVER_ERROR"})
    )
    preview = call_tool(server, "api_attachments_create_preview", {"attachment": {"priority": 2}})
    error = call_tool(
        server,
        "api_attachments_create_execute",
        {"confirmation_ticket": preview["confirmation_ticket"]},
    )

    assert error["code"] == StableErrorCode.BILLY_ERROR
    assert len(requests) == 1
