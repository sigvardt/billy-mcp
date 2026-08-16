---
name: state
desc: Current node state for the Billy MCP complete run.
tags: [billy, coverage, ui_writes]
sources:
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
  - https://www.billy.dk/api/
created: 2026-08-16T13:50:50Z
updated: 2026-08-16T13:50:50Z
---

## Now

Owner radio `96908DC6` is binding. The job is to finish the interface write lane and the MCP, then close under the owner scope. API live tests stay deferred. This is not a HOLD.

HEAD is `6f0303e` on `main.billy_complete`. Parent `main` and `origin/main` are already ancestors (fetch+merge: already up to date). No parent commits to take.

## Verified on HEAD

- `src/billy_mcp/server.py` registers 52 `ui_*` tools.
- Zero registered `ui_*` preview or execute submit tools.
- Every write-shaped UI tool is `*_open` / list / shell only.
- `coverage/status.json`: `complete` false; implemented/contract 528; UI live/vision 344; API live stays false.
- Official docs lock: MD5 `8b94b0135c91fd15fe54ea33e088a4be`, ETag `wcw4x9hqvu3603`.
- Coverage still treats many `form_open_only` / `delete_chrome_open_only` / `create_chrome_open_only` rows as implemented and live-tested. Owner says that is wrong for create/update/delete parity.

## Children

No running children. Three stale stopped descendants were retired and will not be continued:

- `main.billy_complete.auth_status_independent_review_codex_fallback`
- `main.billy_complete.wave5t_live_gate_harness`
- `main.billy_complete.wave5sb_files_upload_product`

157 historical child branches; 62 tips still have commits not on HEAD. None are mergeable product:

- `ui_auth_status`: child `9b89fa6` is not an ancestor. `browser.py` 376 vs HEAD 9572; `server.py` 177 vs 1194. HEAD already has `auth_status`, `auth_login_start`, `auth_login_wait`. Merge-tree is changed-in-both on all six product files. Merge would regress. Skip.
- Wiki-only (3): `wave5t_ui_auth_discovery` and `wave5u_method_probe_contract` already on HEAD (HEAD equal or longer). The Codex credentials fallback page is superseded by `wiki/auth_credentials_pre_submit_research.md`. Skip.
- Remaining 58: fractal scaffolding or review leaves only. Skip.

No child merge. No integration outbox.

## Research

Brief: `.fractal/main.billy_complete/tmp/grok-research.md`. Fingerprint: `tmp/research201-fingerprint.json`.

Official docs HTML moved (ETag `121myuqjdm53603`, MD5 `b4307fa281f8592d1cad7e9206e2d7de`) but only Next.js build id + Prismic ref. Resource TOC and `/v2/contacts` table unchanged. Do not re-lock MD5 this slice.

16 create/update/delete **parity** rows are open-only and still marked implemented + live. Zero UI preview/execute tools.

EXECUTE 190.1 landed the failing 16-row gate (captured), honesty, and `ui_writes` protocol stubs. Coverage: implemented 512, live/vision 328, contract 528, complete false. Offline suite 1675 passed. Next: commit skeleton, spawn seven Grok children. Contacts first live slot.

See `decisions.md` and `todo.md`.
