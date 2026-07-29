---
name: wave_fiveg_product_ready_research_independent_review
title: Wave-5g product-ready research independent review ACCEPT
desc: Authoritative root Grok acceptance of the cited offline product-ready handoff for sales-tax ruleset and rule ticketed writes under the accepted Wave-5g freeze.
tags: [billy, api, sales-tax, writes, review, coverage, research]
sources:
  - https://www.billy.dk/api/
  - wiki/wave_fiveg_ticketed_writes_contract.md
  - wiki/wave_fiveg_freeze_independent_review.md
  - coverage/api_v2_manifest.yaml
  - coverage/status.json
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
created: 2026-07-29T22:08:00Z
updated: 2026-07-29T22:08:00Z
---

# Wave-5g product-ready research independent review ACCEPT

## Verdict

| Claim | Result |
| --- | --- |
| Wave-5g product-ready research handoff | **ACCEPT** offline as implementation handoff only |
| Official documentation versus maintained inventory | **PASS** |
| Research versus accepted freeze tool/path/root map | **PASS** |
| Coverage honesty before product | **PASS** |
| Wave-5g product implementation | **not accepted** — separate Grok review required after root integration |
| Live, UI, vision, bulk, and completeness | **not claimed / fail-closed** |

The authoritative root `INDEPENDENT-REVIEW` Grok step accepted the product-ready
research at scratch `.fractal/main.billy_complete/tmp/grok-research.md`
(research32) against HEAD **`0d6ccd8`**, freeze tip **`5612aa8`**, and freeze
page `wiki/wave_fiveg_ticketed_writes_contract.md`. Full cited findings live
outside the public repository at
`.fractal/main.billy_complete/tmp/grok-review.md`.

## Exact reviewed scope

This ACCEPT covers only the cited handoff that opens Codex Power product work
for the six singular API v2 CUD operations already frozen:

| Inventory id | Method and client path | Singular request root | Response roots |
| --- | --- | --- | --- |
| `api.salesTaxRulesets.create` | `POST /salesTaxRulesets` | `salesTaxRuleset` | `salesTaxRulesets`, optional `salesTaxRules` |
| `api.salesTaxRulesets.update` | `PUT /salesTaxRulesets/:id` | `salesTaxRuleset` | `salesTaxRulesets`, optional `salesTaxRules` |
| `api.salesTaxRulesets.delete` | `DELETE /salesTaxRulesets/:id` | bodyless | `salesTaxRulesets`, optional deleted metadata |
| `api.salesTaxRules.create` | `POST /salesTaxRules` | `salesTaxRule` | `salesTaxRules` |
| `api.salesTaxRules.update` | `PUT /salesTaxRules/:id` | `salesTaxRule` | `salesTaxRules` |
| `api.salesTaxRules.delete` | `DELETE /salesTaxRules/:id` | bodyless | `salesTaxRules`, optional deleted metadata |

Official documentation was re-fetched during review with ETag
`hsisik4g9p3603`, body length 147934, and MD5
`c2efda0ee4cf9cf200e14910c5fc6996`, matching `coverage/status.json` with no
source drift. Unauthenticated probes returned 401 for POST and PUT on both
collections and 200 for missing-id DELETE, which research correctly refuses to
treat as cleanup proof. `accountNatures` and `postings` POST remain 405 and
stay out of this product.

Coverage at HEAD remains 142 implemented, 142 contract-tested, 0 live, 0
vision, and `complete: false`. No `sales_tax_writes` module exists. The
registry assert remains 190 `api_*` tools. All six target CUD rows stay red;
bulk rows keep empty `tool_name`. All 339 UI rows stay unimplemented.

## Product gate

This ACCEPT opens offline product implementation for the twelve ticketed
sales-tax ruleset/rule write tools (six preview plus six execute) under the
accepted freeze. It is not a product ACCEPT. After product integrates at root,
a separate independent Grok product review must inspect exact routes, request
and response mapping, ticket binding and replay boundaries, optional child
multi-root behaviour, registry target 202 `api_*` tools, coverage target 148
offline rows with the six sales-tax CUD rows contract-tested only by real
suites, and fail-closed live/UI/bulk state.

No browser was launched, no credential or customer data was used, and no raw
browser evidence is retained. The acceptance remains an offline research
handoff decision only.
