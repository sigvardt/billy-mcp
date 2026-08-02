---
name: ui_files_list_get_not_applicable_research184
title: files.list and files.get UI not applicable (research184)
desc: Dual-session research184 freeze — api.files.list and api.files.get have no dedicated mit.billy.dk workflow; Bilag is attachments inventory not files list.
tags: [billy, ui, parity, not_applicable, research184, files]
sources:
  - https://www.billy.dk/api/
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
  - .fractal/main.billy_complete/tmp/research184_focus_dual.json
  - wiki/ui_uploads_list_shell.md
created: 2026-08-02T12:50:00Z
updated: 2026-08-02T12:50:00Z
---

# files.list and files.get UI not applicable (research184)

## Decision

| API id | UI parity | Decision |
| --- | --- | --- |
| `api.files.list` | `ui.parity.files.list` | `not_applicable` accepted |
| `api.files.get` | `ui.parity.files.get` | `not_applicable` accepted |

Evidence code: `GEO_UI_NO_EQUIVALENT_WORKFLOW`.

## Dual evidence (non-sensitive)

- Soft routes `/:org_slug/files` and `/:org_slug/filer` soft-empty dual (body_len
  138, empty h1).
- Greened Bilag `/:org_slug/uploads` SPA resource hits: **attachments** dual,
  **files** zero dual.
- Therefore Bilag must not dual-count as `files.list` or `files.get`.
- `files.create` dual-counts onto `ui_uploads_list` upload-surface open only
  (see [[ui_uploads_list_shell]]).
- No disposable records; profiles purged; no env API token.

## Explicit non-claims

- Does not green attachments residual get/create/update/delete.
- Does not green files bulk ops.
- Does not green annual_reports.
- API `live_tested` remains false with `out_of_scope_by_user`.

Official docs fingerprint at research: ETag `wcw4x9hqvu3603`, MD5
`8b94b0135c91fd15fe54ea33e088a4be` (unchanged).
