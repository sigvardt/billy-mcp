---
name: state
desc: Current node state, verified review decisions, and open qualification work.
tags: [billy, coverage, review]
sources:
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
  - https://www.billy.dk/api/
created: 2026-07-30T06:20:59Z
updated: 2026-07-30T08:07:00Z
---

# state

## Current state

- Wave-5c through Wave-5l write modules are merged into root; root registration uses the one shared `ConfirmationStore` and `WriteProtocolService`.
- Root registry **246** `api_*` tools. Offline coverage **170** implemented + contract_tested. Live/vision still 0. `complete: false`.
- Wave-5k freeze and product: ACCEPT offline.
- Wave-5l freeze ACCEPT: `wiki/wave_fivel_freeze_independent_review.md` (contract MD5 `3c49c4f41f3d9485a177a6ee643db412`).
- Wave-5l product is on root (`sales_tax_payment_writes.py`); offline create+update green. Codex fallback product ACCEPT at `wiki/wave_fivel_product_codex_fallback_review.md`; required Grok product gate may still be pending separately and does not block Wave-5m product.
- Wave-5m freeze page on root: `wiki/wave_fivem_ticketed_writes_contract.md`.
- Wave-5m freeze independent review: **ACCEPT** at `wiki/wave_fivem_freeze_independent_review.md` (authoritative). Codex freeze fallback record is non-authoritative corroboration only.
- Wave-5m product research handoff: research58 **ACCEPT** as research (`tmp/grok-research.md`). Independent review58: product **not accepted** (module absent; 246 tools; create/update rows still red).
- Product child `main.billy_complete.wave5m_contact_balance_payment_product` is active under freeze ACCEPT.
- bankPayments / salesTaxPayments create+update offline-qualified; deletes 405 red; bulk ambiguous empty.
- UI all red; bulk 92 empty-tool red; no live token; no UI credentials.

## Verification

- Official docs retain ETag `hsisik4g9p3603`, MD5 `c2efda0ee4cf9cf200e14910c5fc6996`, body 147934 (review58 reconfirm).
- Unauth: contactBalancePayments POST/PUT **401**, DELETE **405** reconfirmed.
- Coverage honesty: implemented/contract_tested **170**, live/vision **0**, `complete: false`. No false greens. No bulk greened.

## Review decisions (authoritative)

- Wave-5g through Wave-5k freeze/product: **ACCEPT** offline where recorded.
- Wave-5l freeze page: **ACCEPT** offline.
- Wave-5l product: Codex fallback ACCEPT recorded; Grok product gate still pending if not merged as authoritative.
- Wave-5m freeze page: **ACCEPT** offline (Grok independent review).
- Wave-5m research58 handoff: **ACCEPT** as research only.
- Wave-5m product: **not accepted** (not implemented on root).
- Overall completeness: **FAIL**.

## Open coverage work

1. Finish Wave-5m product leaf (four tools; +2 → 172 offline, tools 250); then independent product review.
2. When greening create row, fix cleanup text away from “delete dedicated test resource” (singular DELETE unsupported).
3. Later freezes: invoiceLateFees create+update; invoiceReminders create only; remaining blocked CUD.
4. Bulk 92, UI/auth/vision, live CUD still open.

## Evidence boundaries

- Official API fingerprint: etag `hsisik4g9p3603`, MD5 `c2efda0ee4cf9cf200e14910c5fc6996`.
- contactBalancePayments Supports omits singular delete; unauth DELETE **405**.
- bankPayment sample is not the contactBalancePayment request schema.
- Research and freeze ACCEPT do not green product rows.

## References

- Research: `.fractal/main.billy_complete/tmp/grok-research.md` (research58)
- Probes: `.fractal/main.billy_complete/tmp/write-probes-research58.json`
- Wave-5m freeze ACCEPT: `wiki/wave_fivem_freeze_independent_review.md`
- Wave-5m freeze contract: `wiki/wave_fivem_ticketed_writes_contract.md`
- Offline probe rules: `wiki/offline_write_probe_rules.md`
