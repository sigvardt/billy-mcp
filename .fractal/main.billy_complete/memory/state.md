---
name: state
desc: Current node state, verified review decisions, and open qualification work.
tags: [billy, coverage, review]
sources:
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
  - https://www.billy.dk/api/
created: 2026-07-29T09:56:00Z
updated: 2026-07-31T11:45:00Z
---

# state

## Current state

- Product `ui_recurring_invoices_list` ACCEPT (IR 186.8). FIX-VERIFY clean: no
  product fixes; lint pass; 1354 offline; live reconfirm + vision purge_verified.
  Uncommitted product ready for COMMIT.
- Coverage: implemented/contract 193; live/vision 9; API live 0; complete false.
- Docs fingerprint ETag `wcw4x9hqvu3603`, MD5 `8b94b0135c91fd15fe54ea33e088a4be`.
- Operator: grok-only; no live API.

## Verification

- Dual-session recurring path/h1/CTA; optional `/empty` unit-tested; vision purge_verified.
- UI-only discovery greened; no api_recurring_*; invoices recurringInvoiceId UI not greened.

## Review decisions (authoritative)

- Product `ui_recurring_invoices_list`: **ACCEPT**.
- Prior quotes/bank_accounts/invoices/products/clients/auth: **ACCEPT**.
- Overall completeness: **FAIL**.

## Open coverage work

1. COMMIT ui_recurring_invoices_list product.
2. Next UI shell after commit (next red discovery family research).
3. Residual/bulk offline red only; no live API methods.

## Live UI tools (9 rows)

- `ui_invoices_list`, `ui_products_list`, `ui_clients_list`, `ui_bank_accounts_list`,
  `ui_quotes_list`, `ui_recurring_invoices_list`
- discovery: invoices, products, customers, bank_accounts, quotes, recurring_invoices
- parity: contacts.list, invoices.list, products.list

## Evidence boundaries

- No invent `api_recurring_*`.
- No green invoices recurringInvoiceId UI from this shell.
- Interface read-back: second browser session only.
- Grok-only children (`--agent=grok`).

## References

- Plan: `plans/2026-07-31T11:19:32.906Z-186.8-ui_recurring_invoices_list.md`
- IR: `tmp/grok-review.md`
- Vision: `tmp/vision-records/ui_recurring_invoices_list.json`
- Wiki: `wiki/ui_recurring_invoices_list_shell.md`
