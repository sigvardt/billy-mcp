---
name: state
desc: Current node state, verified review decisions, and open qualification work.
tags: [billy, coverage, review]
sources:
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
  - https://www.billy.dk/api/
created: 2026-07-29T09:56:00Z
updated: 2026-07-31T11:20:00Z
---

# state

## Current state

- Product `ui_quotes_list` ACCEPT (IR 186.7). FIX-VERIFY clean: no product fixes;
  lint + 1346 offline + live reconfirm. Uncommitted product ready for COMMIT.
- Coverage: implemented/contract 192; live/vision 8; API live 0; complete false.
- Docs fingerprint ETag `wcw4x9hqvu3603`, MD5 `8b94b0135c91fd15fe54ea33e088a4be`.
- Operator: grok-only; no live API.

## Verification

- Dual-session quotes path/h1/CTA; empty `/quotes/empty` accepted; vision purge_verified.
- UI-only discovery greened; no api_quotes_*; recurring_invoices still red.

## Review decisions (authoritative)

- Product `ui_quotes_list`: **ACCEPT**.
- Prior bank_accounts/invoices/products/clients/auth: **ACCEPT**.
- Overall completeness: **FAIL**.

## Open coverage work

1. COMMIT ui_quotes_list product.
2. Next UI shell after commit (recurring_invoices list shell research).
3. Residual/bulk offline red only; no live API methods.

## Live UI tools (8 rows)

- `ui_invoices_list`, `ui_products_list`, `ui_clients_list`, `ui_bank_accounts_list`, `ui_quotes_list`
- discovery: invoices, products, customers, bank_accounts, quotes
- parity: contacts.list, invoices.list, products.list

## Evidence boundaries

- No invent `api_quotes_*`.
- No green invoices quoteId UI or recurring_invoices from quotes shell alone.
- Interface read-back: second browser session only.
- Grok-only children (`--agent=grok`).

## References

- Plan: `plans/2026-07-31T11:01:51.621Z-186.7-ui_quotes_list.md`
- IR: `tmp/grok-review.md`
- Vision: `tmp/vision-records/ui_quotes_list.json`
- Wiki: `wiki/ui_quotes_list_shell.md`
