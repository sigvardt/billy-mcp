---
name: wave_fiver_sales_tax_returns_freeze_ready_research
title: Wave-5r salesTaxReturns update freeze-ready research
desc: Cited offline freeze-ready package for singular salesTaxReturns update ticketed writes; create, delete, bulk, product, live, UI, and completeness remain separate.
tags: [billy, api, sales_tax_returns, writes, research, offline]
sources:
  - https://www.billy.dk/api/
  - https://api.billysbilling.com/v2
  - wiki/wave_fivep_candidate_write_research.md
  - wiki/wave_fiveq_ticketed_writes_contract.md
  - wiki/offline_write_probe_rules.md
  - coverage/api_v2_manifest.yaml
  - coverage/status.json
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
created: 2026-07-30T14:46:00Z
updated: 2026-07-30T14:46:00Z
---

# Wave-5r salesTaxReturns update freeze-ready research

## Authority boundary

This page freezes **research evidence only** for a future wiki freeze contract covering singular Billy API **`salesTaxReturns` update**. It is not freeze ACCEPT, product authority, implementation, tests, coverage greening, live qualification, UI/vision work, bulk resolution, or completeness.

Full probe matrices and scratch snapshots live outside the shared wiki at
`.fractal/main.billy_complete/tmp/grok-research.md` (research73).

## Official docs fingerprint (2026-07-30)

| Field | Value |
| --- | --- |
| URL | https://www.billy.dk/api/ |
| HTTP | 200 |
| ETag | `"wcw4x9hqvu3603"` |
| Body bytes | 147934 |
| MD5 | `8b94b0135c91fd15fe54ea33e088a4be` |
| Note | Byte-identical to research72 / research71 / research70 HTML bodies |

Inventory lock metadata in `coverage/status.json` still cites ETag
`hsisik4g9p3603` / MD5 `c2efda0ee4cf9cf200e14910c5fc6996` (access/CDN drift only;
Supports and property tables unchanged).

API base remains locked to `https://api.billysbilling.com/v2`. Paths below are
client-relative and omit `/v2`.

## Unauthenticated method gates

Probes used JSON object body `{}` for POST/PUT. No credentials. No persistent
records. Access 2026-07-30T14:45:18Z.

| Method | Path | Status | errorCode |
| --- | --- | --- | --- |
| POST | `/salesTaxReturns` | 405 | `METHOD_NOT_ALLOWED` (does not support creating records) |
| PUT | `/salesTaxReturns/:id` | 401 | `AUTHENTICATION_REQUIRED` |
| DELETE | `/salesTaxReturns/:id` | 405 | `METHOD_NOT_ALLOWED` (does not support deleting a single record) |
| PUT | `/salesTaxReturns/:id` empty body | 400 | `INVALID_REQUEST_BODY` (not method-closed) |

Shared 401 message: must use Basic auth or an OAuth access token.

## Official Supports and properties

`/v2/salesTaxReturns` Supports: get by id, list, **update**, bulk save, bulk delete.
Supports omits create and singular delete (matches method gates).

| Property | Type | Notes | Freeze treatment |
| --- | --- | --- | --- |
| organization | belongs-to | readonly | not client-writable |
| createdTime | datetime | readonly | not client-writable |
| periodType | enum | readonly | not client-writable |
| period | string | readonly | not client-writable |
| periodText | string | | opaque inner value; candidate non-readonly offline |
| correctionNo | integer | readonly | not client-writable |
| startDate | date | readonly | not client-writable |
| endDate | date | readonly | not client-writable |
| reportDeadline | date | | opaque inner value; candidate non-readonly offline |
| isSettled | boolean | | opaque; candidate non-readonly; live may be one-way |
| isPaid | boolean | readonly | not client-writable |

No official salesTaxReturns create/update sample JSON. Do not invent payment,
filing, bulk settlement, or webhook routes. Do not claim that blank-notes
columns succeed live: keep the inner map opaque.

## Exact future freeze surface

| Inventory id | Preview tool | Execute tool | Request | Required success root |
| --- | --- | --- | --- | --- |
| `api.salesTaxReturns.update` | `api_sales_tax_returns_update_preview` | `api_sales_tax_returns_update_execute` | `PUT /salesTaxReturns/:id` with outer `{id, salesTaxReturn: map}` | `salesTaxReturns` |

These two names are the **only** tools a Wave-5r freeze page may declare.

Shared ticketed-write rules (design + prior freezes):

- Outer Pydantic models forbid undeclared fields.
- Inner `salesTaxReturn` is an opaque map.
- If inner `salesTaxReturn.id` is present, it must equal path `id`.
- Preview issues a single-use ticket (≤5 minutes) bound to execute tool, org,
  target, canonical request, and expected effect.
- Execute accepts only `{confirmation_ticket}`; no business payload; no approval
  boolean; one HTTP write; no retry.

## Exclusions

- No create or delete tools (405).
- No bulk tools (no bulk body contract; 92 bulk rows stay red).
- No webhooks (0 mentions on official page).
- No live, UI, vision, or completeness claims.
- No singular-delete cleanup claim; restore-via-PUT is unproven; settlement may
  be irreversible live.
- No claim that `periodText`, `reportDeadline`, or `isSettled` are safe to mutate.
- Do not green coverage from research or freeze text alone.

## Related candidates (not this freeze)

| Candidate | Offline posture |
| --- | --- |
| users update | Wave-5q product merged offline on root (178); product independent ACCEPT separate; live still red |
| transactions create/update | Method-open later research; property table all readonly offline |
| invoiceReminderAssociations delete | **Blocked** (DELETE missing id returns 200 meta-only; cleanup unproven) |
| Many Supports create/update geo/reference rows | Unauth POST/PUT **405** overrides Supports; not freeze candidates |
| Specials (files upload, invoice email, delivery, logs) | Method-open later special wave |

## Coverage honesty at research time

Root baseline is **178** implemented and contract-tested API rows (users update
product merged), still 0 live, 0 vision, 92 ambiguous bulk red, UI all red,
`complete: false`. Research itself does not green `api.salesTaxReturns.update`
or any other row.

## Recommended next step

Codex Power authors wiki-only
`wiki/wave_fiver_ticketed_writes_contract.md` from this package. Independent
freeze ACCEPT is required before any salesTaxReturns product module,
registration, tests, or coverage greening.
