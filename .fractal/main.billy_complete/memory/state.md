---
name: state
desc: Current node state, verified review decisions, and open qualification work.
tags: [billy, coverage, review]
sources:
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
  - https://www.billy.dk/api/
created: 2026-07-29T12:12:38Z
updated: 2026-07-29T16:43:00Z
---

# state

## Current state

- Root includes Wave-5a registration merge and independent ACCEPT review.
- Runtime: **142** `api_*` + 2 coverage; shared ConfirmationStore + WriteProtocolService; 24 preview + 24 execute writes.
- Coverage: implemented 118, contract_tested 118, live 0, vision 0, `complete: false`. Docs fingerprint unchanged.
- Wave-5a registration product: **ACCEPT** offline; overall product completeness still **FAIL**.
- Wave-5b **contract freeze**: wiki `wave_fiveb_ticketed_writes_contract.md` independently **ACCEPT**ed; product is integrated on root and pending a separate Grok product review.
- Wave-5b account and daybook-balance-account leaves were merged and their child seed directories cleaned from root; the retained product modules are `account_writes.py` and `daybook_balance_account_writes.py` with their contract suites.
- Wave-5c **research freeze** ready: daybookTransactions + daybookTransactionLines (6 CUD / 12 tools). Cited brief in node tmp; do not implement until Wave-5b product ACCEPT.
- Generated coverage prose matches the current offline API read-and-write phase; regeneration preserved all fail-closed row states.
- UI all red; bulk 92 empty-tool red; four specials red; no live token.

## Review decisions (authoritative)

- Catalog/daybook tips: **ACCEPT** selective merge (prior).
- Root registration **baseline** (pre-integration): ACCEPT honesty / FAIL product (`wiki/wave_fivea_root_registration_baseline_review.md`).
- Integrated registration product: **ACCEPT** offline (`wiki/wave_fivea_registration_independent_review.md`).
- Wave-5b freeze: **ACCEPT** (`.fractal/main.billy_complete/tmp/grok-review.md`); root product review pending separate Grok review.
- Wave-5c contract: researched and ready; product blocked on Wave-5b close.
- Overall completeness: **FAIL** until live, bulk, remaining writes, specials, UI/vision close red rows.

## Wave-5b contract freeze

- Official docs: etag `hsisik4g9p3603`, MD5 `c2efda0ee4cf9cf200e14910c5fc6996`, 147934 bytes (unchanged).
- Nine clear CUD rows: accountGroups, accounts, daybookBalanceAccounts → 18 tools → **142** api_* / **118** offline rows on root.
- Live unauth: Wave-5b POST 401; accountGroups PUT/GET-id 404 quirk; DELETE empty 200 not cleanup.
- accountNatures and postings CUD unauth **405** despite docs Supports write; out of 5b; stay red.
- Durable freeze: `wiki/wave_fiveb_ticketed_writes_contract.md`.

## Wave-5c research (next product after 5b)

- Six clear CUD rows: daybookTransactions, daybookTransactionLines → 12 tools → 154 api_* / 124 offline after 5b+5c.
- Live unauth this pass: POST/PUT 401; DELETE empty 200; GET-id 404; OPTIONS 204 with CORS Allow including PATCH (not a clear PATCH license).
- Create docs require at least one embedded line; line fields mostly immutable; state enum draft/approved/voided for live only.
- Explicit non-goals: invoices/bills, attachments/files special, ledger `transactions` CUD (readonly property table), postings/natures, bulk, UI.
- Research brief: `.fractal/main.billy_complete/tmp/grok-research.md`.
- Probe artifact: `.fractal/main.billy_complete/tmp/write-probes-research19.json`.

## Next work

1. Complete the independent Grok review of the integrated Wave-5b root product; resolve any finding before advancing the scope.
2. Promote Wave-5c brief to wiki freeze; implement 12 daybook-transaction write tools only after Wave-5b product ACCEPT; register to 154; offline 124; Grok product review.
3. Remaining clear writes (invoices/bills first), specials, bulk (live only), UI/auth/vision, live qualification.

## Evidence boundaries

- Official API fingerprint: etag `hsisik4g9p3603`, MD5 `c2efda0ee4cf9cf200e14910c5fc6996`.
- Focused offline write/coverage suite: **128** passed at registration review.
- Root non-live/non-vision suite: **644** passed with coverage and repository-policy checks after Wave-5b integration.
- Unauth DELETE empty 200 is not cleanup proof.
- Unauth natures/postings 405 is not a green reclassification by itself.
- Research does not green coverage rows.

## References

- Review: `.fractal/main.billy_complete/tmp/grok-review.md`
- Wiki: `wiki/wave_fivea_registration_independent_review.md`
- Research (Wave-5c): `.fractal/main.billy_complete/tmp/grok-research.md`
- Freeze 5b: `wiki/wave_fiveb_ticketed_writes_contract.md`
- Freeze 5a: `wiki/wave_five_ticketed_writes_contract.md`
