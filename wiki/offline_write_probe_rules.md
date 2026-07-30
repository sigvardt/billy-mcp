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
updated: 2026-07-30T08:18:00Z
---

# Offline write probe rules from official docs and unauth API gates

## Authority

Derived from Billy's public API docs at https://www.billy.dk/api/ (ETag
`hsisik4g9p3603`, MD5 `c2efda0ee4cf9cf200e14910c5fc6996`, body 147934 bytes as
of 2026-07-29) and unauthenticated probes against the locked base
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

Probe refresh: 2026-07-30T08:15:26Z (research59), docs ETag `hsisik4g9p3603`, MD5
`c2efda0ee4cf9cf200e14910c5fc6996` (byte-identical body 147934). Scratch
detail: `.fractal/main.billy_complete/tmp/write-probes-research59.json` (+
bulk-hint; prior research58 / 57 / 56 / 55 / 54 / 47 / 46 / 44 / 43 / 40). No
drift on bankPayments or salesTaxPayments POST/PUT 401 or singular DELETE 405.
contactBalancePayments / invoiceLateFees POST/PUT 401 and singular DELETE 405
reconfirmed. invoiceLateFees and invoiceReminders bulk DELETE with `ids[]`
return **405** (Supports bulk delete overridden offline). invoiceReminders POST
401 PUT/DELETE 405 reconfirmed. invoiceReminderAssociations create/update 405
reconfirmed.

## Next freezes (planning only)

- Wave-5g through Wave-5l offline products remain on root for create+update
  where accepted. Live/UI/vision/bulk and overall completeness remain fail-closed.
- Wave-5l freeze is accepted offline
  (`wiki/wave_fivel_ticketed_writes_contract.md`,
  `wiki/wave_fivel_freeze_independent_review.md`). Product is merged on root
  (`sales_tax_payment_writes.py`) with its Codex fallback product review record
  retained; no Wave-5l review decision changes in this evidence refresh.
- Wave-5m freeze for singular `contactBalancePayments` **create + update only**
  is **ACCEPT** offline (`wiki/wave_fivem_ticketed_writes_contract.md` MD5
  `fcb0e58742c8abc8ca9078859bb74eb8`;
  `wiki/wave_fivem_freeze_independent_review.md`). Product is on root
  (`contact_balance_payment_writes.py`); offline product **ACCEPT** at
  `wiki/wave_fivem_product_independent_review.md` (root 250 tools / 172 offline).
- Wave-5n freeze-ready research for `invoiceLateFees` create+update is in
  `.fractal/main.billy_complete/tmp/grok-research.md` (research59). Freeze page
  authoring is open after Wave-5m product ACCEPT; product for late fees still
  requires a separate freeze ACCEPT first.
- After Wave-5n: `invoiceReminders` create only (PUT/DELETE 405). Keep
  `contactBalancePostings` and `invoiceReminderAssociations` create/update
  offline-blocked (405).
