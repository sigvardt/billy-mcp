---
name: ui_integrations_open_shell
desc: Read-only Billy integrations soft-empty shell classification (research124 freeze).
tags: [billy, ui, integrations, soft-empty, discovery]
sources:
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
  - https://www.billy.dk/api/
created: 2026-07-31T19:00:00Z
updated: 2026-07-31T19:00:00Z
---

# ui_integrations_open_shell

## Contract

| Field | Value |
| --- | --- |
| Tool | `ui_integrations_open` |
| Coverage row | `ui.discovery.integrations` |
| Path class | `/:org_slug/integrations` (optional query allowed if path stays integrations) |
| Heading | empty (not Fordele; not marketplace title) |
| Success kind | `soft_empty` (`dedicated_shell=false`, `same_shell_as_addons=false`) |
| Input | empty (`extra=forbid`) |
| Success fields | `path_class`, `shell_kind`, `dedicated_shell`, `same_shell_as_addons`, `heading`, `shell_markers_present` |
| parity_status | `soft_empty_shell_observed` |

## Non-claims

- Fordele hub (`/:org_slug/add-ons`, h1 `Fordele`, nav `Udforsk integrationer`) is **not** this tool. That row is `ui_addons_open`.
- Soft paths (`integration`, `apps`, `marketplace`, nested, `settings/*`) are **not** success.
- Marketing link **Se alle vores integrationer** targets `www.billy.dk/apps/` and is **never** navigated (outside app egress allowlist).
- No official Billy API integrations resource. Do **not** invent `api_integrations_*`.
- Never click partner CTAs (Install/Connect, Se alle, Opret adgangsnøgle, Kom i gang, …).
- Does not green inventory, settings_*, annual_reports, or re-green addons.
- API `live_tested` remains false with `out_of_scope_by_user`.

## Qualification

- Offline unit/model/server registration tests.
- Live dual independent browser sessions (no `BILLY_API_TOKEN`).
- Vision review record under tmp with `purge_verified: true` after frame purge.
