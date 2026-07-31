---
name: state
desc: Current node state, verified review decisions, and open qualification work.
tags: [billy, coverage, review]
sources:
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
  - https://www.billy.dk/api/
created: 2026-07-29T09:56:00Z
updated: 2026-07-31T12:27:10Z
---

# state

## Current state

- Continue mode iter 11 from clean tip `7429657` (suppliers product already committed).
- Coverage: implemented/contract 195; live/vision 11; API live 0; complete false.
- Docs fingerprint ETag `wcw4x9hqvu3603`, MD5 `8b94b0135c91fd15fe54ea33e088a4be`.
- Operator: grok-only; no live API; no running children.

## Verification

- Last product: `ui_suppliers_list` dual-session + vision purge_verified (ACCEPT).
- Offline baseline at tip: 1368 passed class (reconfirm in EXECUTE).
- Live baseline: 11 UI discovery/parity rows green.

## Review decisions (authoritative)

- Product `ui_suppliers_list`: **ACCEPT** (committed 186.10).
- Prior products_import/recurring/quotes/bank/clients/products/invoices/auth: **ACCEPT**.
- Overall completeness: **FAIL**.

## Open coverage work

1. Next UI shell: purchases maps to `/:org_slug/bills` (h1 `Køb`); dual live + vision.
2. Then balances and uploads discovery shells.
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

## Prepare (iter 11)

- Parent `main`: already up to date; no merge commit.
- No running children. Historical child tips: product already on root (`auth_status`, wave5t/u wiki) or scaffold-only; no child merges this iteration.
- Uncommitted: memory/state.md only (SYNC continue note).

## Research (iter 11)

- research110 freeze: `ui_bills_list` for `ui.discovery.purchases` → `/:org_slug/bills` h1 `Køb` CTA `Opret køb`; dual match; docs fingerprint unchanged; brief `tmp/grok-research.md`.

## Plan (iter 11)

- Plan: `plans/2026-07-31T12:13:15.985Z-186.11-ui_bills_list.md` — product `ui_bills_list` for `ui.discovery.purchases` + shell-open `ui.parity.bills.list`; root-only; dual live+vision.

## Execute (iter 11)

- Producted `ui_bills_list` (models/browser/server/tests/coverage/wiki).
- Bills signature uses first h1 (multi-h1 shell).
- Offline 1376 pass; live dual + vision purge_verified.
- Coverage live/vision 13; complete false.
- Ready for REVIEW.

## Independent review (iter 11)

- Product `ui_bills_list`: **ACCEPT** (tmp/grok-review.md).
- Overall completeness: **FAIL** (expected).
- No product blockers; proceed FIX-VERIFY/COMMIT.

## FIX-VERIFY (iter 11)

- IR product ACCEPT; no required fixes applied.
- Lint pass; offline 1376; live bills reconfirm pass; vision purge_verified.
- Coverage live/vision 13; complete false.
- Ready for COMMIT.
