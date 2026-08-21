---
name: ui_debtor_balances_list_shell
title: UI debtor balances list shell open
desc: Read-only headless ui_debtor_balances_list contract for Billy debtor balances (Tilgodehavender) list shell open only.
tags: [billy, ui, debtor_balances, headless]
sources:
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
  - https://www.billy.dk/api/
created: 2026-07-31T12:40:00Z
updated: 2026-07-31T12:40:00Z
---

# UI debtor balances list shell open

## Contract

Tool `ui_debtor_balances_list` opens the authenticated Billy debtor balances
list shell on `mit.billy.dk` under path class `/:org_slug/debtorbalance`.

Success fields (non-PII only):

- `path_class`: `/:org_slug/debtorbalance` (query params allowed on the real URL)
- `heading`: `Tilgodehavender`
- `create_action_visible`: CTA `Opret faktura` is present (never clicked)
- `shell_markers_present`: shared shell markers when visible

Input is empty. Callers must reach READY via `auth_login_start` /
`auth_login_wait` first. Organisation slug comes only from the session URL or
the outside-git UI identity file.

Inventory mapping: design discovery family `debtor_balances` maps to this
route. There is no official `/v2/debtorbalance` API resource.

## Explicit non-claims

- No invent `api_debtor_balances_*`
- No invoice create (never click `Opret faktura`)
- No greening of `ui.discovery.creditor_balances`
- No greening of `ui.parity.contactBalancePayments.*`,
  `contactBalancePostings.*`, or `balanceModifiers.*`
- No greening of uploads or receipt_inbox discovery
- No live API read-back

## Qualification notes

Dual independent headless sessions prove DOM classification. Vision review
covers list-surface frames only; durable record is non-sensitive with
`purge_verified` after frame purge. Inventory row greened by this shell:
`ui.discovery.debtor_balances` only (`list_shell_open_only`).

Related offline API families remain contract-tested separately where producted;
API `live_tested` remains false under user-scoped qualification.
