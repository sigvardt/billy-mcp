---
name: state
desc: Current node state, verified review decisions, and open qualification work.
tags: [billy, coverage, review]
sources:
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
  - https://www.billy.dk/api/
created: 2026-07-29T12:12:38Z
updated: 2026-07-29T15:31:22Z
---

# state

## Current state

- Root product surface: **94** real `api_*` tools + 2 `coverage_*` at runtime. Write modules on root: protocol multi-root, contacts, contact persons, catalog, and daybooks. **No write tools registered** in `create_server`.
- Static AST under `src/` already names **124** `api_*` tools (30 write preview/execute strings in leaf modules). Coverage checker allows them via inventory previews + execute-twin gate. **Offline greening still requires evidence map entries.**
- Clear resource get/list offline: **92/92** implemented and contract_tested.
- Specials offline-green: `api.special.user_get`, `api.special.user_organizations` only (4 specials remain red).
- Coverage: implemented 94, contract_tested 94, live_tested 0, vision 0, `complete: false`.
- Official docs fingerprint unchanged (etag `hsisik4g9p3603`, MD5 `c2efda0ee4cf9cf200e14910c5fc6996`).
- UI discovery still unauthenticated login only; all 339 UI rows red.
- `BILLY_API_TOKEN` unavailable; no live qualification claimed.
- Wave-5 contract freeze binding. Execute-twin coverage gate present.

## Wave-5a status

- Catalog tip `ba4101a` / daybook tip `0d4b0e5`: **ACCEPT** selective product/test merge (done).
- Protocol + contacts + contact persons: **ACCEPT** and merged earlier.
- Independent reviews: `wiki/wave_fivea_catalog_daybook_independent_review.md`, `wiki/wave_fivea_candidate_independent_review.md`.
- Next slice: **root registration** of all 30 write tools; green only 15 offline inventory rows; keep live false.

## Evidence boundaries

- Official API: https://www.billy.dk/api/ fingerprint above.
- 207 clear / 92 bulk / 6 specials → 305 API; 339 UI; 0 webhooks.
- Unauth DELETE empty 200 is not cleanup proof. Bulk unproven.
- Remaining red API work after this registration: ~101 clear singular writes, 92 bulk, four specials (plus live for everything).

## Review decisions

- Wave-4 offline integration: **ACCEPT** slice; **FAIL** product completeness.
- Wave-5 contract freeze: **ACCEPT** honesty; no write greening.
- Foundation protocol merge: **ACCEPT**.
- Wave-5a protocol/contacts/contact persons: **ACCEPT**.
- Wave-5a catalog + daybook tips: **ACCEPT** selective merge.
- Root fail-closed **ACCEPT / PASS**; product completeness **FAIL** until registration + review.

## Next implementation slice (for Codex Power)

1. `create_server`: one `ConfirmationStore` + one `WriteProtocolService`; register contacts, contact persons, catalog, daybooks (30 tools).
2. `OFFLINE_API_IMPLEMENTATION_EVIDENCE` for the 15 Wave-5a CUD inventory ids with focused write tests + `tests/unit/test_coverage_server.py`.
3. Regenerate coverage; expect implemented/contract_tested **109**, live **0**, complete **false**.
4. Update server registry test: **124** `api_*` tools.
5. Independent Grok product review after integrated registration.

## Research notes (durable)

- Docs fingerprint still `hsisik4g9p3603` / `c2efda0ee4cf9cf200e14910c5fc6996` (research16 re-fetch identical to research15).
- Unauth DELETE empty 200 on products, productPrices, contacts, contactPersons, daybooks.
- Product create sample embeds `prices[]` with `unitPrice` + `currencyId`; product ops use `additional_plural_roots=("productPrices",)`.
- Multi-word singular roots use Billy camelCase on MCP surface (`contactPerson`, `productPrice`).
- Greening path is only `OFFLINE_API_IMPLEMENTATION_EVIDENCE` in `scripts/generate_coverage_report.py`, not AST presence alone.
- 46 resources × bulk save/delete = 92 bulk rows; no body contract.

## References

- Research: `.fractal/main.billy_complete/tmp/grok-research.md`
- Wiki: `wiki/wave_fivea_catalog_daybook_independent_review.md`, `wiki/wave_fivea_candidate_independent_review.md`, `wiki/wave_five_ticketed_writes_contract.md`
