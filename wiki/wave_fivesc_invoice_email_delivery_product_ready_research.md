---
name: wave_fivesc_invoice_email_delivery_product_ready_research
title: Wave-5s-C invoice email and delivery product-ready research
desc: Cited product-ready handoff for ticketed invoice email and invoiceDeliveries specials; custom ConfirmationStore services required; no coverage greening.
tags: [billy, api, specials, invoices, email, e-invoice, delivery, research, offline, product-ready]
sources:
  - https://www.billy.dk/api/
  - https://api.billysbilling.com/v2
  - wiki/wave_fivesc_invoice_email_delivery_research.md
  - wiki/wave_fivesc_invoice_email_delivery_research_independent_review.md
  - wiki/offline_write_probe_rules.md
  - wiki/wave_fives_residual_specials_research.md
  - coverage/api_v2_manifest.yaml
  - coverage/status.json
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
  - src/billy_mcp/api/write_protocol.py
  - src/billy_mcp/confirmations.py
  - src/billy_mcp/redaction.py
  - src/billy_mcp/api/invoice_log_reads.py
  - "parent scratch: .fractal/main.billy_complete/tmp/grok-research.md (research82)"
created: 2026-07-30T18:05:00Z
updated: 2026-07-30T18:05:00Z
---

# Wave-5s-C invoice email and delivery product-ready research

## Authority boundary

This page is a **product-ready research handoff** for Codex Power after the
Wave-5s-C freeze ([[wave_fivesc_invoice_email_delivery_research]]) and its
independent research ACCEPT
([[wave_fivesc_invoice_email_delivery_research_independent_review]]).

It is **not** product ACCEPT, live qualification, UI/vision work, bulk
resolution, or completeness. It does **not** green coverage.

Full probe matrices and scratch snapshots live at
`.fractal/main.billy_complete/tmp/grok-research.md` (research82). Wire freeze
detail remains on [[wave_fivesc_invoice_email_delivery_research]].

## Official docs fingerprint (this pass)

| Field | Value |
| --- | --- |
| URL | https://www.billy.dk/api/ |
| Access | 2026-07-30T18:02:53Z |
| HTTP | 200 |
| ETag | `"wcw4x9hqvu3603"` |
| Body bytes | 147934 |
| MD5 | `8b94b0135c91fd15fe54ea33e088a4be` |
| Note | Byte-identical to research81 freeze HTML body |

Inventory lock metadata in `coverage/status.json` still cites ETag
`hsisik4g9p3603` / MD5 `c2efda0ee4cf9cf200e14910c5fc6996` (access/CDN drift
only). API base remains locked to `https://api.billysbilling.com/v2`. Webhook
count on the public plain extract remains **0**.

## Gate order

| Gate | Status |
| --- | --- |
| Wave-5s-C freeze research | **ACCEPT as research** |
| Wave-5s-C freeze independent review | **ACCEPT as research** |
| Wave-5s-B product | Active child; root merge pending |
| Wave-5s-B product independent review | After merge; Grok mandatory |
| This product-ready handoff | Ready for Codex Power **after** 5s-B product IR |
| Wave-5s-C product | Not started |
| Residual clear / bulk / UI | Still blocked offline |

## Unauthenticated probe posture (reconfirmed)

Access **2026-07-30T18:03:24Z**, locked base only, no credentials, no
persistent records.

| Route | Open offline | Closed offline |
| --- | --- | --- |
| `POST /invoices/:id/emails` with JSON object root | **401** AUTHENTICATION_REQUIRED | — |
| same with non-object body | — | **400** INVALID_REQUEST_BODY |
| GET/PUT/DELETE `/invoices/:id/emails` | — | **405** POST only |
| `POST /invoiceDeliveries` | **401** | — |
| GET collection /invoiceDeliveries | **401** (exists; **not** official tool) | — |
| GET singular /invoiceDeliveries/:id | — | **404** RECORD_NOT_FOUND |
| PUT singular | **401** (exists; **not** official tool) | — |
| DELETE singular | — | **405** |
| `POST /invoices/:id/invoiceDeliveries` | — | **404** UNKNOWN_RESOURCE |

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

## Product-ready code binding decisions

### Do not use generic `WriteProtocolService` alone

Root helper rules conflict with the freeze:

1. POST forbids `resource_id` and builds path as `collection_path` only.
2. Email needs nested `/invoices/{invoiceId}/emails`.
3. POST bindings always set `target=None`; email and delivery need
   `target=invoiceId`.
4. Success mapping requires plural list roots; email has no official success
   sample, and delivery inventory names singular `invoiceDelivery`.

**Implement both specials as custom services over `ConfirmationStore` +
`BillyHttpClient.request`**, following the Wave-5s-B binary upload special
pattern (custom preview/execute module), not as pure `WriteOperationSpec`
leaves.

### FastMCP boundary

Apply the upload-child lesson: use strict string annotations at the tool
boundary (`StrictStr` / min_length), forbid extra fields, and keep execute
inputs ticket-only. These tools have no boolean header flags.

### Redaction

`redaction.py` already includes `email`, `emailbody`, `emailsubject`. Tests
must prove body/subject do not leak through error paths.

### Response fields remain provisional

| Row | Inventory response_fields | Offline mapper posture |
| --- | --- | --- |
| email | `changed_records[]` | Fail closed on unknown envelopes; live revises |
| delivery | `invoiceDelivery` | Prefer singular object; fail closed otherwise |

## Offline contract test matrix (minimum)

Shared: preview issues ticket with zero HTTP; one-shot execute; replay;
expiry; wrong tool; invoice/org/payload tamper; base URL lock; no token tool
fields.

Email-specific: nested path uses bound invoiceId only; body root `email`; omit
unset `copyToUserId`; no destination_url; redaction.

Delivery-specific: GLN 13-digit validation; CVR without receiverGln allowed;
never nested create path; never invent fields; status via invoice logs only.

## Residual after this slice

After 5s-B and 5s-C offline product IR, specials not-impl should be **0**.
Remaining offline-blocked clear rows stay: 405 false friends, transactions
CUD, bankPayments delete, associations delete. Ambiguous bulk **92** stay red.
UI/auth/vision remain red without credentials and live organisation work.

## Non-claims

- No coverage greening from this page.
- No live, UI, vision, bulk, or completeness claims.
- No webhook API and no headed browser.
- Research handoff is not product ACCEPT.
