---
name: wave_fives_research89_independent_review
title: Research89 and Wave-5t harness independent review
desc: Independent Grok review of Research89 residual/bulk reconfirmation and the root-integrated Wave-5t live-gate harness. ACCEPT research and infrastructure only; completeness FAIL; no coverage greening.
tags: [billy, review, research, wave5t, residual, bulk, infrastructure]
sources:
  - https://www.billy.dk/api/
  - https://api.billysbilling.com/v2
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
  - wiki/wave_fives_residual_specials_research.md
  - wiki/offline_write_probe_rules.md
  - coverage/status.json
  - coverage/api_v2_manifest.yaml
  - "parent scratch: .fractal/main.billy_complete/tmp/grok-review.md (review89)"
  - "parent scratch: .fractal/main.billy_complete/tmp/grok-research.md (research89)"
created: 2026-07-30T20:55:00Z
updated: 2026-07-30T21:03:00Z
---

# Research89 and Wave-5t harness independent review

## Verdict

| Claim | Result |
| --- | --- |
| Research89 residual/bulk reconfirm | **ACCEPT** as research only |
| Root coverage honesty (184/184/0/0, complete false) | **PASS** |
| Wave-5t live-gate harness | **ACCEPT as infrastructure/research only** |
| UI discovery fallback product | **not ready** |
| Residual/bulk tools, live, vision, completeness | **FAIL / not claimed** |

Full reproducible detail: parent scratch
`.fractal/main.billy_complete/tmp/grok-review.md` (review89).

## Docs fingerprint (independent)

| Field | Value |
| --- | --- |
| URL | https://www.billy.dk/api/ |
| ETag | `"wcw4x9hqvu3603"` |
| Bytes | 147934 |
| MD5 | `8b94b0135c91fd15fe54ea33e088a4be` |
| vs Research89 | Byte-identical |

## Harness boundaries and integration

The review covered these four child product files, then root integrated them
without source changes in merge commit `7571cec`:

- `src/billy_mcp/live_probe.py`
- `scripts/run_live_probe.py`
- `tests/live/test_live_probe.py`
- `tests/unit/test_live_probe.py`

Fail-closed no-token/no-network; token path requires matching non-production org guard; evidence outside repository; observations are **OPTIONS-only** and always `contract_qualified: false`. Matrix is exact residual **29** + bulk **92** (inventory ID match). Does **not** green coverage. Does **not** re-prove method-level 401/405 residual gates. Does **not** cover special `GET /user/organizations` (still open live risk per Research89).

## Open programme blockers

1. Live token + dedicated non-production organisation designation.
2. UI credentials / session for post-login parity and vision.
3. Live prove or correct `GET /v2/user/organizations` (unauth 404 vs docs + offline special).
4. Keep residual/bulk red after the clean-archive focused run (**10 passed, 1
   opt-in live skip**) and root integration; the harness is not a qualification
   substitute.

## Related

- Residual ranking: [[wave_fives_residual_specials_research]]
- Research88 IR: [[wave_fives_research88_independent_review]]
- Probe rules: [[offline_write_probe_rules]]
- UI login surface: [[billy_ui_discovery_brief]]
