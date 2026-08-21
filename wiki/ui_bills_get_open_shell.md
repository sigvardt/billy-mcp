---
name: ui_bills_get_open_shell
desc: Read-only bill detail get-open shell (maps api.bills.get).
tags: [billy, ui, bills, get]
sources:
  - research170 dual bills detail
  - plans/2026-08-01T23:06:32.292Z-186.71-ui_bills_get_open.md
created: 2026-08-02T00:00:00Z
updated: 2026-08-02T00:00:00Z
---

# ui_bills_get_open_shell

Read-only FastMCP tool `ui_bills_get_open` opens a bill detail surface for the authenticated Billy UI session.

## Contract

- Path class: `/:org_slug/bills/:id` (not list, not `/bills/new`).
- List text-click may land on `/edit`; product soft-navigates to the read path.
- Never submits Gem / Godkend / Opdater / Slet / Træk.
- Dual-session live qualification with SPA-seeded disposable draft bill (nested line: accountId, taxRateId, description, amount; no paymentDate).
- Maps `api.bills.get` with parity `detail_open_only`.
- Distinct from `ui_bills_list` (list shell) and `ui_bills_create_open` (form open).

## Egress

Browser path_allow on `api.billysbilling.com` includes GET/POST/DELETE `/v2/bills` and GET `/v2/taxRates` for list settle and disposable seed/cleanup. No live API token.

## Evidence

- research170 dual detail_ready
- Live: `tests/live/test_ui_bills_get_open.py`
- Vision record: owner-only frames purged; durable non-sensitive review under node tmp vision-records
