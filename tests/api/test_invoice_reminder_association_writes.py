"""Contract tests for ticketed singular invoice-reminder-association writes."""

from __future__ import annotations

import asyncio
from collections.abc import Callable
from typing import cast

import httpx
import pytest
from fastmcp import FastMCP
from fastmcp.exceptions import ValidationError as FastMcpValidationError
from pydantic import ValidationError

from billy_mcp.api.invoice_reminder_association_writes import (
    InvoiceReminderAssociationCreatePreviewInput,
    InvoiceReminderAssociationUpdatePreviewInput,
    register_invoice_reminder_association_write_tools,
)
from billy_mcp.api.write_protocol import WriteExecuteInput, WriteProtocolService
from billy_mcp.client import BillyHttpClient
from billy_mcp.confirmations import ConfirmationStore

MockHandler = Callable[[httpx.Request], httpx.Response]

VALID_ASSOCIATION = {"reminder": "reminder-1", "invoice": "invoice-1"}


def make_server(
    handler: MockHandler,
    *,
    token: str | None = "invoice-reminder-association-write-test-token",
    confirmations: ConfirmationStore | None = None,
) -> tuple[FastMCP, list[httpx.Request]]:
    """Create a fully local FastMCP server with a recording locked client."""

    requests: list[httpx.Request] = []

    def recording_handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return handler(request)

    client = BillyHttpClient(lambda: token, transport=httpx.MockTransport(recording_handler))
    server = FastMCP("invoice-reminder-association-write-contract-test")
    register_invoice_reminder_association_write_tools(
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
    structured_result = structured_content.get("result", structured_content)
    assert isinstance(structured_result, dict)
    return cast(dict[str, object], structured_result)


def test_registers_exactly_four_flat_typed_invoice_reminder_association_write_tools() -> None:
    server, _ = make_server(lambda request: httpx.Response(200, json={}))

    by_name = {tool.name: tool for tool in asyncio.run(server.list_tools())}
    expected_properties = {
        "api_invoice_reminder_associations_create_preview": {"invoiceReminderAssociation"},
        "api_invoice_reminder_associations_create_execute": {"confirmation_ticket"},
        "api_invoice_reminder_associations_update_preview": {
            "id",
            "invoiceReminderAssociation",
        },
        "api_invoice_reminder_associations_update_execute": {"confirmation_ticket"},
    }
    assert set(by_name) == set(expected_properties)
    for name, fields in expected_properties.items():
        schema = by_name[name].parameters
        properties = cast(dict[str, object], schema["properties"])
        assert schema["additionalProperties"] is False
        assert set(properties) == fields
        assert "input" not in properties
    documented = {"reminder", "invoice"}
    for tool_name in (
        "api_invoice_reminder_associations_create_preview",
        "api_invoice_reminder_associations_update_preview",
    ):
        nested_schema = cast(
            dict[str, object],
            by_name[tool_name].parameters["properties"]["invoiceReminderAssociation"],
        )
        if "$ref" in nested_schema:
            ref = str(nested_schema["$ref"]).rsplit("/", maxsplit=1)[-1]
            defs = by_name[tool_name].parameters.get("$defs") or by_name[tool_name].parameters.get(
                "defs"
            )
            assert isinstance(defs, dict)
            nested_schema = cast(dict[str, object], defs[ref])
        nested = cast(dict[str, object], nested_schema["properties"])
        assert set(nested) == documented
        assert nested_schema.get("additionalProperties") is False


@pytest.mark.parametrize(
    ("input_model", "payload"),
    [
        (
            InvoiceReminderAssociationCreatePreviewInput,
            {"invoiceReminderAssociation": VALID_ASSOCIATION, "extra": True},
        ),
        (
            InvoiceReminderAssociationUpdatePreviewInput,
            {
                "id": "assoc-1",
                "invoiceReminderAssociation": VALID_ASSOCIATION,
                "extra": True,
            },
        ),
        (
            InvoiceReminderAssociationUpdatePreviewInput,
            {"id": "", "invoiceReminderAssociation": VALID_ASSOCIATION},
        ),
        (WriteExecuteInput, {"confirmation_ticket": "ticket", "invoiceReminderAssociation": {}}),
        (InvoiceReminderAssociationCreatePreviewInput, {"invoiceReminderAssociation": {}}),
        (
            InvoiceReminderAssociationCreatePreviewInput,
            {"invoiceReminderAssociation": {"reminder": "reminder-1"}},
        ),
        (
            InvoiceReminderAssociationCreatePreviewInput,
            {"invoiceReminderAssociation": {"invoice": "invoice-1"}},
        ),
        (
            InvoiceReminderAssociationCreatePreviewInput,
            {"invoiceReminderAssociation": {"reminder": "", "invoice": "invoice-1"}},
        ),
        (
            InvoiceReminderAssociationCreatePreviewInput,
            {"invoiceReminderAssociation": {"reminder": "reminder-1", "invoice": ""}},
        ),
        (
            InvoiceReminderAssociationCreatePreviewInput,
            {
                "invoiceReminderAssociation": {
                    **VALID_ASSOCIATION,
                    "lateFee": "late-fee-1",
                }
            },
        ),
        (
            InvoiceReminderAssociationCreatePreviewInput,
            {"invoiceReminderAssociation": {**VALID_ASSOCIATION, "reminderId": "r1"}},
        ),
        (
            InvoiceReminderAssociationUpdatePreviewInput,
            {
                "id": "assoc-1",
                "invoiceReminderAssociation": {**VALID_ASSOCIATION, "invoiceId": "i1"},
            },
        ),
        (
            InvoiceReminderAssociationUpdatePreviewInput,
            {
                "id": "assoc-1",
                "invoiceReminderAssociation": {**VALID_ASSOCIATION, "undocumented": True},
            },
        ),
    ],
)
def test_outer_inputs_forbid_extras_empty_ids_and_readonly_nested_keys(
    input_model: type[InvoiceReminderAssociationCreatePreviewInput]
    | type[InvoiceReminderAssociationUpdatePreviewInput]
    | type[WriteExecuteInput],
    payload: dict[str, object],
) -> None:
    with pytest.raises(ValidationError):
        input_model.model_validate(payload)


@pytest.mark.parametrize(
    ("tool_name", "arguments"),
    [
        (
            "api_invoice_reminder_associations_create_preview",
            {"invoiceReminderAssociation": {**VALID_ASSOCIATION, "lateFee": "late-fee-1"}},
        ),
        (
            "api_invoice_reminder_associations_create_preview",
            {"invoiceReminderAssociation": {**VALID_ASSOCIATION, "reminderId": "r1"}},
        ),
        (
            "api_invoice_reminder_associations_update_preview",
            {
                "id": "assoc-1",
                "invoiceReminderAssociation": {**VALID_ASSOCIATION, "invoiceId": "i1"},
            },
        ),
        (
            "api_invoice_reminder_associations_create_preview",
            {"invoiceReminderAssociation": {"reminder": "reminder-1"}},
        ),
        (
            "api_invoice_reminder_associations_update_preview",
            {"id": "assoc-1", "invoiceReminderAssociation": {}},
        ),
    ],
)
def test_preview_tools_reject_readonly_missing_and_aliased_nested_keys(
    tool_name: str,
    arguments: dict[str, object],
) -> None:
    server, requests = make_server(
        lambda request: pytest.fail(f"preview made an HTTP request: {request.method} {request.url}")
    )

    with pytest.raises(FastMcpValidationError):
        asyncio.run(server.call_tool(tool_name, arguments))

    assert requests == []


@pytest.mark.parametrize(
    ("tool_name", "arguments", "expected_request"),
    [
        (
            "api_invoice_reminder_associations_create_preview",
            {"invoiceReminderAssociation": VALID_ASSOCIATION},
            {"invoiceReminderAssociation": VALID_ASSOCIATION},
        ),
        (
            "api_invoice_reminder_associations_update_preview",
            {"id": "assoc-1", "invoiceReminderAssociation": VALID_ASSOCIATION},
            {"invoiceReminderAssociation": VALID_ASSOCIATION},
        ),
    ],
)
def test_previews_are_mutation_free_and_bind_the_exact_canonical_request(
    tool_name: str,
    arguments: dict[str, object],
    expected_request: dict[str, object],
) -> None:
    server, requests = make_server(
        lambda request: pytest.fail(f"preview made an HTTP request: {request.method} {request.url}")
    )

    preview = call_tool(server, tool_name, arguments)

    assert requests == []
    assert preview["canonical_request"] == expected_request
    assert preview["expected_effect_state"] == {
        "action": tool_name.removeprefix("api_invoice_reminder_associations_").removesuffix(
            "_preview"
        ),
        "resource": "invoiceReminderAssociation",
        **({"id": arguments["id"]} if "id" in arguments else {}),
    }
    assert isinstance(preview["confirmation_ticket"], str)
