---
name: wave_fivesc_research85_product_ready_reconfirm
title: Wave-5s-C research85 product-ready reconfirm
desc: Post-containment-gate reconfirm that official docs and Wave-5s-C email/delivery wire are unchanged; full residual clear 29 unauth matrix; no coverage greening.
tags: [billy, api, specials, invoices, email, e-invoice, delivery, research, offline]
sources:
  - https://www.billy.dk/api/
  - https://api.billysbilling.com/v2
  - wiki/wave_fivesc_invoice_email_delivery_research.md
  - wiki/wave_fivesc_invoice_email_delivery_product_ready_research.md
  - wiki/wave_fivesc_research84_handoff_reconfirm.md
  - wiki/wave_fivesc_research84_independent_review.md
  - wiki/offline_write_probe_rules.md
  - coverage/status.json
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
  - "parent scratch: .fractal/main.billy_complete/tmp/grok-research.md (research85)"
created: 2026-07-30T19:19:00Z
updated: 2026-07-30T19:19:00Z
---

# Wave-5s-C research85 product-ready reconfirm

## Authority boundary

This page freezes **research reconfirm** after research84 IR ACCEPT. The
Wave-5s-B's descriptor-containment repair is merged on root; mandatory Grok
product ACCEPT remains open. This page is not product ACCEPT, live
qualification, UI/vision work, bulk resolution, or completeness. It does not
green coverage.

Full probe matrices and the operator brief live at
`.fractal/main.billy_complete/tmp/grok-research.md` (research85). Wire freeze
detail remains on [[wave_fivesc_invoice_email_delivery_research]]. Product-ready
detail remains on [[wave_fivesc_invoice_email_delivery_product_ready_research]].

## Official docs fingerprint (this pass)

| Field | Value |
| --- | --- |
| URL | https://www.billy.dk/api/ |
| Access | 2026-07-30T19:16:06Z |
| HTTP | 200 |
| ETag | `"wcw4x9hqvu3603"` |
| Body bytes | 147934 |
| MD5 | `8b94b0135c91fd15fe54ea33e088a4be` |
| Note | Byte-identical to research81–research84 HTML bodies |

Inventory lock metadata in `coverage/status.json` still cites ETag
`hsisik4g9p3603` / MD5 `c2efda0ee4cf9cf200e14910c5fc6996` (access/CDN drift
only). API base remains locked to `https://api.billysbilling.com/v2`. Webhook
count on the public plain extract remains **0**. Unauth `GET/POST /webhooks`
returns **404**.

## Verdict

| Question | Answer |
| --- | --- |
| Docs drift since research84? | **No** |
| Wave-5s-C wire still frozen? | **Yes** |
| Residual clear offline-productable? | **No** (full 29-row unauth matrix) |
| Next Codex product slice | Wave-5s-C four tools after Grok Wave-5s-B product ACCEPT |
| Specials not-impl | 2 (`invoice_email`, `invoice_delivery`) |
| Clear not-impl | 29 (all offline-blocked) |
| Bulk | 92 red |
| UI | 339 red (no credentials this pass) |

## Unauthenticated probe posture (reconfirmed)

Access **2026-07-30T19:17:21Z** / residual matrix **2026-07-30T19:18:22Z**,
locked base only, no credentials, no persistent records. Detail:
`tmp/write-probes-research85.json`.

- `POST /invoices/:id/emails` JSON object → **401**; array/null body → **400**;
  GET/PUT/DELETE → **405**
- `POST /invoiceDeliveries` → **401**; nested under invoices → **404**;
  singular DELETE → **405**
- Residual geo/ref/postings/associations create-update → **405** METHOD_NOT_ALLOWED
  with explicit “does not support creating/updating” messages
- `POST`/`PUT` `/transactions` → **401** method open but docs mark all properties
  readonly except immutable organization → still offline-blocked
- `DELETE` transactions / invoiceReminderAssociations missing id → **200** meta-only
- `DELETE` bankPayments/:id → **405**

## Bounded Codex slice (unchanged)

After containment repair merge and mandatory Grok product ACCEPT of Wave-5s-B:

1. `api_invoices_send_email_preview` / `api_invoices_send_email_execute`
2. `api_invoice_deliveries_create_preview` / `api_invoice_deliveries_create_execute`

Custom `ConfirmationStore` services only; `target=invoiceId`; no destination
URL; fail-closed provisional responses; contract tests only; live stays red.

## Non-claims

- No coverage greening from this page.
- No live, UI, vision, bulk, or completeness claims.
- No webhook API and no headed browser.
- Research reconfirm is not product ACCEPT for 5s-B or 5s-C.
