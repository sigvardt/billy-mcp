---
name: state
desc: Current node state, verified review decisions, and open qualification work.
tags: [billy, coverage, review]
sources:
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
  - https://www.billy.dk/api/
created: 2026-07-29T12:12:38Z
updated: 2026-07-29T16:22:40Z
---

# state

## Current state

- Root includes Wave-5a registration merge and independent ACCEPT review.
- Runtime: **124** `api_*` + 2 coverage; shared ConfirmationStore + WriteProtocolService; 15 preview + 15 execute writes.
- Coverage: implemented 109, contract_tested 109, live 0, vision 0, `complete: false`. Docs fingerprint unchanged.
- Wave-5a registration product: **ACCEPT** offline; overall product completeness still **FAIL**.
- Wave-5b **contract freeze**: wiki `wave_fiveb_ticketed_writes_contract.md` independently **ACCEPT**ed; product not on root.
- Wave-5b implementation children active: `wave5b_account_writes`, `wave5b_daybook_balance_writes` (Codex Power).
- Generated coverage prose matches the current offline API read-and-write phase; regeneration preserved all fail-closed row states.
- UI all red; bulk 92 empty-tool red; four specials red; no live token.

## Review decisions (authoritative)

- Catalog/daybook tips: **ACCEPT** selective merge (prior).
- Root registration **baseline** (pre-integration): ACCEPT honesty / FAIL product (`wiki/wave_fivea_root_registration_baseline_review.md`).
- Integrated registration product: **ACCEPT** offline (`wiki/wave_fivea_registration_independent_review.md`).
- Wave-5b freeze: **ACCEPT** (`.fractal/main.billy_complete/tmp/grok-review.md`); Wave-5b product pending separate review.
- Overall completeness: **FAIL** until live, bulk, remaining writes, specials, UI/vision close red rows.

## Wave-5b contract freeze

- Official docs: etag `hsisik4g9p3603`, MD5 `c2efda0ee4cf9cf200e14910c5fc6996`, 147934 bytes (unchanged).
- Nine clear CUD rows: accountGroups, accounts, daybookBalanceAccounts → 18 tools → 142 api_* / 118 offline rows.
- Live unauth: Wave-5b POST 401; accountGroups PUT/GET-id 404 quirk; DELETE empty 200 not cleanup.
- accountNatures and postings CUD unauth **405** despite docs Supports write; out of 5b; stay red.
- Durable freeze: `wiki/wave_fiveb_ticketed_writes_contract.md`.
- Research: `.fractal/main.billy_complete/tmp/grok-research.md`.

## Next work

1. Merge Wave-5b leaves when complete; root-register 18 tools; regenerate coverage to 118 offline; Grok product review.
2. Remaining clear writes, specials, bulk (live only), UI/auth/vision, live qualification.

## Evidence boundaries

- Official API fingerprint: etag `hsisik4g9p3603`, MD5 `c2efda0ee4cf9cf200e14910c5fc6996`.
- Focused offline write/coverage suite: **128** passed at registration review.
- Root non-live/non-vision suite: **593** passed with coverage and repository-policy checks.
- Unauth DELETE empty 200 is not cleanup proof.
- Unauth natures/postings 405 is not a green reclassification by itself.
- The freeze review's coverage-report title finding was fixed without changing manifest or status qualification.

## References

- Review: `.fractal/main.billy_complete/tmp/grok-review.md`
- Wiki: `wiki/wave_fivea_registration_independent_review.md`
- Research (Wave-5b): `.fractal/main.billy_complete/tmp/grok-research.md`
- Freeze: `wiki/wave_five_ticketed_writes_contract.md`
