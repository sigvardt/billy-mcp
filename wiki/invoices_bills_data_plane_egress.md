---
name: invoices_bills_data_plane_egress
title: Invoices and bills browser GET data plane
desc: Scoped browser path_allow for Billy SPA invoices and bills list GET (research168).
tags: [billy, ui, invoices, bills, egress]
sources:
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
  - https://www.billy.dk/api/
  - coverage/browser_egress.yaml
created: 2026-08-01T21:50:00Z
updated: 2026-08-01T21:50:00Z
---

# Invoices and bills browser GET data plane

## Contract

Host `api.billysbilling.com` stays `browser_action: path_allow`.

Allowed for the headless Billy SPA (prefix GET only):

| path | methods | notes |
| --- | --- | --- |
| `/v2/invoices` | GET | covers list and `/summary` |
| `/v2/bills` | GET | covers list and `/summary` |

## Explicit non-claims

- No new UI tool (`ui_invoices_get_open` / `ui_bills_get_open` not producted)
- Does not green `ui.parity.invoices.get` or `ui.parity.bills.get`
- Does not open POST/PUT/DELETE on invoices or bills
- Does not open `POST /v2/invoices/…/emails` (special invoice email stays red)
- Not API live verification (`live_tested` remains false with out-of-scope policy)

## Qualification notes

Research168 dual-session TEMP path_allow proved `GET /v2/invoices` +
`GET /v2/invoices/summary` and `GET /v2/bills` + `GET /v2/bills/summary` succeed
without `ERR_BLOCKED_BY_CLIENT`. Empty-org list shells remain valid
(`Ingen fakturaer` / `Ingen udgifter`). Detail get-open stays deferred until a
disposable seed yields dual `detail_ready`.

Existing list tools `ui_invoices_list` and `ui_bills_list` keep their chrome-only
contracts; this egress only unblocks SPA data-plane settle under the allowlist.
