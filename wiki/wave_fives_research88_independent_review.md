---
name: wave_fives_research88_independent_review
title: Research88 residual bulk live-gate independent review
desc: Independent Grok review of Research88 and Wave-5t plan baseline. ACCEPT as research only. Coverage remains 184/184/0/0 complete false. No product greening.
tags: [billy, api, residual, bulk, research, review, live-gate]
sources:
  - https://www.billy.dk/api/
  - https://api.billysbilling.com/v2
  - wiki/wave_fives_residual_specials_research.md
  - wiki/offline_write_probe_rules.md
  - coverage/status.json
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
  - "parent scratch: .fractal/main.billy_complete/tmp/grok-review.md (review88)"
created: 2026-07-30T20:32:00Z
updated: 2026-07-30T20:32:00Z
---

# Research88 residual bulk live-gate independent review

## Verdict

| Claim | Result |
| --- | --- |
| Research88 residual/bulk ranking | **ACCEPT** as research only |
| Official docs vs inventory honesty | **PASS** |
| Coverage after plan baseline | **PASS** honesty (184/184/0/0, `complete: false`) |
| Wave-5t plan boundaries | **ACCEPT** as planning only |
| Live / UI / vision / residual tools / bulk tools / completeness | **FAIL / not claimed** |

Required product fixes: **none** for research ACCEPT.

## Evidence

- Docs re-fetch: ETag `"wcw4x9hqvu3603"`, 147934 bytes, MD5 `8b94b0135c91fd15fe54ea33e088a4be` (byte-identical to Research88).
- Residual clear not-impl **29** confirmed; specials **6/6** offline; bulk **92** red; UI **339** red.
- Unauth sample probes match Research88: 405 false friends, bankPayments delete 405, transactions POST 401 + DELETE meta-200, associations ids[] error shape, `PUT /{res}/bulk` 401 candidate, PATCH empty plural meta-200 not a contract, webhooks 404.
- Commit reviewed: `23dae67` (wiki/memory/plan only; no coverage greening; no product tools).

## Programme blockers

1. Dedicated non-production `BILLY_API_TOKEN` + organisation identity required for residual/bulk live work.
2. Wave-5t harness leaf RESEARCH failed on Grok authentication; harness product files not on root until a successful leaf run merges.
3. UI credentials still required for interface qualification.

Full review scratch: `.fractal/main.billy_complete/tmp/grok-review.md`.
