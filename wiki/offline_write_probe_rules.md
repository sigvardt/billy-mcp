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
updated: 2026-07-30T01:08:00Z
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
| `invoiceLateFees` | POST/PUT 401; DELETE **405** (Supports omits singular delete) |
| `invoiceReminders` | POST 401; PUT/DELETE **405** (Supports: create only among singular writes) |
| `invoiceReminderAssociations` | POST/PUT **405**; DELETE missing-id 200 — do not offline-green create/update |
| `organizations` | POST/PUT 401; DELETE **405** |
| `users` | POST/DELETE **405**; PUT 401 (Supports: update, no create) |
| `files` | POST 401; PUT/DELETE **405**; property table all readonly — JSON create is not the binary upload special |
| `bankLineMatches`, `bankLines`, `bankLineSubjectAssociations` | POST/PUT 401; DELETE missing-id 200 — full singular CUD probe-open; property tables extracted (research40); match has-many `lines`/`subjectAssociations` document replace-on-set while Notes say readonly — live must prove embed; offline freeze may use opaque inners |

Probe refresh: 2026-07-30T00:52:57Z, docs ETag `hsisik4g9p3603`, MD5
`c2efda0ee4cf9cf200e14910c5fc6996`. Scratch detail:
`.fractal/main.billy_complete/tmp/write-probes-research40.json` (compact:
`write-probes-research40-compact.json`; prior: research37 / research34-compact).

## Next freezes (planning only)

- Wave-5g product (`salesTaxRulesets` + `salesTaxRules`) is accepted as an
  offline product slice at root `55faa02` by
  `wiki/wave_fiveg_product_independent_review.md`; live/UI/vision/bulk and
  overall completeness remain fail-closed.
- Wave-5h attachment singular JSON CUD freeze and product remain accepted
  offline (`wiki/wave_fiveh_ticketed_writes_contract.md`,
  `wiki/wave_fiveh_product_independent_review.md` at `29cecbe`).
- Wave-5i sales-tax account and meta-field product is accepted offline at root
  merge `084ad77` by `wiki/wave_fivei_product_independent_review.md` (220 tools
  / 157 offline rows). Live/UI/vision/bulk and overall completeness remain
  fail-closed.
- Recommended next offline freeze: Wave-5j singular `bankLineMatches` +
  `bankLines` + `bankLineSubjectAssociations` CUD (9 clear ops / 18 tools).
  Freeze-ready research is accepted as a drafting handoff only by
  `wiki/wave_fivej_freeze_ready_research_independent_review.md`. Cited brief:
  `.fractal/main.billy_complete/tmp/grok-research.md` (research40). Freeze page
  and product do not yet exist. Exclude `bankPayments` singular delete (405)
  and all bulk rows.
