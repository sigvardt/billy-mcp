---
name: daybook_transaction_lines_not_applicable_research182
title: daybookTransactionLines non-bulk UI not applicable (research182)
desc: Dual-session freeze that dedicated daybookTransactionLines workflows are absent; lines remain embedded on daybook detail only.
tags: [billy, ui, daybookTransactionLines, not_applicable, research182]
sources:
  - https://www.billy.dk/api/
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
  - .fractal/main.billy_complete/tmp/research182_focus_dual.json
  - .fractal/main.billy_complete/tmp/grok-research.md
created: 2026-08-02T11:30:00Z
updated: 2026-08-02T11:30:00Z
---

# daybookTransactionLines non-bulk UI not applicable (research182)

## Decision

`api.daybookTransactionLines.get|list|create|update|delete` map to UI
`not_applicable` with evidence code `GEO_UI_NO_EQUIVALENT_WORKFLOW`.

## Dual evidence (non-production org)

- Daybook detail `/:org_slug/daybooks/:id` opens with embedded
  **Tilføj kassekladdelinje** and **Ingen postering valgt**.
- Dedicated routes (`daybook-transaction-lines`, `daybookTransactionLines`,
  seeded id paths) soft-empty (body length class 138 dual).
- No dedicated list/get/create/update/delete chrome dual.

## Dual-count ban

Embedded **Tilføj kassekladdelinje** is already greened as
`ui_daybook_transactions_create_open` → `api.daybookTransactions.create` only.
It must not also green any `daybookTransactionLines.*` product row.

Bulk daybookTransactionLines ops stay red under the external-contract bulk freeze.

## Related product (same package)

`ui_transactions_create_open` maps `api.transactions.create` as
`create_chrome_open_only` on Posteringer list (**Ny postering**), distinct from
`ui_transactions_list`.
