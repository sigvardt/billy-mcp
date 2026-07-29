"""Contract tests for the frozen, read-only Billy sales-tax tools."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

import httpx
import pytest
from fastmcp import FastMCP
from pydantic import BaseModel, ValidationError

from billy_mcp.api.tax_reads import (
    SalesTaxAccountGetRequest,
    SalesTaxAccountsListRequest,
    SalesTaxMetaFieldGetRequest,
    SalesTaxMetaFieldsListRequest,
    SalesTaxPaymentGetRequest,
    SalesTaxPaymentsListRequest,
    SalesTaxReturnGetRequest,
    SalesTaxReturnsListRequest,
    SalesTaxRuleGetRequest,
    SalesTaxRulesetGetRequest,
    SalesTaxRulesetsListRequest,
    SalesTaxRulesListRequest,
    SortDirection,
    TaxRateDeductionComponentGetRequest,
    TaxRateDeductionComponentsListRequest,
    TaxRateGetRequest,
    TaxRatesListRequest,
    get_sales_tax_account,
    get_sales_tax_meta_field,
    get_sales_tax_payment,
    get_sales_tax_return,
    get_sales_tax_rule,
    get_sales_tax_ruleset,
    get_tax_rate,
    get_tax_rate_deduction_component,
    list_sales_tax_accounts,
    list_sales_tax_meta_fields,
    list_sales_tax_payments,
    list_sales_tax_returns,
    list_sales_tax_rules,
    list_sales_tax_rulesets,
    list_tax_rate_deduction_components,
    list_tax_rates,
    register_tax_read_tools,
)
from billy_mcp.client import BillyHttpClient
from billy_mcp.models import StableErrorCode, ToolError

ReadFunction = Callable[..., BaseModel | ToolError]


@dataclass(frozen=True)
class Resource:
    """Frozen path, root, handler, and input-model facts for one resource."""

    collection: str
    singular: str
    plural: str
    get_tool: str
    list_tool: str
    get_request: type[BaseModel]
    list_request: type[BaseModel]
    get: ReadFunction
    list: ReadFunction


RESOURCES = (
    Resource(
        collection="taxRates",
        singular="taxRate",
        plural="taxRates",
        get_tool="api_tax_rates_get",
        list_tool="api_tax_rates_list",
        get_request=TaxRateGetRequest,
        list_request=TaxRatesListRequest,
        get=get_tax_rate,
        list=list_tax_rates,
    ),
    Resource(
        collection="taxRateDeductionComponents",
        singular="taxRateDeductionComponent",
        plural="taxRateDeductionComponents",
        get_tool="api_tax_rate_deduction_components_get",
        list_tool="api_tax_rate_deduction_components_list",
        get_request=TaxRateDeductionComponentGetRequest,
        list_request=TaxRateDeductionComponentsListRequest,
        get=get_tax_rate_deduction_component,
        list=list_tax_rate_deduction_components,
    ),
    Resource(
        collection="salesTaxRulesets",
        singular="salesTaxRuleset",
        plural="salesTaxRulesets",
        get_tool="api_sales_tax_rulesets_get",
        list_tool="api_sales_tax_rulesets_list",
        get_request=SalesTaxRulesetGetRequest,
        list_request=SalesTaxRulesetsListRequest,
        get=get_sales_tax_ruleset,
        list=list_sales_tax_rulesets,
    ),
    Resource(
        collection="salesTaxRules",
        singular="salesTaxRule",
        plural="salesTaxRules",
        get_tool="api_sales_tax_rules_get",
        list_tool="api_sales_tax_rules_list",
        get_request=SalesTaxRuleGetRequest,
        list_request=SalesTaxRulesListRequest,
        get=get_sales_tax_rule,
        list=list_sales_tax_rules,
    ),
    Resource(
        collection="salesTaxAccounts",
        singular="salesTaxAccount",
        plural="salesTaxAccounts",
        get_tool="api_sales_tax_accounts_get",
        list_tool="api_sales_tax_accounts_list",
        get_request=SalesTaxAccountGetRequest,
        list_request=SalesTaxAccountsListRequest,
        get=get_sales_tax_account,
        list=list_sales_tax_accounts,
    ),
    Resource(
        collection="salesTaxMetaFields",
        singular="salesTaxMetaField",
        plural="salesTaxMetaFields",
        get_tool="api_sales_tax_meta_fields_get",
        list_tool="api_sales_tax_meta_fields_list",
        get_request=SalesTaxMetaFieldGetRequest,
        list_request=SalesTaxMetaFieldsListRequest,
        get=get_sales_tax_meta_field,
        list=list_sales_tax_meta_fields,
    ),
    Resource(
        collection="salesTaxReturns",
        singular="salesTaxReturn",
        plural="salesTaxReturns",
        get_tool="api_sales_tax_returns_get",
        list_tool="api_sales_tax_returns_list",
        get_request=SalesTaxReturnGetRequest,
        list_request=SalesTaxReturnsListRequest,
        get=get_sales_tax_return,
        list=list_sales_tax_returns,
    ),
    Resource(
        collection="salesTaxPayments",
        singular="salesTaxPayment",
        plural="salesTaxPayments",
        get_tool="api_sales_tax_payments_get",
        list_tool="api_sales_tax_payments_list",
        get_request=SalesTaxPaymentGetRequest,
        list_request=SalesTaxPaymentsListRequest,
        get=get_sales_tax_payment,
        list=list_sales_tax_payments,
    ),
)


def make_client(handler: httpx.MockTransport) -> BillyHttpClient:
    """Create a token-backed locked client against an in-process mock transport."""

    return BillyHttpClient(lambda: "test-token", transport=handler)


@pytest.mark.parametrize("resource", RESOURCES, ids=lambda resource: resource.collection)
def test_singular_reads_encode_ids_and_map_every_documented_root(resource: Resource) -> None:
    requests: list[httpx.Request] = []
    identifier = "tax /? id"

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return httpx.Response(200, json={resource.singular: {"id": identifier, "opaque": True}})

    result = resource.get(
        make_client(httpx.MockTransport(handler)),
        resource.get_request(id=identifier, include="related"),
    )

    assert isinstance(result, BaseModel)
    assert not isinstance(result, ToolError)
    assert result.model_dump() == {resource.singular: {"id": identifier, "opaque": True}}
    assert str(requests[0].url) == (
        f"https://api.billysbilling.com/v2/{resource.collection}/tax%20%2F%3F%20id?include=related"
    )
    assert requests[0].method == "GET"


@pytest.mark.parametrize("resource", RESOURCES, ids=lambda resource: resource.collection)
def test_lists_use_only_documented_query_and_map_every_root_with_paging(
    resource: Resource,
) -> None:
    requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return httpx.Response(
            200,
            json={
                resource.plural: [{"id": resource.collection, "opaque": resource.singular}],
                "meta": {
                    "paging": {
                        "page": 2,
                        "pageCount": 3,
                        "pageSize": 50,
                        "total": 125,
                        "firstUrl": f"/{resource.collection}?page=1",
                        "previousUrl": f"/{resource.collection}?page=1",
                        "nextUrl": f"/{resource.collection}?page=3",
                        "lastUrl": f"/{resource.collection}?page=3",
                    }
                },
            },
        )

    result = resource.list(
        make_client(httpx.MockTransport(handler)),
        resource.list_request(
            page=2,
            pageSize=50,
            include="related",
            sortProperty="name",
            sortDirection=SortDirection.DESC,
        ),
    )

    assert isinstance(result, BaseModel)
    assert not isinstance(result, ToolError)
    assert result.model_dump()[resource.plural] == [
        {"id": resource.collection, "opaque": resource.singular}
    ]
    assert result.model_dump(by_alias=True)["meta"]["paging"]["pageCount"] == 3
    assert result.model_dump(by_alias=True)["meta"]["paging"]["nextUrl"] == (
        f"/{resource.collection}?page=3"
    )
    assert requests[0].url.path == f"/v2/{resource.collection}"
    assert requests[0].url.params == httpx.QueryParams(
        {
            "page": "2",
            "pageSize": "50",
            "include": "related",
            "sortProperty": "name",
            "sortDirection": "DESC",
        }
    )
    assert {key for key, _ in requests[0].url.params.multi_items()} == {
        "page",
        "pageSize",
        "include",
        "sortProperty",
        "sortDirection",
    }


@pytest.mark.parametrize("resource", RESOURCES, ids=lambda resource: resource.collection)
def test_lists_preserve_an_absent_optional_meta_root(resource: Resource) -> None:
    requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return httpx.Response(200, json={resource.plural: []})

    result = resource.list(make_client(httpx.MockTransport(handler)), resource.list_request())

    assert isinstance(result, BaseModel)
    assert not isinstance(result, ToolError)
    assert result.model_dump() == {resource.plural: []}
    assert requests[0].url.params == httpx.QueryParams({"page": "1", "pageSize": "1000"})


@pytest.mark.parametrize("request_type", [resource.get_request for resource in RESOURCES])
@pytest.mark.parametrize(
    ("values", "field"),
    [({"id": ""}, "id"), ({"id": "tax-1", "unexpected": "value"}, "unexpected")],
)
def test_get_requests_reject_blank_ids_and_unknown_keys(
    request_type: type[BaseModel], values: dict[str, object], field: str
) -> None:
    with pytest.raises(ValidationError) as failure:
        request_type.model_validate(values)

    assert failure.value.errors()[0]["loc"] == (field,)


@pytest.mark.parametrize("request_type", [resource.list_request for resource in RESOURCES])
@pytest.mark.parametrize(
    ("values", "field"),
    [
        ({"page": 0}, "page"),
        ({"pageSize": 0}, "pageSize"),
        ({"pageSize": 1001}, "pageSize"),
        ({"sortDirection": "DOWN"}, "sortDirection"),
        ({"offset": 1}, "offset"),
        ({"taxRateId": "tax-rate-1"}, "taxRateId"),
        ({"rulesetId": "ruleset-1"}, "rulesetId"),
        ({"organizationId": "organization-1"}, "organizationId"),
        ({"source": "unknown"}, "source"),
        ({"type": "unknown"}, "type"),
        ({"contactType": "unknown"}, "contactType"),
        ({"periodType": "unknown"}, "periodType"),
        ({"q": "tax"}, "q"),
    ],
)
def test_list_requests_reject_paging_escapes_and_undeclared_filters(
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
    results: list[BaseModel | ToolError] = []
    for resource in RESOURCES:
        results.extend(
            [
                resource.get(client, resource.get_request(id="tax-1")),
                resource.list(client, resource.list_request()),
            ]
        )

    assert len(results) == 16
    assert all(isinstance(result, ToolError) for result in results)
    assert {result.code for result in results if isinstance(result, ToolError)} == {
        StableErrorCode.AUTH_REQUIRED
    }


@pytest.mark.parametrize("resource", RESOURCES, ids=lambda resource: resource.collection)
def test_undeclared_response_roots_return_typed_errors(resource: Resource) -> None:
    result = resource.get(
        make_client(httpx.MockTransport(lambda request: httpx.Response(200, json={"wrong": {}}))),
        resource.get_request(id="tax-1"),
    )

    assert isinstance(result, ToolError)
    assert result.code is StableErrorCode.BILLY_ERROR
    assert result.details == {"expected_root": resource.singular}


@pytest.mark.parametrize("resource", RESOURCES, ids=lambda resource: resource.collection)
def test_undeclared_list_response_roots_return_typed_errors(resource: Resource) -> None:
    result = resource.list(
        make_client(httpx.MockTransport(lambda request: httpx.Response(200, json={"wrong": []}))),
        resource.list_request(),
    )

    assert isinstance(result, ToolError)
    assert result.code is StableErrorCode.BILLY_ERROR
    assert result.details == {"expected_root": resource.plural}


@pytest.mark.asyncio
async def test_registration_exposes_exactly_sixteen_scoped_flat_read_tools() -> None:
    collections = {resource.collection: resource for resource in RESOURCES}

    def handler(request: httpx.Request) -> httpx.Response:
        path_parts = request.url.path.removeprefix("/v2/").split("/")
        resource = collections[path_parts[0]]
        if len(path_parts) == 1:
            return httpx.Response(200, json={resource.plural: [{"id": resource.collection}]})
        return httpx.Response(200, json={resource.singular: {"id": resource.collection}})

    server = FastMCP("tax-reads-test")
    register_tax_read_tools(server, make_client(httpx.MockTransport(handler)))

    tools = {tool.name: tool for tool in await server.list_tools()}
    assert set(tools) == {resource.get_tool for resource in RESOURCES} | {
        resource.list_tool for resource in RESOURCES
    }
    for resource in RESOURCES:
        assert set(tools[resource.get_tool].parameters["properties"]) == {"id", "include"}
        assert set(tools[resource.list_tool].parameters["properties"]) == {
            "page",
            "pageSize",
            "include",
            "sortProperty",
            "sortDirection",
        }
        assert "offset" not in tools[resource.list_tool].parameters["properties"]
        for field in ("taxRateId", "rulesetId", "source", "type", "contactType", "periodType"):
            assert field not in tools[resource.list_tool].parameters["properties"]
        get_result = await server.call_tool(resource.get_tool, {"id": resource.collection})
        list_result = await server.call_tool(resource.list_tool, {"page": 1, "pageSize": 1000})
        assert get_result.structured_content == {
            "result": {resource.singular: {"id": resource.collection}}
        }
        assert list_result.structured_content == {
            "result": {resource.plural: [{"id": resource.collection}]}
        }
