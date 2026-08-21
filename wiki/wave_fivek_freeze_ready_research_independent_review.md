---
name: wave_fivek_freeze_ready_research_independent_review
title: Wave-5k freeze-ready research independent Grok review ACCEPT
desc: Independent Grok acceptance of the cited offline freeze-ready research handoff for singular bankPayments create and update ticketed writes (delete excluded on 405).
tags: [billy, api, bank, payments, writes, review, research]
sources:
  - https://www.billy.dk/api/
  - wiki/offline_write_probe_rules.md
  - coverage/api_v2_manifest.yaml
  - coverage/status.json
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
created: 2026-07-30T02:27:00Z
updated: 2026-07-30T02:27:00Z
---

# Wave-5k freeze-ready research independent Grok review ACCEPT

## Verdict and authority

**ACCEPT — freeze-ready research handoff only** for the two clear singular
Billy API v2 write operations `api.bankPayments.create` and
`api.bankPayments.update`.

The cited research lives outside the public repository at
`.fractal/main.billy_complete/tmp/grok-research.md` (research44). Full findings:
`.fractal/main.billy_complete/tmp/grok-review.md`.

This ACCEPT opens only the offline freeze-page authoring gate **after**
Wave-5j bank-line product is merged and independently product-reviewed. It is
**not** acceptance of a freeze contract page, product tools, coverage greens,
bulk tools, singular delete tools, live qualification, UI parity, vision, or
overall completeness.

No production code or coverage flags were greened in the reviewed research.
Official documentation was re-fetched independently at ETag `hsisik4g9p3603`,
content-length 147934 bytes, MD5 `c2efda0ee4cf9cf200e14910c5fc6996`, matching
`coverage/status.json`.

## Accepted research scope

Two inventory rows / planned four ticketed tools (preview + execute):

| Inventory id | Planned preview tool | Planned execute tool | HTTP |
| --- | --- | --- | --- |
| `api.bankPayments.create` | `api_bank_payments_create_preview` | `api_bank_payments_create_execute` | `POST /bankPayments` |
| `api.bankPayments.update` | `api_bank_payments_update_preview` | `api_bank_payments_update_execute` | `PUT /bankPayments/:id` |

Verified independently against the official page, inventory, and unauthenticated
probes:

- Supports lists create, update, **and** singular delete; unauthenticated
  DELETE returns **405** `METHOD_NOT_ALLOWED` (“does not support deleting a
  single record”) and **overrides** Supports delete for offline green tools.
- Unauthenticated POST and PUT return **401** `AUTHENTICATION_REQUIRED` —
  method-open at the auth gate for offline freeze of create and update only.
- Bulk save/delete remain empty-tool `ambiguous_bulk`.
- Official sample publishes `cashSide` members **debit** and **credit** and
  association `subjectReference` form `invoice:…`. Inner product maps stay
  opaque.
- Primary documented mutable update field is `isVoided` (set true to cancel;
  cannot un-cancel). Live cleanup cannot rely on DELETE.
- Planned arithmetic after a future Wave-5j product (238 tools / 166 offline)
  then Wave-5k product: **242** tools / **168** offline; delete row stays red.
- Research keeps create/update/delete red on root today (157 offline;
  `complete: false`).

## Explicit non-acceptance

- No Wave-5k freeze contract page is accepted here (none exists yet).
- No bank-payment product implementation or registry tools.
- No coverage greens for create, update, delete, or bulk rows.
- No singular delete tools despite inventory `tool_name`
  `api_bank_payments_delete_preview`.
- No Wave-5j product acceptance (product still absent on root).
- No live, UI, vision, or completeness claim.

## Next gate after this ACCEPT

1. Complete Wave-5j bank-line product and independent product review ACCEPT.
2. Codex Power authors `wiki/wave_fivek_ticketed_writes_contract.md` from
   research44 and this page.
3. Independent freeze review of that freeze page.
4. Only then a product leaf for the four create/update tools.

No browser was launched, no credential or customer data was used, and no raw
browser evidence is retained.
