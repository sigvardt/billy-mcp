---
name: state
desc: Current node state, verified review decisions, and open qualification work.
tags: [billy, coverage, review]
sources:
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
  - https://www.billy.dk/api/
created: 2026-07-30T15:57:03Z
updated: 2026-07-30T20:20:00Z
---

# state

## Current state

- Wave-5c through Wave-5r write modules merged on root (including salesTaxReturns update).
- Wave-5s-A `api_invoice_logs_list` and Wave-5s-B ticketed file upload (containment-repaired) are merged with offline product ACCEPT (live still false).
- Wave-5s-C ticketed invoice email + invoiceDeliveries product is merged on root (`0efceae`). Tools: `api_invoices_send_email_preview`/`execute`, `api_invoice_deliveries_create_preview`/`execute`. Module: `src/billy_mcp/api/invoice_email_delivery_writes.py`.
- All **6** specials are implemented offline. Residual clear not-impl **29**. Ambiguous bulk **92** red. UI **339** red.
- Root offline coverage: **184** implemented + contract_tested. Live/vision **0**. `complete: false`.
- Research88: docs fingerprint still MD5 `8b94b0135c91fd15fe54ea33e088a4be`. No offline-productable residual special remains. Next slice is Wave-5t live residual/bulk gate harness (not product tools).
- `BILLY_API_TOKEN` and UI secrets verified unset this research pass.

## Verification

- Research88 docs re-fetch: ETag `"wcw4x9hqvu3603"`, 147934 bytes, MD5 `8b94b0135c91fd15fe54ea33e088a4be` (byte-identical to review87).
- Research88 residual unauth matrix: 405 false friends with explicit METHOD_NOT_ALLOWED messages; bankPayments delete 405; transactions POST/PUT 401 + readonly table; associations create/update 405; delete meta-only + ids[] error shape.
- Research88 bulk unauth: `PUT /{res}/bulk` → 401 candidate; `POST /{res}/bulk` → 405; `PATCH /{res}` empty plural → unauth meta-200 (not a contract).
- Coverage honesty: 184/184/0/0, `complete: false`.

## Review decisions (authoritative)

- Wave-5m through Wave-5q freeze/product: **ACCEPT** offline.
- Wave-5r freeze/product independent: **ACCEPT** offline.
- Wave-5s residual/specials research: **ACCEPT as research**.
- Wave-5s-A invoiceLogs: product offline green.
- Wave-5s-B containment-repaired upload product: **ACCEPT** offline only.
- Wave-5s-C freeze / product-ready / research83–87: **ACCEPT as research** where applicable.
- Wave-5s-C product (review87): **ACCEPT offline only**; `live_tested` false.
- Research88 residual/bulk live-gate ranking: **research only** (not product ACCEPT).
- Overall completeness: **FAIL**.

## Open coverage work

1. Wave-5t live residual/bulk gate harness (fail-closed without token) — recommended next Codex slice.
2. Residual clear 29 — live token required; offline 405/readonly blocks remain.
3. Ambiguous bulk 92 — live matrix required; strongest offline method-open candidate is `PUT /{resource}/bulk`.
4. UI/auth/vision qualification — credentials + dedicated org.
5. Live qualification for high side-effect specials (email, delivery, upload) on non-production org only.

## Evidence boundaries

- Do not implement residual or bulk tools from Supports text, unauth 401 alone, or PATCH meta-200.
- Wave-5s-C product ACCEPT is offline only; do not set email/delivery `live_tested` without non-production proof.
- Response roots for email/delivery remain provisional until live envelope proof.
- No webhooks (official 0 mentions; API 404 UNKNOWN_RESOURCE).
- Email binds `target=invoiceId`; no `destination_url`; no multi-recipient.
- Delivery: no invented `receiverCvr`/get/list/update; status via invoiceLogs.

## References

- Research88 brief: `.fractal/main.billy_complete/tmp/grok-research.md`
- Probes: `.fractal/main.billy_complete/tmp/write-probes-research88.json`
- Freeze history: `wiki/wave_fivesc_invoice_email_delivery_research.md`
- Product-ready: `wiki/wave_fivesc_invoice_email_delivery_product_ready_research.md`
- Review87 IR: `wiki/wave_fivesc_research87_independent_review.md`
- Probe rules: `wiki/offline_write_probe_rules.md`
- Residual specials research: `wiki/wave_fives_residual_specials_research.md`
