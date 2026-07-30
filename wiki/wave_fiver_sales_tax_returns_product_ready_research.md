---
name: wave_fiver_sales_tax_returns_product_ready_research
title: Wave-5r salesTaxReturns product-ready research
desc: Cited freeze-page verification and product implementation map for singular salesTaxReturns update ticketed writes; freeze IR ACCEPT still required before product source; no coverage greening from research.
tags: [billy, api, sales_tax_returns, writes, research, offline, product-ready]
sources:
  - https://www.billy.dk/api/
  - https://api.billysbilling.com/v2
  - wiki/wave_fiver_sales_tax_returns_freeze_ready_research.md
  - wiki/wave_fiver_sales_tax_returns_freeze_ready_research_independent_review.md
  - wiki/offline_write_probe_rules.md
  - wiki/wave_fiveq_ticketed_writes_contract.md
  - coverage/api_v2_manifest.yaml
  - coverage/status.json
  - src/billy_mcp/api/user_writes.py
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
created: 2026-07-30T15:10:00Z
updated: 2026-07-30T15:10:00Z
---

# Wave-5r salesTaxReturns product-ready research

## Authority boundary

This page freezes **research evidence** for:

1. Independent verification of the Wave-5r freeze page content (child tip), and
2. The exact offline product file map for singular `salesTaxReturns` update.

It is **not** freeze ACCEPT, product authority, implementation, tests, coverage
greening, live qualification, UI/vision work, bulk resolution, or completeness.

Full probe matrices and scratch snapshots live outside the shared wiki at
`.fractal/main.billy_complete/tmp/grok-research.md` (research74).

## Official docs fingerprint

| Field | Value |
| --- | --- |
| URL | https://www.billy.dk/api/ |
| HTTP | 200 |
| ETag | `"wcw4x9hqvu3603"` |
| Body bytes | 147934 |
| MD5 | `8b94b0135c91fd15fe54ea33e088a4be` |
| Note | Byte-identical to research73 / research72 / research71 / research70 HTML bodies |

Inventory lock metadata in `coverage/status.json` still cites ETag
`hsisik4g9p3603` / MD5 `c2efda0ee4cf9cf200e14910c5fc6996` (access/CDN drift only;
Supports and property tables unchanged).

API base remains locked to `https://api.billysbilling.com/v2`. Paths below are
client-relative and omit `/v2`.

## Unauthenticated method gates

Probes used JSON object body `{}` for POST/PUT. No credentials. No persistent
records.

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

## Freeze page under verification

| Field | Value |
| --- | --- |
| Path | `wiki/wave_fiver_ticketed_writes_contract.md` |
| Child branch tip | `main.billy_complete.wave5r_sales_tax_returns_freeze` @ `a8590b4` |
| Content MD5 | `078aca13828b5e0d71b454c1aa2dc00f` |
| Root presence | Missing until freeze merge |

Research74 found the freeze page content consistent with official Supports,
property boundary, method gates, ticketed-write design, and the freeze-ready
research package. Independent freeze ACCEPT remains a separate Grok freeze IR.

## Exact product surface (after freeze IR ACCEPT only)

| Inventory id | Preview tool | Execute tool | Request | Required success root |
| --- | --- | --- | --- | --- |
| `api.salesTaxReturns.update` | `api_sales_tax_returns_update_preview` | `api_sales_tax_returns_update_execute` | `PUT /salesTaxReturns/:id` with outer `{id, salesTaxReturn: map}` | `salesTaxReturns` |

These two names are the **only** tools product may implement for this wave.

Shared ticketed-write rules:

- Outer Pydantic models forbid undeclared fields.
- Inner `salesTaxReturn` is an opaque map.
- If inner `salesTaxReturn.id` is present, it must equal path `id`.
- Preview issues a single-use ticket (≤5 minutes) bound to execute tool, org,
  target, canonical request, and expected effect.
- Execute accepts only `{confirmation_ticket}`; no business payload; no approval
  boolean; one HTTP write; no retry.
- Use shared `WriteProtocolService` / `ConfirmationStore`.
- Twin template: `src/billy_mcp/api/user_writes.py`.

## Product file map (Codex Power, post freeze IR)

| Path | Action |
| --- | --- |
| `src/billy_mcp/api/sales_tax_return_writes.py` | Create update-only twin |
| `tests/api/test_sales_tax_return_writes.py` | Contract tests for two tools |
| `src/billy_mcp/server.py` | Register write tools |
| `scripts/generate_coverage_report.py` | Offline evidence for `api.salesTaxReturns.update` |
| Coverage artifacts | Regenerate to offline **179** (live remains 0) |
| `tests/unit/test_coverage_server.py` | API tool count **262 → 264** |

## Exclusions

- No create or delete tools (405).
- No bulk tools (no bulk body contract; 92 bulk rows stay red).
- No webhooks (0 mentions on official page).
- No live, UI, vision, or completeness claims.
- No singular-delete cleanup claim; restore-via-PUT is unproven; settlement may
  be irreversible live.
- No product source before freeze IR ACCEPT of freeze MD5 `078aca13828b5e0d71b454c1aa2dc00f`.
- Do not green coverage from research or freeze text alone.

## Related candidates (not this product)

| Candidate | Offline posture |
| --- | --- |
| users update | Wave-5q product merged offline (178); product independent ACCEPT on sibling branch; live still red |
| transactions create/update | Method-open later research; property table all readonly offline |
| invoiceReminderAssociations delete | **Blocked** (DELETE missing id returns 200 meta-only) |
| Many Supports create/update geo/reference rows | Unauth POST/PUT **405** overrides Supports |
| Specials (files upload, invoice email, delivery) | Method-open later special wave |

## Coverage honesty at research time

Root baseline is **178** implemented and contract-tested API rows, still 0 live,
0 vision, 92 ambiguous bulk red, UI all red, `complete: false`. Research itself
does not green `api.salesTaxReturns.update` or any other row.

## Recommended next steps

1. Merge freeze page to root (content MD5 `078aca13828b5e0d71b454c1aa2dc00f`).
2. Grok freeze independent review.
3. Only after freeze IR ACCEPT: Codex Power product leaf per the file map above.
