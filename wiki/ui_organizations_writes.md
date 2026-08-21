---
name: ui_organizations_writes
title: UI organizations update writes
desc: Ticketed company-phone preview and execute, empty restore, accept plus purge, preview remap.
tags: [billy, ui, organizations, writes, tickets]
sources:
  - wiki/ui_write_ticket_protocol.md
  - wiki/ui_settings_company_open_shell.md
  - radio:AD8966F2
  - radio:23709235
created: 2026-08-16T14:30:00Z
updated: 2026-08-18T06:26:00Z
---

# UI organizations update writes

Ticketed Billy interface write for the company / Virksomhed panel on
`/:org_slug/settings`. Preview writes nothing. Execute accepts only
`confirmation_ticket`. The UI lane never calls `https://api.billysbilling.com/v2`.

Root wires `register_ui_organization_write_tools` with the shared
`BrowserRuntime`. Coverage row `ui.parity.organizations.update` names
`ui_organizations_update_preview` after independent accept and purge.
Honesty 16 still keeps implemented, live_tested, and vision_verified
false. Discovery, list, and get stay on `ui_settings_company_open`.

## Tools

| Tool | Input | Effect |
| --- | --- | --- |
| `ui_organizations_update_preview` | `{phone, organization_id}` only, `extra=forbid` | Binds the phone change and issues a ticket. No browser. No HTTP. |
| `ui_organizations_update_execute` | `{confirmation_ticket}` only | Consumes the ticket, then calls the submit hook. |

Bound target is `settings_company`. Expected effect is
`{action: update, resource: organization, surface: settings_company, field: phone}`.
Tickets expire in at most five minutes and are single-use.

Qualify through FastMCP `call_tool`. `BrowserRuntime` is not the pass proof.

## Fail closed

Allowlist: `phone` (Telefon on the company panel). Restore the original value
after a live submit through a second ticket.

Preview input is `{phone, organization_id}` only (`extra=forbid`). Exact
empty phone is a deliberate clear. Whitespace-only phone is rejected.
Non-empty phone is trimmed. Closed fields never appear on the schema:

- users / Brugere
- access tokens / Adgangsnøgler
- subscription / Abonnement
- VAT / Moms / filings
- payments
- owners / Tilføj ejer
- `name` and `registrationNo` (not reversible enough for this family)

Do not invent `ui_annual_*` or `ui_organizations_create_*`. Create stays
`not_applicable` on [[ui_organizations_create_not_applicable]].

Do not green honesty on `ui.parity.organizations.update`. Accept plus
purge is recorded. Implemented, live_tested, and vision_verified stay
false on the honesty overlay.

## Phone dump

Read-only inspect helper
`src/billy_mcp/ui_writes/organizations_phone_dump.py` records
allowlisted tokens only. Live dump
`inspect-live-organizations-phone.json` (owner-local, not git):

- path `settings`, heading `indstillinger`
- company panel markers present
- phone field visible, input name class `phone`
- exact **Gem ændringer** count 1
- forbidden surface `none`
- `proved_phone_only=true`
- `phone_value_len=0`

`persist_allowed_from` follows the proved surface. Empty original is a
reversible clear (`23709235`). Restore uses a second ticket with
`phone=""`. Do not remake this dump.

Radio `D5136C2E` (contacts slot) is stale. `23709235` is the go-ahead
for empty-phone restore. Read-back is `input[name=phone]`, not page
text.

## Cleanup

Live FastMCP set plus empty restore is proved. Independent review
accepted `run_id=0937a009bf7e496ca2ce15a8af313868`. Frame folder is
gone. Vision record is `author=independent_review`,
`reviewer_verdict=accept`, `purge_verified=true`. Old live
`run_id=affdb4f98390481880e4bcd554ec4fd9` stays in assertion refs.

Never leave company settings changed. Never persist or radio the
original phone, organisation id, URLs, tokens, or screenshots.

## Tests

- Offline tickets: `tests/unit/test_ui_organizations_writes.py`.
- Empty-phone contract: `tests/unit/test_ui_organizations_empty_phone.py`.
- Dump keys: `tests/unit/test_ui_organizations_phone_dump.py`.
- Live dump: `tests/live/test_ui_organizations_phone_dump.py` (no save).
- Live FastMCP set plus empty restore: `tests/live/test_ui_organizations_writes.py`.
