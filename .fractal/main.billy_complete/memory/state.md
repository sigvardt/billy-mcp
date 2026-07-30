---
name: state
desc: Current node state, verified review decisions, and open qualification work.
tags: [billy, coverage, review]
sources:
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
  - https://www.billy.dk/api/
created: 2026-07-29T22:11:45Z
updated: 2026-07-30T04:59:00Z
---

# state

## Current state

- Wave-5c through Wave-5j write modules are merged into root; root registration uses the one shared `ConfirmationStore` and `WriteProtocolService`.
- Wave-5j product is on root (`src/billy_mcp/api/bank_line_writes.py`). Registry **238** `api_*` tools. Offline coverage **166** implemented + contract_tested. Live/vision still 0. `complete: false`.
- Wave-5k freeze page is on root at `wiki/wave_fivek_ticketed_writes_contract.md`.
- **Wave-5k freeze independent Grok review: ACCEPT** at
  `wiki/wave_fivek_freeze_independent_review.md` (root independent review).
  Opens offline four-tool product leaf only.
- Codex Power fallback freeze page remains on root at
  `wiki/wave_fivek_freeze_codex_fallback_review.md` as non-authoritative record only.
- Wave-5k product module still **absent** (`src/billy_mcp/api/bank_payment_writes.py`).
- Coverage: implemented 166, contract_tested 166, live 0, vision 0, `complete: false`.
  Next offline greens after product: bankPayments create+update only (**+2 → 168**, tools **242**).
- UI all red; bulk 92 empty-tool red; no live token; no UI credentials.

## Verification

- Official docs retain ETag `hsisik4g9p3603`, MD5
  `c2efda0ee4cf9cf200e14910c5fc6996`, and a 147934-byte body.
- Unauth probes: bankPayments POST/PUT **401**; DELETE **405** singular-delete refusal.
- No false coverage greens; registry 238; bankPayments write tools absent.
- Freeze ACCEPT does not green coverage and is not product ACCEPT.

## Review decisions (authoritative)

- Wave-5g through Wave-5i freeze/product: **ACCEPT** offline where recorded.
- Wave-5j freeze and product: **ACCEPT** offline (product via Codex fallback ACCEPT page).
- Wave-5k freeze-ready / implementation / authoring-readiness / package / authority research: **ACCEPT** offline handoffs as recorded.
- Wave-5k product-ready research: **ACCEPT offline handoff only**.
- Wave-5k freeze page: **ACCEPT** at `wiki/wave_fivek_freeze_independent_review.md`.
- Wave-5k product: **not authored / not accepted**.
- Overall completeness: **FAIL**.

## Open coverage work

1. Wave-5k product leaf (four tools) now authorised by freeze ACCEPT → registry 242 / coverage 168 offline; delete stays red.
2. Independent product review ACCEPT after product merge.
3. Later freezes: salesTaxPayments / contactBalancePayments / invoiceLateFees
   create+update; invoiceReminders create only (PUT 405); remaining blocked CUD.
4. Bulk 92, UI/auth/vision, live CUD still open.

## Evidence boundaries

- Official API fingerprint: etag `hsisik4g9p3603`, MD5 `c2efda0ee4cf9cf200e14910c5fc6996`.
- bankPayments singular DELETE remains **405**; no delete tools.
- Inventory create cleanup: void via irreversible `isVoided` (live verify later).
- No coverage green from review alone.

## References

- Freeze ACCEPT: `wiki/wave_fivek_freeze_independent_review.md`
- Freeze contract: `wiki/wave_fivek_ticketed_writes_contract.md`
- Fallback freeze record: `wiki/wave_fivek_freeze_codex_fallback_review.md`
- Current review scratch: `.fractal/main.billy_complete/tmp/grok-review.md`
- Current research scratch: `.fractal/main.billy_complete/tmp/grok-research.md`
