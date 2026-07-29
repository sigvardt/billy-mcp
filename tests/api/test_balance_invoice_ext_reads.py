"""Synthetic contract tests for frozen balance and invoice-extension reads."""

from __future__ import annotations

from collections.abc import Callable

import httpx
import pytest
from fastmcp import FastMCP
from pydantic import BaseModel, ValidationError

from billy_mcp.api.balance_invoice_ext_reads import (
    BalanceInvoiceExtensionGetRequest,
    BalanceInvoiceExtensionListRequest,
    BalanceInvoiceExtensionReadService,
    ContactBalancePaymentGetSuccess,
    ContactBalancePaymentsListSuccess,
    ContactBalancePostingGetSuccess,
    ContactBalancePostingsListSuccess,
    InvoiceLateFeeGetSuccess,
    InvoiceLateFeesListSuccess,
    InvoiceReminderAssociationGetSuccess,
    InvoiceReminderAssociationsListSuccess,
    InvoiceReminderGetSuccess,
    InvoiceRemindersListSuccess,
    SortDirection,
    register_balance_invoice_extension_read_tools,
)
from billy_mcp.client import BillyHttpClient
from billy_mcp.models import StableErrorCode, ToolError

MockHandler = Callable[[httpx.Request], httpx.Response]
ClientFactory = Callable[[MockHandler], tuple[BillyHttpClient, list[httpx.Request]]]


@pytest.fixture
def client_factory() -> ClientFactory:
    """Provide the locked client against an in-process mock transport only."""

    def build(handler: MockHandler) -> tuple[BillyHttpClient, list[httpx.Request]]:
        requests: list[httpx.Request] = []

        def record_request(request: httpx.Request) -> httpx.Response:
            requests.append(request)
            return handler(request)

        return (
            BillyHttpClient(lambda: "test-token", transport=httpx.MockTransport(record_request)),
            requests,
        )

    return build


def test_singular_reads_encode_identifiers_and_map_every_documented_root(
    client_factory: ClientFactory,
) -> None:
    """Every singular handler confines its identifier to one encoded path segment."""

    roots = iter(
        (
            ("contactBalancePayment", {"id": "payment /?"}),
            ("contactBalancePosting", {"id": "posting /?"}),
            ("invoiceLateFee", {"id": "late-fee /?"}),
            ("invoiceReminder", {"id": "reminder /?"}),
            ("invoiceReminderAssociation", {"id": "association /?"}),
        )
    )

    def handler(request: httpx.Request) -> httpx.Response:
        root, record = next(roots)
        return httpx.Response(200, json={root: record})

    client, requests = client_factory(handler)
    service = BalanceInvoiceExtensionReadService(client)

    payment = service.contact_balance_payments_get(
        BalanceInvoiceExtensionGetRequest(id="payment /?", include="contact")
    )
    posting = service.contact_balance_postings_get(
        BalanceInvoiceExtensionGetRequest(id="posting /?", include="originator")
    )
    late_fee = service.invoice_late_fees_get(
        BalanceInvoiceExtensionGetRequest(id="late-fee /?", include="invoice")
    )
    reminder = service.invoice_reminders_get(
        BalanceInvoiceExtensionGetRequest(id="reminder /?", include="contact")
    )
    association = service.invoice_reminder_associations_get(
        BalanceInvoiceExtensionGetRequest(id="association /?", include="reminder")
    )

    assert isinstance(payment, ContactBalancePaymentGetSuccess)
    assert payment.contactBalancePayment.model_dump() == {"id": "payment /?"}
    assert isinstance(posting, ContactBalancePostingGetSuccess)
    assert posting.contactBalancePosting.model_dump() == {"id": "posting /?"}
    assert isinstance(late_fee, InvoiceLateFeeGetSuccess)
    assert late_fee.invoiceLateFee.model_dump() == {"id": "late-fee /?"}
    assert isinstance(reminder, InvoiceReminderGetSuccess)
    assert reminder.invoiceReminder.model_dump() == {"id": "reminder /?"}
    assert isinstance(association, InvoiceReminderAssociationGetSuccess)
    assert association.invoiceReminderAssociation.model_dump() == {"id": "association /?"}
    assert [str(request.url) for request in requests] == [
        "https://api.billysbilling.com/v2/contactBalancePayments/payment%20%2F%3F?include=contact",
        "https://api.billysbilling.com/v2/contactBalancePostings/posting%20%2F%3F?include=originator",
        "https://api.billysbilling.com/v2/invoiceLateFees/late-fee%20%2F%3F?include=invoice",
        "https://api.billysbilling.com/v2/invoiceReminders/reminder%20%2F%3F?include=contact",
        "https://api.billysbilling.com/v2/invoiceReminderAssociations/association%20%2F%3F?include=reminder",
    ]
    assert all(request.method == "GET" for request in requests)


def test_lists_use_only_the_frozen_query_allowlist_and_preserve_paging(
    client_factory: ClientFactory,
) -> None:
    """Every collection path maps its plural root and documented paging envelope."""

    roots = {
        "/v2/contactBalancePayments": "contactBalancePayments",
        "/v2/contactBalancePostings": "contactBalancePostings",
        "/v2/invoiceLateFees": "invoiceLateFees",
        "/v2/invoiceReminders": "invoiceReminders",
        "/v2/invoiceReminderAssociations": "invoiceReminderAssociations",
    }

    def handler(request: httpx.Request) -> httpx.Response:
        root = roots[request.url.path]
        return httpx.Response(
            200,
            json={
                root: [{"id": root}],
                "meta": {
                    "paging": {
                        "page": 2,
                        "pageCount": 3,
                        "pageSize": 25,
                        "total": 60,
                        "nextUrl": f"/{root}?page=3",
                    }
                },
            },
        )

    client, requests = client_factory(handler)
    service = BalanceInvoiceExtensionReadService(client)
    request = BalanceInvoiceExtensionListRequest(
        page=2,
        pageSize=25,
        include="originator",
        sortProperty="createdTime",
        sortDirection=SortDirection.DESC,
    )

    payments = service.contact_balance_payments_list(request)
    postings = service.contact_balance_postings_list(request)
    late_fees = service.invoice_late_fees_list(request)
    reminders = service.invoice_reminders_list(request)
    associations = service.invoice_reminder_associations_list(request)

    assert isinstance(payments, ContactBalancePaymentsListSuccess)
    assert payments.contactBalancePayments[0].model_dump() == {"id": "contactBalancePayments"}
    assert isinstance(postings, ContactBalancePostingsListSuccess)
    assert postings.contactBalancePostings[0].model_dump() == {"id": "contactBalancePostings"}
    assert isinstance(late_fees, InvoiceLateFeesListSuccess)
    assert late_fees.invoiceLateFees[0].model_dump() == {"id": "invoiceLateFees"}
    assert isinstance(reminders, InvoiceRemindersListSuccess)
    assert reminders.invoiceReminders[0].model_dump() == {"id": "invoiceReminders"}
    assert isinstance(associations, InvoiceReminderAssociationsListSuccess)
    assert associations.invoiceReminderAssociations[0].model_dump() == {
        "id": "invoiceReminderAssociations"
    }
    for result in (payments, postings, late_fees, reminders, associations):
        assert result.meta is not None and result.meta.paging is not None
        assert result.meta.paging.model_dump()["page"] == 2
        assert result.meta.paging.model_dump()["pageCount"] == 3
        assert result.meta.paging.model_dump()["pageSize"] == 25
        assert result.meta.paging.model_dump()["total"] == 60
        assert result.meta.paging.model_dump()["nextUrl"].endswith("?page=3")
    expected_params = httpx.QueryParams(
        {
            "page": "2",
            "pageSize": "25",
            "include": "originator",
            "sortProperty": "createdTime",
            "sortDirection": "DESC",
        }
    )
    assert [request.url.path for request in requests] == list(roots)
    assert all(request.url.params == expected_params for request in requests)
    assert all(set(request.url.params) == set(expected_params) for request in requests)


def test_default_list_query_and_absent_meta_are_preserved_without_fabrication(
    client_factory: ClientFactory,
) -> None:
    """Default paging has no undocumented query keys or invented metadata."""

    client, requests = client_factory(
        lambda request: httpx.Response(200, json={"invoiceReminders": []})
    )

    result = BalanceInvoiceExtensionReadService(client).invoice_reminders_list(
        BalanceInvoiceExtensionListRequest()
    )

    assert isinstance(result, InvoiceRemindersListSuccess)
    assert result.model_dump() == {"invoiceReminders": []}
    assert requests[0].url.params == httpx.QueryParams({"page": "1", "pageSize": "1000"})


def test_list_request_accepts_both_documented_page_size_boundaries() -> None:
    """The lower and upper documented page-size bounds are usable."""

    assert BalanceInvoiceExtensionListRequest(pageSize=1).page_size == 1
    assert BalanceInvoiceExtensionListRequest(pageSize=1000).page_size == 1000


@pytest.mark.parametrize(
    ("request_type", "values", "field"),
    [
        (BalanceInvoiceExtensionGetRequest, {"id": ""}, "id"),
        (BalanceInvoiceExtensionGetRequest, {"id": "record-1", "include": ""}, "include"),
        (BalanceInvoiceExtensionGetRequest, {"id": "record-1", "page": 1}, "page"),
        (BalanceInvoiceExtensionGetRequest, {"id": "record-1", "request": {}}, "request"),
        (BalanceInvoiceExtensionListRequest, {"page": 0}, "page"),
        (BalanceInvoiceExtensionListRequest, {"pageSize": 0}, "pageSize"),
        (BalanceInvoiceExtensionListRequest, {"pageSize": 1001}, "pageSize"),
        (BalanceInvoiceExtensionListRequest, {"include": ""}, "include"),
        (BalanceInvoiceExtensionListRequest, {"sortProperty": ""}, "sortProperty"),
        (BalanceInvoiceExtensionListRequest, {"sortDirection": "DOWN"}, "sortDirection"),
        (BalanceInvoiceExtensionListRequest, {"offset": 0}, "offset"),
        (BalanceInvoiceExtensionListRequest, {"request": {}}, "request"),
        (BalanceInvoiceExtensionListRequest, {"invoiceId": "invoice-1"}, "invoiceId"),
        (BalanceInvoiceExtensionListRequest, {"contactId": "contact-1"}, "contactId"),
        (BalanceInvoiceExtensionListRequest, {"reminderId": "reminder-1"}, "reminderId"),
        (BalanceInvoiceExtensionListRequest, {"unexpected": "value"}, "unexpected"),
    ],
)
def test_requests_reject_unknown_fields_and_out_of_contract_values(
    request_type: type[BaseModel], values: dict[str, object], field: str
) -> None:
    """Flat request models reject paging escapes, nesting, and invented filters."""

    with pytest.raises(ValidationError) as failure:
        request_type.model_validate(values)

    assert failure.value.errors()[0]["loc"] == (field,)


@pytest.mark.parametrize("error_code", ["AUTHENTICATION_REQUIRED", "OAUTH_INVALID_ACCESS_TOKEN"])
def test_all_ten_handlers_preserve_both_documented_typed_authentication_errors(
    client_factory: ClientFactory, error_code: str
) -> None:
    """The locked client maps both proved 401 envelopes to ``AUTH_REQUIRED``."""

    client, requests = client_factory(
        lambda request: httpx.Response(401, json={"errorCode": error_code})
    )
    service = BalanceInvoiceExtensionReadService(client)
    get_request = BalanceInvoiceExtensionGetRequest(id="record-1")
    list_request = BalanceInvoiceExtensionListRequest()

    results = (
        service.contact_balance_payments_get(get_request),
        service.contact_balance_payments_list(list_request),
        service.contact_balance_postings_get(get_request),
        service.contact_balance_postings_list(list_request),
        service.invoice_late_fees_get(get_request),
        service.invoice_late_fees_list(list_request),
        service.invoice_reminders_get(get_request),
        service.invoice_reminders_list(list_request),
        service.invoice_reminder_associations_get(get_request),
        service.invoice_reminder_associations_list(list_request),
    )

    assert all(isinstance(result, ToolError) for result in results)
    assert {result.code for result in results if isinstance(result, ToolError)} == {
        StableErrorCode.AUTH_REQUIRED
    }
    assert [request.url.path for request in requests] == [
        "/v2/contactBalancePayments/record-1",
        "/v2/contactBalancePayments",
        "/v2/contactBalancePostings/record-1",
        "/v2/contactBalancePostings",
        "/v2/invoiceLateFees/record-1",
        "/v2/invoiceLateFees",
        "/v2/invoiceReminders/record-1",
        "/v2/invoiceReminders",
        "/v2/invoiceReminderAssociations/record-1",
        "/v2/invoiceReminderAssociations",
    ]


def test_malformed_singular_and_plural_roots_return_typed_errors(
    client_factory: ClientFactory,
) -> None:
    """Unexpected response roots never become guessed success payloads."""

    singular_client, _ = client_factory(lambda request: httpx.Response(200, json={"wrong": {}}))
    plural_client, _ = client_factory(
        lambda request: httpx.Response(200, json={"invoiceLateFees": {}})
    )

    singular_result = BalanceInvoiceExtensionReadService(singular_client).invoice_reminders_get(
        BalanceInvoiceExtensionGetRequest(id="reminder-1")
    )
    plural_result = BalanceInvoiceExtensionReadService(plural_client).invoice_late_fees_list(
        BalanceInvoiceExtensionListRequest()
    )

    assert isinstance(singular_result, ToolError)
    assert singular_result.code is StableErrorCode.BILLY_ERROR
    assert singular_result.details == {"expected_root": "invoiceReminder"}
    assert isinstance(plural_result, ToolError)
    assert plural_result.code is StableErrorCode.BILLY_ERROR
    assert plural_result.details == {"expected_root": "invoiceLateFees"}


@pytest.mark.asyncio
async def test_registers_exactly_ten_flat_tools_with_structured_output(
    client_factory: ClientFactory,
) -> None:
    """FastMCP exposes direct flat schemas and serialisable successful results."""

    list_roots = {
        "/v2/contactBalancePayments": "contactBalancePayments",
        "/v2/contactBalancePostings": "contactBalancePostings",
        "/v2/invoiceLateFees": "invoiceLateFees",
        "/v2/invoiceReminders": "invoiceReminders",
        "/v2/invoiceReminderAssociations": "invoiceReminderAssociations",
    }

    def handler(request: httpx.Request) -> httpx.Response:
        root = list_roots.get(request.url.path)
        if root is not None:
            return httpx.Response(200, json={root: []})
        return httpx.Response(200, json={"invoiceReminder": {"id": "reminder-1"}})

    client, _ = client_factory(handler)
    server = FastMCP("balance-invoice-extension-test")
    register_balance_invoice_extension_read_tools(server, client)

    tools = {tool.name: tool for tool in await server.list_tools()}
    assert set(tools) == {
        "api_contact_balance_payments_get",
        "api_contact_balance_payments_list",
        "api_contact_balance_postings_get",
        "api_contact_balance_postings_list",
        "api_invoice_late_fees_get",
        "api_invoice_late_fees_list",
        "api_invoice_reminders_get",
        "api_invoice_reminders_list",
        "api_invoice_reminder_associations_get",
        "api_invoice_reminder_associations_list",
    }
    get_tools = {
        "api_contact_balance_payments_get",
        "api_contact_balance_postings_get",
        "api_invoice_late_fees_get",
        "api_invoice_reminders_get",
        "api_invoice_reminder_associations_get",
    }
    list_tools = set(tools) - get_tools
    for name in get_tools:
        assert set(tools[name].parameters["properties"]) == {"id", "include"}
        assert tools[name].parameters["required"] == ["id"]
    for name in list_tools:
        properties = tools[name].parameters["properties"]
        assert set(properties) == {"page", "pageSize", "include", "sortProperty", "sortDirection"}
        assert "request" not in properties
        assert "offset" not in properties
        assert "invoiceId" not in properties
        assert "contactId" not in properties
        assert "reminderId" not in properties

    list_result = await server.call_tool(
        "api_contact_balance_payments_list", {"page": 1, "pageSize": 1000}
    )
    get_result = await server.call_tool("api_invoice_reminders_get", {"id": "reminder-1"})

    assert list_result.structured_content == {"result": {"contactBalancePayments": []}}
    assert get_result.structured_content == {"result": {"invoiceReminder": {"id": "reminder-1"}}}
