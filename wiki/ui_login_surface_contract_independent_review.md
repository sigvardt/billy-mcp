---
name: ui_login_surface_contract_independent_review
title: UI login surface contract independent review
desc: Independent Grok review98 of research98 and the merged wiki-only UI login-surface contract; accepts documentation freeze only; completeness remains failed.
tags: [billy, ui, auth, login, review, grok, coverage]
sources:
  - https://www.billy.dk/api/
  - https://mit.billy.dk/
  - https://api.billysbilling.com/v2
  - wiki/ui_login_surface_contract.md
  - .fractal/main.billy_complete/tmp/grok-research.md
  - .fractal/main.billy_complete/tmp/grok-review.md
  - coverage/status.json
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
created: 2026-07-31T00:35:00Z
updated: 2026-07-31T00:36:00Z
---

# UI login surface contract independent review

## Verdict

**ACCEPT research98 as research. ACCEPT merged `wiki/ui_login_surface_contract.md` as research/contract documentation only. Completeness FAIL.**

The merge at tip `5e9cb61` is wiki-only (`wiki/ui_login_surface_contract.md` plus generated index). It does not change source, tests, or coverage flags. The documented decision matches independent observation: the credential-absent Billy login page is already the typed `auth_status` surface; a new `ui_*` login probe would be a duplicate and is rejected.

Full review text (commands, probes, bounds): owner-only node scratch
`.fractal/main.billy_complete/tmp/grok-review.md` (review98).

## Independent reconfirmations

| Item | Result |
| --- | --- |
| Official docs https://www.billy.dk/api/ | ETag `wcw4x9hqvu3603`, 147934 bytes, MD5 `8b94b0135c91fd15fe54ea33e088a4be` (byte-identical to research98) |
| Webhooks | 0 official mentions |
| Headless EN/DA login | `https://mit.billy.dk/login`; labels `Log in` / `Log ind`; forms 0; no captcha iframe |
| Unauth org path | `GET /user/organizations` 404; `GET /organizations` 401 |
| Coverage | 184 implemented + contract_tested; live 0; vision 0; UI 339 all red; `complete: false` |
| Residual / bulk tools | still absent; residual fixtures remain fail-closed |

## Explicit non-claims

- Not product ACCEPT for any new tool.
- Not live UI, vision, session restore, organisation selection, residual, or bulk qualification.
- Not completeness.
- Offline `auth_status` / `auth_login_start` / `auth_login_wait` remain offline ACCEPT only from earlier reviews.

## Review finding resolved

Review98 found that the contract still named the superseded `research97` relay
as its evidence authority. Root fix verification retargeted the contract to the
current research98 relay; no contract substance, tool, or coverage flag changed.

## Root follow-up verification

The citation-only fix passed `BILLY_TEST_MODE=commit` with **1304 passed, 1
deselected**. Ruff format/lint, Pyright, coverage false-completeness validation,
repository policy validation, and wiki lint for both knowledge stores also
passed. The review created no screenshot, frame, HAR, or trace; none was
retained in the repository. Review98's owner-only scratch records are the cited
documentation, DOM/probe summaries, and review report; unrelated historical
scratch archives are outside this review's evidence boundary.

## Related pages

- [[ui_login_surface_contract]]
- [[auth_credentials_pre_submit_research]]
- [[wave5u_method_probe_contract]]
