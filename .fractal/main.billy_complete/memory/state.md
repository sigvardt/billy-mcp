---
name: state
desc: Current node state, verified review decisions, and open qualification work.
tags: [billy, coverage, review]
sources:
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
  - https://www.billy.dk/api/
created: 2026-07-29T09:56:00Z
updated: 2026-07-31T12:10:00Z
---

# state

## Current state

- Product `ui_suppliers_list` IR **ACCEPT**; FIX-VERIFY clean (lint + 1368 offline + live reconfirm).
- Uncommitted product ready for COMMIT (iteration 186.10).
- Coverage: implemented/contract 195; live/vision 11; API live 0; complete false.
- Docs fingerprint ETag `wcw4x9hqvu3603`, MD5 `8b94b0135c91fd15fe54ea33e088a4be`.
- Operator: grok-only; no live API.

## Verification

- Dual-session suppliers path/h1/CTA; vision purge_verified true.
- Optional IR note fixed: `coverage/report.md` now reports live/vision counts.
- Offline: `scripts/test.sh` 1368 passed, 10 deselected.
- Live: `tests/live/test_ui_suppliers_list.py` passed on reconfirm.

## Review decisions (authoritative)

- Product `ui_suppliers_list`: **ACCEPT**.
- Prior products_import/recurring/quotes/bank/clients/products/invoices/auth: **ACCEPT**.
- Overall completeness: **FAIL**.

## Open coverage work

1. COMMIT ui_suppliers_list product.
2. Next UI shell: purchases maps to `/:org_slug/bills` (h1 `Køb`); then balances, uploads.
3. Residual/bulk offline API reds only; no live API methods.

## Live UI tools (11 rows)

- list/import shells greened through suppliers: invoices, products, clients,
  bank_accounts, quotes, recurring_invoices, products_import, suppliers

## Evidence boundaries

- No invent `api_suppliers_*`.
- No green purchases/bills from suppliers product.
- Interface read-back: second browser session only.
- Grok-only children (`--agent=grok`).

## References

- Plan: `plans/2026-07-31T11:55:41.116Z-186.10-ui_suppliers_list.md`
- IR: `tmp/grok-review.md`
- Vision: `tmp/vision-records/ui_suppliers_list.json`
- Wiki: `wiki/ui_suppliers_list_shell.md`
