---
name: wave_fives_residual_specials_research
title: Wave-5s residual clear and specials research
desc: Post-Wave-5s-C residual ranking. All six specials are offline-producted. Residual clear 29 and bulk 92 stay live-gated. Next Codex slice is Wave-5t live residual/bulk gate harness. No coverage greening from research.
tags: [billy, api, specials, residual, writes, research, offline, live-gate]
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
  - "parent scratch: .fractal/main.billy_complete/tmp/grok-research.md (research88)"
created: 2026-07-30T16:05:00Z
updated: 2026-07-31T23:35:00Z
---

# Wave-5s residual clear and specials research

## Authority boundary

This page freezes **research evidence** for residual clear not-impl and the
special routes after Wave-5r. Wave-5s-A/B/C specials are now merged offline.
It is not product ACCEPT for residual/bulk, live qualification, UI/vision work,
or completeness. It does not green coverage.

Full probe matrices and scratch snapshots live at
`.fractal/main.billy_complete/tmp/grok-research.md` (research90 is the current
Wave-5u method-level upgrade brief; research89/88 residual ranking still holds;
research77–87 are historical). InvoiceLogs list
offline freeze detail: [[wave_fivesa_invoice_logs_list_research]]. Files upload
offline freeze detail: [[wave_fivesb_files_upload_research]]. Product-ready:
[[wave_fivesb_files_upload_product_ready_research]]. Email + delivery freeze:
[[wave_fivesc_invoice_email_delivery_research]]. Email + delivery product-ready:
[[wave_fivesc_invoice_email_delivery_product_ready_research]]. Product IR:
[[wave_fivesc_research87_independent_review]]. Research90 IR: [[wave_fives_research90_independent_review]].

## Gate status

| Gate | Status |
| --- | --- |
| Wave-5r freeze IR | **ACCEPT** ([[wave_fiver_freeze_independent_review]]) |
| Wave-5r product on root | **Merged + product IR ACCEPT offline** ([[wave_fiver_product_independent_review]] @ `5ad69a6`) |
| Root offline baseline | **184** implemented + contract_tested; live 0; vision 0; `complete: false` |
| Clear not-impl on root | **29** residual writes (all offline-blocked) |
| Specials not-impl | **0** (all 6 specials offline producted; live still false) |
| Ambiguous bulk | 92 red |
| Wave-5s-A product | **Merged** offline (`api_invoice_logs_list`) |
| Wave-5s-B product | **Merged** offline (containment-repaired upload; live false) |
| Wave-5s-C product | **Merged** offline (`0efceae`; review87 ACCEPT offline only) |
| Next offline product tools | **None** — residual/bulk require live token |
| Recommended next slice | **Wave-5u residual unauth gate + bulk-delete canonical-form fixtures** (infrastructure only; form-matrix already merged). Live residual/bulk observation still blocked without `BILLY_API_TOKEN` |

## Official docs fingerprint

| Field | Value |
| --- | --- |
| URL | https://www.billy.dk/api/ |
| HTTP | 200 |
| ETag | `"wcw4x9hqvu3603"` |
| Body bytes | 147934 |
| MD5 | `8b94b0135c91fd15fe54ea33e088a4be` |
| Note | Byte-identical to research76–88 HTML body (research89 re-fetch) |

Inventory lock metadata in `coverage/status.json` still cites ETag
`hsisik4g9p3603` / MD5 `c2efda0ee4cf9cf200e14910c5fc6996` (access/CDN drift only).

API base remains locked to `https://api.billysbilling.com/v2`. Sample upload curl
host `api.billy.dk` must never become the client base.

## Research89 reconfirm (no coverage green)

| Check | Result |
| --- | --- |
| Docs body | Unchanged vs research88 |
| Residual 29 unauth gates | Unchanged (405 false friends; bankPayments delete 405; transactions POST/PUT 401, DELETE meta-200) |
| Bulk candidates | `PUT /{res}/bulk` **401** on open; PATCH collection meta-200 still **not** a contract |
| Specials method-open | emails, deliveries, invoiceLogs, files, `/user` still **401** unauth |
| `GET /user/organizations` | Unauth **404** `UNKNOWN_RESOURCE` (docs still cite the path; offline special risk — live must prove or correct) |
| UI login (headless, no creds) | `mit.billy.dk/login`, English chrome (`Login` / `Log in`); stable `name=email|password|remember` |
| Recommended slice | Still Wave-5t fail-closed live residual/bulk gate harness only |

## Research90 reconfirm (no coverage green)

| Check | Result |
| --- | --- |
| Docs body | Unchanged vs research88/89 (ETag `"wcw4x9hqvu3603"`, MD5 `8b94b0135c91fd15fe54ea33e088a4be`) |
| OPTIONS discrimination | **None** — unauth OPTIONS on residual/bulk paths returns **204** empty body and the same full CORS method list for closed (`accountNatures` POST=405) and open (`transactions` POST=401, `contacts` PUT `/bulk`=401) routes |
| Method-level residual/bulk | Unchanged vs research89 |
| `GET /user/organizations` | Still unauth **404** `UNKNOWN_RESOURCE` |
| UI login | Reconfirmed English `Log in`; stable `name=email|password|remember` |
| Recommended slice | **Wave-5u** method-level live residual/bulk observation upgrade (still fail-closed and unqualified; no residual/bulk tools; no coverage green). Wave-5t OPTIONS harness remains infrastructure only |
| Scratch brief | `.fractal/main.billy_complete/tmp/grok-research.md` (research90) |

## Research95 reconfirm (no coverage green)

| Check | Result |
| --- | --- |
| Docs body | Unchanged vs research88–94 (ETag `"wcw4x9hqvu3603"`, MD5 `8b94b0135c91fd15fe54ea33e088a4be`) |
| Residual 29 unauth gates | Unchanged (405 false friends; bankPayments delete 405; transactions POST/PUT 401, DELETE meta-200) |
| Bulk save `PUT /{res}/bulk` empty plural | **401** on open resources |
| Bulk delete empty `ids[]` / empty array forms | **400** `INVALID_DELETE_ID_ARRAY` (error, not no-op) |
| Bulk delete `ids[]=<synthetic-absent-id>` unauth | **200** meta-only — **not** authenticated non-persistence proof |
| bankPayments bulk empty | **405** |
| `GET /user/organizations` | Still unauth **404** `UNKNOWN_RESOURCE` |
| UI login EN/DA | EN title `Login` / submit `Log in`; DA title `Log ind` / submit `Log ind` |
| Offline auth product | Root ACCEPT offline only (review94); no UI greening |
| Recommended slice | Encode research95 bulk-delete form matrix into Wave-5u harness tests/comments only; residual/bulk tools still blocked; live needs `BILLY_API_TOKEN` |
| Scratch brief | `.fractal/main.billy_complete/tmp/grok-research.md` (research95) |
| Independent review | **ACCEPT as research** — [[wave_fives_research95_independent_review]] |

## Research96 reconfirm (no coverage green)

| Check | Result |
| --- | --- |
| Docs body | Unchanged vs research88–95 (ETag `"wcw4x9hqvu3603"`, MD5 `8b94b0135c91fd15fe54ea33e088a4be`) |
| Form-matrix harness | **Merged** on root tip `2d3b501` (research95 encode done; still infrastructure only) |
| Residual 29 unauth gates | Unchanged; 405 messages explicitly “does not support creating/updating records” |
| Bulk delete server form | Empty `ids[]` **400** message states `DELETE /{resource}?ids[]=123&ids[]=456` |
| Bulk delete JSON/form body | **400** `INVALID_DELETE_ID_ARRAY` — query form only |
| bankPayments bulk empty | **405** “does not support bulk deleting records” |
| `GET /user/organizations` no token | **404** `UNKNOWN_RESOURCE` (“Unknown resource `v2/user/organizations`”) |
| `GET /organizations` no token | **401** `AUTHENTICATION_REQUIRED` (known resource) |
| Garbage `X-Access-Token` | **401** `OAUTH_INVALID_ACCESS_TOKEN` on any path — auth-first; **does not prove path existence** |
| UI login EN/DA | Reconfirmed `Log in` / `Log ind`; captcha iframe 0 |
| Recommended slice | Encode residual unauth gate fixtures + bulk-delete canonical `ids[]` query template into Wave-5u harness only; still no residual/bulk tools; live needs `BILLY_API_TOKEN` |
| Scratch brief | `.fractal/main.billy_complete/tmp/grok-research.md` (research96) |
| Independent review | **ACCEPT as research** — [[wave_fives_research96_independent_review]] |

## Residual ranking (research88; held by research89)



### A. Specials offline (done; live still false)

| Priority | Inventory id | Wire | Note |
| --- | --- | --- | --- |
| done | `api.special.invoice_logs` | `GET /invoiceLogs` | Product merged offline |
| done | `api.special.files_upload` (+ pair `api.files.create`) | `POST /files` binary | Containment-repaired; live false |
| done | `api.special.invoice_email` | `POST /invoices/:invoiceId/emails` | Ticketed; live false |
| done | `api.special.invoice_delivery` | `POST /invoiceDeliveries` | Ticketed; live false |
| done | `api.special.user_get` / `user_organizations` | `GET /user`, `GET /user/organizations` | Offline tools exist; research89 unauth `GET /user/organizations` is **404** — live must prove path |

### B. Blocked offline (keep red) — residual clear 29

| Bucket | Rows | Why (research88 unauth + docs) |
| --- | --- | --- |
| 405 false friends | accountNatures, balanceModifiers, cities, countries, countryGroups, currencies, locales, states, zipcodes, postings, contactBalancePostings, invoiceReminderAssociations create/update | Unauth POST/PUT **405** `METHOD_NOT_ALLOWED` with explicit "does not support creating/updating records" |
| bankPayments delete | `api.bankPayments.delete` | Unauth DELETE **405** "does not support deleting a single record" |
| transactions CUD | create/update/delete | POST/PUT **401** method-open but property table lists **all fields readonly** (research89 docs extract); DELETE 200 meta-only is not cleanup |
| associations delete | `api.invoiceReminderAssociations.delete` | Unauth DELETE 200 meta-only; error on missing ids documents `?ids[]=` form only |
| bulk | all 92 | No body contract on official page; see bulk candidate note below |
| webhooks | none | 0 official mentions; API `UNKNOWN_RESOURCE` 404 |

### C. Bulk candidate (research only; not productable offline)

| Pattern | Unauth result | Use |
| --- | --- | --- |
| `PUT /{resource}/bulk` + plural root | **401** on open resources | Strongest offline method-open candidate for bulk save |
| `POST /{resource}/bulk` | **405** | Closed path form |
| `PATCH /{resource}` empty plural | **200** meta-only unauth | **Not a contract** — do not ship tools |
| `DELETE /{resource}?ids[]=` | **200** meta-only or **405** | Identifier shape hint only |

Live non-production must prove request body, response roots, partial failure, and cleanup before any bulk tools.

### D. Recommended next Codex slice

**Wave-5t live residual/bulk gate harness**: detect `BILLY_API_TOKEN`, fail-closed without it, run residual 29 + bulk candidate matrix against the dedicated non-production organisation only, write non-sensitive evidence outside git, never green coverage from scaffolding. No residual/bulk FastMCP tools in that slice.

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
   `api.files.create` + `api.special.files_upload` (product in flight / merge).
4. **Wave-5s-C:** invoice email + delivery ticketed pairs (high side effect;
   live later). Freeze map: [[wave_fivesc_invoice_email_delivery_research]].

Do not offline-freeze transactions, bankPayments delete, 405 false friends, or
bulk from this research.

## Non-claims

- No coverage greening from this page.
- No live, UI, vision, or completeness claims.
- No webhook API.
- No headed browser and no disposable records in research.
