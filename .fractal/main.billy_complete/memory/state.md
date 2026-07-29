---
name: state
desc: Current node state, verified review decisions, and open qualification work.
tags: [billy, coverage, review]
sources:
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
  - https://www.billy.dk/api/
created: 2026-07-29T12:12:38Z
updated: 2026-07-29T12:35:00Z
---

# state

## Current state

- Wave-1 through Wave-3 offline reads are on root: **44** real `api_*` tools +
  2 `coverage_*`. Status: 44 implemented/contract_tested, 0 live_tested,
  complete false.
- Wave-4 first cohort is **merged as source** (geo 8, tax 16, bank 10) with
  focused contract tests, but **not registered** and **not greened**. Root
  product surface still 44 offline tools.
- Second-cohort leaves active: balance/invoice-ext (10) and ledger/users (6).
- Official docs fingerprint unchanged.
- UI discovery still unauthenticated login only; all UI rows red.
- `BILLY_API_TOKEN` unavailable; full mode fails closed (438 offline pass, then
  completeness gate fails).
- Root lint, coverage-inventory, policy checks, and the 438-test non-live
  suite pass after the first-cohort merge; the three first-cohort modules also
  pass 213 focused tests when run together.

## Evidence boundaries

- Official API fingerprint: ETag `hsisik4g9p3603`, 147934 bytes, MD5
  `c2efda0ee4cf9cf200e14910c5fc6996` (https://www.billy.dk/api/).
- 46 resources, 207 clear ops, 92 bulk ambiguous, 6 specials; 0 webhooks.
- Documented list filter tables only for invoices, bills, daybookTransactions.
- Live unauth: cities/states/zipcodes require `countryId`; countryGroups public;
  unauth `GET /user/organizations` returns 404 (docs path kept offline until
  authenticated live proof).
- Remaining clear red: 165 (50 get/list + 115 writes). Specials red except user
  get/organizations.

## Review decisions

- Independent review (first-cohort merge): **FAIL** product completeness;
  **ACCEPT** anti-false-green and first-cohort module quality; **FAIL** root
  wiring of Wave-4 (expected integration gap, not false green).
- No REQUIRED rewrites of geo/tax/bank modules from that review.
- The review's 46-tool registry reproduction (44 `api_*`, two `coverage_*`)
  confirms that the missing Wave-4 registration/evidence is a real pending
  integration task, not an incorrect review finding.
- Accepted: inventory arithmetic matches official Supports.
- Accepted for Wave-4: require `countryId` on cities/states/zipcodes lists from
  live evidence; do not invent other resource filters offline.
- Rejected as complete: product completeness, live, UI/vision, auth product
  tools, bulk resolution, unregistered Wave-4 greening.
- Child delivery branches can include generated `.fractal/<child>` runtime
  artifacts; merge product archive only, prune seed dirs before root verify.

## Next implementation slice (for Codex Power)

1. Finish and merge second-cohort leaves (16 tools).
2. Root integration: register all 50 Wave-4 tools + offline evidence → **94**
   `api_*` + 2 `coverage_*`; complete stays false; live_tested stays false.
3. When token exists: live-test offline-green reads (include authenticated
   `/user/organizations`); bulk probes; ticketed writes.
4. Authenticated UI only with credentials + DOM + read-back + vision + purge.

## References

- Research: `.fractal/main.billy_complete/tmp/grok-research.md`
- Review: `.fractal/main.billy_complete/tmp/grok-review.md`
- Wiki: `wiki/wave_four_first_cohort_independent_review.md`,
  `wiki/wave_four_remaining_clear_reads_contract.md`,
  `wiki/wave_four_freeze_independent_review.md`,
  `wiki/wave_three_envelope_rereview.md`
