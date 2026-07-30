---
name: wave_fivep_product_independent_review
title: Wave-5p organizations product independent review ACCEPT
desc: Authoritative offline Grok ACCEPT for singular organizations create and update ticketed write tools on root b4393a2; singular delete, bulk, live, UI, vision, and completeness remain fail-closed.
tags: [billy, api, organizations, writes, review, product]
sources:
  - https://www.billy.dk/api/
  - https://api.billysbilling.com/v2
  - wiki/wave_fivep_ticketed_writes_contract.md
  - wiki/wave_fivep_freeze_independent_review.md
  - wiki/offline_write_probe_rules.md
  - coverage/api_v2_manifest.yaml
  - coverage/status.json
  - coverage/ui_workflows_manifest.yaml
  - scripts/generate_coverage_report.py
  - src/billy_mcp/api/organization_writes.py
  - src/billy_mcp/api/write_protocol.py
  - src/billy_mcp/confirmations.py
  - src/billy_mcp/client.py
  - src/billy_mcp/config.py
  - src/billy_mcp/redaction.py
  - src/billy_mcp/server.py
  - tests/api/test_organization_writes.py
  - tests/unit/test_coverage_server.py
  - tests/coverage/test_coverage_inventory.py
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
created: 2026-07-30T12:45:00Z
updated: 2026-07-30T12:45:00Z
---

# Wave-5p organizations product independent review ACCEPT

## Verdict

| Claim | Result |
| --- | --- |
| Wave-5p offline product (singular create + update ticketed writes only) | **ACCEPT** |
| Official documentation versus create+update product surface | **PASS** |
| Exactly four write tools versus freeze contract | **PASS** |
| Ticket binding, path lock, response-root mapping, no-retry | **PASS** |
| Strict outer models, opaque inner maps, update path/body id match | **PASS** |
| Sensitive subscription-card redaction infrastructure | **PASS** |
| Coverage honesty (`complete: false`; live 0; vision 0; bulk red; UI red) | **PASS** |
| Organizations create/update offline green; singular delete excluded; bulk red | **PASS** |
| Live, UI, vision, bulk, singular-delete cleanup, completeness | **not claimed / fail-closed** |

**Verdict: ACCEPT**

This authoritative root Grok product review accepts only the offline Wave-5p
organizations ticketed-write **create and update** product slice at root
baseline **`b4393a2`**
(`b4393a29293ff95c23fd9f39edbf57464689923c`), which contains product merge
`7bd7694`, product implementation `fbc8996`, and inventory reconcile `7a6f16d`.

This ACCEPT is not live testing, UI/vision acceptance, bulk resolution,
singular-delete authorisation or delete-cleanup qualification, webhook support,
or overall product completeness.

No production source, tests, coverage rows, status values, or prior contract
pages were modified by this review. Exclusive deliverable is this page.

## Reviewed baseline

| Item | Value |
| --- | --- |
| Root product baseline under review | `b4393a2` (`b4393a29293ff95c23fd9f39edbf57464689923c`) |
| Product merge | `7bd7694` (`merge main.billy_complete.wave5p_organizations_product`) |
| Product implementation commit | `fbc8996` (adds `organization_writes.py` + tests + inventory greening for create/update) |
| Inventory reconcile | `7a6f16d` |
| Freeze page | `wiki/wave_fivep_ticketed_writes_contract.md` (full-file MD5 `2742eda7bafecd619aba5fa8ad0694c5`) |
| Freeze independent review | **ACCEPT** at `wiki/wave_fivep_freeze_independent_review.md` |
| Product module MD5 | `d656020400bd7003062e9689a9aec8d0` (`src/billy_mcp/api/organization_writes.py`) |
| Locked API base | `https://api.billysbilling.com/v2` (`src/billy_mcp/config.py`) |

Merge `7bd7694` and implementation `fbc8996` are ancestors of `b4393a2`. This
review targets the **root integration** on this branch, not a detached product
child worktree.

## Evidence classes (keep separate)

| Class | What it proves | What it does not prove |
| --- | --- | --- |
| Current official docs (`https://www.billy.dk/api/`) | Supports create and update; omits singular delete; property table for opaque-map and sensitivity treatment | Authenticated success, live mutation, cleanup qualification |
| This-review unauth probes (`https://api.billysbilling.com/v2`) | Method gates: JSON-object POST/PUT 401; singular DELETE 405 | Live mutation, accepted payloads, response extensions |
| Offline contract tests | Schema, tickets, path, mapping, no-retry, registry/coverage honesty | Live org behaviour, UI parity, vision |
| Live / UI / vision | Not performed | Not claimed |

## Official documentation (this review)

Fetched `https://www.billy.dk/api/` during this review (curl only; no headed
browser):

| Fingerprint field | Observed value |
| --- | --- |
| HTTP status | 200 |
| HTTP ETag | `wcw4x9hqvu3603` |
| Body MD5 | `8b94b0135c91fd15fe54ea33e088a4be` |
| Body size | 147934 bytes |

Inventory lock still records ETag `hsisik4g9p3603` / MD5
`c2efda0ee4cf9cf200e14910c5fc6996` while access meta is
`wcw4x9hqvu3603` / `8b94b0135c91fd15fe54ea33e088a4be` at the same 147934-byte
size. Access-metadata churn alone is not a contract change (same reading as the
freeze independent review and `wiki/offline_write_probe_rules.md`).

Direct citation for `/v2/organizations` (plain text from the official HTML):

> Supports: get by id, list, create, update, bulk save, bulk delete

Official Supports **lists create and update** and **omits singular delete**.
Bulk save/delete remain listed on docs but stay out of this product (ambiguous
bulk inventory rows, empty tool names).

Property notes observed on the same page (opaque inner map; not Pydantic field
validation):

| Property | Official notes | Product treatment check |
| --- | --- | --- |
| `ownerUser` | required | Opaque inner map only — **PASS** |
| `name` | required | Opaque inner map only — **PASS** |
| `country` | immutable, required | Opaque; immutability is a boundary, not write permission — **PASS** |
| `baseCurrency` | immutable, required | Opaque; same boundary — **PASS** |
| `fiscalYearEndMonth` / `firstFiscalYearStart` / `firstFiscalYearEnd` | required | Opaque; no invented numeric/date encoding — **PASS** |
| `subscriptionPeriod` | required enum | Opaque; no enum set frozen in tools — **PASS** |
| `subscriptionCardType` / `subscriptionCardNumber` / `subscriptionCardExpires` | (empty notes) | Sensitive keys registered in `redaction.py` — **PASS** (see redaction) |
| Documented readonly fields (e.g. `createdTime`, `url`, `isTrial`) | readonly | Not required outer tool fields — **PASS** |

## Unauthenticated probes (evidence only, not live qualification)

Against locked base `https://api.billysbilling.com/v2` with JSON object bodies,
no credentials:

| Call | Result |
| --- | --- |
| `POST /organizations` body `{"organization":{"name":"probe-no-auth"}}` | **401** `AUTHENTICATION_REQUIRED` (`meta.statusCode` 401) |
| `PUT /organizations/probe-id` body `{"id":"probe-id","organization":{"name":"probe-no-auth"}}` | **401** `AUTHENTICATION_REQUIRED` |
| `DELETE /organizations/probe-id` | **405** `METHOD_NOT_ALLOWED` |

These reconfirm the freeze gates: POST/PUT open at the authentication gate for
singular create/update; singular DELETE is closed and therefore **excluded**
from the product surface. They are not authenticated live tests and do not
green `live_tested`.

## Accepted product surface

Exactly four ticketed write tools (plus pre-existing read tools
`api_organizations_get` / `api_organizations_list` / `api_user_list_organizations`,
which are not part of this write product ACCEPT):

| Inventory id | Preview tool | Execute tool | Method and client path | Singular request root | Required success root |
| --- | --- | --- | --- | --- | --- |
| `api.organizations.create` | `api_organizations_create_preview` | `api_organizations_create_execute` | `POST /organizations` | `organization` | `organizations` |
| `api.organizations.update` | `api_organizations_update_preview` | `api_organizations_update_execute` | `PUT /organizations/:id` | `organization` | `organizations` |

Implementation: `src/billy_mcp/api/organization_writes.py` (MD5
`d656020400bd7003062e9689a9aec8d0`), registered from `src/billy_mcp/server.py`
via `register_organization_write_tools` on the shared root
`WriteProtocolService` and `ConfirmationStore`. Client base remains locked to
`https://api.billysbilling.com/v2`.

No organizations singular delete, bulk, webhook, generic HTTP, or browser write
tool is registered by this product.

## Assertions checked

| # | Assertion | Result | Evidence |
| --- | --- | --- | --- |
| 1 | Exactly four create/update preview+execute tools; no delete/bulk write tools for this product | **PASS** | `organization_writes.py` registers exactly four `server.tool` names; focused test `test_registers_exactly_four_flat_typed_organization_write_tools` asserts set equality and forbids delete/bulk names |
| 2 | Strict outer models (`extra="forbid"`); opaque `organization` maps; update path/body id matching | **PASS** | `OrganizationCreatePreviewInput` / `OrganizationUpdatePreviewInput`; update validator rejects `organization.id != id`; empty `id` rejected (`minLength=1`); extras forbidden |
| 3 | Ticket-only execute; exact binding; single use; expiry; tamper; wrong-executor; replay | **PASS** | Execute inputs are `confirmation_ticket` only; `WriteProtocolService.execute` checks binding tool name, `ConfirmationStore.consume`, then discards prepared ticket; org write tests cover mismatch, replay, expiry, and invalid tickets |
| 4 | One HTTP write with no retry; required `organizations` response root | **PASS** | `BillyHttpClient.request` sets write retries to 0 (`_RETRY_SAFE_METHODS` is GET/HEAD only); execute calls `_client.request` once after consume; missing/malformed `organizations` root → `VALIDATION_ERROR`; success maps `changed_records.organizations` |
| 5 | Spec path and roots match freeze | **PASS** | `_organization_specification`: `collection_path="/organizations"`, `singular_root="organization"`, `plural_root="organizations"`, POST create / PUT update only |
| 6 | Sensitive subscription-card redaction | **PASS** | `src/billy_mcp/redaction.py` registers `subscriptionCardType`, `subscriptionCardNumber`, `subscriptionCardExpires` (and related subscription keys), case-insensitive; applied in upstream error envelopes (`errors.py`) and organization read mapping (`bootstrap_reads.py`); unit redaction tests cover the organization subscription fixture. Write success mapping uses the shared protocol record map (no extra log retention of card data in this product). Review retained no card values. |
| 7 | Create inventory offline-green with cleanup wording; response field `organizations[]`; update offline-green; bulk remain red; no singular delete inventory row | **PASS** | `api.organizations.create`: `implemented`+`contract_tested` true, `live_tested` false, cleanup `live non-production cleanup strategy unqualified; singular DELETE is unsupported`, `response_fields: ["organizations[]"]`. `api.organizations.update`: offline green. Bulk save/delete empty-tool `ambiguous_bulk` red. No `api.organizations.delete` inventory row. |
| 8 | Root **260** `api_*` tools; **177** implemented/contract-tested; live **0**; vision **0**; bulk ambiguous **92**; UI all red; `complete: false` | **PASS** | `coverage/status.json` qualification + source_counts; `tests/unit/test_coverage_server.py` asserts `len(api_tool_names) == 260`; UI manifest walk: 339 rows, 0 implemented/contract/live; API ops: 0 live_tested, 0 vision_verified, 92 ambiguous bulk all red |
| 9 | Server registration on shared write protocol; locked API host | **PASS** | `server.py` imports and calls `register_organization_write_tools(server, client, write_protocol)`; `config.py` locks `API_BASE_URL` |
| 10 | Current docs support create+update; omit singular delete; 401/405 evidence accurate and not claimed as live testing | **PASS** | Official Supports quote above; probes table above; explicit non-live wording |
| 11 | No sensitive material, raw browser evidence, live mutation, or UI/vision claim retained in tracked paths | **PASS** | This page uses public docs fingerprints, unauth status codes, offline tests, and committed source only |
| 12 | Focused organization write/coverage/registry/policy checks pass offline | **PASS** | Node `scripts/test.sh` results below |

## Commands and results

```text
# Official docs
curl -sS -D headers -o billy-api-docs.html https://www.billy.dk/api/
# HTTP/2 200; etag "wcw4x9hqvu3603"; content-length 147934;
# MD5 8b94b0135c91fd15fe54ea33e088a4be

# Unauth method gates (no token; JSON object body)
POST   /v2/organizations {...}              -> 401 AUTHENTICATION_REQUIRED
PUT    /v2/organizations/probe-id {...}     -> 401 AUTHENTICATION_REQUIRED
DELETE /v2/organizations/probe-id           -> 405 METHOD_NOT_ALLOWED

# Focused offline product + coverage + registry + policy (node test.sh)
bash .fractal/main.billy_complete.wave5p_product_review/scripts/test.sh
# pytest: 34 passed in 4.63s
#   tests/api/test_organization_writes.py (19)
#   tests/coverage/test_coverage_inventory.py (13)
#   tests/unit/test_coverage_server.py (2)
# check_coverage.py --reject-false-completeness: passed (305 API, 339 UI)
# check_repository_policy.py: passed
# exit 0
```

## Coverage and fail-closed boundaries

| Metric | Value at `b4393a2` product surface |
| --- | --- |
| `api_*` tools | **260** |
| `implemented_rows` | **177** |
| `contract_tested_rows` | **177** |
| `live_tested_rows` | **0** |
| `vision_verified_rows` | **0** |
| `api_ambiguous_bulk` | **92** (all red / empty tool) |
| `complete` | **false** |
| `api.organizations.create` | offline green; cleanup says singular DELETE unsupported; response `organizations[]` |
| `api.organizations.update` | offline green |
| `api.organizations.bulk_save` / `.bulk_delete` | empty-tool red (`ambiguous_bulk`) |
| Singular delete inventory row | **absent** (correct; not greened; DELETE 405) |
| All UI rows (339) | remain red / unqualified |
| Live / vision for all API rows | remain 0 / unqualified |

**Reading of "only organizations create/update may be green offline" for this
slice:** prior waves already greened other offline API rows. At this baseline
the organizations CUD surface has only create and update offline-green; bulk
stays red; singular delete has no inventory row and no tools. Global offline
count is 177, not 2.

## Explicit non-accepts

- Live API qualification (`live_tested` remains false; status blocker still
  notes `BILLY_API_TOKEN` unavailable).
- All UI parity and vision verification.
- Ambiguous bulk save/delete tools and greening.
- Singular delete tools (Supports omit; DELETE 405; cleanup wording is not
  cleanup qualification).
- Webhooks, generic HTTP escape hatches, headed browser controls.
- Overall project completeness (`complete` remains false).
- Any claim that unauth 401/405 probes are live testing.
- Any claim that create cleanup wording is live cleanup qualification.

## Protocol alignment

Shared design ticket protocol in
`docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md` (preview then
ticket-only execute; short-lived single-use tickets; no silent retries) matches
the product implementation through `WriteProtocolService` and
`ConfirmationStore`. Consume-before-request and a single
`BillyHttpClient.request` with write retries forced to zero enforce no silent
retry on the prepared write.

## Authorisation opened by this ACCEPT

With this offline product ACCEPT on root, parent orchestration may treat
Wave-5p singular organizations **create and update** as product-gated offline
and may proceed to the next researched offline freeze/product slice. That later
work requires its own freeze and independent reviews. This page does not
authorise live greening, bulk tools, or singular delete.

## Scratch evidence (not for git)

Node-local only under
`.fractal/main.billy_complete.wave5p_product_review/tmp/evidence/` (purged or
status-only after review):

- docs HTML + headers for fingerprint
- unauth probe status codes and error codes only

## Verdict line

**ACCEPT**
