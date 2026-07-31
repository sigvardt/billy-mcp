---
name: ui_financing_open_shell
desc: Read-only Billy financing landing shell contract (research116 freeze).
tags: [billy, ui, financing, discovery]
sources:
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
  - https://www.billy.dk/api/
created: 2026-07-31T14:40:00Z
updated: 2026-07-31T14:40:00Z
---

# ui_financing_open_shell

## Contract

| Field | Value |
| --- | --- |
| Tool | `ui_financing_open` |
| Coverage row | `ui.discovery.financing` |
| Path class | `/:org_slug/financing` |
| Heading | `Ansøg om erhvervslån` |
| Bank nav label | `Ansøg om lån` (observe) |
| Apply CTA | `Få et uforpligtende tilbud` (presence only; never click) |
| Input | empty (`extra=forbid`) |
| Success fields | `path_class`, `heading`, `apply_cta_observed`, `shell_markers_present` |
| parity_status | `shell_open_only` |

## Non-claims

- No official Billy API financing/loan resource. Do **not** invent
  `api_financing_*`, `api_loans_*`, `api_loan_applications_*`, or `api_froda_*`.
- Design §14.4: external financing apply/submit is not tested against production.
  This product is **read-only open** only.
- Never click apply/offer/consent/submit CTAs.
- Does not green `ui.discovery.bank_accounts` or `ui.discovery.bank_reconciliation`.
- Soft subpaths (`financing/apply`, …) and aliases (`loan`, `finance`, …) are not
  this tool's success path.
- API `live_tested` remains false with `out_of_scope_by_user`.

## Qualification

- Offline unit/model/server registration tests.
- Live dual independent browser sessions (no `BILLY_API_TOKEN`).
- Vision review record under tmp with `purge_verified: true` after frame purge.
