---
name: wave_fivee_ticketed_writes_contract
title: Wave-5e bill ticketed-write contract
desc: Cited offline contract for Billy bill and bill-line singular ticketed writes.
tags: [billy, api, bills, writes, contract]
sources:
  - https://www.billy.dk/api/
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
  - wiki/wave_fived_ticketed_writes_contract.md
  - wiki/wave_fived_product_independent_review.md
  - coverage/api_v2_manifest.yaml
created: 2026-07-29T19:35:00Z
updated: 2026-07-29T19:35:00Z
---

# Wave-5e bill ticketed-write contract

## Authority and gate

This is the frozen, offline-only implementation contract for the six documented
singular Billy API v2 CUD rows for `bills` and `billLines`. It is derived from
the cited official API page, re-fetched by Grok with ETag `hsisik4g9p3603`, MD5
`c2efda0ee4cf9cf200e14910c5fc6996`, and unchanged 147934-byte body. The full
cited research brief is retained outside the public repository at
`.fractal/main.billy_complete/tmp/grok-research.md`.

Wave-5d has independent Grok offline acceptance in
[[wave_fived_product_independent_review]], so this contract authorises a
Wave-5e independent freeze review. It does not authorise product implementation
until that review accepts this exact contract. It never authorises live, UI,
vision, bulk, special-route, or overall-completeness claims.

## Exact inventory and tool surface

| Inventory id | Preview tool | Execute tool | HTTP request | Request root | Response roots |
| --- | --- | --- | --- | --- | --- |
| `api.bills.create` | `api_bills_create_preview` | `api_bills_create_execute` | `POST /bills` | `bill` | `bills` |
| `api.bills.update` | `api_bills_update_preview` | `api_bills_update_execute` | `PUT /bills/:id` | `bill` | `bills` |
| `api.bills.delete` | `api_bills_delete_preview` | `api_bills_delete_execute` | `DELETE /bills/:id` | id binding only | `bills`, optional deleted metadata |
| `api.billLines.create` | `api_bill_lines_create_preview` | `api_bill_lines_create_execute` | `POST /billLines` | `billLine` | `billLines`, optional `bills` |
| `api.billLines.update` | `api_bill_lines_update_preview` | `api_bill_lines_update_execute` | `PUT /billLines/:id` | `billLine` | `billLines`, optional `bills` |
| `api.billLines.delete` | `api_bill_lines_delete_preview` | `api_bill_lines_delete_execute` | `DELETE /billLines/:id` | id binding only | `billLines`, optional `bills` and deleted metadata |

The `api.billLines.update` preview tool is
`api_bill_lines_update_preview`. Each inventory row remains one API operation:
its `tool_name` is the preview tool, while the execute twin is registered but
is not a second coverage row.

## Shared write protocol

- Requests use only the locked API base `https://api.billysbilling.com/v2` and
  the client-relative paths shown above; no `/v2` path prefix is repeated.
- Create and update requests contain exactly one singular root. Updates are
  `PUT`, support partial fields, and require any body `id` to equal the route
  id. Deletes have no body and bind canonical request `{"id": "…"}`.
- Use the root's one `ConfirmationStore` and `WriteProtocolService`; do not
  construct a leaf-local store or retry a write request.
- Every `WriteOperationSpec` has the exact server-owned non-empty
  `execute_tool_name`, and every executor passes that name back to the shared
  service. Mismatch fails as `CONFIRMATION_MISMATCH` before ticket consumption
  and before HTTP.
- Each preview is non-mutating and returns a short-lived, single-use ticket
  bound to the exact tool, organisation, target, canonical request, and
  expected effect. Execute accepts only `confirmation_ticket`.
- Outer Pydantic inputs forbid extra fields; inner `bill` and `billLine`
  objects remain opaque to preserve the documented API field surface for later
  live qualification.

## Bill and bill-line boundaries

Billy documents bills with immutable required `organization` and `contact`, a
required immutable `paymentDate`, required `entryDate`, state default `draft`,
optional `lines`, attachments, and readonly financial values. Callers use the
documented `…Id` JSON field convention for belongs-to relationships, such as
`organizationId`, `contactId`, `paymentAccountId`, `currencyId`, and
`creditedBillId`. The bill payload remains opaque offline.

The bill `lines` property is has-many, but unlike invoice lines it has no
documented required, minimum-one-line, replace-on-set, or create-only rule. Do
not infer invoice embedded-line lifecycle rules for bills. The documented bill
`state` filter has `draft`, `approved`, and `voided`, but the page gives no
invoice-style irreversible-transition rule; do not infer one offline.

Bill lines use `billId`, `accountId`, `taxRateId`, `description`, and `amount`.
They do not use invoice-line `productId` or `unitPrice` fields. Line operation
specifications must set `additional_plural_roots=("bills",)`: a write may
return the changed parent bill, but its absence is valid and must not be
fabricated. Bill-parent writes use no additional response root until live
evidence establishes one.

The page's attachment-link example permits an opaque bill payload to contain
`attachmentIds: [{"id": "…"}]`. This does not authorise file upload or
attachment CUD; binary file upload remains a separate path/digest-bound special
operation.

## Required offline evidence

Each resource suite must prove strict flat typed inputs, preview non-mutation,
exact HTTP method/path/body, bodyless deletes, update-id matching, typed
authentication and not-found failures, ticket tamper, expiry, replay, wrong
organisation/target/payload, same-module executor mismatch, and no extra write.
The bill-line suite must prove both present and absent optional `bills` response
roots. Root tests must prove both cross-resource executor-mismatch directions
and a post-wave registry count of 178 `api_*` tools.

Coverage generation may mark only these six API rows implemented and
contract-tested after the product and all required tests land. The expected
offline state is 136 implemented/contract-tested API rows, zero live rows, all
UI rows red, 92 ambiguous bulk rows red, unchanged special-route state, and
`complete: false`.

## Live evidence gaps and exclusions

Unauthenticated probes saw `POST` and `PUT` return 401 and missing-id `DELETE`
return empty 200 success on both collections. The latter is not cleanup or live
qualification evidence. Live non-production tests must resolve bill-line parent
responses, embedded bill-line semantics, bill payment-date requirements, bill
state transitions, bare bills, credit notes, and attachment-link behaviour.

This cohort excludes all bulk save/delete routes, file binary upload, attachment
CUD, invoice email/delivery/log specials, invoices and invoice lines,
transactions, postings, tax/bank/reference writes, browser/UI workflows, and
live qualification. The 92 ambiguous bulk rows remain empty-tool red. Postings
CUD remains outside the cohort: unauthenticated probes return 405 despite
documented Supports flags, so no write contract is inferred.
