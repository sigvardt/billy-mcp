---
name: wave_fivei_ticketed_writes_contract
title: Wave-5i sales-tax account and meta-field ticketed-write contract
desc: Cited offline contract for singular sales-tax account and meta-field ticketed writes, accepted by independent Grok review.
tags: [billy, api, sales-tax, writes, coverage]
sources:
  - https://www.billy.dk/api/
  - wiki/wave_fivei_freeze_ready_research_independent_review.md
  - wiki/wave_fivei_freeze_independent_review.md
  - wiki/wave_fiveg_ticketed_writes_contract.md
  - wiki/offline_write_probe_rules.md
  - coverage/api_v2_manifest.yaml
  - coverage/status.json
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
created: 2026-07-30T00:00:00Z
updated: 2026-07-30T00:24:00Z
---

# Wave-5i sales-tax account and meta-field ticketed-write contract

## Authority and gate

This is the frozen offline-only implementation contract for the six documented
singular Billy API v2 CUD rows for `salesTaxAccounts` and `salesTaxMetaFields`.
It derives from the cited official API page, re-fetched by Grok with ETag
`hsisik4g9p3603`, MD5 `c2efda0ee4cf9cf200e14910c5fc6996`, and an unchanged
147934-byte body. The complete cited research and unauthenticated probe record
is retained outside the repository at
`.fractal/main.billy_complete/tmp/grok-research.md`.

The authoring gate is the ACCEPT recorded in
`wiki/wave_fivei_freeze_ready_research_independent_review.md`. The independent
Grok freeze review recorded in
`wiki/wave_fivei_freeze_independent_review.md` accepted this exact contract at
root commit `a176887`. That acceptance opens only the offline
product-implementation gate. It is not acceptance of implementation, live
qualification, browser/UI parity, vision verification, bulk operations, special
routes, or overall completeness.

## Exact inventory and tool surface

| Inventory id | Preview tool | Execute tool | HTTP request | Request root | Response roots |
| --- | --- | --- | --- | --- | --- |
| `api.salesTaxAccounts.create` | `api_sales_tax_accounts_create_preview` | `api_sales_tax_accounts_create_execute` | `POST /salesTaxAccounts` | `salesTaxAccount` | `salesTaxAccounts` |
| `api.salesTaxAccounts.update` | `api_sales_tax_accounts_update_preview` | `api_sales_tax_accounts_update_execute` | `PUT /salesTaxAccounts/:id` | `salesTaxAccount` | `salesTaxAccounts` |
| `api.salesTaxAccounts.delete` | `api_sales_tax_accounts_delete_preview` | `api_sales_tax_accounts_delete_execute` | `DELETE /salesTaxAccounts/:id` | id binding only | `salesTaxAccounts`, optional deleted metadata |
| `api.salesTaxMetaFields.create` | `api_sales_tax_meta_fields_create_preview` | `api_sales_tax_meta_fields_create_execute` | `POST /salesTaxMetaFields` | `salesTaxMetaField` | `salesTaxMetaFields` |
| `api.salesTaxMetaFields.update` | `api_sales_tax_meta_fields_update_preview` | `api_sales_tax_meta_fields_update_execute` | `PUT /salesTaxMetaFields/:id` | `salesTaxMetaField` | `salesTaxMetaFields` |
| `api.salesTaxMetaFields.delete` | `api_sales_tax_meta_fields_delete_preview` | `api_sales_tax_meta_fields_delete_execute` | `DELETE /salesTaxMetaFields/:id` | id binding only | `salesTaxMetaFields`, optional deleted metadata |

Each inventory row remains one API operation: its `tool_name` is the preview
tool, while the execute twin is registered but is not a second coverage row.
All six rows are medium sensitivity and record
`AUTHENTICATION_REQUIRED` and `OAUTH_INVALID_ACCESS_TOKEN` as documented
authentication errors. Until product code and real offline suites exist, every
one remains `implemented: false`, `contract_tested: false`, and
`live_tested: false`.

## Shared write protocol

- Requests use only the locked API base `https://api.billysbilling.com/v2` and
  the client-relative paths above; no request path repeats `/v2`.
- Create and update requests contain exactly one singular root. Updates are
  `PUT`, support a partial payload, and require any inner `id` to equal the
  route id. Deletes have no body and bind canonical request `{"id": "…"}`.
- Use the root's one `ConfirmationStore` and `WriteProtocolService`; do not
  construct a resource-local store and do not retry a write request.
- Each `WriteOperationSpec` has the exact non-empty server-owned
  `execute_tool_name`, and each execute handler passes it to the shared
  service. A mismatch must return `CONFIRMATION_MISMATCH` before ticket
  consumption and before HTTP.
- Every preview is non-mutating and returns a short-lived, single-use ticket
  bound to the exact tool, organisation, target, canonical request, and
  expected effect. Execute accepts only `confirmation_ticket`; an approval
  boolean or replacement business fields are not accepted.
- Outer Pydantic inputs must forbid undeclared fields. Inner
  `salesTaxAccount` and `salesTaxMetaField` objects remain opaque offline: the
  public contract does not publish all relation serialisations or enum values.

Both operation families set `additional_plural_roots=()`. Non-delete success
must map the primary plural root. Delete may map
`meta.deletedRecords.<plural>` when it is present, but must not fabricate
metadata or sibling record roots.

## Sales-tax account boundaries

The official `/v2/salesTaxAccounts` property table documents:

| Property | Type | Documentation boundary | Offline contract treatment |
| --- | --- | --- | --- |
| `organization` | belongs-to | immutable and required | Keep opaque; live work must establish the accepted wire value. |
| `account` | belongs-to | required, not marked immutable | Keep opaque; do not assume it is immutable or hard-type its wire form. |
| `type` | enum | required; allowed values are not published | Keep opaque; do not invent enum values. |
| `priority` | integer | no immutable or readonly marker | A clear candidate for later partial-update qualification. |

The API page documents singular get/list/create/update/delete plus bulk save
and bulk delete. It does not publish a bulk request, response, or partial-failure
contract, so both bulk rows remain `ambiguous_bulk` with empty tool
names. This contract authorises no bulk tool.

## Sales-tax meta-field boundaries

The official `/v2/salesTaxMetaFields` property table documents:

| Property | Type | Documentation boundary | Offline contract treatment |
| --- | --- | --- | --- |
| `organization` | belongs-to | immutable and required | Keep opaque; live work must establish the accepted wire value. |
| `name` | string | required, not marked immutable | Keep opaque with respect to update semantics; do not infer immutability. |
| `description` | string | no marker | A clear candidate for later partial-update qualification. |
| `priority` | integer | no marker | A clear candidate for later partial-update qualification. |
| `isPredefined` | boolean | no readonly marker | Keep opaque; do not borrow ruleset readonly semantics. |

As with accounts, bulk save and bulk delete are documented only as Supports
entries. Their rows remain empty-tool ambiguous bulk work.

## Probe evidence and safety limits

Unauthenticated probes against the locked base returned 401 for POST and PUT
on both collections. A DELETE of a missing id returned 200, consistent with
the official idempotent-delete narrative. The latter is neither cleanup proof
nor live qualification. OPTIONS advertises CORS methods but is not authority
for a real write method.

These findings satisfy the documented offline probe rule for a freeze draft:
the Supports tables, inventory, and real POST/PUT authentication gates agree.
They do not supply valid create payloads, mutation semantics, response
envelopes, authenticated deletion, or organisation cleanup evidence.

## Required offline product evidence

Before coverage may mark these rows implemented and contract-tested, a later
product must provide real suites proving:

- strict flat typed outer inputs and opaque inner-payload preservation;
- non-mutating preview, exact method, client-relative path, singular request
  root, bodyless delete, and update body/route id equality;
- typed authentication and not-found responses;
- ticket tamper, expiry, replay, wrong organisation, target, payload, and
  expected-effect failures;
- same-resource and cross-resource executor mismatch rejection before ticket
  consumption or HTTP through the root's single confirmation store;
- primary-root response mapping without fabricated sibling roots, and optional
  deleted metadata only when present; and
- one request only for an execution, with no write retry.

The later product should use a new module such as
`src/billy_mcp/api/sales_tax_account_meta_writes.py`; it must not expand the
accepted Wave-5g `sales_tax_writes.py` cohort. After real implementation and
tests, the registry target is 220 `api_*` tools and the offline coverage target
is 157 implemented and contract-tested API rows. Live evidence remains zero,
all UI and vision rows remain red, the 92 ambiguous bulk rows remain red, and
`coverage/status.json` remains `complete: false`.

## Live evidence gaps and exclusions

Authenticated non-production work must determine valid create bodies,
belongs-to serialisation, account `type` enum values, account and meta-field
update mutability, real response envelopes, and cleanup by authenticated
delete plus an independent read-back. In particular, it must test the possible
mutability of account `account`, meta-field `name`, and `isPredefined` rather
than inferring it from a missing immutable or readonly marker.

This contract excludes all bulk routes, `files` binary upload and special
routes, attachments, sales-tax ruleset/rule/payment/return work, webhooks,
generic HTTP or browser controls, live qualification, browser/UI parity, and
vision verification. No credential, organisation record, rendered frame, HAR,
trace, or screenshot is introduced by this freeze page.
