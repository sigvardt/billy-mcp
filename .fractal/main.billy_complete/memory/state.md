---
name: state
desc: Current node state, verified review decisions, and open qualification work.
tags: [billy, coverage, review]
sources:
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
  - https://www.billy.dk/api/
created: 2026-07-29T12:12:38Z
updated: 2026-07-29T12:20:00Z
---

# state

## Current state

- Wave-1 through Wave-3 offline reads are on root: **44** real `api_*` tools +
  2 `coverage_*`. Status: 44 implemented/contract_tested, 0 live_tested,
  complete false.
- Wave-4 freeze remains valid after docs re-fetch: all **50** remaining clear
  get/list operations cited in `tmp/grok-research.md` and
  `wiki/wave_four_remaining_clear_reads_contract.md`.
- Official docs fingerprint unchanged.
- First-cohort Wave-4 leaves active (geo/tax/bank) with module files present in
  child worktrees; not merged to root. Second cohort not started.
- UI discovery still unauthenticated login only; all UI rows red.
- `BILLY_API_TOKEN` unavailable; full mode fails closed after the offline suite
  passes.

## Evidence boundaries

- Official API fingerprint: ETag `hsisik4g9p3603`, 147934 bytes, MD5
  `c2efda0ee4cf9cf200e14910c5fc6996` (https://www.billy.dk/api/).
- 46 resources, 207 clear ops, 92 bulk ambiguous, 6 specials; 0 webhooks.
- Documented list filter tables only for invoices, bills, daybookTransactions.
- **Live (unauth):** cities/states/zipcodes require `countryId` (400 OTHER
  without it). countryGroups public 200. Most other Wave-4 lists return 401
  AUTHENTICATION_REQUIRED. **New:** unauth `GET /user/organizations` returns
  404 UNKNOWN_RESOURCE while unauth `GET /user` returns 401; official path
  kept for the offline special until authenticated live proof.
- Wave-3 offline greens remain; remaining clear red: 165 (50 get/list + 115
  writes). Specials red except user get/organizations.

## Review decisions

- Independent review: **FAIL** product completeness; **ACCEPT** offline
  Wave-1–3 quality, anti-false-green, and the Wave-4 freeze (geo countryId
  inventory without greening).
- Accepted: inventory arithmetic still matches official Supports.
- Accepted for Wave-4: require `countryId` on cities/states/zipcodes lists from
  live evidence; do not invent other resource filters offline.
- Rejected as complete: product completeness, live, UI/vision, auth product
  tools, bulk resolution.
- Do not rewrite `api_user_list_organizations` from unauth 404 alone.

## Next implementation slice (for Codex Power)

1. Finish first-cohort Wave-4 leaves (geo/tax/bank); merge clean deliveries.
2. Start second-cohort leaves: balance/invoice-ext (10 tools) and
   ledger/users (6 tools) per research brief property tables.
3. Root integration: register 50 tools → **94** `api_*` + 2 `coverage_*`;
   complete stays false; live_tested stays false.
4. When token exists: live-test offline-green reads (include authenticated
   `/user/organizations`); bulk probes; ticketed writes; never invent bulk
   bodies.
5. Authenticated UI only with credentials + DOM + read-back + vision + purge.

## References

- Research: `.fractal/main.billy_complete/tmp/grok-research.md`
- Review: `.fractal/main.billy_complete/tmp/grok-review.md`
- Wiki: `wiki/billy_api_v2_research_seed.md`, `wiki/billy_ui_discovery_brief.md`,
  `wiki/phase_zero_contract.md`, `wiki/wave_one_reads_contract.md`,
  `wiki/wave_two_filtered_reads_contract.md`,
  `wiki/wave_three_unfiltered_reads_contract.md`,
  `wiki/wave_four_remaining_clear_reads_contract.md`,
  `wiki/wave_four_freeze_independent_review.md`
