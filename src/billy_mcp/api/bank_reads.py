"""Typed, read-only tools for the frozen Billy bank and balance contract."""

from __future__ import annotations

from collections.abc import Mapping
from enum import StrEnum
from typing import cast
from urllib.parse import quote

from fastmcp import FastMCP
from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    SerializerFunctionWrapHandler,
    ValidationError,
    model_serializer,
)

from billy_mcp.client import DEFAULT_PAGE_SIZE, MAX_PAGE_SIZE, BillyHttpClient, BillyResponse
from billy_mcp.models import StableErrorCode, ToolError


class SortDirection(StrEnum):
    """The documented collection sort directions."""

    ASC = "ASC"
    DESC = "DESC"


class _ReadRequest(BaseModel):
    """Shared strict validation for the deliberately small bank read surface."""

    model_config = ConfigDict(extra="forbid", populate_by_name=True)


class BankGetRequest(_ReadRequest):
    """Documented inputs for every singular bank or balance read."""

    id: str = Field(min_length=1)
    include: str | None = Field(default=None, min_length=1)


class BankListRequest(_ReadRequest):
    """The complete documented query surface for every bank collection."""

    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=DEFAULT_PAGE_SIZE, alias="pageSize", ge=1, le=MAX_PAGE_SIZE)
    include: str | None = Field(default=None, min_length=1)
    sort_property: str | None = Field(default=None, alias="sortProperty", min_length=1)
    sort_direction: SortDirection | None = Field(default=None, alias="sortDirection")


class BankRecord(BaseModel):
    """An opaque upstream bank or balance record."""

    model_config = ConfigDict(extra="allow")


class Paging(BaseModel):
    """The optional upstream paging object, preserved without assumed fields."""

    model_config = ConfigDict(extra="allow")


class BankMeta(BaseModel):
    """The documented optional metadata envelope for bank collection reads."""

    model_config = ConfigDict(extra="allow")

    paging: Paging | None = None

    @model_serializer(mode="wrap")
    def serialize_optional_paging(
        self, handler: SerializerFunctionWrapHandler
    ) -> dict[str, object]:
        """Avoid fabricating a paging field when the upstream omits it."""

        serialized = cast(dict[str, object], handler(self))
        return {key: value for key, value in serialized.items() if value is not None}


class BankPaymentGetSuccess(BaseModel):
    """Mapped success envelope for ``api_bank_payments_get``."""

    model_config = ConfigDict(extra="forbid")

    bankPayment: BankRecord


class _BankListSuccess(BaseModel):
    """Keep absent upstream metadata absent from collection tool results."""

    model_config = ConfigDict(extra="forbid")

    meta: BankMeta | None = None

    @model_serializer(mode="wrap")
    def serialize_optional_meta(self, handler: SerializerFunctionWrapHandler) -> dict[str, object]:
        """Avoid fabricating an empty metadata root when Billy omits it."""

        serialized = cast(dict[str, object], handler(self))
        return {key: value for key, value in serialized.items() if value is not None}


class BankPaymentsListSuccess(_BankListSuccess):
    """Mapped success envelope for ``api_bank_payments_list``."""

    bankPayments: list[BankRecord]


class BankLineMatchGetSuccess(BaseModel):
    """Mapped success envelope for ``api_bank_line_matches_get``."""

    model_config = ConfigDict(extra="forbid")

    bankLineMatch: BankRecord


class BankLineMatchesListSuccess(_BankListSuccess):
    """Mapped success envelope for ``api_bank_line_matches_list``."""

    bankLineMatches: list[BankRecord]


class BankLineGetSuccess(BaseModel):
    """Mapped success envelope for ``api_bank_lines_get``."""

    model_config = ConfigDict(extra="forbid")

    bankLine: BankRecord


class BankLinesListSuccess(_BankListSuccess):
    """Mapped success envelope for ``api_bank_lines_list``."""

    bankLines: list[BankRecord]


class BankLineSubjectAssociationGetSuccess(BaseModel):
    """Mapped success envelope for ``api_bank_line_subject_associations_get``."""

    model_config = ConfigDict(extra="forbid")

    bankLineSubjectAssociation: BankRecord


class BankLineSubjectAssociationsListSuccess(_BankListSuccess):
    """Mapped success envelope for ``api_bank_line_subject_associations_list``."""

    bankLineSubjectAssociations: list[BankRecord]


class BalanceModifierGetSuccess(BaseModel):
    """Mapped success envelope for ``api_balance_modifiers_get``."""

    model_config = ConfigDict(extra="forbid")

    balanceModifier: BankRecord


class BalanceModifiersListSuccess(_BankListSuccess):
    """Mapped success envelope for ``api_balance_modifiers_list``."""

    balanceModifiers: list[BankRecord]


class BankReadService:
    """Typed handlers over the locked client, separate from root server wiring."""

    def __init__(self, client: BillyHttpClient) -> None:
        self._client = client

    def bank_payments_get(self, request: BankGetRequest) -> BankPaymentGetSuccess | ToolError:
        """Read one bank payment by its Billy identifier."""

        record = self._get("/bankPayments", "bankPayment", request)
        return (
            record if isinstance(record, ToolError) else BankPaymentGetSuccess(bankPayment=record)
        )

    def bank_payments_list(self, request: BankListRequest) -> BankPaymentsListSuccess | ToolError:
        """Read one documented page of bank payments."""

        records = self._list("/bankPayments", "bankPayments", request)
        if isinstance(records, ToolError):
            return records
        bank_payments, meta = records
        return BankPaymentsListSuccess(bankPayments=bank_payments, meta=meta)

    def bank_line_matches_get(self, request: BankGetRequest) -> BankLineMatchGetSuccess | ToolError:
        """Read one bank line match by its Billy identifier."""

        record = self._get("/bankLineMatches", "bankLineMatch", request)
        return (
            record
            if isinstance(record, ToolError)
            else BankLineMatchGetSuccess(bankLineMatch=record)
        )

    def bank_line_matches_list(
        self, request: BankListRequest
    ) -> BankLineMatchesListSuccess | ToolError:
        """Read one documented page of bank line matches."""

        records = self._list("/bankLineMatches", "bankLineMatches", request)
        if isinstance(records, ToolError):
            return records
        bank_line_matches, meta = records
        return BankLineMatchesListSuccess(bankLineMatches=bank_line_matches, meta=meta)

    def bank_lines_get(self, request: BankGetRequest) -> BankLineGetSuccess | ToolError:
        """Read one bank line by its Billy identifier."""

        record = self._get("/bankLines", "bankLine", request)
        return record if isinstance(record, ToolError) else BankLineGetSuccess(bankLine=record)

    def bank_lines_list(self, request: BankListRequest) -> BankLinesListSuccess | ToolError:
        """Read one documented page of bank lines."""

        records = self._list("/bankLines", "bankLines", request)
        if isinstance(records, ToolError):
            return records
        bank_lines, meta = records
        return BankLinesListSuccess(bankLines=bank_lines, meta=meta)

    def bank_line_subject_associations_get(
        self, request: BankGetRequest
    ) -> BankLineSubjectAssociationGetSuccess | ToolError:
        """Read one bank line subject association by its Billy identifier."""

        record = self._get("/bankLineSubjectAssociations", "bankLineSubjectAssociation", request)
        return (
            record
            if isinstance(record, ToolError)
            else BankLineSubjectAssociationGetSuccess(bankLineSubjectAssociation=record)
        )

    def bank_line_subject_associations_list(
        self, request: BankListRequest
    ) -> BankLineSubjectAssociationsListSuccess | ToolError:
        """Read one documented page of bank line subject associations."""

        records = self._list("/bankLineSubjectAssociations", "bankLineSubjectAssociations", request)
        if isinstance(records, ToolError):
            return records
        associations, meta = records
        return BankLineSubjectAssociationsListSuccess(
            bankLineSubjectAssociations=associations,
            meta=meta,
        )

    def balance_modifiers_get(
        self, request: BankGetRequest
    ) -> BalanceModifierGetSuccess | ToolError:
        """Read one balance modifier by its Billy identifier."""

        record = self._get("/balanceModifiers", "balanceModifier", request)
        return (
            record
            if isinstance(record, ToolError)
            else BalanceModifierGetSuccess(balanceModifier=record)
        )

    def balance_modifiers_list(
        self, request: BankListRequest
    ) -> BalanceModifiersListSuccess | ToolError:
        """Read one documented page of balance modifiers."""

        records = self._list("/balanceModifiers", "balanceModifiers", request)
        if isinstance(records, ToolError):
            return records
        balance_modifiers, meta = records
        return BalanceModifiersListSuccess(balanceModifiers=balance_modifiers, meta=meta)

    def _get(
        self, collection_path: str, root: str, request: BankGetRequest
    ) -> BankRecord | ToolError:
        response = self._client.request(
            "GET",
            _item_path(collection_path, request.id),
            params=_get_params(request),
        )
        return _record_from_response(response, root)

    def _list(
        self, collection_path: str, root: str, request: BankListRequest
    ) -> tuple[list[BankRecord], BankMeta | None] | ToolError:
        response = self._client.request("GET", collection_path, params=_list_params(request))
        return _list_from_response(response, root)


def register_bank_read_tools(server: FastMCP, client: BillyHttpClient) -> None:
    """Register exactly the ten frozen bank and balance read tools."""

    service = BankReadService(client)

    def api_bank_payments_get(
        id: str = Field(min_length=1), include: str | None = Field(default=None, min_length=1)
    ) -> BankPaymentGetSuccess | ToolError:
        """Read one Billy bank payment by identifier."""

        return service.bank_payments_get(BankGetRequest(id=id, include=include))

    def api_bank_payments_list(
        page: int = Field(default=1, ge=1),
        pageSize: int = Field(default=DEFAULT_PAGE_SIZE, ge=1, le=MAX_PAGE_SIZE),
        include: str | None = Field(default=None, min_length=1),
        sortProperty: str | None = Field(default=None, min_length=1),
        sortDirection: SortDirection | None = None,
    ) -> BankPaymentsListSuccess | ToolError:
        """List Billy bank payments with documented paging, inclusion, and sorting."""

        return service.bank_payments_list(
            BankListRequest(
                page=page,
                pageSize=pageSize,
                include=include,
                sortProperty=sortProperty,
                sortDirection=sortDirection,
            )
        )

    def api_bank_line_matches_get(
        id: str = Field(min_length=1), include: str | None = Field(default=None, min_length=1)
    ) -> BankLineMatchGetSuccess | ToolError:
        """Read one Billy bank line match by identifier."""

        return service.bank_line_matches_get(BankGetRequest(id=id, include=include))

    def api_bank_line_matches_list(
        page: int = Field(default=1, ge=1),
        pageSize: int = Field(default=DEFAULT_PAGE_SIZE, ge=1, le=MAX_PAGE_SIZE),
        include: str | None = Field(default=None, min_length=1),
        sortProperty: str | None = Field(default=None, min_length=1),
        sortDirection: SortDirection | None = None,
    ) -> BankLineMatchesListSuccess | ToolError:
        """List Billy bank line matches with documented paging, inclusion, and sorting."""

        return service.bank_line_matches_list(
            BankListRequest(
                page=page,
                pageSize=pageSize,
                include=include,
                sortProperty=sortProperty,
                sortDirection=sortDirection,
            )
        )

    def api_bank_lines_get(
        id: str = Field(min_length=1), include: str | None = Field(default=None, min_length=1)
    ) -> BankLineGetSuccess | ToolError:
        """Read one Billy bank line by identifier."""

        return service.bank_lines_get(BankGetRequest(id=id, include=include))

    def api_bank_lines_list(
        page: int = Field(default=1, ge=1),
        pageSize: int = Field(default=DEFAULT_PAGE_SIZE, ge=1, le=MAX_PAGE_SIZE),
        include: str | None = Field(default=None, min_length=1),
        sortProperty: str | None = Field(default=None, min_length=1),
        sortDirection: SortDirection | None = None,
    ) -> BankLinesListSuccess | ToolError:
        """List Billy bank lines with documented paging, inclusion, and sorting."""

        return service.bank_lines_list(
            BankListRequest(
                page=page,
                pageSize=pageSize,
                include=include,
                sortProperty=sortProperty,
                sortDirection=sortDirection,
            )
        )

    def api_bank_line_subject_associations_get(
        id: str = Field(min_length=1), include: str | None = Field(default=None, min_length=1)
    ) -> BankLineSubjectAssociationGetSuccess | ToolError:
        """Read one Billy bank line subject association by identifier."""

        return service.bank_line_subject_associations_get(BankGetRequest(id=id, include=include))

    def api_bank_line_subject_associations_list(
        page: int = Field(default=1, ge=1),
        pageSize: int = Field(default=DEFAULT_PAGE_SIZE, ge=1, le=MAX_PAGE_SIZE),
        include: str | None = Field(default=None, min_length=1),
        sortProperty: str | None = Field(default=None, min_length=1),
        sortDirection: SortDirection | None = None,
    ) -> BankLineSubjectAssociationsListSuccess | ToolError:
        """List Billy bank line subject associations with documented query controls."""

        return service.bank_line_subject_associations_list(
            BankListRequest(
                page=page,
                pageSize=pageSize,
                include=include,
                sortProperty=sortProperty,
                sortDirection=sortDirection,
            )
        )

    def api_balance_modifiers_get(
        id: str = Field(min_length=1), include: str | None = Field(default=None, min_length=1)
    ) -> BalanceModifierGetSuccess | ToolError:
        """Read one Billy balance modifier by identifier."""

        return service.balance_modifiers_get(BankGetRequest(id=id, include=include))

    def api_balance_modifiers_list(
        page: int = Field(default=1, ge=1),
        pageSize: int = Field(default=DEFAULT_PAGE_SIZE, ge=1, le=MAX_PAGE_SIZE),
        include: str | None = Field(default=None, min_length=1),
        sortProperty: str | None = Field(default=None, min_length=1),
        sortDirection: SortDirection | None = None,
    ) -> BalanceModifiersListSuccess | ToolError:
        """List Billy balance modifiers with documented paging, inclusion, and sorting."""

        return service.balance_modifiers_list(
            BankListRequest(
                page=page,
                pageSize=pageSize,
                include=include,
                sortProperty=sortProperty,
                sortDirection=sortDirection,
            )
        )

    server.tool(name="api_bank_payments_get", description="Read one Billy bank payment.")(
        api_bank_payments_get
    )
    server.tool(name="api_bank_payments_list", description="List Billy bank payments.")(
        api_bank_payments_list
    )
    server.tool(name="api_bank_line_matches_get", description="Read one Billy bank line match.")(
        api_bank_line_matches_get
    )
    server.tool(name="api_bank_line_matches_list", description="List Billy bank line matches.")(
        api_bank_line_matches_list
    )
    server.tool(name="api_bank_lines_get", description="Read one Billy bank line.")(
        api_bank_lines_get
    )
    server.tool(name="api_bank_lines_list", description="List Billy bank lines.")(
        api_bank_lines_list
    )
    server.tool(
        name="api_bank_line_subject_associations_get",
        description="Read one Billy bank line subject association.",
    )(api_bank_line_subject_associations_get)
    server.tool(
        name="api_bank_line_subject_associations_list",
        description="List Billy bank line subject associations.",
    )(api_bank_line_subject_associations_list)
    server.tool(name="api_balance_modifiers_get", description="Read one Billy balance modifier.")(
        api_balance_modifiers_get
    )
    server.tool(name="api_balance_modifiers_list", description="List Billy balance modifiers.")(
        api_balance_modifiers_list
    )


def _item_path(collection_path: str, identifier: str) -> str:
    return f"{collection_path}/{quote(identifier, safe='')}"


def _get_params(request: BankGetRequest) -> dict[str, str]:
    return {} if request.include is None else {"include": request.include}


def _list_params(request: BankListRequest) -> dict[str, int | str]:
    params: dict[str, int | str] = {"page": request.page, "pageSize": request.page_size}
    if request.include is not None:
        params["include"] = request.include
    if request.sort_property is not None:
        params["sortProperty"] = request.sort_property
    if request.sort_direction is not None:
        params["sortDirection"] = request.sort_direction.value
    return params


def _record_from_response(response: BillyResponse | ToolError, root: str) -> BankRecord | ToolError:
    payload = _response_mapping(response, root)
    if isinstance(payload, ToolError):
        return payload
    record = payload.get(root)
    if not isinstance(record, Mapping):
        return _invalid_response(root)
    try:
        return BankRecord.model_validate(record)
    except ValidationError:
        return _invalid_response(root)


def _list_from_response(
    response: BillyResponse | ToolError, root: str
) -> tuple[list[BankRecord], BankMeta | None] | ToolError:
    payload = _response_mapping(response, root)
    if isinstance(payload, ToolError):
        return payload
    values = payload.get(root)
    if not isinstance(values, list):
        return _invalid_response(root)
    records: list[BankRecord] = []
    for value in cast(list[object], values):
        if not isinstance(value, Mapping):
            return _invalid_response(root)
        try:
            records.append(BankRecord.model_validate(value))
        except ValidationError:
            return _invalid_response(root)
    meta = _meta_from_response(payload, root)
    if isinstance(meta, ToolError):
        return meta
    return records, meta


def _response_mapping(
    response: BillyResponse | ToolError, root: str
) -> Mapping[str, object] | ToolError:
    if isinstance(response, ToolError):
        return response
    data = response.data
    if not isinstance(data, Mapping):
        return _invalid_response(root)
    return cast(Mapping[str, object], data)


def _meta_from_response(payload: Mapping[str, object], root: str) -> BankMeta | ToolError | None:
    meta = payload.get("meta")
    if meta is None:
        return None
    if not isinstance(meta, Mapping):
        return _invalid_response(root)
    try:
        return BankMeta.model_validate(meta)
    except ValidationError:
        return _invalid_response(root)


def _invalid_response(root: str) -> ToolError:
    return ToolError(
        code=StableErrorCode.BILLY_ERROR,
        message="Billy API response did not contain the documented bank or balance root.",
        details={"expected_root": root},
    )
