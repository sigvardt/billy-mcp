---
name: state
desc: Current node state, verified review decisions, and open qualification work.
tags: [billy, coverage, review]
sources:
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
  - https://www.billy.dk/api/
created: 2026-07-30T15:57:03Z
updated: 2026-07-30T19:45:00Z
---

# state

## Current state

- Wave-5c through Wave-5r write modules merged on root (including salesTaxReturns update).
- Wave-5s-A `api_invoice_logs_list` and Wave-5s-B ticketed `api_files_upload_preview`/`api_files_upload_execute` are merged on root with descriptor-relative no-follow containment. Root offline coverage remains **182** implemented + contract_tested. Live/vision **0**. `complete: false`.
- Wave-5s-B containment repair merged (`b54f8f9`). Independent Grok product review **ACCEPT** offline for the containment-repaired upload (focused suite 38 passed; live still false).
- Wave-5s-C research86 product implementation handoff: official docs MD5 `8b94b0135c91fd15fe54ea33e088a4be` byte-identical to research81–85. Wire unchanged. Sequencing gate **OPEN**. Residual clear **29** offline-blocked. Specials not-impl **2** (email + delivery). Email/delivery product modules still absent.
- Wave-5s-C product may start: Codex Power four-tool leaf is unblocked.
- UI all red (339); bulk 92 red; no live token; no UI credentials.

## Verification

- Research86 docs re-fetch: ETag `"wcw4x9hqvu3603"`, 147934 bytes, MD5 `8b94b0135c91fd15fe54ea33e088a4be`, byte-identical to research85.
- Research86 unauth probes: email POST object root 401; non-object/empty 400; non-POST 405; delivery POST 401; nested create 404; webhooks 404.
- Upload execute opens via configured-root `O_NOFOLLOW` descriptor traversal; same-digest outside-root symlink races return `FILE_NOT_ALLOWED` with zero HTTP.
- Coverage honesty: 182/182/0/0, `complete: false`. No research greening. `WriteProtocolService` POST still `target=None` / collection-only path / plural success roots.

## Review decisions (authoritative)

- Wave-5m through Wave-5q freeze/product: **ACCEPT** offline.
- Wave-5r freeze/product independent: **ACCEPT** offline.
- Wave-5s residual/specials research: **ACCEPT as research**.
- Wave-5s-A invoiceLogs research IR: **ACCEPT as research**.
- Wave-5s-B freeze + product-ready research independent: **ACCEPT** offline as handoff only (historical).
- Wave-5s-B containment-repaired product (review85): **ACCEPT** offline only; `live_tested` false.
- Wave-5s-C freeze research independent: **ACCEPT as research** (not product ACCEPT).
- Wave-5s-C product-ready research independent: **ACCEPT** offline as handoff only (not product ACCEPT).
- Wave-5s-C research83–85 reconfirms independent: **ACCEPT as research handoff only**.
- Wave-5s-C research86 product implementation handoff: **ready for Codex Power product** (not product ACCEPT).
- Wave-5s-C product ACCEPT: **open** (tools not implemented).
- Overall completeness: **FAIL**.

## Open coverage work

1. Codex Power Wave-5s-C: email + delivery ticketed pairs per freeze + product-ready + research83–86 (custom services, target=invoiceId).
2. Later: residual clear 405 false friends / transactions property posture / bulk 92 / UI/auth/vision (live token required for residual offline-blocked rows).

## Evidence boundaries

- Research ACCEPT / product-ready handoff is not product for email/delivery, live, UI, vision, bulk, or completeness.
- Wave-5s-B product ACCEPT is offline only; do not set upload `live_tested` without non-production proof.
- Do not green coverage from research alone.
- Email binds `target=invoiceId`; no `destination_url`; no multi-recipient.
- Delivery: no invented `receiverCvr`/get/list/update; status via invoiceLogs.
- Response roots provisional until live proof.
- Generic WriteProtocolService POST target=None and plural-list success mapping are insufficient for email/delivery specials.
- Unauth 405 overrides Supports for residual clear offline green.
- Transactions Supports create/update/delete does not yield offline freeze: properties readonly except immutable organization.

## References

- Freeze: `wiki/wave_fivesc_invoice_email_delivery_research.md`
- Product-ready: `wiki/wave_fivesc_invoice_email_delivery_product_ready_research.md`
- Research85 reconfirm: `wiki/wave_fivesc_research85_product_ready_reconfirm.md`
- Research85 IR + upload product ACCEPT: `wiki/wave_fivesc_research85_independent_review.md`
- Research86 product implementation handoff: `wiki/wave_fivesc_research86_product_implementation_handoff.md`
- Probe rules: `wiki/offline_write_probe_rules.md`
- Research scratch: `.fractal/main.billy_complete/tmp/grok-research.md`
- Review scratch: `.fractal/main.billy_complete/tmp/grok-review.md`
