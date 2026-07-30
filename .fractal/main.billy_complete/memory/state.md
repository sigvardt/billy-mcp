---
name: state
desc: Current node state, verified review decisions, and open qualification work.
tags: [billy, coverage, review]
sources:
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
  - https://www.billy.dk/api/
created: 2026-07-30T06:20:59Z
updated: 2026-07-30T08:45:00Z
---

# state

## Current state

- Wave-5c through Wave-5m write modules are merged into root; root registration uses the one shared `ConfirmationStore` and `WriteProtocolService`.
- Root registry **250** `api_*` tools. Offline coverage **172** implemented + contract_tested. Live/vision still 0. `complete: false`.
- Wave-5k freeze and product: ACCEPT offline.
- Wave-5l freeze ACCEPT: `wiki/wave_fivel_freeze_independent_review.md`.
- Wave-5l product on root; Codex fallback product ACCEPT recorded.
- Wave-5m freeze ACCEPT: `wiki/wave_fivem_freeze_independent_review.md` (contract MD5 `fcb0e58742c8abc8ca9078859bb74eb8`).
- Wave-5m product on root: `contact_balance_payment_writes.py` + tests; merge `8297713`; acceptance record `8133858`.
- Wave-5m product independent review: **ACCEPT** offline at `wiki/wave_fivem_product_independent_review.md`.
- Research60: Wave-5n `invoiceLateFees` freeze page is the **next Codex slice** (gate open). Freeze page not yet authored.
- Official docs: plain contract identical to prior lock; HTTP ETag/MD5 advanced to `juf598rs793603` / `f3925615c452b34694abb7f2856e845a` (Prismic `ref` only). Inventory still pins prior ETag/MD5.
- bankPayments / salesTaxPayments / contactBalancePayments create+update offline-qualified; deletes 405 red where applicable; bulk ambiguous empty.
- UI all red; bulk 92 empty-tool red; no live token; no UI credentials.

## Verification

- Official plain docs identical to research59; HTTP fingerprint `juf598rs793603` / `f3925615c452b34694abb7f2856e845a` / body 147934 (research60).
- Unauth contactBalancePayments POST/PUT **401**, DELETE **405** reconfirmed.
- Unauth invoiceLateFees POST/PUT **401**, singular DELETE **405**, bulk DELETE **405** reconfirmed.
- Coverage honesty: implemented/contract_tested **172**, live/vision **0**, `complete: false`. No false greens. No bulk greened.

## Review decisions (authoritative)

- Wave-5g through Wave-5k freeze/product: **ACCEPT** offline where recorded.
- Wave-5l freeze page: **ACCEPT** offline.
- Wave-5l product: Codex fallback ACCEPT recorded.
- Wave-5m freeze page: **ACCEPT** offline.
- Wave-5m product: **ACCEPT** offline.
- Research60 Wave-5n freeze-ready: **ACCEPT as research** only; freeze page not present.
- Wave-5n freeze page: not present; no ACCEPT.
- Overall completeness: **FAIL**.

## Open coverage work

1. Author Wave-5n freeze for invoiceLateFees create+update (research60 package); then freeze review and product.
2. Later: invoiceReminders create only; associations create/update stay blocked offline (405).
3. Optional: refresh inventory evidence strings from prior ETag/MD5 to current HTTP fingerprint after plain identity is recorded (not a contract change).
4. Bulk 92, UI/auth/vision, live CUD still open.

## Evidence boundaries

- Official API plain contract lock: prior MD5 `c2efda0ee4cf9cf200e14910c5fc6996` still matches stripped body.
- Current HTTP access: etag `juf598rs793603`, MD5 `f3925615c452b34694abb7f2856e845a`.
- contactBalancePayments / invoiceLateFees Supports omit singular delete; unauth DELETE **405**.
- invoiceLateFees bulk DELETE unauth **405** overrides Supports bulk delete for offline greening.
- Product offline ACCEPT is not live/UI/vision ACCEPT.

## References

- Research: `.fractal/main.billy_complete/tmp/grok-research.md` (research60)
- Wave-5m product ACCEPT: `wiki/wave_fivem_product_independent_review.md`
- Wave-5m freeze: `wiki/wave_fivem_ticketed_writes_contract.md`
- Offline probe rules: `wiki/offline_write_probe_rules.md`
