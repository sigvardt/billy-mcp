---
name: billy-api-v2-research-seed
desc: Official Billy API v2 inventory seed from docs review (2026-07-29). Not a completeness claim.
tags: [billy, api, research]
sources:
  - https://www.billy.dk/api/
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
created: 2026-07-29T08:12:00Z
updated: 2026-07-29T08:23:38Z
---

# billy-api-v2-research-seed

Primary source: https://www.billy.dk/api/ (accessed 2026-07-29).  
Base URL lock: `https://api.billysbilling.com/v2`. Auth header: `X-Access-Token`.

## Counts

| Metric | Count |
| --- | ---: |
| Resources in official TOC | 46 |
| Supports flags | 299 |
| Clear get/list/create/update/delete ops | 207 |
| Bulk save + bulk delete flags | 92 (contract incomplete on current docs) |
| Documented webhooks | 0 |

## Global conventions

- GET one `/v2/{plural}/:id` → singular object
- GET list `/v2/{plural}` → plural array + optional `meta.paging`
- POST create, PUT partial update, DELETE one (idempotent)
- Write responses return all changed records; deletes in `meta.deletedRecords`
- Paging (current official docs): `page`/`pageSize` only, max pageSize 1000 (default 1000). Historical docs also mention `offset`/`pageSize` — treat offset as unproven until live check
- Include: `include=resource.property:sideload|embed`
- Sort: `sortProperty`, `sortDirection` ASC|DESC
- Locales via `Accept-Language`: en_US, da_DK, fr_FR, nl_NL, de_DE
- Documented list filters only for invoices, bills, daybookTransactions

## Special routes outside resource Supports matrix

- `POST /v2/files` multipart with X-Filename and optional x-create-attachment / x-create-variants / x-organizationid / x-should-scan
- `POST /v2/invoices/:invoiceId/emails`
- `POST /v2/invoiceDeliveries` (async e-invoice; poll invoiceLogs)
- `GET /v2/invoiceLogs`
- `GET /v2/user`
- `GET /v2/user/organizations`
- Samples also use `GET /organization` (path ambiguous vs organizations resource)

## Bulk ambiguity

Every resource Supports line lists bulk save and bulk delete. Current official conventions section does not document PATCH bulk body or DELETE `ids[]` query form (older public gists do). Keep all 92 bulk rows red until live non-production verification.

## Error envelope (unauthenticated)

```json
{
  "meta": { "statusCode": 401, "success": false },
  "errorMessage": "…",
  "errorCode": "AUTHENTICATION_REQUIRED",
  "errorTime": "…",
  "helpUrl": "https://www.billy.dk/support/"
}
```

## UI note

Interface inventory still depends on dedicated non-production org headless discovery. Design lists route families under invoices, quotes, recurring, products, customers, purchases, bank, daybooks, reports, VAT, exports, inventory, settings. Quotes/recurring/inventory appear UI-first relative to the official API TOC.

## Implementation order seed

1. Freeze red `coverage/api_v2_manifest.yaml` and UI manifest
2. Shared FastMCP foundation, locked HTTP client, tickets, headless browser shell
3. Read-only API tools: user/org → reference data → contacts/products → invoices/bills/daybooks
4. Writes with preview/execute after reads are green
5. Bulk and irreversible specials only after live contract proof

No row is complete until discovered, implemented, contract_tested, and live_tested (UI also vision_verified).
