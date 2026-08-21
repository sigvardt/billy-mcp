---
name: wave_fivee_freeze_independent_review
title: Wave-5e contract freeze independent review ACCEPT
desc: Authoritative root Grok acceptance of the cited offline contract for bill and bill-line singular ticketed writes.
tags: [billy, api, bills, writes, review, coverage]
sources:
  - https://www.billy.dk/api/
  - wiki/wave_fivee_ticketed_writes_contract.md
  - coverage/api_v2_manifest.yaml
  - coverage/status.json
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
created: 2026-07-29T19:42:00Z
updated: 2026-07-29T19:48:00Z
---

# Wave-5e contract freeze independent review ACCEPT

## Verdict

| Claim | Result |
| --- | --- |
| Wave-5e cited contract freeze | **ACCEPT** |
| Official documentation versus maintained inventory | **PASS** |
| Freeze versus exact six-row tool/path/root map | **PASS** |
| Coverage honesty before product integration | **PASS** |
| Wave-5e product implementation | **not accepted** — separate Grok review required after root integration |
| Live, UI, vision, bulk, and completeness | **not claimed / fail-closed** |

The authoritative root `INDEPENDENT-REVIEW` Grok step accepted exact commit
`fc8118e809368fc8d2cf9fd8b0f7db4b43d333bb`. Its lifecycle event is 1649 and
recorded Grok cost is `0.3978628`. The review is a root review, not a result
from the subsequently exited child reviewer. This durable record restores that
authoritative verdict without relying on the child branch.

## Exact reviewed scope

The reviewed commit contains the frozen offline contract at
`wiki/wave_fivee_ticketed_writes_contract.md`. It is limited to the following
six singular API v2 operations:

| Inventory id | Method and client path | Singular request root | Primary response root |
| --- | --- | --- | --- |
| `api.bills.create` | `POST /bills` | `bill` | `bills` |
| `api.bills.update` | `PUT /bills/:id` | `bill` | `bills` |
| `api.bills.delete` | `DELETE /bills/:id` | bodyless | `bills` |
| `api.billLines.create` | `POST /billLines` | `billLine` | `billLines` |
| `api.billLines.update` | `PUT /billLines/:id` | `billLine` | `billLines` |
| `api.billLines.delete` | `DELETE /billLines/:id` | bodyless | `billLines` |

The accepted contract preserves the locked
`https://api.billysbilling.com/v2` base, client-relative paths without a
duplicated `/v2`, opaque inner bill payloads, strict outer Pydantic inputs,
partial `PUT`, update-id equality, and bodyless deletes. It requires the root
shared `ConfirmationStore` and `WriteProtocolService`, exact server-owned
executor-name ticket binding, single-use short-lived tickets, and no write
retry.

Bill-line writes may include a returned `bills` parent record through
`additional_plural_roots=("bills",)`, but the parent is optional and must not
be fabricated. Bill lines use `billId`, `accountId`, `taxRateId`,
`description`, and `amount`; the contract correctly excludes invoice-line
`productId` and `unitPrice` assumptions.

## Recheck and product gate

The acceptance is tied to the literal `fc8118e` contract, not an inferred
later state. The restored record was rechecked by reading that commit's
six-row map, request roots, ticket protocol, optional bill-parent mapping,
field boundaries, coverage target, and exclusions.

This ACCEPT opens the two offline product implementation modules for bills and
bill lines. It is not a product ACCEPT. After both modules are integrated at
root, a separate independent Grok product review must inspect exact routes,
request and response mapping, ticket binding and replay boundaries, registry
and coverage arithmetic, and fail-closed coverage. It must reject any live,
UI, vision, bulk, or overall-completeness claim without separate qualifying
evidence.

No browser was launched, no credential or customer data was used, and no raw
browser evidence is retained. The acceptance remains an offline contract
decision only.
