"""Synthetic contract tests for typed, read-only Billy ledger and users tools."""

from __future__ import annotations

import httpx
import pytest
from fastmcp import FastMCP
from pydantic import BaseModel, ValidationError

from billy_mcp.api.ledger_user_reads import (
    PostingGetRequest,
    PostingGetSuccess,
    PostingsListRequest,
    PostingsListSuccess,
    SortDirection,
    TransactionGetRequest,
    TransactionGetSuccess,
    TransactionsListRequest,
    TransactionsListSuccess,
    UserGetRequest,
    UserGetSuccess,
    UsersListRequest,
    UsersListSuccess,
    get_posting,
    get_transaction,
    get_user,
    list_postings,
    list_transactions,
    list_users,
    register_ledger_user_read_tools,
)
from billy_mcp.client import BillyHttpClient
from billy_mcp.models import StableErrorCode, ToolError


def make_client(handler: httpx.MockTransport) -> BillyHttpClient:
    """Create a token-backed locked client against an in-process mock transport."""

    return BillyHttpClient(lambda: "test-token", transport=handler)


def test_gets_use_documented_encoded_paths_and_singular_roots() -> None:
    requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        roots = {
            "/v2/transactions/transaction /?": "transaction",
            "/v2/postings/posting /?": "posting",
            "/v2/users/user /?": "user",
        }
        root = roots[request.url.path]
        return httpx.Response(200, json={root: {"id": root, "name": root}})

    client = make_client(httpx.MockTransport(handler))
    transaction = get_transaction(
        client, TransactionGetRequest(id="transaction /?", include="postings")
    )
    posting = get_posting(client, PostingGetRequest(id="posting /?", include="transaction"))
    user = get_user(client, UserGetRequest(id="user /?", include="profilePicFile"))

    assert isinstance(transaction, TransactionGetSuccess)
    assert isinstance(posting, PostingGetSuccess)
    assert isinstance(user, UserGetSuccess)
    assert transaction.transaction.model_dump() == {"id": "transaction", "name": "transaction"}
    assert posting.posting.model_dump() == {"id": "posting", "name": "posting"}
    assert user.user.model_dump() == {"id": "user", "name": "user"}
    assert [str(request.url) for request in requests] == [
        "https://api.billysbilling.com/v2/transactions/transaction%20%2F%3F?include=postings",
        "https://api.billysbilling.com/v2/postings/posting%20%2F%3F?include=transaction",
        "https://api.billysbilling.com/v2/users/user%20%2F%3F?include=profilePicFile",
    ]
    assert all(request.method == "GET" for request in requests)


def test_gets_omit_the_optional_include_query_when_absent() -> None:
    requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        roots = {
            "/v2/transactions/transaction-1": "transaction",
            "/v2/postings/posting-1": "posting",
            "/v2/users/user-1": "user",
        }
        root = roots[request.url.path]
        return httpx.Response(200, json={root: {"id": root}})

    client = make_client(httpx.MockTransport(handler))
    assert isinstance(
        get_transaction(client, TransactionGetRequest(id="transaction-1")), TransactionGetSuccess
    )
    assert isinstance(get_posting(client, PostingGetRequest(id="posting-1")), PostingGetSuccess)
    assert isinstance(get_user(client, UserGetRequest(id="user-1")), UserGetSuccess)
    assert all(not request.url.params for request in requests)


def test_lists_use_exact_query_allowlist_and_map_roots_with_paging() -> None:
    requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        roots = {
            "/v2/transactions": "transactions",
            "/v2/postings": "postings",
            "/v2/users": "users",
        }
        root = roots[request.url.path]
        return httpx.Response(
            200,
            json={
                root: [{"id": root, "name": root}],
                "meta": {
                    "paging": {
                        "page": 2,
                        "pageCount": 3,
                        "pageSize": 50,
                        "total": 125,
                        "firstUrl": f"/{root}?page=1",
                        "previousUrl": f"/{root}?page=1",
                        "nextUrl": f"/{root}?page=3",
                        "lastUrl": f"/{root}?page=3",
                    }
                },
            },
        )

    client = make_client(httpx.MockTransport(handler))
    transactions = list_transactions(
        client,
        TransactionsListRequest(
            page=2,
            pageSize=50,
            include="postings",
            sortProperty="entryDate",
            sortDirection=SortDirection.ASC,
        ),
    )
    postings = list_postings(
        client,
        PostingsListRequest(
            page=2,
            pageSize=50,
            include="account",
            sortProperty="amount",
            sortDirection=SortDirection.DESC,
        ),
    )
    users = list_users(
        client,
        UsersListRequest(
            page=2,
            pageSize=50,
            include="profilePicFile",
            sortProperty="name",
            sortDirection=SortDirection.ASC,
        ),
    )

    assert isinstance(transactions, TransactionsListSuccess)
    assert isinstance(postings, PostingsListSuccess)
    assert isinstance(users, UsersListSuccess)
    assert transactions.transactions[0].model_dump() == {
        "id": "transactions",
        "name": "transactions",
    }
    assert postings.postings[0].model_dump() == {"id": "postings", "name": "postings"}
    assert users.users[0].model_dump() == {"id": "users", "name": "users"}
    assert transactions.meta is not None and transactions.meta.paging is not None
    assert postings.meta is not None and postings.meta.paging is not None
    assert users.meta is not None and users.meta.paging is not None
    assert transactions.meta.paging.page_count == 3
    assert postings.meta.paging.next_url == "/postings?page=3"
    assert users.meta.paging.page_size == 50
    assert [request.url.params for request in requests] == [
        httpx.QueryParams(
            {
                "page": "2",
                "pageSize": "50",
                "include": "postings",
                "sortProperty": "entryDate",
                "sortDirection": "ASC",
            }
        ),
        httpx.QueryParams(
            {
                "page": "2",
                "pageSize": "50",
                "include": "account",
                "sortProperty": "amount",
                "sortDirection": "DESC",
            }
        ),
        httpx.QueryParams(
            {
                "page": "2",
                "pageSize": "50",
                "include": "profilePicFile",
                "sortProperty": "name",
                "sortDirection": "ASC",
            }
        ),
    ]
    assert all(
        {key for key, _ in request.url.params.multi_items()}
        == {"page", "pageSize", "include", "sortProperty", "sortDirection"}
        for request in requests
    )


def test_lists_preserve_absent_meta_and_send_documented_defaults() -> None:
    requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        roots = {
            "/v2/transactions": "transactions",
            "/v2/postings": "postings",
            "/v2/users": "users",
        }
        return httpx.Response(200, json={roots[request.url.path]: []})

    client = make_client(httpx.MockTransport(handler))
    transactions = list_transactions(client, TransactionsListRequest())
    postings = list_postings(client, PostingsListRequest())
    users = list_users(client, UsersListRequest())

    assert isinstance(transactions, TransactionsListSuccess)
    assert isinstance(postings, PostingsListSuccess)
    assert isinstance(users, UsersListSuccess)
    assert transactions.model_dump() == {"transactions": []}
    assert postings.model_dump() == {"postings": []}
    assert users.model_dump() == {"users": []}
    assert [request.url.params for request in requests] == [
        httpx.QueryParams({"page": "1", "pageSize": "1000"}),
        httpx.QueryParams({"page": "1", "pageSize": "1000"}),
        httpx.QueryParams({"page": "1", "pageSize": "1000"}),
    ]


@pytest.mark.parametrize(
    ("request_type", "values", "field"),
    [
        (TransactionGetRequest, {"id": ""}, "id"),
        (PostingGetRequest, {"id": "posting-1", "include": ""}, "include"),
        (UserGetRequest, {"id": "user-1", "request": {}}, "request"),
        (TransactionGetRequest, {"id": "transaction-1", "offset": 1}, "offset"),
        (TransactionsListRequest, {"page": 0}, "page"),
        (PostingsListRequest, {"pageSize": 0}, "pageSize"),
        (UsersListRequest, {"pageSize": 1001}, "pageSize"),
        (TransactionsListRequest, {"include": ""}, "include"),
        (PostingsListRequest, {"sortProperty": ""}, "sortProperty"),
        (UsersListRequest, {"sortDirection": "DOWN"}, "sortDirection"),
        (TransactionsListRequest, {"offset": 1}, "offset"),
        (PostingsListRequest, {"request": {}}, "request"),
        (UsersListRequest, {"organizationId": "organization-1"}, "organizationId"),
        (TransactionsListRequest, {"postingId": "posting-1"}, "postingId"),
        (PostingsListRequest, {"userId": "user-1"}, "userId"),
        (UsersListRequest, {"q": "Ada"}, "q"),
    ],
)
def test_request_models_reject_invalid_values_and_all_undeclared_fields(
    request_type: type[BaseModel], values: dict[str, object], field: str
) -> None:
    with pytest.raises(ValidationError) as failure:
        request_type.model_validate(values)

    assert failure.value.errors()[0]["loc"] == (field,)


@pytest.mark.parametrize("error_code", ["AUTHENTICATION_REQUIRED", "OAUTH_INVALID_ACCESS_TOKEN"])
def test_documented_authentication_errors_remain_typed_for_every_tool(error_code: str) -> None:
    client = make_client(
        httpx.MockTransport(lambda request: httpx.Response(401, json={"errorCode": error_code}))
    )
    results = (
        get_transaction(client, TransactionGetRequest(id="transaction-1")),
        get_posting(client, PostingGetRequest(id="posting-1")),
        get_user(client, UserGetRequest(id="user-1")),
        list_transactions(client, TransactionsListRequest()),
        list_postings(client, PostingsListRequest()),
        list_users(client, UsersListRequest()),
    )

    assert all(isinstance(result, ToolError) for result in results)
    assert {result.code for result in results if isinstance(result, ToolError)} == {
        StableErrorCode.AUTH_REQUIRED
    }


def test_malformed_documented_roots_return_typed_errors() -> None:
    client = make_client(
        httpx.MockTransport(lambda request: httpx.Response(200, json={"wrong": {}}))
    )
    results = (
        get_transaction(client, TransactionGetRequest(id="transaction-1")),
        get_posting(client, PostingGetRequest(id="posting-1")),
        get_user(client, UserGetRequest(id="user-1")),
        list_transactions(client, TransactionsListRequest()),
        list_postings(client, PostingsListRequest()),
        list_users(client, UsersListRequest()),
    )

    assert all(isinstance(result, ToolError) for result in results)
    assert {
        result.details["expected_root"] for result in results if isinstance(result, ToolError)
    } == {
        "transaction",
        "posting",
        "user",
        "transactions",
        "postings",
        "users",
    }
    assert {result.code for result in results if isinstance(result, ToolError)} == {
        StableErrorCode.BILLY_ERROR
    }


def test_malformed_meta_root_returns_a_typed_error() -> None:
    result = list_transactions(
        make_client(
            httpx.MockTransport(
                lambda request: httpx.Response(200, json={"transactions": [], "meta": []})
            )
        ),
        TransactionsListRequest(),
    )

    assert isinstance(result, ToolError)
    assert result.code is StableErrorCode.BILLY_ERROR
    assert result.details == {"expected_root": "meta"}


@pytest.mark.asyncio
async def test_registration_exposes_exactly_six_flat_tools_and_structured_output() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        singular_roots = {
            "/v2/transactions/transaction-1": "transaction",
            "/v2/postings/posting-1": "posting",
            "/v2/users/user-1": "user",
        }
        list_roots = {
            "/v2/transactions": "transactions",
            "/v2/postings": "postings",
            "/v2/users": "users",
        }
        if request.url.path in singular_roots:
            root = singular_roots[request.url.path]
            return httpx.Response(200, json={root: {"id": root}})
        root = list_roots[request.url.path]
        return httpx.Response(200, json={root: []})

    server = FastMCP("ledger-user-reads-test")
    register_ledger_user_read_tools(server, make_client(httpx.MockTransport(handler)))

    tools = {tool.name: tool for tool in await server.list_tools()}
    assert set(tools) == {
        "api_transactions_get",
        "api_transactions_list",
        "api_postings_get",
        "api_postings_list",
        "api_users_get",
        "api_users_list",
    }
    for name in ("api_transactions_get", "api_postings_get", "api_users_get"):
        parameters = tools[name].parameters
        assert set(parameters["properties"]) == {"id", "include"}
        assert parameters["required"] == ["id"]
        assert "request" not in parameters["properties"]
    for name in ("api_transactions_list", "api_postings_list", "api_users_list"):
        properties = tools[name].parameters["properties"]
        assert set(properties) == {"page", "pageSize", "include", "sortProperty", "sortDirection"}
        assert "offset" not in properties
        assert "request" not in properties
        assert "organizationId" not in properties
    assert (
        await server.call_tool("api_transactions_get", {"id": "transaction-1"})
    ).structured_content == {"result": {"transaction": {"id": "transaction"}}}
    assert (await server.call_tool("api_postings_get", {"id": "posting-1"})).structured_content == {
        "result": {"posting": {"id": "posting"}}
    }
    assert (await server.call_tool("api_users_get", {"id": "user-1"})).structured_content == {
        "result": {"user": {"id": "user"}}
    }
    assert (
        await server.call_tool("api_transactions_list", {"page": 1, "pageSize": 1000})
    ).structured_content == {"result": {"transactions": []}}
    assert (
        await server.call_tool("api_postings_list", {"page": 1, "pageSize": 1000})
    ).structured_content == {"result": {"postings": []}}
    assert (
        await server.call_tool("api_users_list", {"page": 1, "pageSize": 1000})
    ).structured_content == {"result": {"users": []}}
