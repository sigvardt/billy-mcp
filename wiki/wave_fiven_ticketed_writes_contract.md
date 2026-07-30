---
name: wave_fiven_ticketed_writes_contract
title: Wave-5n invoice-late-fee ticketed writes contract
desc: Cited offline contract that freezes only singular invoiceLateFees create and update ticketed writes; delete and bulk operations are excluded.
tags: [billy, api, invoice-late-fees, writes, ticketed, coverage]
sources:
  - https://www.billy.dk/api/
  - .fractal/main.billy_complete/tmp/grok-research.md
  - wiki/wave_fivem_product_independent_review.md
  - wiki/offline_write_probe_rules.md
  - coverage/api_v2_manifest.yaml
  - coverage/status.json
created: 2026-07-30T08:48:22Z
updated: 2026-07-30T08:48:22Z
---

# Wave-5n invoice-late-fee ticketed writes contract

## Scope and authority

This offline contract freezes exactly the two singular `invoiceLateFees` writes:
create and update. Its prerequisite is the accepted Wave-5m product review on
root, [[wave_fivem_product_independent_review]]. It authorises no product
implementation, tests, tool registration, inventory/status change, or coverage
greening.

Research60 accessed the official API documentation with ETag
`juf598rs793603`, MD5 `f3925615c452b34694abb7f2856e845a`, and a 147934-byte
body. Its stripped plain contract matches the earlier inventory lock (ETag
`hsisik4g9p3603`, MD5 `c2efda0ee4cf9cf200e14910c5fc6996`); the fingerprint
change is access metadata, not a new contract. The locked client base is
`https://api.billysbilling.com/v2`; paths in this page are client-relative and
therefore omit `/v2`.

The research60 root baseline is 250 `api_*` tools, 172 implemented and
contract-tested offline rows, zero live-tested rows, zero vision-verified rows,
and `complete: false`. These are preserved baseline facts, not a claim of
overall completion or a change to any coverage row.

A separate independent **Grok** freeze review must ACCEPT this page before any
product child can start.

## Exact frozen surface

| Inventory id | Preview tool | Execute tool | Method and client path | Singular request root | Required success root |
| --- | --- | --- | --- | --- | --- |
| `api.invoiceLateFees.create` | `api_invoice_late_fees_create_preview` | `api_invoice_late_fees_create_execute` | `POST /invoiceLateFees` | `invoiceLateFee` | `invoiceLateFees` |
| `api.invoiceLateFees.update` | `api_invoice_late_fees_update_preview` | `api_invoice_late_fees_update_execute` | `PUT /invoiceLateFees/:id` | `invoiceLateFee` | `invoiceLateFees` |

Each row is one Billy operation. The inventory tool name is the future preview
tool; its execute twin is introduced later without creating an additional
inventory row. This page freezes neither another operation nor another tool.

## Shared ticketed-write protocol

- Preview input is a strict outer object. Create accepts exactly
  `{invoiceLateFee: map}`. Update accepts exactly `{id: non-empty string,
  invoiceLateFee: map}`. Undeclared outer fields are forbidden.
- The inner `invoiceLateFee` map is opaque. This contract does not define a
  payload schema, relation wire form, `*Id` alias, date encoding, number
  encoding, or accepted update semantics.
- On update, an inner `invoiceLateFee.id` is optional; if present, it must
  equal the route `id`.
- Preview is non-mutating and prepares a short-lived, single-use confirmation
  ticket for its exact operation and executor. The future root uses one shared
  `ConfirmationStore` and one shared `WriteProtocolService`.
- Execute accepts exactly `{confirmation_ticket: non-empty string}`. It is
  ticket-only: no approval boolean, replacement business fields, or second
  preview input is accepted.
- Execute issues one write request and never retries a prepared write.

Only the required `invoiceLateFees` response root may be mapped. No additional
response root, record, or metadata mapping is frozen or fabricated.

## Official field boundaries

The property table constrains a future opaque inner map; it does not create a
request schema.

| Property | Official boundary | Contract treatment |
| --- | --- | --- |
| `invoice` | immutable, required | Preserve only as an opaque map value; do not define a relation wire form. |
| `entryDate` | immutable, required | Preserve only as an opaque map value; do not define a date encoding. |
| `flatFee` | immutable, required | Preserve only as an opaque map value; do not define a number encoding. |
| `percentageFee` | immutable, required | Preserve only as an opaque map value; do not define a number encoding. |
| `createdTime` | readonly | Do not expose it as a mutable outer field. |
| `amount` | readonly | Do not require or expose it as a mutable outer field. |
| `isVoided` | unproven update candidate | Do not promise accepted update semantics, unvoid behaviour, irreversibility, or cleanup. |

No official `invoiceLateFee` create payload sample establishes a more specific
inner-map contract.

## Method gates, delete, and bulk boundaries

The unauthenticated probes returned 401 `AUTHENTICATION_REQUIRED` for
`POST /invoiceLateFees` and `PUT /invoiceLateFees/nonexistent-probe-id`.
Those auth gates permit this offline create/update freeze only; they do not
prove an accepted payload, mutation result, response extension, or cleanup.

The unauthenticated singular DELETE probe returned 405
`METHOD_NOT_ALLOWED`; official Supports omits singular delete. The probed bulk
DELETE (`DELETE /invoiceLateFees?ids[]=nonexistent`) also returned 405. Singular
delete is excluded: no delete preview or execute tool is authorised.

Both bulk inventory rows remain empty-tool red:

| Inventory id | Status | Frozen action |
| --- | --- | --- |
| `api.invoiceLateFees.bulk_save` | `ambiguous_bulk`, empty tool name | Excluded; no request/response body contract is established. |
| `api.invoiceLateFees.bulk_delete` | `ambiguous_bulk`, empty tool name; DELETE probe 405 | Excluded; Supports does not authorise an offline bulk tool. |

No webhook is documented for this surface.

## Product gate and exclusions

Only after the required independent Grok freeze review ACCEPTs this page may a
separate product child implement and test the four frozen tools. That later
work must retain strict outer-input rejection, opaque inner-map preservation,
update-id equality, ticket-only execute input, the shared services,
required-root-only mapping, and one write with no retry.

This freeze excludes singular delete, both bulk operations, cleanup strategies,
relation wire forms, payload schemas, date and number encodings, accepted
update semantics, additional response roots, webhooks, generic HTTP or browser
controls, credentials, product implementation or registration, coverage
greening, and live, UI, or vision qualification.
