---
name: ui_account_groups_not_applicable
title: Account groups API UI parity not applicable
desc: Dual-session research143 freeze — no equivalent mit.billy.dk workflow for accountGroups API parity; soft-empty paths match nonsense; NA accepted.
tags: [billy, ui, parity, accountGroups, not_applicable]
sources:
  - https://www.billy.dk/api/
  - https://mit.billy.dk/
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
  - coverage/ui_workflows_manifest.yaml
  - wiki/ui_geo_cities_not_applicable.md
  - wiki/ui_currencies_locales_not_applicable.md
  - wiki/ui_account_natures_balance_modifiers_not_applicable.md
created: 2026-08-01T04:45:00Z
updated: 2026-08-01T04:45:00Z
---

# Account groups API UI parity not applicable

## Decision

UI parity rows for dual-proved `accountGroups` API families are
**`not_applicable`** with machine-readable evidence code
`GEO_UI_NO_EQUIVALENT_WORKFLOW` (same absence class as geo/currency/accountNatures NA).

Design allows UI parity `not_applicable` only when Billy exposes **no equivalent
UI workflow**. Dual independent headless sessions on the dedicated
non-production organisation support that classification for:

- `accountGroups` (all seven parity ops: get, list, create, update, delete,
  bulk_save, bulk_delete)

Peer freezes: [[ui_geo_cities_not_applicable]],
[[ui_currencies_locales_not_applicable]],
[[ui_account_natures_balance_modifiers_not_applicable]].

## Dual-session evidence (non-sensitive)

| Observation | Result |
| --- | --- |
| Sessions | Two independent ephemeral profiles → READY |
| Soft seeds `accountGroups`, `account-groups` | soft-empty SPA chrome only (body length class 127, empty h1) |
| Nonsense path control | **same** soft-empty class |
| Typed contrast shells | settings accounting (multi-section including Kontoplan), settings VAT (Momssatser multi-resource), settings company, daybooks editor, bank accounts, products dual-ok |

Scratch dual summary (owner tmp, not git):
`research143_residual_parity_dual.json`.

## Inventory contract

| Field | Value |
| --- | --- |
| `parity_status` | `not_applicable` |
| `tool_name` | empty (no `ui_account_groups_*` tools) |
| Flags | discovered, implemented, contract_tested, live_tested, vision_verified all true |
| `vision_evidence` | null (no retained frames) |
| `qualification.not_applicable_decision` | `accepted` |
| `qualification.sessions` | `dual_independent_ephemeral` |
| `qualification.evidence_ref` | `research143_account_groups_dual` |

## Contrast with annual reports

`ui.discovery.annual_reports` keeps **`not_applicable` rejected**: nav label
Årsrapporter and route family exist (Upsedasse on the test org is inaccessibility,
not absence). See [[ui_annual_reports_inaccessible]].

## Related surfaces that are not this freeze

| Surface | Why not greened as accountGroups |
| --- | --- |
| Settings Regnskab / Kontoplan | Multi-section accounts surface; deferred dual-count for `accounts.list` |
| Soft `productPrices` seeds | Soft-empty only; product create form is a real surface → **reject NA** |
| Settings company | Organization settings surface; defer organizations parity |
| Bankkonti / Afstemning | Bank shells exist; bankPayments/bankLines binding unproven |
| Soft `taxRates` seeds | Momssatser multi-resource panel is a real surface |

## Non-claims

- Does not invent UI tools for account groups.
- Does not green productPrices, organizations, bankPayments, bankLines, accounts,
  taxRates, or daybooks.list.
- Does not green API bulk rows or change API `live_tested` (stays false,
  `out_of_scope_by_user`).
- Does not set `coverage/status.json` complete true.
