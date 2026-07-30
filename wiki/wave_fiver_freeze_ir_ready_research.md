---
name: wave_fiver_freeze_ir_ready_research
title: Wave-5r salesTaxReturns freeze IR readiness research
desc: Cited re-verification that the Wave-5r freeze page is on root and ready for independent freeze review; product remains blocked until freeze IR ACCEPT; no coverage greening.
tags: [billy, api, sales_tax_returns, writes, research, offline, freeze-ir]
sources:
  - https://www.billy.dk/api/
  - https://api.billysbilling.com/v2
  - wiki/wave_fiver_ticketed_writes_contract.md
  - wiki/wave_fiver_sales_tax_returns_freeze_ready_research.md
  - wiki/wave_fiver_sales_tax_returns_freeze_ready_research_independent_review.md
  - wiki/wave_fiver_sales_tax_returns_product_ready_research.md
  - wiki/wave_fiver_sales_tax_returns_product_ready_research_independent_review.md
  - wiki/offline_write_probe_rules.md
  - coverage/api_v2_manifest.yaml
  - coverage/status.json
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
  - "parent scratch: .fractal/main.billy_complete/tmp/grok-research.md (research75)"
created: 2026-07-30T15:25:00Z
updated: 2026-07-30T15:25:00Z
---

# Wave-5r salesTaxReturns freeze IR readiness research

## Authority boundary

This page freezes **research evidence** that:

1. The Wave-5r freeze page is present on root with a stable content MD5, and
2. Official docs and unauthenticated method gates still match that freeze.

It is **not** freeze ACCEPT, product authority, implementation, tests, coverage
greening, live qualification, UI/vision work, bulk resolution, or completeness.

Full probe matrices and scratch snapshots live outside the shared wiki at
`.fractal/main.billy_complete/tmp/grok-research.md` (research75).

## Official docs fingerprint

| Field | Value |
| --- | --- |
| URL | https://www.billy.dk/api/ |
| HTTP | 200 |
| ETag | `"wcw4x9hqvu3603"` |
| Body bytes | 147934 |
| MD5 | `8b94b0135c91fd15fe54ea33e088a4be` |
| Access | 2026-07-30T15:22:05Z |
| Note | Byte-identical to research74 / research73 HTML bodies |

Inventory lock metadata in `coverage/status.json` still cites ETag
`hsisik4g9p3603` / MD5 `c2efda0ee4cf9cf200e14910c5fc6996` (access/CDN drift only;
Supports and property tables unchanged).

API base remains locked to `https://api.billysbilling.com/v2`. Paths below are
client-relative and omit `/v2`.

## Unauthenticated method gates

Probes used JSON object body `{}` for POST/PUT. No credentials. No persistent
records. Access 2026-07-30T15:22:30Z.

| Method | Path | Status | errorCode |
| --- | --- | --- | --- |
| POST | `/salesTaxReturns` | 405 | `METHOD_NOT_ALLOWED` |
| PUT | `/salesTaxReturns/:id` | 401 | `AUTHENTICATION_REQUIRED` |
| DELETE | `/salesTaxReturns/:id` | 405 | `METHOD_NOT_ALLOWED` |
| PUT | `/salesTaxReturns/:id` empty body | 400 | `INVALID_REQUEST_BODY` |

Shared 401 message: must use Basic auth or an OAuth access token.

## Official Supports and properties

`/v2/salesTaxReturns` Supports: get by id, list, **update**, bulk save, bulk delete.
Supports omits create and singular delete (matches method gates).

Readonly offline: `organization`, `createdTime`, `periodType`, `period`,
`correctionNo`, `startDate`, `endDate`, `isPaid`.

Blank-notes columns stay opaque offline with no live success claim:
`periodText`, `reportDeadline`, `isSettled` (settlement may be one-way live).

## Freeze page under freeze IR

| Field | Value |
| --- | --- |
| Path | `wiki/wave_fiver_ticketed_writes_contract.md` |
| Root HEAD when packaged | `a418165` |
| Content MD5 | `078aca13828b5e0d71b454c1aa2dc00f` |
| Root presence | **Present** (merged from authoring tip `a8590b4`) |
| Freeze IR page | **Missing** (next gate) |

Research75 found the freeze page content consistent with official Supports,
property boundary, method gates, ticketed-write design, and the freeze-ready
plus product-ready research packages. Independent freeze ACCEPT remains a
separate Grok freeze IR.

## Exact frozen surface (for freeze IR)

| Inventory id | Preview tool | Execute tool | Request | Required success root |
| --- | --- | --- | --- | --- |
| `api.salesTaxReturns.update` | `api_sales_tax_returns_update_preview` | `api_sales_tax_returns_update_execute` | `PUT /salesTaxReturns/:id` with outer `{id, salesTaxReturn: map}` | `salesTaxReturns` |

These two names are the **only** tools freeze declares for this wave.

Shared ticketed-write rules: preview non-mutating; ticket ≤5 minutes; single-use;
execute accepts only `confirmation_ticket`; exactly one HTTP write; no retry;
fail-closed on ticket mismatch. Inner map is opaque. Optional inner id must
match path id when present.

## Coverage honesty

| Metric | Value |
| --- | --- |
| Offline implemented + contract_tested | 178 |
| Live tested | 0 |
| Vision verified | 0 |
| Registry API tools | 262 |
| `api.salesTaxReturns.update` | implemented false; contract_tested false; live_tested false |
| `complete` | false |
| Ambiguous bulk empty tools | 92 |
| Clear not-impl remaining | 31 (this update is one) |

No product source file `sales_tax_return_writes.py`. Research does not green
coverage.

## Product after freeze IR ACCEPT only

Template: `src/billy_mcp/api/user_writes.py`.

Create:

- `src/billy_mcp/api/sales_tax_return_writes.py`
- `tests/api/test_sales_tax_return_writes.py`
- register in `src/billy_mcp/server.py`
- offline greening via `scripts/generate_coverage_report.py`
- `WAVE_FIVER_WRITE_API_TOOL_NAMES` size 2; registry 262 → 264

Do **not** start product until freeze IR ACCEPT of freeze MD5
`078aca13828b5e0d71b454c1aa2dc00f`.

## Freeze IR checklist

1. Re-fetch https://www.billy.dk/api/ ; confirm MD5 `8b94b0135c91fd15fe54ea33e088a4be` or document any drift.
2. Re-probe unauth gates on `https://api.billysbilling.com/v2` with body `{}`.
3. Confirm freeze page MD5 `078aca13828b5e0d71b454c1aa2dc00f` on the reviewed commit.
4. Verify one inventory id, two tools, PUT path, opaque map, ticket protocol, exclusions.
5. Confirm coverage still red for the update row; no product source; no greening.
6. Verdict **ACCEPT** authorises product leaf only; not greening by itself, not live/UI/vision, not completeness.

## Explicit non-claims

- Not freeze ACCEPT.
- Not product ACCEPT or product source authority before freeze IR.
- Not live, UI, vision, bulk, webhook, or completeness claims.
- Not greening of any coverage row.
