---
name: wave_fivesc_research83_independent_review
title: Wave-5s-C research83 reconfirm independent review ACCEPT
desc: Authoritative root Grok acceptance of the research83 implementation-ready reconfirm for ticketed invoice email and invoiceDeliveries; product and completeness remain open.
tags: [billy, api, specials, invoices, email, e-invoice, delivery, research, review, offline]
sources:
  - https://www.billy.dk/api/
  - https://api.billysbilling.com/v2
  - wiki/wave_fivesc_invoice_email_delivery_research.md
  - wiki/wave_fivesc_invoice_email_delivery_product_ready_research.md
  - wiki/offline_write_probe_rules.md
  - coverage/api_v2_manifest.yaml
  - coverage/status.json
  - src/billy_mcp/api/write_protocol.py
  - src/billy_mcp/api/file_upload_writes.py
  - "parent scratch: .fractal/main.billy_complete/tmp/grok-review.md"
created: 2026-07-30T18:38:00Z
updated: 2026-07-30T18:38:00Z
---

# Wave-5s-C research83 reconfirm independent review ACCEPT

## Verdict

| Claim | Result |
| --- | --- |
| Wave-5s-C research83 reconfirm handoff | **ACCEPT** as research handoff only |
| Official documentation versus inventory (email + delivery) | **PASS** (provisional response fields retained) |
| Unauth method-gate matrix | **PASS** |
| Residual clear ranking (29; 405 majority) | **PASS** as research ranking |
| Generic write-protocol insufficiency claim | **PASS** (reproduced on root) |
| Coverage honesty | **PASS** (182/182/0/0, `complete: false`) |
| Wave-5s-C product implementation | **not accepted** — tools absent |
| Wave-5s-B product ACCEPT | **not accepted** — digest→`read_bytes` race still open; mandatory Grok product IR missing |
| Live, UI, vision, bulk, completeness | **not claimed / fail-closed** |

Full cited findings: `.fractal/main.billy_complete/tmp/grok-review.md` (review83).

## Independent verification summary

- Official docs re-fetch: ETag `"wcw4x9hqvu3603"`, 147934 bytes, MD5
  `8b94b0135c91fd15fe54ea33e088a4be` (byte-identical to research83 HTML).
- Unauth probes reconfirm email POST open at 401, non-POST 405; delivery POST
  401; nested delivery create 404; residual 405 false friends; transactions
  POST 401 still offline-blocked without live property samples.
- Inventory rows `api.special.invoice_email` and `api.special.invoice_delivery`
  remain red. Root offline counts **182/182/0/0**, `complete: false`.
- Root has no email/delivery product modules.
- `WriteProtocolService` still forces POST `target=None`, collection-only POST
  path, and plural-list success roots — custom `ConfirmationStore` services
  remain the correct product path.
- Upload execute still re-hashes identity then calls `read_bytes()` without
  hashing the uploaded buffer against the ticket digest (`file_upload_writes.py`).

## Non-claims

- Not product ACCEPT for Wave-5s-C or Wave-5s-B.
- Not live, UI, vision, bulk, or completeness ACCEPT.
- No coverage greening from this review.
- Codex fallback product review is non-authoritative for Wave-5s-B.

## Next gates

1. Exact-byte upload binding repair + **Grok** product IR of repaired Wave-5s-B.
2. Codex Power Wave-5s-C product leaf per freeze + product-ready + research83.
3. Grok Wave-5s-C product IR after merge.
