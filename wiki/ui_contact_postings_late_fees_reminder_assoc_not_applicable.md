---
name: ui_contact_postings_late_fees_reminder_assoc_not_applicable
title: Contact postings late fees reminder associations API UI parity not applicable
desc: Dual-session research144 freeze — no equivalent mit.billy.dk workflow for contactBalancePostings, invoiceLateFees, and invoiceReminderAssociations API parity; soft-empty paths match nonsense; NA accepted.
tags: [billy, ui, parity, contactBalancePostings, invoiceLateFees, invoiceReminderAssociations, not_applicable]
sources:
  - https://www.billy.dk/api/
  - https://mit.billy.dk/
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
  - coverage/ui_workflows_manifest.yaml
  - wiki/ui_geo_cities_not_applicable.md
  - wiki/ui_account_groups_not_applicable.md
created: 2026-08-01T05:20:00Z
updated: 2026-08-01T05:20:00Z
---

# Contact postings late fees reminder associations API UI parity not applicable

## Decision

UI parity rows for dual-proved join and meta API families below are
**`not_applicable`** with machine-readable evidence code
`GEO_UI_NO_EQUIVALENT_WORKFLOW` (same absence class as geo and accountGroups NA).

Design allows UI parity `not_applicable` only when Billy exposes **no equivalent
UI workflow**. Dual independent headless sessions on the dedicated
non-production organisation support that classification for:

- `contactBalancePostings` (six parity ops: get, list, create, update, bulk_save,
  bulk_delete)
- `invoiceReminderAssociations` (seven parity ops including singular delete)
- `invoiceLateFees` (six parity ops: get, list, create, update, bulk_save,
  bulk_delete)

Peer freezes: [[ui_geo_cities_not_applicable]],
[[ui_account_groups_not_applicable]],
[[ui_account_natures_balance_modifiers_not_applicable]],
[[ui_contact_balance_payments_not_applicable]] (contactBalance**Payments**, not
Postings), [[ui_contact_persons_not_applicable]].

## Dual-session evidence (non-sensitive)

| Observation | Result |
| --- | --- |
| Sessions | Two independent ephemeral profiles → READY |
| Soft seeds for the three families (camel and kebab forms where seeded) | soft-empty SPA chrome only (body length class 127, empty h1) |
| Nonsense path control | **same** soft-empty class |
| List and settings shell markers (Rykker, Morarente, Gebyr, Tilknytning) | dual false on invoices, balances, and settings invoicing shells |
| Typed contrast shells | invoices, balances, settings, daybooks editor, bank recon, products, uploads dual-ok |

Scratch dual summaries (owner tmp, not git):
`research144_residual_parity_dual.json`, `research144_shell_markers.json`.

## Inventory contract

| Field | Value |
| --- | --- |
| `parity_status` | `not_applicable` |
| `tool_name` | empty (no dedicated UI tools for these families) |
| Flags | discovered, implemented, contract_tested, live_tested, vision_verified all true |
| `vision_evidence` | null (no retained frames) |
| `qualification.not_applicable_decision` | `accepted` |
| `qualification.sessions` | `dual_independent_ephemeral` |
| `qualification.evidence_ref` | `research144_contact_invoice_join_dual` |

## Contrast with annual reports

`ui.discovery.annual_reports` keeps **`not_applicable` rejected**: nav label
Årsrapporter and route family exist (Upsedasse on the test org is inaccessibility,
not absence). See [[ui_annual_reports_inaccessible]].

## Related surfaces that are not this freeze

| Surface | Why not greened as this package |
| --- | --- |
| Soft `productPrices` + `/products/new` | Product create form is a real surface → **reject NA** |
| bankLineMatches / bankLineSubjectAssociations soft seeds | Bank recon shell greened → **reject pure NA** |
| daybookBalanceAccounts soft seeds | Daybooks editor greened → **reject pure NA** |
| salesTax* / taxRateDeduction soft seeds | Momssatser multi-resource greened → **reject pure NA** |
| Nested invoiceLines / billLines / contactPersons | Nested under parent list shells → not pure absence |

## Non-claims

- Does not invent UI tools for these families.
- Does not green productPrices, bankLine*, daybookBalanceAccounts, salesTax*,
  taxRateDeductionComponents, nested line resources, organizations, or accounts.
- Does not green bulk API tools or API `live_tested` cells.
- Does not close offline API write gaps outside the UI NA classification.
- Does not mark annual reports not applicable.
