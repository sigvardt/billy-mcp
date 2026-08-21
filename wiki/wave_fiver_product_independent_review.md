---
name: wave_fiver_product_independent_review
title: Wave-5r salesTaxReturns product independent review ACCEPT
desc: Authoritative offline Grok ACCEPT for singular salesTaxReturns update ticketed write tools on parent baseline 5ad69a6; create, singular delete, bulk, live, UI, vision, and completeness remain fail-closed.
tags: [billy, api, sales_tax_returns, writes, review, product]
sources:
  - https://www.billy.dk/api/
  - https://api.billysbilling.com/v2
  - wiki/wave_fiver_ticketed_writes_contract.md
  - wiki/wave_fiver_freeze_independent_review.md
  - wiki/wave_fiver_product_implementation_research.md
  - wiki/offline_write_probe_rules.md
  - coverage/api_v2_manifest.yaml
  - coverage/status.json
  - scripts/generate_coverage_report.py
  - src/billy_mcp/api/sales_tax_return_writes.py
  - src/billy_mcp/api/write_protocol.py
  - src/billy_mcp/confirmations.py
  - src/billy_mcp/client.py
  - src/billy_mcp/config.py
  - src/billy_mcp/server.py
  - tests/api/test_sales_tax_return_writes.py
  - tests/unit/test_coverage_server.py
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
  - "parent scratch: .fractal/main.billy_complete/tmp/grok-review.md"
created: 2026-07-30T16:18:00Z
updated: 2026-07-30T16:18:00Z
---

# Wave-5r salesTaxReturns product independent review ACCEPT

## Verdict

| Claim | Result |
| --- | --- |
| Wave-5r offline product (singular update ticketed writes only) | **ACCEPT** |
| Official documentation versus update-only product surface | **PASS** |
| Unauth method gates (POST 405; PUT 401; DELETE 405) | **PASS** |
| Exactly two update tools versus freeze contract | **PASS** |
| Ticket binding, path lock, response-root mapping, no-retry | **PASS** |
| Strict outer models, opaque inner map, optional path/body id match | **PASS** |
| Sensitive-value and ticket log redaction (preview path) | **PASS** |
| Coverage honesty (`complete: false`; 179 offline; 264 tools; live 0; vision 0; bulk red; UI red) | **PASS** |
| salesTaxReturns update offline green; create/delete tools absent; bulk red | **PASS** |
| Live, UI, vision, bulk, create, singular-delete cleanup, completeness | **not claimed / fail-closed** |

**Verdict: ACCEPT**

This authoritative Grok product review accepts only the offline Wave-5r
salesTaxReturns ticketed-write **update** product slice at parent baseline
**`5ad69a6`** (`5ad69a6a65c1722539e84d1961153afdb17d5de7`), which merges product
implementation `cf33343`.

This ACCEPT is not live testing, UI/vision acceptance, bulk resolution, create
or singular-delete authorisation, cleanup qualification, webhook support,
Wave-5s implementation, or overall product completeness.

No production source, tests, coverage rows, status values, or freeze pages were
modified by this review. Exclusive durable deliverable is this page. Full
checklist lives at `.fractal/main.billy_complete/tmp/grok-review.md`.

## Reviewed baseline

| Item | Value |
| --- | --- |
| Parent product baseline under review | `5ad69a6` (`5ad69a6a65c1722539e84d1961153afdb17d5de7`) |
| Product merge | `5ad69a6` (`merge main.billy_complete.wave5r_sales_tax_returns_product`) |
| Product implementation commit | `cf33343` (adds `sales_tax_return_writes.py`, contract tests, generator greening for update only) |
| Freeze page | `wiki/wave_fiver_ticketed_writes_contract.md` (full-file MD5 `078aca13828b5e0d71b454c1aa2dc00f`) |
| Freeze independent review | **ACCEPT** at [[wave_fiver_freeze_independent_review]] |
| Product module MD5 | `ef5692d95c73caa751a6e9197a82bbec` (`src/billy_mcp/api/sales_tax_return_writes.py`) |
| Locked API base | `https://api.billysbilling.com/v2` (`src/billy_mcp/config.py`) |
| Max ticket TTL | five minutes (`src/billy_mcp/confirmations.py`) |

## Evidence classes (keep separate)

| Class | What it proves | What it does not prove |
| --- | --- | --- |
| Current official docs (`https://www.billy.dk/api/`) | Supports update; omits create and singular delete | Authenticated success, live mutation, cleanup |
| This-review unauth probes (`https://api.billysbilling.com/v2`) | POST 405; PUT 401; singular DELETE 405 | Live mutation, accepted payloads |
| Offline contract tests | Schema, tickets, path, mapping, no-retry, registry/coverage honesty | Live behaviour, UI parity, vision |
| Live / UI / vision | Not performed | Not claimed |

## Official documentation (this review)

Fetched `https://www.billy.dk/api/` during this review (HTTP client only; no
headed browser):

| Fingerprint field | Observed value |
| --- | --- |
| HTTP status | 200 |
| HTTP ETag | `wcw4x9hqvu3603` |
| Body MD5 | `8b94b0135c91fd15fe54ea33e088a4be` |
| Body size | 147934 bytes |

Inventory lock still records ETag `hsisik4g9p3603` / MD5
`c2efda0ee4cf9cf200e14910c5fc6996`. Access-metadata churn alone is not a
contract change.

Direct citation for `/v2/salesTaxReturns`:

> Supports: get by id, list, update, bulk save, bulk delete

Official Supports **lists update**, **omits create**, and **omits singular
delete**. Bulk save/delete remain listed on docs but stay out of this product
(ambiguous bulk inventory rows, empty tool names).

Readonly properties (`organization`, `createdTime`, `periodType`, `period`,
`correctionNo`, `startDate`, `endDate`, `isPaid`) are not client-writable
schema fields. Blank-notes fields (`periodText`, `reportDeadline`, `isSettled`)
remain opaque; settlement may be one-way live. Product does not claim field-level
validation. **PASS.**

## Unauthenticated method gates (this review)

Base `https://api.billysbilling.com/v2`. No credentials. No persistent records.
POST/PUT body `{}`.

| Method | Path | Status | errorCode |
| --- | --- | --- | --- |
| POST | `/salesTaxReturns` | 405 | `METHOD_NOT_ALLOWED` |
| PUT | `/salesTaxReturns/:id` | 401 | `AUTHENTICATION_REQUIRED` |
| DELETE | `/salesTaxReturns/:id` | 405 | `METHOD_NOT_ALLOWED` |

Matches freeze contract and [[offline_write_probe_rules]]. **PASS.**

## Product surface check

| Freeze requirement | Product evidence | Result |
| --- | --- | --- |
| Inventory `api.salesTaxReturns.update` | greened offline only | **PASS** |
| `api_sales_tax_returns_update_preview` | registered; schema `{id, salesTaxReturn}` | **PASS** |
| `api_sales_tax_returns_update_execute` | registered; schema `{confirmation_ticket}` | **PASS** |
| No create/delete/bulk tools | module + registry assertions | **PASS** |
| `PUT /salesTaxReturns/:id` | `WriteMethod.PUT`; path escape test | **PASS** |
| Outer `{salesTaxReturn: map}` | `singular_root="salesTaxReturn"` | **PASS** |
| Success root `salesTaxReturns` | `plural_root`; rejects missing/malformed | **PASS** |
| Opaque inner map + optional id match | validators + opaque-field test | **PASS** |
| Preview mutation-free | request list empty on preview | **PASS** |
| Single-use ticket ≤5 min | TTL + tamper/replay/expiry tests | **PASS** |
| One non-retried HTTP write | error cases assert one request | **PASS** |
| Missing token no network | typed `AUTH_REQUIRED` | **PASS** |
| Log redaction | sensitive values and ticket absent from logs | **PASS** |

Twin shape: `src/billy_mcp/api/user_writes.py` (Wave-5q **ACCEPT** offline).

## Local verification commands

```bash
.venv/bin/python -m pytest tests/api/test_sales_tax_return_writes.py tests/unit/test_coverage_server.py -q
.venv/bin/python scripts/check_coverage.py --reject-false-completeness
```

Observed this review: contract suite and registry tests pass; coverage integrity
passes (305 API / 339 UI rows); `coverage/status.json` reports implemented 179,
contract_tested 179, live 0, vision 0, `complete: false`.

## Coverage honesty

| Row / metric | Status |
| --- | --- |
| `api.salesTaxReturns.update` | implemented + contract_tested; live false |
| `api.salesTaxReturns.bulk_save` / `bulk_delete` | red; empty tools |
| Remaining clear not-impl | 30 |
| Special not-impl | 4 |
| UI | 0 implemented; 0 vision |
| Completeness | **false** |

No stub, skip, mock-live, or vision-only greening.

## Required fixes

None for offline product ACCEPT.

Non-blocking notes: inventory docs metadata still cites older access ETag/MD5;
live field acceptance for blank-notes properties remains open; no live cleanup
claim.

## Explicit non-claims

Live API qualification; UI/browser/vision; create/delete/bulk tools; webhooks;
cleanup qualification; Wave-5s product; overall completeness.
