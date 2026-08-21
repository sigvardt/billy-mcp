---
name: ui_bills_update_open_shell
desc: Read-only bill edit form open shell (maps api.bills.update).
tags: [billy, ui, bills, update]
sources:
  - research172 dual bills edit form
  - plans/2026-08-01T23:51:32.461Z-186.72-ui_bills_update_open.md
created: 2026-08-02T00:00:00Z
updated: 2026-08-02T00:00:00Z
---

# ui_bills_update_open_shell

Read-only FastMCP tool `ui_bills_update_open` opens a bill edit form for the authenticated Billy UI session.

## Contract

- Path class: `/:org_slug/bills/:id/edit` (not list, not `/bills/new`, not read-only detail).
- Soft-navigates from read detail `/:org_slug/bills/:id` to `/edit` when needed.
- Never submits Opdater / Godkend / Slet / Træk / Upload / Registrer betaling.
- Dual-session live qualification with SPA-seeded disposable draft bill (nested line: accountId, taxRateId, description, amount; no paymentDate).
- Maps `api.bills.update` with parity `form_open_only`.
- Distinct from `ui_bills_list`, `ui_bills_create_open`, and `ui_bills_get_open`.

## Egress

Reuses committed browser path_allow on `api.billysbilling.com` for GET/POST/DELETE `/v2/bills` and GET `/v2/taxRates`. No live API token. No egress expansion in this product.

## Evidence

- research172 dual update_form_ready on edit path
- Live: `tests/live/test_ui_bills_update_open.py`
- Vision record: owner-only frames purged; durable non-sensitive review under node tmp vision-records
