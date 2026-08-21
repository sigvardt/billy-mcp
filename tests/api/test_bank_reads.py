"""Contract tests for the typed, read-only Billy bank and balance tools."""

from __future__ import annotations

import asyncio
from collections.abc import Callable

import httpx
import pytest
from fastmcp import FastMCP
from pydantic import BaseModel, ValidationError

from billy_mcp.api.bank_reads import (
    BankGetRequest,
    BankLineSide,
    BankLinesListRequest,
    BankLineSortProperty,
    BankLineStatus,
    BankListRequest,
    BankReadService,
    SortDirection,
    register_bank_read_tools,
)
from billy_mcp.client import BillyHttpClient
from billy_mcp.models import StableErrorCode, ToolError

MockHandler = Callable[[httpx.Request], httpx.Response]
ClientFactory = Callable[[MockHandler], tuple[BillyHttpClient, list[httpx.Request]]]


@pytest.fixture
def client_factory() -> ClientFactory:
    """Provide the locked client on an in-process transport only."""

    def build(handler: MockHandler) -> tuple[BillyHttpClient, list[httpx.Request]]:
        requests: list[httpx.Request] = []

        def recording_handler(request: httpx.Request) -> httpx.Response:
            requests.append(request)
            return handler(request)

        return (
            BillyHttpClient(lambda: "test-token", transport=httpx.MockTransport(recording_handler)),
            requests,
        )

    return build


def test_singular_reads_encode_ids_and_map_every_documented_root(
    client_factory: ClientFactory,
) -> None:
    singular_roots = {
        "/v2/bankPayments/item /?": "bankPayment",
        "/v2/bankLineMatches/item /?": "bankLineMatch",
        "/v2/bankLines/item /?": "bankLine",
        "/v2/bankLineSubjectAssociations/item /?": "bankLineSubjectAssociation",
        "/v2/balanceModifiers/item /?": "balanceModifier",
    }

    def handler(request: httpx.Request) -> httpx.Response:
        root = singular_roots[request.url.path]
        return httpx.Response(200, json={root: {"id": root, "marker": "synthetic"}})

    client, requests = client_factory(handler)
    service = BankReadService(client)
    request = BankGetRequest(id="item /?", include="related")
    results = {
        "bankPayment": service.bank_payments_get(request),
        "bankLineMatch": service.bank_line_matches_get(request),
        "bankLine": service.bank_lines_get(request),
        "bankLineSubjectAssociation": service.bank_line_subject_associations_get(request),
        "balanceModifier": service.balance_modifiers_get(request),
    }

    for root, result in results.items():
        assert isinstance(result, BaseModel)
        assert result.model_dump()[root] == {"id": root, "marker": "synthetic"}
    assert [request.url.path for request in requests] == list(singular_roots)
    assert [str(request.url) for request in requests] == [
        "https://api.billysbilling.com/v2/bankPayments/item%20%2F%3F?include=related",
        "https://api.billysbilling.com/v2/bankLineMatches/item%20%2F%3F?include=related",
        "https://api.billysbilling.com/v2/bankLines/item%20%2F%3F?include=related",
        "https://api.billysbilling.com/v2/bankLineSubjectAssociations/item%20%2F%3F?include=related",
        "https://api.billysbilling.com/v2/balanceModifiers/item%20%2F%3F?include=related",
    ]
    assert all(
        request.url.params == httpx.QueryParams({"include": "related"}) for request in requests
    )


def test_collection_reads_use_only_documented_queries_and_map_optional_paging(
    client_factory: ClientFactory,
) -> None:
    list_roots = {
        "/v2/bankPayments": "bankPayments",
        "/v2/bankLineMatches": "bankLineMatches",
        "/v2/bankLineSubjectAssociations": "bankLineSubjectAssociations",
        "/v2/balanceModifiers": "balanceModifiers",
    }

    def handler(request: httpx.Request) -> httpx.Response:
        root = list_roots[request.url.path]
        response: dict[str, object] = {root: [{"id": root, "marker": "synthetic"}]}
        if root == "bankPayments":
            response["meta"] = {"paging": {"page": 2, "pageSize": 25, "total": 26}}
        return httpx.Response(200, json=response)

    client, requests = client_factory(handler)
    service = BankReadService(client)
    request = BankListRequest(
        page=2,
        pageSize=25,
        include="related",
        sortProperty="createdTime",
        sortDirection=SortDirection.DESC,
    )
    results = {
        "bankPayments": service.bank_payments_list(request),
        "bankLineMatches": service.bank_line_matches_list(request),
        "bankLineSubjectAssociations": service.bank_line_subject_associations_list(request),
        "balanceModifiers": service.balance_modifiers_list(request),
    }

    for root, result in results.items():
        assert isinstance(result, BaseModel)
        assert result.model_dump()[root] == [{"id": root, "marker": "synthetic"}]
    assert results["bankPayments"].model_dump()["meta"] == {
        "paging": {"page": 2, "pageSize": 25, "total": 26}
    }
    for root in tuple(list_roots)[1:]:
        assert results[list_roots[root]].model_dump().get("meta") is None
    assert [request.url.path for request in requests] == list(list_roots)
    expected_query = httpx.QueryParams(
        {
            "page": "2",
            "pageSize": "25",
            "include": "related",
            "sortProperty": "createdTime",
            "sortDirection": "DESC",
        }
    )
    assert all(request.url.params == expected_query for request in requests)
    assert {key for key, _ in requests[0].url.params.multi_items()} == {
        "page",
        "pageSize",
        "include",
        "sortProperty",
        "sortDirection",
    }


def test_bank_lines_list_requires_account_id_and_sends_documented_filters(
    client_factory: ClientFactory,
) -> None:
    """Given official bank-line list filters, When listing, Then the query is exact."""

    client, requests = client_factory(
        lambda request: httpx.Response(200, json={"bankLines": [{"id": "line-1"}]})
    )
    request = BankLinesListRequest(
        accountId="account-1",
        page=2,
        pageSize=25,
        include="related",
        sortProperty=BankLineSortProperty.ENTRY_DATE,
        sortDirection=SortDirection.DESC,
        isReconciled=True,
        status=BankLineStatus.BOOKED,
        side=BankLineSide.DEBIT,
        externalId="ext-1",
        receiptState="missing_receipt",
        minAmount=10.5,
        maxAmount=20.0,
        minEntryDate="2026-01-01",
        maxEntryDate="2026-01-31",
        entryDatePeriod="month:2026-01",
        q="rent",
    )

    result = BankReadService(client).bank_lines_list(request)

    assert isinstance(result, BaseModel)
    assert result.model_dump() == {"bankLines": [{"id": "line-1"}]}
    assert [captured.url.path for captured in requests] == ["/v2/bankLines"]
    assert all("/accounts" not in str(captured.url) for captured in requests)
    assert requests[0].url.params == httpx.QueryParams(
        {
            "page": "2",
            "pageSize": "25",
            "include": "related",
            "sortProperty": "entryDate",
            "sortDirection": "DESC",
            "accountId": "account-1",
            "isReconciled": "true",
            "status": "booked",
            "side": "debit",
            "externalId": "ext-1",
            "receiptState": "missing_receipt",
            "minAmount": "10.5",
            "maxAmount": "20.0",
            "minEntryDate": "2026-01-01",
            "maxEntryDate": "2026-01-31",
            "entryDatePeriod": "month:2026-01",
            "q": "rent",
        }
    )


def test_bank_lines_list_omits_unset_optional_filters(
    client_factory: ClientFactory,
) -> None:
    """Given only accountId, When listing bank lines, Then optionals are omitted."""

    client, requests = client_factory(
        lambda request: httpx.Response(200, json={"bankLines": [], "meta": {}})
    )

    result = BankReadService(client).bank_lines_list(BankLinesListRequest(accountId="account-1"))

    assert isinstance(result, BaseModel)
    assert result.model_dump() == {"bankLines": [], "meta": {}}
    assert requests[0].url.params == httpx.QueryParams(
        {"page": "1", "pageSize": "1000", "accountId": "account-1"}
    )


def test_collection_reads_preserve_an_absent_optional_meta_root(
    client_factory: ClientFactory,
) -> None:
    client, requests = client_factory(
        lambda request: httpx.Response(200, json={"balanceModifiers": []})
    )

    result = BankReadService(client).balance_modifiers_list(BankListRequest())

    assert isinstance(result, BaseModel)
    assert result.model_dump() == {"balanceModifiers": []}
    assert requests[0].url.params == httpx.QueryParams({"page": "1", "pageSize": "1000"})


def test_collection_reads_preserve_meta_without_an_undocumented_paging_field(
    client_factory: ClientFactory,
) -> None:
    client, _ = client_factory(
        lambda request: httpx.Response(200, json={"bankLineMatches": [], "meta": {}})
    )

    result = BankReadService(client).bank_line_matches_list(BankListRequest())

    assert isinstance(result, BaseModel)
    assert result.model_dump() == {"bankLineMatches": [], "meta": {}}


@pytest.mark.parametrize(
    ("request_type", "arguments", "field"),
    [
        (BankGetRequest, {"id": ""}, "id"),
        (BankGetRequest, {"id": "bank-1", "include": ""}, "include"),
        (BankGetRequest, {"id": "bank-1", "unexpected": True}, "unexpected"),
        (BankListRequest, {"page": 0}, "page"),
        (BankListRequest, {"pageSize": 0}, "pageSize"),
        (BankListRequest, {"pageSize": 1001}, "pageSize"),
        (BankListRequest, {"include": ""}, "include"),
        (BankListRequest, {"sortProperty": ""}, "sortProperty"),
        (BankListRequest, {"sortDirection": "DOWN"}, "sortDirection"),
        (BankListRequest, {"offset": 1}, "offset"),
        (BankListRequest, {"organizationId": "organization-1"}, "organizationId"),
        (BankListRequest, {"accountId": "account-1"}, "accountId"),
        (BankListRequest, {"matchId": "match-1"}, "matchId"),
        (BankListRequest, {"bankLineId": "line-1"}, "bankLineId"),
        (BankListRequest, {"subjectId": "subject-1"}, "subjectId"),
        (BankListRequest, {"contactId": "contact-1"}, "contactId"),
        (BankListRequest, {"q": "synthetic"}, "q"),
        (BankLinesListRequest, {}, "accountId"),
        (BankLinesListRequest, {"accountId": ""}, "accountId"),
        (
            BankLinesListRequest,
            {"accountId": "account-1", "sortProperty": "createdTime"},
            "sortProperty",
        ),
        (BankLinesListRequest, {"accountId": "account-1", "status": "draft"}, "status"),
        (BankLinesListRequest, {"accountId": "account-1", "side": "asset"}, "side"),
        (BankLinesListRequest, {"accountId": "account-1", "offset": 1}, "offset"),
        (
            BankLinesListRequest,
            {"accountId": "account-1", "organizationId": "organization-1"},
            "organizationId",
        ),
        (BankLinesListRequest, {"accountId": "account-1", "matchId": "match-1"}, "matchId"),
    ],
)
def test_requests_reject_invalid_values_and_undeclared_filters(
    request_type: type[BaseModel], arguments: dict[str, object], field: str
) -> None:
    with pytest.raises(ValidationError) as failure:
        request_type.model_validate(arguments)

    assert failure.value.errors()[0]["loc"] == (field,)


@pytest.mark.parametrize("error_code", ["AUTHENTICATION_REQUIRED", "OAUTH_INVALID_ACCESS_TOKEN"])
def test_all_tools_preserve_typed_authentication_errors(
    client_factory: ClientFactory, error_code: str
) -> None:
    client, requests = client_factory(
        lambda request: httpx.Response(401, json={"errorCode": error_code})
    )
    service = BankReadService(client)
    get_request = BankGetRequest(id="bank-1")
    list_request = BankListRequest()
    bank_lines_request = BankLinesListRequest(accountId="account-1")
    results = [
        service.bank_payments_get(get_request),
        service.bank_payments_list(list_request),
        service.bank_line_matches_get(get_request),
        service.bank_line_matches_list(list_request),
        service.bank_lines_get(get_request),
        service.bank_lines_list(bank_lines_request),
        service.bank_line_subject_associations_get(get_request),
        service.bank_line_subject_associations_list(list_request),
        service.balance_modifiers_get(get_request),
        service.balance_modifiers_list(list_request),
    ]

    assert all(isinstance(result, ToolError) for result in results)
    assert {result.code for result in results if isinstance(result, ToolError)} == {
        StableErrorCode.AUTH_REQUIRED
    }
    assert [request.url.path for request in requests] == [
        "/v2/bankPayments/bank-1",
        "/v2/bankPayments",
        "/v2/bankLineMatches/bank-1",
        "/v2/bankLineMatches",
        "/v2/bankLines/bank-1",
        "/v2/bankLines",
        "/v2/bankLineSubjectAssociations/bank-1",
        "/v2/bankLineSubjectAssociations",
        "/v2/balanceModifiers/bank-1",
        "/v2/balanceModifiers",
    ]


def test_undeclared_response_root_returns_a_typed_error(client_factory: ClientFactory) -> None:
    client, _ = client_factory(lambda request: httpx.Response(200, json={"wrong": {}}))

    result = BankReadService(client).bank_lines_get(BankGetRequest(id="line-1"))

    assert isinstance(result, ToolError)
    assert result.code is StableErrorCode.BILLY_ERROR
    assert result.details == {"expected_root": "bankLine"}


def test_registration_exposes_exactly_the_ten_bank_and_balance_tools(
    client_factory: ClientFactory,
) -> None:
    list_roots = {
        "/v2/bankPayments": "bankPayments",
        "/v2/bankLineMatches": "bankLineMatches",
        "/v2/bankLines": "bankLines",
        "/v2/bankLineSubjectAssociations": "bankLineSubjectAssociations",
        "/v2/balanceModifiers": "balanceModifiers",
    }
    client, requests = client_factory(
        lambda request: httpx.Response(200, json={list_roots[request.url.path]: []})
    )
    server = FastMCP("bank-reads-contract-test")

    register_bank_read_tools(server, client)

    tools = {tool.name: tool for tool in asyncio.run(server.list_tools())}
    assert set(tools) == {
        "api_bank_payments_get",
        "api_bank_payments_list",
        "api_bank_line_matches_get",
        "api_bank_line_matches_list",
        "api_bank_lines_get",
        "api_bank_lines_list",
        "api_bank_line_subject_associations_get",
        "api_bank_line_subject_associations_list",
        "api_balance_modifiers_get",
        "api_balance_modifiers_list",
    }
    for name in {
        "api_bank_payments_get",
        "api_bank_line_matches_get",
        "api_bank_lines_get",
        "api_bank_line_subject_associations_get",
        "api_balance_modifiers_get",
    }:
        assert set(tools[name].parameters["properties"]) == {"id", "include"}
    for name in {
        "api_bank_payments_list",
        "api_bank_line_matches_list",
        "api_bank_line_subject_associations_list",
        "api_balance_modifiers_list",
    }:
        assert set(tools[name].parameters["properties"]) == {
            "page",
            "pageSize",
            "include",
            "sortProperty",
            "sortDirection",
        }
    assert set(tools["api_bank_lines_list"].parameters["properties"]) == {
        "page",
        "pageSize",
        "include",
        "sortProperty",
        "sortDirection",
        "accountId",
        "isReconciled",
        "status",
        "side",
        "externalId",
        "receiptState",
        "minAmount",
        "maxAmount",
        "minEntryDate",
        "maxEntryDate",
        "entryDatePeriod",
        "q",
    }
    assert "accountId" in tools["api_bank_lines_list"].parameters.get("required", [])
    result = asyncio.run(server.call_tool("api_bank_payments_list", {"page": 1, "pageSize": 1000}))
    assert result.structured_content == {"result": {"bankPayments": []}}
    assert [request.url.path for request in requests] == ["/v2/bankPayments"]
