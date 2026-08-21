---
name: wave_fives_research95_independent_review
title: Wave-5 research95 independent review
desc: Independent Grok acceptance of research95 bulk-delete form-matrix findings and wiki promotions as research only; completeness remains failed; no residual/bulk product tools.
tags: [billy, research, review, residual, bulk, live-gate, auth]
sources:
  - https://www.billy.dk/api/
  - https://api.billysbilling.com/v2
  - https://mit.billy.dk/
  - coverage/status.json
  - coverage/api_v2_manifest.yaml
  - coverage/ui_workflows_manifest.yaml
  - wiki/wave5u_method_probe_contract.md
  - wiki/wave_fives_residual_specials_research.md
  - wiki/auth_credentials_pre_submit_research.md
  - src/billy_mcp/browser.py
  - src/billy_mcp/live_probe.py
  - ".fractal/main.billy_complete/tmp/grok-research.md (research95)"
  - ".fractal/main.billy_complete/tmp/grok-review.md (review95)"
created: 2026-07-31T00:20:00Z
updated: 2026-07-31T00:20:00Z
---

# Wave-5 research95 independent review

## Verdict

| Claim | Result |
| --- | --- |
| Research95 docs + residual/bulk form matrix | **ACCEPT as research only** |
| Wiki residual research95 section + Wave-5u bulk-delete form evidence | **ACCEPT as research promotion** |
| Root coverage honesty (184/184/0/0, `complete: false`) | **PASS** |
| Offline auth pre-submit product (`Log in` / `Log ind`) | **ACCEPT offline only** (prior review still holds) |
| Residual 29 / bulk 92 product tools | **FAIL / correctly absent** |
| UI discovery / live / vision | **FAIL / not claimed** |
| Wave-5u form-matrix harness encode on root | **Not present** (planned infrastructure only) |
| Completeness | **FAIL** |

Primary independent report (owner scratch):
`.fractal/main.billy_complete/tmp/grok-review.md` (review95).

## Independently verified facts

Official API page https://www.billy.dk/api/ re-fetched with ETag
`"wcw4x9hqvu3603"`, body MD5 `8b94b0135c91fd15fe54ea33e088a4be`, body
byte-identical to the research95 capture. No webhook API. Bulk save/delete
remain Supports flags only (**46** / **46**), with no bulk body or response
schema.

Unauthenticated API probes against `https://api.billysbilling.com/v2` reproduced
research95 with zero mismatches on the review matrix, including:

- empty bulk-delete `ids[]` / empty-array forms → **400**
  `INVALID_DELETE_ID_ARRAY` (error, not a no-op)
- synthetic non-empty `ids[]=<absent>` → **200** meta-only (not authenticated
  non-persistence or cleanup proof)
- residual closed POST **405**; transactions POST **401**; bankPayments delete
  **405**; docs path `GET /user/organizations` **404**; webhooks **404**

Headless login (no credentials, no submit): English title `Login` / submit
`Log in`; Danish title `Log ind` / submit `Log ind`; stable
`name=email|password|remember` and `button[data-cy=login-button]`. CAPTCHA
bootstrap flags alone are not `AUTH_INTERACTION_REQUIRED`.

Inventory honesty: API residual **29** and bulk **92** remain not implemented;
specials **6** offline only; UI **339** all red. Focused offline unit suite for
browser, config, and live_probe reported **45 passed**. live_probe matrix size
remains **121** with bulk-delete query names exactly `ids[]`, and no-token runs
skip without networking.

## Explicit non-claims

Unauthenticated **401**, **405**, meta-only **200**, OPTIONS **204**, empty
bulk **400**, and synthetic-id bulk **200** do not authorise residual or bulk
tools, live qualification, or coverage greening. Offline auth product ACCEPT
does not green UI inventory rows. Completeness remains failed until dedicated
non-production credentials, residual/bulk non-persistence proofs, full UI
parity, and vision records exist under the design gates.
