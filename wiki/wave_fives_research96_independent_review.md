---
name: wave_fives_research96_independent_review
title: Wave-5 research96 independent review
desc: Independent Grok review of Research96 residual/bulk form and path-class evidence plus root coverage honesty. ACCEPT research only; research96 harness encode not on tip; form-matrix infrastructure ACCEPT; completeness FAIL; no coverage greening.
tags: [billy, review, research, wave5u, residual, bulk, infrastructure]
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
  - "parent scratch: .fractal/main.billy_complete/tmp/grok-research.md (research96)"
  - "parent scratch: .fractal/main.billy_complete/tmp/grok-review.md (review96)"
created: 2026-07-31T23:45:00Z
updated: 2026-07-31T23:45:00Z
---

# Wave-5 research96 independent review

## Verdicts

| Claim | Result |
| --- | --- |
| Research96 docs/residual/bulk/login evidence | **ACCEPT as research only** |
| Wiki residual research96 section | **ACCEPT as research promotion** |
| research95 form-matrix harness on root | **ACCEPT as infrastructure only** |
| research96 residual-gate fixture encode | **NOT PRESENT** (plan only at tip `121f662`) |
| Residual/bulk product tools | **FAIL / correctly absent** |
| UI / live / vision | **FAIL / not claimed** |
| Coverage honesty | **PASS** (`complete: false`, 184/184/0/0) |
| Overall completeness | **FAIL** |

## Independent evidence summary

- Official docs https://www.billy.dk/api/ : ETag `"wcw4x9hqvu3603"`, 147934 bytes, MD5 `8b94b0135c91fd15fe54ea33e088a4be` (byte-identical to research96).
- Unauth probes: empty bulk `ids[]` → **400** `INVALID_DELETE_ID_ARRAY` with server form `DELETE /contacts?ids[]=123&ids[]=456`; synthetic `ids[]` → **200** meta-only; JSON body rejected; no-token `GET /user/organizations` → **404**; `/organizations` → **401**; garbage token → **401** `OAUTH_INVALID_ACCESS_TOKEN` on known and unknown paths (auth-first).
- Login EN/DA: submit **`Log in`** / **`Log ind`**; no credential submit; captcha iframe 0.
- `research88_candidates()`: 121 candidates exact inventory match; all `permits_real_method_network=False`.
- `pytest tests/unit/test_live_probe.py`: **12 passed**.
- No `BILLY_API_TOKEN` on runner.

## Non-claims

Does not green residual **29**, bulk **92**, specials live, or UI **339**. Does not authorise residual/bulk tools from unauth probes. Does not rewrite docs path for `GET /user/organizations` offline.

## Scratch evidence (owner-only)

- `.fractal/main.billy_complete/tmp/grok-review.md` (review96 full report)
- `.fractal/main.billy_complete/tmp/write-probes-review96.json`
- `.fractal/main.billy_complete/tmp/ui-login-dom-review96.json`
- `.fractal/main.billy_complete/tmp/billy-api-docs-review96.html`
