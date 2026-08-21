---
name: wave_fiveq_users_product_implementation_research_independent_review
title: Wave-5q users product implementation research independent review
desc: Independent Grok ACCEPT as research for the Wave-5q users update product implementation handoff; product source, live, UI, vision, and completeness remain separate.
tags: [billy, api, users, writes, review, research]
sources:
  - https://www.billy.dk/api/
  - https://api.billysbilling.com/v2
  - wiki/wave_fiveq_users_product_implementation_research.md
  - wiki/wave_fiveq_ticketed_writes_contract.md
  - wiki/wave_fiveq_freeze_independent_review.md
  - wiki/offline_write_probe_rules.md
  - coverage/api_v2_manifest.yaml
  - coverage/status.json
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
created: 2026-07-30T14:22:00Z
updated: 2026-07-30T14:22:00Z
---

# Wave-5q users product implementation research independent review

## Verdict

**ACCEPT as research** for the Wave-5q offline product implementation handoff covering singular `users` update only (exactly two ticketed tools after freeze independent ACCEPT).

This is not product ACCEPT, freeze re-ACCEPT, live ACCEPT, UI ACCEPT, vision ACCEPT, bulk resolution, or overall completeness. It does not green coverage.

## Scope accepted

- Official API contract for `/v2/users` Supports get by id, list, **update**, bulk save, bulk delete; omits create and singular delete.
- Independent docs fingerprint: HTTP 200, ETag `"wcw4x9hqvu3603"`, MD5 `8b94b0135c91fd15fe54ea33e088a4be`, body 147934 bytes (byte-identical to the research72 snapshot).
- Unauthenticated probes on locked base `https://api.billysbilling.com/v2` with JSON object body `{}`:
  - `POST /users` → 405 `METHOD_NOT_ALLOWED`
  - `PUT /users/:id` → 401 `AUTHENTICATION_REQUIRED`
  - `DELETE /users/:id` → 405 `METHOD_NOT_ALLOWED`
  - Empty-body PUT → 400 `INVALID_REQUEST_BODY`
- Freeze page MD5 `c53717468aff0406799feca225a00728` and freeze IR **ACCEPT** remain the product-source authority.
- Handoff names only `api_users_update_preview` and `api_users_update_execute`; opaque `user` map; ticket protocol; high sensitivity; restore-via-PUT cleanup honesty.
- Root coverage honesty: 177 implemented + contract_tested; live 0; vision 0; `complete: false`; `api.users.update` still red; 92 bulk empty-tool red; UI 0 green.

## Product status at review time

No `src/billy_mcp/api/user_writes.py` on root. Product child may be active separately. Product ACCEPT requires merged tools, contract tests, generator greening to 178 offline rows, registry tool count 262, and a separate product independent review.

## Non-claims

Not product ACCEPT. Not live/UI/vision. Not bulk resolution. Not completeness. No credentials used. No headed browser. No persistent test data.

Parent scratch detail: `.fractal/main.billy_complete/tmp/grok-review.md` (review72).
