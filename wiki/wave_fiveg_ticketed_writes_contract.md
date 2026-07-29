---
name: wave_fiveg_ticketed_writes_contract
title: Wave-5g sales-tax rules ticketed-write contract
desc: Cited offline contract for singular sales-tax ruleset and rule ticketed writes, pending independent Grok freeze review.
tags: [billy, api, sales-tax, writes, coverage]
sources:
  - https://www.billy.dk/api/
  - wiki/wave_fivef_ticketed_writes_contract.md
  - wiki/wave_fivef_product_independent_review.md
  - coverage/api_v2_manifest.yaml
  - coverage/status.json
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
created: 2026-07-29T21:45:00Z
updated: 2026-07-29T21:45:00Z
---

# Wave-5g sales-tax rules ticketed-write contract

## Authority and gate

This is the frozen, offline-only implementation contract for the six documented
singular Billy API v2 CUD rows for `salesTaxRulesets` and `salesTaxRules`. It
derives from the cited official API page, re-fetched by Grok with ETag
`hsisik4g9p3603`, MD5 `c2efda0ee4cf9cf200e14910c5fc6996`, and unchanged
147934-byte body. The complete cited research and unauthenticated probe record
is retained outside the repository at
`.fractal/main.billy_complete/tmp/grok-research.md`.

This contract requires an independent Grok freeze review before any product
implementation. An ACCEPT would open only the offline product-implementation
gate. It is not acceptance of implementation, live qualification, browser/UI
parity, vision verification, bulk operations, special routes, or overall
completeness.

## Exact inventory and tool surface

| Inventory id | Preview tool | Execute tool | HTTP request | Request root | Response roots |
| --- | --- | --- | --- | --- | --- |
| `api.salesTaxRulesets.create` | `api_sales_tax_rulesets_create_preview` | `api_sales_tax_rulesets_create_execute` | `POST /salesTaxRulesets` | `salesTaxRuleset` | `salesTaxRulesets`, optional `salesTaxRules` |
| `api.salesTaxRulesets.update` | `api_sales_tax_rulesets_update_preview` | `api_sales_tax_rulesets_update_execute` | `PUT /salesTaxRulesets/:id` | `salesTaxRuleset` | `salesTaxRulesets`, optional `salesTaxRules` |
| `api.salesTaxRulesets.delete` | `api_sales_tax_rulesets_delete_preview` | `api_sales_tax_rulesets_delete_execute` | `DELETE /salesTaxRulesets/:id` | id binding only | `salesTaxRulesets`, optional deleted metadata |
| `api.salesTaxRules.create` | `api_sales_tax_rules_create_preview` | `api_sales_tax_rules_create_execute` | `POST /salesTaxRules` | `salesTaxRule` | `salesTaxRules` |
| `api.salesTaxRules.update` | `api_sales_tax_rules_update_preview` | `api_sales_tax_rules_update_execute` | `PUT /salesTaxRules/:id` | `salesTaxRule` | `salesTaxRules` |
| `api.salesTaxRules.delete` | `api_sales_tax_rules_delete_preview` | `api_sales_tax_rules_delete_execute` | `DELETE /salesTaxRules/:id` | id binding only | `salesTaxRules`, optional deleted metadata |

Each inventory row remains one API operation: its `tool_name` is the preview
tool, while the execute twin is registered but is not a second coverage row.
All rows are medium sensitivity. The inventory records
`AUTHENTICATION_REQUIRED` and `OAUTH_INVALID_ACCESS_TOKEN` as the documented
authentication errors; response mapping must preserve concrete changed records
and any documented `meta.deletedRecords` metadata.

## Shared write protocol

- Requests use only the locked API base `https://api.billysbilling.com/v2` and
  the client-relative paths shown above; no `/v2` path prefix is repeated.
- Create and update requests contain exactly one singular root. Updates are
  `PUT`, support a partial payload, and require any body `id` to equal the
  route id. Deletes have no body and bind canonical request `{"id": "…"}`.
- Use the root's one `ConfirmationStore` and `WriteProtocolService`; do not
  construct a leaf-local store or retry a write request.
- Every `WriteOperationSpec` has the exact server-owned, non-empty
  `execute_tool_name`, and every executor passes that name to the shared
  service. A mismatch must fail as `CONFIRMATION_MISMATCH` before ticket
  consumption and before HTTP.
- Each preview is non-mutating and returns a short-lived, single-use ticket
  bound to the exact tool, organisation, target, canonical request, and
  expected effect. Execute accepts only `confirmation_ticket`.
- Outer Pydantic inputs must forbid extra fields. Inner `salesTaxRuleset` and
  `salesTaxRule` objects remain opaque offline because the public contract does
  not specify all enum or embedded-record lifecycle values.

## Ruleset boundaries

The official property table documents `organization` and `name` as immutable
and required, and serialises their belongs-to relation as `organizationId`.
`abbreviation`, `description`, and `fallbackTaxRate` are immutable; the latter
uses `fallbackTaxRateId`. `isPredefined` is readonly. The `rules` has-many
relation is immutable. The global embedded-record narrative may permit an
opaque create payload, but this contract does not infer replacement,
create-only, or update semantics for it.

No clear mutable field is documented for the ruleset, but the official Supports
table lists update and an unauthenticated `PUT` is blocked by authentication
(401), not by method rejection. The update operation is therefore retained
with an opaque inner payload and must be live-qualified later.

Ruleset operation specifications set
`additional_plural_roots=("salesTaxRules",)`. That returned child list is
optional, must be mapped only when present and well-formed, and must never be
fabricated when absent.

## Rule boundaries

The official property table documents immutable required belongs-to `ruleset`
and `country`, serialised as `rulesetId` and `countryId`. Optional immutable
belongs-to values use `stateId`, `countryGroupId`, and `taxRateId`.
`contactType` is an immutable enum whose allowed values are not published;
`priority` is also immutable. These uncertainties require an opaque inner
`salesTaxRule` payload and later live discovery.

No clear mutable field is documented for a rule, but update remains a documented
Supports operation and a real unauthenticated `PUT` returns 401 rather than
405. Child operation specifications set `additional_plural_roots=()`. Do not
infer that child writes return or mutate a parent `salesTaxRulesets` root.

## Probe evidence and safety limits

Current unauthenticated probes against the locked API base returned 401 for
POST and PUT on both collections. Missing-id DELETE returned an empty 200
response, consistent with the official idempotent-delete narrative. That empty
response is neither cleanup proof nor live qualification evidence. OPTIONS
advertises CORS methods but is not authority for a real write method.

The API page documents bulk save and bulk delete support but provides no
request/response body contract for either operation. All four sales-tax
ruleset/rule bulk rows remain `ambiguous_bulk` with empty `tool_name`; this
contract authorises no bulk tool. It also authorises no file upload, JSON
`files` create, webhook, invoice special, attachment, sales-tax sibling,
posting, bank-payment, reference-data, transaction, UI, or live workflow.

## Required offline evidence

The product suite must prove strict flat typed inputs, preview non-mutation,
exact HTTP method/path/body, bodyless deletes, update-id matching, typed
authentication and not-found failures, ticket tamper, expiry, replay, wrong
organisation/target/payload, same-module executor mismatch, and no extra
write. It must prove that parent responses map a present optional
`salesTaxRules` list but succeed when that list is absent, and that child
responses do not fabricate a parent `salesTaxRulesets` root. Root tests must
establish cross-resource executor binding through the single store and a
post-product registry count of 202 `api_*` tools.

Only after product code and those tests land may coverage generation mark these
six rows implemented and contract-tested. The expected offline state then is
148 implemented/contract-tested API rows, zero live rows, all UI rows red, 92
ambiguous bulk rows red, unchanged special-route state, and `complete: false`.

## Live evidence gaps and exclusions

Live non-production tests must determine whether an organisation-scoped token
requires `organizationId` on create, valid `contactType` enum values, whether
predefined rulesets reject update or delete, whether parent create accepts
embedded `rules`, whether responses include the optional child root, and
whether any partial update is accepted despite the immutable property table.
They must prove cleanup with authenticated delete plus independent GET
read-back. Until then all six rows remain `live_tested: false`.

This cohort excludes all bulk routes, files and attachments, invoice specials,
sales-tax account/meta-field/payment/return resources, postings, bank payments,
platform/reference writes, transactions, browser/UI workflows, and every
completeness claim. `accountNatures` and `postings` writes remain red because
real unauthenticated POST and PUT return 405 despite permissive CORS OPTIONS
advertising. No live test token, organisation data, browser evidence,
screenshot, frame, HAR, trace, or credential is introduced by this contract.
