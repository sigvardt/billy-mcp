---
name: wave_fivesa_invoice_logs_list_research
title: Wave-5s-A invoiceLogs list research
desc: Cited offline contract for the read-only special api_invoice_logs_list after Wave-5r product ACCEPT; list-only GET /invoiceLogs with sample query and response; no coverage greening from research.
tags: [billy, api, specials, invoice_logs, research, offline]
sources:
  - https://www.billy.dk/api/
  - https://api.billysbilling.com/v2
  - wiki/offline_write_probe_rules.md
  - wiki/billy_api_v2_research_seed.md
  - wiki/wave_fives_residual_specials_research.md
  - wiki/wave_fiver_product_independent_review.md
  - coverage/api_v2_manifest.yaml
  - coverage/status.json
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
  - "parent scratch: .fractal/main.billy_complete/tmp/grok-research.md (research78)"
created: 2026-07-30T16:28:00Z
updated: 2026-07-30T16:28:00Z
---

# Wave-5s-A invoiceLogs list research

## Authority boundary

This page freezes **research evidence** for the next offline residual product:
read-only special `api_invoice_logs_list` (`api.special.invoice_logs`). It is
not product ACCEPT, live qualification, UI/vision work, bulk resolution, or
completeness. It does not green coverage.

Full probe matrices and Codex implementation map:
`.fractal/main.billy_complete/tmp/grok-research.md` (research78).

## Prerequisites

| Gate | Status |
| --- | --- |
| Wave-5r product IR | **ACCEPT offline** ([[wave_fiver_product_independent_review]]) |
| Residual ranking | **ACCEPT as research** ([[wave_fives_residual_specials_research]]) |
| Root offline baseline | 179 implemented + contract_tested; live 0; vision 0; `complete: false` |
| Registry | 264 API tools before this slice |

## Official docs fingerprint

| Field | Value |
| --- | --- |
| URL | https://www.billy.dk/api/ |
| HTTP | 200 |
| ETag | `"wcw4x9hqvu3603"` |
| Body bytes | 147934 |
| MD5 | `8b94b0135c91fd15fe54ea33e088a4be` |
| Note | Byte-identical to research77 HTML body |

Inventory lock metadata in `coverage/status.json` still cites ETag
`hsisik4g9p3603` / MD5 `c2efda0ee4cf9cf200e14910c5fc6996` (access/CDN drift only).

API base remains locked to `https://api.billysbilling.com/v2`.

## Contract (official narrative only)

`invoiceLogs` is **not** in the resource TOC Supports matrix. The only official
contract is under e-invoice delivery status polling.

```http
GET /v2/invoiceLogs?invoiceId=…&organizationId=…&sortProperty=eventTime&sortDirection=DESC
```

Success root: `invoiceLogs[]`. Sample entry fields: `type` (`received`,
`signedoff`, `failed`), `message`, `messageKey`, `eventTime`.  
Pagination: **none** documented; inventory `pagination: null`.  
Tool: `api_invoice_logs_list` (read-only; no preview/execute pair).  
Do **not** ship singular get, create, update, or delete tools.

## Unauthenticated probes (2026-07-30)

Base `https://api.billysbilling.com/v2`, no token, no persistent records.

| Call | Status | errorCode |
| --- | --- | --- |
| GET collection (with or without sample query) | 401 | `AUTHENTICATION_REQUIRED` |
| GET synthetic id | 404 | `RECORD_NOT_FOUND` (runtime path exists; **not** product) |
| POST / PUT / DELETE | 405 | `METHOD_NOT_ALLOWED` |

## Offline freeze for Codex Power

| Decision | Rule |
| --- | --- |
| Tool | Exactly one: `api_invoice_logs_list` |
| Path | `GET /invoiceLogs` on locked base |
| Required query | `invoiceId`, `organizationId` (sample always includes both) |
| Sort | `sortProperty=eventTime`, `sortDirection=DESC` (documented sample; freeze those offline) |
| Paging | Omit `page` / `pageSize` offline |
| Response | Map `invoiceLogs` array; entries opaque with known type values documented |
| Writes | Forbidden offline (405) |
| Singular get | Forbidden offline (undocumented) |
| Coverage after product | Offline green **+1 special** → 180/180; registry 265; live/vision still 0; `complete: false` |

## Ambiguities (live later)

- Company-token optionality of `organizationId`
- Whether ASC or non-`eventTime` sorts are accepted
- Whether page/pageSize work
- Full live entry schema including possible `id`

None of these block offline list implementation under the sample contract.

## Bounded next slice

Codex Power Wave-5s-A only: module + register + contract tests + registry 265 +
`OFFLINE_API_IMPLEMENTATION_EVIDENCE` for `api.special.invoice_logs`.

Then Grok product IR. Wave-5s-B files upload and Wave-5s-C email/delivery stay
separate.

## Non-claims

- No coverage greening from this page.
- No live, UI, vision, or completeness claims.
- No webhook API.
- No headed browser and no disposable records in research.
