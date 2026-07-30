---
name: state
desc: Current node state, verified review decisions, and open qualification work.
tags: [billy, coverage, review]
sources:
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
  - https://www.billy.dk/api/
created: 2026-07-30T15:57:03Z
updated: 2026-07-30T18:15:00Z
---

# state

## Current state

- Wave-5c through Wave-5r write modules merged on root (including salesTaxReturns update).
- Wave-5s-A `api_invoice_logs_list` merged. Root offline coverage **180** implemented + contract_tested. Live/vision **0**. `complete: false`.
- Wave-5s-B product child active: `wave5sb_files_upload_product`. Product tools remain absent on root, but its committed archive passed StrictBool and CR/LF safety regression checks, focused tests, Ruff, Pyright, coverage generation, and repository policy checks. Its merge is ready for the next PREPARE gate. Pre-edit Grok-auth failure has a completed Codex Power fallback record (non-authoritative).
- Wave-5s-C freeze research: **ACCEPT as research** (research81 + independent review). Docs MD5 `8b94b0135c91fd15fe54ea33e088a4be`.
- Wave-5s-C product-ready research: **ACCEPT offline as handoff only** (research82 + independent review82). Custom ConfirmationStore services required; generic WriteProtocolService insufficient.
- UI all red (339); bulk 92 red; clear not-impl 30; specials not-impl 3; no live token; no UI credentials.

## Verification

- Review82 independent docs re-fetch: ETag `"wcw4x9hqvu3603"`, 147934 bytes, MD5 `8b94b0135c91fd15fe54ea33e088a4be`, byte-identical to research82.
- Independent unauth probes match research82 email/delivery matrix and residual 405 false friends.
- Inventory response_fields for email/delivery remain provisional (no official success samples).
- Coverage honesty: 180/180/0/0, `complete: false`. No research greening. Email/delivery/files specials still red on root.
- The verified Wave-5s-B archive reports 182/182/0/0 and `complete: false`; this is branch evidence only until the labelled root merge and Grok product IR.

## Review decisions (authoritative)

- Wave-5m through Wave-5q freeze/product: **ACCEPT** offline.
- Wave-5r freeze/product independent: **ACCEPT** offline.
- Wave-5s residual/specials research: **ACCEPT as research**.
- Wave-5s-A invoiceLogs research IR: **ACCEPT as research**.
- Wave-5s-B freeze + product-ready research independent: **ACCEPT** offline as handoff only (not product ACCEPT).
- Wave-5s-B Codex fallback review: **ACCEPT as research handoff only**; it cannot discharge the mandatory Grok product audit.
- Wave-5s-C freeze research independent: **ACCEPT as research** (not product ACCEPT).
- Wave-5s-C product-ready research independent: **ACCEPT** offline as handoff only (not product ACCEPT).
- Overall completeness: **FAIL**.

## Open coverage work

1. Merge the archive-verified Wave-5s-B product at the next PREPARE gate, then run the mandatory independent Grok product review.
2. Mandatory Grok product independent review after 5s-B root merge; the existing Codex fallback cannot discharge it.
3. Codex Power Wave-5s-C after 5s-B product IR: email + delivery ticketed pairs per freeze + product-ready research (custom services, target=invoiceId).
4. Later: 405 false friends, transactions, bulk 92, UI/auth/vision.

## Evidence boundaries

- Research ACCEPT / product-ready handoff is not product, live, UI, vision, bulk, or completeness.
- Do not green coverage from research alone.
- Email binds `target=invoiceId`; no `destination_url`; no multi-recipient.
- Delivery: no invented `receiverCvr`/get/list/update; status via invoiceLogs.
- Response roots provisional until live proof.
- Generic WriteProtocolService POST target=None and plural-list success mapping are insufficient for these specials.

## References

- Freeze: `wiki/wave_fivesc_invoice_email_delivery_research.md`
- Freeze IR: `wiki/wave_fivesc_invoice_email_delivery_research_independent_review.md`
- Product-ready: `wiki/wave_fivesc_invoice_email_delivery_product_ready_research.md`
- Product-ready IR: `wiki/wave_fivesc_invoice_email_delivery_product_ready_research_independent_review.md`
- Wave-5s-B fallback: `wiki/wave_fivesb_files_upload_research_codex_fallback_review.md`
- Research scratch: `.fractal/main.billy_complete/tmp/grok-research.md`
- Review scratch: `.fractal/main.billy_complete/tmp/grok-review.md`
