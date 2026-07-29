---
name: state
desc: Current node state, verified review decisions, and open qualification work.
tags: [billy, coverage, review]
sources:
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
  - https://www.billy.dk/api/
created: 2026-07-29T12:12:38Z
updated: 2026-07-29T15:05:00Z
---

# state

## Current state

- Root product surface: **94** real `api_*` tools + 2 `coverage_*` (clear get/list offline complete). The accepted Wave-5a implementation modules are merged, but no write tool is registered yet.
- Clear resource get/list offline: **92/92** implemented and contract_tested.
- Specials offline-green: `api.special.user_get`, `api.special.user_organizations` only (4 specials remain red).
- Coverage: implemented 94, contract_tested 94, live_tested 0, vision 0, `complete: false`.
- Official docs fingerprint unchanged (etag `hsisik4g9p3603`, MD5 `c2efda0ee4cf9cf200e14910c5fc6996`).
- UI discovery still unauthenticated login only; all 339 UI rows red.
- `BILLY_API_TOKEN` unavailable; no live qualification claimed.
- Wave-5 **contract freeze** @ `9624d26`. Shared write protocol merged at `1e25dc2` (primary root only). Execute-twin coverage gate on root @ `5ab3efa`. **No write tools registered** on root.
- The accepted Wave-5a source leaves were intentionally closed after selective merge; their branch tips remain audit evidence.

## Wave-5a independent review (current)

- Full report: `.fractal/main.billy_complete/tmp/grok-review.md`.
- Shared wiki: `wiki/wave_fivea_candidate_independent_review.md` (updated).
- Root fail-closed **PASS**. Product completeness **FAIL** (expected).
- Protocol tip `4b2c12c` (product from `239bc52`): **ACCEPT** multi-root.
- Contact tip `a86afe9` (product from `1b8bb42`): **ACCEPT** flat schema; prior nested-input reject closed.
- Contact-person tip `341d0b1` (product from `cd0a379`): **ACCEPT** update id minLength; prior reject closed.
- Focused overlay suite: **58** passed (protocol + contacts + contact persons).
- Selective root merges: `95e03c4` protocol, `9d40949` contacts, and
  `b25582f` contact persons. Integrated checks passed: lint and **546**
  non-live tests.
- Docs fingerprint re-verified this review pass.
- Fallback child review remains non-authoritative if present; this Grok root review is the merge gate.

## Evidence boundaries

- Official API: https://www.billy.dk/api/ fingerprint above.
- 207 clear / 92 bulk / 6 specials → 305 API; 339 UI; 0 webhooks.
- Unauth DELETE empty 200 is not cleanup proof. Bulk unproven.
- Remaining red API work: 115 clear writes, 92 bulk, four specials.

## Review decisions

- Wave-4 offline integration: **ACCEPT** slice; **FAIL** product completeness.
- Wave-5 contract freeze: **ACCEPT** honesty; no write greening.
- Foundation protocol merge: **ACCEPT**.
- Wave-5a candidates (current tips): protocol **ACCEPT**; contacts **ACCEPT**; contact persons **ACCEPT** for selective product/test merge only.
- Root fail-closed **ACCEPT / PASS**; product completeness **FAIL**.
- Before greening any Wave-5a row: multi-root on root, flat schemas, paired tools, ticket matrix, registration, offline evidence only; live stays false.

## Next implementation slice (for Codex Power)

1. Catalog (multi-root dependent; `productPrices` additional root on product ops) and daybook leaves are active against the verified root base; review their committed tips independently when they report.
2. Root registration: one store + protocol, 30 write tools, green only 15 offline write rows → 124 `api_*`.
3. Independent Grok product review after integrated Wave-5a registration.

## Research notes (durable)

- Official docs fingerprint still `hsisik4g9p3603` / `c2efda0ee4cf9cf200e14910c5fc6996`.
- Unauth DELETE empty 200 on products, productPrices, contacts, contactPersons, daybooks.
- Product create sample embeds `prices[]` with `unitPrice` + `currencyId`.
- productPrices description swap is docs noise; types/required authoritative.
- Daybooks: required `name` + `isTransactionSummaryEnabled`.
- Contact `paymentTermsDays` required note; locale belongs-to; ignore historical paymentTermsValue/localeId/brand.
- ContactPersons name XOR email left to live.
- 46 resources × bulk save/delete = 92 bulk rows; no body contract.

## References

- Research: `.fractal/main.billy_complete/tmp/grok-research.md`
- Review: `.fractal/main.billy_complete/tmp/grok-review.md`
- Wiki: `wiki/wave_fivea_candidate_independent_review.md`, `wiki/wave_five_ticketed_writes_contract.md`, `wiki/wave_five_write_protocol_independent_review.md`
