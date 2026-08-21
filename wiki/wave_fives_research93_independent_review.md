---
name: wave_fives_research93_independent_review
title: Research93 independent review
desc: Independent Grok review of research93 and pre-merge product scan. Accepts research only; rejects product merge on login submit-label regression; programme remains incomplete.
tags: [billy, review, research, auth, credentials, coverage, product]
sources:
  - https://www.billy.dk/api/
  - .fractal/main.billy_complete/tmp/grok-research.md
  - .fractal/main.billy_complete/tmp/grok-review.md
  - wiki/auth_credentials_pre_submit_research.md
  - coverage/status.json
  - coverage/api_v2_manifest.yaml
  - src/billy_mcp/browser.py
  - src/billy_mcp/server.py
created: 2026-07-31T00:35:00Z
updated: 2026-07-31T00:35:00Z
---

# Research93 independent review

## Verdict

**ACCEPT research93 and the research freeze refinements as research only.**  
**REJECT merge of `auth_credentials_pre_submit_product` until submit labels are fixed.**  
**FAIL product completeness, live/UI qualification, residual/bulk, and any green claim.**

| Claim | Result |
| --- | --- |
| Official docs fingerprint vs research93 | **ACCEPT** (ETag `wcw4x9hqvu3603`, MD5 `8b94b0135c91fd15fe54ea33e088a4be`) |
| Login signature on root (`Log in`\|`Log ind`) | **ACCEPT** credential-absent only |
| Wiki pre-submit research freeze (research93) | **ACCEPT** as research boundary |
| Pre-submit product tools on root tip | **FAIL / not present** |
| Child product tip `b508477` pre-merge | **REJECT** — `_LOGIN_SUBMIT_LABELS` uses `Login` instead of frozen `Log in` |
| Residual 29 + bulk 92 red honesty | **PASS** |
| Coverage `complete: false`, 184/184/0/0 | **PASS** honesty |
| Overall programme | **FAIL** |

Full scratch report: `.fractal/main.billy_complete/tmp/grok-review.md` (review93).

## Evidence highlights

- Independent docs re-fetch byte-identical to research93; inventory lock MD5
  still drifts only (`hsisik4g9p3603` / `c2efda0ee4cf9cf200e14910c5fc6996`).
- Unauth probes: empty `ids[]` → **400** `INVALID_DELETE_ID_ARRAY`;
  `GET /user/organizations` → **404**; residual closed POST → **405**;
  transactions POST and bulk PUT → **401**.
- Live headless login: `https://mit.billy.dk/login`, title `Login`, submit
  `button[data-cy=login-button]` text **`Log in`**, `button[type=submit]` count 0,
  captcha iframe 0. No credential submit.
- CAPTCHA product bootstrap flags remain noise, not `AUTH_INTERACTION_REQUIRED`.
- Root tip still has only `auth_status` with correct labels `Log in`|`Log ind`.
- Child product leaves coverage untouched (good) but regresses submit labels to
  `Login`|`Log ind` and tests teach `Login`. Real EN login would always
  `UI_CHANGED` after merge.
- UI **339** all red; specials offline live-false; no vision.

## Required before product merge or green

1. Child repair: restore `_LOGIN_SUBMIT_LABELS` and unit fixtures to exact
   `Log in` and `Log ind` only. Never accept title text `Login` as the button
   label.
2. Parent clean-archive review of the fixed scoped diff, then Grok product IR.
3. Dedicated non-production API token + organisation (and browser credential
   references outside git) before any live submit or residual/bulk networking.
4. Keep residual/bulk **BLOCK BEFORE NETWORK** until non-persistence proof.
5. Live-prove or correct `GET /user/organizations` before special live flip.
6. Do not green any UI inventory row from offline pre-submit plumbing alone.
