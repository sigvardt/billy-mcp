---
name: wave_fivep_freeze_ready_research_independent_review
title: Wave-5p organizations freeze-ready research independent review
desc: Independent Grok ACCEPT as research for the Wave-5p organizations create and update freeze-ready package; freeze page, product, live, UI, and completeness remain separate.
tags: [billy, api, organizations, writes, review, research]
sources:
  - https://www.billy.dk/api/
  - https://api.billysbilling.com/v2
  - .fractal/main.billy_complete/tmp/grok-research.md
  - .fractal/main.billy_complete/tmp/grok-review.md
  - wiki/wave_fivep_candidate_write_research.md
  - wiki/offline_write_probe_rules.md
  - coverage/api_v2_manifest.yaml
  - coverage/status.json
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
created: 2026-07-30T11:32:00Z
updated: 2026-07-30T11:32:00Z
---

# Wave-5p organizations freeze-ready research independent review

## Verdict

**ACCEPT as research** for the Wave-5p offline freeze-ready package covering singular `organizations` create and update only (exactly four future ticketed tools once a freeze page and product exist).

This is not freeze ACCEPT, product ACCEPT, live ACCEPT, UI ACCEPT, vision ACCEPT, bulk resolution, or overall completeness.

## Scope accepted

- Official API contract for `/v2/organizations` Supports create and update among singular writes; Supports omits singular delete.
- Independent docs fingerprint: ETag `wcw4x9hqvu3603`, MD5 `8b94b0135c91fd15fe54ea33e088a4be`, body 147934 bytes (byte-identical to the research67 snapshot).
- Unauthenticated probes against `https://api.billysbilling.com/v2` with JSON object body `{}`: organizations POST and PUT return 401 `AUTHENTICATION_REQUIRED`; singular DELETE returns 405 `METHOD_NOT_ALLOWED`.
- Research67 correctly bounds the freeze package to `api_organizations_create_preview` / `_execute` and `api_organizations_update_preview` / `_execute` with opaque `organization` map, required success root `organizations`, shared ticket protocol, and no delete/bulk/webhook tools.
- Inventory create cleanup text that assumes singular DELETE is incorrect offline; greening must use fail-closed non-delete wording.
- `users` update and `salesTaxReturns` update remain sequential later candidates; `invoiceReminderAssociations` delete remains **blocked** offline (DELETE missing id returns 200 meta-only without cleanup proof; create/update return 405).
- Coverage honesty remains 174 implemented and contract-tested, zero live, zero vision, 92 ambiguous bulk red, `complete: false`. No false greens from research67.
- Wave-5p freeze page is not on root yet. Organizations product module is absent.

## Exact future freeze surface accepted as research package

| Inventory id | Preview | Execute | Method and client path | Singular request root | Required success root |
| --- | --- | --- | --- | --- | --- |
| `api.organizations.create` | `api_organizations_create_preview` | `api_organizations_create_execute` | `POST /organizations` | `organization` | `organizations` |
| `api.organizations.update` | `api_organizations_update_preview` | `api_organizations_update_execute` | `PUT /organizations/:id` | `organization` | `organizations` |

## Explicit non-acceptances

- `wiki/wave_fivep_ticketed_writes_contract.md` freeze ACCEPT (page not present at review time)
- Organizations product tools or coverage greening
- Wave-5o product ACCEPT on root (child may be complete off-root; root merge and product review remain separate)
- `invoiceReminderAssociations` any write offline
- Bulk 92 resolution, live CUD, UI, vision, completeness

## Evidence

Independent review body: `.fractal/main.billy_complete/tmp/grok-review.md`  
Research package: `.fractal/main.billy_complete/tmp/grok-research.md` (research67)  
Probe scratch: `.fractal/main.billy_complete/tmp/write-probes-review67.json`  
Docs: ETag `wcw4x9hqvu3603`, MD5 `8b94b0135c91fd15fe54ea33e088a4be`, body 147934  
Prior candidate research: [[wave_fivep_candidate_write_research]]
