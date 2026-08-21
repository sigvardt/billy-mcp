---
name: ui_bank_reconciliation_open_shell
title: UI bank reconciliation open shell
desc: Read-only headless ui_bank_reconciliation_open contract for Billy Afstemning shell open only.
tags: [billy, ui, bank-reconciliation, afstemning, headless]
sources:
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
  - https://www.billy.dk/api/
created: 2026-07-31T14:10:00Z
updated: 2026-07-31T14:10:00Z
---

# UI bank reconciliation open shell

## Contract

Tool `ui_bank_reconciliation_open` opens the authenticated Billy bank
reconciliation (Afstemning) shell on `mit.billy.dk` under path class
`/:org_slug/bank_accounts/:id/sync` (underscore `bank_accounts`).

Success fields (non-PII only):

- `path_class`: `/:org_slug/bank_accounts/:id/sync`
- `heading`: observed h1 when present, else empty string
- `empty_content_shell`: true when no h1 and no table/grid (current test org)
- `afstemning_nav_visible`: Afstemning nav label present
- `shell_markers_present`: shared shell markers when visible

Input is empty. Callers must reach READY via `auth_login_start` /
`auth_login_wait` first. Organisation slug comes only from the session URL or
the outside-git UI identity file. Account id is harvested from the Afstemning
nav `href` only; callers never supply it.

## Explicit non-claims

- No `api_bank_accounts_*`, `api_reconciliation_*`, or `api_afstemning_*` tools
- No connect-bank, import-transactions, or match/write actions
- No greening of `ui.parity.bankLines.*`, bankLineMatches, or bankPayments
- No re-greening of `ui.discovery.bank_accounts` / `ui_bank_accounts_list`
- Does not accept hyphen list path `bank-accounts` or h1 `Bankkonti` as success
- No live API read-back

## Qualification notes

Dual independent headless sessions prove DOM classification. Empty content
shell is a valid success state for the dedicated test organisation. Vision
review covers recon-surface frames only; durable record is non-sensitive with
`purge_verified` after frame purge. Inventory row
`ui.discovery.bank_reconciliation` is greened for shell open only.

Official docs have no `bankAccounts` or reconciliation resource. API
`live_tested` remains false under user-scoped qualification.
