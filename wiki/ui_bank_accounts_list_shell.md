---
name: ui_bank_accounts_list_shell
title: UI bank accounts list shell open
desc: Read-only headless ui_bank_accounts_list contract for Billy bank accounts list shell open only.
tags: [billy, ui, bank-accounts, headless]
sources:
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
  - https://www.billy.dk/api/
created: 2026-07-31T10:50:00Z
updated: 2026-07-31T10:50:00Z
---

# UI bank accounts list shell open

## Contract

Tool `ui_bank_accounts_list` opens the authenticated Billy bank accounts list
shell on `mit.billy.dk` under path class `/:org_slug/bank-accounts`.

Success fields (non-PII only):

- `path_class`: `/:org_slug/bank-accounts` (query params allowed on the real URL)
- `heading`: `Bankkonti`
- `connect_bank_action_visible`: CTA `Forbind til bank` is present (never clicked)
- `shell_markers_present`: shared shell markers when visible

Input is empty. Callers must reach READY via `auth_login_start` /
`auth_login_wait` first. Organisation slug comes only from the session URL or
the outside-git UI identity file.

## Explicit non-claims

- No bankAccounts API tool (`api_bank_accounts_*` must not exist)
- No connect-bank or import-transactions actions
- No greening of `ui.parity.bankLines.*`, bankPayments, or bankLineMatches
- No live API read-back
- Bank reconciliation is a separate discovery track

## Qualification notes

Dual independent headless sessions prove DOM classification. Vision review
covers list-surface frames only; durable record is non-sensitive with
`purge_verified` after frame purge. Inventory row
`ui.discovery.bank_accounts` must not embed API filter schemas while greened.

Official docs have no `bankAccounts` resource. API `live_tested` remains false
under user-scoped qualification.
