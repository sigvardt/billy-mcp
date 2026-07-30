---
name: state
desc: Current node state, verified review decisions, and open qualification work.
tags: [billy, coverage, review]
sources:
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
  - https://www.billy.dk/api/
created: 2026-07-30T15:57:03Z
updated: 2026-07-30T18:38:00Z
---

# state

## Current state

- Wave-5c through Wave-5r write modules merged on root (including salesTaxReturns update).
- Wave-5s-A `api_invoice_logs_list` and Wave-5s-B ticketed `api_files_upload_preview`/`api_files_upload_execute` merged on root. Root offline coverage is **182** implemented + contract_tested. Live/vision **0**. `complete: false`.
- Wave-5s-B integrated as merge `b6e2c51` with StrictBool and CR/LF safety repairs. Mandatory Grok product IR still open (Grok review child killed; Codex fallback non-authoritative). Upload identity re-check then separate `read_bytes()` TOCTOU race still present on root (`file_upload_writes.py` execute). Race-fix child active.
- Wave-5s-C freeze research: **ACCEPT as research** (research81 + independent review). Docs MD5 `8b94b0135c91fd15fe54ea33e088a4be`.
- Wave-5s-C product-ready research: **ACCEPT offline as handoff only** (research82 + independent review82). Custom ConfirmationStore services required; generic WriteProtocolService insufficient.
- Wave-5s-C implementation-ready reconfirm (research83): docs **byte-identical**; residual clear **29** ranked. Independent review83: **ACCEPT as research handoff only**.
- UI all red (339); bulk 92 red; clear not-impl 29; specials not-impl 2; no live token; no UI credentials.

## Verification

- Review83 docs re-fetch: ETag `"wcw4x9hqvu3603"`, 147934 bytes, MD5 `8b94b0135c91fd15fe54ea33e088a4be`, byte-identical to research83.
- Independent unauth probes match research83 email/delivery and residual matrix.
- Coverage honesty: 182/182/0/0, `complete: false`. No research greening. Email/delivery specials remain red; files upload implemented+contract_tested, not live-tested, product ACCEPT blocked by race + missing Grok IR.

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
- Wave-5s-B product ACCEPT: **FAIL / open** (race + Grok IR missing).
- Overall completeness: **FAIL**.

## Open coverage work

1. Finish exact-byte upload binding repair; relaunch mandatory Grok product IR of repaired Wave-5s-B (Codex fallback cannot accept).
2. Codex Power Wave-5s-C: email + delivery ticketed pairs per freeze + product-ready + research83 (custom services, target=invoiceId).
3. Later: residual clear 405 false friends / transactions property posture / bulk 92 / UI/auth/vision.


## Evidence boundaries

- Research ACCEPT / product-ready handoff is not product, live, UI, vision, bulk, or completeness.
- Do not green coverage from research alone.
- Email binds `target=invoiceId`; no `destination_url`; no multi-recipient.
- Delivery: no invented `receiverCvr`/get/list/update; status via invoiceLogs.
- Response roots provisional until live proof.
- Generic WriteProtocolService POST target=None and plural-list success mapping are insufficient for these specials.
- Unauth 405 overrides Supports for residual clear offline green.

## References

- Freeze: `wiki/wave_fivesc_invoice_email_delivery_research.md`
- Freeze IR: `wiki/wave_fivesc_invoice_email_delivery_research_independent_review.md`
- Product-ready: `wiki/wave_fivesc_invoice_email_delivery_product_ready_research.md`
- Product-ready IR: `wiki/wave_fivesc_invoice_email_delivery_product_ready_research_independent_review.md`
- Research83 IR: `wiki/wave_fivesc_research83_independent_review.md`
- Wave-5s-B fallback: `wiki/wave_fivesb_files_upload_research_codex_fallback_review.md`
- Probe rules: `wiki/offline_write_probe_rules.md`
- Research scratch: `.fractal/main.billy_complete/tmp/grok-research.md`
- Review scratch: `.fractal/main.billy_complete/tmp/grok-review.md`
