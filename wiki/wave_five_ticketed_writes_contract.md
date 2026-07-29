---
name: wave_five_ticketed_writes_contract
desc: Frozen contract for the first offline ticketed Billy create, update, and delete tool cohort.
tags: [billy, api, writes, confirmation]
sources:
  - https://www.billy.dk/api/
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
  - coverage/api_v2_manifest.yaml
  - .fractal/main.billy_complete/tmp/grok-research.md
created: 2026-07-29T13:20:00Z
updated: 2026-07-29T13:20:00Z
---

# wave_five_ticketed_writes_contract

This is the frozen implementation contract for the first offline ticketed
write cohort. It implements neither live qualification nor product
completeness. The underlying official documentation fingerprint is ETag
`hsisik4g9p3603`, MD5 `c2efda0ee4cf9cf200e14910c5fc6996`.

## Scope

| Inventory IDs | Route | Request root | Success roots | Preview / execute tool stems |
| --- | --- | --- | --- | --- |
| `api.products.create`, `.update`, `.delete` | `/v2/products` | `product` | changed product records; `meta.deletedRecords` | `api_products_{create,update,delete}_{preview,execute}` |
| `api.productPrices.create`, `.update`, `.delete` | `/v2/productPrices` | `productPrice` | changed product-price records; `meta.deletedRecords` | `api_product_prices_{create,update,delete}_{preview,execute}` |
| `api.contacts.create`, `.update`, `.delete` | `/v2/contacts` | `contact` | changed contact records; `meta.deletedRecords` | `api_contacts_{create,update,delete}_{preview,execute}` |
| `api.contactPersons.create`, `.update`, `.delete` | `/v2/contactPersons` | `contactPerson` | changed contact-person records; `meta.deletedRecords` | `api_contact_persons_{create,update,delete}_{preview,execute}` |
| `api.daybooks.create`, `.update`, `.delete` | `/v2/daybooks` | `daybook` | changed daybook records; `meta.deletedRecords` | `api_daybooks_{create,update,delete}_{preview,execute}` |

Each table row represents three inventory operations and six callable tools:
POST create preview/execute, PUT update preview/execute, and singular DELETE
preview/execute. The fifteen inventory `tool_name` values remain the preview
names; the paired execute tools are required registrations, not new inventory
rows.

## HTTP contract

- Create is `POST /v2/{collection}` with `{singularRoot: object}`.
- Update is `PUT /v2/{collection}/{id}` with `{singularRoot: object}`.
- Delete is `DELETE /v2/{collection}/{id}` with no request body.
- IDs are validated non-empty and percent-encoded as one path segment.
- A successful response is mapped only from documented changed-record roots and
  optional `meta.deletedRecords`; omit an absent optional metadata root rather
  than fabricating it.
- The request is sent only through the locked Billy client. Writes have no
  automatic retry. Missing credentials and Billy 401 envelopes map to
  `AUTH_REQUIRED`; 404 maps to `NOT_FOUND`.
- Request root objects are typed Pydantic fields with `extra="forbid"` on every
  outer input and result model. Do not expose generic JSON request, generic HTTP,
  arbitrary URL, or generic browser tools.

Official property tables establish these dependency-sensitive fields for later
live qualification: products need their organisation/name/account context;
product prices need product, unit price, and currency; contacts need country;
contact persons need contact plus name or email; and daybooks need name plus
`isTransactionSummaryEnabled`. The offline slice must not invent additional
required fields where the official docs or test organisation has not resolved
their exact value shape.

## Autonomous write protocol

For every write, the preview tool validates the typed input, selects the known
organisation when available, canonicalises the complete request, creates a
short-lived ticket, and returns without making a Billy mutation. The execute
tool accepts exactly `{ "confirmation_ticket": "…" }` and no business fields
or approval boolean.

The confirmation binding is exact and single-use:

| Binding field | Create | Update | Delete |
| --- | --- | --- | --- |
| `tool` | exact execute tool name | exact execute tool name | exact execute tool name |
| `organization_id` | selected organisation or null | selected organisation or null | selected organisation or null |
| `target` | null | resource id | resource id |
| `request` | complete canonical `{root: object}` | complete canonical `{root: object}` | canonical `{id: id}` |
| `expected_effect_state` | create/resource summary | update/resource/id summary | delete/resource/id summary |
| file/destination bindings | null | null | null |

Tickets are process-volatile, contain at least 256 bits of cryptographic
entropy, expire in no more than five minutes, and return the existing stable
confirmation errors for invalid, expired, consumed, or mismatched use. Tests
must cover ticket tampering, wrong tool, organisation, target, request, and
effect, plus replay and expiry. Preview tests must prove no HTTP write occurs;
execute tests must capture the exact method, route, and JSON body.

Every preview result includes a human-readable summary, the exact canonical
request, expected effect state, opaque confirmation ticket, and UTC expiry.
Every execute result is a typed mapped Billy success or a typed `ToolError`.
Tickets, emails, phones, and other sensitive values are never logged.

## Qualification boundary

- Green only `implemented` and `contract_tested` for these fifteen rows after
  both paired tools, focused contract tests, server registration, and generated
  evidence exist.
- Keep `live_tested`, all interface/vision states, all 92 bulk rows, every
  out-of-cohort clear write, specials, auth tools, and `complete` red.
- The unauthenticated DELETE 200 observation is not authenticated cleanup
  evidence and cannot green a row or prove `meta.deletedRecords`.
- No file upload, invoice email/delivery, webhook, callback, or generic tool is
  in this contract.

## Sources

1. Official Billy API documentation: https://www.billy.dk/api/ (fingerprint
   above; current-documentation research in the cited Grok brief).
2. Approved design, sections 5–6 and write protocol requirements:
   `docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md`.
3. Complete operation, request/response, error, sensitivity, and current-state
   rows: `coverage/api_v2_manifest.yaml`.
4. Cited official-document analysis and reproducible unauthenticated probes:
   `.fractal/main.billy_complete/tmp/grok-research.md`.
