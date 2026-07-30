---
name: wave_fivel_ticketed_writes_contract
title: Wave-5l sales-tax-payment ticketed writes contract
desc: Cited offline-only contract for singular Billy salesTaxPayments create and update ticketed writes; independent Grok freeze review ACCEPT recorded; singular delete is excluded on documented 405.
tags: [billy, api, sales-tax, payments, writes, coverage]
sources:
  - https://www.billy.dk/api/
  - .fractal/main.billy_complete/tmp/grok-research.md
  - wiki/wave_fivek_product_independent_review.md
  - wiki/wave_fivel_freeze_independent_review.md
  - wiki/offline_write_probe_rules.md
  - coverage/api_v2_manifest.yaml
  - coverage/status.json
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
created: 2026-07-30T05:39:10Z
updated: 2026-07-30T05:44:00Z
---

# Wave-5l sales-tax-payment ticketed writes contract

## Scope and authority

This offline contract freezes only the two clear singular write operations for
`/v2/salesTaxPayments`: create and update. The prerequisite Wave-5k
bank-payment product is accepted at
`wiki/wave_fivek_product_independent_review.md`; the cited research54 package
then opens this freeze-page step only. Independent Grok freeze review ACCEPT is
recorded in `wiki/wave_fivel_freeze_independent_review.md`. Product leaf may
proceed under that gate. This page does not itself implement product tools,
live-qualify, or green any coverage row.

The primary official source is https://www.billy.dk/api/, re-fetched for the
research package with ETag `hsisik4g9p3603`, MD5
`c2efda0ee4cf9cf200e14910c5fc6996`, and a 147934-byte body. API traffic stays
on the locked base `https://api.billysbilling.com/v2`; paths below are
client-relative and therefore do not repeat `/v2`.

The maintained inventory already has green offline read tools for this resource
(`api_sales_tax_payments_get` and `api_sales_tax_payments_list`). Its create and
update rows remain discovered but unimplemented, untested, and not live-tested
until a separate product leaf implements and tests the four tools below.

## Exact frozen surface

| Inventory id | Preview tool | Execute tool | Method and client path | Singular request root | Required success root |
| --- | --- | --- | --- | --- | --- |
| `api.salesTaxPayments.create` | `api_sales_tax_payments_create_preview` | `api_sales_tax_payments_create_execute` | `POST /salesTaxPayments` | `salesTaxPayment` | `salesTaxPayments` |
| `api.salesTaxPayments.update` | `api_sales_tax_payments_update_preview` | `api_sales_tax_payments_update_execute` | `PUT /salesTaxPayments/:id` | `salesTaxPayment` | `salesTaxPayments` |

Each inventory row denotes one Billy operation; its `tool_name` is the preview
tool and the execute twin is registered later without adding an inventory row.
This page changes neither tool registration nor coverage state.

## Shared ticketed-write protocol

- Preview inputs are strict typed outer objects. Create accepts exactly
  `{salesTaxPayment: map}` and update accepts exactly `{id: non-empty string,
  salesTaxPayment: map}`; undeclared outer fields are forbidden.
- The inner `salesTaxPayment` map is opaque. The official page publishes no
  sales-tax-payment create sample, so this contract does not invent relation
  wire forms, `*Id` aliases, amount formats, date encodings, or enum members.
- Update is a partial `PUT`. If an inner `salesTaxPayment.id` appears, it must
  equal the route `id`; the inner id is otherwise optional.
- Preview is non-mutating and returns a short-lived, exact, single-use
  confirmation ticket bound to the exact server executor, organisation, target,
  canonical request, and expected effect. Execute accepts exactly
  `{confirmation_ticket: non-empty string}`: no boolean approval, replacement
  business fields, or second preview input is allowed.
- The root retains one shared `ConfirmationStore` and one shared
  `WriteProtocolService`. Each eventual `WriteOperationSpec` uses the exact,
  non-empty executor name from the table; an executor-binding mismatch fails
  with `CONFIRMATION_MISMATCH` before ticket consumption and before HTTP.
- Execute issues exactly one write request. Prepared writes are discarded and
  never retried.

The required success root is `salesTaxPayments`. Related plural roots are
mapped only when the Billy response actually contains them; this contract fixes
no related-root set and permits no fabricated record or metadata.

## Sales-tax-payment field boundaries

The official property table constrains a future implementation without turning
the opaque inner map into an invented request schema.

| Property | Official boundary | Offline treatment |
| --- | --- | --- |
| `salesTaxReturn` | belongs-to, immutable, required | Preserve only as an opaque create-map value; do not promise update support or a relation wire form. |
| `entryDate` | date, immutable, required | Preserve only as an opaque create-map value; do not invent a date encoding. |
| `account` | belongs-to, immutable, required | Preserve only as an opaque create-map value; do not promise update support or a relation wire form. |
| `amount` | float, readonly | Do not require or expose as a mutable outer request field. |
| `side` | enum, readonly; no members published for this resource | Do not require or expose as a mutable outer enum. |
| `isVoided` | boolean present; no long cancel narrative published | Treat only as the documented mutable update candidate. Do not promise unvoid, irreversibility, cleanup, or live semantics. |

## Delete and bulk boundaries

The official Supports list includes get, list, create, update, bulk save, and
bulk delete; it does not list singular delete. The cited unauthenticated probe
of `DELETE /salesTaxPayments/nonexistent-probe-id` returned 405
`METHOD_NOT_ALLOWED` with `Resource at \`salesTaxPayments\` does not support
deleting a single record.` That explicit refusal controls this offline contract:
there is no singular-delete inventory row and no delete preview or execute tool
is authorised.

The `api.salesTaxPayments.bulk_save` and `.bulk_delete` rows remain
`ambiguous_bulk` with empty tool names. The Supports flags do not provide a
bulk request body, response body, partial-failure behavior, or limits; this
contract authorises no bulk tools. The unauthenticated POST and PUT 401 results
open an offline freeze but do not prove an accepted payload, mutation result,
or cleanup behavior.

## Later product evidence and coverage limit

The current root has 242 `api_*` tools and 168 implemented plus
contract-tested offline API rows; live and vision counts are zero and
`coverage/status.json` remains `complete: false`. This page itself changes none
of those figures.

Only after an independent freeze review accepts this page may a separate
product leaf add `src/billy_mcp/api/sales_tax_payment_writes.py`, its focused
tests, and server registration. That later work may target 246 tools and 170
implemented plus contract-tested offline rows only after real implementation
and passing tests. It must prove strict outer-input rejection, opaque inner-map
preservation, exact method and client-relative path, singular-root request
construction, partial-update id equality, all ticket binding rejections,
required-root mapping without response fabrication, and one write without
retry.

Live qualification, cleanup through `isVoided`, UI parity, vision, and related
response-root behavior require later dedicated non-production evidence. The
inventory's create cleanup text must not be read as an authorisation to delete:
singular delete is unavailable and cleanup remains unproven.

## Exclusions

This freeze authorises neither singular delete nor bulk save/delete. It also
excludes product registration or implementation; webhooks; generic HTTP,
browser, or cleanup controls; live qualification; browser/UI parity; vision
verification; credentials; persistent organisation data; contact-balance
payments, invoice-late-fee, and invoice-reminder work; and any overall
completeness claim.
