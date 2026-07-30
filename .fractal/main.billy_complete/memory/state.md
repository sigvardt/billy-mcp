---
name: state
desc: Current node state, verified review decisions, and open qualification work.
tags: [billy, coverage, review]
sources:
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
  - https://www.billy.dk/api/
created: 2026-07-30T15:57:03Z
updated: 2026-07-30T19:25:00Z
---

# state

## Current state

- Wave-5c through Wave-5r write modules merged on root (including salesTaxReturns update).
- Wave-5s-A `api_invoice_logs_list` and Wave-5s-B ticketed `api_files_upload_preview`/`api_files_upload_execute` are merged on root. Wave-5s-B execution now acquires the upload through descriptor-relative no-follow traversal, validates that descriptor, and reads/hashes/sends its single buffer. Root offline coverage remains **182** implemented + contract_tested. Live/vision **0**. `complete: false`.
- Wave-5s-B containment repair merged as `b54f8f9`. The only remaining Wave-5s-B product gate is the mandatory Grok product IR; Codex fallback reviews remain non-authoritative.
- Wave-5s-C freeze / product-ready / research83 / research84 / research85: research handoff reconfirmed. Docs MD5 `8b94b0135c91fd15fe54ea33e088a4be` byte-identical through research85. Wire unchanged. Residual clear **29** fully matrixed offline-blocked (405 false friends, transactions property posture, bankPayments delete 405, association/transaction DELETE 200 meta-only). Specials not-impl **2** (email + delivery). Email/delivery product modules absent.
- Wave-5s-C product intentionally remains unstarted until a Wave-5s-B Grok product ACCEPT (sequencing gate).
- UI all red (339); bulk 92 red; no live token; no UI credentials.

## Verification

- Research85 docs re-fetch: ETag `"wcw4x9hqvu3603"`, 147934 bytes, MD5 `8b94b0135c91fd15fe54ea33e088a4be`, byte-identical to research81–84.
- Research85 unauth probes match email/delivery gates; residual clear 29 full matrix in `tmp/write-probes-research85.json`.
- The pre-repair MockTransport reproduction showed that a same-digest outside-root symlink could replace the previewed path after identity validation and emit one POST. The merged repair adds terminal and intermediate symlink-window regressions that require `FILE_NOT_ALLOWED` with zero HTTP, while changed bytes require `FILE_CHANGED` with zero HTTP.
- The repair passed a 38-test focused clean-archive suite and the root 1,223-test non-live suite. Root Ruff format/check, Pyright, coverage consistency, and repository-policy checks pass.
- Coverage honesty: 182/182/0/0, `complete: false`. No research greening. `WriteProtocolService` POST still `target=None` / collection-only path / plural success roots.

## Review decisions (authoritative)

- Wave-5m through Wave-5q freeze/product: **ACCEPT** offline.
- Wave-5r freeze/product independent: **ACCEPT** offline.
- Wave-5s residual/specials research: **ACCEPT as research**.
- Wave-5s-A invoiceLogs research IR: **ACCEPT as research**.
- Wave-5s-B freeze + product-ready research independent: **ACCEPT** offline as handoff only (not product ACCEPT).
- Wave-5s-B Codex fallback review: **non-authoritative**; cannot discharge mandatory Grok product audit.
- Wave-5s-C freeze research independent: **ACCEPT as research** (not product ACCEPT).
- Wave-5s-C product-ready research independent: **ACCEPT** offline as handoff only (not product ACCEPT).
- Wave-5s-C research83 reconfirm independent (review83): **ACCEPT as research handoff only**.
- Wave-5s-C research84 handoff reconfirm independent (review84): **ACCEPT as research handoff only**.
- Wave-5s-C research85 product-ready reconfirm: **research only** (pending independent review step).
- Wave-5s-B product ACCEPT: **FAIL / open** (mandatory Grok IR missing).
- Overall completeness: **FAIL**.

## Open coverage work

1. Complete the mandatory Grok product IR of the containment-repaired Wave-5s-B; Codex fallback cannot accept.
2. Codex Power Wave-5s-C: email + delivery ticketed pairs per freeze + product-ready + research83–85 (custom services, target=invoiceId) — only after step 1.
4. Later: residual clear 405 false friends / transactions property posture / bulk 92 / UI/auth/vision (live token required for residual offline-blocked rows).

## Evidence boundaries

- Research ACCEPT / product-ready handoff is not product, live, UI, vision, bulk, or completeness.
- Do not green coverage from research alone.
- Email binds `target=invoiceId`; no `destination_url`; no multi-recipient.
- Delivery: no invented `receiverCvr`/get/list/update; status via invoiceLogs.
- Response roots provisional until live proof.
- Generic WriteProtocolService POST target=None and plural-list success mapping are insufficient for these specials.
- Unauth 405 overrides Supports for residual clear offline green.
- Transactions Supports create/update/delete does not yield offline freeze: properties readonly except immutable organization.
- Path-based `read_bytes()` after a standalone identity recheck is not sufficient for upload containment, even with a matching SHA-256 digest. The execution read must be rooted and no-follow at descriptor level.

## References

- Freeze: `wiki/wave_fivesc_invoice_email_delivery_research.md`
- Freeze IR: `wiki/wave_fivesc_invoice_email_delivery_research_independent_review.md`
- Product-ready: `wiki/wave_fivesc_invoice_email_delivery_product_ready_research.md`
- Product-ready IR: `wiki/wave_fivesc_invoice_email_delivery_product_ready_research_independent_review.md`
- Research83 IR: `wiki/wave_fivesc_research83_independent_review.md`
- Research84 reconfirm: `wiki/wave_fivesc_research84_handoff_reconfirm.md`
- Research84 IR: `wiki/wave_fivesc_research84_independent_review.md`
- Research85 reconfirm: `wiki/wave_fivesc_research85_product_ready_reconfirm.md`
- Wave-5s-B fallback: `wiki/wave_fivesb_files_upload_product_codex_fallback_review.md`
- Probe rules: `wiki/offline_write_probe_rules.md`
- Research scratch: `.fractal/main.billy_complete/tmp/grok-research.md`
- Review scratch: `.fractal/main.billy_complete/tmp/grok-review.md`
