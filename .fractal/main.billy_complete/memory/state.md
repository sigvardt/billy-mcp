---
name: state
desc: Current node state, verified review decisions, and open qualification work.
tags: [billy, coverage, review]
sources:
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
  - https://www.billy.dk/api/
created: 2026-07-29T22:11:45Z
updated: 2026-07-29T23:00:00Z
---

# state

## Current state

- Wave-5c through Wave-5g write modules are merged into root; root registration uses the one shared `ConfirmationStore` and `WriteProtocolService`.
- Root merge **`55faa02`** integrates Wave-5g product **`e6f96e7`**: **202** `api_*` + 2 coverage tools; twelve ticketed sales-tax ruleset/rule write tools. Offline product **ACCEPT** at `wiki/wave_fiveg_product_independent_review.md`. Acceptance recorded at **`71492f1`**. Smoke re-check at review: 44 offline product tests pass; registry still 202.
- Wave-5g freeze remains **`5612aa8`** (`wiki/wave_fiveg_ticketed_writes_contract.md`); freeze ACCEPT at `wiki/wave_fiveg_freeze_independent_review.md`.
- Wave-5h freeze-ready research at scratch `tmp/grok-research.md` (research34) is independently **ACCEPT** as freeze-writing handoff only (`wiki/wave_fiveh_freeze_ready_research_independent_review.md`). Freeze page not written; no attachment write module; attachment CUD rows still red.
- Research and probe policy commit **`fc4743a`**. Review findings: `tmp/grok-review.md`.
- Root non-live verification after the durable review record passes formatting,
  Ruff, Pyright, coverage and repository-policy checks, and all 892 tests. No
  live call or browser evidence was produced.
- Coverage: implemented 148, contract_tested 148, live 0, vision 0, `complete: false`. Clear red CUD: 61.
- Official docs fingerprint still etag `hsisik4g9p3603`, MD5 `c2efda0ee4cf9cf200e14910c5fc6996` (body 147934 bytes). Review re-fetch matches.
- Wave-5f product at root merge **`353449d`**: **ACCEPT** offline (`wiki/wave_fivef_product_independent_review.md`).
- UI all red; bulk 92 empty-tool red; four specials red; no live token in process env.
- Historical unmerged review leaves remain intentionally closed rather than merged. Codex fallback review leaves do not replace Grok product ACCEPT.

## Review decisions (authoritative)

- Wave-5a integrated product: **ACCEPT** offline.
- Wave-5b freeze: **ACCEPT**.
- Wave-5b product at `920ceab`: **REJECTED**.
- Wave-5b repair at `a2a0996`: **ACCEPT** offline.
- Wave-5c freeze: **ACCEPT** offline contract only.
- Wave-5c product at tip `f235ac2`: **ACCEPT** offline by independent Grok audit.
- Wave-5d freeze at tip `5c376de`: **ACCEPT** offline contract only.
- Wave-5d product at tip `1108e2f`: **ACCEPT** offline by independent Grok.
- Wave-5e freeze at `fc8118e`: **ACCEPT** offline by the authoritative root Grok independent review.
- Wave-5e product at tip `15d0bde`: **ACCEPT** offline by independent Grok.
- Wave-5f freeze at tip `d412e8c`: **ACCEPT** offline by the authoritative root Grok independent review.
- Wave-5f product-ready research at tip `1c9e6cb`: **ACCEPT** offline as implementation handoff only.
- Wave-5f product at root merge `353449d`: **ACCEPT** offline by independent Grok.
- Wave-5g freeze at tip `5612aa8`: **ACCEPT** offline by the authoritative root Grok independent review.
- Wave-5g product-ready research: **ACCEPT** offline as implementation handoff only.
- Wave-5g product at root merge `55faa02`: **ACCEPT** offline by independent Grok (`wiki/wave_fiveg_product_independent_review.md`).
- Wave-5h freeze-ready research (research34 at `fc4743a`): **ACCEPT** offline as freeze-writing handoff only (`wiki/wave_fiveh_freeze_ready_research_independent_review.md`).
- Wave-5h freeze: **not written**.
- Wave-5h product: **not implemented**.
- Overall completeness: **FAIL** until live, bulk, remaining writes, specials, UI/vision close red rows.

## Open coverage work

1. Freeze Wave-5h attachments singular CUD from accepted research §4 into `wiki/wave_fiveh_ticketed_writes_contract.md`; independent freeze review; product (+6 tools → 208; coverage 151).
2. Freeze Wave-5i salesTaxAccounts + salesTaxMetaFields CUD; product (+12 tools → 220; coverage 157).
3. Later full CUD (probe-open): bankLineMatches, bankLines, bankLineSubjectAssociations (dedicated research depth required for embedded replace semantics).
4. Later partial CUD: salesTaxPayments create/update, salesTaxReturns update, bankPayments create/update, contactBalancePayments create/update, invoiceLateFees create/update, invoiceReminders create, organizations create/update, users update.
5. Specials: binary files upload, invoice email/delivery/logs.
6. Bulk (live only), UI/auth/vision.
7. Blocked offline without more evidence: `accountNatures`, `postings`, `balanceModifiers`, `contactBalancePostings`, geo reference CUD (all unauth 405), `bankPayments`/`salesTaxPayments` delete (405), `transactions` CUD (all-readonly property table), `invoiceReminderAssociations` create/update (405).

## Evidence boundaries

- Official API fingerprint: etag `hsisik4g9p3603`, MD5 `c2efda0ee4cf9cf200e14910c5fc6996`.
- Product ACCEPT is offline only; no live/UI/bulk/completeness claim.
- Unauth DELETE empty 200 is not cleanup proof.
- Unauth METHOD_NOT_ALLOWED 405 overrides Supports-flag optimism for offline green paths.

## References

- Review (scratch): `.fractal/main.billy_complete/tmp/grok-review.md`
- Research Wave-5h (scratch): `.fractal/main.billy_complete/tmp/grok-research.md`
- Wiki research ACCEPT 5h: `wiki/wave_fiveh_freeze_ready_research_independent_review.md`
- Wiki product ACCEPT 5g: `wiki/wave_fiveg_product_independent_review.md`
- Wiki freeze 5g: `wiki/wave_fiveg_ticketed_writes_contract.md`
- Wiki freeze ACCEPT 5g: `wiki/wave_fiveg_freeze_independent_review.md`
- Wiki offline probe policy: `wiki/offline_write_probe_rules.md`
