"""Contract tests for ticketed bank-line match, line, and association writes."""

from __future__ import annotations

import asyncio
import json
from collections.abc import Callable
from datetime import UTC, datetime, timedelta
from typing import cast

import httpx
import pytest
from fastmcp import FastMCP
from pydantic import BaseModel, ValidationError

from billy_mcp.api.bank_line_writes import (
    BankLineCreatePreviewInput,
    BankLineDeletePreviewInput,
    BankLineMatchCreatePreviewInput,
    BankLineMatchDeletePreviewInput,
    BankLineMatchUpdatePreviewInput,
    BankLineSubjectAssociationCreatePreviewInput,
    BankLineSubjectAssociationDeletePreviewInput,
    BankLineSubjectAssociationUpdatePreviewInput,
    BankLineUpdatePreviewInput,
    register_bank_line_write_tools,
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
    """Controllable UTC clock for deterministic ticket-expiry tests."""

    def __init__(self) -> None:
        self.now = datetime(2026, 7, 30, tzinfo=UTC)

    def __call__(self) -> datetime:
        return self.now


def make_server(
    handler: MockHandler,
    *,
    token: str | None = "bank-line-write-test-token",
    confirmations: ConfirmationStore | None = None,
) -> tuple[FastMCP, list[httpx.Request]]:
    """Create a local server with the production client base and a recording transport."""

    requests: list[httpx.Request] = []

    def recording_handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return handler(request)

    client = BillyHttpClient(
        lambda: token,
        transport=httpx.MockTransport(recording_handler),
    )
    server = FastMCP("bank-line-write-contract-test")
    register_bank_line_write_tools(
        server,
        client,
        WriteProtocolService(client, confirmations or ConfirmationStore()),
    )
    return server, requests


def call_tool(server: FastMCP, tool_name: str, arguments: dict[str, object]) -> dict[str, object]:
    """Call one typed tool with its direct MCP argument object."""

    result = asyncio.run(server.call_tool(tool_name, arguments))
    structured_content = result.structured_content
    assert isinstance(structured_content, dict)
    payload = structured_content.get("result", structured_content)
    assert isinstance(payload, dict)
    return cast(dict[str, object], payload)


def test_registers_exactly_eighteen_flat_typed_bank_line_write_tools() -> None:
    server, _ = make_server(lambda request: httpx.Response(200, json={}))

    by_name = {tool.name: tool for tool in asyncio.run(server.list_tools())}
    expected_properties = {
        "api_bank_line_matches_create_preview": {"bankLineMatch"},
        "api_bank_line_matches_create_execute": {"confirmation_ticket"},
        "api_bank_line_matches_update_preview": {"id", "bankLineMatch"},
        "api_bank_line_matches_update_execute": {"confirmation_ticket"},
        "api_bank_line_matches_delete_preview": {"id"},
        "api_bank_line_matches_delete_execute": {"confirmation_ticket"},
        "api_bank_lines_create_preview": {"bankLine"},
        "api_bank_lines_create_execute": {"confirmation_ticket"},
        "api_bank_lines_update_preview": {"id", "bankLine"},
        "api_bank_lines_update_execute": {"confirmation_ticket"},
        "api_bank_lines_delete_preview": {"id"},
        "api_bank_lines_delete_execute": {"confirmation_ticket"},
        "api_bank_line_subject_associations_create_preview": {"bankLineSubjectAssociation"},
        "api_bank_line_subject_associations_create_execute": {"confirmation_ticket"},
        "api_bank_line_subject_associations_update_preview": {
            "id",
            "bankLineSubjectAssociation",
        },
        "api_bank_line_subject_associations_update_execute": {"confirmation_ticket"},
        "api_bank_line_subject_associations_delete_preview": {"id"},
        "api_bank_line_subject_associations_delete_execute": {"confirmation_ticket"},
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
        (BankLineMatchCreatePreviewInput, {"bankLineMatch": {}, "extra": True}),
        (
            BankLineMatchUpdatePreviewInput,
            {"id": "match-1", "bankLineMatch": {}, "extra": True},
        ),
        (BankLineMatchDeletePreviewInput, {"id": "match-1", "extra": True}),
        (BankLineCreatePreviewInput, {"bankLine": {}, "extra": True}),
        (BankLineUpdatePreviewInput, {"id": "line-1", "bankLine": {}, "extra": True}),
        (BankLineDeletePreviewInput, {"id": "line-1", "extra": True}),
        (
            BankLineSubjectAssociationCreatePreviewInput,
            {"bankLineSubjectAssociation": {}, "extra": True},
        ),
        (
            BankLineSubjectAssociationUpdatePreviewInput,
            {
                "id": "association-1",
                "bankLineSubjectAssociation": {},
                "extra": True,
            },
        ),
        (BankLineSubjectAssociationDeletePreviewInput, {"id": "association-1", "extra": True}),
        (BankLineMatchUpdatePreviewInput, {"id": "", "bankLineMatch": {}}),
        (BankLineMatchDeletePreviewInput, {"id": ""}),
        (BankLineUpdatePreviewInput, {"id": "", "bankLine": {}}),
        (BankLineDeletePreviewInput, {"id": ""}),
        (
            BankLineSubjectAssociationUpdatePreviewInput,
            {"id": "", "bankLineSubjectAssociation": {}},
        ),
        (BankLineSubjectAssociationDeletePreviewInput, {"id": ""}),
        (
            BankLineMatchUpdatePreviewInput,
            {"id": "match-1", "bankLineMatch": {"id": "other"}},
        ),
        (BankLineUpdatePreviewInput, {"id": "line-1", "bankLine": {"id": "other"}}),
        (
            BankLineSubjectAssociationUpdatePreviewInput,
            {
                "id": "association-1",
                "bankLineSubjectAssociation": {"id": "other"},
            },
        ),
        (WriteExecuteInput, {"confirmation_ticket": "ticket", "bankLine": {}}),
    ],
)
def test_outer_inputs_reject_extras_empty_ids_and_mismatched_body_ids(
    input_model: type[BaseModel],
    payload: dict[str, object],
) -> None:
    with pytest.raises(ValidationError):
        input_model.model_validate(payload)


def test_opaque_inner_payloads_preserve_unknown_fields_and_matching_ids() -> None:
    match = BankLineMatchUpdatePreviewInput.model_validate(
        {
            "id": "match-1",
            "bankLineMatch": {"id": "match-1", "future": {"rank": 1}},
        }
    )
    line = BankLineUpdatePreviewInput.model_validate(
        {"id": "line-1", "bankLine": {"id": "line-1", "future": {"rank": 2}}}
    )
    association = BankLineSubjectAssociationUpdatePreviewInput.model_validate(
        {
            "id": "association-1",
            "bankLineSubjectAssociation": {
                "id": "association-1",
                "future": {"rank": 3},
            },
        }
    )

    assert match.bankLineMatch["future"] == {"rank": 1}
    assert line.bankLine["future"] == {"rank": 2}
    assert association.bankLineSubjectAssociation["future"] == {"rank": 3}


@pytest.mark.parametrize(
    ("tool_name", "arguments", "expected_request", "expected_effect"),
    [
        (
            "api_bank_line_matches_create_preview",
            {"bankLineMatch": {"opaque": {"rank": 1}}},
            {"bankLineMatch": {"opaque": {"rank": 1}}},
            {"action": "create", "resource": "bankLineMatch"},
        ),
        (
            "api_bank_line_matches_update_preview",
            {"id": "match-1", "bankLineMatch": {"isApproved": True}},
            {"bankLineMatch": {"isApproved": True}},
            {"action": "update", "resource": "bankLineMatch", "id": "match-1"},
        ),
        (
            "api_bank_line_matches_delete_preview",
            {"id": "match-1"},
            {"id": "match-1"},
            {"action": "delete", "resource": "bankLineMatch", "id": "match-1"},
        ),
        (
            "api_bank_lines_create_preview",
            {"bankLine": {"opaque": {"rank": 2}}},
            {"bankLine": {"opaque": {"rank": 2}}},
            {"action": "create", "resource": "bankLine"},
        ),
        (
            "api_bank_lines_update_preview",
            {"id": "line-1", "bankLine": {"description": "updated"}},
            {"bankLine": {"description": "updated"}},
            {"action": "update", "resource": "bankLine", "id": "line-1"},
        ),
        (
            "api_bank_lines_delete_preview",
            {"id": "line-1"},
            {"id": "line-1"},
            {"action": "delete", "resource": "bankLine", "id": "line-1"},
        ),
        (
            "api_bank_line_subject_associations_create_preview",
            {"bankLineSubjectAssociation": {"opaque": {"rank": 3}}},
            {"bankLineSubjectAssociation": {"opaque": {"rank": 3}}},
            {"action": "create", "resource": "bankLineSubjectAssociation"},
        ),
        (
            "api_bank_line_subject_associations_update_preview",
            {
                "id": "association-1",
                "bankLineSubjectAssociation": {"opaque": {"rank": 4}},
            },
            {"bankLineSubjectAssociation": {"opaque": {"rank": 4}}},
            {
                "action": "update",
                "resource": "bankLineSubjectAssociation",
                "id": "association-1",
            },
        ),
        (
            "api_bank_line_subject_associations_delete_preview",
            {"id": "association-1"},
            {"id": "association-1"},
            {
                "action": "delete",
                "resource": "bankLineSubjectAssociation",
                "id": "association-1",
            },
        ),
    ],
)
def test_previews_are_mutation_free_and_bind_exact_requests(
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
    assert isinstance(preview["confirmation_ticket"], str)


@pytest.mark.parametrize(
    (
        "preview_name, execute_name, arguments, response, method, path, body, "
        "expected_changed, expected_deleted"
    ),
    [
        (
            "api_bank_line_matches_create_preview",
            "api_bank_line_matches_create_execute",
            {"bankLineMatch": {"amount": 100, "side": "opaque"}},
            {
                "bankLineMatches": [{"id": "match-1"}],
                "bankLines": [{"id": "line-1"}],
                "bankLineSubjectAssociations": [{"id": "association-1"}],
            },
            "POST",
            "/v2/bankLineMatches",
            {"bankLineMatch": {"amount": 100, "side": "opaque"}},
            {
                "bankLineMatches": [{"id": "match-1"}],
                "bankLines": [{"id": "line-1"}],
                "bankLineSubjectAssociations": [{"id": "association-1"}],
            },
            None,
        ),
        (
            "api_bank_line_matches_update_preview",
            "api_bank_line_matches_update_execute",
            {"id": "match /?", "bankLineMatch": {"isApproved": True}},
            {"bankLineMatches": [{"id": "match /?", "isApproved": True}]},
            "PUT",
            "/v2/bankLineMatches/match%20%2F%3F",
            {"bankLineMatch": {"isApproved": True}},
            {"bankLineMatches": [{"id": "match /?", "isApproved": True}]},
            None,
        ),
        (
            "api_bank_line_matches_delete_preview",
            "api_bank_line_matches_delete_execute",
            {"id": "match /?"},
            {
                "bankLines": [{"id": "line-1"}],
                "meta": {"deletedRecords": {"bankLineMatches": ["match /?"]}},
            },
            "DELETE",
            "/v2/bankLineMatches/match%20%2F%3F",
            None,
            {"bankLines": [{"id": "line-1"}]},
            {"bankLineMatches": ["match /?"]},
        ),
        (
            "api_bank_lines_create_preview",
            "api_bank_lines_create_execute",
            {"bankLine": {"description": "opaque"}},
            {"bankLines": [{"id": "line-1"}]},
            "POST",
            "/v2/bankLines",
            {"bankLine": {"description": "opaque"}},
            {"bankLines": [{"id": "line-1"}]},
            None,
        ),
        (
            "api_bank_lines_update_preview",
            "api_bank_lines_update_execute",
            {"id": "line /?", "bankLine": {"description": "updated"}},
            {"bankLines": [{"id": "line /?", "description": "updated"}]},
            "PUT",
            "/v2/bankLines/line%20%2F%3F",
            {"bankLine": {"description": "updated"}},
            {"bankLines": [{"id": "line /?", "description": "updated"}]},
            None,
        ),
        (
            "api_bank_lines_delete_preview",
            "api_bank_lines_delete_execute",
            {"id": "line /?"},
            {"meta": {"deletedRecords": {"bankLines": ["line /?"]}}},
            "DELETE",
            "/v2/bankLines/line%20%2F%3F",
            None,
            {},
            {"bankLines": ["line /?"]},
        ),
        (
            "api_bank_line_subject_associations_create_preview",
            "api_bank_line_subject_associations_create_execute",
            {"bankLineSubjectAssociation": {"subject": {"opaque": True}}},
            {"bankLineSubjectAssociations": [{"id": "association-1"}]},
            "POST",
            "/v2/bankLineSubjectAssociations",
            {"bankLineSubjectAssociation": {"subject": {"opaque": True}}},
            {"bankLineSubjectAssociations": [{"id": "association-1"}]},
            None,
        ),
        (
            "api_bank_line_subject_associations_update_preview",
            "api_bank_line_subject_associations_update_execute",
            {
                "id": "association /?",
                "bankLineSubjectAssociation": {"subject": {"opaque": False}},
            },
            {"bankLineSubjectAssociations": [{"id": "association /?"}]},
            "PUT",
            "/v2/bankLineSubjectAssociations/association%20%2F%3F",
            {"bankLineSubjectAssociation": {"subject": {"opaque": False}}},
            {"bankLineSubjectAssociations": [{"id": "association /?"}]},
            None,
        ),
        (
            "api_bank_line_subject_associations_delete_preview",
            "api_bank_line_subject_associations_delete_execute",
            {"id": "association /?"},
            {"meta": {"deletedRecords": {"bankLineSubjectAssociations": ["association /?"]}}},
            "DELETE",
            "/v2/bankLineSubjectAssociations/association%20%2F%3F",
            None,
            {},
            {"bankLineSubjectAssociations": ["association /?"]},
        ),
    ],
)
def test_execute_sends_exact_singular_cud_shapes_once(
    preview_name: str,
    execute_name: str,
    arguments: dict[str, object],
    response: dict[str, object],
    method: str,
    path: str,
    body: dict[str, object] | None,
    expected_changed: dict[str, object],
    expected_deleted: dict[str, list[str]] | None,
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
    assert execution["changed_records"] == expected_changed
    assert execution["deleted_records"] == expected_deleted
    if body is None:
        assert request.content == b""
    else:
        assert json.loads(request.content) == body


def test_match_optional_child_roots_are_mapped_only_when_returned() -> None:
    server, _ = make_server(
        lambda request: httpx.Response(
            200,
            json={
                "bankLineMatches": [{"id": "match-1"}],
                "unrelated": [{"id": "ignored"}],
            },
        )
    )

    preview = call_tool(
        server,
        "api_bank_line_matches_create_preview",
        {"bankLineMatch": {"opaque": True}},
    )
    execution = call_tool(
        server,
        "api_bank_line_matches_create_execute",
        {"confirmation_ticket": preview["confirmation_ticket"]},
    )

    assert execution["changed_records"] == {"bankLineMatches": [{"id": "match-1"}]}


@pytest.mark.parametrize(
    ("preview_name", "execute_name", "arguments", "primary_root", "extra_roots"),
    [
        (
            "api_bank_lines_create_preview",
            "api_bank_lines_create_execute",
            {"bankLine": {"opaque": True}},
            "bankLines",
            {
                "bankLineMatches": [{"id": "match-1"}],
                "bankLineSubjectAssociations": [{"id": "association-1"}],
            },
        ),
        (
            "api_bank_line_subject_associations_create_preview",
            "api_bank_line_subject_associations_create_execute",
            {"bankLineSubjectAssociation": {"opaque": True}},
            "bankLineSubjectAssociations",
            {
                "bankLineMatches": [{"id": "match-1"}],
                "bankLines": [{"id": "line-1"}],
            },
        ),
    ],
)
def test_child_resources_do_not_map_parent_or_sibling_roots(
    preview_name: str,
    execute_name: str,
    arguments: dict[str, object],
    primary_root: str,
    extra_roots: dict[str, object],
) -> None:
    response = {primary_root: [{"id": "primary-1"}], **extra_roots}
    server, _ = make_server(lambda request: httpx.Response(200, json=response))

    preview = call_tool(server, preview_name, arguments)
    execution = call_tool(
        server,
        execute_name,
        {"confirmation_ticket": preview["confirmation_ticket"]},
    )

    assert execution["changed_records"] == {primary_root: [{"id": "primary-1"}]}


@pytest.mark.parametrize(
    "response",
    [
        {"bankLines": [{"id": "line-1"}]},
        {"bankLineMatches": {"id": "match-1"}},
        {
            "bankLineMatches": [{"id": "match-1"}],
            "bankLines": {"id": "line-1"},
        },
    ],
)
def test_match_create_rejects_missing_or_malformed_declared_roots(
    response: dict[str, object],
) -> None:
    server, _ = make_server(lambda request: httpx.Response(200, json=response))

    preview = call_tool(
        server,
        "api_bank_line_matches_create_preview",
        {"bankLineMatch": {"opaque": True}},
    )
    execution = call_tool(
        server,
        "api_bank_line_matches_create_execute",
        {"confirmation_ticket": preview["confirmation_ticket"]},
    )

    assert execution["code"] == StableErrorCode.VALIDATION_ERROR


def test_deletes_do_not_invent_absent_roots_or_deleted_metadata() -> None:
    server, _ = make_server(lambda request: httpx.Response(200, json={"meta": {}}))

    preview = call_tool(server, "api_bank_lines_delete_preview", {"id": "line-1"})
    execution = call_tool(
        server,
        "api_bank_lines_delete_execute",
        {"confirmation_ticket": preview["confirmation_ticket"]},
    )

    assert execution == {"changed_records": {}, "deleted_records": None}


def test_tampered_expired_replayed_and_wrong_executor_tickets_do_not_write() -> None:
    clock = Clock()
    server, requests = make_server(
        lambda request: httpx.Response(200, json={"bankLineMatches": [{"id": "match-1"}]}),
        confirmations=ConfirmationStore(clock),
    )
    preview = call_tool(
        server,
        "api_bank_line_matches_create_preview",
        {"bankLineMatch": {"opaque": True}},
    )
    ticket = cast(str, preview["confirmation_ticket"])

    tampered = call_tool(
        server,
        "api_bank_line_matches_create_execute",
        {"confirmation_ticket": f"{ticket}x"},
    )
    wrong_executor = call_tool(
        server,
        "api_bank_line_matches_delete_execute",
        {"confirmation_ticket": ticket},
    )
    assert tampered["code"] == StableErrorCode.CONFIRMATION_INVALID
    assert wrong_executor["code"] == StableErrorCode.CONFIRMATION_MISMATCH
    assert requests == []

    clock.now += timedelta(minutes=6)
    expired = call_tool(
        server,
        "api_bank_line_matches_create_execute",
        {"confirmation_ticket": ticket},
    )
    assert expired["code"] == StableErrorCode.CONFIRMATION_EXPIRED
    assert requests == []

    replay_preview = call_tool(
        server,
        "api_bank_line_matches_create_preview",
        {"bankLineMatch": {"opaque": True}},
    )
    replay_ticket = cast(str, replay_preview["confirmation_ticket"])
    first = call_tool(
        server,
        "api_bank_line_matches_create_execute",
        {"confirmation_ticket": replay_ticket},
    )
    replay = call_tool(
        server,
        "api_bank_line_matches_create_execute",
        {"confirmation_ticket": replay_ticket},
    )
    assert first["changed_records"] == {"bankLineMatches": [{"id": "match-1"}]}
    assert replay["code"] == StableErrorCode.CONFIRMATION_CONSUMED
    assert len(requests) == 1


@pytest.mark.parametrize(
    "changes",
    [
        {"execute_tool_name": "api_bank_line_matches_other_execute"},
        {"organization_id": "other-organisation"},
        {"resource_id": "other-match"},
        {"payload": {"isApproved": False}},
        {"expected_effect_state": {"action": "other"}},
    ],
)
def test_ticket_binding_rejects_executor_organisation_target_payload_and_effect_changes(
    changes: dict[str, object],
) -> None:
    specification = WriteOperationSpec(
        execute_tool_name="api_bank_line_matches_update_execute",
        method=WriteMethod.PUT,
        collection_path="/bankLineMatches",
        singular_root="bankLineMatch",
        plural_root="bankLineMatches",
        additional_plural_roots=("bankLines", "bankLineSubjectAssociations"),
        payload={"isApproved": True},
        resource_id="match-1",
        organization_id=None,
        summary="Update one Billy bank-line match.",
        expected_effect_state={
            "action": "update",
            "resource": "bankLineMatch",
            "id": "match-1",
        },
    )
    store = ConfirmationStore()
    ticket = store.issue(confirmation_binding_for(specification))

    with pytest.raises(ConfirmationFailure) as failure:
        store.consume(
            ticket.value,
            confirmation_binding_for(specification.model_copy(update=changes)),
        )

    assert failure.value.error.code is StableErrorCode.CONFIRMATION_MISMATCH


def test_empty_token_returns_typed_auth_error_without_network_activity() -> None:
    server, requests = make_server(
        lambda request: pytest.fail(f"missing token attempted HTTP request: {request.url}"),
        token="",
    )
    preview = call_tool(
        server,
        "api_bank_lines_create_preview",
        {"bankLine": {"opaque": True}},
    )
    error = call_tool(
        server,
        "api_bank_lines_create_execute",
        {"confirmation_ticket": preview["confirmation_ticket"]},
    )

    assert error["code"] == StableErrorCode.AUTH_REQUIRED
    assert requests == []


@pytest.mark.parametrize(
    "status, response, preview_name, arguments, execute_name, expected_code",
    [
        (
            401,
            {"errorCode": "AUTHENTICATION_REQUIRED"},
            "api_bank_line_matches_create_preview",
            {"bankLineMatch": {"opaque": True}},
            "api_bank_line_matches_create_execute",
            StableErrorCode.AUTH_REQUIRED,
        ),
        (
            404,
            {"errorCode": "RECORD_NOT_FOUND"},
            "api_bank_line_subject_associations_update_preview",
            {
                "id": "missing",
                "bankLineSubjectAssociation": {"opaque": True},
            },
            "api_bank_line_subject_associations_update_execute",
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


def test_write_failure_is_not_retried() -> None:
    server, requests = make_server(
        lambda request: httpx.Response(500, json={"errorCode": "INTERNAL_SERVER_ERROR"})
    )
    preview = call_tool(
        server,
        "api_bank_line_subject_associations_create_preview",
        {"bankLineSubjectAssociation": {"opaque": True}},
    )
    error = call_tool(
        server,
        "api_bank_line_subject_associations_create_execute",
        {"confirmation_ticket": preview["confirmation_ticket"]},
    )

    assert error["code"] == StableErrorCode.BILLY_ERROR
    assert len(requests) == 1
