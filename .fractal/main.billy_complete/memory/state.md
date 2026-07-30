---
name: state
desc: Current node state, verified review decisions, and open qualification work.
tags: [billy, coverage, review]
sources:
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
  - https://www.billy.dk/api/
created: 2026-07-30T15:57:03Z
updated: 2026-07-30T19:08:00Z
---

# state

## Current state

- Wave-5c through Wave-5r write modules merged on root (including salesTaxReturns update).
- Wave-5s-A `api_invoice_logs_list` and Wave-5s-B ticketed `api_files_upload_preview`/`api_files_upload_execute` merged on root. The merged transient-buffer SHA-256 guard catches changed-byte replacement, but is insufficient for configured-root containment: a same-digest outside-root symlink can be substituted after identity validation and read before `post_file`. Root offline coverage is **182** implemented + contract_tested. Live/vision **0**. `complete: false`.
- Wave-5s-B product remains blocked by the same-digest symlink containment TOCTOU and the mandatory Grok product IR. The Codex fallback failure is non-authoritative but supplies a local, deterministic reproduction and required descriptor-traversal repair shape. Active child: `wave5sb_upload_containment_fix`.
- Wave-5s-C freeze / product-ready / research83 / research84: research handoff accepted by independent review. Docs MD5 `8b94b0135c91fd15fe54ea33e088a4be` byte-identical. Wire unchanged. Residual clear **29** still offline-blocked (405 false friends, transactions property posture, bankPayments delete 405). Specials not-impl **2** (email + delivery). Email/delivery product modules absent.
- Wave-5s-C product intentionally unstarted until Wave-5s-B Grok product ACCEPT (sequencing gate).
- UI all red (339); bulk 92 red; no live token; no UI credentials.

## Verification

- Review84 independent docs re-fetch: ETag `"wcw4x9hqvu3603"`, 147934 bytes, MD5 `8b94b0135c91fd15fe54ea33e088a4be`, byte-identical to research84.
- Independent unauth probes match research84 email/delivery and residual matrix; transactions POST/PUT 401 with all non-org properties readonly.
- Root reproduced the upload containment defect with a local MockTransport: swapping the previewed file to a same-digest symlink whose target lies outside the configured root after the identity recheck returned upload success and emitted one mock POST. This confirms that the current resolved-path `read_bytes()` is unsafe even when the buffer digest matches.
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
- Wave-5s-B product ACCEPT: **FAIL / open** (same-digest symlink containment repair and Grok IR missing).
- Overall completeness: **FAIL**.

## Open coverage work

1. Codex Power containment repair for Wave-5s-B: acquire and validate the upload through configured-root-aware no-follow descriptor traversal, then read/hash/send the same descriptor buffer. Add a deterministic same-digest outside-root symlink-window regression with zero HTTP.
2. Complete the mandatory Grok product IR of the containment-repaired Wave-5s-B when Grok authentication is available; Codex fallback cannot accept.
3. Codex Power Wave-5s-C: email + delivery ticketed pairs per freeze + product-ready + research83/84 (custom services, target=invoiceId) — only after step 2.
3. Later: residual clear 405 false friends / transactions property posture / bulk 92 / UI/auth/vision (live token required for residual offline-blocked rows).

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
- Wave-5s-B fallback: `wiki/wave_fivesb_files_upload_research_codex_fallback_review.md`
- Probe rules: `wiki/offline_write_probe_rules.md`
- Research scratch: `.fractal/main.billy_complete/tmp/grok-research.md`
- Review scratch: `.fractal/main.billy_complete/tmp/grok-review.md`
