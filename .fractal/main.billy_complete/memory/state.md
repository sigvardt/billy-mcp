---
name: state
desc: Current node state, verified review decisions, and open qualification work.
tags: [billy, coverage, review]
sources:
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
  - https://www.billy.dk/api/
created: 2026-07-29T12:12:38Z
updated: 2026-07-29T13:10:00Z
---

# state

## Current state

- Root product surface: **94** real `api_*` tools + 2 `coverage_*` (clear get/list offline complete).
- Clear resource get/list offline: **92/92** implemented and contract_tested.
- Specials offline-green: `api.special.user_get`, `api.special.user_organizations` only (4 specials remain red).
- Coverage: implemented 94, contract_tested 94, live_tested 0, vision 0, `complete: false`.
- Offline suite: **487** passed (`not live and not vision`). Full mode fails only at completeness gate (expected).
- Official docs fingerprint unchanged (etag `hsisik4g9p3603`, MD5 `c2efda0ee4cf9cf200e14910c5fc6996`).
- UI discovery still unauthenticated login only; all 339 UI rows red.
- `BILLY_API_TOKEN` unavailable; no live qualification claimed.
- Wave-4 root independent review: offline **PASS**, product incomplete (wiki record committed).

## Evidence boundaries

- Official API: https://www.billy.dk/api/ fingerprint above.
- 46 resources, 207 clear ops, 92 bulk ambiguous, 6 specials; 0 webhooks.
- Documented list filter tables only for invoices, bills, daybookTransactions.
- Live unauth: cities/states/zipcodes require `countryId`; countryGroups public; unauth `GET /user/organizations` returns 404 (docs path kept offline until authenticated live proof); org-scoped get-by-id often 404 without token while lists return 401.
- **Write probes (unauth):** POST/PUT → 401 AUTHENTICATION_REQUIRED; invalid token → OAUTH_INVALID_ACCESS_TOKEN; **DELETE → 200 empty success without deletedRecords** (idempotent; not cleanup proof). Bulk still unproven.
- Remaining red API work: 115 clear writes, 92 bulk, four specials (upload, invoice email/delivery/logs).

## Review decisions

- Independent review of Wave-4 offline integration: **ACCEPT** slice quality and anti-false-green; **FAIL** product completeness.
- No REQUIRED rewrites of geo/tax/bank/balance/ledger read modules.
- Rejected as complete: live, UI/vision, auth product tools, bulk resolution, write tools, full-mode completeness.

## Next implementation slice (for Codex Power)

Wave-5a ticketed clear writes (see research brief):

1. Shared write framework + wire `ConfirmationStore` into tools.
2. First cohort (15 inventory ops / 30 tools): products, productPrices, contacts, contactPersons, daybooks — preview + execute each.
3. Contract tests for ticket matrix, request construction, no preview mutation, 401/404 fixtures.
4. Offline-green only those 15 rows; live/UI/bulk/complete stay false.
5. Then expand writes; with token: live reads + writes + bulk probes; then specials, auth, UI/vision.

## References

- Research: `.fractal/main.billy_complete/tmp/grok-research.md`
- Review: wiki `wave_four_root_integration_independent_review.md`
- Wiki: `wiki/wave_four_remaining_clear_reads_contract.md`, `wiki/billy_ui_discovery_brief.md`, `wiki/billy_api_v2_research_seed.md`
