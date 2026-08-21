---
name: ui_residual_soft_empty_not_applicable_research183
title: Residual soft-empty UI parity not applicable (research183)
desc: Dual-session research183 freeze — 50 non-bulk residual API ops have no dedicated mit.billy.dk workflow; soft routes empty dual; greened parents stay exclusive.
tags: [billy, ui, parity, not_applicable, research183, residual]
sources:
  - https://www.billy.dk/api/
  - https://mit.billy.dk/
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
  - coverage/ui_workflows_manifest.yaml
  - coverage/status.json
created: 2026-08-02T12:20:00Z
updated: 2026-08-02T12:20:00Z
---

# Residual soft-empty UI parity not applicable (research183)

## Decision

Fifty non-bulk UI parity rows are **`not_applicable`** with evidence code
`GEO_UI_NO_EQUIVALENT_WORKFLOW` after dual independent headless sessions on the
dedicated non-production organisation.

Official docs fingerprint (unchanged): MD5 `8b94b0135c91fd15fe54ea33e088a4be`,
ETag `wcw4x9hqvu3603`.

## Exact freeze set (50)

| Family | API ops |
| --- | --- |
| daybookBalanceAccounts | get, list, create, update, delete |
| bankLines | get, list, create, update, delete |
| bankPayments | get, list, create, update, delete |
| bankLineMatches | get, list, create, update, delete |
| bankLineSubjectAssociations | get, list, create, update, delete |
| postings | get, list, create, update |
| salesTaxAccounts | get, list, create, update, delete |
| salesTaxRules | get, list, create, update, delete |
| salesTaxMetaFields | get, list, create, update, delete |
| salesTaxPayments | get, list, create, update |
| salesTaxReturns | get, update only (list stays tool-green) |

Bulk `*_save` / `*_delete` for these families stay external-contract red.

## Dual evidence

- Dedicated soft routes (camel and kebab) render soft-empty SPA chrome only
  (body length class **138** dual; no real h1).
- Global nav may expose a false-positive **Opret** control count; that is not
  dedicated create chrome for these resources.
- Seeded daybook detail opens dual and shows only daybook-transaction create
  chrome (**Tilføj kassekladdelinje** / **Ingen postering valgt**); no
  Saldo/Balance/Konti markers for daybookBalanceAccounts.
- Bank accounts list (**Bankkonti**) and bank reconciliation harvest path remain
  greened and are **not** bankLines/bankPayments/matches surfaces.
- Transactions list (**Posteringer**) remains greened for **transactions.***
  only — not postings.*
- Settings VAT / Momsangivelser remain greened for taxRates/rulesets list and
  salesTaxReturns.list only — not residual sales-tax account/rule/meta/payment
  CRUD or salesTaxReturns get/update form chrome (detail soft inputs_n **0**).

No `BILLY_API_TOKEN`. Disposable daybook seed cleaned dual. Profiles purged.

## Dual-count bans

| Greened parent | Must not absorb residual ops |
| --- | --- |
| daybooks / daybookTransactions create | daybookBalanceAccounts.* |
| bank accounts list / bank reconciliation open | bankLines.*, bankPayments.*, bankLineMatches.*, bankLineSubjectAssociations.* |
| transactions list / create | postings.* |
| settings VAT open | salesTaxAccounts.*, salesTaxRules.*, salesTaxMetaFields.* |
| vat declarations list | salesTaxPayments.*; salesTaxReturns.get/update |

## Deferred / stay red

- attachments ×5 and files ×3 — Bilag greened; pure NA rejected without separate
  dual-count policy
- annual_reports — Upsedasse dual; org inaccessible (NA rejected)
- bulk 92 ambiguous rows — external-contract freeze

## Qualification shape

| Field | Value |
| --- | --- |
| parity_status | not_applicable |
| tool_name | empty |
| discovered / implemented / contract_tested / live_tested / vision_verified | true |
| vision_evidence | null |
| qualification.kind | ui_not_applicable |
| qualification.not_applicable_decision | accepted |
| qualification.sessions | dual_independent_ephemeral |
| evidence_code | GEO_UI_NO_EQUIVALENT_WORKFLOW |
| research_id | research183 |

Peer freezes: [[daybook_transaction_lines_not_applicable_research182]],
[[ui_accounts_get_create_update_delete_not_applicable]].
