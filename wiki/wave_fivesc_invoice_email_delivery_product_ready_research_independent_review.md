---
name: wave_fivesc_invoice_email_delivery_product_ready_research_independent_review
title: Wave-5s-C product-ready research independent review ACCEPT
desc: Authoritative root Grok acceptance of the cited offline product-ready handoff for ticketed invoice email and invoiceDeliveries specials; product and completeness remain open.
tags: [billy, api, specials, invoices, email, e-invoice, delivery, research, review, product-ready, offline]
sources:
  - https://www.billy.dk/api/
  - https://api.billysbilling.com/v2
  - wiki/wave_fivesc_invoice_email_delivery_product_ready_research.md
  - wiki/wave_fivesc_invoice_email_delivery_research.md
  - wiki/wave_fivesc_invoice_email_delivery_research_independent_review.md
  - wiki/wave_fives_residual_specials_research.md
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
  - coverage/api_v2_manifest.yaml
  - coverage/status.json
  - src/billy_mcp/api/write_protocol.py
  - "parent scratch: .fractal/main.billy_complete/tmp/grok-review.md"
created: 2026-07-30T18:15:00Z
updated: 2026-07-30T18:15:00Z
---

# Wave-5s-C product-ready research independent review ACCEPT

## Verdict

| Claim | Result |
| --- | --- |
| Wave-5s-C product-ready research handoff (research82) | **ACCEPT** offline as implementation handoff only |
| Official documentation versus maintained inventory | **PASS** (provisional response fields retained) |
| Research versus freeze tool/path/request map | **PASS** |
| Unauth method-gate matrix | **PASS** |
| Generic write-protocol insufficiency claim | **PASS** (reproduced on root) |
| Coverage honesty before product | **PASS** |
| Wave-5s-C product implementation | **not accepted** — separate Grok product review required after root integration |
| Wave-5s-B product | **not accepted** here — still requires merge + mandatory Grok product IR |
| Live, UI, vision, bulk, and completeness | **not claimed / fail-closed** |

The authoritative root `INDEPENDENT-REVIEW` Grok step accepted the product-ready
research at scratch `.fractal/main.billy_complete/tmp/grok-research.md`
(research82) against freeze page [[wave_fivesc_invoice_email_delivery_research]],
freeze IR [[wave_fivesc_invoice_email_delivery_research_independent_review]],
product-ready page [[wave_fivesc_invoice_email_delivery_product_ready_research]],
residual ranking [[wave_fives_residual_specials_research]], design high-side-effect
rules, and root baseline **`54b3b1c`**. Full cited findings live outside the public
repository at `.fractal/main.billy_complete/tmp/grok-review.md`.

## Independent verification summary

- Official docs re-fetch: ETag `"wcw4x9hqvu3603"`, 147934 bytes, MD5
  `8b94b0135c91fd15fe54ea33e088a4be` (byte-identical to research82).
- Unauth probes reconfirm email POST open at 401, non-object body 400, non-POST
  405; delivery POST 401; nested delivery create 404; residual 405 false friends
  unchanged.
- Inventory rows `api.special.invoice_email` and `api.special.invoice_delivery`
  remain red (`implemented/contract_tested/live_tested = false`). Root offline
  counts stay **180/180/0/0**, `complete: false`.
- Root has no email/delivery product modules or server registration.
- `WriteProtocolService` still forces POST `target=None`, POST path =
  `collection_path` only, and plural-list success roots — custom
  `ConfirmationStore` services remain the correct product path.

## Non-claims

- Not product ACCEPT for Wave-5s-C or Wave-5s-B.
- Not live, UI, vision, bulk, or completeness ACCEPT.
- No coverage greening from this review.
- No headed browser and no disposable records.

## Next gate

1. Root-merge archive-verified Wave-5s-B product.
2. Mandatory Grok Wave-5s-B product independent review.
3. Only then Codex Power Wave-5s-C product leaf per
   [[wave_fivesc_invoice_email_delivery_product_ready_research]].
