---
name: state
desc: Current node state, verified review decisions, and open qualification work.
tags: [billy, coverage, review]
sources:
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
  - https://www.billy.dk/api/
created: 2026-07-29T09:56:00Z
updated: 2026-07-31T12:30:00Z
---

# state

## Current state

- Product `ui_products_import` ACCEPT (IR 186.9). FIX-VERIFY: egress generator
  live test_references fixed; lint pass; 1361 offline; live reconfirm + vision
  purge_verified. Uncommitted product ready for COMMIT.
- Coverage: implemented/contract 194; live/vision 10; API live 0; complete false.
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

1. COMMIT ui_products_import product.
2. Next UI shell after commit (suppliers / bills-Køb / balances / uploads).
3. Residual/bulk offline API reds only; no live API methods.


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

## Prepare notes (iteration 9 continue)

- Parent `main`: already fully contained in HEAD; merge no-op.
- 62 child branches still show commits ahead of `main.billy_complete`; none
  carry unmerged product worth integrating:
  - `ui_auth_status` product already on root and child is behind on src/tests.
  - Remaining ahead commits are fractal scaffolding, failed research leaves, or
    older wiki drafts superseded by root wiki.
  - Missing-on-root research wiki candidate
    (`ui_auth_credentials_login_organization_research_codex_fallback.md`) left
    unmerged; root already has auth credentials research pages.
- No child merges this PREPARE. No running children.
