---
name: wave_fivesc_research84_handoff_reconfirm
title: Wave-5s-C research84 handoff reconfirm
desc: Post race-fix reconfirm that official docs and Wave-5s-C email/delivery wire are unchanged; residual clear stays offline-blocked; no coverage greening.
tags: [billy, api, specials, invoices, email, e-invoice, delivery, research, offline]
sources:
  - https://www.billy.dk/api/
  - https://api.billysbilling.com/v2
  - wiki/wave_fivesc_invoice_email_delivery_research.md
  - wiki/wave_fivesc_invoice_email_delivery_product_ready_research.md
  - wiki/wave_fivesc_research83_independent_review.md
  - wiki/offline_write_probe_rules.md
  - coverage/status.json
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
  - "parent scratch: .fractal/main.billy_complete/tmp/grok-research.md (research84)"
created: 2026-07-30T18:55:00Z
updated: 2026-07-30T18:55:00Z
---

# Wave-5s-C research84 handoff reconfirm

## Authority boundary

This page freezes **research reconfirm** after the Wave-5s-B exact-byte upload
race-fix merge. It is not product ACCEPT, live qualification, UI/vision work,
bulk resolution, or completeness. It does not green coverage.

Full probe matrices and scratch snapshots live at
`.fractal/main.billy_complete/tmp/grok-research.md` (research84). Wire freeze
detail remains on [[wave_fivesc_invoice_email_delivery_research]]. Product-ready
detail remains on [[wave_fivesc_invoice_email_delivery_product_ready_research]].

## Official docs fingerprint (this pass)

| Field | Value |
| --- | --- |
| URL | https://www.billy.dk/api/ |
| Access | 2026-07-30T18:52:23Z |
| HTTP | 200 |
| ETag | `"wcw4x9hqvu3603"` |
| Body bytes | 147934 |
| MD5 | `8b94b0135c91fd15fe54ea33e088a4be` |
| Note | Byte-identical to research81–research83 HTML bodies |

Inventory lock metadata in `coverage/status.json` still cites ETag
`hsisik4g9p3603` / MD5 `c2efda0ee4cf9cf200e14910c5fc6996` (access/CDN drift
only). API base remains locked to `https://api.billysbilling.com/v2`. Webhook
count on the public plain extract remains **0**.

## Verdict

| Question | Answer |
| --- | --- |
| Docs drift since research83? | **No** |
| Wave-5s-C wire still frozen? | **Yes** |
| Residual clear offline-productable? | **No** |
| Next Codex product slice | Wave-5s-C four tools after Grok Wave-5s-B product ACCEPT |
| Specials not-impl | 2 (`invoice_email`, `invoice_delivery`) |
| Clear not-impl | 29 (all offline-blocked) |
| Bulk | 92 red |

## Unauthenticated probe posture (reconfirmed)

Access **2026-07-30T18:53:40Z**, locked base only, no credentials, no
persistent records. Matches research83:

- `POST /invoices/:id/emails` with JSON object root → **401**
- non-object body → **400**
- GET/PUT/DELETE emails → **405** POST only
- `POST /invoiceDeliveries` → **401**
- nested `POST /invoices/:id/invoiceDeliveries` → **404** UNKNOWN_RESOURCE
- residual clear POST/PUT geo/ref/postings/associations create → **405**
- `POST`/`PUT` `/transactions` → **401** method open
- `DELETE` transactions / invoiceReminderAssociations missing id → **200** meta-only
- `DELETE` bankPayments → **405**

## Transactions offline block (deepened)

Official `/v2/transactions` Supports create/update/delete, but every property
except immutable required `organization` is marked **readonly**. Unauth method
open is not enough for an offline freeze. Keep
`api.transactions.create|update|delete` red until live non-production evidence
supplies a real body shape and cleanup path. Prefer existing daybook
transaction product tools for journal-style writes.

## Bounded Codex slice (unchanged)

After mandatory Grok product ACCEPT of repaired Wave-5s-B:

1. `api_invoices_send_email_preview` / `api_invoices_send_email_execute`
2. `api_invoice_deliveries_create_preview` / `api_invoice_deliveries_create_execute`

Custom `ConfirmationStore` services only; `target=invoiceId`; no destination
URL; fail-closed provisional responses; contract tests only; live stays red.

## Non-claims

- No coverage greening from this page.
- No live, UI, vision, bulk, or completeness claims.
- No webhook API and no headed browser.
- Research reconfirm is not product ACCEPT for 5s-B or 5s-C.
