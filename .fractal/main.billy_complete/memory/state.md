---
name: state
desc: Current node state, verified review decisions, and open qualification work.
tags: [billy, coverage, review]
sources:
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
  - https://www.billy.dk/api/
created: 2026-07-29T12:12:38Z
updated: 2026-07-29T16:05:00Z
---

# state

## Current state

- Root includes Wave-5a registration merge (`45f099f` / `7cb74e2`).
- Runtime: **124** `api_*` + 2 coverage; shared ConfirmationStore + WriteProtocolService; 15 preview + 15 execute writes.
- Coverage: implemented 109, contract_tested 109, live 0, vision 0, `complete: false`. Docs fingerprint unchanged.
- Independent Grok product review of registration: **ACCEPT** offline Wave-5a; overall product completeness still **FAIL**.
- Wave-5b research brief ready; no Wave-5b product green yet.
- UI all red; bulk 92 empty-tool red; four specials red; no live token.
- The duplicate `wave5a_registration_review` child was intentionally closed
  after the root Grok review record was published; it produced no project
  deliverable.

## Review decisions (authoritative)

- Catalog/daybook tips: **ACCEPT** selective merge (prior).
- Root registration **baseline** (pre-integration): ACCEPT honesty / FAIL product (`wiki/wave_fivea_root_registration_baseline_review.md`).
- Integrated registration product: **ACCEPT** offline (`wiki/wave_fivea_registration_independent_review.md`, `tmp/grok-review.md`).
- Overall completeness: **FAIL** until live, bulk, remaining writes, specials, UI/vision close red rows.

## Next work

1. Implement Wave-5b (accountGroups, accounts, daybookBalanceAccounts) offline ticketed writes per research brief.
2. Remaining clear writes, specials, bulk (live only), UI/auth/vision, live qualification.

## Evidence boundaries

- Official API fingerprint: etag `hsisik4g9p3603`, MD5 `c2efda0ee4cf9cf200e14910c5fc6996`.
- Focused offline write/coverage suite: **128** passed this review.
- Root non-live/non-vision suite: **593** passed with coverage and repository-policy checks.
- Unauth DELETE empty 200 is not cleanup proof.

## References

- Review: `.fractal/main.billy_complete/tmp/grok-review.md`
- Wiki: `wiki/wave_fivea_registration_independent_review.md`
- Research (Wave-5b): `.fractal/main.billy_complete/tmp/grok-research.md`
- Freeze: `wiki/wave_five_ticketed_writes_contract.md`
