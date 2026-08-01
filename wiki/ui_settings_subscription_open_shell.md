---
name: ui_settings_subscription_open_shell
desc: Read-only Billy Indstillinger Abonnement empty settings panel open (research134 freeze).
tags: [billy, ui, settings, subscription, abonnement, indstillinger, discovery]
sources:
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
  - https://www.billy.dk/api/
created: 2026-08-01T00:30:00Z
updated: 2026-08-01T00:30:00Z
---

# ui_settings_subscription_open_shell

## Contract

| Field | Value |
| --- | --- |
| Tool | `ui_settings_subscription_open` |
| Coverage row | `ui.discovery.settings_subscription` |
| Open sequence | hub `/:org_slug/settings` then observe-only click **Abonnement** |
| Success path class | `/:org_slug/settings` |
| Heading | `Indstillinger` |
| shell_kind | `settings_subscription` |
| Panel signature | empty content panel (no nonempty h2; no panel-only content markers) |
| Input | empty (`extra=forbid`) |
| Success fields | `path_class`, `heading`, `shell_kind`, `empty_panel` |
| parity_status | `shell_open_only` |

## Non-claims

- Soft seeds (`settings/abonnement`, `settings/billing`, `settings/plan`, …) are **not** sole success. Soft seed `settings/subscription` may dual-open empty panel but product uses hub+click.
- Company default, accounting Regnskab, invoicing Faktura, user Profil, VAT Momssatser, users Brugere, access-token Adgangsnøgler, and beta Betas panels are **not** success.
- Global chrome tokens (`Fakturering`, `Pro`) alone are **not** success markers.
- No official Billy API settings or subscription / plan CRUD resource. Do **not** invent `api_settings_*` or `api_subscription_*`.
- Never click write/billing CTAs (`Opgrader*`, Skift abonnement, Betal, Køb, `Opret*`, Gem*, Tilføj*, Slet, Upload).
- Does not green annual_reports, other settings_*, or prior shells.
- API `live_tested` remains false with `out_of_scope_by_user`.
- If Billy later fills Abonnement content, expect `UI_CHANGED` and re-freeze.

## Qualification

- Offline unit/model/server registration tests.
- Live dual independent browser sessions (no `BILLY_API_TOKEN`).
- Vision review record under tmp with `purge_verified: true` after frame purge.
