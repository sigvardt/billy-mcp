"""Typed, read-only tools for the frozen Billy sales-tax endpoints."""

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


class _RequestModel(BaseModel):
    """Reject undeclared inputs while accepting documented Billy wire aliases."""

    model_config = ConfigDict(
        extra="forbid", strict=True, validate_by_alias=True, validate_by_name=True
    )


class SortDirection(StrEnum):
    """The two documented collection sort directions."""

    ASC = "ASC"
    DESC = "DESC"


class _GetRequest(_RequestModel):
    """Shared documented input for a singular tax-resource read."""

    id: str = Field(min_length=1)
    include: str | None = None

    def query_params(self) -> dict[str, str]:
        """Return only the optional documented singular-read query field."""

        return {} if self.include is None else {"include": self.include}


class _ListRequest(_RequestModel):
    """Shared, deliberately small list-query allowlist for tax resources."""

    page: int = Field(default=1, ge=1)
    page_size: int = Field(
        default=DEFAULT_PAGE_SIZE,
        alias="pageSize",
        serialization_alias="pageSize",
        ge=1,
        le=MAX_PAGE_SIZE,
    )
    include: str | None = None
    sort_property: str | None = Field(
        default=None, alias="sortProperty", serialization_alias="sortProperty"
    )
    sort_direction: SortDirection | None = Field(
        default=None, alias="sortDirection", serialization_alias="sortDirection"
    )

    def query_params(self) -> dict[str, str | int]:
        """Serialise only documented paging, inclusion, and sorting parameters."""

        return cast(
            dict[str, str | int],
            self.model_dump(by_alias=True, exclude_none=True, mode="json"),
        )


class TaxRateGetRequest(_GetRequest):
    """Input for retrieving one tax rate."""


class TaxRateDeductionComponentGetRequest(_GetRequest):
    """Input for retrieving one tax-rate deduction component."""


class SalesTaxRulesetGetRequest(_GetRequest):
    """Input for retrieving one sales-tax ruleset."""


class SalesTaxRuleGetRequest(_GetRequest):
    """Input for retrieving one sales-tax rule."""


class SalesTaxAccountGetRequest(_GetRequest):
    """Input for retrieving one sales-tax account."""


class SalesTaxMetaFieldGetRequest(_GetRequest):
    """Input for retrieving one sales-tax meta field."""


class SalesTaxReturnGetRequest(_GetRequest):
    """Input for retrieving one sales-tax return."""


class SalesTaxPaymentGetRequest(_GetRequest):
    """Input for retrieving one sales-tax payment."""


class TaxRatesListRequest(_ListRequest):
    """Input for the documented tax-rates collection read."""


class TaxRateDeductionComponentsListRequest(_ListRequest):
    """Input for the documented tax-rate-deduction-components collection read."""


class SalesTaxRulesetsListRequest(_ListRequest):
    """Input for the documented sales-tax-rulesets collection read."""


class SalesTaxRulesListRequest(_ListRequest):
    """Input for the documented sales-tax-rules collection read."""


class SalesTaxAccountsListRequest(_ListRequest):
    """Input for the documented sales-tax-accounts collection read."""


class SalesTaxMetaFieldsListRequest(_ListRequest):
    """Input for the documented sales-tax-meta-fields collection read."""


class SalesTaxReturnsListRequest(_ListRequest):
    """Input for the documented sales-tax-returns collection read."""


class SalesTaxPaymentsListRequest(_ListRequest):
    """Input for the documented sales-tax-payments collection read."""


class _OpaquePayload(BaseModel):
    """An opaque JSON object returned by Billy."""

    model_config = ConfigDict(extra="allow")


class TaxRatePayload(_OpaquePayload):
    """An opaque tax-rate payload."""


class TaxRateDeductionComponentPayload(_OpaquePayload):
    """An opaque tax-rate-deduction-component payload."""


class SalesTaxRulesetPayload(_OpaquePayload):
    """An opaque sales-tax-ruleset payload."""


class SalesTaxRulePayload(_OpaquePayload):
    """An opaque sales-tax-rule payload."""


class SalesTaxAccountPayload(_OpaquePayload):
    """An opaque sales-tax-account payload."""


class SalesTaxMetaFieldPayload(_OpaquePayload):
    """An opaque sales-tax-meta-field payload."""


class SalesTaxReturnPayload(_OpaquePayload):
    """An opaque sales-tax-return payload."""


class SalesTaxPaymentPayload(_OpaquePayload):
    """An opaque sales-tax-payment payload."""


class Paging(BaseModel):
    """The optional documented collection paging fields."""

    model_config = ConfigDict(extra="ignore")

    page: int | None = None
    page_count: int | None = Field(default=None, alias="pageCount")
    page_size: int | None = Field(default=None, alias="pageSize")
    total: int | None = None
    first_url: str | None = Field(default=None, alias="firstUrl")
    previous_url: str | None = Field(default=None, alias="previousUrl")
    next_url: str | None = Field(default=None, alias="nextUrl")
    last_url: str | None = Field(default=None, alias="lastUrl")


class TaxMeta(BaseModel):
    """The optional metadata root shared by sales-tax collection reads."""

    model_config = ConfigDict(extra="ignore")

    paging: Paging | None = None


class TaxRateGetSuccess(BaseModel):
    """Successful response for ``api_tax_rates_get``."""

    model_config = ConfigDict(extra="forbid")

    taxRate: TaxRatePayload


class TaxRateDeductionComponentGetSuccess(BaseModel):
    """Successful response for ``api_tax_rate_deduction_components_get``."""

    model_config = ConfigDict(extra="forbid")

    taxRateDeductionComponent: TaxRateDeductionComponentPayload


class SalesTaxRulesetGetSuccess(BaseModel):
    """Successful response for ``api_sales_tax_rulesets_get``."""

    model_config = ConfigDict(extra="forbid")

    salesTaxRuleset: SalesTaxRulesetPayload


class SalesTaxRuleGetSuccess(BaseModel):
    """Successful response for ``api_sales_tax_rules_get``."""

    model_config = ConfigDict(extra="forbid")

    salesTaxRule: SalesTaxRulePayload


class SalesTaxAccountGetSuccess(BaseModel):
    """Successful response for ``api_sales_tax_accounts_get``."""

    model_config = ConfigDict(extra="forbid")

    salesTaxAccount: SalesTaxAccountPayload


class SalesTaxMetaFieldGetSuccess(BaseModel):
    """Successful response for ``api_sales_tax_meta_fields_get``."""

    model_config = ConfigDict(extra="forbid")

    salesTaxMetaField: SalesTaxMetaFieldPayload


class SalesTaxReturnGetSuccess(BaseModel):
    """Successful response for ``api_sales_tax_returns_get``."""

    model_config = ConfigDict(extra="forbid")

    salesTaxReturn: SalesTaxReturnPayload


class SalesTaxPaymentGetSuccess(BaseModel):
    """Successful response for ``api_sales_tax_payments_get``."""

    model_config = ConfigDict(extra="forbid")

    salesTaxPayment: SalesTaxPaymentPayload


class _ListSuccess(BaseModel):
    """Keep absent upstream metadata absent from collection tool results."""

    model_config = ConfigDict(extra="forbid")

    meta: TaxMeta | None = None

    @model_serializer(mode="wrap")
    def serialize_optional_meta(self, handler: SerializerFunctionWrapHandler) -> dict[str, object]:
        """Avoid fabricating metadata when Billy omits the root."""

        serialized = cast(dict[str, object], handler(self))
        return {key: value for key, value in serialized.items() if value is not None}


class TaxRatesListSuccess(_ListSuccess):
    """Successful response for ``api_tax_rates_list``."""

    taxRates: list[TaxRatePayload]


class TaxRateDeductionComponentsListSuccess(_ListSuccess):
    """Successful response for ``api_tax_rate_deduction_components_list``."""

    taxRateDeductionComponents: list[TaxRateDeductionComponentPayload]


class SalesTaxRulesetsListSuccess(_ListSuccess):
    """Successful response for ``api_sales_tax_rulesets_list``."""

    salesTaxRulesets: list[SalesTaxRulesetPayload]


class SalesTaxRulesListSuccess(_ListSuccess):
    """Successful response for ``api_sales_tax_rules_list``."""

    salesTaxRules: list[SalesTaxRulePayload]


class SalesTaxAccountsListSuccess(_ListSuccess):
    """Successful response for ``api_sales_tax_accounts_list``."""

    salesTaxAccounts: list[SalesTaxAccountPayload]


class SalesTaxMetaFieldsListSuccess(_ListSuccess):
    """Successful response for ``api_sales_tax_meta_fields_list``."""

    salesTaxMetaFields: list[SalesTaxMetaFieldPayload]


class SalesTaxReturnsListSuccess(_ListSuccess):
    """Successful response for ``api_sales_tax_returns_list``."""

    salesTaxReturns: list[SalesTaxReturnPayload]


class SalesTaxPaymentsListSuccess(_ListSuccess):
    """Successful response for ``api_sales_tax_payments_list``."""

    salesTaxPayments: list[SalesTaxPaymentPayload]


def get_tax_rate(
    client: BillyHttpClient, request: TaxRateGetRequest
) -> TaxRateGetSuccess | ToolError:
    """Retrieve one tax rate through its documented singular response root."""

    record = _get_record(client, request, "/taxRates", "taxRate")
    if isinstance(record, ToolError):
        return record
    try:
        return TaxRateGetSuccess(taxRate=TaxRatePayload.model_validate(record))
    except ValidationError:
        return _unexpected_response("taxRate")


def get_tax_rate_deduction_component(
    client: BillyHttpClient, request: TaxRateDeductionComponentGetRequest
) -> TaxRateDeductionComponentGetSuccess | ToolError:
    """Retrieve one tax-rate deduction component through its documented root."""

    record = _get_record(
        client,
        request,
        "/taxRateDeductionComponents",
        "taxRateDeductionComponent",
    )
    if isinstance(record, ToolError):
        return record
    try:
        return TaxRateDeductionComponentGetSuccess(
            taxRateDeductionComponent=TaxRateDeductionComponentPayload.model_validate(record)
        )
    except ValidationError:
        return _unexpected_response("taxRateDeductionComponent")


def get_sales_tax_ruleset(
    client: BillyHttpClient, request: SalesTaxRulesetGetRequest
) -> SalesTaxRulesetGetSuccess | ToolError:
    """Retrieve one sales-tax ruleset through its documented singular root."""

    record = _get_record(client, request, "/salesTaxRulesets", "salesTaxRuleset")
    if isinstance(record, ToolError):
        return record
    try:
        return SalesTaxRulesetGetSuccess(
            salesTaxRuleset=SalesTaxRulesetPayload.model_validate(record)
        )
    except ValidationError:
        return _unexpected_response("salesTaxRuleset")


def get_sales_tax_rule(
    client: BillyHttpClient, request: SalesTaxRuleGetRequest
) -> SalesTaxRuleGetSuccess | ToolError:
    """Retrieve one sales-tax rule through its documented singular root."""

    record = _get_record(client, request, "/salesTaxRules", "salesTaxRule")
    if isinstance(record, ToolError):
        return record
    try:
        return SalesTaxRuleGetSuccess(salesTaxRule=SalesTaxRulePayload.model_validate(record))
    except ValidationError:
        return _unexpected_response("salesTaxRule")


def get_sales_tax_account(
    client: BillyHttpClient, request: SalesTaxAccountGetRequest
) -> SalesTaxAccountGetSuccess | ToolError:
    """Retrieve one sales-tax account through its documented singular root."""

    record = _get_record(client, request, "/salesTaxAccounts", "salesTaxAccount")
    if isinstance(record, ToolError):
        return record
    try:
        return SalesTaxAccountGetSuccess(
            salesTaxAccount=SalesTaxAccountPayload.model_validate(record)
        )
    except ValidationError:
        return _unexpected_response("salesTaxAccount")


def get_sales_tax_meta_field(
    client: BillyHttpClient, request: SalesTaxMetaFieldGetRequest
) -> SalesTaxMetaFieldGetSuccess | ToolError:
    """Retrieve one sales-tax meta field through its documented singular root."""

    record = _get_record(client, request, "/salesTaxMetaFields", "salesTaxMetaField")
    if isinstance(record, ToolError):
        return record
    try:
        return SalesTaxMetaFieldGetSuccess(
            salesTaxMetaField=SalesTaxMetaFieldPayload.model_validate(record)
        )
    except ValidationError:
        return _unexpected_response("salesTaxMetaField")


def get_sales_tax_return(
    client: BillyHttpClient, request: SalesTaxReturnGetRequest
) -> SalesTaxReturnGetSuccess | ToolError:
    """Retrieve one sales-tax return through its documented singular root."""

    record = _get_record(client, request, "/salesTaxReturns", "salesTaxReturn")
    if isinstance(record, ToolError):
        return record
    try:
        return SalesTaxReturnGetSuccess(salesTaxReturn=SalesTaxReturnPayload.model_validate(record))
    except ValidationError:
        return _unexpected_response("salesTaxReturn")


def get_sales_tax_payment(
    client: BillyHttpClient, request: SalesTaxPaymentGetRequest
) -> SalesTaxPaymentGetSuccess | ToolError:
    """Retrieve one sales-tax payment through its documented singular root."""

    record = _get_record(client, request, "/salesTaxPayments", "salesTaxPayment")
    if isinstance(record, ToolError):
        return record
    try:
        return SalesTaxPaymentGetSuccess(
            salesTaxPayment=SalesTaxPaymentPayload.model_validate(record)
        )
    except ValidationError:
        return _unexpected_response("salesTaxPayment")


def list_tax_rates(
    client: BillyHttpClient, request: TaxRatesListRequest
) -> TaxRatesListSuccess | ToolError:
    """Retrieve tax rates and their optional documented paging metadata."""

    records = _list_records(client, request, "/taxRates", "taxRates")
    if isinstance(records, ToolError):
        return records
    values, meta = records
    try:
        return TaxRatesListSuccess(
            taxRates=[TaxRatePayload.model_validate(value) for value in values], meta=meta
        )
    except ValidationError:
        return _unexpected_response("taxRates")


def list_tax_rate_deduction_components(
    client: BillyHttpClient, request: TaxRateDeductionComponentsListRequest
) -> TaxRateDeductionComponentsListSuccess | ToolError:
    """Retrieve tax-rate deduction components and optional paging metadata."""

    records = _list_records(
        client,
        request,
        "/taxRateDeductionComponents",
        "taxRateDeductionComponents",
    )
    if isinstance(records, ToolError):
        return records
    values, meta = records
    try:
        return TaxRateDeductionComponentsListSuccess(
            taxRateDeductionComponents=[
                TaxRateDeductionComponentPayload.model_validate(value) for value in values
            ],
            meta=meta,
        )
    except ValidationError:
        return _unexpected_response("taxRateDeductionComponents")


def list_sales_tax_rulesets(
    client: BillyHttpClient, request: SalesTaxRulesetsListRequest
) -> SalesTaxRulesetsListSuccess | ToolError:
    """Retrieve sales-tax rulesets and their optional paging metadata."""

    records = _list_records(client, request, "/salesTaxRulesets", "salesTaxRulesets")
    if isinstance(records, ToolError):
        return records
    values, meta = records
    try:
        return SalesTaxRulesetsListSuccess(
            salesTaxRulesets=[SalesTaxRulesetPayload.model_validate(value) for value in values],
            meta=meta,
        )
    except ValidationError:
        return _unexpected_response("salesTaxRulesets")


def list_sales_tax_rules(
    client: BillyHttpClient, request: SalesTaxRulesListRequest
) -> SalesTaxRulesListSuccess | ToolError:
    """Retrieve sales-tax rules and their optional paging metadata."""

    records = _list_records(client, request, "/salesTaxRules", "salesTaxRules")
    if isinstance(records, ToolError):
        return records
    values, meta = records
    try:
        return SalesTaxRulesListSuccess(
            salesTaxRules=[SalesTaxRulePayload.model_validate(value) for value in values], meta=meta
        )
    except ValidationError:
        return _unexpected_response("salesTaxRules")


def list_sales_tax_accounts(
    client: BillyHttpClient, request: SalesTaxAccountsListRequest
) -> SalesTaxAccountsListSuccess | ToolError:
    """Retrieve sales-tax accounts and their optional paging metadata."""

    records = _list_records(client, request, "/salesTaxAccounts", "salesTaxAccounts")
    if isinstance(records, ToolError):
        return records
    values, meta = records
    try:
        return SalesTaxAccountsListSuccess(
            salesTaxAccounts=[SalesTaxAccountPayload.model_validate(value) for value in values],
            meta=meta,
        )
    except ValidationError:
        return _unexpected_response("salesTaxAccounts")


def list_sales_tax_meta_fields(
    client: BillyHttpClient, request: SalesTaxMetaFieldsListRequest
) -> SalesTaxMetaFieldsListSuccess | ToolError:
    """Retrieve sales-tax meta fields and their optional paging metadata."""

    records = _list_records(client, request, "/salesTaxMetaFields", "salesTaxMetaFields")
    if isinstance(records, ToolError):
        return records
    values, meta = records
    try:
        return SalesTaxMetaFieldsListSuccess(
            salesTaxMetaFields=[SalesTaxMetaFieldPayload.model_validate(value) for value in values],
            meta=meta,
        )
    except ValidationError:
        return _unexpected_response("salesTaxMetaFields")


def list_sales_tax_returns(
    client: BillyHttpClient, request: SalesTaxReturnsListRequest
) -> SalesTaxReturnsListSuccess | ToolError:
    """Retrieve sales-tax returns and their optional paging metadata."""

    records = _list_records(client, request, "/salesTaxReturns", "salesTaxReturns")
    if isinstance(records, ToolError):
        return records
    values, meta = records
    try:
        return SalesTaxReturnsListSuccess(
            salesTaxReturns=[SalesTaxReturnPayload.model_validate(value) for value in values],
            meta=meta,
        )
    except ValidationError:
        return _unexpected_response("salesTaxReturns")


def list_sales_tax_payments(
    client: BillyHttpClient, request: SalesTaxPaymentsListRequest
) -> SalesTaxPaymentsListSuccess | ToolError:
    """Retrieve sales-tax payments and their optional paging metadata."""

    records = _list_records(client, request, "/salesTaxPayments", "salesTaxPayments")
    if isinstance(records, ToolError):
        return records
    values, meta = records
    try:
        return SalesTaxPaymentsListSuccess(
            salesTaxPayments=[SalesTaxPaymentPayload.model_validate(value) for value in values],
            meta=meta,
        )
    except ValidationError:
        return _unexpected_response("salesTaxPayments")


def register_tax_read_tools(server: FastMCP, client: BillyHttpClient) -> None:
    """Register exactly the sixteen frozen sales-tax read tools."""

    def api_tax_rates_get(
        id: str = Field(min_length=1), include: str | None = None
    ) -> TaxRateGetSuccess | ToolError:
        """Read one Billy tax rate by identifier."""

        return get_tax_rate(client, TaxRateGetRequest(id=id, include=include))

    def api_tax_rates_list(
        page: int = Field(default=1, ge=1),
        pageSize: int = Field(default=DEFAULT_PAGE_SIZE, ge=1, le=MAX_PAGE_SIZE),
        include: str | None = None,
        sortProperty: str | None = None,
        sortDirection: SortDirection | None = None,
    ) -> TaxRatesListSuccess | ToolError:
        """Read Billy tax rates with documented paging, inclusion, and sorting only."""

        return list_tax_rates(
            client,
            TaxRatesListRequest(
                page=page,
                pageSize=pageSize,
                include=include,
                sortProperty=sortProperty,
                sortDirection=sortDirection,
            ),
        )

    def api_tax_rate_deduction_components_get(
        id: str = Field(min_length=1), include: str | None = None
    ) -> TaxRateDeductionComponentGetSuccess | ToolError:
        """Read one Billy tax-rate deduction component by identifier."""

        return get_tax_rate_deduction_component(
            client,
            TaxRateDeductionComponentGetRequest(id=id, include=include),
        )

    def api_tax_rate_deduction_components_list(
        page: int = Field(default=1, ge=1),
        pageSize: int = Field(default=DEFAULT_PAGE_SIZE, ge=1, le=MAX_PAGE_SIZE),
        include: str | None = None,
        sortProperty: str | None = None,
        sortDirection: SortDirection | None = None,
    ) -> TaxRateDeductionComponentsListSuccess | ToolError:
        """Read Billy tax-rate deduction components with documented list controls only."""

        return list_tax_rate_deduction_components(
            client,
            TaxRateDeductionComponentsListRequest(
                page=page,
                pageSize=pageSize,
                include=include,
                sortProperty=sortProperty,
                sortDirection=sortDirection,
            ),
        )

    def api_sales_tax_rulesets_get(
        id: str = Field(min_length=1), include: str | None = None
    ) -> SalesTaxRulesetGetSuccess | ToolError:
        """Read one Billy sales-tax ruleset by identifier."""

        return get_sales_tax_ruleset(client, SalesTaxRulesetGetRequest(id=id, include=include))

    def api_sales_tax_rulesets_list(
        page: int = Field(default=1, ge=1),
        pageSize: int = Field(default=DEFAULT_PAGE_SIZE, ge=1, le=MAX_PAGE_SIZE),
        include: str | None = None,
        sortProperty: str | None = None,
        sortDirection: SortDirection | None = None,
    ) -> SalesTaxRulesetsListSuccess | ToolError:
        """Read Billy sales-tax rulesets with documented list controls only."""

        return list_sales_tax_rulesets(
            client,
            SalesTaxRulesetsListRequest(
                page=page,
                pageSize=pageSize,
                include=include,
                sortProperty=sortProperty,
                sortDirection=sortDirection,
            ),
        )

    def api_sales_tax_rules_get(
        id: str = Field(min_length=1), include: str | None = None
    ) -> SalesTaxRuleGetSuccess | ToolError:
        """Read one Billy sales-tax rule by identifier."""

        return get_sales_tax_rule(client, SalesTaxRuleGetRequest(id=id, include=include))

    def api_sales_tax_rules_list(
        page: int = Field(default=1, ge=1),
        pageSize: int = Field(default=DEFAULT_PAGE_SIZE, ge=1, le=MAX_PAGE_SIZE),
        include: str | None = None,
        sortProperty: str | None = None,
        sortDirection: SortDirection | None = None,
    ) -> SalesTaxRulesListSuccess | ToolError:
        """Read Billy sales-tax rules with documented list controls only."""

        return list_sales_tax_rules(
            client,
            SalesTaxRulesListRequest(
                page=page,
                pageSize=pageSize,
                include=include,
                sortProperty=sortProperty,
                sortDirection=sortDirection,
            ),
        )

    def api_sales_tax_accounts_get(
        id: str = Field(min_length=1), include: str | None = None
    ) -> SalesTaxAccountGetSuccess | ToolError:
        """Read one Billy sales-tax account by identifier."""

        return get_sales_tax_account(client, SalesTaxAccountGetRequest(id=id, include=include))

    def api_sales_tax_accounts_list(
        page: int = Field(default=1, ge=1),
        pageSize: int = Field(default=DEFAULT_PAGE_SIZE, ge=1, le=MAX_PAGE_SIZE),
        include: str | None = None,
        sortProperty: str | None = None,
        sortDirection: SortDirection | None = None,
    ) -> SalesTaxAccountsListSuccess | ToolError:
        """Read Billy sales-tax accounts with documented list controls only."""

        return list_sales_tax_accounts(
            client,
            SalesTaxAccountsListRequest(
                page=page,
                pageSize=pageSize,
                include=include,
                sortProperty=sortProperty,
                sortDirection=sortDirection,
            ),
        )

    def api_sales_tax_meta_fields_get(
        id: str = Field(min_length=1), include: str | None = None
    ) -> SalesTaxMetaFieldGetSuccess | ToolError:
        """Read one Billy sales-tax meta field by identifier."""

        return get_sales_tax_meta_field(
            client,
            SalesTaxMetaFieldGetRequest(id=id, include=include),
        )

    def api_sales_tax_meta_fields_list(
        page: int = Field(default=1, ge=1),
        pageSize: int = Field(default=DEFAULT_PAGE_SIZE, ge=1, le=MAX_PAGE_SIZE),
        include: str | None = None,
        sortProperty: str | None = None,
        sortDirection: SortDirection | None = None,
    ) -> SalesTaxMetaFieldsListSuccess | ToolError:
        """Read Billy sales-tax meta fields with documented list controls only."""

        return list_sales_tax_meta_fields(
            client,
            SalesTaxMetaFieldsListRequest(
                page=page,
                pageSize=pageSize,
                include=include,
                sortProperty=sortProperty,
                sortDirection=sortDirection,
            ),
        )

    def api_sales_tax_returns_get(
        id: str = Field(min_length=1), include: str | None = None
    ) -> SalesTaxReturnGetSuccess | ToolError:
        """Read one Billy sales-tax return by identifier."""

        return get_sales_tax_return(client, SalesTaxReturnGetRequest(id=id, include=include))

    def api_sales_tax_returns_list(
        page: int = Field(default=1, ge=1),
        pageSize: int = Field(default=DEFAULT_PAGE_SIZE, ge=1, le=MAX_PAGE_SIZE),
        include: str | None = None,
        sortProperty: str | None = None,
        sortDirection: SortDirection | None = None,
    ) -> SalesTaxReturnsListSuccess | ToolError:
        """Read Billy sales-tax returns with documented list controls only."""

        return list_sales_tax_returns(
            client,
            SalesTaxReturnsListRequest(
                page=page,
                pageSize=pageSize,
                include=include,
                sortProperty=sortProperty,
                sortDirection=sortDirection,
            ),
        )

    def api_sales_tax_payments_get(
        id: str = Field(min_length=1), include: str | None = None
    ) -> SalesTaxPaymentGetSuccess | ToolError:
        """Read one Billy sales-tax payment by identifier."""

        return get_sales_tax_payment(client, SalesTaxPaymentGetRequest(id=id, include=include))

    def api_sales_tax_payments_list(
        page: int = Field(default=1, ge=1),
        pageSize: int = Field(default=DEFAULT_PAGE_SIZE, ge=1, le=MAX_PAGE_SIZE),
        include: str | None = None,
        sortProperty: str | None = None,
        sortDirection: SortDirection | None = None,
    ) -> SalesTaxPaymentsListSuccess | ToolError:
        """Read Billy sales-tax payments with documented list controls only."""

        return list_sales_tax_payments(
            client,
            SalesTaxPaymentsListRequest(
                page=page,
                pageSize=pageSize,
                include=include,
                sortProperty=sortProperty,
                sortDirection=sortDirection,
            ),
        )

    server.tool(name="api_tax_rates_get", description="Read one Billy tax rate.")(api_tax_rates_get)
    server.tool(name="api_tax_rates_list", description="List Billy tax rates.")(api_tax_rates_list)
    server.tool(
        name="api_tax_rate_deduction_components_get",
        description="Read one Billy tax-rate deduction component.",
    )(api_tax_rate_deduction_components_get)
    server.tool(
        name="api_tax_rate_deduction_components_list",
        description="List Billy tax-rate deduction components.",
    )(api_tax_rate_deduction_components_list)
    server.tool(name="api_sales_tax_rulesets_get", description="Read one Billy sales-tax ruleset.")(
        api_sales_tax_rulesets_get
    )
    server.tool(name="api_sales_tax_rulesets_list", description="List Billy sales-tax rulesets.")(
        api_sales_tax_rulesets_list
    )
    server.tool(name="api_sales_tax_rules_get", description="Read one Billy sales-tax rule.")(
        api_sales_tax_rules_get
    )
    server.tool(name="api_sales_tax_rules_list", description="List Billy sales-tax rules.")(
        api_sales_tax_rules_list
    )
    server.tool(name="api_sales_tax_accounts_get", description="Read one Billy sales-tax account.")(
        api_sales_tax_accounts_get
    )
    server.tool(name="api_sales_tax_accounts_list", description="List Billy sales-tax accounts.")(
        api_sales_tax_accounts_list
    )
    server.tool(
        name="api_sales_tax_meta_fields_get",
        description="Read one Billy sales-tax meta field.",
    )(api_sales_tax_meta_fields_get)
    server.tool(
        name="api_sales_tax_meta_fields_list", description="List Billy sales-tax meta fields."
    )(api_sales_tax_meta_fields_list)
    server.tool(name="api_sales_tax_returns_get", description="Read one Billy sales-tax return.")(
        api_sales_tax_returns_get
    )
    server.tool(name="api_sales_tax_returns_list", description="List Billy sales-tax returns.")(
        api_sales_tax_returns_list
    )
    server.tool(name="api_sales_tax_payments_get", description="Read one Billy sales-tax payment.")(
        api_sales_tax_payments_get
    )
    server.tool(name="api_sales_tax_payments_list", description="List Billy sales-tax payments.")(
        api_sales_tax_payments_list
    )


def _get_record(
    client: BillyHttpClient, request: _GetRequest, collection_path: str, root: str
) -> Mapping[str, object] | ToolError:
    """Read a singular resource and validate its documented object root."""

    response = client.request(
        "GET",
        f"{collection_path}/{quote(request.id, safe='')}",
        params=request.query_params() or None,
    )
    if isinstance(response, ToolError):
        return response
    payload = _response_mapping(response)
    record = None if payload is None else _object_mapping(payload.get(root))
    return _unexpected_response(root) if record is None else record


def _list_records(
    client: BillyHttpClient, request: _ListRequest, collection_path: str, root: str
) -> tuple[list[Mapping[str, object]], TaxMeta | None] | ToolError:
    """Read a collection and validate its documented list and optional meta roots."""

    response = client.request("GET", collection_path, params=request.query_params())
    if isinstance(response, ToolError):
        return response
    payload = _response_mapping(response)
    values: object = None if payload is None else payload.get(root)
    if not isinstance(values, list):
        return _unexpected_response(root)
    records: list[Mapping[str, object]] = []
    for value in cast(list[object], values):
        record = _object_mapping(value)
        if record is None:
            return _unexpected_response(root)
        records.append(record)
    meta_value: object = None if payload is None else payload.get("meta")
    meta = _object_mapping(meta_value)
    if meta_value is not None and meta is None:
        return _unexpected_response("meta")
    try:
        return records, None if meta is None else TaxMeta.model_validate(meta)
    except ValidationError:
        return _unexpected_response("meta")


def _response_mapping(response: BillyResponse) -> Mapping[str, object] | None:
    """Narrow a successful client payload to the JSON object expected by these reads."""

    return _object_mapping(response.data)


def _object_mapping(value: object) -> Mapping[str, object] | None:
    """Narrow untyped decoded JSON to an object mapping."""

    if not isinstance(value, Mapping):
        return None
    return cast(Mapping[str, object], value)


def _unexpected_response(root: str) -> ToolError:
    """Avoid inventing a success shape when Billy omits a documented response root."""

    return ToolError(
        code=StableErrorCode.BILLY_ERROR,
        message="Billy API response did not contain a documented sales-tax root.",
        details={"expected_root": root},
    )
