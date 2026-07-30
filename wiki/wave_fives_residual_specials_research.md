---
name: wave_fives_residual_specials_research
title: Wave-5s residual clear and specials research
desc: Cited post-Wave-5r residual ranking for remaining clear not-impl and four special routes; invoiceLogs list is the recommended first offline residual product; no coverage greening from research.
tags: [billy, api, specials, residual, writes, research, offline]
sources:
  - https://www.billy.dk/api/
  - https://api.billysbilling.com/v2
  - wiki/offline_write_probe_rules.md
  - wiki/billy_api_v2_research_seed.md
  - wiki/wave_fiver_freeze_independent_review.md
  - wiki/wave_fiver_product_implementation_research.md
  - coverage/api_v2_manifest.yaml
  - coverage/status.json
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
  - "parent scratch: .fractal/main.billy_complete/tmp/grok-research.md (research77)"
created: 2026-07-30T16:05:00Z
updated: 2026-07-30T16:28:00Z
---

# Wave-5s residual clear and specials research

## Authority boundary

This page freezes **research evidence** for residual clear not-impl and the four
red special routes after Wave-5r product work. It is not product ACCEPT, live
qualification, UI/vision work, bulk resolution, or completeness. It does not
green coverage.

Full probe matrices and scratch snapshots live at
`.fractal/main.billy_complete/tmp/grok-research.md` (research77 ranking;
research78 deepens Wave-5s-A). InvoiceLogs list offline freeze detail:
[[wave_fivesa_invoice_logs_list_research]].

## Gate status

| Gate | Status |
| --- | --- |
| Wave-5r freeze IR | **ACCEPT** ([[wave_fiver_freeze_independent_review]]) |
| Wave-5r product on root | **Merged + product IR ACCEPT offline** ([[wave_fiver_product_independent_review]] @ `5ad69a6`) |
| Root offline baseline | 179 implemented + contract_tested; live 0; vision 0; `complete: false` |
| Clear not-impl on root | 30 |
| Specials not-impl | 4 |
| Ambiguous bulk | 92 red |
| Wave-5s-A research | **Ready** ([[wave_fivesa_invoice_logs_list_research]]) |

## Official docs fingerprint

| Field | Value |
| --- | --- |
| URL | https://www.billy.dk/api/ |
| HTTP | 200 |
| ETag | `"wcw4x9hqvu3603"` |
| Body bytes | 147934 |
| MD5 | `8b94b0135c91fd15fe54ea33e088a4be` |
| Note | Byte-identical to research76 HTML body |

Inventory lock metadata in `coverage/status.json` still cites ETag
`hsisik4g9p3603` / MD5 `c2efda0ee4cf9cf200e14910c5fc6996` (access/CDN drift only).

API base remains locked to `https://api.billysbilling.com/v2`. Sample upload curl
host `api.billy.dk` must never become the client base.

## Residual ranking (offline)

### A. Next offline products (method open + documented shape)

| Priority | Inventory id | Wire | Offline note |
| --- | --- | --- | --- |
| 1 | `api.special.invoice_logs` | `GET /invoiceLogs` | List special; side effects none; filters from narrative |
| 2 | `api.special.files_upload` (+ pair `api.files.create`) | `POST /files` binary | Ticket binds path + digest; not JSON create |
| 3 | `api.special.invoice_email` | `POST /invoices/:invoiceId/emails` | Ticketed; external email |
| 4 | `api.special.invoice_delivery` | `POST /invoiceDeliveries` | Ticketed; async e-invoice; poll logs |

### B. Blocked offline (keep red)

| Bucket | Rows | Why |
| --- | --- | --- |
| 405 false friends | accountNatures, balanceModifiers, cities, countries, countryGroups, currencies, locales, states, zipcodes, postings, contactBalancePostings, invoiceReminderAssociations create/update | Unauth POST/PUT **405** overrides Supports |
| bankPayments delete | `api.bankPayments.delete` | Unauth DELETE **405** despite Supports delete |
| transactions CUD | create/update/delete | Property table all readonly offline; DELETE 200 meta-only is not cleanup |
| associations delete | `api.invoiceReminderAssociations.delete` | Unauth DELETE 200 meta-only; needs live cleanup proof |
| bulk | all 92 | No body contract on official page |
| webhooks | none | 0 official mentions |

## Special contracts (official narrative)

### invoiceLogs list

```http
GET /v2/invoiceLogs?invoiceId=…&organizationId=…&sortProperty=eventTime&sortDirection=DESC
```

Success root: `invoiceLogs[]`. Sample entry fields: `type` (`received`,
`signedoff`, `failed`), `message`, `messageKey`, `eventTime`.  
Unauth: collection GET **401**; synthetic id GET **404**.  
Tool: `api_invoice_logs_list` (read-only; no preview/execute pair).

### files upload

```http
POST /v2/files
```

Headers: auth, `X-Filename`, `Content-Type`, optional `x-create-attachment`,
`x-create-variants`, `x-organizationid`, `x-should-scan`. Body: raw bytes.  
Response roots: `files[]`, optional `attachments[]`.  
Resource Supports create; property table all readonly — JSON create is not the
documented path. Tools: `api_files_upload_preview` / `api_files_upload_execute`.

### invoice email

```http
POST /v2/invoices/:invoiceId/emails
```

Body root `email` with required `contactPersonId`, `emailBody`, `emailSubject`;
optional `copyToUserId`. One contact person per call. Unauth POST **401**.

### invoice delivery

```http
POST /v2/invoiceDeliveries
```

Body root `invoiceDelivery` with `invoiceId`, `organizationId`,
`receiverIdType` (`gln`|`cvr`), optional `receiverGln` (13 digits when gln),
`orderReference`, `senderUserId`. Invoice must be approved. Status via
invoiceLogs, not `sentState`. Unauth POST **401**.

## Unauthenticated probe summary (2026-07-30T16:03:17Z)

Base `https://api.billysbilling.com/v2`, JSON `{}` for POST/PUT, no token, no
persistent records. Detail: `tmp/write-probes-research77.json`.

| Area | Result |
| --- | --- |
| specials files/email/delivery POST, invoiceLogs GET | **401** AUTHENTICATION_REQUIRED |
| salesTaxReturns PUT | **401** (product gate) |
| salesTaxReturns POST/DELETE | **405** |
| bankPayments DELETE | **405** |
| 405 false friends sample set | **405** |
| transactions POST/PUT | **401**; DELETE missing id **200** meta-only |

## Bounded Codex Power slices

1. Wave-5r product merge + product IR: **done** (offline ACCEPT).
2. **Wave-5s-A:** `api_invoice_logs_list` only; offline special green +1.
   Implementation map: [[wave_fivesa_invoice_logs_list_research]].
3. **Wave-5s-B:** files upload ticketed pair; pair generator evidence for
   `api.files.create` + `api.special.files_upload`.
4. **Wave-5s-C:** invoice email + delivery ticketed pairs (high side effect;
   live later).

Do not offline-freeze transactions, bankPayments delete, 405 false friends, or
bulk from this research.

## Non-claims

- No coverage greening from this page.
- No live, UI, vision, or completeness claims.
- No webhook API.
- No headed browser and no disposable records in research.
