---
name: wave_fives_research90_independent_review
title: Research90 and Wave-5u plan independent review
desc: Independent Grok review of Research90 OPTIONS non-discrimination evidence and the Wave-5u method-level observation plan. ACCEPT research and planning only; completeness FAIL; no coverage greening.
tags: [billy, review, research, wave5u, residual, bulk, infrastructure]
sources:
  - https://www.billy.dk/api/
  - https://api.billysbilling.com/v2
  - wiki/wave_fives_residual_specials_research.md
  - wiki/offline_write_probe_rules.md
  - coverage/status.json
  - coverage/api_v2_manifest.yaml
  - src/billy_mcp/live_probe.py
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
  - "parent scratch: .fractal/main.billy_complete/tmp/grok-review.md (review90)"
  - "parent scratch: .fractal/main.billy_complete/tmp/grok-research.md (research90)"
created: 2026-07-30T21:22:00Z
updated: 2026-07-30T21:22:00Z
---

# Research90 and Wave-5u plan independent review

## Authority boundary

This page freezes **independent review** of Research90 and the Wave-5u plan on
root tip `ee46c3f`. It is not product ACCEPT for residual/bulk tools, live
qualification, UI/vision work, or completeness. It does not green coverage.

Full report: `.fractal/main.billy_complete/tmp/grok-review.md` (review90).

## Verdicts

| Claim | Result |
| --- | --- |
| Research90 docs + residual/bulk reconfirm | **ACCEPT** as research only |
| OPTIONS non-discrimination (204 + full CORS on closed and open routes) | **ACCEPT** as research (independently reproduced) |
| Wave-5u plan (method-level fail-closed observation) | **ACCEPT** as planning only |
| Root coverage honesty | **PASS** (184/184/0/0, `complete: false`) |
| Wave-5t OPTIONS harness | **ACCEPT infrastructure only** (non-qualifying) |
| Wave-5u implementation / residual / bulk / UI / vision / completeness | **FAIL** |

## Independent evidence

| Check | Result |
| --- | --- |
| Docs | ETag `"wcw4x9hqvu3603"`, 147934 bytes, MD5 `8b94b0135c91fd15fe54ea33e088a4be` (byte-identical to research90) |
| OPTIONS `/accountNatures` / `/transactions` | **204**, identical full CORS method list |
| POST `/accountNatures` | **405** `METHOD_NOT_ALLOWED` |
| POST `/transactions` | **401** `AUTHENTICATION_REQUIRED` |
| PUT `/contacts/bulk` | **401** |
| GET `/user/organizations` | **404** `UNKNOWN_RESOURCE` |
| Residual/bulk matrix vs inventory | 29 + 92 exact match in `research88_candidates()` |
| Harness on root | still `OBSERVATION_METHOD = "OPTIONS"` |

## Blockers (parent-facing)

1. Live token + dedicated non-production organisation guard unset.
2. UI credentials / session absent (UI 339; vision 0).
3. `GET /v2/user/organizations` docs vs unauth 404 vs offline tool path.
4. Wave-5u method-level implementation not on root (plan only).

## Implementer constraints for Wave-5u

- No residual/bulk MCP tools; no coverage flag writes from harness.
- Replace OPTIONS with static candidate methods only after token + org guard + owner-only evidence gates.
- Sanitise to status + optional `errorCode` only.
- Contract must justify non-mutating observation bodies/queries; block candidates that cannot be justified.
- Reconcile `invoiceReminderAssociations` singular DELETE vs error-taught `ids[]` form without inventing tools.
- PATCH collection meta-200 is never a bulk contract.
