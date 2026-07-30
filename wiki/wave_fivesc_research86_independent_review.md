---
name: wave_fivesc_research86_independent_review
title: Wave-5s-C research86 independent review ACCEPT
desc: Authoritative root Grok acceptance of the research86 product implementation handoff for ticketed invoice email and invoiceDeliveries; product and completeness remain open.
tags: [billy, api, specials, invoices, email, e-invoice, delivery, research, review, offline]
sources:
  - https://www.billy.dk/api/
  - https://api.billysbilling.com/v2
  - wiki/wave_fivesc_research86_product_implementation_handoff.md
  - wiki/wave_fivesc_invoice_email_delivery_research.md
  - wiki/wave_fivesc_invoice_email_delivery_product_ready_research.md
  - wiki/wave_fivesc_research85_independent_review.md
  - wiki/offline_write_probe_rules.md
  - coverage/api_v2_manifest.yaml
  - coverage/status.json
  - src/billy_mcp/api/write_protocol.py
  - "parent scratch: .fractal/main.billy_complete/tmp/grok-review.md"
created: 2026-07-30T19:52:00Z
updated: 2026-07-30T19:52:00Z
---

# Wave-5s-C research86 independent review ACCEPT

## Verdict

| Claim | Result |
| --- | --- |
| Wave-5s-C research86 product implementation handoff | **ACCEPT** as research handoff only |
| Official documentation versus inventory (email + delivery) | **PASS** (provisional response fields retained) |
| Unauth method-gate matrix | **PASS** |
| Residual clear ranking (29; 405 majority; transactions blocked) | **PASS** as research ranking |
| Generic write-protocol insufficiency claim | **PASS** (reproduced on root) |
| Coverage honesty | **PASS** (182/182/0/0, `complete: false`) |
| Wave-5s-C product implementation | **not accepted** — tools absent on root |
| Live, UI, vision, bulk, completeness | **not claimed / fail-closed** |

Full cited findings: `.fractal/main.billy_complete/tmp/grok-review.md` (review86).

## Independent verification summary

- Official docs re-fetch: ETag `"wcw4x9hqvu3603"`, 147934 bytes, MD5
  `8b94b0135c91fd15fe54ea33e088a4be` (byte-identical to research86 HTML).
- Unauth probes reconfirm email POST open at 401, non-object/empty body 400,
  non-POST 405; delivery POST 401; nested delivery create 404; webhooks 404;
  residual 405 false friends; transactions POST still offline-blocked by
  property table (readonly except immutable organization).
- Inventory rows `api.special.invoice_email` and `api.special.invoice_delivery`
  remain red. Root offline counts **182/182/0/0**, `complete: false`.
- Root has no email/delivery product modules.
- `WriteProtocolService` still forces POST `target=None`, collection-only POST
  path, and plural-list success roots — custom `ConfirmationStore` services
  remain the correct product path for Wave-5s-C.
- Active product leaf `wave5sc_email_delivery_product` is expected; product IR
  waits for root merge.

## Sequencing

Wave-5s-C research implementation handoff is discharged. Codex Power product
leaf may continue. Product ACCEPT and live/UI/bulk/completeness stay closed.

## Non-claims

- Not completeness, live, UI, vision, bulk, or product ACCEPT.
- Research86 ACCEPT is not Wave-5s-C product ACCEPT.
