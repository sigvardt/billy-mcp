---
name: wave_fiveq_users_product_ready_research_independent_review
title: Wave-5q users product-ready research independent review
desc: Independent Grok ACCEPT as research for the Wave-5q users update product-ready package; freeze independent ACCEPT and product remain separate gates.
tags: [billy, api, users, writes, review, research]
sources:
  - https://www.billy.dk/api/
  - https://api.billysbilling.com/v2
  - wiki/wave_fiveq_users_product_ready_research.md
  - wiki/wave_fiveq_ticketed_writes_contract.md
  - wiki/wave_fiveq_users_freeze_ready_research.md
  - wiki/wave_fiveq_users_freeze_ready_research_independent_review.md
  - wiki/offline_write_probe_rules.md
  - coverage/api_v2_manifest.yaml
  - coverage/status.json
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
created: 2026-07-30T13:05:00Z
updated: 2026-07-30T13:05:00Z
---

# Wave-5q users product-ready research independent review

## Verdict

**ACCEPT as research** for the Wave-5q offline product-ready package covering
singular `users` update only (exactly two ticketed tools after a separate freeze
independent ACCEPT).

This is not freeze-page ACCEPT, product ACCEPT, live ACCEPT, UI ACCEPT, vision
ACCEPT, bulk resolution, or overall completeness. It does not authorise
implementation by itself.

## Scope accepted

- Official API contract for `/v2/users` Supports get by id, list, **update**,
  bulk save, and bulk delete. Supports omits create and singular delete (matches
  method gates).
- Independent docs fingerprint: HTTP 200, ETag `"wcw4x9hqvu3603"`, MD5
  `8b94b0135c91fd15fe54ea33e088a4be`, body 147934 bytes (byte-identical to the
  research71 / research70 snapshot cited by the package).
- Inventory lock metadata in `coverage/status.json` still cites ETag
  `hsisik4g9p3603` / MD5 `c2efda0ee4cf9cf200e14910c5fc6996` (documented access/CDN
  drift only; Supports and property tables unchanged on re-fetch).
- Unauthenticated probes against locked base `https://api.billysbilling.com/v2`
  with JSON object body `{}` and no credentials:
  - `POST /users` → 405 `METHOD_NOT_ALLOWED` (does not support creating records)
  - `PUT /users/:id` → 401 `AUTHENTICATION_REQUIRED` (Basic or OAuth required)
  - `DELETE /users/:id` → 405 `METHOD_NOT_ALLOWED` (does not support deleting a
    single record)
  - Empty-body PUT control → 400 `INVALID_REQUEST_BODY` (not a method-closed
    signal), matching the package and [[offline_write_probe_rules]]
- Freeze page [[wave_fiveq_ticketed_writes_contract]] is present on root; on-disk
  MD5 `c53717468aff0406799feca225a00728` matches the package claim. Freeze
  independent review page for that contract has **not** landed; product source
  correctly remains barred until freeze independent ACCEPT.
- Product-ready package bounds the leaf to
  `api_users_update_preview` / `api_users_update_execute` only: `PUT /users/:id`,
  strict outer `{id, user}`, opaque `user` map, optional matching inner `id`,
  required success root `users`, shared ticket protocol (single-use ≤5 minutes,
  execute accepts only `confirmation_ticket`, one no-retry HTTP write).
- PII (`email`, `phone`) and privilege flags (`isStaff`, `isSupporter`,
  `isAdmin`) are called high sensitivity; package forbids inventing password,
  invite, MFA, or special auth-user routes.
- Fail-closed cleanup: greening must not claim singular DELETE (405 closed).
  Inventory row `api.users.update` still carries generic cleanup text
  ("restore prior test state"); the package correctly overrides that for
  offline greening.
- Coverage honesty at review time: **177** implemented and contract-tested,
  live **0**, vision **0**, 92 ambiguous bulk red, UI 339 all red,
  `complete: false`. Package arithmetic 177 → 178 offline after a future product
  merge is correct; research greened nothing.
- Inventory confirms `api.users.update` is `implemented: false`,
  `contract_tested: false`, tool name still the prospective preview name only.
  Bulk users rows remain empty-tool red. No `user_writes` product module and no
  `api_users_update_*` registration on this branch (only existing ledger user
  reads).
- Wave-5r `salesTaxReturns` update remains sequential later work;
  `invoiceReminderAssociations` delete remains blocked offline.

## Exact product surface accepted as research package

| Inventory id | Preview | Execute | Method and client path | Request | Required success root |
| --- | --- | --- | --- | --- | --- |
| `api.users.update` | `api_users_update_preview` | `api_users_update_execute` | `PUT /users/:id` | outer `{id, user}` with opaque `user` map | `users` |

These two names are the only tools a Wave-5q product leaf may register after
freeze independent ACCEPT.

## Explicit non-acceptances

- **Freeze independent ACCEPT** of [[wave_fiveq_ticketed_writes_contract]]
  (still not landed as a freeze IR page; freeze-ready research IR
  [[wave_fiveq_users_freeze_ready_research_independent_review]] is a different
  gate and does not accept the freeze page)
- Users product tools, server registration, contract tests, or coverage greening
- Create or singular delete tools (405)
- Bulk save/delete tools (92 bulk rows stay red)
- Webhook tools
- Live CUD, UI, vision qualification, or completeness
- Authorisation to open a Codex Power product leaf before freeze IR ACCEPT

## Evidence

| Item | Value |
| --- | --- |
| Package under review | [[wave_fiveq_users_product_ready_research]] |
| Freeze page | [[wave_fiveq_ticketed_writes_contract]] MD5 `c53717468aff0406799feca225a00728` |
| Freeze-ready research | [[wave_fiveq_users_freeze_ready_research]] |
| Prior freeze-ready research IR | [[wave_fiveq_users_freeze_ready_research_independent_review]] |
| Probe rules | [[offline_write_probe_rules]] (`users` POST/DELETE 405; PUT 401) |
| Docs re-fetch | ETag `"wcw4x9hqvu3603"`, MD5 `8b94b0135c91fd15fe54ea33e088a4be`, 147934 bytes, HTTP 200 |
| Supports snippet | `Supports: get by id, list, update, bulk save, bulk delete` |
| Coverage | `coverage/status.json` 177/177 offline, live 0, vision 0, complete false |
| Inventory | `api.users.update` implemented false / contract_tested false |
| Product source | absent (`src/billy_mcp/api/user_writes.py` not present) |
| Probe scratch (git-ignored) | node `tmp/write-probes-review.json` and `tmp/docs_fingerprint.json` |

## Remaining gate

1. Parent-owned independent freeze review of
   [[wave_fiveq_ticketed_writes_contract]] → ACCEPT or REJECT.
2. Only after freeze IR ACCEPT: Codex Power product leaf for the two tools above.
3. Then product independent review. This research ACCEPT is not a substitute for
   either step.
