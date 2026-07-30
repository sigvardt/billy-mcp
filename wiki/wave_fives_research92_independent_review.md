---
name: wave_fives_research92_independent_review
title: Research92 independent review
desc: Independent Grok review of research92 and tip auth credential pre-submit research freeze. Accepts research only; programme remains incomplete.
tags: [billy, review, research, auth, credentials, coverage]
sources:
  - https://www.billy.dk/api/
  - .fractal/main.billy_complete/tmp/grok-research.md
  - .fractal/main.billy_complete/tmp/grok-review.md
  - wiki/auth_credentials_pre_submit_research.md
  - coverage/status.json
  - coverage/api_v2_manifest.yaml
  - src/billy_mcp/browser.py
  - src/billy_mcp/server.py
created: 2026-07-31T00:20:00Z
updated: 2026-07-31T00:20:00Z
---

# Research92 independent review

## Verdict

**ACCEPT research92 and the tip research freeze as research only.**  
**FAIL product completeness, live/UI qualification, residual/bulk, and any green claim.**

| Claim | Result |
| --- | --- |
| Official docs fingerprint vs research92 | **ACCEPT** (ETag `wcw4x9hqvu3603`, MD5 `8b94b0135c91fd15fe54ea33e088a4be`) |
| Login signature + offline `auth_status` | **ACCEPT** credential-absent only |
| Wiki pre-submit research freeze | **ACCEPT** as research boundary |
| Pre-submit product tools on tip | **FAIL / not present** |
| Residual 29 + bulk 92 red honesty | **PASS** |
| Coverage `complete: false`, 184/184/0/0 | **PASS** honesty |
| Overall programme | **FAIL** |

Full scratch report: `.fractal/main.billy_complete/tmp/grok-review.md` (review92).

## Evidence highlights

- Independent docs re-fetch byte-identical to research92; inventory lock MD5
  still drifts only (`hsisik4g9p3603` / `c2efda0ee4cf9cf200e14910c5fc6996`).
- Unauth probes: empty `ids[]` → **400** `INVALID_DELETE_ID_ARRAY`;
  `GET /user/organizations` → **404**; residual closed POST → **405**;
  transactions POST and bulk PUT → **401**.
- Live headless `auth_status` → `AUTH_REQUIRED` on Danish login; submit is
  `button[data-cy=login-button]` (`Log ind`); `button[type=submit]` count 0.
- Tip `b7f226a` freezes wiki/plan/memory only; no `coverage/*` or product greening.
- UI **339** all red; specials offline live-false; no vision.

## Required before product green

1. Dedicated non-production API token + organisation (and browser credential
   references outside git) before any live submit or residual/bulk networking.
2. Keep residual/bulk **BLOCK BEFORE NETWORK** until non-persistence proof.
3. Live-prove or correct `GET /user/organizations` before special live flip.
4. After pre-submit product merge: independent Grok product IR; still no UI
   coverage green from offline plumbing alone.
