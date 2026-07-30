---
name: wave_fives_research91_independent_review
desc: Independent Grok review of research91 and offline typed auth_status at tip cf38b5c; overall completeness FAIL.
tags: [billy, review, auth, research, coverage]
sources:
  - https://www.billy.dk/api/
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
  - src/billy_mcp/browser.py
  - src/billy_mcp/models.py
  - src/billy_mcp/server.py
  - coverage/status.json
  - wiki/wave5u_method_probe_contract.md
  - wiki/wave5t_ui_auth_discovery.md
created: 2026-07-30T21:55:00Z
updated: 2026-07-30T21:55:00Z
---

# wave_fives_research91_independent_review

Independent Grok review of research91 and the typed `auth_status` merge.
This page is **not** completeness and does not green coverage.

## Verdicts

| Claim | Result |
| --- | --- |
| Research91 (docs + residual/bulk + login signature) | **ACCEPT as research** |
| Offline `auth_status` (credential-absent) | **ACCEPT**; UI inventory stays red |
| Root coverage honesty 184/184/0/0, `complete: false` | **PASS** |
| Residual 29 / bulk 92 / UI 339 product completeness | **FAIL** |
| Overall completeness | **FAIL** |

## Official docs

Primary source [Billy API v2 documentation](https://www.billy.dk/api/) re-fetched
for this review: HTTP 200, ETag `"wcw4x9hqvu3603"`, 147934 bytes, MD5
`8b94b0135c91fd15fe54ea33e088a4be` (byte-identical to research91). Inventory lock
MD5 drift only. Webhooks still absent from the official page.

## auth_status (offline)

Registered tool `auth_status` opens only the fixed headless root
`https://mit.billy.dk/`, requires exact `/login`, and matches:

- `input[type=email][name=email]`
- `input[type=password][name=password]`
- `input[type=checkbox][name=remember]`
- `button[data-cy=login-button]` with trimmed text in `{Log in, Log ind}`

It must not use `button[type=submit]` (live DOM has no type attribute and no
wrapping form). Success is only `AUTH_REQUIRED`. Drift returns `UI_CHANGED`.
No generic browser MCP controls. Merge must not alter `coverage/*`.

Independent credential-absent live check returned `AUTH_REQUIRED` with Danish
submit label `Log ind`.

## Residual / bulk / live blockers

- All residual clear **29** and bulk **92** remain red.
- Wave-5u contract keeps every real-method candidate **BLOCK BEFORE NETWORK**.
- Empty bulk `ids[]` returns **400** `INVALID_DELETE_ID_ARRAY` (not a no-op).
- Unauth `GET /user/organizations` is **404**; `GET /organizations` is **401**.
  Offline special still follows the docs path; live proof required later.
- Root live harness remains OPTIONS-only infrastructure and cannot qualify methods.

## Non-claims

No live_tested, vision_verified, UI parity, residual/bulk product tools, or
webhook API. No headed browser. No persistent business records from this review.
