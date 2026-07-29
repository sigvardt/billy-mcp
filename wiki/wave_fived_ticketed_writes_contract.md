---
name: wave_fived_ticketed_writes_contract
title: Wave-5d invoice ticketed-write contract
desc: Cited offline contract for Billy invoice and invoice-line singular ticketed writes.
tags: [billy, api, invoices, writes, contract]
sources:
  - https://www.billy.dk/api/
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
  - wiki/wave_fivec_ticketed_writes_contract.md
  - wiki/wave_fivec_product_independent_review.md
  - coverage/api_v2_manifest.yaml
created: 2026-07-29T18:50:00Z
updated: 2026-07-29T18:50:00Z
---

# Wave-5d invoice ticketed-write contract

## Authority and gate

This is the frozen, offline-only implementation contract for the six
documented singular Billy API v2 CUD rows for `invoices` and `invoiceLines`.
It is derived from the cited official API page, re-fetched by Grok with ETag
`hsisik4g9p3603`, MD5 `c2efda0ee4cf9cf200e14910c5fc6996`, and unchanged
147934-byte body. The full cited research brief is retained outside the public
repository at `.fractal/main.billy_complete/tmp/grok-research.md`.

Wave-5c's ticketed-write product has independent Grok offline acceptance in
[[wave_fivec_product_independent_review]], so this contract authorises the
Wave-5d offline product implementation. It never authorises live, UI, vision,
bulk, special-route, or overall-completeness claims.

## Exact inventory and tool surface

| Inventory id | Preview tool | Execute tool | HTTP request | Request root | Response roots |
| --- | --- | --- | --- | --- | --- |
| `api.invoices.create` | `api_invoices_create_preview` | `api_invoices_create_execute` | `POST /invoices` | `invoice` | `invoices` |
| `api.invoices.update` | `api_invoices_update_preview` | `api_invoices_update_execute` | `PUT /invoices/:id` | `invoice` | `invoices` |
| `api.invoices.delete` | `api_invoices_delete_preview` | `api_invoices_delete_execute` | `DELETE /invoices/:id` | id binding only | `invoices`, optional deleted metadata |
| `api.invoiceLines.create` | `api_invoice_lines_create_preview` | `api_invoice_lines_create_execute` | `POST /invoiceLines` | `invoiceLine` | `invoiceLines`, optional `invoices` |
| `api.invoiceLines.update` | `api_invoice_lines_update_preview` | `api_invoice_lines_update_execute` | `PUT /invoiceLines/:id` | `invoiceLine` | `invoiceLines`, optional `invoices` |
| `api.invoiceLines.delete` | `api_invoice_lines_delete_preview` | `api_invoice_lines_delete_execute` | `DELETE /invoiceLines/:id` | id binding only | `invoiceLines`, optional `invoices` and deleted metadata |

Each inventory row remains one API operation: its `tool_name` is the preview
tool, while the execute twin is registered but not a second coverage row.

## Shared write protocol

- Requests use only the locked API base `https://api.billysbilling.com/v2` and
  client-relative paths shown above; no `/v2` path prefix is repeated.
- Create and update requests contain exactly one singular root. Updates are
  `PUT`, support partial fields, and require any body `id` to equal the route
  id. Deletes have no body and bind canonical request `{"id": "…"}`.
- Use the root's one `ConfirmationStore` and `WriteProtocolService`; do not
  construct a leaf-local store or retry a write request.
- Every `WriteOperationSpec` has the exact server-owned non-empty
  `execute_tool_name`, and every executor passes that name back to the shared
  service. Mismatch fails as `CONFIRMATION_MISMATCH` before ticket consume and
  before HTTP.
- Each preview is non-mutating and returns a short-lived, single-use ticket
  bound to the exact tool, organisation, target, canonical request, and
  expected effect. Execute accepts only `confirmation_ticket`.
- Outer Pydantic inputs forbid extra fields; inner `invoice` and `invoiceLine`
  objects stay opaque to preserve the documented API field surface for later
  live qualification.

## Invoice-specific boundaries

The official page describes invoice embedded `lines` as atomic, create-only,
and requiring at least one line. The offline tool therefore preserves a caller
payload as an opaque `invoice` root rather than inventing schema validation or
a separate embedded-write protocol. Invoice state transition from draft to
approved is irreversible in the documented contract and remains out of live
qualification until a safe disposable cleanup path is evidenced.

Invoice-line specifications must set
`additional_plural_roots=("invoices",)`. A line-write response may return the
modified parent invoice as well as the primary line root. The parent root is
optional for mapping, but when present it belongs in
`changed_records["invoices"]`; code and fixtures must not fabricate it when
absent. Invoice parent writes use no additional response root until live
evidence supports embedded-return behaviour.

## Required offline evidence

Focused tests for each resource prove strict typed inputs, preview
non-mutation, exact HTTP method/path/body, bodyless deletes, ticket tamper,
expiry, replay, wrong organisation/target/payload, same-module executor
mismatch, typed authentication/not-found failures, and no extra write. Root
tests prove both cross-resource executor-mismatch directions and the post-wave
registry count of 166 `api_*` tools.

Coverage generation may mark only these six API rows implemented and
contract-tested after the product and all required tests land. The expected
offline state then is 130 implemented/contract-tested API rows, zero live rows,
all UI rows red, 92 ambiguous bulk rows red, and `complete: false`.

## Exclusions

This cohort excludes bill and bill-line writes, all bulk save/delete routes,
invoice email/delivery/log specials, file upload and attachments,
reminder/late-fee routes, browser/UI workflows, and live qualification.
Unauthenticated delete success is not cleanup evidence. No operation outside
the six rows is made green by this contract.
