---
name: wave_fiveq_users_freeze_ready_research
title: Wave-5q users update freeze-ready research
desc: Cited offline freeze-ready package for singular users update ticketed writes; create, delete, bulk, product, live, UI, and completeness remain separate.
tags: [billy, api, users, writes, research, offline]
sources:
  - https://www.billy.dk/api/
  - https://api.billysbilling.com/v2
  - wiki/wave_fivep_candidate_write_research.md
  - wiki/wave_fivep_ticketed_writes_contract.md
  - wiki/offline_write_probe_rules.md
  - coverage/api_v2_manifest.yaml
  - coverage/status.json
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
created: 2026-07-30T12:24:00Z
updated: 2026-07-30T12:24:00Z
---

# Wave-5q users update freeze-ready research

## Authority boundary

This page freezes **research evidence only** for a future wiki freeze contract covering singular Billy API **`users` update**. It is not freeze ACCEPT, product authority, implementation, tests, coverage greening, live qualification, UI/vision work, bulk resolution, or completeness.

Full probe matrices and scratch snapshots live outside the shared wiki at
`.fractal/main.billy_complete/tmp/grok-research.md` (research70).

## Official docs fingerprint (2026-07-30)

| Field | Value |
| --- | --- |
| URL | https://www.billy.dk/api/ |
| HTTP | 200 |
| ETag | `"wcw4x9hqvu3603"` |
| Body bytes | 147934 |
| MD5 | `8b94b0135c91fd15fe54ea33e088a4be` |
| Note | Byte-identical to research69 / research68 / research67 HTML bodies |

Inventory lock metadata in `coverage/status.json` still cites ETag
`hsisik4g9p3603` / MD5 `c2efda0ee4cf9cf200e14910c5fc6996` (access/CDN drift only;
Supports and property tables unchanged).

API base remains locked to `https://api.billysbilling.com/v2`. Paths below are
client-relative and omit `/v2`.

## Unauthenticated method gates

Probes used JSON object body `{}` for POST/PUT. No credentials. No persistent
records.

| Method | Path | Status | errorCode |
| --- | --- | --- | --- |
| POST | `/users` | 405 | `METHOD_NOT_ALLOWED` (does not support creating records) |
| PUT | `/users/:id` | 401 | `AUTHENTICATION_REQUIRED` |
| DELETE | `/users/:id` | 405 | `METHOD_NOT_ALLOWED` (does not support deleting a single record) |

Shared 401 message: must use Basic auth or an OAuth access token.

## Official Supports and properties

`/v2/users` Supports: get by id, list, **update**, bulk save, bulk delete.
Supports omits create and singular delete (matches method gates).

| Property | Type | Notes | Freeze treatment |
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

## Exact future freeze surface

| Inventory id | Preview tool | Execute tool | Request | Required success root |
| --- | --- | --- | --- | --- |
| `api.users.update` | `api_users_update_preview` | `api_users_update_execute` | `PUT /users/:id` with outer `{id, user: map}` | `users` |

These two names are the **only** tools a Wave-5q freeze page may declare.

Shared ticketed-write rules (design + prior freezes):

- Outer Pydantic models forbid undeclared fields.
- Inner `user` is an opaque map.
- If inner `user.id` is present, it must equal path `id`.
- Preview issues a single-use ticket (≤5 minutes) bound to execute tool, org,
  target, canonical request, and expected effect.
- Execute accepts only `{confirmation_ticket}`; no business payload; no approval
  boolean; one HTTP write; no retry.

## Exclusions

- No create or delete tools (405).
- No bulk tools (no bulk body contract; 92 bulk rows stay red).
- No webhooks (0 mentions on official page).
- No live, UI, vision, or completeness claims.
- No singular-delete cleanup claim; inventory “restore prior test state” is
  unproven live.
- No privilege-flag safety claim offline.
- Do not green coverage from research or freeze text alone.

## Related candidates (not this freeze)

| Candidate | Offline posture |
| --- | --- |
| organizations create/update | Wave-5p freeze ACCEPT; product leaf in flight |
| salesTaxReturns update | Sequential Wave-5r; PUT 401; narrow non-readonly columns |
| invoiceReminderAssociations delete | **Blocked** (DELETE missing id returns 200 meta-only; cleanup unproven) |
| Many Supports create/update geo/reference rows | Unauth POST/PUT **405** overrides Supports; not freeze candidates |
| transactions create/update | Method-open later research; property table all readonly offline |
| Specials (files upload, invoice email, delivery, logs) | Method-open later special wave |

## Coverage honesty at research time

Root baseline remains 175 implemented and contract-tested API rows, 0 live, 0
vision, 92 ambiguous bulk red, UI all red, `complete: false`. This research
changes none of those figures.

## Recommended next step

Codex Power authors wiki-only
`wiki/wave_fiveq_ticketed_writes_contract.md` from this package. Independent
freeze ACCEPT is required before any users product module, registration, tests,
or coverage greening.
