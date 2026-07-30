---
name: wave_fivep_freeze_independent_review
title: Wave-5p contract freeze independent review ACCEPT
desc: Authoritative root Grok acceptance of the cited offline contract for singular organizations create and update ticketed writes (singular delete excluded on 405).
tags: [billy, api, organizations, writes, review, coverage]
sources:
  - https://www.billy.dk/api/
  - https://api.billysbilling.com/v2
  - wiki/wave_fivep_ticketed_writes_contract.md
  - wiki/wave_fivep_candidate_write_research.md
  - wiki/wave_fivep_freeze_ready_research_independent_review.md
  - wiki/offline_write_probe_rules.md
  - coverage/api_v2_manifest.yaml
  - coverage/status.json
  - src/billy_mcp/redaction.py
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
created: 2026-07-30T11:52:00Z
updated: 2026-07-30T11:52:00Z
---

# Wave-5p contract freeze independent review ACCEPT

## Verdict

| Claim | Result |
| --- | --- |
| Wave-5p cited contract freeze | **ACCEPT** |
| Official documentation versus freeze map | **PASS** |
| Unauth method gates (POST/PUT 401 JSON body; singular DELETE 405) | **PASS** |
| Freeze versus exact two-row / four-tool map | **PASS** |
| Ticket protocol, body-id equality, redaction, cleanup limit | **PASS** |
| Coverage honesty before product integration | **PASS** |
| Wave-5p product implementation | **not accepted** - separate parent-managed Codex Power product leaf and product review required |
| Live, UI, vision, bulk, and completeness | **not claimed / fail-closed** |

**Verdict: ACCEPT**

This authoritative root Grok independent review accepts the freeze page
`wiki/wave_fivep_ticketed_writes_contract.md` (content MD5
`2742eda7bafecd619aba5fa8ad0694c5`) at reviewed parent baseline `afbe5188`
(`afbe5188b029e89e7e865a6b9ee8b9a5881f51f4`). Branch tip `a6967e9` is the node
init commit only; freeze content at HEAD matches `afbe5188` byte-for-byte.

This page is the freeze gate for Wave-5p. It is not product acceptance. ACCEPT
authorises only a subsequent, separate Codex Power offline product
implementation leaf for the four named tools.

## Reviewed baseline

| Item | Value |
| --- | --- |
| Root commit | `afbe5188` (`afbe5188b029e89e7e865a6b9ee8b9a5881f51f4`) |
| Freeze page | `wiki/wave_fivep_ticketed_writes_contract.md` |
| Freeze content MD5 | `2742eda7bafecd619aba5fa8ad0694c5` |
| Candidate research (not freeze ACCEPT) | `wiki/wave_fivep_candidate_write_research.md` |
| Prior research review (not freeze ACCEPT) | `wiki/wave_fivep_freeze_ready_research_independent_review.md` |
| Locked API base | `https://api.billysbilling.com/v2` |

## Sources and method

| Source | How used |
| --- | --- |
| https://www.billy.dk/api/ | Primary. Live fetch this review: HTTP 200, ETag `wcw4x9hqvu3603`, body MD5 `8b94b0135c91fd15fe54ea33e088a4be`, 147934 bytes. Matches freeze and research67 access meta. `/v2/organizations` Supports and property table re-parsed from the fetched HTML. |
| Unauth probes `https://api.billysbilling.com/v2` | Independent reconfirm with JSON object body `{}` and no token: `POST /organizations` → 401 `AUTHENTICATION_REQUIRED`; `PUT /organizations/nonexistent-probe-id-wave5p` → 401 `AUTHENTICATION_REQUIRED`; singular `DELETE /organizations/nonexistent-probe-id-wave5p` → 405 `METHOD_NOT_ALLOWED` ("does not support deleting a single record"). Supplemental: bulk `DELETE /organizations?ids[]=nonexistent` → 405 ("does not support bulk deleting records"). Not live qualification. |
| `wiki/wave_fivep_ticketed_writes_contract.md` | Full freeze surface under review. |
| `wiki/wave_fivep_candidate_write_research.md` | Context only; this review re-fetched docs and re-probed gates rather than copying research67. |
| `wiki/offline_write_probe_rules.md` | Auth-gate vs 405 override rules; organizations row records POST/PUT 401 and DELETE 405. |
| `coverage/api_v2_manifest.yaml` @ `afbe5188` | Organizations rows: get/list green offline; create/update red with reserved preview tool names only; both bulk empty-tool `ambiguous_bulk`; no singular delete inventory row. |
| `coverage/status.json` @ `afbe5188` | `implemented_rows` 175, `contract_tested_rows` 175, `live_tested_rows` 0, `vision_verified_rows` 0, `api_ambiguous_bulk` 92, `complete: false`. |
| Registry @ `afbe5188` | 256 unique `api_*` tools per `tests/unit/test_coverage_server.py`; organizations tools present are only `api_organizations_get` and `api_organizations_list` (no create/update write tools). |
| `src/billy_mcp/redaction.py` | Existing sensitive-key redaction includes `subscriptionCardType` / `subscriptionCardNumber` / `subscriptionCardExpires` (case-insensitive). |
| Design `docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md` | Ticketed write / confirmation protocol discipline (strict preview, ticket-only execute, no silent retries). |

No headed browser. No credentials. No live mutations. No raw probe bodies retained in tracked paths.

## Exact reviewed scope

The accepted contract freezes exactly two singular API v2 JSON operations
(four ticketed tools: preview + execute per operation):

| Inventory id | Preview tool | Execute tool | Method and client path | Singular request root | Required success root |
| --- | --- | --- | --- | --- | --- |
| `api.organizations.create` | `api_organizations_create_preview` | `api_organizations_create_execute` | `POST /organizations` | `organization` | `organizations` |
| `api.organizations.update` | `api_organizations_update_preview` | `api_organizations_update_execute` | `PUT /organizations/:id` | `organization` (+ path `id`) | `organizations` |

Official docs for `/v2/organizations` (this review): Supports **get by id,
list, create, update, bulk save, bulk delete**. Singular delete is omitted from
Supports and closed by 405.

Property boundaries checked against the official table (selected required and
sensitive rows; full table parsed this review):

| Property | Official notes | Freeze treatment check |
| --- | --- | --- |
| `ownerUser` | belongs-to; required | Opaque inner value only - **PASS** |
| `name` | string; required | Opaque - **PASS** |
| `country` | belongs-to; immutable, required | Opaque; immutability as boundary not allowlist - **PASS** |
| `baseCurrency` | belongs-to; immutable, required | Opaque; immutability as boundary - **PASS** |
| `fiscalYearEndMonth` | integer; required | Opaque; no numeric freeze - **PASS** |
| `firstFiscalYearStart` / `firstFiscalYearEnd` | date; required | Opaque; no date encoding freeze - **PASS** |
| `subscriptionPeriod` | enum; required, default monthly | Opaque; no enum/default freeze - **PASS** |
| `locale` | belongs-to; required | Opaque - **PASS** |
| `emailAttachmentDeliveryMode` / `vatPeriod` / `invoiceNoMode` / `paymentTermsMode` | enum; required | Opaque - **PASS** |
| `nextInvoiceNo` / `paymentTermsDays` | integer; required | Opaque - **PASS** |
| `subscriptionCardType` / `subscriptionCardNumber` / `subscriptionCardExpires` | string/date; no special Supports flag | Explicit sensitive redaction duty - **PASS** |
| Documented readonly set (`createdTime`, `url`, logo/icon URLs, `isTrial`, lock fields, …) | readonly | Treated as not client-writable boundary - **PASS** |

No official create sample invents a stricter inner schema; the freeze correctly
keeps the `organization` map opaque.

## Criteria checked

| # | Criterion | Result |
| --- | --- | --- |
| 1 | Authorises exactly `api.organizations.create` and `api.organizations.update` with exactly four tools (two preview + two execute) | **PASS** - two table rows; execute twins are not extra inventory rows; no delete or bulk tools frozen |
| 2 | Strict outer Pydantic inputs with `extra="forbid"`; opaque `organization` map; client-relative `POST /organizations` and `PUT /organizations/:id`; required success root `organizations` | **PASS** - all stated on freeze; paths omit `/v2` as client-relative against locked base |
| 3 | Ticket-only execute; five-minute single-use exact operation bindings; no retries; fail-closed on bad tickets | **PASS** - shared `ConfirmationStore` / `WriteProtocolService`; execute input is only `{confirmation_ticket}`; exactly one non-retried HTTP write |
| 4 | Update body-id equality when inner `organization.id` is present; absent inner id not invented | **PASS** |
| 5 | DELETE 405 cleanup limit; create cleanup text unqualified; update restoration unproven | **PASS** - independently reconfirmed singular DELETE 405; freeze cleanup line is non-qualification |
| 6 | Sensitive subscription-card redaction required; no claim to retain or validate card data | **PASS** - freeze names the three card fields; product redaction helper already covers them |
| 7 | Excludes singular delete, all bulk rows, generic transport, webhooks, live, UI, vision, product, registration, greening, and completeness | **PASS** - explicit exclusion list; bulk remains empty-tool red |
| 8 | Coverage honesty: 175 offline green, 0 live, 0 vision, 92 bulk red, `complete: false`; create/update still red | **PASS** - `coverage/status.json` and manifest create/update `implemented: false`, `contract_tested: false` |

No discrepancy requires REJECT.

## Assertions checked (detail)

| Assertion | Result |
| --- | --- |
| Exactly two inventory rows; four named future tools | **PASS** |
| Paths `POST /organizations` and `PUT /organizations/:id` (client-relative, no double `/v2`) | **PASS** |
| Outer create `{organization: map}`; update `{id, organization: map}` | **PASS** |
| Inner map opaque `dict[str, JsonValue]`; not a generic HTTP body; not a field schema | **PASS** |
| Required response root only `organizations` | **PASS** |
| Preview non-mutating; ticket ≤ five minutes; single-use; bound to execute tool, org, target, request, effect | **PASS** |
| Create target `null`; update target path `id` | **PASS** |
| Execute accepts only confirmation ticket; no business payload or approval boolean | **PASS** |
| Exactly one HTTP write; no retry | **PASS** |
| Update path `id` equals inner `organization.id` when supplied | **PASS** |
| POST/PUT unauth 401 is offline gate only, not live qualification | **PASS** - reconfirmed this review |
| Singular DELETE 405 excludes delete product and cleanup qualification | **PASS** - reconfirmed this review |
| Bulk save/delete excluded (no full bulk body contract; 92 bulk rows remain red) | **PASS** - supplemental bulk DELETE also 405 this review |
| Webhooks, generic transport, UI, vision, live, completeness excluded | **PASS** |
| Subscription card fields must be redacted; not logged or stored | **PASS** |
| Product tools not implemented or registered at freeze baseline | **PASS** - only get/list registered for organizations |
| Registry honesty 256 `api_*` tools; organizations write tools absent | **PASS** |
| Coverage 175/175 offline; live 0; vision 0; bulk 92; `complete: false` | **PASS** |

## Method-gate evidence (this review)

| Method and path | HTTP | errorCode | Freeze consequence |
| --- | --- | --- | --- |
| `POST /organizations` body `{}` | 401 | `AUTHENTICATION_REQUIRED` | Offline create gate only |
| `PUT /organizations/:id` body `{}` | 401 | `AUTHENTICATION_REQUIRED` | Offline update gate only |
| `DELETE /organizations/:id` | 405 | `METHOD_NOT_ALLOWED` | Singular delete closed |
| `DELETE /organizations?ids[]=…` (supplemental) | 405 | `METHOD_NOT_ALLOWED` | Bulk delete closed offline; bulk already excluded |

Unauthenticated probes never prove a valid payload, successful mutation,
response shape beyond the error envelope, cleanup, or live qualification.

## Coverage honesty snapshot

| Metric | Value at `afbe5188` |
| --- | --- |
| `implemented_rows` | 175 |
| `contract_tested_rows` | 175 |
| `live_tested_rows` | 0 |
| `vision_verified_rows` | 0 |
| `api_ambiguous_bulk` | 92 |
| `complete` | false |
| `api.organizations.create` | red (`api_organizations_create_preview` reserved name only) |
| `api.organizations.update` | red (`api_organizations_update_preview` reserved name only) |
| `api.organizations.bulk_save` / `bulk_delete` | red, empty tool, `ambiguous_bulk` |
| Singular delete inventory row | absent (correct; Supports omits singular delete) |

Research67 recorded 174 offline greens before Wave-5o product integration. This
freeze review baseline is after that merge and correctly shows **175**. The
freeze page itself does not green inventory.

## Defects

None. No actionable freeze defects found.

## Authorisation boundary

| Stage | Status after this review |
| --- | --- |
| Research | Prior context only |
| Freeze page | Accepted by this review |
| Independent freeze ACCEPT | **This page - ACCEPT** |
| Product implementation | **Blocked until** a separate Codex Power leaf implements and contract-tests the four tools without greening live/UI/vision or completeness |
| Product independent review | Still required after product merge |
| Live / UI / vision / bulk / completeness | Remain fail-closed and red |

## Conclusion

**ACCEPT** the Wave-5p organizations create/update ticketed-write freeze at
parent baseline `afbe5188` with freeze MD5 `2742eda7bafecd619aba5fa8ad0694c5`.
Primary docs fingerprint, unauth method gates, exact two-row/four-tool map,
ticket protocol, body-id equality, DELETE 405 cleanup limit, subscription-card
redaction duty, exclusion list, and coverage honesty all hold under independent
recheck. Product work may proceed only as a separate offline implementation
leaf; this review is not product, live, UI, vision, cleanup, or completeness
acceptance.
