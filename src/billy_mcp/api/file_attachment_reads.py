"""Typed, read-only tools for the frozen Billy files and attachments contract."""

from __future__ import annotations

from collections.abc import Mapping
from enum import StrEnum
from typing import cast
from urllib.parse import quote

from fastmcp import FastMCP
from pydantic import BaseModel, ConfigDict, Field, ValidationError

from billy_mcp.client import DEFAULT_PAGE_SIZE, MAX_PAGE_SIZE, BillyHttpClient, BillyResponse
from billy_mcp.models import StableErrorCode, ToolError


class SortDirection(StrEnum):
    """The documented collection sort directions."""

    ASC = "ASC"
    DESC = "DESC"


class _ReadInput(BaseModel):
    """Shared strict validation for the deliberately small read surface."""

    model_config = ConfigDict(extra="forbid", populate_by_name=True)


class FileAttachmentGetRequest(_ReadInput):
    """Documented inputs shared by singular file and attachment reads."""

    id: str = Field(min_length=1)
    include: str | None = Field(default=None, min_length=1)


class FileAttachmentListRequest(_ReadInput):
    """The complete documented query surface for files and attachments."""

    page: int = Field(default=1, ge=1)
    page_size: int = Field(
        default=DEFAULT_PAGE_SIZE,
        alias="pageSize",
        ge=1,
        le=MAX_PAGE_SIZE,
    )
    include: str | None = Field(default=None, min_length=1)
    sort_property: str | None = Field(default=None, alias="sortProperty", min_length=1)
    sort_direction: SortDirection | None = Field(default=None, alias="sortDirection")


class FileAttachmentRecord(BaseModel):
    """An opaque upstream file or attachment object."""

    model_config = ConfigDict(extra="allow")


class Paging(BaseModel):
    """The optional upstream paging object, preserved without assumed fields."""

    model_config = ConfigDict(extra="allow")


class FileGetSuccess(BaseModel):
    """Mapped success envelope for ``api_files_get``."""

    model_config = ConfigDict(extra="forbid")

    file: FileAttachmentRecord


class FilesListSuccess(BaseModel):
    """Mapped success envelope for ``api_files_list``."""

    model_config = ConfigDict(extra="forbid")

    files: list[FileAttachmentRecord]
    paging: Paging | None = None


class AttachmentGetSuccess(BaseModel):
    """Mapped success envelope for ``api_attachments_get``."""

    model_config = ConfigDict(extra="forbid")

    attachment: FileAttachmentRecord


class AttachmentsListSuccess(BaseModel):
    """Mapped success envelope for ``api_attachments_list``."""

    model_config = ConfigDict(extra="forbid")

    attachments: list[FileAttachmentRecord]
    paging: Paging | None = None


class FileAttachmentReadService:
    """Typed handlers over the locked client, separate from root server wiring."""

    def __init__(self, client: BillyHttpClient) -> None:
        self._client = client

    def files_get(self, request: FileAttachmentGetRequest) -> FileGetSuccess | ToolError:
        """Read one file by its Billy identifier."""

        response = self._client.request(
            "GET", _item_path("/files", request.id), params=_get_params(request)
        )
        record = _record_from_response(response, "file")
        if isinstance(record, ToolError):
            return record
        return FileGetSuccess(file=record)

    def files_list(self, request: FileAttachmentListRequest) -> FilesListSuccess | ToolError:
        """Read one documented page of files."""

        response = self._client.request("GET", "/files", params=_list_params(request))
        records = _list_from_response(response, "files")
        if isinstance(records, ToolError):
            return records
        files, paging = records
        return FilesListSuccess(files=files, paging=paging)

    def attachments_get(
        self, request: FileAttachmentGetRequest
    ) -> AttachmentGetSuccess | ToolError:
        """Read one attachment by its Billy identifier."""

        response = self._client.request(
            "GET", _item_path("/attachments", request.id), params=_get_params(request)
        )
        record = _record_from_response(response, "attachment")
        if isinstance(record, ToolError):
            return record
        return AttachmentGetSuccess(attachment=record)

    def attachments_list(
        self, request: FileAttachmentListRequest
    ) -> AttachmentsListSuccess | ToolError:
        """Read one documented page of attachments."""

        response = self._client.request("GET", "/attachments", params=_list_params(request))
        records = _list_from_response(response, "attachments")
        if isinstance(records, ToolError):
            return records
        attachments, paging = records
        return AttachmentsListSuccess(attachments=attachments, paging=paging)


def register_file_attachment_read_tools(server: FastMCP, client: BillyHttpClient) -> None:
    """Register exactly the four verified file and attachment read tools."""

    service = FileAttachmentReadService(client)
    server.tool(name="api_files_get", description="Read one Billy file.")(service.files_get)
    server.tool(name="api_files_list", description="List Billy files.")(service.files_list)
    server.tool(name="api_attachments_get", description="Read one Billy attachment.")(
        service.attachments_get
    )
    server.tool(name="api_attachments_list", description="List Billy attachments.")(
        service.attachments_list
    )


def _item_path(collection_path: str, identifier: str) -> str:
    return f"{collection_path}/{quote(identifier, safe='')}"


def _get_params(request: FileAttachmentGetRequest) -> dict[str, str]:
    return {} if request.include is None else {"include": request.include}


def _list_params(request: FileAttachmentListRequest) -> dict[str, int | str]:
    params: dict[str, int | str] = {"page": request.page, "pageSize": request.page_size}
    if request.include is not None:
        params["include"] = request.include
    if request.sort_property is not None:
        params["sortProperty"] = request.sort_property
    if request.sort_direction is not None:
        params["sortDirection"] = request.sort_direction.value
    return params


def _record_from_response(
    response: BillyResponse | ToolError, root: str
) -> FileAttachmentRecord | ToolError:
    payload = _response_mapping(response, root)
    if isinstance(payload, ToolError):
        return payload
    record = payload.get(root)
    if not isinstance(record, Mapping):
        return _invalid_response(root)
    try:
        return FileAttachmentRecord.model_validate(record)
    except ValidationError:
        return _invalid_response(root)


def _list_from_response(
    response: BillyResponse | ToolError, root: str
) -> tuple[list[FileAttachmentRecord], Paging | None] | ToolError:
    payload = _response_mapping(response, root)
    if isinstance(payload, ToolError):
        return payload
    values = payload.get(root)
    if not isinstance(values, list):
        return _invalid_response(root)
    records: list[FileAttachmentRecord] = []
    for value in cast(list[object], values):
        if not isinstance(value, Mapping):
            return _invalid_response(root)
        try:
            records.append(FileAttachmentRecord.model_validate(value))
        except ValidationError:
            return _invalid_response(root)
    paging = _paging_from_response(payload, root)
    if isinstance(paging, ToolError):
        return paging
    return records, paging


def _response_mapping(
    response: BillyResponse | ToolError, root: str
) -> Mapping[str, object] | ToolError:
    if isinstance(response, ToolError):
        return response
    data = response.data
    if not isinstance(data, Mapping):
        return _invalid_response(root)
    return cast(Mapping[str, object], data)


def _paging_from_response(payload: Mapping[str, object], root: str) -> Paging | ToolError | None:
    meta = payload.get("meta")
    if meta is None:
        return None
    if not isinstance(meta, Mapping):
        return _invalid_response(root)
    meta_mapping = cast(Mapping[str, object], meta)
    paging = meta_mapping.get("paging")
    if paging is None:
        return None
    if not isinstance(paging, Mapping):
        return _invalid_response(root)
    try:
        return Paging.model_validate(paging)
    except ValidationError:
        return _invalid_response(root)


def _invalid_response(root: str) -> ToolError:
    return ToolError(
        code=StableErrorCode.BILLY_ERROR,
        message="Billy API response did not contain the documented file or attachment root.",
        details={"expected_root": root},
    )
