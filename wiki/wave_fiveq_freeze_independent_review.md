---
name: wave_fiveq_freeze_independent_review
title: Wave-5q contract freeze independent review ACCEPT
desc: Authoritative root Grok acceptance of the cited offline contract for singular users update ticketed writes (create, singular delete, bulk, live, UI, vision, and completeness excluded).
tags: [billy, api, users, writes, review, coverage]
sources:
  - https://www.billy.dk/api/
  - https://api.billysbilling.com/v2
  - wiki/wave_fiveq_ticketed_writes_contract.md
  - wiki/wave_fiveq_users_freeze_ready_research.md
  - wiki/wave_fiveq_users_product_ready_research.md
  - wiki/wave_fiveq_users_freeze_ready_research_independent_review.md
  - wiki/offline_write_probe_rules.md
  - coverage/api_v2_manifest.yaml
  - coverage/status.json
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
created: 2026-07-30T13:05:00Z
updated: 2026-07-30T13:05:00Z
---

# Wave-5q contract freeze independent review ACCEPT

## Verdict

| Claim | Result |
| --- | --- |
| Wave-5q cited contract freeze | **ACCEPT** |
| Official documentation versus freeze map | **PASS** |
| Unauth method gates (PUT 401 JSON object; POST and singular DELETE 405) | **PASS** |
| Freeze versus exact one-row / two-tool update-only map | **PASS** |
| Ticket protocol, body-id equality, sensitivity boundary | **PASS** |
| Coverage honesty before product integration | **PASS** |
| Wave-5q product implementation | **not accepted** - separate parent-managed Codex Power product leaf and product review required |
| Live, UI, vision, bulk, create, singular delete, and completeness | **not claimed / fail-closed** |

**Verdict: ACCEPT**

This authoritative root Grok independent review accepts the freeze page
`wiki/wave_fiveq_ticketed_writes_contract.md` (content MD5
`c53717468aff0406799feca225a00728`) at reviewed branch baseline `67cb8ba`
(`67cb8ba64483d090578afc35d3c9ced0e481a157`). Freeze content matches the
users-freeze merge (`b8304ae` / authoring tip `a4e00ca`) byte-for-byte.

This page is the freeze gate for Wave-5q. It is not product acceptance. ACCEPT
authorises only a subsequent, separate Codex Power offline product
implementation leaf for the two named users-update tools. It does **not**
authorise coverage greening by itself, live/UI/vision work, bulk tools, create
or delete tools, cleanup qualification, or completeness.

## Reviewed baseline

| Item | Value |
| --- | --- |
| Reviewed commit | `67cb8ba` (`67cb8ba64483d090578afc35d3c9ced0e481a157`) |
| Freeze page | `wiki/wave_fiveq_ticketed_writes_contract.md` |
| Freeze content MD5 | `c53717468aff0406799feca225a00728` |
| Freeze-ready research (not freeze ACCEPT) | `wiki/wave_fiveq_users_freeze_ready_research.md` |
| Prior research IR (ACCEPT as research only) | `wiki/wave_fiveq_users_freeze_ready_research_independent_review.md` |
| Product-ready research (not product ACCEPT) | `wiki/wave_fiveq_users_product_ready_research.md` |
| Parent research scratch (when present) | `.fractal/main.billy_complete/tmp/grok-research.md` (research71) |
| Locked API base | `https://api.billysbilling.com/v2` |

## Sources and method (official evidence)

| Source | How used |
| --- | --- |
| https://www.billy.dk/api/ | Primary. Independent live fetch this review: HTTP 200, ETag `wcw4x9hqvu3603`, body MD5 `8b94b0135c91fd15fe54ea33e088a4be`, 147934 bytes. Byte-identical to Research70 / Research71 access fingerprint. `/v2/users` Supports and property table re-parsed from the fetched HTML. Inventory lock in `coverage/status.json` still records ETag `hsisik4g9p3603` / MD5 `c2efda0ee4cf9cf200e14910c5fc6996`; access/CDN metadata drift alone is not a users Supports or property change. |
| Unauth probes `https://api.billysbilling.com/v2` | Independent reconfirm with JSON object body `{}` and no token: `PUT /users/nonexistent-probe-id` → 401 `AUTHENTICATION_REQUIRED`; `POST /users` → 405 `METHOD_NOT_ALLOWED` (“does not support creating records”); singular `DELETE /users/nonexistent-probe-id` → 405 `METHOD_NOT_ALLOWED` (“does not support deleting a single record”). Not live qualification. No credentials. No created records. No raw probe bodies retained in tracked paths. |
| `wiki/wave_fiveq_ticketed_writes_contract.md` | Full freeze surface under review. |
| `wiki/wave_fiveq_users_freeze_ready_research.md` | Context; this review re-fetched docs and re-probed gates rather than copying Research70. |
| `wiki/wave_fiveq_users_product_ready_research.md` | Context only for product-ready packaging; not freeze authority and not product ACCEPT. |
| `wiki/offline_write_probe_rules.md` | Auth-gate vs 405 override rules; `users` row records POST/DELETE **405** and PUT **401** (Supports update; no create). |
| `coverage/api_v2_manifest.yaml` @ `67cb8ba` | Users rows: get/list green offline; update red with reserved preview tool name only; both bulk empty-tool `ambiguous_bulk`; no singular create or delete inventory rows. |
| `coverage/status.json` @ `67cb8ba` | `implemented_rows` 177, `contract_tested_rows` 177, `live_tested_rows` 0, `vision_verified_rows` 0, `api_ambiguous_bulk` 92, `complete: false`. |
| Registry @ `67cb8ba` | 260 unique `api_*` tools per `tests/unit/test_coverage_server.py`; users tools present are only `api_users_get` and `api_users_list` (no update write tools). |
| Design `docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md` | Ticketed write / confirmation protocol discipline (strict preview, ticket-only execute, no silent retries). |
| Peer freeze IR pattern | e.g. `wiki/wave_fivep_freeze_independent_review.md`, `wiki/wave_fiveo_freeze_independent_review.md` |

No headed browser. No credentials. No live mutations. No secrets or raw browser evidence tracked in git.

## Exact reviewed scope

The accepted contract freezes exactly one singular API v2 JSON update operation
(two ticketed tools: one preview + one execute):

| Inventory id | Preview tool | Execute tool | Method and client path | Singular request root | Required success root |
| --- | --- | --- | --- | --- | --- |
| `api.users.update` | `api_users_update_preview` | `api_users_update_execute` | `PUT /users/:id` | `user` (+ path `id`) | `users` |

Official docs for `/v2/users` (this review): Supports **get by id, list,
update, bulk save, bulk delete**. Supports omits create and singular delete
(matches method gates).

Property boundaries checked against the official table re-parsed this review:

| Property | Official notes | Freeze treatment check |
| --- | --- | --- |
| `createdTime` | datetime; readonly | Not client-writable boundary - **PASS** |
| `name` | string; required | Opaque inner value only - **PASS** |
| `email` | string; required | Opaque; explicit PII redaction duty - **PASS** |
| `phone` | string | Opaque; explicit PII redaction duty - **PASS** |
| `profilePicFile` | belongs-to; readonly | Not client-writable boundary - **PASS** |
| `profilePicUrl` / `profilePic48Url` | string; readonly | Not client-writable boundary - **PASS** |
| `isStaff` / `isSupporter` / `isAdmin` | boolean | Opaque; high-privilege sensitivity; no safety claim - **PASS** |
| `isSupportAccessAllowed` | boolean | Opaque - **PASS** |

No official create/update sample invents a stricter inner schema; the freeze
correctly keeps the `user` map opaque and invents no password, invite, MFA, or
auth-user special route. Existing redaction already covers `email` and `phone`;
privilege flags remain an explicit product redaction duty (not a freeze defect).

## Criteria checked

| # | Criterion | Result |
| --- | --- | --- |
| 1 | Authorises exactly `api.users.update` with exactly two tools (`api_users_update_preview` + `api_users_update_execute`) | **PASS** - one table row; execute twin is not an extra inventory row; no create, delete, or bulk tools frozen |
| 2 | Strict outer input `{id: non-empty string, user: map}` with undeclared outer fields forbidden; client-relative `PUT /users/:id`; required success root `users` | **PASS** - all stated on freeze; paths omit `/v2` as client-relative against locked base |
| 3 | Inner `user` is opaque `dict[str, JsonValue]`; not a generic HTTP control and not a field-level schema | **PASS** |
| 4 | Optional inner `user.id` must equal path `id` when present; absent inner id is not invented | **PASS** |
| 5 | Ticket-only execute; five-minute single-use exact operation bindings; exactly one HTTP write; no retry; fail-closed on bad tickets | **PASS** - execute input is only `{confirmation_ticket}`; no business payload or approval boolean |
| 6 | Unauth PUT 401 with JSON object body opens offline update freeze only; not live qualification | **PASS** - independently reconfirmed this review |
| 7 | POST 405 excludes create; singular DELETE 405 excludes delete and does not qualify cleanup | **PASS** - independently reconfirmed this review |
| 8 | Sensitivity: `email`/`phone` PII; `isStaff`/`isSupporter`/`isAdmin` privilege flags; no claim privilege flags are safe to mutate | **PASS** |
| 9 | Excludes create, singular delete, every bulk op, webhooks, generic controls, live, UI, vision, cleanup qualification, greening, completeness | **PASS** |
| 10 | Coverage honesty: update still red; bulk empty-tool red; complete false; no write tools registered | **PASS** |

No discrepancy requires REJECT.

## Assertions checked (detail)

| Assertion | Result |
| --- | --- |
| Exactly one inventory row; two named future tools | **PASS** |
| Path `PUT /users/:id` (client-relative, no double `/v2`) | **PASS** |
| Outer update `{id, user: map}`; undeclared outer fields forbidden | **PASS** |
| Inner map opaque; not generic transport; not field allowlist | **PASS** |
| Required response root only `users` | **PASS** |
| Preview non-mutating; ticket ≤ five minutes; single-use; bound to execute tool, org, target, request, effect | **PASS** |
| Execute accepts only confirmation ticket; no business payload or approval boolean | **PASS** |
| Exactly one HTTP write; no retry | **PASS** |
| Update path `id` equals inner `user.id` when supplied | **PASS** |
| PUT unauth 401 is offline gate only, not live qualification | **PASS** - reconfirmed this review |
| POST 405 excludes create product | **PASS** - reconfirmed this review |
| Singular DELETE 405 excludes delete product and cleanup qualification | **PASS** - reconfirmed this review |
| Bulk save/delete excluded (no full bulk body contract; 92 bulk rows remain red) | **PASS** |
| Webhooks, generic transport, UI, vision, live, completeness excluded | **PASS** |
| PII and privilege flags must be treated as sensitive; not logged or stored as raw values | **PASS** |
| Product tools not implemented or registered at freeze baseline | **PASS** - only get/list registered for users |
| Registry honesty 260 `api_*` tools; users write tools absent | **PASS** |
| Coverage 177/177 offline; live 0; vision 0; bulk 92; `complete: false` | **PASS** |

## Method-gate evidence (this review)

| Method and path | HTTP | errorCode | Freeze consequence |
| --- | --- | --- | --- |
| `PUT /users/:id` body `{}` | 401 | `AUTHENTICATION_REQUIRED` | Offline singular-update gate only |
| `POST /users` body `{}` | 405 | `METHOD_NOT_ALLOWED` | Create closed and excluded |
| `DELETE /users/:id` | 405 | `METHOD_NOT_ALLOWED` | Singular delete closed and excluded |

Unauthenticated probes never prove a valid payload, successful mutation,
response shape beyond the error envelope, cleanup, or live qualification.
Research71 notes that empty-body PUT can return 400 `INVALID_REQUEST_BODY`
before auth; method openness for this freeze is proven only with a JSON object
body (this review used `{}`).

## Coverage honesty snapshot

| Metric | Value at `67cb8ba` |
| --- | --- |
| `implemented_rows` | 177 |
| `contract_tested_rows` | 177 |
| `live_tested_rows` | 0 |
| `vision_verified_rows` | 0 |
| `api_ambiguous_bulk` | 92 |
| `complete` | false |
| `api.users.get` / `api.users.list` | green offline (`api_users_get` / `api_users_list`) |
| `api.users.update` | red (`implemented: false`, `contract_tested: false`; reserved tool name `api_users_update_preview` only) |
| `api.users.bulk_save` / `bulk_delete` | red, empty tool, `ambiguous_bulk` |
| Singular create / delete inventory rows | absent (correct; Supports omits create and singular delete) |

Inventory currently marks update sensitivity as `medium` and cleanup as
“restore prior test state.” The freeze correctly elevates PII and privilege
flags as sensitive for future product work and does not qualify live cleanup.
Those inventory notes are not freeze defects.

The freeze page itself does not green inventory.

## Defects

None. No actionable freeze defects found.

## Authorisation boundary

| Stage | Status after this review |
| --- | --- |
| Research | Prior context only (Research70 freeze-ready; Research71 product-ready packaging) |
| Freeze page | Accepted by this review |
| Independent freeze ACCEPT | **This page - ACCEPT** |
| Product implementation | **Opened only for** a separate Codex Power offline leaf that implements and contract-tests the two tools; still blocked until that leaf is authorised and lands |
| Product independent review | Still required after product merge |
| Coverage greening by this page alone | **Not authorised** |
| Live / UI / vision / bulk / create / delete / cleanup / completeness | Remain fail-closed and red |

## Conclusion

**ACCEPT** the Wave-5q users update ticketed-write freeze at branch baseline
`67cb8ba` with freeze MD5 `c53717468aff0406799feca225a00728`. Primary docs
fingerprint, unauth method gates, exact one-row/two-tool update-only map, ticket
protocol, optional body-id equality, sensitivity boundary, and exclusion list
all hold.

Remaining gate: parent merges this review, then may authorise a separate offline
Codex Power users-update product leaf. That product still requires its own
independent review. This ACCEPT does not authorise coverage greening by itself,
live/UI/vision work, bulk tools, create/delete tools, cleanup qualification, or
completeness.
