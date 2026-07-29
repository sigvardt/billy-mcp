---
name: state
desc: Current node state, verified review decisions, and open qualification work.
tags: [billy, coverage, review]
sources:
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
  - https://www.billy.dk/api/
created: 2026-07-29T12:12:38Z
updated: 2026-07-29T12:44:00Z
---

# state

## Current state

- Wave-1 through Wave-3 offline reads are registered on root: **44** real
  `api_*` tools + 2 `coverage_*`. Status: 44 implemented/contract_tested,
  0 live_tested, complete false.
- Wave-4's fifty clear get/list tools are merged and registered: geo (8), tax
  (16), bank (10), balance/invoice extension (10), and ledger/users (6). Root
  now exposes **94** real `api_*` tools plus 2 `coverage_*` tools.
- Generated coverage has exactly 94 API rows marked `implemented` and
  `contract_tested`; every API `live_tested` flag remains false and
  `complete` remains false.
- Official docs fingerprint unchanged (etag `hsisik4g9p3603`, MD5
  `c2efda0ee4cf9cf200e14910c5fc6996`).
- UI discovery still unauthenticated login only; all UI rows red.
- `BILLY_API_TOKEN` unavailable; full mode fails closed. The post-integration
  focused suite covers 275 tests; complete non-live verification remains due.

## Evidence boundaries

- Official API fingerprint: ETag `hsisik4g9p3603`, 147934 bytes, MD5
  `c2efda0ee4cf9cf200e14910c5fc6996` (https://www.billy.dk/api/).
- 46 resources, 207 clear ops, 92 bulk ambiguous, 6 specials; 0 webhooks.
- Documented list filter tables only for invoices, bills, daybookTransactions.
- Live unauth: cities/states/zipcodes require `countryId`; countryGroups public
  (list + get `/countryGroups/eu` → root `countryGroup`); unauth
  `GET /user/organizations` returns 404 (docs path kept offline until
  authenticated live proof).
- Live unauth: org-scoped **get-by-id** often returns **404 RECORD_NOT_FOUND**
  without a token while **lists** return **401 AUTHENTICATION_REQUIRED**.
- Remaining clear red: 50 get/list (Wave-4) + all writes. Specials red except
  user get/organizations.

## Review decisions

- Independent review (first-cohort merge): **FAIL** product completeness;
  **ACCEPT** anti-false-green and first-cohort module quality; **FAIL** root
  wiring of Wave-4 (expected integration gap, not false green).
- No REQUIRED rewrites of geo/tax/bank modules from that review.
- Accepted: inventory arithmetic matches official Supports.
- Accepted for Wave-4: require `countryId` on cities/states/zipcodes lists from
  live evidence; do not invent other resource filters offline.
- Rejected as complete: product completeness, live, UI/vision, auth product
  tools, bulk resolution, unregistered Wave-4 greening.
- Child delivery branches can include generated `.fractal/<child>` runtime
  artifacts; merge product archive only, prune seed dirs before root verify.

## Next implementation slice (for Codex Power)

1. Run complete non-live and expected-fail full gates, then request an
   independent Grok review of the registered 94-tool offline surface.
2. Map `RECORD_NOT_FOUND` on get tools (live unauth matrix); keep 401 on lists.
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
