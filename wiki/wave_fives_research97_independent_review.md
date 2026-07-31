---
name: wave_fives_research97_independent_review
title: Wave-5 research97 independent review
desc: Independent Grok review of Research97 residual/bulk/login evidence and merged Research96 harness fixtures. ACCEPT research + infrastructure only; bulk open/closed class encode not present; completeness FAIL; no coverage greening.
tags: [billy, review, research, wave5u, residual, bulk, infrastructure, ui]
sources:
  - https://www.billy.dk/api/
  - https://api.billysbilling.com/v2
  - https://mit.billy.dk/
  - wiki/wave_fives_residual_specials_research.md
  - wiki/wave5u_method_probe_contract.md
  - coverage/api_v2_manifest.yaml
  - coverage/ui_workflows_manifest.yaml
  - coverage/status.json
  - src/billy_mcp/live_probe.py
  - tests/unit/test_live_probe.py
  - "parent scratch: .fractal/main.billy_complete/tmp/grok-research.md (research97)"
  - "parent scratch: .fractal/main.billy_complete/tmp/grok-review.md (review97)"
created: 2026-07-31T00:15:00Z
updated: 2026-07-31T00:15:00Z
---

# Wave-5 research97 independent review

## Verdicts

| Claim | Result |
| --- | --- |
| Research97 docs/residual/bulk/login evidence | **ACCEPT as research only** |
| Wiki residual research97 section | **ACCEPT as research promotion** |
| Research96 residual + bulk canonical fixtures on root tip `1b06773` | **ACCEPT as infrastructure only** |
| research95 form-matrix harness on root | **ACCEPT as infrastructure only** |
| Research97 bulk open/closed fixtures for all 92 bulk rows | **NOT PRESENT** (30-resource sample only; not product) |
| Residual/bulk product tools | **FAIL / correctly absent** |
| UI / live / vision | **FAIL / not claimed** |
| Coverage honesty | **PASS** (`complete: false`, 184/184/0/0) |
| Overall completeness | **FAIL** |

## Independent evidence summary

- Official docs https://www.billy.dk/api/ : ETag `"wcw4x9hqvu3603"`, 147934 bytes, MD5 `8b94b0135c91fd15fe54ea33e088a4be` (byte-identical to research97).
- Residual fixtures: exact **29** inventory ids; **25×405**, **2×401** (transactions create/update), **2×200** meta-only deletes; all `permits_real_method_network=False`.
- Bulk-delete: empty `ids[]` → **400** `INVALID_DELETE_ID_ARRAY` with server form `DELETE /contacts?ids[]=123&ids[]=456`; JSON body rejected; bankPayments/users/organizations/salesTaxReturns bulk empty → **405**.
- Bulk-save empty: open resources **401**; residual false-friends + files **405**.
- No-token `GET /user/organizations` → **404**; `/organizations` → **401**; garbage token → **401** `OAUTH_INVALID_ACCESS_TOKEN` (auth-first).
- Cities list unauth requires `countryId` (**400** `OTHER`).
- Login EN/DA: submit **`Log in`** / **`Log ind`**; Danish needs Playwright locale + Accept-Language; no credential submit; captcha iframe 0.
- `pytest tests/unit/test_live_probe.py`: **17 passed**.
- Coverage false-completeness and repository policy checks passed.
- No `BILLY_API_TOKEN` on runner.

## Non-claims

Does not green residual **29**, bulk **92**, specials live, or UI **339**. Does not authorise residual/bulk tools from unauth probes. Does not rewrite docs path for `GET /user/organizations` offline. Does not freeze all-92 bulk open/closed classes from the 30-resource research97 sample. Does not ACCEPT any new `ui_*` product from the in-flight login-surface research child.

## Scratch evidence (owner-only)

- `.fractal/main.billy_complete/tmp/grok-review.md` (review97 full report)
- `.fractal/main.billy_complete/tmp/write-probes-review97.json`
- `.fractal/main.billy_complete/tmp/ui-login-dom-review97.json`
- `.fractal/main.billy_complete/tmp/billy-api-docs-review97.html`
