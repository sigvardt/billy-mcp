---
name: wave_fivesc_research87_product_in_flight_reconfirm
title: Wave-5s-C research87 product in-flight reconfirm
desc: Post-research86 reconfirm that official docs and Wave-5s-C email/delivery wire are unchanged while the Codex Power product leaf is active; residual clear stays offline-blocked; no coverage greening.
tags: [billy, api, specials, invoices, email, e-invoice, delivery, research, offline, product-ready]
sources:
  - https://www.billy.dk/api/
  - https://api.billysbilling.com/v2
  - wiki/wave_fivesc_invoice_email_delivery_research.md
  - wiki/wave_fivesc_invoice_email_delivery_product_ready_research.md
  - wiki/wave_fivesc_research86_product_implementation_handoff.md
  - wiki/wave_fivesc_research86_independent_review.md
  - wiki/offline_write_probe_rules.md
  - coverage/api_v2_manifest.yaml
  - coverage/status.json
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
  - src/billy_mcp/api/write_protocol.py
  - src/billy_mcp/api/file_upload_writes.py
  - src/billy_mcp/confirmations.py
  - "parent scratch: .fractal/main.billy_complete/tmp/grok-research.md (research87)"
created: 2026-07-30T19:58:00Z
updated: 2026-07-30T19:58:00Z
---

# Wave-5s-C research87 product in-flight reconfirm

## Authority boundary

This page is an **in-flight product reconfirm** after research86 independent review ACCEPT of the product implementation handoff ([[wave_fivesc_research86_independent_review]]) and while the Codex Power product leaf is active.

It is **not** product ACCEPT, live qualification, UI/vision work, bulk resolution, or completeness. It does **not** green coverage. Observing a child worktree WIP module is **not** an independent product review.

Full probe matrices and scratch snapshots live at
`.fractal/main.billy_complete/tmp/grok-research.md` (research87). Wire freeze
detail remains on [[wave_fivesc_invoice_email_delivery_research]]. Product-ready
code binding remains on [[wave_fivesc_invoice_email_delivery_product_ready_research]].
Implementation handoff remains on [[wave_fivesc_research86_product_implementation_handoff]].

## Official docs fingerprint (this pass)

| Field | Value |
| --- | --- |
| URL | https://www.billy.dk/api/ |
| Access | 2026-07-30T19:58:00Z |
| HTTP | 200 |
| ETag | `"wcw4x9hqvu3603"` |
| Body bytes | 147934 |
| MD5 | `8b94b0135c91fd15fe54ea33e088a4be` |
| Note | Byte-identical to research81–research86 HTML body |

Inventory lock metadata in `coverage/status.json` still cites ETag
`hsisik4g9p3603` / MD5 `c2efda0ee4cf9cf200e14910c5fc6996` (access/CDN drift
only). API base remains locked to `https://api.billysbilling.com/v2`. Webhook
count on the public plain extract remains **0**.

## Sequencing gate

| Gate | Status |
| --- | --- |
| Wave-5s-B containment repair merged | **Done** |
| Wave-5s-B offline product ACCEPT (Grok) | **Done** (review85) |
| Wave-5s-C freeze + product-ready + research83–86 | **ACCEPT as research** |
| Wave-5s-C product leaf | **Active** (`wave5sc_email_delivery_product`) |
| This in-flight reconfirm | Wire + residual blocks unchanged; finish leaf only |
| Wave-5s-C product independent review | After merge to root |
| Residual clear / bulk / UI | Still blocked offline |

## Unauthenticated probe posture (reconfirmed)

Access **2026-07-30T19:58:00Z**, locked base only, no credentials, no
persistent records.

| Route | Open offline | Closed offline |
| --- | --- | --- |
| `POST /invoices/:id/emails` with JSON object root | **401** AUTHENTICATION_REQUIRED | — |
| same with non-object / empty body | — | **400** INVALID_REQUEST_BODY |
| `GET /invoices/:id/emails` | — | **405** POST only |
| `PUT /invoices/:id/emails` no body | — | **400** body parser first |
| `PUT /invoices/:id/emails` with JSON body | — | **405** POST only (explicit message) |
| `DELETE /invoices/:id/emails` | — | **405** POST only |
| `POST /invoiceDeliveries` | **401** | — |
| GET collection /invoiceDeliveries | **401** (exists; **not** official tool) | — |
| GET singular /invoiceDeliveries/:id | — | **404** RECORD_NOT_FOUND |
| PUT singular | **401** (exists; **not** official tool) | — |
| DELETE singular | — | **405** |
| `POST /invoices/:id/invoiceDeliveries` | — | **404** UNKNOWN_RESOURCE |

Residual samples reconfirmed: `POST` countries/currencies/postings **405**;
`POST` transactions **401** but property table blocks offline freeze;
`DELETE` bankPayments **405**; `DELETE` invoiceReminderAssociations missing id
**200** (not cleanup proof); webhooks **404**.

## Wire contract (unchanged)

### Email

- Tools: `api_invoices_send_email_preview` / `api_invoices_send_email_execute`
- Path: `POST /v2/invoices/:invoiceId/emails`
- Body root: `email` with required `contactPersonId`, `emailBody`,
  `emailSubject`; optional `copyToUserId`
- One contact person per call; no raw recipient addresses; no multi-recipient
- Ticket `target` = `invoiceId`; no `destination_url`
- High side effect; live stays red until dedicated non-production path

### Delivery

- Tools: `api_invoice_deliveries_create_preview` /
  `api_invoice_deliveries_create_execute`
- Path: `POST /v2/invoiceDeliveries` only (never nested under invoices)
- Body root: `invoiceDelivery` with `invoiceId`, `organizationId`,
  `receiverIdType` (`gln`|`cvr`), optional `receiverGln` / `orderReference`,
  required `senderUserId` per inventory
- When `gln`, `receiverGln` required and exactly 13 digits
- Do **not** invent `receiverCvr`
- Ticket `organization_id` = payload organization; `target` = invoiceId
- Status via existing `api_invoice_logs_list`
- Do **not** productise get/list/update/delete invoiceDeliveries offline

## Bounded Codex Power slice

Finish the active product leaf only. Four tools. Two special inventory rows.
Offline `implemented` + `contract_tested` only. Keep `live_tested` false.
Custom `ConfirmationStore` services required; do not rely on generic
`WriteProtocolService` alone.

After leaf merge: Grok product independent review. Residual clear **29**, bulk
**92**, UI **339**, and completeness remain out of scope without live token or
docs change.

## Residual clear 29 (still offline-blocked)

accountNatures create/update; balanceModifiers create/update;
bankPayments.delete; cities create/update; contactBalancePostings
create/update; countryGroups create/update; countries create/update;
currencies create/update; invoiceReminderAssociations create/update/delete;
locales create/update; postings create/update; states create/update;
transactions create/update/delete; zipcodes create/update.

## Non-claims

- No coverage greening from research.
- No live token, headed browser, disposable records, or retained frames.
- Research reconfirm is not product ACCEPT.
- Child WIP observation is not product ACCEPT.
