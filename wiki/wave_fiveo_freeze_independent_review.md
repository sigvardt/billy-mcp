---
name: wave_fiveo_freeze_independent_review
title: Wave-5o contract freeze independent review ACCEPT
desc: Authoritative root Grok acceptance of the cited offline contract for singular invoiceReminders create ticketed writes (update, delete, bulk, and association writes excluded).
tags: [billy, api, invoice-reminders, writes, review, coverage]
sources:
  - https://www.billy.dk/api/
  - https://api.billysbilling.com/v2
  - wiki/wave_fiveo_ticketed_writes_contract.md
  - wiki/wave_fiveo_freeze_authoring_research_independent_review.md
  - wiki/wave_fiveo_freeze_ready_research_independent_review.md
  - wiki/wave_fiven_product_independent_review.md
  - wiki/offline_write_probe_rules.md
  - coverage/api_v2_manifest.yaml
  - coverage/status.json
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
created: 2026-07-30T10:46:00Z
updated: 2026-07-30T10:46:00Z
---

# Wave-5o contract freeze independent review ACCEPT

## Verdict

| Claim | Result |
| --- | --- |
| Wave-5o cited contract freeze | **ACCEPT** |
| Official documentation versus freeze map | **PASS** |
| Unauth method gates (POST 401 JSON body; PUT, singular DELETE, bulk DELETE 405) | **PASS** |
| Freeze versus exact one-row / two-tool map | **PASS** |
| Coverage honesty before product integration | **PASS** |
| Wave-5o product implementation | **not accepted** - separate parent-managed Codex Power product leaf and product review required |
| Live, UI, vision, bulk, and completeness | **not claimed / fail-closed** |

**Verdict: ACCEPT**

This authoritative root Grok independent review accepts the freeze page
`wiki/wave_fiveo_ticketed_writes_contract.md` (content MD5
`6fec5754cc76c4a07b344021cbc3c36b`) at reviewed root baseline `a6a56cf`
(`a6a56cf6dca41d8f9695297576824edea832975e`). Branch tip `33ad102` is the node
init commit only; freeze content at HEAD matches `a6a56cf` byte-for-byte.

This page is the freeze gate for Wave-5o. It is not product acceptance.

## Reviewed baseline

| Item | Value |
| --- | --- |
| Root commit | `a6a56cf` (`a6a56cf6dca41d8f9695297576824edea832975e`) |
| Freeze page | `wiki/wave_fiveo_ticketed_writes_contract.md` |
| Freeze content MD5 | `6fec5754cc76c4a07b344021cbc3c36b` |
| Prerequisite product | Wave-5n product offline ACCEPT (`wiki/wave_fiven_product_independent_review.md`) |
| Prior research (not freeze ACCEPT) | `wiki/wave_fiveo_freeze_ready_research_independent_review.md`, `wiki/wave_fiveo_freeze_authoring_research_independent_review.md` |

## Sources and method

| Source | How used |
| --- | --- |
| https://www.billy.dk/api/ | Primary. Live fetch this review: HTTP ETag `wcw4x9hqvu3603`, body MD5 `8b94b0135c91fd15fe54ea33e088a4be`, 147934 bytes. Matches freeze research64 access meta. Inventory lock still records ETag `hsisik4g9p3603` / MD5 `c2efda0ee4cf9cf200e14910c5fc6996`; access-metadata churn alone is not a contract change. `/v2/invoiceReminders` Supports and property table re-parsed from the fetched HTML. |
| Unauth probes `https://api.billysbilling.com/v2` | Independent reconfirm with JSON object body and no token: `POST /invoiceReminders` with `{}` → 401 `AUTHENTICATION_REQUIRED`; `PUT /invoiceReminders/nonexistent-probe-id` with `{}` → 405 `METHOD_NOT_ALLOWED` (“does not support updating records”); singular `DELETE /invoiceReminders/nonexistent-probe-id` → 405 (“does not support deleting a single record”); bulk `DELETE /invoiceReminders?ids[]=nonexistent` → 405 (“does not support bulk deleting records”). Not live qualification. |
| `wiki/wave_fiveo_ticketed_writes_contract.md` | Full freeze surface under review. |
| `wiki/offline_write_probe_rules.md` | Auth-gate vs 405 override rules; `invoiceReminders` row records POST 401 and PUT/DELETE/bulk DELETE 405. |
| `coverage/api_v2_manifest.yaml` @ `a6a56cf` | Five `invoiceReminders` rows: get/list green offline; create red with reserved preview tool name only; both bulk empty-tool `ambiguous_bulk`; no singular update or delete inventory rows. |
| `coverage/status.json` @ `a6a56cf` | `implemented_rows` 174, `contract_tested_rows` 174, `live_tested_rows` 0, `vision_verified_rows` 0, `api_ambiguous_bulk` 92, `complete: false`. |
| Registry @ `a6a56cf` | 254 unique `api_*` tools per `tests/unit/test_coverage_server.py`; only `api_invoice_reminders_get` and `api_invoice_reminders_list` for this resource (no create write tools). |
| Design `docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md` | Ticketed write / confirmation protocol discipline (strict preview, ticket-only execute, no silent retries). |
| Prior research pages | Context only; this review re-fetched docs and re-probed gates rather than copying research64. |

No headed browser. No credentials. No live mutations. No raw probe bodies retained in tracked paths.

## Exact reviewed scope

The accepted contract freezes exactly one singular API v2 JSON create operation
(two ticketed tools: one preview + one execute):

| Inventory id | Preview tool | Execute tool | Method and client path | Singular request root | Required success root |
| --- | --- | --- | --- | --- | --- |
| `api.invoiceReminders.create` | `api_invoice_reminders_create_preview` | `api_invoice_reminders_create_execute` | `POST /invoiceReminders` | `invoiceReminder` | `invoiceReminders` |

Official docs for `/v2/invoiceReminders` (this review): Supports **get by id,
list, create, bulk save, bulk delete**. Update and singular delete are omitted.
Property table (this review):

| Property | Official notes | Freeze treatment check |
| --- | --- | --- |
| `organization` | belongs-to; immutable, required | Required opaque value only; no relation wire form - **PASS** |
| `contact` | belongs-to; required | Required opaque value only; no relation wire form - **PASS** |
| `createdTime` | datetime; readonly | Not a mutable outer field - **PASS** |
| `associations` | has-many; notes empty | Opaque supplied value only; no association schema - **PASS** |
| `flatFee` | float; notes empty | Opaque; no number encoding - **PASS** |
| `percentageFee` | float; notes empty | Opaque; no number encoding - **PASS** |
| `feeCurrency` | belongs-to; required | Required opaque value only; no relation wire form - **PASS** |
| `sendEmail` | boolean; notes empty | Opaque; no email-send promise - **PASS** |
| `contactPerson` | belongs-to; required | Required opaque value only; no relation wire form - **PASS** |
| `emailSubject` | string; required | Required opaque value only; no extra string semantics - **PASS** |
| `emailBody` | string; required | Required opaque value only; no extra string semantics - **PASS** |
| `copyToUser` | belongs-to; notes empty | Opaque; no relation wire form - **PASS** |
| `downloadUrl` | string; notes empty | Unproven; not required on create; no download semantics - **PASS** |

No official create sample establishes a more specific `invoiceReminder` inner
map; the freeze correctly refuses to invent one.

## Criteria checked

| # | Criterion | Result |
| --- | --- | --- |
| 1 | Authorises exactly `api.invoiceReminders.create` and exactly `api_invoice_reminders_create_preview` + `api_invoice_reminders_create_execute` | **PASS** - single table row; execute twin is not a second inventory row; no other operation or tool frozen |
| 2 | Freezes only client-relative `POST /invoiceReminders`, outer `{invoiceReminder: map}`, ticket-only execute, shared confirmation/write services, exactly one non-retried write, required-root-only `invoiceReminders` response mapping | **PASS** - all stated on the freeze page; paths omit `/v2` as client-relative |
| 3 | Inner map opaque; all documented field boundaries preserved; no relation wire-form, nested association, date/number, email, or download semantics claim | **PASS** - property table matches current official notes; every field is opaque or unproven without invented wire form |
| 4 | Evidence treats `POST {}` 401 as offline create gate; PUT, singular DELETE, bulk DELETE 405 as exclusions; update, delete, both bulk rows, association writes, webhooks, live/UI/vision, cleanup qualification, coverage changes, product, and completeness remain excluded | **PASS** - independently reconfirmed this review; freeze exclusion list matches; Supports omits update and singular delete |
| 5 | Root inventory 174 implemented/contract-tested, live 0, vision 0, 92 ambiguous bulk, `complete: false`; invoiceReminders create still red | **PASS** - `coverage/status.json` and manifest create row `implemented: false`, `contract_tested: false` |

No discrepancy requires REJECT.

## Assertions checked (detail)

| Assertion | Result |
| --- | --- |
| Exactly singular create; two named ticketed tools | **PASS** |
| Path `POST /invoiceReminders` (client-relative, no double `/v2`) | **PASS** |
| Singular request root `invoiceReminder`; required success root `invoiceReminders` | **PASS** |
| Strict outer `{invoiceReminder: map}`; opaque inner map | **PASS** |
| Ticket-only execute via shared `ConfirmationStore` + `WriteProtocolService`; one write and no retry | **PASS** |
| Immutable/readonly/unproven field treatment; no invented relation, association, date, number, email, or download semantics | **PASS** |
| JSON-object-body POST 401 evidence reconfirmed this review | **PASS** |
| PUT 405, singular DELETE 405, bulk DELETE 405 reconfirmed this review | **PASS** |
| No bulk tools frozen; bulk inventory rows remain empty-tool red `ambiguous_bulk` | **PASS** |
| No association write tools frozen; association create/update remain out of scope | **PASS** |
| No webhook documented for this surface | **PASS** |
| No live / UI / vision claim; no product create write registration at baseline | **PASS** |
| Coverage honesty: 254 `api_*` tools, 174 offline implemented and contract-tested, 0 live, 0 vision, 92 bulk ambiguous, `complete: false` | **PASS** |

## Protocol and inventory notes (non-blocking)

- Shared protocol on the freeze page matches prior accepted Wave-5 ticketed-write
 freezes and the design confirmation-ticket model.
- Inventory create `cleanup` still reads `delete dedicated test resource`. That
 text is inventory residual, not freeze authorisation. The freeze already
 requires later product greening to replace it with fail-closed wording that
 singular DELETE is unsupported. This does not reject the freeze page.
- Inventory create `response_fields` still list generic `changed_records[]`
 placeholders. The freeze correctly requires only the success root
 `invoiceReminders` for offline mapping.
- Current official docs ETag/MD5 match the freeze’s research64 access meta and
 differ from the older inventory lock; Supports and property contract for
 `invoiceReminders` are unchanged. This is access-metadata drift only.

## Product gate

Only after this freeze **ACCEPT** may a separate parent-managed Codex Power
product leaf implement and contract-test the two frozen create tools. Target
offline arithmetic after real tests and honest greening: implemented and
contract-tested **175** (174+1 inventory row for create; execute twin does not
add an inventory row), `api_*` tools **256** (254+2). Live and vision remain
zero; `coverage/status.json` stays `complete: false` until full qualification.
Create cleanup text must not claim singular delete.

This review does not create or configure that product child.

## Exclusions

This ACCEPT is not product acceptance, live qualification, UI/vision
acceptance, bulk resolution, webhook invention, update or singular delete
authorisation, association-write authorisation, coverage greening, cleanup
qualification, or overall completeness.

## Current-source findings vs inherited research

| Topic | Inherited research / freeze text | This independent review |
| --- | --- | --- |
| Docs fingerprint | ETag `wcw4x9hqvu3603`, MD5 `8b94b0135c91fd15fe54ea33e088a4be`, 147934 bytes | Re-fetched; identical |
| Supports | get by id, list, create, bulk save, bulk delete | Re-parsed HTML; identical; no update, no singular delete |
| Property table | 13 fields as on freeze page | Re-parsed; field names, types, and notes match freeze treatment |
| POST `{}` | 401 `AUTHENTICATION_REQUIRED` | Reconfirmed 401 `AUTHENTICATION_REQUIRED` |
| PUT | 405 update unsupported | Reconfirmed 405 `METHOD_NOT_ALLOWED` (updating records) |
| Singular DELETE | 405 single-record unsupported | Reconfirmed 405 |
| Bulk DELETE | 405 bulk delete unsupported | Reconfirmed 405 |
| Inventory honesty | 174 / 0 live / 0 vision / 92 bulk / complete false; create red | Re-read `coverage/status.json` and create row; match |

No inherited claim about this freeze surface was contradicted by the current
official source or the unauth method gates.

## Verdict line

**ACCEPT**
