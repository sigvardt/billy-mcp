---
name: ui_organizations_create_not_applicable
desc: UI parity not_applicable freeze for api.organizations.create (research177 dual absence of org-create CTA).
tags: [billy, ui, organizations, not_applicable, parity]
sources:
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
  - https://www.billy.dk/api/
created: 2026-08-02T04:00:00Z
updated: 2026-08-02T04:00:00Z
---

# ui_organizations_create_not_applicable

## Contract

| Field | Value |
| --- | --- |
| UI row | `ui.parity.organizations.create` |
| API row | `api.organizations.create` |
| parity_status | `not_applicable` |
| tool_name | empty |
| evidence_code | `GEO_UI_NO_EQUIVALENT_WORKFLOW` |
| evidence_ref | `research177_organizations_create_dual` |
| sessions | `dual_independent_ephemeral` |

## Evidence (research177)

- Dual independent headless sessions on dedicated non-production org.
- Company/Virksomhed settings panel dual present (list/get/update dual-count on `ui_settings_company_open`).
- Create CTAs Opret/Ny/Tilføj virksomhed **0 dual**.
- Multi-org create workflow not present dual.
- Exact id only — does not NA list/get/update/bulk.

## Non-claims

- Does not change offline `api.organizations.create` tools/contract tests.
- API `live_tested` remains false with `out_of_scope_by_user`.
- bulk_save/bulk_delete stay external-contract red.
