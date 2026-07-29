---
name: wave_one_reads_contract
desc: Frozen official contract for the first Billy API read-only implementation wave.
sources:
  - https://www.billy.dk/api/
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
created: 2026-07-29T09:56:00Z
updated: 2026-07-29T09:56:00Z
---

# wave_one_reads_contract

This is the implementation boundary for the first API read-only wave. The
official evidence is preserved in the current Grok contract brief; this page
records only the stable shared rules needed by implementation workers.

## Shared transport and status rules

- Use `https://api.billysbilling.com/v2` and `X-Access-Token` only. Tool paths
  are relative (`/products`), never `/v2/products`; the alias host is denied.
- Every tool has Pydantic input and success models and returns a typed
  `ToolError` on failure. There are no generic HTTP controls or placeholder
  registrations.
- Lists accept only documented `page`, `pageSize` (1–1000), optional `include`,
  `sortProperty`, and `sortDirection` (`ASC` or `DESC`). Do not invent filters
  or offset paging.
- Each tool needs request-construction, root-response mapping, paging, and
  authentication-error fixture tests. `live_tested` remains false without the
  dedicated non-production organisation and token.

## Owned read tools

| Area | Tools |
| --- | --- |
| Bootstrap | `api_user_get`, `api_user_list_organizations`, `api_organizations_get`, `api_organizations_list` |
| Reference data | `api_currencies_get/list`, `api_countries_get/list`, `api_locales_get/list` |
| Catalogue | `api_products_get/list`, `api_product_prices_get/list` |
| Contacts | `api_contacts_get/list` |

Singular reads map the documented singular root key; list reads map the plural
root and optional `meta.paging`. Organisation subscription-card fields must be
redacted. Writes, bulk operations, files upload, invoice special routes,
contact-persons, UI workflows, browser auth, and the ambiguous singular
`/organization` sample are outside this wave.

## Registration boundary

Each implemented area module exposes only its real typed registration function.
Root `server.py` wires a module only after the module and its contract tests are
merged. No module may update coverage, modify shared server wiring, or claim a
live result before root integration verifies the merged tools.
