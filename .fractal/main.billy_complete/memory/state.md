---
name: state
desc: Current node state, verified review decisions, and open qualification work.
tags: [billy, coverage, review]
sources:
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
  - https://www.billy.dk/api/
created: 2026-07-29T12:12:38Z
updated: 2026-07-29T16:12:51Z
---

# state

## Current state

- Root includes Wave-5a registration merge and independent ACCEPT review.
- Runtime: **124** `api_*` + 2 coverage; shared ConfirmationStore + WriteProtocolService; 15 preview + 15 execute writes.
- Coverage: implemented 109, contract_tested 109, live 0, vision 0, `complete: false`. Docs fingerprint unchanged.
- Wave-5a registration product: **ACCEPT** offline; overall product completeness still **FAIL**.
- Wave-5b research brief re-verified and **implementation-ready** (prerequisite gate closed).
- UI all red; bulk 92 empty-tool red; four specials red; no live token.

## Review decisions (authoritative)

- Catalog/daybook tips: **ACCEPT** selective merge (prior).
- Root registration **baseline** (pre-integration): ACCEPT honesty / FAIL product (`wiki/wave_fivea_root_registration_baseline_review.md`).
- Integrated registration product: **ACCEPT** offline (`wiki/wave_fivea_registration_independent_review.md`).
- Overall completeness: **FAIL** until live, bulk, remaining writes, specials, UI/vision close red rows.

## Wave-5b contract freeze (research)

- Official docs: etag `hsisik4g9p3603`, MD5 `c2efda0ee4cf9cf200e14910c5fc6996`, 147934 bytes (unchanged).
- Nine clear CUD rows: accountGroups, accounts, daybookBalanceAccounts → 18 tools → 142 api_* / 118 offline rows.
- Live unauth: Wave-5b POST 401; accountGroups PUT/GET-id 404 quirk; DELETE empty 200 not cleanup.
- **New:** accountNatures and postings POST/PUT/DELETE unauth **405** despite docs Supports write; out of 5b; stay red.
- Full cited brief: `.fractal/main.billy_complete/tmp/grok-research.md`.

## Next work

1. Implement Wave-5b (accountGroups, accounts, daybookBalanceAccounts) offline ticketed writes per research brief.
2. Remaining clear writes, specials, bulk (live only), UI/auth/vision, live qualification.

## Evidence boundaries

- Official API fingerprint: etag `hsisik4g9p3603`, MD5 `c2efda0ee4cf9cf200e14910c5fc6996`.
- Focused offline write/coverage suite: **128** passed at registration review.
- Root non-live/non-vision suite: **593** passed with coverage and repository-policy checks.
- Unauth DELETE empty 200 is not cleanup proof.
- Unauth natures/postings 405 is not a green reclassification by itself.

## References

- Review: `.fractal/main.billy_complete/tmp/grok-review.md`
- Wiki: `wiki/wave_fivea_registration_independent_review.md`
- Research (Wave-5b): `.fractal/main.billy_complete/tmp/grok-research.md`
- Freeze: `wiki/wave_five_ticketed_writes_contract.md`
