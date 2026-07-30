---
name: wave_fiver_freeze_independent_review
title: Wave-5r contract freeze independent review ACCEPT
desc: Authoritative root Grok acceptance of the cited offline contract for singular salesTaxReturns update ticketed writes (create, singular delete, bulk, live, UI, vision, and completeness excluded).
tags: [billy, api, sales_tax_returns, writes, review, coverage]
sources:
  - https://www.billy.dk/api/
  - https://api.billysbilling.com/v2
  - wiki/wave_fiver_ticketed_writes_contract.md
  - wiki/wave_fiver_freeze_ir_ready_research.md
  - wiki/wave_fiver_sales_tax_returns_freeze_ready_research.md
  - wiki/wave_fiver_sales_tax_returns_freeze_ready_research_independent_review.md
  - wiki/wave_fiver_sales_tax_returns_product_ready_research.md
  - wiki/wave_fiver_sales_tax_returns_product_ready_research_independent_review.md
  - wiki/offline_write_probe_rules.md
  - coverage/api_v2_manifest.yaml
  - coverage/status.json
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
  - "parent scratch: .fractal/main.billy_complete/tmp/grok-review.md (review75)"
created: 2026-07-30T15:35:00Z
updated: 2026-07-30T15:35:00Z
---

# Wave-5r contract freeze independent review ACCEPT

## Verdict

| Claim | Result |
| --- | --- |
| Wave-5r cited contract freeze | **ACCEPT** |
| Official documentation versus freeze map | **PASS** |
| Unauth method gates (PUT 401 JSON object; POST and singular DELETE 405) | **PASS** |
| Freeze versus exact one-row / two-tool update-only map | **PASS** |
| Ticket protocol, body-id equality, property boundary | **PASS** |
| Coverage honesty before product integration | **PASS** |
| Wave-5r product implementation | **not accepted** — separate Codex Power product leaf and product review required |
| Live, UI, vision, bulk, create, singular delete, and completeness | **not claimed / fail-closed** |

**Verdict: ACCEPT**

This authoritative root Grok independent review accepts the freeze page
`wiki/wave_fiver_ticketed_writes_contract.md` (content MD5
`078aca13828b5e0d71b454c1aa2dc00f`) at reviewed branch baseline `322f301`
(`322f301ed8b3ef5cf6409eac5f24b76c27ad366c`).

This page is the freeze gate for Wave-5r. It is not product acceptance. ACCEPT
authorises only a subsequent, separate Codex Power offline product
implementation leaf for the two named salesTaxReturns-update tools. It does
**not** authorise coverage greening by itself, live/UI/vision work, bulk tools,
create or delete tools, cleanup qualification, or completeness.

## Reviewed baseline

| Item | Value |
| --- | --- |
| Reviewed commit | `322f301` (`322f301ed8b3ef5cf6409eac5f24b76c27ad366c`) |
| Freeze page | `wiki/wave_fiver_ticketed_writes_contract.md` |
| Freeze content MD5 | `078aca13828b5e0d71b454c1aa2dc00f` |
| Freeze IR readiness research | `wiki/wave_fiver_freeze_ir_ready_research.md` |
| Freeze-ready research (not freeze ACCEPT) | `wiki/wave_fiver_sales_tax_returns_freeze_ready_research.md` |
| Prior research IR (ACCEPT as research only) | `wiki/wave_fiver_sales_tax_returns_freeze_ready_research_independent_review.md` |
| Product-ready research (not product ACCEPT) | `wiki/wave_fiver_sales_tax_returns_product_ready_research.md` |
| Product-ready research IR (ACCEPT as research only) | `wiki/wave_fiver_sales_tax_returns_product_ready_research_independent_review.md` |
| Parent review scratch | `.fractal/main.billy_complete/tmp/grok-review.md` (review75) |
| Locked API base | `https://api.billysbilling.com/v2` |

## Sources and method (official evidence)

| Source | How used |
| --- | --- |
| https://www.billy.dk/api/ | Primary. Independent live fetch this review: HTTP 200, ETag `wcw4x9hqvu3603`, body MD5 `8b94b0135c91fd15fe54ea33e088a4be`, 147934 bytes. Byte-identical to Research75 access fingerprint. `/v2/salesTaxReturns` Supports and property table re-parsed from the fetched HTML. Inventory lock in `coverage/status.json` still records ETag `hsisik4g9p3603` / MD5 `c2efda0ee4cf9cf200e14910c5fc6996`; access/CDN metadata drift alone is not a Supports or property change. |
| Unauth probes `https://api.billysbilling.com/v2` | Independent reconfirm with JSON object body `{}` and no token: `PUT /salesTaxReturns/:id` → 401 `AUTHENTICATION_REQUIRED`; `POST /salesTaxReturns` → 405 `METHOD_NOT_ALLOWED` (“does not support creating records”); singular `DELETE /salesTaxReturns/:id` → 405 `METHOD_NOT_ALLOWED` (“does not support deleting a single record”); empty-body PUT → 400 `INVALID_REQUEST_BODY`. Not live qualification. No credentials. No created records. |
| `wiki/wave_fiver_ticketed_writes_contract.md` | Full freeze surface under review. |
| `wiki/wave_fiver_freeze_ir_ready_research.md` | Context; this review re-fetched docs and re-probed gates rather than copying Research75. |
| `wiki/offline_write_probe_rules.md` | Auth-gate vs 405 override rules; `salesTaxReturns` row records POST/DELETE **405** and PUT **401** (Supports update; no create/delete). |
| `coverage/api_v2_manifest.yaml` @ `322f301` | salesTaxReturns get/list green offline; update red with reserved preview tool name only; both bulk empty-tool `ambiguous_bulk`; no singular create or delete inventory rows. |
| `coverage/status.json` @ `322f301` | `implemented_rows` 178, `contract_tested_rows` 178, `live_tested_rows` 0, `vision_verified_rows` 0, `api_ambiguous_bulk` 92, `complete: false`. |
| Registry @ `322f301` | 262 unique `api_*` tools per `tests/unit/test_coverage_server.py`; no salesTaxReturns write tools registered. |
| Design `docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md` | Ticketed write / confirmation protocol discipline (strict preview, ticket-only execute, no silent retries). |
| Peer freeze IR pattern | e.g. `wiki/wave_fiveq_freeze_independent_review.md` |

No headed browser. No credentials. No live mutations. No secrets or raw browser evidence tracked in git.

## Exact reviewed scope

The accepted contract freezes exactly one singular API v2 JSON update operation
(two ticketed tools: one preview + one execute):

| Inventory id | Preview tool | Execute tool | Method and client path | Singular request root | Required success root |
| --- | --- | --- | --- | --- | --- |
| `api.salesTaxReturns.update` | `api_sales_tax_returns_update_preview` | `api_sales_tax_returns_update_execute` | `PUT /salesTaxReturns/:id` | `salesTaxReturn` (+ path `id`) | `salesTaxReturns` |

Official docs for `/v2/salesTaxReturns` (this review): Supports **get by id, list,
update, bulk save, bulk delete**. Supports omits create and singular delete
(matches method gates).

Property boundaries checked against the official table re-parsed this review:

| Property | Official notes | Freeze treatment check |
| --- | --- | --- |
| `organization` | belongs-to; readonly | Not client-writable — **PASS** |
| `createdTime` | datetime; readonly | Not client-writable — **PASS** |
| `periodType` | enum; readonly | Not client-writable — **PASS** |
| `period` | string; readonly | Not client-writable — **PASS** |
| `periodText` | string; blank notes | Opaque only; no live success claim — **PASS** |
| `correctionNo` | integer; readonly | Not client-writable — **PASS** |
| `startDate` / `endDate` | date; readonly | Not client-writable — **PASS** |
| `reportDeadline` | date; blank notes | Opaque only; no live success claim — **PASS** |
| `isSettled` | boolean; blank notes | Opaque only; may be one-way — **PASS** |
| `isPaid` | boolean; readonly | Not client-writable — **PASS** |

No official create/update sample invents a stricter inner schema; the freeze
correctly keeps the `salesTaxReturn` map opaque and invents no payment, filing,
or bulk settlement route.

## Criteria checked

| # | Criterion | Result |
| --- | --- | --- |
| 1 | Authorises exactly `api.salesTaxReturns.update` with exactly two tools | **PASS** |
| 2 | Strict outer input `{id, salesTaxReturn}`; client-relative `PUT /salesTaxReturns/:id`; required success root `salesTaxReturns` | **PASS** |
| 3 | Inner map is opaque `dict[str, JsonValue]`; not a generic HTTP control | **PASS** |
| 4 | Optional inner id must equal path id when present | **PASS** |
| 5 | Ticket-only execute; five-minute single-use exact bindings; one HTTP write; no retry; fail-closed | **PASS** |
| 6 | Create and singular delete excluded (POST/DELETE 405) | **PASS** |
| 7 | Bulk excluded (no body contract) | **PASS** |
| 8 | Webhooks excluded (0 official mentions) | **PASS** |
| 9 | Cleanup honesty (no singular DELETE; restore-via-PUT unproven; settlement may be one-way) | **PASS** |
| 10 | Coverage still red for the update row; no product source; offline 178/178/0/0; complete false | **PASS** |

## Explicit non-acceptances

- Product source, registration, contract tests, or coverage greening
- Live CUD, UI, vision, bulk 92 resolution
- Create, singular delete, webhooks, generic HTTP or browser controls
- Cleanup qualification or completeness

## Contract discrepancies

None that block freeze ACCEPT.

Non-blocking: inventory `response_fields` for the update row still use generic
write narrative strings (`changed_records[]`, `meta.deletedRecords`); freeze
requires plural root `salesTaxReturns` for offline mapping. Align at product
greening time if desired.

## Authority granted by this ACCEPT

Codex Power may implement and offline contract-test only:

- `api_sales_tax_returns_update_preview`
- `api_sales_tax_returns_update_execute`

using the shared write protocol, twin of `src/billy_mcp/api/user_writes.py`,
with offline greening of `api.salesTaxReturns.update` only after product tests
pass. Live, UI, and vision remain separate gates.
