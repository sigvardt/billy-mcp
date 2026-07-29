---
name: state
desc: Current node state, verified review decisions, and open qualification work.
tags: [billy, coverage, review]
sources:
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
  - https://www.billy.dk/api/
created: 2026-07-29T12:12:38Z
updated: 2026-07-29T15:25:00Z
---

# state

## Current state

- Root product surface: **94** real `api_*` tools + 2 `coverage_*`. Write modules on root: protocol multi-root, contacts, contact persons. Catalog/daybook still candidate-only (not on root). **No write tools registered** in `server.py`.
- Clear resource get/list offline: **92/92** implemented and contract_tested.
- Specials offline-green: `api.special.user_get`, `api.special.user_organizations` only (4 specials remain red).
- Coverage: implemented 94, contract_tested 94, live_tested 0, vision 0, `complete: false`.
- Official docs fingerprint unchanged (etag `hsisik4g9p3603`, MD5 `c2efda0ee4cf9cf200e14910c5fc6996`).
- UI discovery still unauthenticated login only; all 339 UI rows red.
- `BILLY_API_TOKEN` unavailable; no live qualification claimed.
- Wave-5 contract freeze binding. Execute-twin coverage gate present.

## Wave-5a independent review (current)

- Full report: `.fractal/main.billy_complete/tmp/grok-review.md`.
- Wiki: `wiki/wave_fivea_catalog_daybook_independent_review.md` (catalog/daybook gate); prior cohort in `wiki/wave_fivea_candidate_independent_review.md`.
- Root fail-closed **PASS**. Product completeness **FAIL** (expected).
- Catalog tip `ba4101a` (product `03f5720`): **ACCEPT** selective product/test merge.
- Daybook tip `0d4b0e5` (product `791c84d`): **ACCEPT** selective product/test merge.
- productPrice MCP naming risk from research is **closed** on the committed catalog tip.
- Focused overlay suite: **105** passed (protocol + contacts + contact persons + catalog + daybook).
- Docs fingerprint re-verified this review pass.
- The dedicated Grok child could not authenticate before review; the root Grok report is authoritative. The non-authoritative Codex fallback was stopped once that gate existed, and no fallback verdict is relied on.

## Evidence boundaries

- Official API: https://www.billy.dk/api/ fingerprint above.
- 207 clear / 92 bulk / 6 specials → 305 API; 339 UI; 0 webhooks.
- Unauth DELETE empty 200 is not cleanup proof. Bulk unproven.
- Remaining red API work: 115 clear writes, 92 bulk, four specials (before Wave-5a registration greening).

## Review decisions

- Wave-4 offline integration: **ACCEPT** slice; **FAIL** product completeness.
- Wave-5 contract freeze: **ACCEPT** honesty; no write greening.
- Foundation protocol merge: **ACCEPT**.
- Wave-5a protocol/contacts/contact persons: **ACCEPT** (merged product modules, unregistered).
- Wave-5a catalog tip `ba4101a`: **ACCEPT** selective merge.
- Wave-5a daybook tip `0d4b0e5`: **ACCEPT** selective merge.
- Root fail-closed **ACCEPT / PASS**; product completeness **FAIL**.
- Before greening any Wave-5a row: root registration of all 30 tools, ticket matrix evidence, offline only; live stays false.

## Next implementation slice (for Codex Power)

1. Selective merge catalog + daybook product/test files only (tips above); exclude child seeds.
2. Root registration: one store + protocol, 30 write tools, green only 15 offline write rows → 124 `api_*`.
3. Independent Grok product review after integrated Wave-5a registration.

## Research notes (durable)

- Official docs fingerprint still `hsisik4g9p3603` / `c2efda0ee4cf9cf200e14910c5fc6996`.
- Unauth DELETE empty 200 on products, productPrices, contacts, contactPersons, daybooks.
- Product create sample embeds `prices[]` with `unitPrice` + `currencyId`.
- productPrices description swap is docs noise; types/required authoritative.
- Daybooks: required `name` + `isTransactionSummaryEnabled` as docs notes; opaque offline payload.
- Multi-word singular roots use Billy camelCase on MCP surface (`contactPerson`, `productPrice`).
- 46 resources × bulk save/delete = 92 bulk rows; no body contract.

## References

- Research: `.fractal/main.billy_complete/tmp/grok-research.md`
- Review: `.fractal/main.billy_complete/tmp/grok-review.md`
- Wiki: `wiki/wave_fivea_catalog_daybook_independent_review.md`, `wiki/wave_fivea_candidate_independent_review.md`, `wiki/wave_five_ticketed_writes_contract.md`
