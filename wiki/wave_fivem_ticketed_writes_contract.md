---
name: wave_fivem_ticketed_writes_contract
title: Wave-5m contact-balance-payment ticketed writes contract
desc: Cited offline-only contract for singular Billy contactBalancePayments create and update ticketed writes; independent Grok freeze review ACCEPT recorded, with singular delete excluded on documented 405.
tags: [billy, api, contact-balance-payments, writes, ticketed, coverage]
sources:
  - https://www.billy.dk/api/
  - wiki/offline_write_probe_rules.md
  - coverage/api_v2_manifest.yaml
  - coverage/status.json
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
created: 2026-07-30T07:25:12Z
updated: 2026-07-30T07:25:12Z
---

# Wave-5m contact-balance-payment ticketed writes contract

## Scope and authority

This offline contract freezes only the two clear singular write operations for
`/v2/contactBalancePayments`: create and update. It authorises neither product
implementation nor coverage changes. The separate independent Grok freeze
review has ACCEPTed this page; a future product leaf remains separately
responsible for real implementation and row-level tests.

The primary official source is https://www.billy.dk/api/, cited with ETag
`hsisik4g9p3603`, MD5 `c2efda0ee4cf9cf200e14910c5fc6996`, and a
147934-byte body. API traffic remains locked to
`https://api.billysbilling.com/v2`; paths below are client-relative and do not
repeat `/v2`.

The existing read tools are `api_contact_balance_payments_get` and
`api_contact_balance_payments_list`. The create and update inventory rows
remain discovered but unimplemented, untested, and not live-tested. This page
does not change those rows or make a completeness claim.

## Exact frozen surface

| Inventory id | Preview tool | Execute tool | Method and client path | Singular request root | Required success root |
| --- | --- | --- | --- | --- | --- |
| `api.contactBalancePayments.create` | `api_contact_balance_payments_create_preview` | `api_contact_balance_payments_create_execute` | `POST /contactBalancePayments` | `contactBalancePayment` | `contactBalancePayments` |
| `api.contactBalancePayments.update` | `api_contact_balance_payments_update_preview` | `api_contact_balance_payments_update_execute` | `PUT /contactBalancePayments/:id` | `contactBalancePayment` | `contactBalancePayments` |

Each inventory row denotes one Billy operation. Its registered future
`tool_name` is the preview tool; the execute twin is registered later without
adding another inventory row. No tool registration is authorised by this page.

## Shared ticketed-write protocol

- Preview inputs are strict outer objects only. Create accepts exactly
  `{contactBalancePayment: map}` and update accepts exactly
  `{id: non-empty string, contactBalancePayment: map}`; undeclared outer fields
  are forbidden.
- The inner `contactBalancePayment` map is opaque. This contract does not
  invent a map schema, `*Id` aliases, relation wire forms, date or amount
  encodings, enum members, or update semantics beyond the stated boundaries.
- If an inner `contactBalancePayment.id` is present on update, it must equal the
  route `id`. The inner id is otherwise optional.
- Preview is non-mutating. It uses the shared short-lived, single-use,
  exact-operation confirmation protocol. Execute accepts exactly
  `{confirmation_ticket: non-empty string}`; it accepts no approval boolean,
  replacement business fields, or second preview input.
- The future implementation uses the shared `ConfirmationStore` and
  `WriteProtocolService`; a ticket is bound to its exact operation and executor
  before it can issue the write. An executor-binding mismatch fails closed with
  `CONFIRMATION_MISMATCH` before ticket consumption and before HTTP.
- Execute issues exactly one write request. Prepared writes are discarded and
  never retried.

The required response root is `contactBalancePayments`. Related response roots
may be mapped only when Billy actually supplies them; this contract permits no
fabricated record, metadata, or response mapping.

## Contact-balance-payment field boundaries

The official property boundaries constrain a future implementation without
turning the opaque inner map into an invented request schema.

| Property | Official boundary | Offline treatment |
| --- | --- | --- |
| `organization` | immutable, required | Preserve only as an opaque map value; do not expose a relation wire form. |
| `entryDate` | immutable, required | Preserve only as an opaque map value; do not invent a date encoding. |
| `amount` | immutable, required | Preserve only as an opaque map value; do not invent an amount encoding. |
| `associations` | immutable, required | Preserve only as an opaque map value; do not promise a relation wire form or update behavior. |
| `contact` | auto-set | Do not require or expose an outer contact field. |
| `currency` | auto-set | Do not require or expose an outer currency field. |
| `side` | auto-set debit/credit | Do not require or expose an outer side field or add enum aliases. |
| `createdTime` | readonly | Do not expose it as a mutable outer field. |
| `isVoided` | documented mutable update candidate | Do not promise unvoid semantics, irreversibility, cleanup, or live behavior. |

The official `bankPayment` sample belongs to a different resource and must not
be copied into this contract or a later contact-balance-payment implementation.

## Method gates, delete, and bulk boundaries

The official Supports list includes get, list, create, update, bulk save, and
bulk delete; it does not include singular delete. The cited unauthenticated
probes returned 401 `AUTHENTICATION_REQUIRED` for `POST /contactBalancePayments`
and `PUT /contactBalancePayments/nonexistent-probe-id`. Those auth gates allow
this offline freeze but do not prove an accepted payload, mutation result,
cleanup method, or live behaviour.

The cited singular DELETE probe returned 405 `METHOD_NOT_ALLOWED` with the
documented single-record-delete refusal. That refusal controls this contract:
there is no singular-delete inventory row and no delete preview or execute tool
is authorised.

`api.contactBalancePayments.bulk_save` and
`api.contactBalancePayments.bulk_delete` remain `ambiguous_bulk` with empty
tool names. Supports flags provide no bulk method/body contract, response body,
partial-failure behaviour, limits, or cleanup strategy, so this page authorises
no bulk tool.

## Coverage context and future product gate

The post-Wave-5l root context is 246 `api_*` tools and 170 implemented plus
contract-tested API rows. Those counts are context only: Wave-5m create and
update stay red, live/UI/vision qualification remains absent, and
`coverage/status.json` remains `complete: false`.

Only after a separate independent Grok freeze review ACCEPTs this contract may
a product leaf implement and test the four frozen tools. That later work must
prove strict outer-input rejection, opaque inner-map preservation, exact method
and client-relative path, singular-root request construction, update id
equality, ticket binding and single-use rejection, required-root handling
without response fabrication, and one write without retry. It must not infer
cleanup from create/update or a deletion path that Billy refuses.

## Exclusions

This freeze authorises neither singular delete nor bulk save/delete. No webhooks
are documented. It also excludes generic HTTP or browser controls; product
registration or implementation; coverage/status changes or greening; live,
browser/UI, or vision qualification; credentials; persistent organisation data;
cleanup strategies; and any overall completeness claim.

Invoice-late-fee, invoice-reminder, contact-balance-posting, and
invoice-reminder-association product work are out of scope. The cited probes
block contactBalancePostings and invoiceReminderAssociations create/update with
405, so this page cannot be used to authorise those surfaces.
