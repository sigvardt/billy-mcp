---
name: wave_two_filtered_reads_contract
desc: Frozen official contract for the invoice, bill, and daybook-transaction API read wave.
tags: [billy, api, read_only, filters]
sources:
  - https://www.billy.dk/api/
  - .fractal/main.billy_complete/tmp/grok-research.md
created: 2026-07-29T10:19:00Z
updated: 2026-07-29T10:53:00Z
---

# wave_two_filtered_reads_contract

This contract bounds the next read-only API wave. It is based on the cited
official-document brief with unchanged fingerprint `hsisik4g9p3603` /
`c2efda0ee4cf9cf200e14910c5fc6996`. It is not an implementation or live-test
claim.

## Shared rules

- Use the locked `https://api.billysbilling.com/v2` client and relative paths.
- Each tool has Pydantic input and success models and returns typed
  `ToolError`; no generic HTTP or browser controls are allowed.
- Every list accepts `page`, `pageSize` (1–1000), and optional `include`, then
  only the resource-specific documented filters below. Offset paging is not
  permitted.
- Singular roots are `invoice`, `bill`, and `daybookTransaction`; list roots
  are `invoices`, `bills`, and `daybookTransactions`, with optional
  `meta.paging`.
- Contract tests cover path and query construction, local filter rejection,
  response roots, paging, and typed 401 mapping. `live_tested` stays false
  without the dedicated non-production organisation and token.

## Owned tools and filters

| Resource | Tools | Additional documented filters |
| --- | --- | --- |
| Invoices | `api_invoices_get`, `api_invoices_list` | `organizationId`, `contactId`, `creditedInvoiceId`, `state`, `invoiceNo`, `externalId`, `minEntryDate`, `maxEntryDate`, `entryDatePeriod`, `minApprovedTime`, `maxApprovedTime`, `approvedTimePeriod`, `minDueDate`, `maxDueDate`, `isPaid`, `currencyId`, `recurringInvoiceId`, `amount`, `quoteId`, `q`; sort is limited to the official invoice enum. |
| Bills | `api_bills_get`, `api_bills_list` | `organizationId`, `contactId`, `creditedBillId`, `minEntryDate`, `maxEntryDate`, `minDueDate`, `maxDueDate`, `isPaid`, `hasAttachments`, `isBare`, `state`, `currencyId`, `suppliersInvoiceNo`, `amount`, `q`; sort is limited to the official bill enum. |
| Daybook transactions | `api_daybook_transactions_get`, `api_daybook_transactions_list` | `organizationId`, `daybookId`, `apiType`, `state`, `minEntryDate`, `maxEntryDate`, `q`; sort is limited to `priority`, `entryDate`, and `createdTime`. |

Period values remain opaque documented strings. Invoices alone permit the
invoice period filters; bills must not inherit them. `quoteId` and
`recurringInvoiceId` are invoice-list filters only and do not prove separate API
resources or UI parity.

## Offline integration evidence

The root server registers the six tools in this contract. Each has a focused
contract suite and a root registry assertion, and the coverage generator records
only `implemented: true` and `contract_tested: true` for the matching API rows.
The evidence remains intentionally incomplete: every `live_tested` field is
false, all interface/vision rows are red, and generated `complete` remains
false.

The bill and invoice `q` parameters are non-empty free-text search strings; the
documented field lists describe what Billy searches, not an enum of permitted
query text. Date/time and period filters retain their documented wire strings
until a dedicated non-production observation verifies stricter parsing.

## Exclusions

This wave excludes every write, preview/execute flow, bulk operation, invoice
email or delivery special, invoice logs, file upload, parent daybooks,
contact-persons, browser authentication, UI workflows, and any live or vision
coverage transition.
