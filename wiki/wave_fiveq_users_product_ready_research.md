---
name: wave_fiveq_users_product_ready_research
title: Wave-5q users product-ready research
desc: Cited offline product-ready package for singular users update ticketed writes after freeze independent ACCEPT; create, delete, bulk, live, UI, and completeness remain separate.
tags: [billy, api, users, writes, research, offline, product]
sources:
  - https://www.billy.dk/api/
  - https://api.billysbilling.com/v2
  - wiki/wave_fiveq_ticketed_writes_contract.md
  - wiki/wave_fiveq_users_freeze_ready_research.md
  - wiki/offline_write_probe_rules.md
  - wiki/wave_fivep_product_independent_review.md
  - coverage/api_v2_manifest.yaml
  - coverage/status.json
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
created: 2026-07-30T12:52:00Z
updated: 2026-07-30T12:52:00Z
---

# Wave-5q users product-ready research

## Authority boundary

This page freezes **research evidence only** for an offline product leaf covering
singular Billy API **`users` update**. It is not freeze independent ACCEPT,
product ACCEPT, implementation, tests, coverage greening, live qualification,
UI/vision work, bulk resolution, or completeness.

Full probe matrices and scratch snapshots live outside the shared wiki at
`.fractal/main.billy_complete/tmp/grok-research.md` (research71).

## Official docs fingerprint (2026-07-30)

| Field | Value |
| --- | --- |
| URL | https://www.billy.dk/api/ |
| HTTP | 200 |
| ETag | `"wcw4x9hqvu3603"` |
| Body bytes | 147934 |
| MD5 | `8b94b0135c91fd15fe54ea33e088a4be` |
| Note | Byte-identical to research70 / research69 / research68 / research67 HTML bodies |

Inventory lock metadata in `coverage/status.json` still cites ETag
`hsisik4g9p3603` / MD5 `c2efda0ee4cf9cf200e14910c5fc6996` (access/CDN drift only;
Supports and property tables unchanged).

API base remains locked to `https://api.billysbilling.com/v2`. Paths below are
client-relative and omit `/v2`.

## Freeze page prerequisite

| Field | Value |
| --- | --- |
| Freeze page | [[wave_fiveq_ticketed_writes_contract]] |
| Freeze page MD5 | `c53717468aff0406799feca225a00728` |
| Freeze independent review | **Not landed** at research packaging time |
| Product rule | No users write source until freeze independent review **ACCEPT** |

## Unauthenticated method gates

Probes used JSON object body `{}` for POST/PUT. No credentials. No persistent
records.

| Method | Path | Status | errorCode |
| --- | --- | --- | --- |
| POST | `/users` | 405 | `METHOD_NOT_ALLOWED` (does not support creating records) |
| PUT | `/users/:id` | 401 | `AUTHENTICATION_REQUIRED` |
| DELETE | `/users/:id` | 405 | `METHOD_NOT_ALLOWED` (does not support deleting a single record) |

Shared 401 message: must use Basic auth or an OAuth access token.

Empty-body PUT control returns **400** `INVALID_REQUEST_BODY` before auth and is
not a method-closed signal.

## Official Supports and properties

`/v2/users` Supports: get by id, list, **update**, bulk save, bulk delete.
Supports omits create and singular delete (matches method gates).

| Property | Type | Notes | Product treatment |
| --- | --- | --- | --- |
| createdTime | datetime | readonly | not client-writable |
| name | string | required | opaque inner value |
| email | string | required | opaque; PII |
| phone | string | | opaque; PII |
| profilePicFile | belongs-to | readonly | not client-writable |
| profilePicUrl / profilePic48Url | string | readonly | not client-writable |
| isStaff / isSupporter / isAdmin | boolean | privilege flags | opaque; high sensitivity |
| isSupportAccessAllowed | boolean | user choice | opaque |

No official users create/update sample JSON. Do not invent password, invite, MFA,
or auth-user special routes. `GET /v2/user` and `GET /v2/user/organizations` are
separate already-green specials.

## Exact product surface

| Inventory id | Preview tool | Execute tool | Request | Required success root |
| --- | --- | --- | --- | --- |
| `api.users.update` | `api_users_update_preview` | `api_users_update_execute` | `PUT /users/:id` with outer `{id, user: map}` | `users` |

These two names are the **only** tools a Wave-5q product leaf may register.

Shared ticketed-write rules (design + freeze):

- Outer Pydantic models forbid undeclared fields.
- Inner `user` is an opaque map.
- If inner `user.id` is present, it must equal path `id`.
- Preview issues a single-use ticket (≤5 minutes) bound to execute tool, org,
  target, canonical request, and expected effect.
- Execute accepts only `{confirmation_ticket}`; no business payload; no approval
  boolean; one HTTP write; no retry.
- Use the shared confirmation store already on root.

## Greening and honesty

| Item | Rule |
| --- | --- |
| Inventory row | Green only `api.users.update` offline (`implemented` + `contract_tested`) |
| Live / vision | Remain false |
| Cleanup | Must not claim singular DELETE (405). Live restore remains unqualified offline |
| Sensitivity | Treat PII and privilege flags as high; redaction already keys `email` and `phone` |
| Coverage count | 177 → 178 offline after merge; `complete` stays false |
| Bulk users | Stay empty-tool red |

## Implementation ownership (after freeze IR ACCEPT)

| Path | Role |
| --- | --- |
| `src/billy_mcp/api/user_writes.py` | New update-only module |
| `tests/api/test_user_writes.py` | Contract tests (organization update twin) |
| `src/billy_mcp/server.py` | Register with shared write protocol |
| `coverage/api_v2_manifest.yaml` + generated status/report | Green one row honestly |

Peer templates: `src/billy_mcp/api/organization_writes.py` (update half) and
`tests/api/test_organization_writes.py`.

## Exclusions

- No create or delete tools (405).
- No bulk tools (no bulk body contract; 92 bulk rows stay red).
- No webhooks (0 mentions on official page).
- No product source before freeze independent ACCEPT.
- No live CUD, UI, vision, or completeness claims.
- Wave-5r `salesTaxReturns` update is a sequential later freeze, not this leaf.
- Method-closed Supports false friends (geo/reference rows with unauth 405) stay red offline.
- `invoiceReminderAssociations` delete remains blocked offline until live cleanup proof.

## Root baseline at packaging

- Wave-5p organizations product independent review: **ACCEPT**.
- Offline coverage: **177** implemented and contract_tested; live **0**; vision **0**.
- UI: 339 all red.
- `BILLY_API_TOKEN` unavailable; no interface discovery this pass.

## Recommended next steps

1. Independent freeze review of [[wave_fiveq_ticketed_writes_contract]] → ACCEPT or REJECT.
2. Optional independent review of this page as **ACCEPT as research**.
3. After freeze ACCEPT only: Codex Power product leaf with the two tools above.
4. Product independent review; then sequential Wave-5r research/freeze for
   `salesTaxReturns` update.
