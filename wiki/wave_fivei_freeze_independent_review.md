---
name: wave_fivei_freeze_independent_review
title: Wave-5i contract freeze independent review ACCEPT
desc: Authoritative root Grok acceptance of the cited offline contract for singular sales-tax account and meta-field ticketed writes.
tags: [billy, api, sales-tax, writes, review, coverage]
sources:
  - https://www.billy.dk/api/
  - wiki/wave_fivei_ticketed_writes_contract.md
  - wiki/wave_fivei_freeze_ready_research_independent_review.md
  - wiki/wave_fiveg_ticketed_writes_contract.md
  - wiki/offline_write_probe_rules.md
  - coverage/api_v2_manifest.yaml
  - coverage/status.json
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
created: 2026-07-30T00:24:00Z
updated: 2026-07-30T00:28:11Z
---

# Wave-5i contract freeze independent review ACCEPT

## Verdict

| Claim | Result |
| --- | --- |
| Wave-5i cited contract freeze | **ACCEPT** |
| Official documentation versus maintained inventory | **PASS** |
| Freeze versus exact six-row tool/path/root map | **PASS** |
| Coverage honesty before product integration | **PASS** |
| Wave-5i product implementation | **not accepted** — separate Grok review required after root integration |
| Live, UI, vision, bulk, and completeness | **not claimed / fail-closed** |

The authoritative root `INDEPENDENT-REVIEW` Grok step accepted the freeze page at
root commit **`a176887`** (`wiki/wave_fivei_ticketed_writes_contract.md`). Full
cited findings live outside the public repository at
`.fractal/main.billy_complete/tmp/grok-review.md`.

The dedicated Grok review child could not authenticate and produced no durable
verdict. Its Codex Power fallback was intentionally closed without a
supplementary review record once this root Grok review accepted the contract.
This root review is the authoritative freeze gate.

## Exact reviewed scope

The accepted contract freezes exactly six singular API v2 JSON CUD operations
(twelve ticketed tools: six preview + six execute):

| Inventory id | Method and client path | Singular request root | Response roots (offline) |
| --- | --- | --- | --- |
| `api.salesTaxAccounts.create` | `POST /salesTaxAccounts` | `salesTaxAccount` | `salesTaxAccounts` only |
| `api.salesTaxAccounts.update` | `PUT /salesTaxAccounts/:id` | `salesTaxAccount` | `salesTaxAccounts` only |
| `api.salesTaxAccounts.delete` | `DELETE /salesTaxAccounts/:id` | bodyless id binding | `salesTaxAccounts`, optional deleted metadata |
| `api.salesTaxMetaFields.create` | `POST /salesTaxMetaFields` | `salesTaxMetaField` | `salesTaxMetaFields` only |
| `api.salesTaxMetaFields.update` | `PUT /salesTaxMetaFields/:id` | `salesTaxMetaField` | `salesTaxMetaFields` only |
| `api.salesTaxMetaFields.delete` | `DELETE /salesTaxMetaFields/:id` | bodyless id binding | `salesTaxMetaFields`, optional deleted metadata |

The accepted contract preserves the locked
`https://api.billysbilling.com/v2` base, client-relative paths without a
duplicated `/v2`, opaque inner sales-tax payloads, strict outer Pydantic
inputs, partial `PUT`, update-id equality, and bodyless deletes. It requires
the root shared `ConfirmationStore` and `WriteProtocolService`, exact
server-owned executor-name ticket binding, single-use short-lived tickets, and
no write retry. Spec constants:

- Accounts: `collection_path="/salesTaxAccounts"`, `singular_root="salesTaxAccount"`,
  `plural_root="salesTaxAccounts"`, `additional_plural_roots=()`
- Meta fields: `collection_path="/salesTaxMetaFields"`,
  `singular_root="salesTaxMetaField"`, `plural_root="salesTaxMetaFields"`,
  `additional_plural_roots=()`

Official field notes match the freeze: account `organization` is immutable
required; `account` is required but not marked immutable; `type` is a required
enum with unpublished values; `priority` is a clear mutable candidate. Meta
field `organization` is immutable required; `name` is required but not marked
immutable; `description` and `priority` are mutable candidates; `isPredefined`
has no readonly marker (unlike Wave-5g rulesets) and stays opaque offline.

Bulk save and bulk delete remain `ambiguous_bulk` with empty `tool_name`. The
freeze invents no bulk body, webhook, file upload, attachment rework, sales-tax
ruleset/rule/payment/return product, posting write, UI tool, or live claim.
Product must land in a new module such as
`sales_tax_account_meta_writes.py` and must not expand Wave-5g
`sales_tax_writes.py`.

## Recheck and product gate

Official documentation was re-fetched during review with ETag
`hsisik4g9p3603`, body length 147934, and MD5
`c2efda0ee4cf9cf200e14910c5fc6996`, matching `coverage/status.json` with no
source drift. Unauthenticated probes returned 401 for POST and PUT on both
collections and 200 for missing-id DELETE, which the freeze correctly refuses
to treat as cleanup proof. Coverage at the freeze tip remains 151 implemented,
151 contract-tested, 0 live, 0 vision, and `complete: false`. No
`sales_tax_account_meta_writes` module exists. The six CUD inventory rows stay
red. Registry remains 208 `api_*` tools.

This ACCEPT opens offline product implementation for the twelve ticketed
sales-tax account and meta-field write tools. It is not a product ACCEPT. After
the product is integrated at root, a separate independent Grok product review
must inspect exact routes, opaque payload discipline, ticket binding and replay
boundaries, registry target **220** `api_*` tools, coverage target **157**
offline rows with the six sales-tax account/meta-field CUD rows
contract-tested only by real suites, and fail-closed live/UI/bulk state.

No browser was launched, no credential or customer data was used, and no raw
browser evidence is retained. The acceptance remains an offline contract
decision only.
