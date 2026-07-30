---
name: state
desc: Current node state, verified review decisions, and open qualification work.
tags: [billy, coverage, review]
sources:
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
  - https://www.billy.dk/api/
created: 2026-07-30T15:57:03Z
updated: 2026-07-30T17:57:00Z
---

# state

## Current state

- Wave-5c through Wave-5r write modules merged on root (including salesTaxReturns update).
- Wave-5s-A `api_invoice_logs_list` merged. Root offline coverage **180** implemented + contract_tested. Live/vision **0**. `complete: false`.
- Wave-5s-B product child active: `wave5sb_files_upload_product`. Product tools still absent on root; the pre-edit Grok-auth failure has a completed Codex Power fallback record, which is intentionally non-authoritative.
- Wave-5s-C freeze research: **ACCEPT as research** (research81 + independent review). Docs MD5 `8b94b0135c91fd15fe54ea33e088a4be` reconfirmed.
- UI all red (339); bulk 92 red; clear not-impl 30; specials not-impl 3; no live token; no UI credentials.

## Verification

- Independent docs re-fetch review81: ETag `"wcw4x9hqvu3603"`, 147934 bytes, MD5 `8b94b0135c91fd15fe54ea33e088a4be`, byte-identical to research81.
- Email/delivery unauth probes match research81; nested delivery path 404; no product modules on root.
- Inventory response_fields for email/delivery remain provisional (no official success samples).
- Coverage honesty: 180/180/0/0, `complete: false`. No research greening.

## Review decisions (authoritative)

- Wave-5m through Wave-5q freeze/product: **ACCEPT** offline.
- Wave-5r freeze/product independent: **ACCEPT** offline.
- Wave-5s residual/specials research: **ACCEPT as research**.
- Wave-5s-A invoiceLogs research IR: **ACCEPT as research**.
- Wave-5s-B freeze + product-ready research independent: **ACCEPT** offline as handoff only (not product ACCEPT).
- Wave-5s-B Codex fallback review: **ACCEPT as research handoff only**; it cannot discharge the mandatory Grok product audit.
- Wave-5s-C freeze research independent: **ACCEPT as research** (not product ACCEPT).
- Overall completeness: **FAIL**.

## Open coverage work

1. Codex Power Wave-5s-B product leaf (active): ticketed upload pair + dual-row green + binary client path.
2. Mandatory Grok product independent review after 5s-B root merge; the existing Codex fallback cannot discharge it.
3. Codex Power Wave-5s-C after 5s-B product IR: email + delivery ticketed pairs per freeze ACCEPT.
4. Later: 405 false friends, transactions, bulk 92, UI/auth/vision.

## Evidence boundaries

- Research ACCEPT is not product, live, UI, vision, bulk, or completeness.
- Do not green coverage from research alone.
- Email binds `target=invoiceId`; no `destination_url`; no multi-recipient.
- Delivery: no invented `receiverCvr`/get/list/update; status via invoiceLogs.
- Response roots provisional until live proof.

## References

- Freeze: `wiki/wave_fivesc_invoice_email_delivery_research.md`
- Freeze IR: `wiki/wave_fivesc_invoice_email_delivery_research_independent_review.md`
- Wave-5s-B fallback: `wiki/wave_fivesb_files_upload_research_codex_fallback_review.md`
- Review scratch: `.fractal/main.billy_complete/tmp/grok-review.md`
- Research scratch: `.fractal/main.billy_complete/tmp/grok-research.md`
