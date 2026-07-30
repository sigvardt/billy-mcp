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
updated: 2026-07-30T18:26:00Z
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
   exists. Supports bulk mentions alone are not enough.
5. API traffic stays on `https://api.billysbilling.com/v2`. The docs' file-upload
   sample host `api.billy.dk` must never become the client base; host-lock tests
   should still deny it.

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

Probe refresh: 2026-07-30T18:24:29Z (research83 residual clear full matrix +
email/delivery specials; prior research82/81/64/63/61). HTTP docs ETag
`wcw4x9hqvu3603`, MD5 `8b94b0135c91fd15fe54ea33e088a4be`, body 147934 still
byte-identical. POST/PUT probes must send a JSON object body (`{}` minimum); a
missing body or `Content-Type: application/json` with empty/non-object body
yields **400** `INVALID_REQUEST_BODY` before auth and is not a method-closed
signal. Empty bytes without Content-Type may still reach **401** — product
always sends a JSON object. Scratch:
`.fractal/main.billy_complete/tmp/write-probes-research83.json`.

## Planning note

Wave-5g through Wave-5r offline products and Wave-5s-A invoiceLogs plus
Wave-5s-B files upload are on root (182 offline contract-tested rows). Live,
UI, vision, bulk, and overall completeness remain fail-closed. Wave-5s-C
invoice email + invoiceDeliveries is the next offline product slice. Keep
`contactBalancePostings` and `invoiceReminderAssociations` create/update
offline-blocked (405). Keep `transactions` CUD offline-blocked without live
property samples. Detail: [[wave_fives_residual_specials_research]].

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
