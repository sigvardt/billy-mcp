---
name: ui_organizations_writes
title: UI organizations update writes
desc: Ticketed ui_organizations_update preview and execute tools, fail-closed company-phone allowlist, and live-slot wait.
tags: [billy, ui, organizations, writes, tickets]
sources:
  - wiki/ui_write_ticket_protocol.md
  - wiki/ui_settings_company_open_shell.md
  - radio:D5136C2E
created: 2026-08-16T14:30:00Z
updated: 2026-08-16T14:35:00Z
---

# UI organizations update writes

Ticketed Billy interface write for the company / Virksomhed panel on
`/:org_slug/settings`. Preview writes nothing. Execute accepts only
`confirmation_ticket`. The UI lane never calls `https://api.billysbilling.com/v2`.

Root wires `register_ui_organization_write_tools(server, ui_write_protocol)`.
This family fills that function. Coverage row `ui.parity.organizations.update`
stays red until root greens it after a live MCP proof.

## Tools

| Tool | Input | Effect |
| --- | --- | --- |
| `ui_organizations_update_preview` | `{phone}` only, `extra=forbid` | Binds the phone change and issues a ticket. No browser. No HTTP. |
| `ui_organizations_update_execute` | `{confirmation_ticket}` only | Consumes the ticket, then calls an optional submit hook. |

Bound target is `settings_company`. Expected effect is
`{action: update, resource: organization, surface: settings_company, field: phone}`.
Tickets expire in at most five minutes and are single-use.

Qualify through FastMCP `call_tool`. `BrowserRuntime` is not the pass proof.

## Fail closed

Allowlist: `phone` (Telefon on the company panel). Restore the original value
after a live submit.

Preview input is `{phone}` only (`extra=forbid`). Blank or whitespace-only
phone is rejected. Closed fields never appear on the schema, so they fail
as a validation error before a ticket is issued:

- users / Brugere
- access tokens / Adgangsnøgler
- subscription / Abonnement
- VAT / Moms / filings
- payments
- owners / Tilføj ejer
- `name` and `registrationNo` (not reversible enough for this family)

Do not invent `ui_annual_*` or `ui_organizations_create_*`. Create stays
`not_applicable` on [[ui_organizations_create_not_applicable]].

A production server with no submit hook returns `VALIDATION_ERROR` and does
**not** consume the ticket. Root's `create_server` wires the register call
without a submit hook, so execute stays inert until a live hook is attached.

After merge, parent must update the durable CUD gate that currently asserts
zero `ui_*_preview` / `ui_*_execute` tools. Do not green
`ui.parity.organizations.update` until a live MCP proof exists.

## Cleanup

Live submit is blocked by parent radio `D5136C2E`. Contacts holds the current
slot. Offline ticket tests are implemented. No company field has been changed.

When root radios a live slot to this family:

1. Unique tagged phone value only.
2. FastMCP preview then execute.
3. Independent second UI session read-back.
4. Four-state capture: initial, filled, submitted, restored.
5. Restore the original phone. Fail `CLEANUP_FAILED` if restore does not land.
6. Purge raw frames. Store only a non-sensitive vision record.

Never leave company settings changed.

## Tests

- Offline: `tests/unit/test_ui_organizations_writes.py` (preview no-submit,
  execute once, replay, expiry, wrong-tool mismatch, fail-closed fields).
- Live: `tests/live/test_ui_organizations_writes.py` waits for the slot and
  must not click `Gem ændringer` until that go-ahead exists.
