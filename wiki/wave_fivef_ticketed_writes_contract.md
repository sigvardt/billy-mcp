---
name: wave_fivef_ticketed_writes_contract
title: Wave-5f tax ticketed-write contract
desc: Cited offline contract for Billy tax-rate and deduction-component singular ticketed writes.
tags: [billy, api, tax, writes, contract]
sources:
  - https://www.billy.dk/api/
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
  - wiki/wave_fivee_ticketed_writes_contract.md
  - coverage/api_v2_manifest.yaml
created: 2026-07-29T20:40:00Z
updated: 2026-07-29T20:40:00Z
---

# Wave-5f tax ticketed-write contract

## Authority and gate

This is the frozen, offline-only implementation contract for the six documented
singular Billy API v2 CUD rows for `taxRates` and
`taxRateDeductionComponents`. It derives from the cited official API page,
re-fetched by Grok with ETag `hsisik4g9p3603`, MD5
`c2efda0ee4cf9cf200e14910c5fc6996`, and unchanged 147934-byte body. The full
cited research brief is retained outside the public repository at
`.fractal/main.billy_complete/tmp/grok-research.md`.

This contract requires an independent Grok freeze review before any product
implementation. Acceptance would open only the offline product-implementation
gate. It must not be read as acceptance of implementation, live qualification,
browser/UI parity, vision verification, bulk operations, special routes, or
overall completeness.

## Exact inventory and tool surface

| Inventory id | Preview tool | Execute tool | HTTP request | Request root | Response roots |
| --- | --- | --- | --- | --- | --- |
| `api.taxRates.create` | `api_tax_rates_create_preview` | `api_tax_rates_create_execute` | `POST /taxRates` | `taxRate` | `taxRates`, optional `taxRateDeductionComponents` |
| `api.taxRates.update` | `api_tax_rates_update_preview` | `api_tax_rates_update_execute` | `PUT /taxRates/:id` | `taxRate` | `taxRates`, optional `taxRateDeductionComponents` |
| `api.taxRates.delete` | `api_tax_rates_delete_preview` | `api_tax_rates_delete_execute` | `DELETE /taxRates/:id` | id binding only | `taxRates`, optional deleted metadata |
| `api.taxRateDeductionComponents.create` | `api_tax_rate_deduction_components_create_preview` | `api_tax_rate_deduction_components_create_execute` | `POST /taxRateDeductionComponents` | `taxRateDeductionComponent` | `taxRateDeductionComponents` |
| `api.taxRateDeductionComponents.update` | `api_tax_rate_deduction_components_update_preview` | `api_tax_rate_deduction_components_update_execute` | `PUT /taxRateDeductionComponents/:id` | `taxRateDeductionComponent` | `taxRateDeductionComponents` |
| `api.taxRateDeductionComponents.delete` | `api_tax_rate_deduction_components_delete_preview` | `api_tax_rate_deduction_components_delete_execute` | `DELETE /taxRateDeductionComponents/:id` | id binding only | `taxRateDeductionComponents`, optional deleted metadata |

Each inventory row remains one API operation: its `tool_name` is the preview
tool, while the execute twin is registered but is not a second coverage row.

## Shared write protocol

- Requests use only the locked API base `https://api.billysbilling.com/v2` and
  the client-relative paths shown above; no `/v2` path prefix is repeated.
- Create and update requests contain exactly one singular root. Updates are
  `PUT`, support partial fields, and require any body `id` to equal the route
  id. Deletes have no body and bind canonical request `{"id": "…"}`.
- Use the root's one `ConfirmationStore` and `WriteProtocolService`; do not
  construct a leaf-local store or retry a write request.
- Every `WriteOperationSpec` has the exact server-owned non-empty
  `execute_tool_name`, and every executor passes that name to the shared
  service. Mismatch fails as `CONFIRMATION_MISMATCH` before ticket consumption
  and before HTTP.
- Each preview is non-mutating and returns a short-lived, single-use ticket
  bound to the exact tool, organisation, target, canonical request, and
  expected effect. Execute accepts only `confirmation_ticket`.
- Outer Pydantic inputs must forbid extra fields. Inner `taxRate` and
  `taxRateDeductionComponent` objects remain opaque offline so callers can use
  the documented field surface without this contract inventing enum values or
  embedded-record lifecycle rules.

## Tax-rate boundaries

The official property table documents `organization` and `name` as immutable
required fields; `rate` is also immutable and required. `abbreviation`,
`description`, `appliesToSales`, `appliesToPurchases`, and
`netAmountMetaField` are immutable. `isPredefined` is readonly. The only clear
offline mutable candidate is `isActive`. Belongs-to values use the documented
`…Id` JSON convention, including `organizationId` and `netAmountMetaFieldId`.

The documented `deductionComponents` property is immutable has-many. An opaque
parent payload may carry it on creation under the official embedded-record
narrative, but this contract does not infer replacement, minimum-count,
create-only, or update semantics. Parent operation specifications set
`additional_plural_roots=("taxRateDeductionComponents",)`: that returned child
list is optional, must be mapped only when present and well-formed, and must
never be fabricated when absent.

## Deduction-component boundaries

The deduction-component table documents immutable required belongs-to
`taxRate`, immutable required `share`, immutable required `source`, and
immutable required belongs-to `account`. The public page does not list the
allowed `source` enum values. `priority` is optional and the only clear
non-immutable offline candidate. Callers use `taxRateId` and `accountId` for
the documented belongs-to JSON form while the inner payload remains opaque.

Child operation specifications set `additional_plural_roots=()`. Do not infer
that child writes return or mutate `taxRates`: the official page does not
establish a parent recomputation or response-root contract for this resource.

## Probe evidence and safety limits

Current unauthenticated probes against the locked API base returned 401 for
POST and PUT on both collections; OPTIONS advertised POST, PUT, and DELETE.
Missing-id DELETE returned an empty 200 response, consistent with the official
idempotent-delete narrative. That empty unauthenticated response is neither
cleanup proof nor live qualification evidence.

The API page documents bulk save and bulk delete support but provides no
request/response body contract for either operation. All four tax bulk rows
remain `ambiguous_bulk` with empty `tool_name`; this contract authorises no
bulk tool. It also authorises no file upload, JSON `files` create, webhook,
invoice special, posting, bank-payment, reference-data, transaction, UI, or
live workflow.

## Required offline evidence

The product suite must prove strict flat typed inputs, preview non-mutation,
exact HTTP method/path/body, bodyless deletes, update-id matching, typed
authentication and not-found failures, ticket tamper, expiry, replay, wrong
organisation/target/payload, same-module executor mismatch, and no extra
write. It must prove that parent responses map present optional
`taxRateDeductionComponents` but succeed when they are absent, and that child
responses do not fabricate a parent `taxRates` root. Root tests must establish
cross-resource executor binding and a post-product registry count of 190
`api_*` tools.

Only after the product and those tests land may coverage generation mark these
six rows implemented and contract-tested. The expected offline state then is
142 implemented/contract-tested API rows, zero live rows, all UI rows red, 92
ambiguous bulk rows red, unchanged special-route state, and `complete: false`.

## Live evidence gaps and exclusions

Live non-production tests must discover valid `source` enum values, whether an
organisation-scoped token needs `organizationId` in a create body, which fields
Billy accepts on update, embedded deduction-component create semantics, actual
multi-root responses, and the behaviour of predefined rates. They must also
prove cleanup with authenticated delete plus independent read-back. Until then,
all six rows remain `live_tested: false`.

This cohort excludes every bulk route, files and attachments, invoice specials,
sales-tax sibling resources, postings, bank payments, platform/reference writes,
transactions, browser/UI workflows, and all completeness claims. The 92
ambiguous bulk rows stay empty-tool red; no live test token, organisation data,
browser evidence, screenshot, frame, HAR, trace, or credential is introduced
by this contract.
