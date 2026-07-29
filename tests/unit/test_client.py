from __future__ import annotations

import httpx
import pytest

from billy_mcp.client import BillyHttpClient, BillyResponse, RequestConstructionError
from billy_mcp.models import StableErrorCode, ToolError


def test_client_is_locked_to_official_host_and_documented_paging() -> None:
    requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return httpx.Response(200, json={"products": []})

    client = BillyHttpClient(lambda: "secret", transport=httpx.MockTransport(handler))
    result = client.list("/products", page=2, page_size=100)

    assert isinstance(result, BillyResponse)
    assert str(requests[0].url) == "https://api.billysbilling.com/v2/products?page=2&pageSize=100"
    assert requests[0].headers["x-access-token"] == "secret"
    assert "authorization" not in requests[0].headers
    with pytest.raises(RequestConstructionError):
        client.request("GET", "https://api.billy.dk/v2/products")
    with pytest.raises(RequestConstructionError):
        client.request("GET", "/products?offset=0")
    with pytest.raises(RequestConstructionError):
        client.request("GET", "/products", params={"offset": 0})
    with pytest.raises(RequestConstructionError):
        client.list("/products", page=0)
    with pytest.raises(RequestConstructionError):
        client.list("/products", page_size=1001)


@pytest.mark.parametrize("path", ["/v2", "/v2/products", "/v2/products/123"])
def test_client_rejects_duplicate_fixed_api_prefix_before_request(path: str) -> None:
    requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return httpx.Response(200, json={})

    client = BillyHttpClient(lambda: "secret", transport=httpx.MockTransport(handler))

    with pytest.raises(RequestConstructionError, match="omit the fixed /v2 prefix"):
        client.request("GET", path)

    assert requests == []


def test_client_translates_documented_logger_prefixed_401() -> None:
    body = (
        "LOGGER ERROR: Authentication strategy does not have an access token.\n"
        '{"errorCode":"OAUTH_INVALID_ACCESS_TOKEN","meta":{"statusCode":401}}'
    )
    client = BillyHttpClient(
        lambda: "invalid",
        transport=httpx.MockTransport(lambda request: httpx.Response(401, text=body)),
    )

    result = client.request("GET", "/products")

    assert isinstance(result, ToolError)
    assert result.code is StableErrorCode.AUTH_REQUIRED


def test_client_retries_only_safe_reads() -> None:
    attempts: list[str] = []

    def handler(request: httpx.Request) -> httpx.Response:
        attempts.append(request.method)
        if request.method == "GET" and attempts.count("GET") == 1:
            return httpx.Response(503, json={"errorCode": "TEMPORARY"})
        if request.method == "POST":
            return httpx.Response(503, json={"errorCode": "TEMPORARY"})
        return httpx.Response(200, json={"ok": True})

    client = BillyHttpClient(lambda: "secret", transport=httpx.MockTransport(handler))

    assert isinstance(client.request("GET", "/products"), BillyResponse)
    assert attempts == ["GET", "GET"]

    attempts.clear()
    failed_write = client.request("POST", "/products", json_body={"product": {}})
    assert isinstance(failed_write, ToolError)
    assert attempts == ["POST"]
