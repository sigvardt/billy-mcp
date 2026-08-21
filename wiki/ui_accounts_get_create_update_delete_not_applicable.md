---
name: ui_accounts_get_create_update_delete_not_applicable
title: Accounts get create update delete UI parity not applicable
desc: Dual-session research178 freeze — no equivalent mit.billy.dk get/create/update/delete chrome for chart accounts; list stays tool-green on settings accounting; exact NA for get/create/update/delete only.
tags: [billy, ui, parity, accounts, not_applicable]
sources:
  - https://www.billy.dk/api/
  - https://mit.billy.dk/
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
  - coverage/ui_workflows_manifest.yaml
  - wiki/ui_settings_accounting_open_shell.md
created: 2026-08-02T07:45:00Z
updated: 2026-08-02T07:45:00Z
---

# Accounts get create update delete UI parity not applicable

## Decision

UI parity rows for dual-proved **accounts get, create, update, and delete** API
operations are **`not_applicable`** with machine-readable evidence code
`GEO_UI_NO_EQUIVALENT_WORKFLOW`.

Design allows UI parity `not_applicable` only when Billy exposes **no equivalent
UI workflow**. Dual independent headless sessions on the dedicated
non-production organisation support that classification for **exact** ops:

- `api.accounts.get`
- `api.accounts.create`
- `api.accounts.update`
- `api.accounts.delete`

**Not** greened by this freeze:

- `api.accounts.list` — greened as settings accounting shell
  ([[ui_settings_accounting_open_shell]] when present)
- `api.accounts.bulk_save` / `bulk_delete` — external-contract bulk freeze
- Soft-empty daybooks residual / users residual / invoiceLines
- Annual reports org inaccessible (NA rejected)

Peer freezes: [[ui_products_get_update_delete_not_applicable]],
[[ui_special_invoice_email_not_applicable]].

## Dual-session evidence (non-sensitive)

| Observation | Result |
| --- | --- |
| Sessions | Two independent ephemeral profiles → READY |
| Settings accounting panel | path `/:org_slug/settings`; Regnskab + Kontoplan dual (list shell) |
| Create CTAs Tilføj/Opret/Ny konto | 0 dual |
| Ret / row get-update | absent dual |
| Mere → Slet konto | absent dual |
| Soft `/accounts` and related | rewrite/soft only; no dedicated CRUD form dual |
| Env `BILLY_API_TOKEN` | unused (SPA session token capture only) |

Scratch dual summary (owner tmp, not git):
`research178_focus_dual.json`.

## Inventory contract

| Field | Value |
| --- | --- |
| `parity_status` | `not_applicable` |
| `tool_name` | empty (no ui_accounts_get/create/update/delete tools) |
| Flags | discovered, implemented, contract_tested, live_tested, vision_verified all true |
| `vision_evidence` | null (no retained frames) |
| `qualification.not_applicable_decision` | `accepted` |
| `qualification.sessions` | `dual_independent_ephemeral` |
| `qualification.evidence_ref` | `research178_accounts_get_create_update_delete_dual` |
| Scope | exact get/create/update/delete only |

## Contrast with list shell

The greened accounts list shell remains open-only on settings Regnskab/Kontoplan.
It must not be dual-counted as account get, create, update, or delete.
