---
name: ui_bills_list_shell
title: UI bills list shell open
desc: Read-only headless ui_bills_list contract for Billy bills (purchases / Køb) list shell open only.
tags: [billy, ui, bills, purchases, headless]
sources:
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
  - https://www.billy.dk/api/
created: 2026-07-31T12:20:00Z
updated: 2026-07-31T12:20:00Z
---

# UI bills list shell open

## Contract

Tool `ui_bills_list` opens the authenticated Billy bills list shell on
`mit.billy.dk` under path class `/:org_slug/bills`.

Success fields (non-PII only):

- `path_class`: `/:org_slug/bills` (query params allowed on the real URL)
- `heading`: `Køb`
- `create_action_visible`: CTA `Opret køb` is present (never clicked)
- `shell_markers_present`: shared shell markers when visible

Input is empty. Callers must reach READY via `auth_login_start` /
`auth_login_wait` first. Organisation slug comes only from the session URL or
the outside-git UI identity file.

Inventory mapping: design discovery family `purchases` maps to this bills
route. There is no working `/purchases` list shell.

## Explicit non-claims

- No invent `api_purchases_*` (docs use `/v2/bills` and `/v2/billLines`)
- No bill create/edit/approve/void/pay (never click `Opret køb` or
  `Håndter alle kladder`)
- No greening of bill create/update/delete/bulk or billLines parity rows beyond
  shell-open `ui.parity.bills.list`
- No greening of debtor/creditor balances or uploads discovery
- No live API read-back

## Qualification notes

Dual independent headless sessions prove DOM classification. Vision review
covers list-surface frames only; durable record is non-sensitive with
`purge_verified` after frame purge. Inventory rows greened by this shell:
`ui.discovery.purchases` and shell-open-only `ui.parity.bills.list`.

Offline `api.bills.*` clear CRUD is contract-green separately; API
`live_tested` remains false under user-scoped qualification.
