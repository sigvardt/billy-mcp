from __future__ import annotations

import json
from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, datetime

import httpx
import pytest
from pydantic import ValidationError

from billy_mcp.api.write_protocol import (
    WriteExecuteInput,
    WriteExecutionResult,
    WriteMethod,
    WriteOperationSpec,
    WritePreviewResult,
    WriteProtocolService,
    canonical_request_for,
    confirmation_binding_for,
    execution_path_for,
)
from billy_mcp.client import BillyHttpClient
from billy_mcp.confirmations import (
    MAX_TICKET_TTL,
    ConfirmationFailure,
    ConfirmationStore,
)
from billy_mcp.models import StableErrorCode, ToolError
from billy_mcp.redaction import REDACTED


class Clock:
    def __init__(self) -> None:
        self.now = datetime(2026, 7, 29, tzinfo=UTC)

    def __call__(self) -> datetime:
        return self.now


def operation(
    method: WriteMethod = WriteMethod.POST,
    **changes: object,
) -> WriteOperationSpec:
    values: dict[str, object] = {
        "execute_tool_name": "api_products_create_execute",
        "method": method,
        "collection_path": "/products",
        "singular_root": "product",
        "plural_root": "products",
        "payload": {"name": "A product", "properties": {"b": 2, "a": 1}},
        "resource_id": None,
        "organization_id": "org-1",
        "summary": "Create product A",
        "expected_effect_state": {"action": "create", "resource": "product"},
    }
    if method is not WriteMethod.POST:
        values.update(
            {
                "execute_tool_name": "api_products_update_execute",
                "resource_id": "product /?",
                "summary": "Update product product /?",
                "expected_effect_state": {
                    "action": "update",
                    "resource": "product",
                    "id": "product /?",
                },
            }
        )
    if method is WriteMethod.DELETE:
        values.update(
            {
                "execute_tool_name": "api_products_delete_execute",
                "payload": None,
                "summary": "Delete product product /?",
                "expected_effect_state": {
                    "action": "delete",
                    "resource": "product",
                    "id": "product /?",
                },
            }
        )
    values.update(changes)
    return WriteOperationSpec.model_validate(values)


def make_service(
    handler: httpx.MockTransport,
    *,
    confirmations: ConfirmationStore | None = None,
) -> WriteProtocolService:
    return WriteProtocolService(
        BillyHttpClient(lambda: "test-token", transport=handler),
        confirmations or ConfirmationStore(),
    )


@pytest.mark.parametrize(
    ("specification", "expected_request", "expected_path"),
    [
        (
            operation(),
            {"product": {"name": "A product", "properties": {"a": 1, "b": 2}}},
            "/products",
        ),
        (
            operation(WriteMethod.PUT),
            {"product": {"name": "A product", "properties": {"a": 1, "b": 2}}},
            "/products/product%20%2F%3F",
        ),
        (
            operation(WriteMethod.DELETE),
            {"id": "product /?"},
            "/products/product%20%2F%3F",
        ),
    ],
)
def test_canonical_request_and_path_cover_all_singular_write_shapes(
    specification: WriteOperationSpec,
    expected_request: dict[str, object],
    expected_path: str,
) -> None:
    assert canonical_request_for(specification) == expected_request
    assert execution_path_for(specification) == expected_path


def test_preview_is_non_mutating_and_serializes_as_a_typed_tool_result() -> None:
    requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return httpx.Response(200, json={"products": []})

    service = make_service(httpx.MockTransport(handler))
    preview = service.preview(operation())

    assert requests == []
    assert preview.canonical_request == {
        "product": {"name": "A product", "properties": {"a": 1, "b": 2}}
    }
    serialized = preview.model_dump(mode="json")
    assert serialized["expires_at"].endswith("Z")
    assert (
        WritePreviewResult.model_validate(serialized).confirmation_ticket
        == preview.confirmation_ticket
    )
    assert WriteExecuteInput.model_validate(
        {"confirmation_ticket": preview.confirmation_ticket}
    ).model_dump() == {"confirmation_ticket": preview.confirmation_ticket}
    with pytest.raises(ValidationError):
        WritePreviewResult.model_validate({**serialized, "unexpected": True})
    with pytest.raises(ValidationError):
        WriteExecuteInput.model_validate(
            {"confirmation_ticket": preview.confirmation_ticket, "confirm": True}
        )
    with pytest.raises(ValidationError):
        WriteExecutionResult.model_validate({"changed_records": {}, "unexpected": True})


@pytest.mark.parametrize(
    ("specification", "response", "expected_method", "expected_body"),
    [
        (
            operation(),
            {"products": [{"id": "product-1"}]},
            "POST",
            {"product": {"name": "A product", "properties": {"a": 1, "b": 2}}},
        ),
        (
            operation(WriteMethod.PUT),
            {"products": [{"id": "product /?"}]},
            "PUT",
            {"product": {"name": "A product", "properties": {"a": 1, "b": 2}}},
        ),
        (
            operation(WriteMethod.DELETE),
            {"meta": {"deletedRecords": {"products": ["product /?"]}}},
            "DELETE",
            None,
        ),
    ],
)
def test_execute_sends_the_exact_stored_method_path_and_body_once(
    specification: WriteOperationSpec,
    response: dict[str, object],
    expected_method: str,
    expected_body: dict[str, object] | None,
) -> None:
    requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return httpx.Response(200, json=response)

    service = make_service(httpx.MockTransport(handler))
    preview = service.preview(specification)
    result = service.execute(
        WriteExecuteInput(confirmation_ticket=preview.confirmation_ticket),
        execute_tool_name=specification.execute_tool_name,
    )

    assert isinstance(result, WriteExecutionResult)
    assert len(requests) == 1
    assert requests[0].method == expected_method
    assert requests[0].url.raw_path.decode() == f"/v2{execution_path_for(specification)}"
    if expected_body is None:
        assert requests[0].content == b""
    else:
        assert json.loads(requests[0].content) == expected_body


def test_execute_never_retries_a_write() -> None:
    attempts: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        attempts.append(request)
        return httpx.Response(503, json={"errorCode": "TEMPORARY"})

    service = make_service(httpx.MockTransport(handler))
    preview = service.preview(operation())
    result = service.execute(
        WriteExecuteInput(confirmation_ticket=preview.confirmation_ticket),
        execute_tool_name="api_products_create_execute",
    )

    assert isinstance(result, ToolError)
    assert result.code is StableErrorCode.BILLY_ERROR
    assert len(attempts) == 1


def test_execution_maps_only_declared_changed_and_deleted_record_roots() -> None:
    service = make_service(
        httpx.MockTransport(
            lambda request: httpx.Response(
                200,
                json={
                    "products": [{"id": "product-1", "name": "A product"}],
                    "contacts": [{"id": "contact-1"}],
                    "meta": {
                        "deletedRecords": {"products": ["old-product"], "contacts": ["old-contact"]}
                    },
                },
            )
        )
    )
    preview = service.preview(operation(WriteMethod.PUT))
    result = service.execute(
        WriteExecuteInput(confirmation_ticket=preview.confirmation_ticket),
        execute_tool_name="api_products_update_execute",
    )

    assert isinstance(result, WriteExecutionResult)
    assert result.model_dump() == {
        "changed_records": {"products": [{"id": "product-1", "name": "A product"}]},
        "deleted_records": {"products": ["old-product"]},
    }


@pytest.mark.parametrize(
    ("body", "expected_changed_records"),
    [
        (
            {
                "products": [{"id": "product-1"}],
                "productPrices": [{"id": "price-1", "productId": "product-1"}],
                "contacts": [{"id": "contact-1"}],
            },
            {
                "products": [{"id": "product-1"}],
                "productPrices": [{"id": "price-1", "productId": "product-1"}],
            },
        ),
        (
            {"products": [{"id": "product-1"}]},
            {"products": [{"id": "product-1"}]},
        ),
    ],
)
def test_execution_maps_every_present_declared_changed_record_root(
    body: dict[str, object],
    expected_changed_records: dict[str, list[dict[str, str]]],
) -> None:
    service = make_service(httpx.MockTransport(lambda request: httpx.Response(200, json=body)))
    preview = service.preview(
        operation(WriteMethod.PUT, additional_plural_roots=("productPrices",))
    )
    result = service.execute(
        WriteExecuteInput(confirmation_ticket=preview.confirmation_ticket),
        execute_tool_name="api_products_update_execute",
    )

    assert isinstance(result, WriteExecutionResult)
    assert result.changed_records == expected_changed_records
    assert result.deleted_records is None


def test_delete_preserves_absent_optional_deleted_records_without_inventing_them() -> None:
    service = make_service(
        httpx.MockTransport(lambda request: httpx.Response(200, json={"meta": {}}))
    )
    preview = service.preview(operation(WriteMethod.DELETE))
    result = service.execute(
        WriteExecuteInput(confirmation_ticket=preview.confirmation_ticket),
        execute_tool_name="api_products_delete_execute",
    )

    assert isinstance(result, WriteExecutionResult)
    assert result.changed_records == {}
    assert result.deleted_records is None


def test_delete_maps_every_present_declared_deleted_record_root() -> None:
    service = make_service(
        httpx.MockTransport(
            lambda request: httpx.Response(
                200,
                json={
                    "meta": {
                        "deletedRecords": {
                            "products": ["old-product"],
                            "productPrices": ["old-price"],
                            "contacts": ["undeclared-contact"],
                        }
                    }
                },
            )
        )
    )
    preview = service.preview(
        operation(WriteMethod.DELETE, additional_plural_roots=("productPrices",))
    )
    result = service.execute(
        WriteExecuteInput(confirmation_ticket=preview.confirmation_ticket),
        execute_tool_name="api_products_delete_execute",
    )

    assert isinstance(result, WriteExecutionResult)
    assert result.changed_records == {}
    assert result.deleted_records == {
        "products": ["old-product"],
        "productPrices": ["old-price"],
    }


@pytest.mark.parametrize("deleted_product_prices", ["not-a-list", [1]])
def test_malformed_declared_additional_deleted_root_returns_validation_error(
    deleted_product_prices: object,
) -> None:
    service = make_service(
        httpx.MockTransport(
            lambda request: httpx.Response(
                200,
                json={
                    "meta": {
                        "deletedRecords": {
                            "products": ["old-product"],
                            "productPrices": deleted_product_prices,
                        }
                    }
                },
            )
        )
    )
    preview = service.preview(
        operation(WriteMethod.DELETE, additional_plural_roots=("productPrices",))
    )
    result = service.execute(
        WriteExecuteInput(confirmation_ticket=preview.confirmation_ticket),
        execute_tool_name="api_products_delete_execute",
    )

    assert isinstance(result, ToolError)
    assert result.code is StableErrorCode.VALIDATION_ERROR


@pytest.mark.parametrize(
    "body",
    [
        {},
        {"products": {}},
        {"products": ["not-an-object"]},
        {"products": [], "meta": {"deletedRecords": {"products": [1]}}},
    ],
)
def test_malformed_success_payload_returns_validation_error(body: dict[str, object]) -> None:
    service = make_service(httpx.MockTransport(lambda request: httpx.Response(200, json=body)))
    preview = service.preview(operation(WriteMethod.PUT))
    result = service.execute(
        WriteExecuteInput(confirmation_ticket=preview.confirmation_ticket),
        execute_tool_name="api_products_update_execute",
    )

    assert isinstance(result, ToolError)
    assert result.code is StableErrorCode.VALIDATION_ERROR


def test_malformed_declared_additional_changed_root_returns_validation_error() -> None:
    service = make_service(
        httpx.MockTransport(
            lambda request: httpx.Response(
                200,
                json={"products": [{"id": "product-1"}], "productPrices": {}},
            )
        )
    )
    preview = service.preview(
        operation(WriteMethod.PUT, additional_plural_roots=("productPrices",))
    )
    result = service.execute(
        WriteExecuteInput(confirmation_ticket=preview.confirmation_ticket),
        execute_tool_name="api_products_update_execute",
    )

    assert isinstance(result, ToolError)
    assert result.code is StableErrorCode.VALIDATION_ERROR


@pytest.mark.parametrize(
    ("status", "body", "expected_code"),
    [
        (
            401,
            {"errorCode": "AUTHENTICATION_REQUIRED", "confirmation_ticket": "never-leak"},
            StableErrorCode.AUTH_REQUIRED,
        ),
        (404, {"errorCode": "RECORD_NOT_FOUND"}, StableErrorCode.NOT_FOUND),
    ],
)
def test_typed_upstream_errors_pass_through_unchanged(
    status: int,
    body: dict[str, str],
    expected_code: StableErrorCode,
) -> None:
    service = make_service(httpx.MockTransport(lambda request: httpx.Response(status, json=body)))
    preview = service.preview(operation())
    result = service.execute(
        WriteExecuteInput(confirmation_ticket=preview.confirmation_ticket),
        execute_tool_name="api_products_create_execute",
    )

    assert isinstance(result, ToolError)
    assert result.code is expected_code
    if status == 401:
        assert result.details["upstream"]["confirmation_ticket"] == REDACTED


def test_ticket_tampering_replay_expiry_and_concurrent_execution_are_safe() -> None:
    clock = Clock()
    requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return httpx.Response(200, json={"products": [{"id": "product-1"}]})

    service = make_service(httpx.MockTransport(handler), confirmations=ConfirmationStore(clock))
    preview = service.preview(operation())

    tampered = service.execute(
        WriteExecuteInput(confirmation_ticket=f"{preview.confirmation_ticket}x"),
        execute_tool_name="api_products_create_execute",
    )
    assert isinstance(tampered, ToolError)
    assert tampered.code is StableErrorCode.CONFIRMATION_INVALID
    assert preview.confirmation_ticket not in tampered.message

    def execute_create(input: WriteExecuteInput) -> WriteExecutionResult | ToolError:
        return service.execute(input, execute_tool_name="api_products_create_execute")

    with ThreadPoolExecutor(max_workers=2) as executor:
        results = list(
            executor.map(
                execute_create,
                [
                    WriteExecuteInput(confirmation_ticket=preview.confirmation_ticket),
                    WriteExecuteInput(confirmation_ticket=preview.confirmation_ticket),
                ],
            )
        )
    assert sum(isinstance(result, WriteExecutionResult) for result in results) == 1
    assert [result.code for result in results if isinstance(result, ToolError)] == [
        StableErrorCode.CONFIRMATION_CONSUMED
    ]
    assert len(requests) == 1

    replayed = service.execute(
        WriteExecuteInput(confirmation_ticket=preview.confirmation_ticket),
        execute_tool_name="api_products_create_execute",
    )
    assert isinstance(replayed, ToolError)
    assert replayed.code is StableErrorCode.CONFIRMATION_CONSUMED
    assert len(requests) == 1

    expiring_preview = service.preview(operation())
    clock.now += MAX_TICKET_TTL
    expired = service.execute(
        WriteExecuteInput(confirmation_ticket=expiring_preview.confirmation_ticket),
        execute_tool_name="api_products_create_execute",
    )
    assert isinstance(expired, ToolError)
    assert expired.code is StableErrorCode.CONFIRMATION_EXPIRED


def test_execute_rejects_the_wrong_executor_without_consuming_the_ticket() -> None:
    requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return httpx.Response(200, json={"products": [{"id": "product-1"}]})

    service = make_service(httpx.MockTransport(handler))
    specification = operation()
    preview = service.preview(specification)

    wrong_executor = service.execute(
        WriteExecuteInput(confirmation_ticket=preview.confirmation_ticket),
        execute_tool_name="api_products_delete_execute",
    )
    assert isinstance(wrong_executor, ToolError)
    assert wrong_executor.code is StableErrorCode.CONFIRMATION_MISMATCH
    assert requests == []

    correct_executor = service.execute(
        WriteExecuteInput(confirmation_ticket=preview.confirmation_ticket),
        execute_tool_name=specification.execute_tool_name,
    )
    assert isinstance(correct_executor, WriteExecutionResult)
    assert len(requests) == 1


def test_terminal_execution_discards_the_request_and_preserves_the_replay_error() -> None:
    confirmations = ConfirmationStore()
    service = make_service(
        httpx.MockTransport(lambda request: httpx.Response(200, json={"products": []})),
        confirmations=confirmations,
    )
    specification = operation()
    preview = service.preview(specification)

    executed = service.execute(
        WriteExecuteInput(confirmation_ticket=preview.confirmation_ticket),
        execute_tool_name=specification.execute_tool_name,
    )
    assert isinstance(executed, WriteExecutionResult)

    wrong_executor_after_execution = service.execute(
        WriteExecuteInput(confirmation_ticket=preview.confirmation_ticket),
        execute_tool_name="api_products_delete_execute",
    )
    assert isinstance(wrong_executor_after_execution, ToolError)
    assert wrong_executor_after_execution.code is StableErrorCode.CONFIRMATION_CONSUMED

    replayed = service.execute(
        WriteExecuteInput(confirmation_ticket=preview.confirmation_ticket),
        execute_tool_name=specification.execute_tool_name,
    )
    assert isinstance(replayed, ToolError)
    assert replayed.code is StableErrorCode.CONFIRMATION_CONSUMED


def test_preview_and_expired_execute_prune_prepared_request_bodies() -> None:
    clock = Clock()
    confirmations = ConfirmationStore(clock)
    service = make_service(
        httpx.MockTransport(lambda request: httpx.Response(200, json={"products": []})),
        confirmations=confirmations,
    )
    specification = operation()
    stale_preview = service.preview(specification)

    clock.now += MAX_TICKET_TTL
    service.preview(specification)

    expired = service.execute(
        WriteExecuteInput(confirmation_ticket=stale_preview.confirmation_ticket),
        execute_tool_name=specification.execute_tool_name,
    )
    assert isinstance(expired, ToolError)
    assert expired.code is StableErrorCode.CONFIRMATION_INVALID

    second_stale_preview = service.preview(specification)
    clock.now += MAX_TICKET_TTL
    direct_expired = service.execute(
        WriteExecuteInput(confirmation_ticket=second_stale_preview.confirmation_ticket),
        execute_tool_name=specification.execute_tool_name,
    )
    assert isinstance(direct_expired, ToolError)
    assert direct_expired.code is StableErrorCode.CONFIRMATION_EXPIRED


@pytest.mark.parametrize(
    "changes",
    [
        {"execute_tool_name": "api_products_other_execute"},
        {"organization_id": "other-org"},
        {"resource_id": "other-product"},
        {"payload": {"name": "Changed"}},
        {"expected_effect_state": {"action": "other"}},
    ],
)
def test_confirmation_binding_rejects_tool_org_target_request_and_effect_mismatches(
    changes: dict[str, object],
) -> None:
    store = ConfirmationStore()
    specification = operation(WriteMethod.PUT)
    binding = confirmation_binding_for(specification)
    assert binding.model_dump(mode="json") == {
        "tool": "api_products_update_execute",
        "organization_id": "org-1",
        "target": "product /?",
        "request": {"product": {"name": "A product", "properties": {"a": 1, "b": 2}}},
        "expected_effect_state": {"action": "update", "id": "product /?", "resource": "product"},
        "file_path": None,
        "file_digest": None,
        "destination_url": None,
    }
    issued = store.issue(binding)
    mismatched = specification.model_copy(update=changes)

    with pytest.raises(ConfirmationFailure) as failure:
        store.consume(issued.value, confirmation_binding_for(mismatched))

    assert failure.value.error.code is StableErrorCode.CONFIRMATION_MISMATCH
    assert issued.value not in failure.value.error.message


def test_operation_spec_rejects_generic_http_and_invalid_singular_shapes() -> None:
    with pytest.raises(ValidationError, match="collection_path"):
        operation(collection_path="https://example.test/products")
    with pytest.raises(ValidationError, match="POST requires"):
        operation(resource_id="product-1")
    with pytest.raises(ValidationError, match="DELETE requires"):
        operation(WriteMethod.DELETE, payload={"name": "not allowed"})
