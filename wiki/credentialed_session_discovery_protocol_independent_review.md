---
name: credentialed_session_discovery_protocol_independent_review
title: Credentialed session discovery protocol independent review
desc: Independent Grok review99 of research99 and the documentation-only credentialed session discovery protocol; accepts research and wiki freeze only; completeness remains failed.
tags: [billy, auth, ui, discovery, review, grok, coverage]
sources:
  - https://www.billy.dk/api/
  - https://mit.billy.dk/
  - https://api.billysbilling.com/v2
  - wiki/credentialed_session_discovery_protocol.md
  - wiki/ui_login_surface_contract.md
  - .fractal/main.billy_complete/tmp/grok-research.md
  - .fractal/main.billy_complete/tmp/grok-review.md
  - coverage/status.json
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
created: 2026-07-31T00:55:00Z
updated: 2026-07-31T00:55:00Z
---

# Credentialed session discovery protocol independent review

## Verdict

**ACCEPT research99 as research. ACCEPT `wiki/credentialed_session_discovery_protocol.md` as research/contract documentation only. Completeness FAIL.**

The working-tree documentation slice freezes the headless credentialed discovery
runbook. It does not change source, tests, or coverage flags. It does not
observe a post-login page. It does not authorise residual, bulk, live, or vision
greening.

## Qualification-scope supersession

Review99 predated the controlling user-approved qualification policy. Its
references to a company API token and API read-back are therefore rejected for
future work: the policy explicitly prohibits live Billy API tests and
credentialed API qualification calls, while requiring a second interface path
or fresh browser session for interface read-back. This does not alter the
review's research-only verdict, coverage non-claims, or the need for dedicated
non-production **browser** credentials before post-login discovery.

Full review text (commands, probes, bounds): owner-only node scratch
`.fractal/main.billy_complete/tmp/grok-review.md` (review99).

## Independent reconfirmations

| Item | Result |
| --- | --- |
| Official docs https://www.billy.dk/api/ | ETag `wcw4x9hqvu3603`, 147934 bytes, MD5 `8b94b0135c91fd15fe54ea33e088a4be` (byte-identical to research99) |
| Webhooks | 0 official mentions |
| Headless EN/DA login | `https://mit.billy.dk/login`; labels `Log in` / `Log ind`; forms 0; no captcha iframe |
| Unauth org path | `GET /user/organizations` 404; `GET /organizations` 401 |
| Residual classes | 25×405; transactions POST/PUT 401; 2× meta-200 deletes |
| Coverage | 184 implemented + contract_tested; live 0; vision 0; UI 339 all red; `complete: false` |
| Protocol wiki | prerequisites, classification, fresh second-interface read-back, purge, no product invent |

## Explicit non-claims

- Not product ACCEPT for any new tool.
- Not live UI, vision, session restore, organisation selection, residual, or bulk qualification.
- Not completeness.
- Offline `auth_status` / `auth_login_start` / `auth_login_wait` remain offline ACCEPT only from earlier reviews.

## Soft notes

- Inventory lock metadata in `coverage/status.json` still cites an older official-docs ETag/MD5 (access drift only).
- TOTP is not a third named env key in current config; MFA stays a future discovery outcome.
- Parent commit of the protocol must remain wiki/memory documentation only.

## Related pages

- [[credentialed_session_discovery_protocol]]
- [[ui_login_surface_contract]]
- [[auth_credentials_pre_submit_research]]
- [[wave_fives_residual_specials_research]]
