---
name: wave_fivesc_invoice_email_delivery_research
title: Wave-5s-C invoice email and e-invoice delivery research
desc: Cited offline freeze for ticketed POST invoice emails and invoiceDeliveries specials; high side effect; no coverage greening.
tags: [billy, api, specials, invoices, email, e-invoice, delivery, research, offline]
sources:
  - https://www.billy.dk/api/
  - https://api.billysbilling.com/v2
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
  - wiki/wave_fives_residual_specials_research.md
  - wiki/offline_write_probe_rules.md
  - coverage/api_v2_manifest.yaml
  - coverage/status.json
  - src/billy_mcp/confirmations.py
  - src/billy_mcp/api/write_protocol.py
  - src/billy_mcp/api/invoice_log_reads.py
  - "parent scratch: .fractal/main.billy_complete/tmp/grok-research.md (research81)"
created: 2026-07-30T17:41:00Z
updated: 2026-07-30T17:41:00Z
---

# Wave-5s-C invoice email and e-invoice delivery research

## Authority boundary

This page freezes **research evidence** for the two remaining high side-effect
specials after Wave-5s-A invoiceLogs and Wave-5s-B files upload work. It is not
product ACCEPT, live qualification, UI/vision work, bulk resolution, or
completeness. It does not green coverage.

Full probe matrices and the operator brief live at
`.fractal/main.billy_complete/tmp/grok-research.md` (research81). Residual
ranking: [[wave_fives_residual_specials_research]].

## Gate status

| Gate | Status |
| --- | --- |
| Wave-5s residual ranking | **ACCEPT as research** |
| Wave-5s-A invoiceLogs product | **Merged** offline |
| Wave-5s-B files upload product-ready research IR | **ACCEPT** offline as handoff |
| Wave-5s-B product | Active child or merge pending |
| Wave-5s-C freeze research | **Ready** (this page) |
| Wave-5s-C freeze independent review | **ACCEPT as research** ([[wave_fivesc_invoice_email_delivery_research_independent_review]]) |
| Wave-5s-C product | After 5s-B product IR |
| Root offline baseline at freeze | 180 implemented + contract_tested; live 0; vision 0; `complete: false` |

## Official docs fingerprint

| Field | Value |
| --- | --- |
| URL | https://www.billy.dk/api/ |
| HTTP | 200 |
| ETag | `"wcw4x9hqvu3603"` |
| Body bytes | 147934 |
| MD5 | `8b94b0135c91fd15fe54ea33e088a4be` |
| Note | Byte-identical to research80 HTML body |

Inventory lock metadata in `coverage/status.json` still cites ETag
`hsisik4g9p3603` / MD5 `c2efda0ee4cf9cf200e14910c5fc6996` (access/CDN drift only).

API base remains locked to `https://api.billysbilling.com/v2`.

## Inventory rows

| Inventory id | Preview tool | Execute twin | Route |
| --- | --- | --- | --- |
| `api.special.invoice_email` | `api_invoices_send_email_preview` | `api_invoices_send_email_execute` | `POST /v2/invoices/:invoiceId/emails` |
| `api.special.invoice_delivery` | `api_invoice_deliveries_create_preview` | `api_invoice_deliveries_create_execute` | `POST /v2/invoiceDeliveries` |

Neither route is in the Resource Documentation Supports TOC. Both are special
narrative endpoints (same class as invoiceLogs and binary files upload).

## Wire contracts

### Sending emails for invoices

```http
POST /v2/invoices/:invoiceId/emails
```

Body root `email` with required `contactPersonId`, `emailBody`, `emailSubject`;
optional `copyToUserId`. One contact person per call. Addresses come from the
contact person (and optional copy user), not from caller-supplied destinations.
Unauth: JSON object POST **401**; empty body **400** `INVALID_REQUEST_BODY`;
GET/PUT/DELETE **405** (POST only).

Ticket must bind `target=invoiceId` and the canonical `email` request. Do not
set `destination_url` (no absolute URL on the wire).

### Sending an invoice as an e-invoice

```http
POST /v2/invoiceDeliveries
```

Body root `invoiceDelivery` with `invoiceId`, `organizationId`,
`receiverIdType` (`gln`|`cvr`), optional `receiverGln` (required and exactly 13
digits when `gln`), optional `orderReference`, and `senderUserId`. Invoice must
be approved. Status via existing `api_invoice_logs_list`, not `sentState`.
Unauth POST **401**. Nested `/invoices/:id/invoiceDeliveries` is
`UNKNOWN_RESOURCE` **404**. Singular DELETE **405**. Collection GET and singular
PUT are method-open offline but **not** official product scope for this slice.

Do not invent `receiverCvr`. Do not invent get/list/update delivery tools.

## Response body gap

Official samples show **no** success response body for either special.
Inventory currently lists email `changed_records[]` and delivery
`invoiceDelivery`. Offline mappers must fail closed or map only after contract
tests define mock shapes; live non-production must prove real roots before
`live_tested`.

## Unauthenticated probe summary (2026-07-30T17:40:57Z)

Base `https://api.billysbilling.com/v2`, no token, no persistent records.
Detail: `tmp/write-probes-research81.json`.

| Area | Result |
| --- | --- |
| emails POST object body | **401** AUTHENTICATION_REQUIRED |
| emails empty body | **400** INVALID_REQUEST_BODY |
| emails GET/PUT/DELETE | **405** POST only |
| invoiceDeliveries POST | **401** |
| invoiceDeliveries GET collection | **401** (not productised) |
| invoiceDeliveries GET :id | **404** RECORD_NOT_FOUND |
| invoiceDeliveries PUT :id | **401** (not productised) |
| invoiceDeliveries DELETE :id | **405** |
| nested invoices/:id/invoiceDeliveries POST | **404** UNKNOWN_RESOURCE |

## Product slice (Codex Power)

After Wave-5s-B product merge and product IR:

1. Implement both ticketed pairs only.
2. Nested email path with `target=invoiceId` binding (write-protocol POST default
   target is null; specialise binding).
3. Flat delivery create; local gln/13-digit validation; org id on ticket.
4. Contract tests: preview/execute, replay, expiry, wrong tool, payload/org/target
   tamper, redaction of email body/subject.
5. Green only via `OFFLINE_API_IMPLEMENTATION_EVIDENCE` for the two special rows.
6. Leave `live_tested` false; irreversible external side effects need dedicated
   non-production destinations later.

## Non-claims

- No coverage greening from this page.
- No live, UI, vision, bulk, or completeness claims.
- No webhook API.
- No headed browser and no disposable records in research.
