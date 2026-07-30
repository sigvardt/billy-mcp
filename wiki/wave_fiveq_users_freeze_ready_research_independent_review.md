---
name: wave_fiveq_users_freeze_ready_research_independent_review
title: Wave-5q users freeze-ready research independent review
desc: Independent Grok ACCEPT as research for the Wave-5q users update freeze-ready package; freeze page, product, live, UI, and completeness remain separate.
tags: [billy, api, users, writes, review, research]
sources:
  - https://www.billy.dk/api/
  - https://api.billysbilling.com/v2
  - .fractal/main.billy_complete/tmp/grok-research.md
  - .fractal/main.billy_complete/tmp/grok-review.md
  - wiki/wave_fiveq_users_freeze_ready_research.md
  - wiki/offline_write_probe_rules.md
  - coverage/api_v2_manifest.yaml
  - coverage/status.json
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
created: 2026-07-30T12:40:00Z
updated: 2026-07-30T12:40:00Z
---

# Wave-5q users freeze-ready research independent review

## Verdict

**ACCEPT as research** for the Wave-5q offline freeze-ready package covering singular `users` update only (exactly two future ticketed tools once a freeze page and product exist).

This is not freeze ACCEPT, product ACCEPT, live ACCEPT, UI ACCEPT, vision ACCEPT, bulk resolution, or overall completeness.

## Scope accepted

- Official API contract for `/v2/users` Supports update among singular writes; Supports omits create and singular delete.
- Independent docs fingerprint: ETag `wcw4x9hqvu3603`, MD5 `8b94b0135c91fd15fe54ea33e088a4be`, body 147934 bytes (byte-identical to the research70 snapshot).
- Unauthenticated probes against `https://api.billysbilling.com/v2` with JSON object body `{}`: users PUT returns 401 `AUTHENTICATION_REQUIRED`; POST and DELETE return 405 `METHOD_NOT_ALLOWED`.
- Research70 correctly bounds the freeze package to `api_users_update_preview` / `api_users_update_execute` with opaque `user` map, required success root `users`, shared ticket protocol, and no create/delete/bulk/webhook tools.
- Inventory `api.users.update` remains `implemented: false` and `contract_tested: false`; research did not green coverage.
- `salesTaxReturns` update remains a sequential later candidate; `invoiceReminderAssociations` delete remains **blocked** offline (DELETE missing id returns 200 meta-only without cleanup proof).
- At review time root coverage is 177 implemented and contract-tested (organizations product integrated offline), zero live, zero vision, 92 ambiguous bulk red, UI 339 all red, `complete: false`. Organizations product **ACCEPT** is not granted by this research review.

## Exact future freeze surface accepted as research package

| Inventory id | Preview | Execute | Method and client path | Request | Required success root |
| --- | --- | --- | --- | --- | --- |
| `api.users.update` | `api_users_update_preview` | `api_users_update_execute` | `PUT /users/:id` | `id` + `user` map | `users` |

## Explicit non-acceptances

- Wave-5q freeze page authoring (not yet on root as product authority)
- Users product tools, registration, tests, or coverage greening
- Live CUD, UI, vision, bulk 92 resolution, association delete offline
- Organizations product independent ACCEPT (separate active product review)
- Overall completeness

## Hygiene note for freeze author

The freeze-ready research page may still describe organizations product as “in flight” relative to research-time wording. Root has integrated organizations create/update offline at 177 with live still false. The freeze page must cite current docs fingerprint and must not restate stale coverage figures as live state.

## Next gate

Codex Power may author wiki-only `wiki/wave_fiveq_ticketed_writes_contract.md` from this accepted research package. Independent freeze ACCEPT is required before any users product module.
