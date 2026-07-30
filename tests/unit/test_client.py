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


def test_file_upload_posts_exact_raw_bytes_and_documented_headers_once() -> None:
    requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return httpx.Response(200, json={"files": []})

    client = BillyHttpClient(lambda: "secret", transport=httpx.MockTransport(handler))
    result = client.post_file(
        file_bytes=b"innocuous upload bytes",
        filename="note.txt",
        content_type="text/plain",
        create_attachment=True,
        create_variants=True,
        organization_id="org-1",
        should_scan=True,
    )

    assert isinstance(result, BillyResponse)
    assert len(requests) == 1
    request = requests[0]
    assert str(request.url) == "https://api.billysbilling.com/v2/files"
    assert request.content == b"innocuous upload bytes"
    assert request.headers["x-access-token"] == "secret"
    assert request.headers["accept"] == "application/json"
    assert request.headers["x-filename"] == "note.txt"
    assert request.headers["content-type"] == "text/plain"
    assert request.headers["x-create-attachment"] == "true"
    assert request.headers["x-create-variants"] == "true"
    assert request.headers["x-organizationid"] == "org-1"
    assert request.headers["x-should-scan"] == "true"


def test_file_upload_omits_optional_headers_and_never_retries() -> None:
    requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return httpx.Response(503, json={"errorCode": "TEMPORARY"})

    client = BillyHttpClient(lambda: "secret", transport=httpx.MockTransport(handler))
    result = client.post_file(
        file_bytes=b"x",
        filename="note.txt",
        content_type="text/plain",
    )

    assert isinstance(result, ToolError)
    assert len(requests) == 1
    headers = requests[0].headers
    assert "x-create-attachment" not in headers
    assert "x-create-variants" not in headers
    assert "x-organizationid" not in headers
    assert "x-should-scan" not in headers


@pytest.mark.parametrize(
    ("filename", "content_type", "organization_id"),
    [
        ("note.txt\r\nX-Injected: value", "text/plain", None),
        ("note.txt", "text/plain\r\nX-Injected: value", None),
        ("note.txt", "text/plain", "org-1\r\nX-Injected: value"),
    ],
)
def test_file_upload_rejects_header_injection_before_request(
    filename: str, content_type: str, organization_id: str | None
) -> None:
    requests: list[httpx.Request] = []
    client = BillyHttpClient(
        lambda: "secret",
        transport=httpx.MockTransport(
            lambda request: requests.append(request) or httpx.Response(200, json={"files": []})
        ),
    )

    with pytest.raises(RequestConstructionError, match="must not contain CR or LF"):
        client.post_file(
            file_bytes=b"x",
            filename=filename,
            content_type=content_type,
            organization_id=organization_id,
        )

    assert requests == []
