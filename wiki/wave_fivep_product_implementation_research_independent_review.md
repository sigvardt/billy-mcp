---
name: wave_fivep_product_implementation_research_independent_review
title: Wave-5p organizations product-implementation research independent review
desc: Independent Grok ACCEPT as research for the Wave-5p organizations create and update product-implementation handoff after freeze independent ACCEPT; product, live, UI, vision, bulk, and completeness remain separate.
tags: [billy, api, organizations, writes, review, research]
sources:
  - https://www.billy.dk/api/
  - https://api.billysbilling.com/v2
  - .fractal/main.billy_complete/tmp/grok-research.md
  - .fractal/main.billy_complete/tmp/grok-review.md
  - wiki/wave_fivep_ticketed_writes_contract.md
  - wiki/wave_fivep_freeze_independent_review.md
  - wiki/wave_fivep_product_ready_research_independent_review.md
  - wiki/offline_write_probe_rules.md
  - coverage/api_v2_manifest.yaml
  - coverage/status.json
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
created: 2026-07-30T12:10:00Z
updated: 2026-07-30T12:20:00Z
---

# Wave-5p organizations product-implementation research independent review

## Verdict

**ACCEPT as research** for the Wave-5p offline product-implementation handoff
covering singular `organizations` create and update only (exactly four
ticketed tools authorized by freeze independent ACCEPT already on root).

This is not product ACCEPT, live ACCEPT, UI ACCEPT, vision ACCEPT, bulk
resolution, or overall completeness.

## Scope accepted

- Official API contract for `/v2/organizations` Supports create and update among
  singular writes; Supports omits singular delete.
- Independent docs fingerprint: ETag `wcw4x9hqvu3603`, MD5
  `8b94b0135c91fd15fe54ea33e088a4be`, body 147934 bytes (byte-identical to the
  research69 snapshot).
- Unauthenticated probes against `https://api.billysbilling.com/v2` with a JSON
  object body `{}`: organizations POST and PUT return 401
  `AUTHENTICATION_REQUIRED`; singular DELETE returns 405 `METHOD_NOT_ALLOWED`.
- Freeze page `wiki/wave_fivep_ticketed_writes_contract.md` (MD5
  `2742eda7bafecd619aba5fa8ad0694c5`) and freeze independent review
  [[wave_fivep_freeze_independent_review]] remain **ACCEPT** and still match
  docs and probes.
- Product handoff correctly packages only the four tools below with an opaque
  `organization` map, required success root `organizations`, shared ticket
  protocol, fail-closed create cleanup on green, and no delete/bulk/webhook
  tools.
- Inventory create cleanup text that assumes singular DELETE is incorrect
  offline; greening must use fail-closed non-delete wording.
- `users` update and `salesTaxReturns` update remain sequential later candidates;
  `invoiceReminderAssociations` delete remains **blocked** offline.
- At the review baseline, coverage remains 175 implemented and contract-tested,
  zero live, zero vision, 92 ambiguous bulk red, UI 339 all red,
  `complete: false`. No false greens from research69; the root organizations
  product module is absent.

## Exact product surface accepted as research package

| Inventory id | Preview | Execute | Method and client path | Singular request root | Required success root |
| --- | --- | --- | --- | --- | --- |
| `api.organizations.create` | `api_organizations_create_preview` | `api_organizations_create_execute` | `POST /organizations` | `organization` | `organizations` |
| `api.organizations.update` | `api_organizations_update_preview` | `api_organizations_update_execute` | `PUT /organizations/:id` | `organization` | `organizations` |

## Explicit non-acceptances

- Organizations product tools, server registration, contract tests, or coverage
  greening (module absent; status still 175/175/0/0)
- Live CUD, UI, vision, bulk 92 resolution, association delete offline
- Overall completeness

## Wiki hygiene resolution

[[wave_fivep_product_ready_research_independent_review]] initially described
the freeze independent-review page as absent, which was historical relative to
research68. The record now links to the separately accepted
[[wave_fivep_freeze_independent_review]] without changing either review's
scope. Do not treat research acceptance as freeze or product acceptance.

## Evidence

Independent review body: `.fractal/main.billy_complete/tmp/grok-review.md`  
Research package: `.fractal/main.billy_complete/tmp/grok-research.md` (research69)  
Probe scratch: `.fractal/main.billy_complete/tmp/write-probes-review69.json`  
Docs: ETag `wcw4x9hqvu3603`, MD5 `8b94b0135c91fd15fe54ea33e088a4be`, body 147934  
Freeze page: [[wave_fivep_ticketed_writes_contract]]  
Freeze ACCEPT: [[wave_fivep_freeze_independent_review]]  
Prior product-ready research review: [[wave_fivep_product_ready_research_independent_review]]

## Next authorized work

Codex Power offline product leaf for the four named tools only (mirror
`src/billy_mcp/api/invoice_late_fee_writes.py`), then a separate independent
product review. Target after real contract tests only: 260 `api_*` tools and
177 offline implemented + contract_tested; live and vision remain 0;
`complete` remains false until later qualification waves.
