---
name: wave_fiveg_freeze_independent_review
title: Wave-5g contract freeze independent review ACCEPT
desc: Authoritative root Grok acceptance of the cited offline contract for sales-tax ruleset and rule singular ticketed writes.
tags: [billy, api, sales-tax, writes, review, coverage]
sources:
  - https://www.billy.dk/api/
  - wiki/wave_fiveg_ticketed_writes_contract.md
  - coverage/api_v2_manifest.yaml
  - coverage/status.json
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
created: 2026-07-29T21:52:00Z
updated: 2026-07-29T21:52:00Z
---

# Wave-5g contract freeze independent review ACCEPT

## Verdict

| Claim | Result |
| --- | --- |
| Wave-5g cited contract freeze | **ACCEPT** |
| Official documentation versus maintained inventory | **PASS** |
| Freeze versus exact six-row tool/path/root map | **PASS** |
| Coverage honesty before product integration | **PASS** |
| Wave-5g product implementation | **not accepted** — separate Grok review required after root integration |
| Live, UI, vision, bulk, and completeness | **not claimed / fail-closed** |

The authoritative root `INDEPENDENT-REVIEW` Grok step accepted exact commit
`5612aa8bfe0c8ce108fb9dc8775bb9f4072b5132`. The full cited findings live outside
the public repository at `.fractal/main.billy_complete/tmp/grok-review.md`.

## Exact reviewed scope

The reviewed commit contains the frozen offline contract at
`wiki/wave_fiveg_ticketed_writes_contract.md`. It is limited to the following
six singular API v2 operations:

| Inventory id | Method and client path | Singular request root | Response roots |
| --- | --- | --- | --- |
| `api.salesTaxRulesets.create` | `POST /salesTaxRulesets` | `salesTaxRuleset` | `salesTaxRulesets`, optional `salesTaxRules` |
| `api.salesTaxRulesets.update` | `PUT /salesTaxRulesets/:id` | `salesTaxRuleset` | `salesTaxRulesets`, optional `salesTaxRules` |
| `api.salesTaxRulesets.delete` | `DELETE /salesTaxRulesets/:id` | bodyless | `salesTaxRulesets`, optional deleted metadata |
| `api.salesTaxRules.create` | `POST /salesTaxRules` | `salesTaxRule` | `salesTaxRules` |
| `api.salesTaxRules.update` | `PUT /salesTaxRules/:id` | `salesTaxRule` | `salesTaxRules` |
| `api.salesTaxRules.delete` | `DELETE /salesTaxRules/:id` | bodyless | `salesTaxRules`, optional deleted metadata |

The accepted contract preserves the locked
`https://api.billysbilling.com/v2` base, client-relative paths without a
duplicated `/v2`, opaque inner sales-tax payloads, strict outer Pydantic inputs,
partial `PUT`, update-id equality, and bodyless deletes. It requires the root
shared `ConfirmationStore` and `WriteProtocolService`, exact server-owned
executor-name ticket binding, single-use short-lived tickets, and no write
retry.

Parent ruleset writes may map a returned `salesTaxRules` list through
`additional_plural_roots=("salesTaxRules",)`, but the list is optional and
must not be fabricated when absent. Child rule writes use
`additional_plural_roots=()` and must not invent a parent `salesTaxRulesets`
multi-root. Official field notes match the freeze: nearly all fields are
immutable or readonly; `contactType` enum values are unpublished and stay
opaque offline; ticketed update is retained because Supports lists update and
unauthenticated PUT returns 401 rather than 405.

Bulk save and bulk delete remain `ambiguous_bulk` with empty `tool_name`. The
freeze invents no bulk body, webhook, file upload, attachment, sales-tax
sibling product, posting write, UI tool, or live claim. `accountNatures` and
`postings` writes stay excluded because real unauthenticated POST returns 405.

## Recheck and product gate

Official documentation was re-fetched during review with ETag
`hsisik4g9p3603`, body length 147934, and MD5
`c2efda0ee4cf9cf200e14910c5fc6996`, matching `coverage/status.json` with no
source drift. Unauthenticated probes returned 401 for POST and PUT on both
collections and 200 for missing-id DELETE, which the freeze correctly refuses
to treat as cleanup proof. Coverage at the freeze tip remains 142 implemented,
142 contract-tested, 0 live, 0 vision, and `complete: false`. No
`sales_tax_writes` module and no Wave-5g write registration exist yet. The
registry assert remains 190 `api_*` tools.

This ACCEPT opens offline product implementation for the twelve ticketed
sales-tax ruleset/rule write tools (six preview plus six execute). It is not a
product ACCEPT. After the product is integrated at root, a separate independent
Grok product review must inspect exact routes, request and response mapping,
ticket binding and replay boundaries, optional child multi-root behaviour,
registry target 202 `api_*` tools, coverage target 148 offline rows with the
six sales-tax CUD rows contract-tested only by real suites, and fail-closed
live/UI/bulk state.

No browser was launched, no credential or customer data was used, and no raw
browser evidence is retained. The acceptance remains an offline contract
decision only.
