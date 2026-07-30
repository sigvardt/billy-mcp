---
name: wave_fivesc_research87_independent_review
title: Wave-5s-C research87 independent review and product ACCEPT offline
desc: Authoritative root Grok acceptance of research87 reconfirm and offline product ACCEPT of ticketed invoice email and invoiceDeliveries; live, UI, residual, bulk, and completeness remain open.
tags: [billy, api, specials, invoices, email, e-invoice, delivery, research, review, offline, product]
sources:
  - https://www.billy.dk/api/
  - https://api.billysbilling.com/v2
  - wiki/wave_fivesc_research87_product_in_flight_reconfirm.md
  - wiki/wave_fivesc_invoice_email_delivery_research.md
  - wiki/wave_fivesc_invoice_email_delivery_product_ready_research.md
  - wiki/wave_fivesc_research86_independent_review.md
  - wiki/offline_write_probe_rules.md
  - coverage/api_v2_manifest.yaml
  - coverage/status.json
  - src/billy_mcp/api/invoice_email_delivery_writes.py
  - tests/api/test_invoice_email_delivery_writes.py
  - "parent scratch: .fractal/main.billy_complete/tmp/grok-review.md (review87)"
created: 2026-07-30T20:10:00Z
updated: 2026-07-30T20:10:00Z
---

# Wave-5s-C research87 independent review and product ACCEPT offline

## Verdict

| Claim | Result |
| --- | --- |
| Wave-5s-C research87 product in-flight reconfirm | **ACCEPT** as research only |
| Official documentation versus inventory (email + delivery) | **PASS** (provisional response fields retained) |
| Unauth method-gate matrix | **PASS** |
| Residual clear ranking (29 offline-blocked) | **PASS** as research ranking |
| Coverage honesty | **PASS** (184/184/0/0, `complete: false`) |
| Wave-5s-C product implementation on root | **ACCEPT** offline only; `live_tested` false |
| Live, UI, vision, bulk, residual freezes, completeness | **not claimed / fail-closed** |

Full cited findings: `.fractal/main.billy_complete/tmp/grok-review.md` (review87).

## Independent verification summary

- Official docs re-fetch: ETag `"wcw4x9hqvu3603"`, 147934 bytes, MD5
  `8b94b0135c91fd15fe54ea33e088a4be` (byte-identical to research81–87 claim).
- Unauth probes reconfirm email POST open at 401, non-object body 400, non-POST
  405; delivery POST 401; nested delivery create 404; webhooks 404; residual
  405 false friends; transactions POST still offline-blocked by property table
  (readonly except immutable organization).
- Inventory rows `api.special.invoice_email` and `api.special.invoice_delivery`
  are offline green (`implemented` + `contract_tested`) with `live_tested`
  false. Root offline counts **184/184/0/0**, `complete: false`.
- Product module `src/billy_mcp/api/invoice_email_delivery_writes.py` is on
  root via merge `0efceae`. Four ticketed tools only. Custom
  `ConfirmationStore` services. Nested email path and collection delivery path
  match official docs. No `receiverCvr`, multi-recipient, destination URL, or
  invented delivery CRUD tools.
- Focused suite `tests/api/test_invoice_email_delivery_writes.py`: **32
  passed** (strict inputs, no-preview HTTP, exact URL/JSON, ticket
  tamper/replay/expiry/wrong tool, fail-closed envelopes, redaction, base URL
  lock, no retry, auth required).
- Root commit-mode verification: **1,255 non-live tests passed**, alongside
  Ruff, Pyright, coverage-inventory, and repository-policy checks.

## Sequencing

Wave-5s-C offline product gate is discharged. Residual clear **29**, bulk
**92**, UI/auth/vision, and live external-send qualification remain closed
without a non-production token and further research freezes.

## Non-claims

- Not completeness, live, UI, vision, or bulk ACCEPT.
- Research87 ACCEPT is research only.
- Product ACCEPT is offline only; do not set `live_tested` without non-production proof.
