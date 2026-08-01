---
name: ui_account_natures_balance_modifiers_not_applicable
title: Account natures and balance modifiers API UI parity not applicable
desc: Dual-session research142 freeze — no equivalent mit.billy.dk workflow for accountNatures/balanceModifiers API parity; soft-empty paths match nonsense; NA accepted.
tags: [billy, ui, parity, accountNatures, balanceModifiers, not_applicable]
sources:
  - https://www.billy.dk/api/
  - https://mit.billy.dk/
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
  - coverage/ui_workflows_manifest.yaml
  - wiki/ui_geo_cities_not_applicable.md
  - wiki/ui_currencies_locales_not_applicable.md
created: 2026-08-01T04:15:00Z
updated: 2026-08-01T04:15:00Z
---

# Account natures and balance modifiers API UI parity not applicable

## Decision

UI parity rows for dual-proved `accountNatures` and `balanceModifiers` API
families are **`not_applicable`** with machine-readable evidence code
`GEO_UI_NO_EQUIVALENT_WORKFLOW` (same absence class as geo/currency NA).

Design allows UI parity `not_applicable` only when Billy exposes **no equivalent
UI workflow**. Dual independent headless sessions on the dedicated
non-production organisation support that classification for:

- `accountNatures` (all six parity ops: get, list, create, update, bulk_save, bulk_delete)
- `balanceModifiers` (same six ops)

Peer freezes: [[ui_geo_cities_not_applicable]], [[ui_currencies_locales_not_applicable]].

## Dual-session evidence (non-sensitive)

| Observation | Result |
| --- | --- |
| Sessions | Two independent ephemeral profiles → READY |
| Soft seeds `account-natures`, `accountNatures`, `balance-modifiers`, `balanceModifiers` | soft-empty SPA chrome only (body length class 127, empty h1) |
| Nonsense path control | **same** soft-empty class |
| Typed contrast shells | settings accounting (Kontoplan markers), settings VAT (Momssatser), daybooks editor (`daybooks/new`), bank accounts (Bankkonti) dual-ok |

Scratch dual summary (owner tmp, not git):
`research142_residual_parity_dual.json`.

## Inventory contract

| Field | Value |
| --- | --- |
| `parity_status` | `not_applicable` |
| `tool_name` | empty (no `ui_account_natures_*` / `ui_balance_modifiers_*` tools) |
| Flags | discovered, implemented, contract_tested, live_tested, vision_verified all true |
| `vision_evidence` | null (no retained frames) |
| `qualification.not_applicable_decision` | `accepted` |
| `qualification.sessions` | `dual_independent_ephemeral` |
| `qualification.evidence_ref` | `research142_account_natures_balance_modifiers_dual` |

## Contrast with annual reports

`ui.discovery.annual_reports` keeps **`not_applicable` rejected**: nav label
Årsrapporter and route family exist (Upsedasse on the test org is inaccessibility,
not absence). See [[ui_annual_reports_inaccessible]].

## Related surfaces that are not this freeze

| Surface | Why not greened as these families |
| --- | --- |
| Settings Regnskab / Kontoplan | Multi-section; deferred dual-count for `accounts.list` only |
| Settings Momssatser | Multi-resource (rulesets + rates); deferred for `taxRates.list` |
| Bankkonti list | UI-only bank accounts shell; no `bankAccounts` API resource |
| Soft `bankPayments` / `bankLines` seeds | Soft-empty only; not producted as NA this freeze |

## Non-claims

- Does not invent UI tools for account natures or balance modifiers.
- Does not green API bulk rows or residual offline create/update for these families.
- Does not change API `live_tested` (stays false, `out_of_scope_by_user`).
- Does not dual-count accounts, taxRates, or daybooks.list.
- Does not set `coverage/status.json` complete true.
