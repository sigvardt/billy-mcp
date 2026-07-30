---
name: wave_fiveq_users_product_independent_review
title: Wave-5q users product independent review ACCEPT
desc: Authoritative offline Grok ACCEPT for singular users update ticketed write tools on parent baseline e47da25; create, singular delete, bulk, live, UI, vision, and completeness remain fail-closed.
tags: [billy, api, users, writes, review, product]
sources:
  - https://www.billy.dk/api/
  - https://api.billysbilling.com/v2
  - wiki/wave_fiveq_ticketed_writes_contract.md
  - wiki/wave_fiveq_freeze_independent_review.md
  - wiki/offline_write_probe_rules.md
  - coverage/api_v2_manifest.yaml
  - coverage/status.json
  - coverage/ui_workflows_manifest.yaml
  - scripts/generate_coverage_report.py
  - src/billy_mcp/api/user_writes.py
  - src/billy_mcp/api/write_protocol.py
  - src/billy_mcp/confirmations.py
  - src/billy_mcp/client.py
  - src/billy_mcp/config.py
  - src/billy_mcp/redaction.py
  - src/billy_mcp/server.py
  - tests/api/test_user_writes.py
  - tests/unit/test_coverage_server.py
  - tests/coverage/test_coverage_inventory.py
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
created: 2026-07-30T15:00:00Z
updated: 2026-07-30T15:00:00Z
---

# Wave-5q users product independent review ACCEPT

## Verdict

| Claim | Result |
| --- | --- |
| Wave-5q offline product (singular update ticketed writes only) | **ACCEPT** |
| Official documentation versus update-only product surface | **PASS** |
| Unauth method gates (POST 405; PUT 401; DELETE 405) | **PASS** |
| Exactly two update tools versus freeze contract | **PASS** |
| Ticket binding, path lock, response-root mapping, no-retry | **PASS** |
| Strict outer models, opaque inner map, optional path/body id match | **PASS** |
| PII redaction (`email`/`phone`) and high-sensitivity accounting | **PASS** |
| Coverage honesty (`complete: false`; 178 offline; 262 tools; live 0; vision 0; bulk red; UI red) | **PASS** |
| Users update offline green; create/delete tools absent; bulk red | **PASS** |
| Live, UI, vision, bulk, create, singular-delete cleanup, completeness | **not claimed / fail-closed** |

**Verdict: ACCEPT**

This authoritative Grok product review accepts only the offline Wave-5q
users ticketed-write **update** product slice at parent baseline **`e47da25`**
(`e47da2588eb881df1b9de3eba3aedc44d2d8a1fc`), which contains product merge
`5d81a0f` and product implementation `a3641fe`.

This ACCEPT is not live testing, UI/vision acceptance, bulk resolution, create
or singular-delete authorisation, cleanup qualification, webhook support, or
overall product completeness.

No production source, tests, coverage rows, status values, freeze pages, or
other wiki pages were modified by this review. Exclusive deliverable is this
page. Parent regenerates `wiki/_index.md` after merge.

## Reviewed baseline

| Item | Value |
| --- | --- |
| Parent product baseline under review | `e47da25` (`e47da2588eb881df1b9de3eba3aedc44d2d8a1fc`) |
| Product merge | `5d81a0f` (`5d81a0fe050e019f96fd2c159ab9b4a6768c965a`, `merge main.billy_complete.wave5q_users_product`) |
| Product implementation commit | `a3641fe` (`a3641fedc298e1c9192f9221cd89ff9b53a97d17`; adds `user_writes.py`, `tests/api/test_user_writes.py`, inventory greening for update) |
| Freeze page | `wiki/wave_fiveq_ticketed_writes_contract.md` (full-file MD5 `c53717468aff0406799feca225a00728`) |
| Freeze independent review | **ACCEPT** at `wiki/wave_fiveq_freeze_independent_review.md` |
| Product module MD5 | `6f2168630f04fbbfa365c5030297d70d` (`src/billy_mcp/api/user_writes.py`) |
| Locked API base | `https://api.billysbilling.com/v2` (`src/billy_mcp/config.py`) |

Merge `5d81a0f` and implementation `a3641fe` are ancestors of `e47da25`. This
review targets the **parent integration baseline** named in the leaf brief, not
a detached product child worktree.

## Evidence classes (keep separate)

| Class | What it proves | What it does not prove |
| --- | --- | --- |
| Current official docs (`https://www.billy.dk/api/`) | Supports update; omits create and singular delete; property table for opaque-map and sensitivity treatment | Authenticated success, live mutation, cleanup qualification |
| This-review unauth probes (`https://api.billysbilling.com/v2`) | Method gates: POST 405; PUT 401; singular DELETE 405 | Live mutation, accepted payloads, response extensions |
| Offline contract tests | Schema, tickets, path, mapping, no-retry, registry/coverage honesty | Live user behaviour, UI parity, vision |
| Live / UI / vision | Not performed | Not claimed |

## Official documentation (this review)

Fetched `https://www.billy.dk/api/` during this review (HTTP client only; no
headed browser):

| Fingerprint field | Observed value |
| --- | --- |
| HTTP status | 200 |
| HTTP ETag | `wcw4x9hqvu3603` |
| Body MD5 | `8b94b0135c91fd15fe54ea33e088a4be` |
| Body size | 147934 bytes |

Inventory lock still records ETag `hsisik4g9p3603` / MD5
`c2efda0ee4cf9cf200e14910c5fc6996` while access meta is
`wcw4x9hqvu3603` / `8b94b0135c91fd15fe54ea33e088a4be` at the same 147934-byte
size. Access-metadata churn alone is not a contract change (same reading as the
freeze independent review and `wiki/offline_write_probe_rules.md`).

Direct citation for `/v2/users` (plain text from the official HTML):

> Supports: get by id, list, update, bulk save, bulk delete

Official Supports **lists update**, **omits create**, and **omits singular
delete**. Bulk save/delete remain listed on docs but stay out of this product
(ambiguous bulk inventory rows, empty tool names).

Property notes observed on the same page (opaque inner map; not Pydantic field
validation):

| Property | Official notes | Product treatment check |
| --- | --- | --- |
| `name` | required | Opaque inner map only — **PASS** |
| `email` | required | Opaque; PII; `redaction.py` keys `email` — **PASS** |
| `phone` | (phone number) | Opaque; PII; `redaction.py` keys `phone` — **PASS** |
| `isStaff` / `isSupporter` / `isAdmin` | boolean privilege flags | Opaque; inventory `sensitivity: high`; freeze does not claim safe to mutate — **PASS** (see residual) |
| `isSupportAccessAllowed` | boolean | Opaque only — **PASS** |
| Documented readonly fields (e.g. `createdTime`, `profilePicFile`, `profilePicUrl`, `profilePic48Url`) | readonly | Not required outer tool fields — **PASS** |

## Unauthenticated probes (evidence only, not live qualification)

Against locked base `https://api.billysbilling.com/v2` with JSON object bodies,
no credentials:

| Call | Result |
| --- | --- |
| `POST /users` body `{"user":{}}` | **405** `METHOD_NOT_ALLOWED` |
| `PUT /users/probe-id-independent-review` body `{"user":{}}` | **401** `AUTHENTICATION_REQUIRED` |
| `DELETE /users/probe-id-independent-review` | **405** `METHOD_NOT_ALLOWED` |

These reconfirm the freeze gates: singular **update** opens only at the
authentication gate (PUT 401); **create** and singular **delete** are
method-closed (POST/DELETE 405) and therefore **excluded** from the product
surface. They are not authenticated live tests and do not green
`live_tested`.

## Accepted product surface

Exactly two ticketed write tools (plus pre-existing read tools `api_users_get`
and `api_users_list`, which are not part of this write product ACCEPT):

| Inventory id | Preview tool | Execute tool | Method and client path | Singular request root | Required success root |
| --- | --- | --- | --- | --- | --- |
| `api.users.update` | `api_users_update_preview` | `api_users_update_execute` | `PUT /users/:id` | `user` | `users` |

Implementation: `src/billy_mcp/api/user_writes.py` (MD5
`6f2168630f04fbbfa365c5030297d70d`), registered from `src/billy_mcp/server.py`
via `register_user_write_tools` on the shared root `WriteProtocolService` and
`ConfirmationStore`. Client base remains locked to
`https://api.billysbilling.com/v2`. Spec uses client-relative
`collection_path="/users"` (client prefixes `/v2`).

No users create, singular delete, bulk, webhook, generic HTTP, or browser write
tool is registered by this product. Registry assertions list 262 unique
`api_*` tool names including the two update tools and excluding create/delete
user write names.

## Assertions checked

| # | Assertion | Result | Evidence |
| --- | --- | --- | --- |
| 1 | Exactly two update preview+execute tools; no create/delete/bulk write tools for this product | **PASS** | `user_writes.py` registers exactly `api_users_update_preview` and `api_users_update_execute`; focused test `test_registers_exactly_two_flat_typed_user_update_tools` asserts set equality and forbids create/delete/bulk names |
| 2 | Strict outer models (`extra="forbid"`); opaque `user` map; optional path/body id matching | **PASS** | `UserUpdatePreviewInput`: non-empty `id`, `user: dict[str, JsonValue]`, `extra="forbid"`; validator rejects `user.id != id`; empty `id` rejected; undeclared outer fields rejected; unknown inner fields preserved |
| 3 | Ticket-only execute; exact binding; single use; expiry; tamper; wrong-executor; replay | **PASS** | Execute input is `confirmation_ticket` only (`WriteExecuteInput`); `WriteProtocolService.execute` checks binding tool name, `ConfirmationStore.consume`, then discards prepared ticket; user write tests cover invalid, expired, and replayed tickets (one HTTP write only) |
| 4 | One HTTP write with no retry; required `users` response root only | **PASS** | `BillyHttpClient.request` sets write retries to 0 (`_RETRY_SAFE_METHODS` is GET/HEAD only); execute calls `_client.request` once after consume; missing/malformed `users` root → `VALIDATION_ERROR`; success maps only `changed_records.users` (extra roots such as `organizations` stripped) |
| 5 | Spec path and roots match freeze | **PASS** | `_user_update_specification`: `WriteMethod.PUT`, `collection_path="/users"`, `singular_root="user"`, `plural_root="users"`, `additional_plural_roots=()`, path-encoded `PUT /users/:id` |
| 6 | PII/privilege sensitivity and redaction | **PASS** | Inventory `sensitivity: high` and side-effects note PII/privilege; `redaction.py` keys `email` and `phone` (plus ticket/token parts); contract test asserts email, phone, and confirmation ticket never appear in logs; freeze does not claim privilege flags are safe to mutate. Residual: `isStaff`/`isSupporter`/`isAdmin` are not registered as dedicated redaction keys (boolean privilege residual, not a product REJECT for this offline slice) |
| 7 | Update inventory offline-green; create/delete tools absent; bulk remain red | **PASS** | `api.users.update`: `implemented`+`contract_tested` true, `live_tested` false, tool `api_users_update_preview`, method `PUT /v2/users/:id`, request fields `id`+`user`. No `api.users.create` or singular `api.users.delete` inventory rows. Bulk save/delete empty-tool `ambiguous_bulk` red. Generator maps update tests at `scripts/generate_coverage_report.py` |
| 8 | Root **262** `api_*` tools; **178** implemented/contract-tested; live **0**; vision **0**; bulk ambiguous **92**; UI all red; `complete: false` | **PASS** | `coverage/status.json` qualification + source_counts; `tests/unit/test_coverage_server.py` asserts `len(api_tool_names) == 262`; UI workflows: 339 rows, 0 implemented/contract/live; API ops: 0 live_tested, 0 vision_verified, 92 ambiguous bulk all red |
| 9 | Server registration on shared write protocol; locked API host | **PASS** | `server.py` imports and calls `register_user_write_tools(server, client, write_protocol)`; `config.py` locks `API_BASE_URL` |
| 10 | Current docs support update only among CUD singulars; 405/401 evidence accurate and not claimed as live testing | **PASS** | Official Supports quote above; probes table above; explicit non-live wording |
| 11 | No sensitive material, raw browser evidence, live mutation, or UI/vision claim retained in tracked paths | **PASS** | This page uses public docs fingerprints, unauth status codes, offline tests, and committed source only |
| 12 | Focused user write/coverage/registry/policy checks pass offline | **PASS** | Commands and results below |

## Commands and results

```text
# Official docs
GET https://www.billy.dk/api/
# HTTP/2 200; ETag wcw4x9hqvu3603; 147934 bytes;
# MD5 8b94b0135c91fd15fe54ea33e088a4be

# Unauth method gates (no token; JSON object body)
POST   /v2/users {...}                                    -> 405 METHOD_NOT_ALLOWED
PUT    /v2/users/probe-id-independent-review {...}        -> 401 AUTHENTICATION_REQUIRED
DELETE /v2/users/probe-id-independent-review              -> 405 METHOD_NOT_ALLOWED

# Focused offline product + coverage + registry
uv run pytest -q \
  tests/api/test_user_writes.py \
  tests/unit/test_coverage_server.py \
  tests/coverage/test_coverage_inventory.py
# 32 passed

uv run python scripts/check_coverage.py --reject-false-completeness
# Coverage inventory checks passed: 305 API rows, 339 UI rows.

uv run python scripts/check_repository_policy.py
# Repository policy checks passed.

bash .fractal/.../scripts/test.sh
# exit 0 (node default no-op; focused suite above is the product proof)
```

## Coverage and fail-closed boundaries

| Metric | Value at `e47da25` product surface |
| --- | --- |
| `api_*` tools | **262** |
| `implemented_rows` | **178** |
| `contract_tested_rows` | **178** |
| `live_tested_rows` | **0** |
| `vision_verified_rows` | **0** |
| `api_ambiguous_bulk` | **92** (all red / empty tool) |
| `complete` | **false** |
| `api.users.update` | offline green; `live_tested` false; tool `api_users_update_preview` |
| `api.users.bulk_save` / `.bulk_delete` | empty-tool red (`ambiguous_bulk`) |
| `api.users.create` / singular delete inventory rows | **absent** (correct; POST/DELETE 405) |
| All UI rows (339), including `ui.parity.users.*` | remain red / unqualified |
| Live / vision for all API rows | remain 0 / false |

**Reading of "only users update may be green offline" for this slice:** prior
waves already greened other offline API rows. At this baseline the users CUD
surface has only update offline-green; create and singular delete have no tools
and no greened create/delete inventory rows; bulk stays red. Global offline
count is 178, not 1.

## Explicit non-accepts

- Live API qualification (`live_tested` remains false; status blocker still
  notes `BILLY_API_TOKEN` unavailable).
- All UI parity and vision verification.
- Ambiguous bulk save/delete tools and greening.
- Create tools (Supports omit create; POST 405).
- Singular delete tools (Supports omit singular delete; DELETE 405).
- Webhooks, generic HTTP escape hatches, headed browser controls.
- Overall project completeness (`complete` remains false).
- Any claim that unauth 401/405 probes are live testing.
- Any claim that privilege flags are safe to mutate or that live cleanup is
  qualified.

## Residual (non-blocking)

`src/billy_mcp/redaction.py` keys `email` and `phone` and generic secret parts
(`token`, `password`, `ticket`, …). Boolean privilege flags
`isStaff`/`isSupporter`/`isAdmin` are not dedicated redaction keys. Offline
preview/execute logging did not leak those values in this review's inspection,
and the freeze forbids claiming privilege mutability. A later hygiene pass may
add explicit privilege-key redaction for error envelopes; it is not a REJECT
root for this offline product slice.

## Protocol alignment

Shared design ticket protocol in
`docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md` (preview then
ticket-only execute; short-lived single-use tickets; no silent retries) matches
the product implementation through `WriteProtocolService` and
`ConfirmationStore`. Consume-before-request and a single
`BillyHttpClient.request` with write retries forced to zero enforce no silent
retry on the prepared write.

## Final statement

**ACCEPT** the offline Wave-5q users **update-only** ticketed-write product at
baseline **`e47da25`**. Create, singular delete, bulk, live, UI, vision,
cleanup, and completeness remain fail-closed and unclaimed.
