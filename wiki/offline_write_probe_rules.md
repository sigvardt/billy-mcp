---
name: offline_write_probe_rules
title: Offline write probe rules from official docs and unauth API gates
desc: Durable rules for when Supports flags may not open offline ticketed-write freezes.
tags: [billy, api, writes, probes]
sources:
  - https://www.billy.dk/api/
  - https://api.billysbilling.com/v2
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
created: 2026-07-29T21:20:00Z
updated: 2026-08-02T14:20:00Z
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
3. Unauthenticated **405** (`METHOD_NOT_ALLOWED`) **overrides** Supports-flag
   optimism for offline green paths. Do not ship ticketed tools for that method
   until authenticated non-production evidence or an official docs change
   proves the method.
4. Bulk save/delete remain empty-tool red until a request/response body contract
   exists. Supports bulk mentions alone are not enough. After research137 docs/asset exhaust, treat bulk as **external-contract blocked** (see below), not as
   an open evidence loop.
5. API traffic stays on `https://api.billysbilling.com/v2`. The docs' file-upload
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
| `invoiceReminderAssociations` | POST/PUT **405**; DELETE missing-id 200 — do not offline-green create/update; collection DELETE without ids → **400** `INVALID_DELETE_ID_ARRAY` citing `ids[]` query form (bulk shape hint only) |
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

Wave-5g through Wave-5s-C offline products are on root (**184** offline
contract-tested rows). All six specials are offline-producted; live remains
false. Residual clear **29**, bulk **92**, UI, vision, and completeness stay
fail-closed. There is no further offline write product slice. Next work is
Wave-5t live residual/bulk gate harness (token required for product progress).
Keep residual 405 false friends and `transactions` CUD offline-blocked without
live samples. Detail: [[wave_fives_residual_specials_research]].

## Wave-5s residual clear (research83)

After specials product (files upload + invoice email + invoiceDeliveries), the
remaining clear not-impl set is **29** rows. Unauth probes against
`https://api.billysbilling.com/v2` (no token, no persistent records) show:

1. **405 false friends (majority):** `accountNatures`, `balanceModifiers`,
   geo/reference create/update (`cities`, `countries`, `currencies`, `states`,
   `zipcodes`, `locales`, `countryGroups`), `contactBalancePostings`,
   `postings`, `invoiceReminderAssociations` create/update, and
   `bankPayments` singular delete. Supports create/update optimism is overridden
   offline by rule 3.
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
