---
name: wave_fivesc_research86_product_implementation_handoff
title: Wave-5s-C research86 product implementation handoff
desc: Post-upload-ACCEPT reconfirm that official docs and Wave-5s-C email/delivery wire are unchanged; sequencing gate open for Codex Power product leaf; residual clear stays offline-blocked; no coverage greening.
tags: [billy, api, specials, invoices, email, e-invoice, delivery, research, offline, product-ready]
sources:
  - https://www.billy.dk/api/
  - https://api.billysbilling.com/v2
  - wiki/wave_fivesc_invoice_email_delivery_research.md
  - wiki/wave_fivesc_invoice_email_delivery_product_ready_research.md
  - wiki/wave_fivesc_research85_independent_review.md
  - wiki/offline_write_probe_rules.md
  - coverage/api_v2_manifest.yaml
  - coverage/status.json
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
  - src/billy_mcp/api/write_protocol.py
  - src/billy_mcp/api/file_upload_writes.py
  - src/billy_mcp/confirmations.py
  - "parent scratch: .fractal/main.billy_complete/tmp/grok-research.md (research86)"
created: 2026-07-30T19:45:00Z
updated: 2026-07-30T19:45:00Z
---

# Wave-5s-C research86 product implementation handoff

## Authority boundary

This page is a **product implementation handoff** after research85 independent review ACCEPT of the product-ready reconfirm and offline product ACCEPT of the containment-repaired file upload ([[wave_fivesc_research85_independent_review]]).

It is **not** product ACCEPT, live qualification, UI/vision work, bulk resolution, or completeness. It does **not** green coverage.

Full probe matrices and scratch snapshots live at
`.fractal/main.billy_complete/tmp/grok-research.md` (research86). Wire freeze
detail remains on [[wave_fivesc_invoice_email_delivery_research]]. Product-ready
code binding remains on [[wave_fivesc_invoice_email_delivery_product_ready_research]].

## Official docs fingerprint (this pass)

| Field | Value |
| --- | --- |
| URL | https://www.billy.dk/api/ |
| Access | 2026-07-30T19:42:21Z |
| HTTP | 200 |
| ETag | `"wcw4x9hqvu3603"` |
| Body bytes | 147934 |
| MD5 | `8b94b0135c91fd15fe54ea33e088a4be` |
| Note | Byte-identical to research81–research85 HTML body |

Inventory lock metadata in `coverage/status.json` still cites ETag
`hsisik4g9p3603` / MD5 `c2efda0ee4cf9cf200e14910c5fc6996` (access/CDN drift
only). API base remains locked to `https://api.billysbilling.com/v2`. Webhook
count on the public plain extract remains **0**.

## Sequencing gate

| Gate | Status |
| --- | --- |
| Wave-5s-B containment repair merged | **Done** |
| Wave-5s-B offline product ACCEPT (Grok) | **Done** (review85) |
| Wave-5s-C freeze + product-ready + reconfirms | **ACCEPT as research** |
| This implementation handoff | **Open for Codex Power product leaf** |
| Wave-5s-C product | Not started |
| Residual clear / bulk / UI | Still blocked offline |

## Unauthenticated probe posture (reconfirmed)

Access **2026-07-30T19:42:21Z**, locked base only, no credentials, no
persistent records.

| Route | Open offline | Closed offline |
| --- | --- | --- |
| `POST /invoices/:id/emails` with JSON object root | **401** AUTHENTICATION_REQUIRED | — |
| same with non-object / empty body | — | **400** INVALID_REQUEST_BODY |
| GET/PUT/DELETE `/invoices/:id/emails` | — | **405** POST only |
| `POST /invoiceDeliveries` | **401** | — |
| GET collection /invoiceDeliveries | **401** (exists; **not** official tool) | — |
| GET singular /invoiceDeliveries/:id | — | **404** RECORD_NOT_FOUND |
| PUT singular | **401** (exists; **not** official tool) | — |
| DELETE singular | — | **405** |
| `POST /invoices/:id/invoiceDeliveries` | — | **404** UNKNOWN_RESOURCE |
| `GET/POST /webhooks` | — | **404** UNKNOWN_RESOURCE |

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

## Product implementation rules (Codex Power)

1. Custom `ConfirmationStore` services following `file_upload_writes.py`.
2. Do **not** use generic `WriteProtocolService` alone: POST sets `target=None`,
   collection-only path, plural-list success roots — incompatible with nested
   email path and provisional singular delivery response.
3. Strict Pydantic; execute ticket-only; no boolean approval flags.
4. Fail closed on unknown success envelopes offline.
5. Redact email body/subject on all error paths.
6. No automatic retry after external-send POST.
7. Green only offline `implemented` + `contract_tested` for the two special rows;
   keep `live_tested` false; keep `complete: false`.

## Residual after this slice

After 5s-C offline product IR, specials not-impl should be **0**.
Remaining offline-blocked clear rows stay at **29** (405 false friends,
transactions CUD, bankPayments delete, associations delete). Ambiguous bulk
**92** stay red. UI/auth/vision remain red without credentials and live
organisation work.

## Non-claims

- No coverage greening from this page.
- No live, UI, vision, bulk, or completeness claims.
- No webhook API and no headed browser.
- Research handoff is not product ACCEPT.
