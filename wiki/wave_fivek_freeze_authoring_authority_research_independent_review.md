---
name: wave_fivek_freeze_authoring_authority_research_independent_review
title: Wave-5k freeze authoring authority research independent Grok review ACCEPT
desc: Independent Grok acceptance that opens offline Wave-5k freeze-page authoring for singular bankPayments create and update after product prerequisite and package content are already accepted.
tags: [billy, api, bank, payments, writes, review, research]
sources:
  - https://www.billy.dk/api/
  - wiki/wave_fivek_freeze_ready_research_independent_review.md
  - wiki/wave_fivek_freeze_implementation_research_independent_review.md
  - wiki/wave_fivek_freeze_authoring_readiness_research_independent_review.md
  - wiki/wave_fivek_freeze_page_authoring_package_research_independent_review.md
  - wiki/wave_fivej_product_independent_review.md
  - wiki/offline_write_probe_rules.md
  - coverage/api_v2_manifest.yaml
  - coverage/status.json
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
created: 2026-07-30T03:40:00Z
updated: 2026-07-30T03:40:00Z
---

# Wave-5k freeze authoring authority research independent Grok review ACCEPT

## Verdict and authority

**ACCEPT — freeze authoring authority research handoff only** for the two clear
singular Billy API v2 write operations `api.bankPayments.create` and
`api.bankPayments.update`.

The cited research lives outside the public repository at
`.fractal/main.billy_complete/tmp/grok-research.md` (research48). Full findings:
`.fractal/main.billy_complete/tmp/grok-review.md`.

This ACCEPT **opens offline Wave-5k freeze-page authoring**. Codex Power may
write `wiki/wave_fivek_ticketed_writes_contract.md` from research48 §5–§6
(package content previously accepted under research47).

This ACCEPT deepens and supersedes the process-gate reading in
`wiki/wave_fivek_freeze_page_authoring_package_research_independent_review.md`
that kept authoring blocked solely on Wave-5j product non-overclaim language.
Package **content** acceptance remains valid; authoring is no longer blocked.

It is **not** acceptance of a freeze contract page, bank-payment product tools,
coverage greens, bulk tools, singular delete tools, live qualification, UI
parity, vision, or overall completeness.

No production code or coverage flags were greened in the reviewed research or
this review. Official documentation was re-fetched independently at ETag
`hsisik4g9p3603`, content-length 147934 bytes, MD5
`c2efda0ee4cf9cf200e14910c5fc6996`, matching `coverage/status.json`.

## Accepted research scope

Two inventory rows / planned four ticketed tools (preview + execute):

| Inventory id | Planned preview tool | Planned execute tool | HTTP |
| --- | --- | --- | --- |
| `api.bankPayments.create` | `api_bank_payments_create_preview` | `api_bank_payments_create_execute` | `POST /bankPayments` |
| `api.bankPayments.update` | `api_bank_payments_update_preview` | `api_bank_payments_update_execute` | `PUT /bankPayments/:id` |

Verified independently against the official page, inventory, and unauthenticated
probes:

- Supports lists create, update, and singular delete; unauthenticated DELETE
  returns **405** `METHOD_NOT_ALLOWED` (“Resource at `bankPayments` does not
  support deleting a single record.”) and **overrides** Supports delete for
  offline green tools.
- Unauthenticated POST and PUT return **401** `AUTHENTICATION_REQUIRED` —
  method-open at the auth gate for offline freeze of create and update only.
- Bulk save/delete remain empty-tool `ambiguous_bulk`.
- Official property table and sample reconfirmed: published `cashSide` members
  **debit** / **credit**; association `subjectReference` form `invoice:…`;
  primary documented mutable update field `isVoided` (set true to cancel;
  cannot un-cancel). Inner product maps stay opaque.
- Root arithmetic: **238** tools / **166** offline. After Wave-5k product:
  **242** tools / **168** offline; delete row stays red.
- bankPayments create/update/delete remain red on root today (`complete: false`).

## Authority resolution accepted

Prerequisites verified on root:

1. Wave-5j bank-line product merged and offline product-reviewed
   (`wiki/wave_fivej_product_independent_review.md`).
2. Wave-5k freeze-ready, freeze-implementation, authoring-readiness, and package
   content research ACCEPTs present under `wiki/`.
3. Wave-5j product ACCEPT correctly non-overclaims Wave-5k (product scope only).
   That non-overclaim is **not** a permanent freeze research block.
4. Wave-5k freeze-ready ACCEPT already opens freeze-page authoring **after**
   Wave-5j product independent review. That “after” condition is met.

This page is the explicit open of Wave-5k freeze authoring requested when the
package review declined to infer open from product ACCEPT alone.

## Explicit non-acceptance

- No Wave-5k freeze contract page is accepted here (none exists yet).
- No bank-payment product implementation or registry tools.
- No coverage greens for create, update, delete, or bulk rows.
- No singular delete tools despite inventory `tool_name`
  `api_bank_payments_delete_preview`.
- No live, UI, vision, or completeness claim.
- Wave-5j product ACCEPT remains limited to eighteen bank-line tools and 166
  offline rows.

## Next gate after this ACCEPT

1. Codex Power authors `wiki/wave_fivek_ticketed_writes_contract.md` from
   research48 §5–§6 and the accepted Wave-5k research chain (create+update only;
   delete excluded with 405 citation).
2. Independent freeze review of that freeze page.
3. Only then a product leaf for the four create/update tools.
4. After product ACCEPT: Wave-5l freeze-ready research for `salesTaxPayments`
   create+update.

No browser was launched, no credential or customer data was used, and no raw
browser evidence is retained.
