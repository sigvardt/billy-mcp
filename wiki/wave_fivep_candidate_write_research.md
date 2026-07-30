---
name: wave_fivep_candidate_write_research
title: Wave-5p candidate write research for organizations, users, sales-tax returns, and reminder associations
desc: Cited official-doc and unauth method-gate research for five inventoried write candidates; recommend or block only, not freeze or product acceptance.
tags: [billy, api, writes, research, organizations, users, sales-tax-returns, invoice-reminders]
sources:
  - https://www.billy.dk/api/
  - https://api.billysbilling.com/v2
  - wiki/offline_write_probe_rules.md
  - wiki/wave_fiveo_ticketed_writes_contract.md
  - wiki/wave_fivej_ticketed_writes_contract.md
  - coverage/api_v2_manifest.yaml
  - coverage/status.json
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
created: 2026-07-30T11:10:00Z
updated: 2026-07-30T11:12:00Z
---

# Wave-5p candidate write research for organizations, users, sales-tax returns, and reminder associations

## Authority and non-claims

This page is **wiki-only research**. Research is not a freeze acceptance, implementation, contract test, live test, UI/vision verification, or completeness claim. It is **not**:

- freeze acceptance
- product implementation or registration authority
- a contract test, live test, UI test, or vision verification
- a completeness claim or inventory green
- cleanup proof for any delete

Primary sources:

1. **Official-doc facts** from the public API page
   [https://www.billy.dk/api/](https://www.billy.dk/api/)
2. **Unauthenticated method-gate evidence** against the locked base
   `https://api.billysbilling.com/v2` (JSON object body `{}` on POST/PUT; no
   credentials; no organisation mutation)
3. **Unproven live/UI behaviour** is never asserted as proven here

Inventory rows in `coverage/api_v2_manifest.yaml` are inventory labels only.
They remain red unless a later accepted freeze and product path greens them
under project rules. All ambiguous bulk operations stay red and out of scope.

Existing probe notes in [[offline_write_probe_rules]] were treated as leads and
rechecked against primary evidence for this brief.

## Official access fingerprint

| Field | Value |
| --- | --- |
| URL | https://www.billy.dk/api/ |
| HTTP status | 200 |
| ETag | `wcw4x9hqvu3603` |
| Body bytes | 147934 |
| Body MD5 | `8b94b0135c91fd15fe54ea33e088a4be` |
| Locked API base | `https://api.billysbilling.com/v2` |

Inventory lock metadata still records older access tags ETag `hsisik4g9p3603`
and MD5 `c2efda0ee4cf9cf200e14910c5fc6996` with the same 147934-byte body size.
This brief treats that as access/CDN metadata drift only; Supports and property
tables for the five candidates below were parsed from the body fetched for this
research and match prior offline write-probe summaries for these resources.

Root honesty snapshot (read-only, not updated by this research):
`coverage/status.json` reports `complete: false`, 174 implemented and
contract-tested rows, 0 live-tested, 0 vision-verified, 92 ambiguous bulk rows.

## Method-gate interpretation rules used

From [[offline_write_probe_rules]] and reconfirmed here:

| Unauth result | Interpretation |
| --- | --- |
| POST/PUT **401** `AUTHENTICATION_REQUIRED` with object body | Method accepted at auth gate; compatible with offline ticketed-write freeze when Supports agrees |
| **405** `METHOD_NOT_ALLOWED` | Method closed offline; overrides Supports optimism for freeze tools |
| DELETE missing id **200** with meta-only body | Compatible with docs' idempotent-delete narrative; **not** cleanup proof; **not** live qualification; **not** a green or implemented contract by itself |
| Empty or missing POST/PUT body → 400 | Invalid probe; not used |

POST/PUT probes used body `{}`. No tokens, no browser, no production or test
organisation mutation.

## Probe matrix (reconfirmed)

Synthetic missing id: `zzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz`.

| Resource | Method | Path | HTTP | errorCode / notes |
| --- | --- | --- | --- | --- |
| organizations | POST | `/organizations` | 401 | `AUTHENTICATION_REQUIRED` |
| organizations | PUT | `/organizations/:id` | 401 | `AUTHENTICATION_REQUIRED` |
| organizations | DELETE | `/organizations/:id` | 405 | `METHOD_NOT_ALLOWED` — does not support deleting a single record |
| users | POST | `/users` | 405 | `METHOD_NOT_ALLOWED` — does not support creating records |
| users | PUT | `/users/:id` | 401 | `AUTHENTICATION_REQUIRED` |
| users | DELETE | `/users/:id` | 405 | `METHOD_NOT_ALLOWED` — does not support deleting a single record |
| salesTaxReturns | POST | `/salesTaxReturns` | 405 | `METHOD_NOT_ALLOWED` — does not support creating records |
| salesTaxReturns | PUT | `/salesTaxReturns/:id` | 401 | `AUTHENTICATION_REQUIRED` |
| salesTaxReturns | DELETE | `/salesTaxReturns/:id` | 405 | `METHOD_NOT_ALLOWED` — does not support deleting a single record |
| invoiceReminderAssociations | POST | `/invoiceReminderAssociations` | 405 | `METHOD_NOT_ALLOWED` — does not support creating records |
| invoiceReminderAssociations | PUT | `/invoiceReminderAssociations/:id` | 405 | `METHOD_NOT_ALLOWED` — does not support updating records |
| invoiceReminderAssociations | DELETE | `/invoiceReminderAssociations/:id` | 200 | meta-only success; top-level keys `meta` only; `meta.success=true`, `meta.statusCode=200`; `deletedRecords` absent |
| invoiceReminderAssociations | DELETE | `/invoiceReminderAssociations` (no ids) | 400 | `INVALID_DELETE_ID_ARRAY` — bulk shape hint only, not a bulk contract |

These results reconfirm the prior lead for all five inventoried operations. No
method-gate drift relative to [[offline_write_probe_rules]].

## Verdict summary

| Inventory id | Official method | Unauth gate | Verdict |
| --- | --- | --- | --- |
| `api.organizations.create` | POST `/v2/organizations` | 401 | **RECOMMEND** offline freeze candidate |
| `api.organizations.update` | PUT `/v2/organizations/:id` | 401 | **RECOMMEND** offline freeze candidate |
| `api.users.update` | PUT `/v2/users/:id` | 401 | **RECOMMEND** offline freeze candidate |
| `api.salesTaxReturns.update` | PUT `/v2/salesTaxReturns/:id` | 401 | **RECOMMEND** offline freeze candidate (narrow writable fields) |
| `api.invoiceReminderAssociations.delete` | DELETE `/v2/invoiceReminderAssociations/:id` | 200 meta-only | **BLOCK** for freeze/product until authenticated non-production cleanup proof |

Bulk save/delete rows for all four resources remain **blocked / out of scope**.

---

## Candidate: `api.organizations.create`

### Verdict

**RECOMMEND** as an offline ticketed-write freeze candidate (preview + execute).
This is research only: not freeze ACCEPT, not product, not live.

### Inventory and official endpoint

| Field | Value |
| --- | --- |
| Inventory id | `api.organizations.create` |
| Inventory tool name (preview) | `api_organizations_create_preview` |
| Official method / path | `POST /v2/organizations` (client path `POST /organizations`) |
| Supports (official) | get by id, list, **create**, **update**, bulk save, bulk delete |
| Singular request root | `organization` |
| Documented success shape (global write convention) | changed records under plural root(s); deletes only in `meta.deletedRecords` when present |
| Filters / pagination | N/A for create |
| Sensitivity | **high** (creates a company; includes subscription and fiscal identity fields) |
| Inventory errors listed | `AUTHENTICATION_REQUIRED`, `OAUTH_INVALID_ACCESS_TOKEN` |

### Documented request / response fields (official property table)

Request body shape is the global singular root `organization` (not invented
beyond inventory + conventions). Properties from the official table:

| Property | Type | Notes (official) |
| --- | --- | --- |
| ownerUser | belongs-to | required |
| createdTime | datetime | readonly |
| name | string | required |
| url | string | readonly |
| street | string | |
| zipcode | string | |
| city | string | |
| country | belongs-to | immutable, required |
| phone | string | |
| fax | string | |
| email | string | |
| registrationNo | string | |
| baseCurrency | belongs-to | immutable, required |
| logoFile | belongs-to | Organization logo |
| logoPdfFile | belongs-to | readonly |
| logoUrl | string | readonly |
| iconFile | belongs-to | Organization icon |
| iconUrl / icon48Url | string | readonly |
| fiscalYearEndMonth | integer | required |
| firstFiscalYearStart | date | required |
| firstFiscalYearEnd | date | required |
| hasBillVoucherNo | boolean | |
| subscriptionCardType | string | **sensitive** |
| subscriptionCardNumber | string | **sensitive** |
| subscriptionCardExpires | date | **sensitive** |
| subscriptionTransaction | belongs-to | |
| isSubscriptionBankPayer | boolean | |
| subscriptionPrice | float | |
| subscriptionPeriod | enum | required, default `"monthly"` |
| subscriptionDiscount | float | readonly |
| subscriptionExpires | date | |
| isTrial | boolean | readonly |
| isTerminated | boolean | |
| terminationTime | datetime | readonly |
| locale | belongs-to | required |
| billEmailAddress | string | readonly |
| isUnmigrated / isLocked / lockedCode / lockedReason / appUrl | various | readonly |
| emailAttachmentDeliveryMode | enum | required |
| hasVat | boolean | |
| vatPeriod | enum | required |
| defaultInvoiceBankAccount | belongs-to | |
| invoiceNoMode | enum | required |
| nextInvoiceNo | integer | required |
| paymentTermsMode | enum | required |
| paymentTermsDays | integer | required |
| defaultTaxMode | enum | |
| defaultSalesAccount | belongs-to | |
| defaultSalesTaxRuleset | belongs-to | |
| bankSyncStartDate | date | |
| defaultBankFeeAccount | belongs-to | |
| defaultBillBankAccount | belongs-to | |

Belongs-to encodings (Id suffix vs embed) are **not invented** here. Freeze
authors must follow the shared ticketed-write protocol used by prior accepted
waves and keep the inner `organization` map opaque unless a freeze page locks
scalars.

### Method-gate result

Unauth `POST /organizations` with `{}` → **401** `AUTHENTICATION_REQUIRED`.
Method is open at the auth gate. Compatible with offline freeze when Supports
create is respected.

### Cleanup limitations

Singular DELETE is **405**. There is **no** offline singular-delete cleanup
path for organizations. Inventory cleanup text that assumes delete of a
dedicated test resource is **unproven and contradicted offline**. Live
qualification (later, with credentials) must design non-delete cleanup or
accept permanent test orgs.

### Exact future tool shape (only if freeze is later accepted)

| Inventory id | Preview | Execute | Method and client path | Request | Required success root |
| --- | --- | --- | --- | --- | --- |
| `api.organizations.create` | `api_organizations_create_preview` | `api_organizations_create_execute` | `POST /organizations` | singular `organization` map | `organizations` when returned |

Ticketed confirmation protocol: same as other accepted write freezes
(preview issues confirmation ticket; execute consumes it). No bulk tools.

### Exclusions

- No singular delete tool (405)
- No bulk save/delete tools
- No live, UI, or vision claims
- No invented required-field validation beyond official Notes
- No subscription-card handling claims beyond field names on the docs table
- Not freeze ACCEPT or product

---

## Candidate: `api.organizations.update`

### Verdict

**RECOMMEND** as an offline ticketed-write freeze candidate (preview + execute).

### Inventory and official endpoint

| Field | Value |
| --- | --- |
| Inventory id | `api.organizations.update` |
| Inventory tool name (preview) | `api_organizations_update_preview` |
| Official method / path | `PUT /v2/organizations/:id` |
| Supports | update among singular writes (see create section) |
| Request roots | path/id binding + singular `organization` partial body |
| Filters / pagination | N/A |
| Sensitivity | **high** (company identity, fiscal, subscription fields) |

### Documented fields

Same property table as create. PUT is partial update per global API
conventions. Readonly and immutable Notes still apply. Do not invent which
subset is mutable live; offline freeze may keep `organization` opaque with id
required.

### Method-gate result

Unauth `PUT /organizations/:id` with `{}` → **401** `AUTHENTICATION_REQUIRED`.
Open at auth gate.

### Cleanup limitations

No singular DELETE (405). Update-restore cleanup is **unproven** without live
non-production evidence. Inventory "restore prior test state" is aspirational
only.

### Exact future tool shape (if freeze later accepted)

| Inventory id | Preview | Execute | Method and client path | Request | Required success root |
| --- | --- | --- | --- | --- | --- |
| `api.organizations.update` | `api_organizations_update_preview` | `api_organizations_update_execute` | `PUT /organizations/:id` | `id` + `organization` | `organizations` when returned |

### Exclusions

Same as create regarding bulk, delete, live/UI/vision, freeze/product
acceptance.

---

## Candidate: `api.users.update`

### Verdict

**RECOMMEND** as an offline ticketed-write freeze candidate (preview + execute).

### Inventory and official endpoint

| Field | Value |
| --- | --- |
| Inventory id | `api.users.update` |
| Inventory tool name (preview) | `api_users_update_preview` |
| Official method / path | `PUT /v2/users/:id` |
| Supports (official) | get by id, list, **update**, bulk save, bulk delete (**no create**) |
| Request roots | `id` + singular `user` |
| Filters / pagination | N/A for update |
| Sensitivity | **high** (PII; staff/admin privilege flags) |

### Documented request / response fields

| Property | Type | Notes (official) |
| --- | --- | --- |
| createdTime | datetime | readonly |
| name | string | required |
| email | string | required |
| phone | string | |
| profilePicFile | belongs-to | readonly |
| profilePicUrl / profilePic48Url | string | readonly |
| isStaff | boolean | staff membership flag |
| isSupporter | boolean | supporter flag |
| isAdmin | boolean | admin flag |
| isSupportAccessAllowed | boolean | user choice for supporter access |

Global write response convention applies (`users` plural when returned). No
list filters for this write.

### Method-gate result

| Method | Result |
| --- | --- |
| POST `/users` | **405** — does not support creating records (Supports omits create; matches) |
| PUT `/users/:id` | **401** `AUTHENTICATION_REQUIRED` |
| DELETE `/users/:id` | **405** — does not support deleting a single record |

Update is open at auth; create/delete closed.

### Cleanup limitations

No singular delete. Restore-prior-state cleanup is unproven live. Privilege
flags must not be flipped in production without explicit operator intent
(product concern for a later leaf; not proven here).

### Exact future tool shape (if freeze later accepted)

| Inventory id | Preview | Execute | Method and client path | Request | Required success root |
| --- | --- | --- | --- | --- | --- |
| `api.users.update` | `api_users_update_preview` | `api_users_update_execute` | `PUT /users/:id` | `id` + `user` | `users` when returned |

### Exclusions

- No create or delete tools (405 / Supports)
- No bulk tools
- No live/UI/vision
- No invented password, invite, or auth-user special routes (`GET /v2/user` and
  `GET /v2/user/organizations` are separate specials, not this inventory row)

---

## Candidate: `api.salesTaxReturns.update`

### Verdict

**RECOMMEND** as an offline ticketed-write freeze candidate (preview + execute),
with a **narrow documented writable surface**. Most properties are readonly;
do not invent create or full mutable schemas.

### Inventory and official endpoint

| Field | Value |
| --- | --- |
| Inventory id | `api.salesTaxReturns.update` |
| Inventory tool name (preview) | `api_sales_tax_returns_update_preview` |
| Official method / path | `PUT /v2/salesTaxReturns/:id` |
| Supports (official) | get by id, list, **update**, bulk save, bulk delete (**no create**) |
| Request roots | `id` + singular `salesTaxReturn` |
| Filters / pagination | N/A for update |
| Sensitivity | **medium-high** (VAT return settlement state) |

### Documented request / response fields

| Property | Type | Notes (official) | Offline write posture |
| --- | --- | --- | --- |
| organization | belongs-to | readonly | not client-writable |
| createdTime | datetime | readonly | not client-writable |
| periodType | enum | readonly | not client-writable |
| period | string | readonly | not client-writable |
| periodText | string | (no readonly note) | candidate writable |
| correctionNo | integer | readonly | not client-writable |
| startDate | date | readonly | not client-writable |
| endDate | date | readonly | not client-writable |
| reportDeadline | date | (no readonly note) | candidate writable |
| isSettled | boolean | (no readonly note) | candidate writable |
| isPaid | boolean | readonly | not client-writable |

Which of the three candidate-writable fields succeed live is **unproven**. An
offline freeze should keep the inner map opaque and must not invent additional
fields. Unlike fully readonly resources such as `postings` (all properties
readonly and method-closed or frozen-out), this resource still documents
update Support and shows non-readonly columns, and the unauth PUT gate is 401.

### Method-gate result

| Method | Result |
| --- | --- |
| POST | **405** create closed (Supports omits create) |
| PUT | **401** open at auth |
| DELETE | **405** singular delete closed |

### Cleanup limitations

No singular DELETE. Settling a tax return may be effectively one-way live;
restore cleanup is **unproven**. Do not claim reversible updates.

### Exact future tool shape (if freeze later accepted)

| Inventory id | Preview | Execute | Method and client path | Request | Required success root |
| --- | --- | --- | --- | --- | --- |
| `api.salesTaxReturns.update` | `api_sales_tax_returns_update_preview` | `api_sales_tax_returns_update_execute` | `PUT /salesTaxReturns/:id` | `id` + `salesTaxReturn` | `salesTaxReturns` when returned |

### Exclusions

- No create/delete tools
- No bulk tools
- No claim that every property is updatable
- No live settlement or payment-state qualification
- Not freeze ACCEPT or product

---

## Candidate: `api.invoiceReminderAssociations.delete`

### Verdict

**BLOCK** for freeze page authoring and Codex Power product implementation.

**Blocker:** Unauthenticated singular DELETE returns **200 meta-only** with no
`deletedRecords` and no resource payload. That is compatible with an
idempotent-delete narrative and proves the method is **not 405-closed**, but it
is **not cleanup proof**, not a green contract, and not sufficient evidence of
successful association removal on a real record. Official Supports also list
create and update for this resource, yet unauth POST/PUT return **405**, so
Supports alone is not trustworthy for this collection without method-gate
confirmation. Until authenticated non-production delete of a disposable real
association proves cleanup (or an official docs change plus project freeze
review explicitly accepts a meta-only offline delete with hard exclusions),
this inventory row stays unavailable to implementation.

### Inventory and official endpoint

| Field | Value |
| --- | --- |
| Inventory id | `api.invoiceReminderAssociations.delete` |
| Inventory tool name (preview) | `api_invoice_reminder_associations_delete_preview` |
| Official method / path | `DELETE /v2/invoiceReminderAssociations/:id` |
| Supports (official) | get by id, list, create, update, bulk save, **delete**, bulk delete |
| Request fields (inventory) | `id` only |
| Documented association properties | `reminder` belongs-to required; `invoice` belongs-to required; `lateFee` belongs-to readonly |
| Filters / pagination | N/A for singular delete |
| Sensitivity | medium (links reminders to invoices; lateFee readonly) |

### Documented fields vs method reality

| Official Supports claim | Unauth method gate | Offline posture |
| --- | --- | --- |
| create | POST **405** | **blocked** (overrides Supports) |
| update | PUT **405** | **blocked** (overrides Supports) |
| delete | DELETE missing-id **200** meta-only | method not closed; **cleanup unproven** → **block product/freeze** |
| bulk save/delete | not probed as green path; collection DELETE without ids → 400 `INVALID_DELETE_ID_ARRAY` citing `ids[]` | bulk remains red / out of scope |

Property table fields `reminder` / `invoice` / `lateFee` describe the resource
shape for reads and for any future create path; they are **not** a create
contract for offline freeze while POST is 405.

### Method-gate result (detail)

- `DELETE /invoiceReminderAssociations/{synthetic-id}` → HTTP **200**, body
  top-level keys only `meta`, `meta.success=true`, `meta.statusCode=200`,
  `deletedRecords` absent.
- This matches the prior lead and [[offline_write_probe_rules]] wording for
  this resource: do not offline-green create/update; treat 200 meta-only delete
  as non-cleanup.
- Contrast: Wave-5j offline-froze some bank-line association deletes with
  explicit "optional deleted metadata only when present" and no cleanup proof.
  This research **does not** extend that freeze acceptance to reminder
  associations without a separate freeze review after stronger evidence,
  because Supports create/update are already contradicted by 405 on this same
  resource.

### Cleanup limitations

- Missing-id 200 is **not** proof a real association was removed.
- Inventory cleanup "not_recoverable; use disposable test data" remains
  aspirational until live non-production evidence exists.
- No create tool is available offline to mint disposable associations (POST
  405), so even a ticketed delete product would lack an offline create path to
  manufacture cleanup subjects.

### Exact future tool shape

**None provided.** Freeze is not defensible for Codex Power from this evidence
alone. If a later authenticated non-production probe proves singular delete of a
real association and independent freeze review accepts it, a possible shape
would mirror other bodyless deletes:

| Inventory id | Preview | Execute | Method | Request |
| --- | --- | --- | --- | --- |
| `api.invoiceReminderAssociations.delete` | (not authorised by this research) | (not authorised) | `DELETE /invoiceReminderAssociations/:id` | id only |

That table is **illustrative of inventory naming only**, not a freeze.

### Exclusions

- No create/update tools (405)
- No bulk tools (ambiguous; 400 without ids is not a bulk contract)
- No cleanup, green, live, UI, vision, or completeness claim
- No Codex Power implementation until the blocker is cleared

---

## Cross-cutting exclusions

- All **92** ambiguous bulk operations remain red and out of scope.
- No webhooks are documented on the official page (0 webhooks in inventory
  seed).
- No browser, UI, or vision work.
- No credentials used; no production or test-organisation mutation performed.
- Raw HTTP frames, headers, and bodies stay in owner-only scratch and are not
  committed.
- Research does not author freeze pages, product modules, tests, or coverage
  edits.

## Recommended next steps (for parent / other leaves; not this leaf)

1. Independent review of this research page (optional parent gate).
2. If parent selects recommended rows: separate wiki freeze contract leaf for
   organizations create/update, users update, and/or salesTaxReturns update
   only, then freeze independent review ACCEPT, then Codex Power product.
3. Keep `api.invoiceReminderAssociations.delete` red until authenticated
   non-production cleanup evidence exists.
4. Never green bulk rows from Supports text alone.

## Evidence classification legend

| Label | Meaning |
| --- | --- |
| Official-doc fact | Parsed from https://www.billy.dk/api/ body for this research |
| Unauth gate | Observed HTTP status/errorCode without credentials |
| Unproven | Live mutation, UI, cleanup success, bulk body, or completeness |
