---
name: wave_fivesc_research85_independent_review
title: Wave-5s-C research85 independent review and Wave-5s-B offline product ACCEPT
desc: Authoritative root Grok acceptance of research85 handoff and offline product ACCEPT of containment-repaired file upload; Wave-5s-C product and completeness remain open.
tags: [billy, api, specials, invoices, email, e-invoice, delivery, upload, research, review, offline]
sources:
  - https://www.billy.dk/api/
  - https://api.billysbilling.com/v2
  - wiki/wave_fivesc_research85_product_ready_reconfirm.md
  - wiki/wave_fivesc_invoice_email_delivery_research.md
  - wiki/wave_fivesc_invoice_email_delivery_product_ready_research.md
  - wiki/wave_fivesc_research84_independent_review.md
  - wiki/offline_write_probe_rules.md
  - coverage/api_v2_manifest.yaml
  - coverage/status.json
  - src/billy_mcp/api/file_upload_writes.py
  - tests/api/test_file_upload_writes.py
  - "parent scratch: .fractal/main.billy_complete/tmp/grok-review.md"
created: 2026-07-30T19:32:00Z
updated: 2026-07-30T19:32:00Z
---

# Wave-5s-C research85 independent review and Wave-5s-B offline product ACCEPT

## Verdict

| Claim | Result |
| --- | --- |
| Wave-5s-C research85 product-ready reconfirm | **ACCEPT** as research handoff only |
| Official documentation versus inventory (email + delivery) | **PASS** (provisional response fields retained) |
| Unauth method-gate matrix | **PASS** |
| Residual clear ranking (29; 405 majority; transactions blocked) | **PASS** as research ranking |
| Generic write-protocol insufficiency claim | **PASS** (reproduced on root) |
| Coverage honesty | **PASS** (182/182/0/0, `complete: false`) |
| Wave-5s-C product implementation | **not accepted** — tools absent |
| Wave-5s-B offline product ACCEPT (containment-repaired upload) | **ACCEPT** offline only; `live_tested` false |
| Live, UI, vision, bulk, completeness | **not claimed / fail-closed** |

Full cited findings: `.fractal/main.billy_complete/tmp/grok-review.md` (review85).

## Independent verification summary

- Official docs re-fetch: ETag `"wcw4x9hqvu3603"`, 147934 bytes, MD5
  `8b94b0135c91fd15fe54ea33e088a4be` (byte-identical to research85 HTML).
- Unauth probes reconfirm email POST open at 401, non-POST 405; delivery POST
  401; nested delivery create 404; residual 405 false friends; transactions
  POST/PUT 401 still offline-blocked (property table readonly except immutable
  organization); webhooks 404.
- Inventory rows `api.special.invoice_email` and `api.special.invoice_delivery`
  remain red. Root offline counts **182/182/0/0**, `complete: false`.
- Root has no email/delivery product modules.
- `WriteProtocolService` still forces POST `target=None`, collection-only POST
  path, and plural-list success roots — custom `ConfirmationStore` services
  remain the correct product path for Wave-5s-C.
- Upload execute uses configured-root descriptor traversal with `O_NOFOLLOW`,
  same-descriptor read/hash/send, and focused tests for same-digest terminal and
  intermediate symlink races (`FILE_NOT_ALLOWED`, zero HTTP). Focused suite:
  **38 passed**.

## Sequencing

Wave-5s-B mandatory Grok product gate is discharged **offline**. Codex Power may
start the Wave-5s-C four-tool product leaf. Live/UI/bulk/completeness stay closed.
Codex fallback product-review children remain non-authoritative.

## Non-claims

- Not completeness, live, UI, vision, or bulk ACCEPT.
- Research85 ACCEPT is not Wave-5s-C product ACCEPT.
- Wave-5s-B product ACCEPT is offline only; live upload stays red.
