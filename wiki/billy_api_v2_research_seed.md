---
name: billy_api_v2_research_seed
desc: Official Billy API v2 inventory seed from docs review (2026-07-29). Not a completeness claim.
tags: [billy, api, research]
sources:
  - https://www.billy.dk/api/
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
created: 2026-07-29T08:12:00Z
updated: 2026-07-29T09:22:00Z
---

# billy_api_v2_research_seed

Primary source: https://www.billy.dk/api/ (re-verified 2026-07-29T09:20Z; etag `hsisik4g9p3603`, 147934 bytes, MD5 `c2efda0ee4cf9cf200e14910c5fc6996` — unchanged).
Base URL lock: `https://api.billysbilling.com/v2`. Auth header: `X-Access-Token`.  
Detailed freeze recipe / next-slice contract: node scratch `.fractal/main.billy_complete/tmp/grok-research.md` (not a completeness claim).

## Counts

| Metric | Count |
| --- | ---: |
| Resources in official TOC | 46 |
| Supports flags | 299 |
| Clear get/list/create/update/delete ops | 207 |
| Bulk save + bulk delete flags | 92 (contract incomplete on current docs) |
| Documented webhooks | 0 |

## Non-resources

- HTML noise includes Prismic CMS `…/api/v2/documents/search` and prose about "supporting documents". That is **not** a Billy API resource. Official Supports TOC has no `/v2/documents`.

## Global conventions

- GET one `/v2/{plural}/:id` → singular object
- GET list `/v2/{plural}` → plural array + optional `meta.paging`
- POST create, PUT partial update, DELETE one (idempotent)
- Write responses return all changed records; deletes in `meta.deletedRecords`
- Paging (current official docs): `page`/`pageSize` only, max pageSize 1000 (default 1000). Word “offset” on the page is bank-fee prose only; historical gists mention offset paging — treat as unproven until live check
- Include: `include=resource.property:sideload|embed`
- Sort: `sortProperty`, `sortDirection` ASC|DESC
- Locales via `Accept-Language`: en_US, da_DK, fr_FR, nl_NL, de_DE
- Documented list filters only for invoices, bills, daybookTransactions
- Deny runtime host `api.billy.dk` (sample noise); lock client to `api.billysbilling.com`

## Special routes outside resource Supports matrix

- `POST /v2/files` multipart with X-Filename and optional x-create-attachment / x-create-variants / x-organizationid / x-should-scan (this is the only documented create path; do not also invent a JSON `{file:…}` create tool)
- `POST /v2/invoices/:invoiceId/emails`
- `POST /v2/invoiceDeliveries` (async e-invoice; poll invoiceLogs)
- `GET /v2/invoiceLogs`
- `GET /v2/user`
- `GET /v2/user/organizations`
- Samples also use `GET /v2/organization` (singular) against base `…/v2` — ambiguous vs `/v2/organizations` resource; live-verify before claiming

## Bulk ambiguity

Every resource Supports line lists bulk save and bulk delete. Current official conventions section does not document PATCH bulk body or DELETE `ids[]` query form (older public gists do). OPTIONS CORS allow-methods include PATCH; that is not a bulk body contract. Keep all 92 bulk rows red until live non-production verification.

## Error envelope (live unauthenticated probes)

Missing auth (`GET /v2/user` with no token):

```json
{
  "meta": { "statusCode": 401, "success": false },
  "errorMessage": "You must use Basic auth or an OAuth access token to make requests to the API.",
  "errorCode": "AUTHENTICATION_REQUIRED",
  "errorTime": "…",
  "helpUrl": "https://www.billy.dk/support/"
}
```

Invalid `X-Access-Token` value:

```json
{
  "meta": { "statusCode": 401, "success": false },
  "errorMessage": "Invalid OAuth 2 access token.",
  "errorCode": "OAUTH_INVALID_ACCESS_TOKEN",
  "helpUrl": "https://www.billy.dk/support/"
}
```

Map both to MCP `AUTH_REQUIRED` until a distinct expiry shape is proven. No full error catalogue on the official page.

## UI note

Interface inventory still depends on dedicated non-production org headless discovery. Design lists route families under invoices, quotes, recurring, products, customers, purchases, bank, daybooks, reports, VAT, exports, inventory, settings. Quotes/recurring/inventory appear UI-first relative to the official API TOC (`quoteId` / `recurringInvoiceId` exist as invoice filters only).

## Implementation order seed

1. Freeze red `coverage/api_v2_manifest.yaml` and UI manifest
2. Shared FastMCP foundation, locked HTTP client, tickets, headless browser shell
3. Wave-1 reads (next): `api_user_*`, `api_organizations_*` get/list, currencies/countries/locales get/list, products and productPrices get/list, contacts get/list
4. Later reads: invoices/bills/daybooks and remaining clear get/list
5. Writes with preview/execute after reads are green
6. Bulk and irreversible specials only after live contract proof

No row is complete until discovered, implemented, contract_tested, and live_tested (UI also vision_verified).
