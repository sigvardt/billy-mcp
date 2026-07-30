---
name: wave_fiveq_users_product_implementation_research
title: Wave-5q users product implementation research
desc: Cited offline product implementation handoff for singular users update ticketed writes after freeze independent ACCEPT; create, delete, bulk, live, UI, and completeness remain separate.
tags: [billy, api, users, writes, research, offline]
sources:
  - https://www.billy.dk/api/
  - https://api.billysbilling.com/v2
  - wiki/wave_fiveq_ticketed_writes_contract.md
  - wiki/wave_fiveq_freeze_independent_review.md
  - wiki/wave_fiveq_users_product_ready_research.md
  - wiki/offline_write_probe_rules.md
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
created: 2026-07-30T14:00:00Z
updated: 2026-07-30T14:00:00Z
---

# Wave-5q users product implementation research

## Authority

| Gate | Status |
| --- | --- |
| Official docs body | ETag `wcw4x9hqvu3603`, 147934 bytes, MD5 `8b94b0135c91fd15fe54ea33e088a4be` (byte-stable vs prior research) |
| Freeze page | `wiki/wave_fiveq_ticketed_writes_contract.md` MD5 `c53717468aff0406799feca225a00728` |
| Freeze independent review | **ACCEPT** (`wiki/wave_fiveq_freeze_independent_review.md`) |
| Product-ready research IR | **ACCEPT as research** |
| This package | **Implementation handoff only** — not product ACCEPT |

This page authorises a Codex Power offline product leaf for the two named tools. It does not green coverage by itself, claim live/UI/vision, or claim completeness.

## Official contract (users update only)

- Path: `/v2/users`
- Supports: get by id, list, **update**, bulk save, bulk delete
- Omits: create, singular delete
- Unauth probes (JSON object body `{}`, locked base `https://api.billysbilling.com/v2`):
  - `POST /users` → 405 `METHOD_NOT_ALLOWED`
  - `PUT /users/:id` → 401 `AUTHENTICATION_REQUIRED` (product gate open)
  - `DELETE /users/:id` → 405 `METHOD_NOT_ALLOWED`
  - Empty-body PUT → 400 `INVALID_REQUEST_BODY` (not method-closed)

## Frozen tools

| Inventory id | Preview | Execute | Request | Required success root |
| --- | --- | --- | --- | --- |
| `api.users.update` | `api_users_update_preview` | `api_users_update_execute` | `PUT /users/:id` with `{id, user: map}` | `users` |

Inner `user` is opaque `dict[str, JsonValue]`. If `user.id` is present it must equal path `id`. Shared confirmation-ticket protocol: preview non-mutating; execute ticket-only; ticket ≤5 minutes; single-use; exact tool/org/target/request/effect binding; one HTTP write; no retry.

Sensitivity: **high** (PII email/phone + privilege flags). Do not assert privilege-flag mutability. Cleanup for live greening is restore-via-PUT; singular DELETE is method-closed.

## Codex Power product leaf

Suggested name: `wave5q_users_product` (`--agent=codex-power`).

| Path | Action |
| --- | --- |
| `src/billy_mcp/api/user_writes.py` | Create update-only twin of organization writes |
| `tests/api/test_user_writes.py` | Create contract tests (two tools) |
| `src/billy_mcp/server.py` | Register tools with shared write protocol |
| `scripts/generate_coverage_report.py` | Add `api.users.update` to `OFFLINE_API_IMPLEMENTATION_EVIDENCE` |
| Coverage artifacts | Regenerate → **178** offline implemented + contract_tested |
| `tests/unit/test_coverage_server.py` | Register two tools; api tool count **260 → 262** |

Template: update half of `src/billy_mcp/api/organization_writes.py` and `tests/api/test_organization_writes.py`.

Out of scope: create/delete/bulk users tools, salesTaxReturns, specials, UI, live, vision, completeness.

## Next after product

1. Grok product independent review.
2. Wave-5r `salesTaxReturns` update-only freeze (PUT 401; POST/DELETE 405; opaque map; non-readonly candidates offline: `periodText`, `reportDeadline`, `isSettled`).

## Non-claims

Not product ACCEPT. Not live/UI/vision. Not bulk resolution. Not completeness. No credentials used. No headed browser. No persistent test data.
