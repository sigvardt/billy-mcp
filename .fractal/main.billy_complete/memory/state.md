---
name: state
desc: Current node state, verified review decisions, and open qualification work.
tags: [billy, coverage, review]
sources:
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
  - https://www.billy.dk/api/
created: 2026-07-29T12:12:38Z
updated: 2026-07-29T14:39:16Z
---

# state

## Current state

- Root product surface: **94** real `api_*` tools + 2 `coverage_*` (clear get/list offline complete). HEAD `4b632c7`.
- Clear resource get/list offline: **92/92** implemented and contract_tested.
- Specials offline-green: `api.special.user_get`, `api.special.user_organizations` only (4 specials remain red).
- Coverage: implemented 94, contract_tested 94, live_tested 0, vision 0, `complete: false`.
- Official docs fingerprint unchanged (etag `hsisik4g9p3603`, MD5 `c2efda0ee4cf9cf200e14910c5fc6996`).
- UI discovery still unauthenticated login only; all 339 UI rows red.
- `BILLY_API_TOKEN` unavailable; no live qualification claimed.
- Wave-5 **contract freeze** @ `9624d26`. Shared write protocol merged at `1e25dc2`. **No write tools registered** on root.
- Uncommitted prep on root (not product): coverage checker allows exact `*_execute` twins of inventory `*_preview` names; focused tests pass.

## Wave-5a candidate review (root Grok)

- Protocol tip `09648ce`: **ACCEPT** multi-root `additional_plural_roots` + multi-plural `meta.deletedRecords` mapping. Merge product files only; do not green inventory from this alone.
- Contact tip `b09e5ec`: **REJECTED** for a nested MCP `input` envelope. The current candidate tip has the required flat `contact` / `id` / `confirmation_ticket` surface, but needs a fresh independent review before it is accepted.
- Contact-person tip `2a56a92`: **REJECTED** because its update-preview `id` schema lacked `minLength: 1`. The current candidate tip adds `Field(min_length=1)` and a schema regression, but needs a fresh independent review before it is accepted.
- Focused overlay suite for three candidates: **58** passed. Root non-live: **511** passed (includes uncommitted checker tests).
- Catalog and daybook leaves not started. Catalog still waits for multi-root on root.
- Wiki: `wiki/wave_fivea_candidate_independent_review.md`. Detail: `.fractal/main.billy_complete/tmp/grok-review.md`.

## Evidence boundaries

- Official API: https://www.billy.dk/api/ fingerprint above.
- 207 clear / 92 bulk / 6 specials → 305 API; 339 UI; 0 webhooks.
- Unauth DELETE empty 200 is not cleanup proof. Bulk unproven.
- Remaining red API work: 115 clear writes, 92 bulk, four specials.

## Review decisions

- Wave-4 offline integration: **ACCEPT** slice; **FAIL** product completeness.
- Wave-5 contract freeze: **ACCEPT** honesty; no write greening.
- Foundation protocol merge: **ACCEPT**.
- Wave-5a candidates: protocol **ACCEPT**; contacts and contact persons are repaired on their branches but await a fresh independent review.
- Root fail-closed **ACCEPT / PASS**; product completeness **FAIL**.
- No REQUIRED rewrite of Wave-4 reads or freeze wiki.
- Before greening any Wave-5a row: multi-root on root, flat schemas, paired tools, ticket matrix, registration, offline evidence only; live stays false.

## Next implementation slice (for Codex Power)

1. Obtain a fresh independent review of the repaired contact and contact-person candidate tips; do not treat the original rejection as an acceptance.
2. Commit execute-twin coverage-checker prep on root.
3. Selectively integrate only verified product/test files: protocol first, then the re-reviewed contact and contact-person modules.
4. Spawn catalog (multi-root dependent) and daybook leaves; then registration for 30 tools / 15 offline-green rows / 124 `api_*`.
5. Independent Grok product review after integrated Wave-5a registration.

## Research notes (durable)

- Official docs fingerprint still `hsisik4g9p3603` / `c2efda0ee4cf9cf200e14910c5fc6996`.
- Unauth DELETE empty 200 on products, productPrices, contacts, contactPersons, daybooks.
- Contact `paymentTermsDays` required note; `locale` belongs-to; ignore historical paymentTermsValue/localeId/brand.
- Product create sample embeds `prices[]`; declare additional plural `productPrices`.
- ContactPersons name XOR email left to live.
- 46 resources × bulk save/delete = 92 bulk rows; no body contract.

## References

- Research: `.fractal/main.billy_complete/tmp/grok-research.md`
- Review: `.fractal/main.billy_complete/tmp/grok-review.md`
- Wiki: `wiki/wave_fivea_candidate_independent_review.md`, `wiki/wave_five_ticketed_writes_contract.md`, `wiki/wave_five_write_protocol_independent_review.md`
