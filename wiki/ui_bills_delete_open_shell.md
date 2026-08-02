---
name: ui_bills_delete_open_shell
desc: Read-only bill delete chrome open shell (maps api.bills.delete).
tags: [billy, ui, bills, delete]
sources:
  - research173 dual bills delete chrome
  - plans/2026-08-02T00:35:05.916Z-186.73-ui_bills_delete_open.md
created: 2026-08-02T00:40:00Z
updated: 2026-08-02T00:40:00Z
---

# ui_bills_delete_open_shell

Read-only FastMCP tool `ui_bills_delete_open` opens bill delete chrome for the authenticated Billy UI session.

## Contract

- Path class: `/:org_slug/bills/:id/edit` (not list, not `/bills/new`, not read-only detail alone).
- Soft-navigates from read detail `/:org_slug/bills/:id` to `/edit` when needed.
- Primary **Slet** present; click Slet once to open confirm (Slet ≥ 2 + **Annuller**).
- Dismiss with **Annuller** only. Never second Slet / permanent delete / Opdater / Godkend / Træk / Upload / Registrer betaling.
- Dual-session live qualification with SPA-seeded disposable draft bill (nested line: accountId, taxRateId, description, amount; no paymentDate).
- Maps `api.bills.delete` with parity `delete_chrome_open_only`.
- Distinct from `ui_bills_list`, `ui_bills_create_open`, `ui_bills_get_open`, and `ui_bills_update_open`.

## Egress

Reuses committed browser path_allow on `api.billysbilling.com` for GET/POST/DELETE `/v2/bills` and GET `/v2/taxRates`. No live API token. No egress expansion in this product.

## Evidence

- research173 dual delete_chrome_ready; confirm open + Annuller dismiss without bill loss
- Live: `tests/live/test_ui_bills_delete_open.py`
- Vision record: owner-only frames purged; durable non-sensitive review under node tmp vision-records
