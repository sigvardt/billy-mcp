---
name: state
desc: Current node state, verified review decisions, and open qualification work.
tags: [billy, coverage, review]
sources:
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
  - https://www.billy.dk/api/
created: 2026-07-29T12:12:38Z
updated: 2026-07-29T13:02:00Z
---

# state

## Current state

- Root product surface: **94** real `api_*` tools + 2 `coverage_*`.
- Clear resource get/list offline: **92/92** implemented and contract_tested.
- Specials offline-green: `api.special.user_get`, `api.special.user_organizations`
  only (4 specials remain red).
- Coverage: implemented 94, contract_tested 94, live_tested 0, vision 0,
  `complete: false`.
- Offline suite: **487** passed (`not live and not vision`). Full mode fails
  only at completeness gate (expected).
- Official docs fingerprint unchanged (etag `hsisik4g9p3603`, MD5
  `c2efda0ee4cf9cf200e14910c5fc6996`).
- UI discovery still unauthenticated login only; all 339 UI rows red.
- `BILLY_API_TOKEN` unavailable; no live qualification claimed.

## Evidence boundaries

- Official API: https://www.billy.dk/api/ fingerprint above.
- 46 resources, 207 clear ops, 92 bulk ambiguous, 6 specials; 0 webhooks.
- Documented list filter tables only for invoices, bills, daybookTransactions.
- Live unauth: cities/states/zipcodes require `countryId`; countryGroups public;
  unauth `GET /user/organizations` returns 404 (docs path kept offline until
  authenticated live proof); org-scoped get-by-id often 404 without token while
  lists return 401.
- Remaining red API work: all clear writes, all bulk, four specials (upload,
  invoice email/delivery/logs).

## Review decisions

- Independent review of Wave-4 offline integration (`3f56399`): **ACCEPT**
  slice quality and anti-false-green; **FAIL** product completeness.
- No REQUIRED rewrites of geo/tax/bank/balance/ledger read modules.
- Rejected as complete: live, UI/vision, auth product tools, bulk resolution,
  write tools, full-mode completeness.
- Optional polish only: explicit 404 contract fixtures on Wave-4 gets (client
  already maps 404 → NOT_FOUND).

## Next implementation slice (for Codex Power)

1. Obtain non-production `BILLY_API_TOKEN`; live-test offline-green reads
   including authenticated `/user/organizations`.
2. Bulk probes from live/official evidence; never invent bulk bodies offline.
3. Ticketed writes (preview + single-use execute) for clear create/update/delete.
4. Remaining specials; `auth_*` product tools; authenticated UI + vision + purge.
5. Only then drive `complete: true` and full suite green.

## References

- Research: `.fractal/main.billy_complete/tmp/grok-research.md`
- Review: `.fractal/main.billy_complete/tmp/grok-review.md`
- Wiki: `wiki/wave_four_remaining_clear_reads_contract.md`,
  `wiki/wave_four_first_cohort_independent_review.md`,
  `wiki/billy_ui_discovery_brief.md`
