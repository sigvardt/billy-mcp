---
name: state
desc: Current node state, verified review decisions, and open qualification work.
tags: [billy, coverage, review]
sources:
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
  - https://www.billy.dk/api/
created: 2026-07-29T12:12:38Z
updated: 2026-07-29T14:09:29Z
---

# state

## Current state

- Root product surface: **94** real `api_*` tools + 2 `coverage_*` (clear get/list offline complete). HEAD `e8a1f9c`.
- Clear resource get/list offline: **92/92** implemented and contract_tested.
- Specials offline-green: `api.special.user_get`, `api.special.user_organizations` only (4 specials remain red).
- Coverage: implemented 94, contract_tested 94, live_tested 0, vision 0, `complete: false`.
- Official docs fingerprint unchanged (etag `hsisik4g9p3603`, MD5 `c2efda0ee4cf9cf200e14910c5fc6996`) after IR re-fetch.
- UI discovery still unauthenticated login only; all 339 UI rows red (`parity_status=discovery_required`).
- `BILLY_API_TOKEN` unavailable; no live qualification claimed.
- Wave-5 **contract freeze** @ `9624d26`. Shared write protocol merged at `1e25dc2`. **No write tools registered** in `server.py`. No `*_writes.py` product modules on root.
- Wave-5a fan-out plan exists; three leaves are active (protocol mapping, contact writes, contact person writes) but **no product commits** are ahead of root. Their pre-edit Grok research step failed because its CLI was unauthenticated; the full retry is now explicitly routed to Codex Power and consumes the frozen cited parent brief without new external research.
- Verification: root lint passed and the non-live suite **510** passed; protocol+confirmation focused suite **32** passed; false-green count **0**.

## Evidence boundaries

- Official API: https://www.billy.dk/api/ fingerprint above.
- 207 clear / 92 bulk / 6 specials → 305 API; 339 UI; 0 webhooks.
- Unauth DELETE empty 200 is not cleanup proof. Bulk unproven.
- Remaining red API work: 115 clear writes, 92 bulk, four specials.

## Review decisions

- Wave-4 offline integration: **ACCEPT** slice; **FAIL** product completeness.
- Wave-5 contract freeze: **ACCEPT** honesty; no write greening.
- Foundation protocol merge: **ACCEPT**; advisories remain (multi-root mapping before embed creates; prune prepared tickets).
- Parent Grok IR @ `e8a1f9c` (this pass): root fail-closed **ACCEPT / PASS**; product completeness **FAIL**; Wave-5a **not delivered**; no false greens; docs fingerprint match.
- No REQUIRED rewrite of Wave-4 reads or freeze wiki.
- Before greening any Wave-5a row: multi-root mapping if embeds claim full roots, paired tools, preview non-mutation, ticket matrix, exact body capture, registration, offline evidence only; live stays false.

## Next implementation slice (for Codex Power)

1. Review the active Wave-5a Codex Power leaves; reject seed-only merges and merge only verified scoped product deliveries.
2. Protocol multi-root response mapping leaf, then catalog/contact/contact_person/daybook write leaves (30 tools).
3. Root wires one `ConfirmationStore` + `WriteProtocolService`, registers 30 tools → 124 `api_*` + 2 coverage; offline-green only 15 write rows.
4. Independent Grok product review of integrated Wave-5a.
5. Later: live token, bulk, specials, auth, UI/vision.

## Research notes (durable)

- Official docs fingerprint still `hsisik4g9p3603` / `c2efda0ee4cf9cf200e14910c5fc6996`.
- Unauth DELETE empty 200 confirmed on products, productPrices, contacts, contactPersons, daybooks.
- Contact property table on **current** docs uses `paymentTermsDays` (required note) and `locale` belongs-to; ignore historical `paymentTermsValue` / `localeId` / `brand`.
- Product create sample embeds `prices[]` with `unitPrice` + `currencyId` (clear embed, not bulk).
- ContactPersons: either name or email; notes mark name required — leave XOR to live.
- productPrices page text swaps unitPrice/currency descriptions; requiredness still clear.

## References

- Research: `.fractal/main.billy_complete/tmp/grok-research.md`
- Review: `.fractal/main.billy_complete/tmp/grok-review.md`
- Wiki: `wiki/wave_five_ticketed_writes_contract.md`, `wiki/wave_five_write_protocol_independent_review.md`, `wiki/wave_four_root_integration_independent_review.md`
