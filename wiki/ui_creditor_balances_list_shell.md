---
name: ui_creditor_balances_list_shell
title: UI creditor balances list shell open
desc: Read-only headless ui_creditor_balances_list contract for Billy creditor balances (Skyldige udgifter) list shell open only.
tags: [billy, ui, creditor_balances, headless]
sources:
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
  - https://www.billy.dk/api/
created: 2026-07-31T12:55:00Z
updated: 2026-07-31T12:55:00Z
---

# UI creditor balances list shell open

## Contract

Tool `ui_creditor_balances_list` opens the authenticated Billy creditor balances
list shell on `mit.billy.dk` under path class `/:org_slug/creditorbalance`.

Success fields (non-PII only):

- `path_class`: `/:org_slug/creditorbalance` (query params allowed on the real URL)
- `heading`: `Skyldige udgifter`
- `create_action_visible`: CTA `Opret køb` is present (never clicked)
- `shell_markers_present`: shared shell markers when visible

Input is empty. Callers must reach READY via `auth_login_start` /
`auth_login_wait` first. Organisation slug comes only from the session URL or
the outside-git UI identity file.

Inventory mapping: design discovery family `creditor_balances` maps to this
route. There is no official `/v2/creditorbalance` API resource.

## Explicit non-claims

- No invent `api_creditor_balances_*`
- No bill create (never click `Opret køb`)
- No greening of `ui.discovery.uploads` or `receipt_inbox`
- No greening of `ui.parity.contactBalancePayments.*`,
  `contactBalancePostings.*`, or `balanceModifiers.*`
- No re-scope of `ui.discovery.debtor_balances`
- No live API read-back

## Qualification notes

Dual independent headless sessions prove DOM classification. Vision review
covers list-surface frames only; durable record is non-sensitive with
`purge_verified` after frame purge. Inventory row greened by this shell:
`ui.discovery.creditor_balances` only (`list_shell_open_only`).

Related offline API families remain contract-tested separately where producted;
API `live_tested` remains false under user-scoped qualification.
