---
name: ui_attachments_get_create_update_delete_not_applicable
title: Attachments get create update delete UI parity not applicable
desc: Dual-session research185 freeze — no equivalent mit.billy.dk get-detail, join-form create, update-form, or delete-chrome workflow for residual attachments ops; list stays dual-count green on Bilag; exact NA for get/create/update/delete only.
tags: [billy, ui, parity, attachments, not_applicable, research185]
sources:
  - https://www.billy.dk/api/
  - https://mit.billy.dk/
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
  - coverage/ui_workflows_manifest.yaml
  - wiki/ui_uploads_list_shell.md
  - wiki/ui_files_list_get_not_applicable_research184.md
  - wiki/ui_products_get_update_delete_not_applicable.md
created: 2026-08-02T13:40:00Z
updated: 2026-08-02T13:40:00Z
---

# Attachments get create update delete UI parity not applicable

## Decision

UI parity rows for dual-proved residual **attachments get, create, update, and
delete** API operations are **`not_applicable`** with machine-readable evidence
code `GEO_UI_NO_EQUIVALENT_WORKFLOW` (same absence class as products residual NA
research176 and files list/get research184).

Design allows UI parity `not_applicable` only when Billy exposes **no equivalent
UI workflow**. Dual independent headless sessions on the dedicated
non-production organisation support that classification for **exact** ops:

- `api.attachments.get`
- `api.attachments.create`
- `api.attachments.update`
- `api.attachments.delete`

**Not** greened by this freeze:

- `api.attachments.list` — dual-counted as [[ui_uploads_list_shell]] (research184)
- `api.files.create` / `api.special.files_upload` — upload-surface open dual-count on Bilag
- `api.files.list` / `api.files.get` — separate NA [[ui_files_list_get_not_applicable_research184]]
- `api.attachments.bulk_save` / `bulk_delete` — external-contract bulk freeze
- `ui.discovery.annual_reports` — org inaccessible (NA rejected)

Peer freezes: [[ui_products_get_update_delete_not_applicable]],
[[ui_files_list_get_not_applicable_research184]], [[ui_uploads_list_shell]].

## Dual-session evidence (non-sensitive)

| Observation | Result |
| --- | --- |
| Sessions | Two independent ephemeral profiles → READY |
| Soft `/:org_slug/attachments` | soft-empty dual (nav chrome only) |
| Bilag `/:org_slug/uploads` | h1 Bilag dual; SPA hits `/v2/attachments` dual; files hits 0 dual |
| Slet / Gem / tbody / click candidates | 0 dual (no get/update/delete chrome) |
| Vedhæft join-form | 0 dual |
| Upload surface | already greened as files.create / special.files_upload open only — not attachments.create |
| Env `BILLY_API_TOKEN` | unused |
| Profiles | purged dual |

Scratch dual summary (owner tmp, not git):
`research185_focus_dual.json`.

## Inventory contract

| Field | Value |
| --- | --- |
| `parity_status` | `not_applicable` |
| `tool_name` | empty (no ui_attachments_get/create/update/delete tools) |
| Flags | discovered, implemented, contract_tested, live_tested, vision_verified all true |
| `vision_evidence` | null (no retained frames) |
| `qualification.not_applicable_decision` | `accepted` |
| `qualification.sessions` | `dual_independent_ephemeral` |
| `qualification.evidence_ref` | `research185_attachments_get_create_update_delete_dual` |
| Scope | exact `api.attachments.get` / `create` / `update` / `delete` only |

## Contrast with list and upload create

- List is the list op dual-counted on Bilag (`ui_uploads_list`) — not get-by-id detail.
- Binary upload open is `files.create` / `special.files_upload` — not an
  attachments.create join form binding `owner` + `file` fields from the API docs.
- Do not dual-count Bilag upload as `attachments.create`.

## Contrast with annual reports

`ui.discovery.annual_reports` keeps **`not_applicable` rejected**: nav label
exists (inaccessibility, not absence). See [[ui_annual_reports_inaccessible]].

## API lane note

Offline `api.attachments.get/create/update/delete` tools and contract tests are
unchanged. `live_tested` stays false with `out_of_scope_by_user`. No live API
traffic.

Official docs fingerprint at research: ETag `wcw4x9hqvu3603`, MD5
`8b94b0135c91fd15fe54ea33e088a4be` (unchanged).
