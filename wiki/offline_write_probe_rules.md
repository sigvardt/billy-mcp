---
name: offline_write_probe_rules
title: Offline write probe rules from official docs and unauth API gates
desc: Durable rules for official Supports, typed nested write payloads, and bulk freeze.
tags: [billy, api, writes, probes]
sources:
  - https://www.billy.dk/api/
  - https://api.billysbilling.com/v2
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
created: 2026-07-29T21:20:00Z
updated: 2026-08-20T03:50:00Z
---

# Offline write probe rules from official docs and unauth API gates

## Authority

Derived from Billy's public API docs at https://www.billy.dk/api/
(current HTTP access ETag `wcw4x9hqvu3603`, MD5
`8b94b0135c91fd15fe54ea33e088a4be`, body 147934 bytes as of 2026-07-30; stripped
plain contract is identical to the prior inventory lock ETag `hsisik4g9p3603` /
MD5 `c2efda0ee4cf9cf200e14910c5fc6996` after whitespace normalisation) and
unauthenticated probes against the locked base
`https://api.billysbilling.com/v2`. This is not live qualification and not
coverage green.

## Rules

1. Unauthenticated **POST/PUT 401** (`AUTHENTICATION_REQUIRED`) means the
   collection accepts the method at the auth gate. It is compatible with an
   offline ticketed-write freeze when Supports and inventory agree.
2. Unauthenticated **DELETE** of a missing id that returns **200** matches the
   docs' idempotent-delete narrative. It is **not** cleanup proof and not live
   qualification.
3. Current official Supports tables are the primary contract. An
   unauthenticated **405** (`METHOD_NOT_ALLOWED`) must not silently
   override them. When Supports lists a singular write **and** the
   official property table names at least one non-readonly field,
   ship the exact typed offline ticketed contract. When Supports
   lists singular **delete** with only a path `id` and no delete
   body table, ship the ticketed DELETE with no JSON body. Keep
   `live_tested` false (`live_api=out_of_scope_by_user`). When
   Supports lists a create/update write but the property table has
   no writable field map, record that contradiction and stay red.
   Live API proof stays out of scope.
4. Bulk save/delete remain empty-tool red until a request/response body contract
   exists. Supports bulk mentions alone are not enough. After research137 docs/asset exhaust, treat bulk as **external-contract blocked** (see below), not as
   an open evidence loop.
5. When the official property table names the exact writable fields for a
   singular write, the FastMCP preview payload is a nested Pydantic model of
   those fields with `extra=forbid`. Do not use an opaque JSON object for that
   payload. Enum members stay opaque strings unless the docs list them. Do not
   infer required fields from live API. `accountNatures` create/update follow
   this rule: `reportType`, `name`, and `normalBalance` only.
   `invoiceReminderAssociations` create/update follow it with required
   `reminder` and `invoice` strings. `lateFee` is readonly and is rejected
   at the FastMCP boundary. `cities` create/update follow it with optional
   string `name`, `county`, `state`, and `country`. Do not rename belongs-to
   fields to `stateId`/`countryId`. Empty payload is allowed. Do not infer
   required from the list filter `countryId`. `countryGroups` create/update
   follow it with optional string `name`, `icon`, and `memberCountryIds`.
   Official type of `memberCountryIds` is string, not array. Reject
   `memberCountries` and JSON arrays. Empty payload is allowed.
   `countries` create/update follow it with optional string `name`,
   boolean `hasStates`, `hasFiniteStates`, `hasFiniteZipcodes`,
   string `icon`, and belongs-to `locale` as an opaque string id.
   Reject `localeId`. Empty payload is allowed.
   Unauthenticated POST/PUT 405 is not the contract.
6. API traffic stays on `https://api.billysbilling.com/v2`. The docs' file-upload
   sample host `api.billy.dk` must never become the client base; host-lock tests
   should still deny it.


## Bulk external-contract freeze (research137)

Official docs and versioned assets were exhausted for exact bulk save/delete
request and response schemas (public page ETag `wcw4x9hqvu3603`, MD5
`8b94b0135c91fd15fe54ea33e088a4be`; page chunk Supports-only; OpenAPI/swagger
probes on official hosts return 404). No exact bulk body/response contract is
published.

Under user scope, live credentialed API qualification is out of scope. Offline
unauth shape evidence (research136) remains: `PUT /{plural}/bulk` requires a
JSON object root; object roots hit `AUTHENTICATION_REQUIRED` before field-level
bulk validation is visible; bulk delete form class uses `ids[]` in error text
only.

**Decision:** all 92 inventory bulk rows stay `ambiguous_bulk` red with machine-readable `qualification.kind=external_contract_blocker` and
`blocker_code=BULK_SCHEMA_UNSPECIFIED_OFFICIAL_DOCS`. No bulk FastMCP tools.
Do not run further bulk evidence-only iterations until Billy publishes schemas
or live API bulk qualification is re-opened by the user.

Shape hints from research136 remain non-authoritative for greening.

## Confirmed examples (unauth, no token)

| Resource | Finding |
| --- | --- |
| `salesTaxRulesets`, `salesTaxRules`, `salesTaxAccounts`, `salesTaxMetaFields`, `attachments` | POST/PUT 401; DELETE missing-id 200; OPTIONS includes the methods |
| `salesTaxPayments` | POST/PUT 401; singular DELETE **405** (Supports omits singular delete) |
| `salesTaxReturns` | POST/DELETE **405**; PUT 401 (Supports: update, no create/delete) |
| `accountNatures` | POST/PUT/DELETE **405** despite Supports create/update |
| `postings` | POST/PUT/DELETE **405**; property table effectively all readonly |
| `bankPayments` | POST/PUT 401; DELETE **405** despite Supports listing delete |
| `transactions` | POST/PUT 401; DELETE 200; property table almost all readonly — do not freeze from Supports alone |
| `balanceModifiers`, `contactBalancePostings` | POST/PUT/DELETE **405** (Supports create/update is not enough) |
| `cities`, `countries`, `currencies`, `states`, `zipcodes`, `locales`, `countryGroups` | POST/PUT/DELETE **405** — reference data not offline-writable |
| `contactBalancePayments` | POST/PUT 401; DELETE **405** |
| `invoiceLateFees` | POST/PUT 401; singular DELETE **405** (Supports omits singular delete); bulk DELETE `?ids[]=` also **405** “does not support bulk deleting records” despite Supports bulk delete |
| `invoiceReminders` | POST 401; PUT/DELETE **405** (Supports: create only among singular writes); bulk DELETE `?ids[]=` **405** |
| `invoiceReminderAssociations` | POST/PUT **405** historical unauth class; official Supports lists create/update with writable `reminder` and `invoice`, so those two rows are ticketed offline tools. DELETE missing-id 200 stays meta-delete unqualified. Collection DELETE without ids → **400** `INVALID_DELETE_ID_ARRAY` citing `ids[]` query form (bulk shape hint only) |
| `organizations` | POST/PUT 401; DELETE **405** |
| `users` | POST/DELETE **405**; PUT 401 (Supports: update, no create) |
| `files` | POST 401; PUT/DELETE **405**; property table all readonly — JSON create is not the binary upload special |
| `bankLineMatches`, `bankLines`, `bankLineSubjectAssociations` | POST/PUT 401; DELETE missing-id 200 — full singular CUD probe-open; property tables extracted (research40); match has-many `lines`/`subjectAssociations` document replace-on-set while Notes say readonly — live must prove embed; offline freeze may use opaque inners |
| invoice email special `POST /invoices/:id/emails` | POST with JSON object root **401**; non-object body **400**; GET/PUT/DELETE **405** (POST only) |
| invoice delivery special `POST /invoiceDeliveries` | POST **401**; GET collection **401** (not official TOC tool); GET `:id` **404**; PUT `:id` **401** (not official); DELETE **405**; nested `POST /invoices/:id/invoiceDeliveries` **404** `UNKNOWN_RESOURCE` |
| bulk candidate `PUT /{res}/bulk` with plural root | **401** on open resources (accounts, contacts, products, invoices, …); **405** on closed ref data | method-open candidate only — not a body/response contract |
| bulk path `POST /{res}/bulk` or `/bulkSave` | **405** | closed |
| bulk-looking `PATCH /{res}` with empty plural array | **200** meta-only unauth (`success: true`) | **not a contract**; never ship bulk tools from this |
| bulk delete `DELETE /{res}?ids[]=` | **200** meta-only on many open deletes; **405** where singular delete closed | shape hint; associations error text documents `ids[]` form |

### Research136 bulk-save body shape (contacts archetype; products cross-check)

Offline unauthenticated only. Official docs still list Supports “bulk save” /
“bulk delete” without path examples or field maps. Inventory may store **shape
hints** (`PUT /v2/{res}/bulk`, `json_object_root`, `DELETE …?ids[]=`) but rows
stay `ambiguous_bulk` / empty tool / not implemented.

| `PUT /{res}/bulk` body | Status | errorCode | Note |
| --- | --- | --- | --- |
| missing / null / string / `[]` / `[{}]` | **400** | `INVALID_REQUEST_BODY` | “JSON document with an **object as root**” |
| `{}`, `{"contacts":[]}`, wrong plural, `{"contacts":[{}]}` | **401** | `AUTHENTICATION_REQUIRED` | any object root passes body parse offline; plural-key schema **unproven** |
| empty-array no-op claim | — | — | **not** proven offline |

| `DELETE /{res}` query | Status | errorCode | Note |
| --- | --- | --- | --- |
| empty / missing `ids[]` | **400** | `INVALID_DELETE_ID_ARRAY` | form text: ``DELETE /contacts?ids[]=123&ids[]=456`` |
| synthetic non-empty `ids[]` | **200** | — | meta-only unauth — **not** effect or cleanup proof |

Never ship bulk FastMCP tools from Supports flags or these shape hints alone.
Scratch: `.fractal/main.billy_complete/tmp/write-probes-research136.json`,
`write-probes-research136-body.json`. Fixture:
`research136_bulk_save_body_matrix` in `src/billy_mcp/live_probe.py`.

Probe refresh: 2026-08-01 (research136 bulk body matrix; prior research88
residual clear full matrix + bulk shape matrix + specials reconfirm). HTTP docs
ETag `wcw4x9hqvu3603`, MD5 `8b94b0135c91fd15fe54ea33e088a4be`, body 147934 still
byte-identical. POST/PUT probes must send a JSON object body (`{}` minimum); a
missing body or `Content-Type: application/json` with empty/non-object body
yields **400** `INVALID_REQUEST_BODY` before auth and is not a method-closed
signal. Empty bytes without Content-Type may still reach **401** — product
always sends a JSON object. Scratch:
`.fractal/main.billy_complete/tmp/write-probes-research88.json` (residuals) and
research136 bulk body probes above.

## Planning note

Wave-5g through Wave-5s-C offline products are on root. Ticketed
`accountNatures` create/update later left the residual honesty freeze
(official Supports plus writable `reportType`, `name`, `normalBalance`).
Current generated snapshot: implemented **525**, contract **530**,
live/vision **339**, complete **false**. Residual honesty remaining **27**
(23 method-closed, 2 readonly-map, 2 meta-delete). Bulk **92** stay
`external_contract_blocker`. Live API stays `out_of_scope_by_user`. Next
offline slice is the remaining method-closed rows whose official property
tables still name writable fields. Do not infer bulk schemas. Detail:
[[wave_fives_residual_specials_research]] and
[[residual_clear_method_closed_inventory_honesty]].

## Wave-5s residual clear (research83)

After specials product (files upload + invoice email + invoiceDeliveries), the
remaining clear not-impl set is **29** rows. Unauth probes against
`https://api.billysbilling.com/v2` (no token, no persistent records) show:

1. **405 false friends (historical majority):** `accountNatures`, `balanceModifiers`,
   geo/reference create/update (`cities`, `countries`, `currencies`, `states`,
   `zipcodes`, `locales`, `countryGroups`), `contactBalancePostings`,
   `postings`, `invoiceReminderAssociations` create/update, and
   `bankPayments` singular delete. Rule 3 now forbids using unauth 405 as
   the contract. `accountNatures` create/update left this freeze as ticketed
   offline tools. Remaining method-closed rows stay red until their official
   writable field map is implemented the same way.
2. **Partial method open only:** `transactions` POST/PUT return **401** but stay
   offline-blocked without live property-table and cleanup evidence.
   `transactions` DELETE and `invoiceReminderAssociations` DELETE of a missing
   id return **200** with `meta.success=true` (idempotent-delete narrative only).
3. Ambiguous bulk **92** remain empty-tool red.

Do not offline-green residual clear from Supports flags alone. Full probe body:
`.fractal/main.billy_complete/tmp/write-probes-research83.json`.

## Residual clear inventory honesty (research186)

The 29 residual clear Supports write rows that stay red after offline product waves carry machine-readable qualifications and empty `tool_name` values in the generated API inventory (see [[residual_clear_method_closed_inventory_honesty]]). This is inventory honesty only: it does not green rows, ship tools, or resolve bulk or annual_reports blockers.


Product-plane UI bulk: research187 honesty left 58 rows discovery_required; research188 dual bulk-chrome promoted 30 strong non-empty-shell rows to UI not_applicable (see [[ui_product_plane_bulk_chrome_dual_na_strong]]); 28 remain discovery_required (empty-shell + soft VAT/users). No bulk tools; API bulk 92 still external-contract red.

Related UI bulk inventory freezes: [[ui_product_plane_bulk_chrome_dual_na_soft_tool]], [[ui_product_plane_bulk_chrome_dual_na_strong]].

## research193 stop-churn (2026-08-02)

Docs lock re-check only (MD5 `8b94b0135c91fd15fe54ea33e088a4be`, ETag `wcw4x9hqvu3603`, body 147934). OpenAPI still 404. api-docs chunk still Supports-only for bulk. No unauth residual/bulk reconfirm package (STEER after research192).

There is still **no** further offline write product slice under fail-closed rules. Next real unlocks are external only:

1. Official bulk request/response/error schema (or OpenAPI), then offline bulk freeze + tools.
2. User expands scope to live non-production API qualification for residual/bulk authenticated probes.
3. Non-Upsedasse annual-reports shell for the sole remaining UI red row (see [[ui_annual_reports_inaccessible]]).

Do not treat citation-only reconfirm commits as product progress. Residual honesty: [[residual_clear_method_closed_inventory_honesty]].
