"""Contract tests for the typed, read-only Billy file and attachment tools."""

from __future__ import annotations

import asyncio
from collections.abc import Callable

import httpx
import pytest
from fastmcp import FastMCP
from pydantic import ValidationError

from billy_mcp.api.file_attachment_reads import (
    AttachmentGetSuccess,
    AttachmentsListSuccess,
    FileAttachmentGetRequest,
    FileAttachmentListRequest,
    FileAttachmentReadService,
    FileGetSuccess,
    FilesListSuccess,
    SortDirection,
    register_file_attachment_read_tools,
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


def test_singular_reads_encode_ids_and_map_documented_roots(
    client_factory: ClientFactory,
) -> None:
    file_client, file_requests = client_factory(
        lambda request: httpx.Response(200, json={"file": {"id": "file/id 1"}})
    )
    attachment_client, attachment_requests = client_factory(
        lambda request: httpx.Response(
            200, json={"attachment": {"id": "attachment/id 1", "priority": 1}}
        )
    )

    file_result = FileAttachmentReadService(file_client).files_get(
        FileAttachmentGetRequest(id="file/id 1", include="owner")
    )
    attachment_result = FileAttachmentReadService(attachment_client).attachments_get(
        FileAttachmentGetRequest(id="attachment/id 1")
    )

    assert isinstance(file_result, FileGetSuccess)
    assert file_result.file.model_dump() == {"id": "file/id 1"}
    assert str(file_requests[0].url) == (
        "https://api.billysbilling.com/v2/files/file%2Fid%201?include=owner"
    )
    assert isinstance(attachment_result, AttachmentGetSuccess)
    assert attachment_result.attachment.model_dump() == {"id": "attachment/id 1", "priority": 1}
    assert str(attachment_requests[0].url) == (
        "https://api.billysbilling.com/v2/attachments/attachment%2Fid%201"
    )


def test_list_reads_use_only_documented_query_parameters_and_map_optional_paging(
    client_factory: ClientFactory,
) -> None:
    files_client, file_requests = client_factory(
        lambda request: httpx.Response(
            200,
            json={
                "files": [{"id": "file-1", "fileName": "invoice.pdf"}],
                "meta": {"paging": {"page": 2, "pageCount": 3, "pageSize": 25, "total": 56}},
            },
        )
    )
    attachments_client, attachment_requests = client_factory(
        lambda request: httpx.Response(200, json={"attachments": [{"id": "attachment-1"}]})
    )
    request = FileAttachmentListRequest(
        page=2,
        pageSize=25,
        include="file",
        sortProperty="createdTime",
        sortDirection=SortDirection.DESC,
    )

    files_result = FileAttachmentReadService(files_client).files_list(request)
    attachments_result = FileAttachmentReadService(attachments_client).attachments_list(
        FileAttachmentListRequest()
    )

    assert isinstance(files_result, FilesListSuccess)
    assert files_result.files[0].model_dump() == {"id": "file-1", "fileName": "invoice.pdf"}
    assert files_result.paging is not None
    assert files_result.paging.model_dump() == {
        "page": 2,
        "pageCount": 3,
        "pageSize": 25,
        "total": 56,
    }
    assert file_requests[0].url.path == "/v2/files"
    assert file_requests[0].url.params == httpx.QueryParams(
        {
            "page": "2",
            "pageSize": "25",
            "include": "file",
            "sortProperty": "createdTime",
            "sortDirection": "DESC",
        }
    )
    assert set(file_requests[0].url.params) == {
        "page",
        "pageSize",
        "include",
        "sortProperty",
        "sortDirection",
    }
    assert isinstance(attachments_result, AttachmentsListSuccess)
    assert attachments_result.attachments[0].model_dump() == {"id": "attachment-1"}
    assert attachments_result.paging is None
    assert attachment_requests[0].url.path == "/v2/attachments"
    assert attachment_requests[0].url.params == httpx.QueryParams({"page": "1", "pageSize": "1000"})


@pytest.mark.parametrize(
    ("arguments", "field"),
    [
        ({"page": 0}, "page"),
        ({"pageSize": 0}, "pageSize"),
        ({"pageSize": 1001}, "pageSize"),
        ({"sortDirection": "DOWN"}, "sortDirection"),
        ({"offset": 10}, "offset"),
        ({"invoiceId": "invoice-1"}, "invoiceId"),
        ({"organizationId": "organization-1"}, "organizationId"),
        ({"fileId": "file-1"}, "fileId"),
        ({"ownerId": "owner-1"}, "ownerId"),
        ({"q": "invoice"}, "q"),
    ],
)
def test_list_input_rejects_paging_escapes_and_invented_filters(
    arguments: dict[str, object], field: str
) -> None:
    with pytest.raises(ValidationError) as failure:
        FileAttachmentListRequest.model_validate(arguments)

    assert failure.value.errors()[0]["loc"] == (field,)


@pytest.mark.parametrize("error_code", ["AUTHENTICATION_REQUIRED", "OAUTH_INVALID_ACCESS_TOKEN"])
def test_all_tools_preserve_typed_authentication_errors(
    client_factory: ClientFactory, error_code: str
) -> None:
    client, requests = client_factory(
        lambda request: httpx.Response(401, json={"errorCode": error_code})
    )
    service = FileAttachmentReadService(client)

    results = [
        service.files_get(FileAttachmentGetRequest(id="file-1")),
        service.files_list(FileAttachmentListRequest()),
        service.attachments_get(FileAttachmentGetRequest(id="attachment-1")),
        service.attachments_list(FileAttachmentListRequest()),
    ]

    assert all(isinstance(result, ToolError) for result in results)
    assert {result.code for result in results if isinstance(result, ToolError)} == {
        StableErrorCode.AUTH_REQUIRED
    }
    assert [request.url.path for request in requests] == [
        "/v2/files/file-1",
        "/v2/files",
        "/v2/attachments/attachment-1",
        "/v2/attachments",
    ]


def test_registration_exposes_exactly_the_four_file_and_attachment_tools(
    client_factory: ClientFactory,
) -> None:
    client, requests = client_factory(
        lambda request: httpx.Response(200, json={"file": {"id": "file-1"}})
    )
    server = FastMCP("file-attachment-contract-test")

    register_file_attachment_read_tools(server, client)

    tools = {tool.name: tool for tool in asyncio.run(server.list_tools())}
    assert set(tools) == {
        "api_files_get",
        "api_files_list",
        "api_attachments_get",
        "api_attachments_list",
    }
    assert set(tools["api_files_list"].parameters["properties"]["request"]["properties"]) == {
        "page",
        "pageSize",
        "include",
        "sortProperty",
        "sortDirection",
    }
    result = asyncio.run(server.call_tool("api_files_get", {"request": {"id": "file-1"}}))
    assert result.structured_content == {"result": {"file": {"id": "file-1"}}}
    assert [request.url.path for request in requests] == ["/v2/files/file-1"]
