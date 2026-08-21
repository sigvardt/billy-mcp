"""Locked HTTP client for the official Billy API host."""

from __future__ import annotations

import json
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from urllib.parse import urlsplit

import httpx

from billy_mcp.config import API_BASE_URL
from billy_mcp.errors import translate_upstream_error
from billy_mcp.models import StableErrorCode, ToolError

MAX_PAGE_SIZE = 1000
DEFAULT_PAGE_SIZE = 1000
_RETRYABLE_STATUSES = {429, 500, 502, 503, 504}
_RETRY_SAFE_METHODS = {"GET", "HEAD"}


class RequestConstructionError(ValueError):
    """Raised before a request that violates the fixed API contract is sent."""


@dataclass(frozen=True)
class BillyResponse:
    """A parsed successful response from the one permitted API host."""

    status_code: int
    data: object


def parse_billy_json(content: str) -> object:
    """Parse a JSON body after the researched optional logger prefix."""

    object_start = content.find("{")
    array_start = content.find("[")
    starts = [position for position in (object_start, array_start) if position >= 0]
    if not starts:
        raise ValueError("Billy response did not contain JSON")
    return json.loads(content[min(starts) :])


class BillyHttpClient:
    """Synchronous client with an immutable host and read-only retry semantics."""

    def __init__(
        self,
        token_provider: Callable[[], str | None],
        *,
        transport: httpx.BaseTransport | None = None,
        max_read_retries: int = 1,
    ) -> None:
        if max_read_retries < 0:
            raise ValueError("max_read_retries must be non-negative")
        self._token_provider = token_provider
        self._max_read_retries = max_read_retries
        self._client = httpx.Client(transport=transport, timeout=20.0)

    def close(self) -> None:
        self._client.close()

    def __enter__(self) -> BillyHttpClient:
        return self

    def __exit__(self, *_: object) -> None:
        self.close()

    def list(
        self, path: str, *, page: int = 1, page_size: int = DEFAULT_PAGE_SIZE
    ) -> BillyResponse | ToolError:
        """Construct documented collection paging with no offset escape hatch."""

        if page < 1:
            raise RequestConstructionError("page must be at least 1")
        if not 1 <= page_size <= MAX_PAGE_SIZE:
            raise RequestConstructionError("pageSize must be between 1 and 1000")
        return self.request("GET", path, params={"page": page, "pageSize": page_size})

    def request(
        self,
        method: str,
        path: str,
        *,
        params: Mapping[str, str | int | float | bool] | None = None,
        json_body: object | None = None,
    ) -> BillyResponse | ToolError:
        """Call only a relative path beneath the official `v2` base URL."""

        url = self._url_for(path)
        self._validate_query_params(params)
        token = self._token_provider()
        if not token:
            return ToolError(
                code=StableErrorCode.AUTH_REQUIRED,
                message="Billy API token is unavailable.",
            )
        normalized_method = method.upper()
        retries = self._max_read_retries if normalized_method in _RETRY_SAFE_METHODS else 0
        headers = {"X-Access-Token": token, "Accept": "application/json"}
        for attempt in range(retries + 1):
            try:
                response = self._client.request(
                    normalized_method,
                    url,
                    headers=headers,
                    params=params,
                    json=json_body,
                )
            except httpx.TransportError:
                if attempt < retries:
                    continue
                return ToolError(
                    code=StableErrorCode.BILLY_ERROR,
                    message="Billy API request could not be completed.",
                )
            if response.status_code in _RETRYABLE_STATUSES and attempt < retries:
                continue
            body: object
            try:
                body = parse_billy_json(response.text)
            except (TypeError, ValueError, json.JSONDecodeError):
                body = {}
            if response.is_error:
                return translate_upstream_error(response.status_code, body)
            return BillyResponse(status_code=response.status_code, data=body)
        raise AssertionError("retry loop must return")

    def post_file(
        self,
        *,
        file_bytes: bytes,
        filename: str,
        content_type: str,
        create_attachment: bool = False,
        create_variants: bool = False,
        organization_id: str | None = None,
        should_scan: bool = False,
    ) -> BillyResponse | ToolError:
        """Upload raw bytes to the one documented Billy files endpoint once."""

        _validate_file_header_value(filename, "X-Filename")
        _validate_file_header_value(content_type, "Content-Type")
        if organization_id is not None:
            _validate_file_header_value(organization_id, "x-organizationid")

        token = self._token_provider()
        if not token:
            return ToolError(
                code=StableErrorCode.AUTH_REQUIRED,
                message="Billy API token is unavailable.",
            )
        headers = {
            "X-Access-Token": token,
            "Accept": "application/json",
            "X-Filename": filename,
            "Content-Type": content_type,
        }
        if create_attachment:
            headers["x-create-attachment"] = "true"
        if create_variants:
            headers["x-create-variants"] = "true"
        if organization_id is not None:
            headers["x-organizationid"] = organization_id
        if should_scan:
            headers["x-should-scan"] = "true"

        try:
            response = self._client.request(
                "POST",
                self._url_for("/files"),
                headers=headers,
                content=file_bytes,
            )
        except httpx.TransportError:
            return ToolError(
                code=StableErrorCode.BILLY_ERROR,
                message="Billy API request could not be completed.",
            )
        body: object
        try:
            body = parse_billy_json(response.text)
        except (TypeError, ValueError, json.JSONDecodeError):
            body = {}
        if response.is_error:
            return translate_upstream_error(response.status_code, body)
        return BillyResponse(status_code=response.status_code, data=body)

    @staticmethod
    def _url_for(path: str) -> str:
        parsed = urlsplit(path)
        if parsed.scheme or parsed.netloc or parsed.query or parsed.fragment:
            raise RequestConstructionError("Only relative Billy API paths are permitted")
        if not path.startswith("/") or ".." in parsed.path.split("/"):
            raise RequestConstructionError("API path must be an absolute relative path below /v2")
        if parsed.path == "/v2" or parsed.path.startswith("/v2/"):
            raise RequestConstructionError("API paths must omit the fixed /v2 prefix")
        return f"{API_BASE_URL}{parsed.path}"

    @staticmethod
    def _validate_query_params(params: Mapping[str, str | int | float | bool] | None) -> None:
        if params is None:
            return
        if "offset" in params:
            raise RequestConstructionError(
                "offset paging is not part of the documented Billy API contract"
            )
        page = params.get("page")
        if page is not None and (isinstance(page, bool) or not isinstance(page, int) or page < 1):
            raise RequestConstructionError("page must be an integer of at least 1")
        page_size = params.get("pageSize")
        if page_size is not None and (
            isinstance(page_size, bool)
            or not isinstance(page_size, int)
            or not 1 <= page_size <= MAX_PAGE_SIZE
        ):
            raise RequestConstructionError("pageSize must be an integer between 1 and 1000")


def _validate_file_header_value(value: str, header_name: str) -> None:
    """Reject blank or line-breaking values before they can add wire headers."""

    if not value.strip():
        raise RequestConstructionError(f"{header_name} must be non-empty")
    if "\r" in value or "\n" in value:
        raise RequestConstructionError(f"{header_name} must not contain CR or LF")
