---
name: wave_fivek_ticketed_writes_contract
title: Wave-5k bank-payment ticketed-write contract
desc: Cited offline-only contract for singular Billy bankPayments create and update ticketed writes, pending independent Grok freeze review.
tags: [billy, api, bank, payments, writes, coverage]
sources:
  - https://www.billy.dk/api/
  - wiki/wave_fivek_freeze_authoring_authority_research_independent_review.md
  - wiki/wave_fivek_freeze_ready_research_independent_review.md
  - wiki/wave_fivek_freeze_implementation_research_independent_review.md
  - wiki/wave_fivek_freeze_authoring_readiness_research_independent_review.md
  - wiki/wave_fivek_freeze_page_authoring_package_research_independent_review.md
  - wiki/offline_write_probe_rules.md
  - coverage/api_v2_manifest.yaml
  - coverage/status.json
  - wiki/wave_fivej_ticketed_writes_contract.md
created: 2026-07-30T04:00:25Z
updated: 2026-07-30T04:00:25Z
---

# Wave-5k bank-payment ticketed-write contract

## Authority and gate

This is the frozen **offline-only** implementation contract for the two clear
singular Billy API v2 operations `api.bankPayments.create` and
`api.bankPayments.update`. The authoring authority is the ACCEPT in
`wiki/wave_fivek_freeze_authoring_authority_research_independent_review.md`;
it expressly opens this page-authoring step and supersedes the earlier package
review's process-only authoring block.

The cited official documentation evidence is exactly ETag `hsisik4g9p3603`,
MD5 `c2efda0ee4cf9cf200e14910c5fc6996`, body 147934 bytes. The locked API base
is `https://api.billysbilling.com/v2`. This contract is not product
implementation, live qualification, browser/UI parity, vision verification,
bulk qualification, or a completeness claim. It requires an independent Grok
freeze review before any Wave-5k product leaf.

## Exact inventory and tool surface

| Inventory id | Preview tool | Execute tool | HTTP request | Request root | Required success root |
| --- | --- | --- | --- | --- | --- |
| `api.bankPayments.create` | `api_bank_payments_create_preview` | `api_bank_payments_create_execute` | `POST /bankPayments` | `bankPayment` | `bankPayments` |
| `api.bankPayments.update` | `api_bank_payments_update_preview` | `api_bank_payments_update_execute` | `PUT /bankPayments/:id` | `bankPayment` | `bankPayments` |

Each inventory row is one API operation: its `tool_name` is the preview tool;
the execute twin is a later server registration, not another coverage row. The
two rows remain `implemented: false`, `contract_tested: false`, and
`live_tested: false` until a later product leaf supplies real implementation
and tests. This page changes neither registration nor coverage.

## Shared ticketed-write protocol

- Client calls use only the locked base and the client-relative paths in the
  table. A client path must not repeat `/v2`.
- Preview inputs are strict typed outer objects. Create accepts exactly
  `{bankPayment: map}`; update accepts exactly `{id: non-empty string,
  bankPayment: map}`. Undeclared outer fields are forbidden. The inner
  `bankPayment` map remains opaque: this contract does not publish a wire schema
  for relations, amounts, dates, or undocumented enum values.
- The update is a partial `PUT`. If an inner `bankPayment.id` is supplied, it
  must equal the route `id`; it is not otherwise required by this contract.
- A preview is non-mutating and produces a short-lived, exact, single-use
  confirmation ticket bound to the server tool, organisation, target, canonical
  request, and expected effect. An execute input is exactly
  `{confirmation_ticket: non-empty string}`; it accepts no approval boolean
  and no replacement business fields.
- The root owns one shared `ConfirmationStore` and one shared
  `WriteProtocolService`. Every `WriteOperationSpec` carries the exact,
  non-empty, server-owned executor tool name from the table. An executor/tool
  binding mismatch fails with `CONFIRMATION_MISMATCH` before ticket consumption
  and before HTTP.
- Execution makes exactly one write request. Prepared writes are discarded; no
  write retry is allowed.

On a successful non-delete operation, `bankPayments` is the required plural
response root. Other plural roots may be returned only when they are actually
present in the service response; the contract promises no fixed related-root
set and permits no fabricated records or metadata.

## Bank-payment field boundaries

The official property documentation constrains a future implementation without
turning the opaque inner map into an invented wire schema.

| Property or group | Documentation boundary | Offline treatment |
| --- | --- | --- |
| `organization`, `contact`, `entryDate`, `cashAmount`, `cashSide`, `cashAccount`, `cashExchangeRate`, `subjectCurrency` | immutable | Preserve only as opaque inner-map values; do not promise update support. |
| `cashSide` | documents `debit` / `credit` | Keep the inner value opaque; do not add a new outer enum schema. |
| `feeAccount` | conditional on `feeAmount` | Preserve the documented dependency without inventing relation wire form or additional validation. |
| `createdTime`, `contactBalancePostings` | readonly | Do not require, write, or expose them as mutable request fields. |
| associations | immutable | Keep their names and wire forms opaque; do not promise association mutation. |
| `isVoided` | primary documented mutable void path: setting `true` cannot be reversed | Treat it as the documented void path only; it does not authorise cleanup, restoration, or a delete operation. |

## Delete and bulk boundaries

Singular bank-payment delete is explicitly excluded. An unauthenticated
`DELETE /bankPayments/:id` returned 405 `METHOD_NOT_ALLOWED` with
`Resource at bankPayments does not support deleting a single record.` This 405
overrides the Supports table for this offline contract. No delete preview or
execute tool is authorised, even though the inventory still records the delete
row; that row remains red.

The bank-payment bulk save and bulk delete rows remain `ambiguous_bulk` with no
tool. The documented Supports flags do not supply a bulk request body, response
body, or partial-failure contract, so this contract authorises no bulk tool.
The 401 POST/PUT probes and the 405 DELETE probe do not establish an accepted
payload, a live mutation result, authenticated deletion, or a live cleanup
claim.

## Later product evidence and coverage limit

The current root arithmetic is 238 `api_*` tools and 166 implemented,
contract-tested offline API rows. A later Wave-5k product may target 242 tools
and 168 offline rows only after real implementation and tests. This page alone
changes neither figure.

Before either frozen row can become implemented or contract-tested, the later
product must prove strict outer input rejection, opaque inner-map preservation,
the exact method and client-relative path, singular-root request construction,
partial-update id equality, ticket expiry/tamper/replay/organisation/target/
payload/expected-effect rejection, executor-binding rejection before ticket
consumption and HTTP, required-root mapping, response-root non-fabrication, and
one write without retry.

Delete, bulk, live qualification, UI parity, vision, and all associated
coverage rows remain red. `coverage/status.json` remains `complete: false`.

## Exclusions

This freeze authorises neither singular delete nor bulk save/delete. It also
excludes product registration or implementation; webhooks; generic HTTP,
browser, or cleanup controls; live qualification; browser/UI parity; vision
verification; credentials; persistent organisation data; and any overall
completeness claim.
