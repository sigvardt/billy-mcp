---
name: wave_fivef_freeze_independent_review
title: Wave-5f contract freeze independent review ACCEPT
desc: Authoritative root Grok acceptance of the cited offline contract for tax-rate and deduction-component singular ticketed writes.
tags: [billy, api, tax, writes, review, coverage]
sources:
  - https://www.billy.dk/api/
  - wiki/wave_fivef_ticketed_writes_contract.md
  - coverage/api_v2_manifest.yaml
  - coverage/status.json
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
created: 2026-07-29T20:49:00Z
updated: 2026-07-29T20:49:00Z
---

# Wave-5f contract freeze independent review ACCEPT

## Verdict

| Claim | Result |
| --- | --- |
| Wave-5f cited contract freeze | **ACCEPT** |
| Official documentation versus maintained inventory | **PASS** |
| Freeze versus exact six-row tool/path/root map | **PASS** |
| Coverage honesty before product integration | **PASS** |
| Wave-5f product implementation | **not accepted** — separate Grok review required after root integration |
| Live, UI, vision, bulk, and completeness | **not claimed / fail-closed** |

The authoritative root `INDEPENDENT-REVIEW` Grok step accepted exact commit
`d412e8c4361bdd21bda7644480f15857d7135484`. The full cited findings live outside
the public repository at `.fractal/main.billy_complete/tmp/grok-review.md`.

## Exact reviewed scope

The reviewed commit contains the frozen offline contract at
`wiki/wave_fivef_ticketed_writes_contract.md`. It is limited to the following
six singular API v2 operations:

| Inventory id | Method and client path | Singular request root | Response roots |
| --- | --- | --- | --- |
| `api.taxRates.create` | `POST /taxRates` | `taxRate` | `taxRates`, optional `taxRateDeductionComponents` |
| `api.taxRates.update` | `PUT /taxRates/:id` | `taxRate` | `taxRates`, optional `taxRateDeductionComponents` |
| `api.taxRates.delete` | `DELETE /taxRates/:id` | bodyless | `taxRates`, optional deleted metadata |
| `api.taxRateDeductionComponents.create` | `POST /taxRateDeductionComponents` | `taxRateDeductionComponent` | `taxRateDeductionComponents` |
| `api.taxRateDeductionComponents.update` | `PUT /taxRateDeductionComponents/:id` | `taxRateDeductionComponent` | `taxRateDeductionComponents` |
| `api.taxRateDeductionComponents.delete` | `DELETE /taxRateDeductionComponents/:id` | bodyless | `taxRateDeductionComponents`, optional deleted metadata |

The accepted contract preserves the locked
`https://api.billysbilling.com/v2` base, client-relative paths without a
duplicated `/v2`, opaque inner tax payloads, strict outer Pydantic inputs,
partial `PUT`, update-id equality, and bodyless deletes. It requires the root
shared `ConfirmationStore` and `WriteProtocolService`, exact server-owned
executor-name ticket binding, single-use short-lived tickets, and no write
retry.

Parent tax-rate writes may map a returned
`taxRateDeductionComponents` list through
`additional_plural_roots=("taxRateDeductionComponents",)`, but the list is
optional and must not be fabricated when absent. Child deduction-component
writes use `additional_plural_roots=()` and must not invent a parent
`taxRates` multi-root. Documented field notes match the official property
tables: tax-rate mutability candidate `isActive`; deduction-component
mutability candidate `priority`; `source` enum values remain undocumented on
the public page and stay opaque offline.

Bulk save and bulk delete remain `ambiguous_bulk` with empty `tool_name`. The
freeze invents no bulk body, webhook, file upload, sales-tax sibling product,
posting write, UI tool, or live claim.

## Recheck and product gate

Official documentation was re-fetched during review with ETag
`hsisik4g9p3603`, body length 147934, and MD5
`c2efda0ee4cf9cf200e14910c5fc6996`, matching `coverage/status.json` with no
source drift. Unauthenticated probes returned 401 for POST and PUT on both
collections and 200 for missing-id DELETE, which the freeze correctly refuses
to treat as cleanup proof. Coverage at the freeze tip remains 136
implemented, 136 contract-tested, 0 live, 0 vision, and `complete: false`. No
`tax_writes` module and no tax write registration exist yet.

This ACCEPT opens offline product implementation for the twelve ticketed tax
write tools (six preview plus six execute). It is not a product ACCEPT. After
the product is integrated at root, a separate independent Grok product review
must inspect exact routes, request and response mapping, ticket binding and
replay boundaries, optional child multi-root behaviour, registry target 190
`api_*` tools, coverage target 142 offline rows with the six tax CUD rows
contract-tested only by real suites, and fail-closed live/UI/bulk state.

No browser was launched, no credential or customer data was used, and no raw
browser evidence is retained. The acceptance remains an offline contract
decision only.
