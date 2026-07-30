---
name: state
desc: Current node state, verified review decisions, and open qualification work.
tags: [billy, coverage, review]
sources:
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
  - https://www.billy.dk/api/
created: 2026-07-30T15:57:03Z
updated: 2026-07-30T20:10:00Z
---

# state

## Current state

- Wave-5c through Wave-5r write modules merged on root (including salesTaxReturns update).
- Wave-5s-A `api_invoice_logs_list` and Wave-5s-B ticketed file upload (containment-repaired) are merged with offline product ACCEPT (live still false).
- Wave-5s-C ticketed invoice email + invoiceDeliveries product is merged on root (`0efceae`). Tools: `api_invoices_send_email_preview`/`execute`, `api_invoice_deliveries_create_preview`/`execute`. Module: `src/billy_mcp/api/invoice_email_delivery_writes.py`.
- Root offline coverage: **184** implemented + contract_tested. Live/vision **0**. `complete: false`. Specials not-impl **0**. Clear not-impl **29**. Bulk **92** red. UI **339** red.
- Research87 docs fingerprint still MD5 `8b94b0135c91fd15fe54ea33e088a4be`. Residual clear still offline-blocked.
- Product child `wave5sc_email_delivery_product` completed and merged. No active product child for specials.

## Verification

- Review87 docs re-fetch: ETag `"wcw4x9hqvu3603"`, 147934 bytes, MD5 `8b94b0135c91fd15fe54ea33e088a4be`.
- Review87 unauth probes match email/delivery method gates; residual samples still block offline freezes.
- Focused product suite: 32 passed (`tests/api/test_invoice_email_delivery_writes.py`).
- Root commit-mode suite: 1,255 non-live tests passed with Ruff, Pyright,
  coverage, and repository-policy checks passing.
- Coverage honesty: 184/184/0/0, `complete: false`. live_tested false on email/delivery specials.

## Review decisions (authoritative)

- Wave-5m through Wave-5q freeze/product: **ACCEPT** offline.
- Wave-5r freeze/product independent: **ACCEPT** offline.
- Wave-5s residual/specials research: **ACCEPT as research**.
- Wave-5s-A invoiceLogs: product offline green.
- Wave-5s-B containment-repaired upload product: **ACCEPT** offline only.
- Wave-5s-C freeze / product-ready / research83–87: **ACCEPT as research** where applicable.
- Wave-5s-C product (review87): **ACCEPT offline only**; `live_tested` false.
- Overall completeness: **FAIL**.

## Open coverage work

1. Residual clear 29 (405 false friends / transactions property posture / bankPayments delete / reminder-association delete meta) — live token or docs change required for offline-blocked rows.
2. Ambiguous bulk 92 — live matrix or official bulk evidence.
3. UI/auth/vision qualification — credentials + dedicated org.
4. Live qualification for high side-effect specials (email, delivery, upload) on non-production org only.

## Evidence boundaries

- Wave-5s-C product ACCEPT is offline only; do not set email/delivery `live_tested` without non-production proof.
- Response roots provisional (`changed_records[]`, singular `invoiceDelivery`) until live envelope proof.
- Do not green residual/bulk/UI from Supports text or research alone.
- Email binds `target=invoiceId`; no `destination_url`; no multi-recipient.
- Delivery: no invented `receiverCvr`/get/list/update; status via invoiceLogs.
- No automatic retry after external-send POST.

## References

- Freeze: `wiki/wave_fivesc_invoice_email_delivery_research.md`
- Product-ready: `wiki/wave_fivesc_invoice_email_delivery_product_ready_research.md`
- Research87 reconfirm: `wiki/wave_fivesc_research87_product_in_flight_reconfirm.md`
- Review87 IR + product ACCEPT: `wiki/wave_fivesc_research87_independent_review.md`
- Probe rules: `wiki/offline_write_probe_rules.md`
- Research scratch: `.fractal/main.billy_complete/tmp/grok-research.md`
- Review scratch: `.fractal/main.billy_complete/tmp/grok-review.md`
