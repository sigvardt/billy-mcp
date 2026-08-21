---
name: wave_fiver_ticketed_writes_contract
title: Wave-5r salesTaxReturns update ticketed writes contract
desc: Cited wiki-only offline contract freezing singular salesTaxReturns update; create, delete, bulk, product, live, UI, and completeness remain excluded.
tags: [billy, api, sales_tax_returns, writes, ticketed, offline]
sources:
  - https://www.billy.dk/api/
  - https://api.billysbilling.com/v2
  - wiki/wave_fiver_sales_tax_returns_freeze_ready_research.md
  - "parent scratch: .fractal/main.billy_complete/tmp/grok-research.md (Research73)"
  - wiki/offline_write_probe_rules.md
  - wiki/wave_fiveq_ticketed_writes_contract.md
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
created: 2026-07-30T14:53:57Z
updated: 2026-07-30T14:53:57Z
---

# Wave-5r salesTaxReturns update ticketed writes contract

## Scope, evidence, and authority boundary

This is a **wiki-only offline freeze contract** for exactly one future Billy
API inventory operation: singular `api.salesTaxReturns.update`. It declares
only the two future tools in the table below. It authorises no source
implementation, server registration, contract tests, coverage or status
change, inventory greening, or product work.

The evidence is the cited [[wave_fiver_sales_tax_returns_freeze_ready_research]]
package and its parent scratch brief at
`.fractal/main.billy_complete/tmp/grok-research.md` (Research73), together with
the approved write-protocol design cited in the package sources. Research73
records the official Billy API documentation and its unauthenticated method
gates. Its API base is
`https://api.billysbilling.com/v2`; every path in this page is client-relative
and therefore omits `/v2`. [[offline_write_probe_rules]] and
[[wave_fiveq_ticketed_writes_contract]] are protocol precedents, not additional
write authority.

The following stages remain separate:

| Stage | Status and meaning |
| --- | --- |
| Research | Research73 supplies official-doc and unauthenticated method-gate evidence only. It is not this freeze, product authority, a test, or qualification. |
| This freeze | This page freezes the future offline contract only. Authoring it is not independent freeze acceptance. |
| Independent review | A later, separately authorised independent freeze review is required before salesTaxReturns product work. |
| Product and testing | A later authorised leaf may implement/register and contract-test the two tools only after the required acceptance; none is created or evidenced here. |
| Live, UI, and vision | Authenticated non-production, UI, and vision evidence are separate work; none is supplied here. |
| Completeness | Research, this freeze, or a later test does not support a completeness claim. |

## Exact frozen surface

| Inventory id | Future preview tool | Future execute tool | Client-relative request | Required success root |
| --- | --- | --- | --- | --- |
| `api.salesTaxReturns.update` | `api_sales_tax_returns_update_preview` | `api_sales_tax_returns_update_execute` | `PUT /salesTaxReturns/:id`; outer `{id, salesTaxReturn: map}` | `salesTaxReturns` |

This is one inventory operation; its execute twin does not create another
inventory row. These are the **only** future tool names declared by this
contract, and neither is implemented or registered by this page.

## Future input, request, and response contract

The future preview has a strict outer model with `extra="forbid"`: it requires
a non-empty route `id` and a `salesTaxReturn` map, with no undeclared outer
fields. The inner `salesTaxReturn` remains an opaque
`dict[str, JsonValue]`, not a generic HTTP control and not a field-level
sales-tax-return schema.

The route `id` is the target for `PUT /salesTaxReturns/:id`. An omitted inner
`salesTaxReturn.id` is accepted. If that inner `id` is supplied, it must equal
the route `id`. The contract freezes no other inner required field, relation
wire form, `*Id` alias, enum set, date or number encoding, field-level
validation, or payload sample.

Future response mapping requires only the `salesTaxReturns` root. This freeze
specifies no response metadata shape, returned record shape, additional root,
or response extension.

## Shared preview and execute protocol

- Preview never mutates. It validates the strict outer boundary, confirms the
  organisation context through the shared protocol, canonicalizes the request,
  describes the expected effect, and issues an opaque, single-use confirmation
  ticket lasting no more than five minutes.
- Each ticket is bound to the exact
  `api_sales_tax_returns_update_execute` tool, organisation, target route `id`,
  canonical request, and expected effect.
- Execute accepts only a non-empty `confirmation_ticket`; it accepts no
  business payload, replacement target, second preview input, or approval
  boolean.
- Execute restores the bound request and makes exactly one HTTP write with no
  retry.
- Missing, invalid, expired, consumed, or mismatched tickets fail closed. A
  mismatch of execute tool, organisation, target, canonical request, or
  expected effect requires a new preview and ticket.

Future implementation must use the shared ticket protocol rather than create a
separate approval mechanism. Confirmation tickets and any sensitive values are
not log or durable-storage material.

## Supports and property boundaries

Research73 records the official `/v2/salesTaxReturns` Supports list as get by
id, list, **update**, bulk save, and bulk delete. It omits create and singular
delete. Supports constrains this narrow update freeze; it is neither a bulk
body contract nor a writable-field allowlist.

The official readonly properties—`organization`, `createdTime`, `periodType`,
`period`, `correctionNo`, `startDate`, `endDate`, and `isPaid`—are not
client-writable. The blank-notes properties `periodText`, `reportDeadline`, and
`isSettled` remain opaque inner values. This freeze does not say they are
writable, accepted live, or reversible through a later update. In particular,
settlement might be one-way.

The property table is a boundary for the opaque map, not permission to mutate a
property and not a field-level validation contract.

## Method gates, cleanup limits, and exclusions

Research73's unauthenticated probes establish only these method gates:

| Method and client-relative path | Result | Contract consequence |
| --- | --- | --- |
| `POST /salesTaxReturns` | 405 `METHOD_NOT_ALLOWED` | Create is closed and excluded. |
| `PUT /salesTaxReturns/:id` | 401 `AUTHENTICATION_REQUIRED` | Opens only this offline singular-update freeze; it proves neither an accepted payload nor a mutation, response, or live qualification. |
| `DELETE /salesTaxReturns/:id` | 405 `METHOD_NOT_ALLOWED` | Singular delete is unsupported and excluded. |
| `PUT /salesTaxReturns/:id` with an empty body | 400 `INVALID_REQUEST_BODY` | The update method is not method-closed; this does not establish a valid payload or field-level validation. |

All bulk operations remain excluded: the official page provides no bulk body
contract, and this freeze declares no bulk tool. No webhook is frozen; the
cited official page supplies no webhook evidence.

Singular DELETE is unsupported. Restore via PUT remains unproven, and possible
settlement changes might be one-way. Those limits are not cleanup
qualification.

This contract explicitly excludes create, singular delete, every bulk
operation, webhooks, generic HTTP controls, browser controls, field-level
payload samples, field-level validation, source implementation, server
registration, contract tests, coverage or status changes, inventory greening,
credentials, live work, UI work, vision work, cleanup qualification, and
completeness claims. It does not claim independent review, product authority,
live, UI, vision, cleanup qualification, or completeness evidence.
