---
name: wave_fiveo_product_independent_review
title: Wave-5o invoice-reminder product independent review ACCEPT
desc: Authoritative offline Grok ACCEPT for singular invoiceReminders create ticketed write tools on root afbe5188; update, delete, bulk, associations, live, UI, vision, and completeness remain fail-closed.
tags: [billy, api, invoice-reminders, writes, review, product]
sources:
  - https://www.billy.dk/api/
  - https://api.billysbilling.com/v2
  - wiki/wave_fiveo_ticketed_writes_contract.md
  - wiki/wave_fiveo_freeze_independent_review.md
  - wiki/offline_write_probe_rules.md
  - coverage/api_v2_manifest.yaml
  - coverage/status.json
  - scripts/generate_coverage_report.py
  - src/billy_mcp/api/invoice_reminder_writes.py
  - src/billy_mcp/api/write_protocol.py
  - src/billy_mcp/server.py
  - src/billy_mcp/client.py
  - src/billy_mcp/config.py
  - tests/api/test_invoice_reminder_writes.py
  - tests/unit/test_coverage_server.py
  - tests/coverage/test_coverage_inventory.py
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
created: 2026-07-30T11:55:00Z
updated: 2026-07-30T11:55:00Z
---

# Wave-5o invoice-reminder product independent review ACCEPT

## Verdict

| Claim | Result |
| --- | --- |
| Wave-5o offline product (singular create ticketed writes only) | **ACCEPT** |
| Official documentation versus create-only product surface | **PASS** |
| Exactly two write tools versus freeze contract | **PASS** |
| Ticket binding, path lock, response-root mapping, no-retry | **PASS** |
| Coverage honesty (`complete: false`; live 0; vision 0; bulk red; no update/delete tools) | **PASS** |
| Live, UI, vision, bulk, update, singular delete, association writes, webhooks, completeness | **not claimed / fail-closed** |

**Verdict: ACCEPT**

This authoritative root Grok product review accepts only the offline Wave-5o
invoice-reminder ticketed-write **create** product slice at parent baseline
**`afbe5188`** (`afbe5188b029e89e7e865a6b9ee8b9a5881f51f4`), which contains
product merge `78108f2` and the product implementation commit `81bf925`.

This ACCEPT is not live testing, UI/vision acceptance, bulk resolution, update
or singular-delete authorisation, association-write authorisation, webhook
support, or overall product completeness.

No production source, tests, coverage rows, status values, or prior contract
pages were modified by this review.

## Reviewed baseline

| Item | Value |
| --- | --- |
| Root product baseline | `afbe5188` (`afbe5188b029e89e7e865a6b9ee8b9a5881f51f4`) |
| Product merge | `78108f2` (`merge main.billy_complete.wave5o_invoice_reminder_product`) |
| Product implementation commit | `81bf925` (adds `invoice_reminder_writes.py` + tests + inventory greening for create) |
| Freeze page | `wiki/wave_fiveo_ticketed_writes_contract.md` (full-file MD5 `6fec5754cc76c4a07b344021cbc3c36b`) |
| Freeze independent review | **ACCEPT** at `wiki/wave_fiveo_freeze_independent_review.md` |

Product file content at baseline matches the worktree copy under review
(MD5 `892d5c2950151072555d1d1017dce927`). Merge `78108f2` is an ancestor of
`afbe5188`.

## Evidence classes (keep separate)

| Class | What it proves | What it does not prove |
| --- | --- | --- |
| Current official docs (`https://www.billy.dk/api/`) | Supports create; omits update and singular delete; property table for opaque-map treatment | Authenticated success, email side effects, cleanup, live qualification |
| This-review unauth probes (`https://api.billysbilling.com/v2`) | Method gates: POST 401; PUT, singular DELETE, bulk DELETE 405 | Live mutation, accepted payloads, response extensions |
| Offline contract tests | Schema, tickets, path, mapping, no-retry, registry/coverage honesty | Live org behaviour, UI parity, vision |
| Live / UI / vision | Not performed | Not claimed |

## Official documentation (this review)

Fetched `https://www.billy.dk/api/` during this review (curl only; no headed
browser):

| Fingerprint field | Observed value |
| --- | --- |
| HTTP ETag | `wcw4x9hqvu3603` |
| Body MD5 | `8b94b0135c91fd15fe54ea33e088a4be` |
| Body size | 147934 bytes |

These match the known public-doc body fingerprint cited for this review and the
freeze research access meta.

Direct citation for `/v2/invoiceReminders` (plain text from the official HTML):

> Supports: get by id, list, create, bulk save, bulk delete

Property notes observed on the same page:

| Property | Official notes | Product treatment check |
| --- | --- | --- |
| `organization` | immutable, required | Opaque inner map only — **PASS** |
| `contact` | required | Opaque; no relation wire form — **PASS** |
| `createdTime` | readonly | Not a mutable outer field — **PASS** |
| `associations` | (empty notes) | Opaque only; no association write tools — **PASS** |
| `flatFee` / `percentageFee` | (empty notes) | Opaque; no number encoding invented — **PASS** |
| `feeCurrency` | required | Opaque; no relation wire form — **PASS** |
| `sendEmail` | (empty notes) | Opaque; no email-send promise — **PASS** |
| `contactPerson` | required | Opaque; no relation wire form — **PASS** |
| `emailSubject` / `emailBody` | required | Opaque strings only — **PASS** |
| `copyToUser` | (empty notes) | Opaque only — **PASS** |
| `downloadUrl` | (empty notes) | Unproven; not required on create — **PASS** |

Official Supports **omits update and singular delete**. That omission, together
with the PUT/DELETE 405 probes below, keeps update and singular delete out of
this product ACCEPT. Bulk save and bulk delete remain listed on docs but stay
out of this product (ambiguous bulk inventory rows, empty tool names).

Inventory lock still records ETag `hsisik4g9p3603` / MD5
`c2efda0ee4cf9cf200e14910c5fc6996` while access meta is
`wcw4x9hqvu3603` / `8b94b0135c91fd15fe54ea33e088a4be` at the same 147934-byte
size. Access-metadata churn alone is not a contract change (same reading as the
freeze independent review and `wiki/offline_write_probe_rules.md`).

## Unauthenticated probes (evidence only, not live qualification)

Against locked base `https://api.billysbilling.com/v2` with JSON object body,
no credentials:

| Call | Result |
| --- | --- |
| `POST /invoiceReminders` body `{}` | **401** `AUTHENTICATION_REQUIRED` |
| `PUT /invoiceReminders/nonexistent-probe-id` body `{}` | **405** `METHOD_NOT_ALLOWED` — resource does not support updating records |
| `DELETE /invoiceReminders/nonexistent-probe-id` | **405** `METHOD_NOT_ALLOWED` — resource does not support deleting a single record |
| `DELETE /invoiceReminders?ids[]=nonexistent` | **405** `METHOD_NOT_ALLOWED` — resource does not support bulk deleting records |

These reconfirm the freeze gates. They are not authenticated live tests and do
not green `live_tested`.

## Accepted product surface

Exactly two ticketed write tools (plus the pre-existing read tools
`api_invoice_reminders_get` / `api_invoice_reminders_list`, which are not part of
this write product ACCEPT):

| Inventory id | Preview tool | Execute tool | Method and client path | Singular request root | Required success root |
| --- | --- | --- | --- | --- | --- |
| `api.invoiceReminders.create` | `api_invoice_reminders_create_preview` | `api_invoice_reminders_create_execute` | `POST /invoiceReminders` | `invoiceReminder` | `invoiceReminders` |

Implementation: `src/billy_mcp/api/invoice_reminder_writes.py`, registered from
`src/billy_mcp/server.py` via `register_invoice_reminder_write_tools` on the
shared root `WriteProtocolService` and `ConfirmationStore`. Client base remains
locked to `https://api.billysbilling.com/v2` in `src/billy_mcp/config.py`.

No invoiceReminders update, delete, bulk, webhook, generic HTTP, or browser
write tool is registered by this product. Association write inventory rows for
`invoiceReminderAssociations` remain red and unregistered as write tools.

## Assertions checked

| # | Assertion | Result | Evidence |
| --- | --- | --- | --- |
| 1 | Exactly two create preview+execute tools; no update/delete/bulk/webhook/generic HTTP/browser write tools for this product | **PASS** | `invoice_reminder_writes.py` registers exactly two `server.tool` names; module docstring and `_invoice_reminder_create_specification` are create/POST only; focused tests assert set equality and forbid update/delete/bulk names on the write server under test |
| 2 | One non-retried `POST /invoiceReminders` maps singular `invoiceReminder` → plural `invoiceReminders` only | **PASS** | Spec uses `method=WriteMethod.POST`, `collection_path="/invoiceReminders"`, `singular_root="invoiceReminder"`, `plural_root="invoiceReminders"`, `additional_plural_roots=()`; execute test asserts raw path `/v2/invoiceReminders`, body equals preview canonical request, and drops unrelated `invoices` response root |
| 3 | Preview rejects unknown outer fields and preserves opaque JSON inner maps; execute is ticket-only | **PASS** | Pydantic `extra="forbid"` on `InvoiceReminderCreatePreviewInput`; opaque `dict[str, JsonValue]`; execute takes only `confirmation_ticket` with `minLength=1`; validation tests reject missing/extra outer fields and non-ticket execute payloads |
| 4 | Preview is mutation-free; shared tickets bind executor, payload, expected effect; single-use; wrong-executor, expiry, replay, and tamper reject without unexpected writes | **PASS** | Preview test fails if any HTTP request is made; `WriteProtocolService.execute` consumes ticket then issues exactly one `_client.request`; wrong-executor → `CONFIRMATION_MISMATCH`; tamper → `CONFIRMATION_INVALID`; replay → `CONFIRMATION_CONSUMED`; expiry → `CONFIRMATION_EXPIRED`; after first success `len(requests) == 1` |
| 5 | Response mapping accepts only required plural root; typed errors for malformed/missing roots and HTTP/auth failures | **PASS** | Success maps only `invoiceReminders`; missing/malformed root → `VALIDATION_ERROR`; 401/404/500 mapped; empty token → `AUTH_REQUIRED` with zero network; failed write is not retried (500 test asserts one call) |
| 6 | Server registration on shared write protocol; locked API host | **PASS** | `server.py` imports and calls `register_invoice_reminder_write_tools(server, client, write_protocol)`; `config.py` locks `API_BASE_URL` to `https://api.billysbilling.com/v2`; `BillyHttpClient` is the locked host client |
| 7 | Create inventory row offline-green with fail-closed cleanup wording; no singular update/delete rows; bulk remain red | **PASS** | `coverage/api_v2_manifest.yaml`: `api.invoiceReminders.create` has `implemented: true`, `contract_tested: true`, `live_tested: false`, cleanup `live non-production cleanup strategy unqualified; singular DELETE is unsupported`; bulk save/delete empty-tool `ambiguous_bulk` red; no singular update or delete inventory rows |
| 8 | Root **256** `api_*` tools; **175** implemented/contract-tested; live **0**; vision **0**; bulk ambiguous **92**; `complete: false` | **PASS** | `coverage/status.json` qualification + source_counts; `tests/unit/test_coverage_server.py` asserts `len(api_tool_names) == 256` |
| 9 | Coverage generator points create row at focused write tests | **PASS** | `scripts/generate_coverage_report.py` maps `api.invoiceReminders.create` → `tests/api/test_invoice_reminder_writes.py` and expected success root `invoiceReminders[]` |
| 10 | Current docs support create and do not justify update or singular delete; 401/405 evidence accurate and not claimed as live testing | **PASS** | Official Supports quote above; probes table above; explicit non-live wording |
| 11 | No sensitive material, raw browser evidence, live mutation, or UI/vision claim | **PASS** | This page and the review method use only public docs, unauth status codes, offline tests, and committed source; no tokens, frames, HAR, or customer data |
| 12 | Focused invoice-reminder write/coverage/registry checks pass offline | **PASS** | Commands/results below |

## Commands and results

```text
# Official docs
curl -sS -D headers -o billy-api-docs.html https://www.billy.dk/api/
# HTTP/2 200; etag "wcw4x9hqvu3603"; content-length 147934;
# MD5 8b94b0135c91fd15fe54ea33e088a4be

# Unauth method gates (no token; JSON object body)
POST /v2/invoiceReminders {}                         -> 401 AUTHENTICATION_REQUIRED
PUT  /v2/invoiceReminders/nonexistent-probe-id {}    -> 405 METHOD_NOT_ALLOWED
DELETE /v2/invoiceReminders/nonexistent-probe-id     -> 405 METHOD_NOT_ALLOWED
DELETE /v2/invoiceReminders?ids[]=nonexistent        -> 405 METHOD_NOT_ALLOWED

# Focused offline product + coverage + registry
uv run pytest tests/api/test_invoice_reminder_writes.py \
  tests/unit/test_coverage_server.py \
  tests/coverage/test_coverage_inventory.py -q
# 30 passed in 4.71s

# Node test.sh (orchestrator no-op; exit 0)
bash .fractal/main.billy_complete.wave5o_product_review/scripts/test.sh
# exit 0
```

## Coverage and fail-closed boundaries

| Metric | Value at `afbe5188` product surface |
| --- | --- |
| `api_*` tools | **256** |
| `implemented_rows` | **175** |
| `contract_tested_rows` | **175** |
| `live_tested_rows` | **0** |
| `vision_verified_rows` | **0** |
| `api_ambiguous_bulk` | **92** |
| `complete` | **false** |
| `api.invoiceReminders.create` | offline green (`implemented` + `contract_tested`) |
| `api.invoiceReminders.bulk_save` / `.bulk_delete` | empty-tool red (`ambiguous_bulk`) |
| Singular update / delete inventory rows | **absent** (correct; not greened) |
| `invoiceReminderAssociations` create/update/delete | remain red (not greened by this product) |
| All UI / vision rows for this resource | remain red / unqualified |

## Explicit non-accepts

- Live API qualification (`live_tested` remains false; `BILLY_API_TOKEN` still unavailable per status blocker).
- All UI parity and vision verification.
- Ambiguous bulk save/delete tools and greening.
- Update tools (Supports omit update; PUT 405).
- Singular delete tools (Supports omit; DELETE 405).
- Invoice-reminder association writes.
- Webhooks, generic HTTP escape hatches, headed browser controls.
- Overall project completeness (`complete` remains false).
- Any claim that unauth 401/405 probes are live testing.
- Any claim that cleanup wording is cleanup qualification.

## Protocol alignment

Shared design ticket protocol in
`docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md` (preview then
ticket-only execute; short-lived single-use tickets; no silent retries) matches
the product implementation through `WriteProtocolService` and
`ConfirmationStore`. Consume-before-request and a single
`BillyHttpClient.request` path enforce no silent retry on the prepared write.

## Authorisation opened by this ACCEPT

With this offline product ACCEPT on root, parent orchestration may treat
Wave-5o singular invoiceReminders **create** as product-gated offline and may
proceed to the next researched offline freeze/product slice. That later work
requires its own freeze and independent reviews. This page does not authorise
live greening, bulk tools, update, singular delete, or association writes.

## Scratch evidence (not for git)

Node-local only under
`.fractal/main.billy_complete.wave5o_product_review/tmp/`:

- `api.html` / `docs.headers`
- unauth probe JSON snippets (`p1.json` … `p4.json`)

## Verdict line

**ACCEPT**
