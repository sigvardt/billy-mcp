"""Contract tests for ticketed singular invoice-reminder-association delete."""

from __future__ import annotations

import asyncio

import httpx
import pytest
from fastmcp.exceptions import ValidationError as FastMcpValidationError
from pydantic import ValidationError

from billy_mcp.api.invoice_reminder_association_writes import (
    InvoiceReminderAssociationDeletePreviewInput,
)
from billy_mcp.api.write_protocol import WriteExecuteInput
from tests.api.test_invoice_reminder_association_writes import call_tool, make_server

DELETE_PREVIEW = "api_invoice_reminder_associations_delete_preview"
DELETE_EXECUTE = "api_invoice_reminder_associations_delete_execute"


def test_registers_six_tools_and_delete_preview_is_id_only() -> None:
    server, _ = make_server(lambda request: httpx.Response(200, json={}))

    by_name = {tool.name: tool for tool in asyncio.run(server.list_tools())}
    assert len(by_name) == 6
    schema = by_name[DELETE_PREVIEW].parameters
    properties = schema["properties"]
    assert schema["additionalProperties"] is False
    assert set(properties) == {"id"}
    assert "input" not in properties
    assert "invoiceReminderAssociation" not in properties
    assert properties["id"]["minLength"] == 1
    execute_schema = by_name[DELETE_EXECUTE].parameters
    execute_properties = execute_schema["properties"]
    assert execute_schema["additionalProperties"] is False
    assert set(execute_properties) == {"confirmation_ticket"}
    assert execute_properties["confirmation_ticket"]["minLength"] == 1


@pytest.mark.parametrize(
    ("input_model", "payload"),
    [
        (InvoiceReminderAssociationDeletePreviewInput, {"id": "assoc-1", "extra": True}),
        (InvoiceReminderAssociationDeletePreviewInput, {"id": ""}),
        (
            InvoiceReminderAssociationDeletePreviewInput,
            {"id": "assoc-1", "invoiceReminderAssociation": {"reminder": "r", "invoice": "i"}},
        ),
        (WriteExecuteInput, {"confirmation_ticket": "ticket", "id": "assoc-1"}),
    ],
)
def test_delete_inputs_forbid_extras_empty_id_and_nested_payload(
    input_model: type[InvoiceReminderAssociationDeletePreviewInput] | type[WriteExecuteInput],
    payload: dict[str, object],
) -> None:
    with pytest.raises(ValidationError):
        input_model.model_validate(payload)


@pytest.mark.parametrize(
    "arguments",
    [
        {"id": ""},
        {"id": "assoc-1", "extra": True},
        {"id": "assoc-1", "invoiceReminderAssociation": {"reminder": "r", "invoice": "i"}},
    ],
)
def test_delete_preview_rejects_empty_id_extras_and_nested_payload_without_http(
    arguments: dict[str, object],
) -> None:
    server, requests = make_server(
        lambda request: pytest.fail(f"preview made an HTTP request: {request.method} {request.url}")
    )

    with pytest.raises(FastMcpValidationError):
        asyncio.run(server.call_tool(DELETE_PREVIEW, arguments))

    assert requests == []


def test_delete_preview_is_mutation_free_and_binds_id_only() -> None:
    server, requests = make_server(
        lambda request: pytest.fail(f"preview made an HTTP request: {request.method} {request.url}")
    )

    preview = call_tool(server, DELETE_PREVIEW, {"id": "assoc-1"})

    assert requests == []
    assert preview["canonical_request"] == {"id": "assoc-1"}
    assert preview["expected_effect_state"] == {
        "action": "delete",
        "resource": "invoiceReminderAssociation",
        "id": "assoc-1",
    }
    assert isinstance(preview["confirmation_ticket"], str)
