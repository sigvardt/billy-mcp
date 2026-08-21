---
name: wave_fives_research94_independent_review
title: Research94 and offline auth pre-submit product independent review
desc: Grok independent review of research94 and the merged offline auth credential pre-submit product on root tip a9c7a9b. Accepts research and offline product only. Completeness remains fail. No coverage greening.
tags: [billy, auth, credentials, login, research, review, grok, offline]
sources:
  - https://www.billy.dk/api/
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
  - wiki/auth_credentials_pre_submit_research.md
  - coverage/status.json
  - coverage/api_v2_manifest.yaml
  - coverage/ui_workflows_manifest.yaml
  - src/billy_mcp/browser.py
  - src/billy_mcp/credentials.py
  - src/billy_mcp/config.py
  - src/billy_mcp/models.py
  - src/billy_mcp/server.py
created: 2026-07-31T00:57:00Z
updated: 2026-07-31T00:58:00Z
---

# Research94 and offline auth pre-submit product independent review

## Authority

This page is the durable, non-sensitive independent review for Grok research94
and the merged offline auth credential pre-submit product on root tip
`a9c7a9b`. Owner-only scratch holds the full evidence bundle under
`.fractal/main.billy_complete/tmp/grok-review.md` (review94),
`grok-research.md` (research94), docs/probe/login JSON artifacts.

This is not a completeness claim. It does not green residual, bulk, special
live, or UI rows.

## Verdicts

| Claim | Result |
| --- | --- |
| Research94 (docs, residual/bulk unauth gates, login label, bulk-delete form hint) | **ACCEPT as research only** |
| Offline product: opaque credential references + `auth_login_start` / `auth_login_wait` with submit labels `Log in` / `Log ind` | **ACCEPT offline only** |
| Coverage honesty (184 implemented + contract_tested, 0 live, 0 vision, complete false) | **PASS** |
| Residual 29 / bulk 92 / UI 339 | remain red |
| Overall completeness | **FAIL** |

## Product ACCEPT bounds

Accepted offline behaviour:

- Empty-input tools only; no secrets or selectors in MCP models.
- Signature-first login transition on `https://mit.billy.dk/login`.
- Exact submit labels `Log in` and `Log ind` (page title `Login` is not a
  submit label).
- Headless forced; reviewed browser egress; page closed after the transition.
- Fail-closed `AUTH_REQUIRED`, `UI_CHANGED`, `EGRESS_DENIED`, `BILLY_ERROR`.
- Unit/contract proof with fake resolver and page seams.

Not accepted:

- Live password submit, post-login UI, org picker, token bootstrap, TOTP,
  CAPTCHA challenge DOM, vision verification, residual/bulk tools, or
  completeness.

## Programme blockers (unchanged)

1. Dedicated non-production Billy organisation and `BILLY_API_TOKEN`.
2. Wave-5u residual/bulk real methods stay **BLOCK BEFORE NETWORK** until a
   reviewed non-persistence proof exists. Empty bulk `ids[]` is **400**
   `INVALID_DELETE_ID_ARRAY`; server documents
   `DELETE /{resource}?ids[]=…`.
3. Live proof or correction of `GET /user/organizations` (docs path; unauth
   **404**) versus `GET /organizations` (unauth **401**).
4. Full headless UI parity with DOM assertions, independent read-back, cleanup,
   and non-sensitive vision records.

## Official docs fingerprint (independent re-fetch)

| Field | Value |
| --- | --- |
| URL | https://www.billy.dk/api/ |
| ETag | `wcw4x9hqvu3603` |
| Body MD5 | `8b94b0135c91fd15fe54ea33e088a4be` |
| Body bytes | 147934 |
| Webhooks | 0 mentions |

Inventory lock metadata may still cite an older CDN ETag/MD5; Supports and
classification are unchanged.

## Related pages

- Research freeze: [[auth_credentials_pre_submit_research]]
- Residual ranking: [[wave_fives_residual_specials_research]]
- Wave-5u contract: [[wave5u_method_probe_contract]]
- Prior research IR: [[wave_fives_research93_independent_review]]
