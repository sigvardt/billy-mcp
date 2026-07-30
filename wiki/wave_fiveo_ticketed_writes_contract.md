---
name: wave_fiveo_ticketed_writes_contract
title: Wave-5o invoice-reminder ticketed writes contract
desc: Cited wiki-only contract freezing singular invoiceReminders create; update, delete, bulk, and association writes remain excluded.
tags: [billy, api, invoice-reminders, writes, ticketed, coverage]
sources:
  - https://www.billy.dk/api/
  - https://api.billysbilling.com/v2
  - .fractal/main.billy_complete/tmp/grok-research.md
  - wiki/wave_fiveo_freeze_ready_research_independent_review.md
  - wiki/wave_fiven_product_independent_review.md
  - wiki/wave_fiven_ticketed_writes_contract.md
  - wiki/offline_write_probe_rules.md
  - coverage/api_v2_manifest.yaml
  - coverage/status.json
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
created: 2026-07-30T10:26:00Z
updated: 2026-07-30T10:26:00Z
---

# Wave-5o invoice-reminder ticketed writes contract

## Scope and authority

This wiki-only offline contract freezes exactly one future Billy API operation:
singular `invoiceReminders` create. It authorises no product source, tests,
server registration, inventory/status change, or coverage greening.

Its prerequisite is the authoritative offline Wave-5n product ACCEPT recorded
in [[wave_fiven_product_independent_review]]. The earlier
[[wave_fiveo_freeze_ready_research_independent_review]] is ACCEPT as research
only. Research64 at `.fractal/main.billy_complete/tmp/grok-research.md` packages
this freeze-authoring evidence; neither research record is a Wave-5o freeze or
product acceptance.

Research64 accessed the [official API documentation](https://www.billy.dk/api/)
with ETag `wcw4x9hqvu3603`, MD5
`8b94b0135c91fd15fe54ea33e088a4be`, and a 147934-byte body. The older
inventory lock records ETag `hsisik4g9p3603` and MD5
`c2efda0ee4cf9cf200e14910c5fc6996`; this is access/CDN metadata drift only, not
a change to the reminder Supports or property contract. The locked API base is
`https://api.billysbilling.com/v2`. Paths below are client-relative and
therefore omit `/v2`.

The present root baseline is 254 `api_*` tools, 174 implemented and
contract-tested rows, zero live-tested rows, zero vision-verified rows, 92
ambiguous bulk rows, and `complete: false`. These are honesty constraints, not
completeness or qualification claims.

A separate independent **Grok** freeze review must ACCEPT this page before any
product child starts.

## Exact frozen surface

| Inventory id | Preview tool | Execute tool | Method and client path | Singular request root | Required success root |
| --- | --- | --- | --- | --- | --- |
| `api.invoiceReminders.create` | `api_invoice_reminders_create_preview` | `api_invoice_reminders_create_execute` | `POST /invoiceReminders` | `invoiceReminder` | `invoiceReminders` |

This row is one Billy operation. Its inventory tool name is the future preview
tool; the execute twin does not create another inventory row. No other
operation or tool is frozen.

## Shared ticketed-write protocol

- Preview accepts exactly `{invoiceReminder: map}` as a strict outer object.
  Undeclared outer fields are forbidden.
- The inner `invoiceReminder` map is opaque. This contract defines no
  relation wire form, `*Id` alias, date or number encoding, email side effect,
  association schema, or more-specific payload schema.
- Preview is non-mutating. It prepares a short-lived, single-use confirmation
  ticket bound to the exact executor, Billy organisation, target, canonical
  request, and expected effect.
- The future root must use one shared `ConfirmationStore` and one shared
  `WriteProtocolService`.
- Execute accepts exactly `{confirmation_ticket: non-empty string}`. It
  accepts no boolean approval, replacement business payload, or second preview
  input.
- Execute restores the bound request, validates the ticket and organisation,
  makes exactly one write, consumes the ticket, and never retries a prepared
  write.

Future response mapping takes only the required `invoiceReminders` root. No
additional response root, response extra, record, or metadata mapping is
frozen.

## Official field boundaries

The official property table constrains the future opaque inner map; it does not
define a request schema.

| Property | Official boundary | Contract treatment |
| --- | --- | --- |
| `organization` | belongs-to; immutable, required | Required opaque value only; do not define a relation wire form. |
| `contact` | belongs-to; required | Required opaque value only; do not define a relation wire form. |
| `createdTime` | datetime; readonly | Do not require or expose it as a mutable outer field. |
| `associations` | has-many; notes empty | Preserve only as an opaque supplied value; define no association schema or replace-on-set behaviour. |
| `flatFee` | float; notes empty | Preserve only as an opaque supplied value; define no number encoding or other semantics. |
| `percentageFee` | float; notes empty | Preserve only as an opaque supplied value; define no number encoding or other semantics. |
| `feeCurrency` | belongs-to; required | Required opaque value only; do not define a relation wire form. |
| `sendEmail` | boolean; notes empty | Preserve only as an opaque supplied value; promise no email-send side effect or other semantics. |
| `contactPerson` | belongs-to; required | Required opaque value only; do not define a relation wire form. |
| `emailSubject` | string; required | Required opaque value only; define no additional string semantics. |
| `emailBody` | string; required | Required opaque value only; define no additional string semantics. |
| `copyToUser` | belongs-to; notes empty | Preserve only as an opaque supplied value; do not define a relation wire form or other semantics. |
| `downloadUrl` | string; notes empty | Treat as unproven; do not require it on create or invent download semantics. |

No official create sample establishes a more specific `invoiceReminder` inner
map.

## Method gates, delete, and bulk boundaries

Under [[offline_write_probe_rules]], the unauthenticated
`POST /invoiceReminders` probe with JSON body `{}` returned 401
`AUTHENTICATION_REQUIRED`. That method gate opens this offline create freeze
only; it proves no accepted payload, mutation result, email effect, response
extension, live qualification, or cleanup.

The PUT probe returned 405 `METHOD_NOT_ALLOWED`, as did singular DELETE and
bulk DELETE with `?ids[]=nonexistent`. Official Supports omits update and
singular delete. Therefore update and singular delete remain excluded.

Both corresponding bulk inventory rows remain `ambiguous_bulk`, empty-tool,
and red. Bulk save has no established request/response body contract, and the
bulk DELETE probe returned 405. No bulk operation is frozen. No webhook is
documented for this surface.

## Product gate and fail-closed exclusions

Only after the required independent Grok freeze review ACCEPTs this page may a
separate product child implement and test the two frozen create tools. When
that later product greens the create row, it must replace the incorrect delete
cleanup wording with the fail-closed wording
`live non-production cleanup strategy unqualified; singular DELETE is unsupported`.
That wording is not cleanup qualification. The future product must preserve
strict outer-input rejection, the opaque inner map, ticket-only execute input,
the shared services, exact ticket bindings, required-root-only response
mapping, and one write with no retry.

This freeze explicitly excludes update, singular delete, both bulk operations,
all invoice-reminder-association writes, relation wire forms, payload schemas,
date and number encodings, email-send promises, response extras, webhooks,
generic HTTP or browser controls, credentials, live/UI/vision work, cleanup
claims, product implementation, tests or registration, coverage and status
changes, inventory greening, and completeness claims.
