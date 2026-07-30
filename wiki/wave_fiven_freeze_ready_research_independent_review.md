---
name: wave_fiven_freeze_ready_research_independent_review
title: Wave-5n invoice-late-fee freeze-ready research independent review
desc: Independent Grok ACCEPT as research for the Wave-5n invoiceLateFees create and update freeze package; freeze page and product remain ungated until separately reviewed.
tags: [billy, api, invoice-late-fees, writes, review, research]
sources:
  - https://www.billy.dk/api/
  - wiki/offline_write_probe_rules.md
  - wiki/wave_fivem_product_independent_review.md
  - coverage/api_v2_manifest.yaml
  - coverage/status.json
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
created: 2026-07-30T08:50:00Z
updated: 2026-07-30T08:50:00Z
---

# Wave-5n invoice-late-fee freeze-ready research independent review

## Verdict

**ACCEPT as research** for the Wave-5n offline freeze package covering singular
`invoiceLateFees` create and update only.

This is not freeze-page ACCEPT, product ACCEPT, live ACCEPT, UI ACCEPT, vision
ACCEPT, bulk resolution, or overall completeness.

## Scope accepted

- Official plain API contract for `/v2/invoiceLateFees` permits create and
  update; Supports omits singular delete.
- Unauthenticated probes against `https://api.billysbilling.com/v2`: POST/PUT
  return 401 `AUTHENTICATION_REQUIRED`; singular DELETE and bulk DELETE with
  `ids[]` return 405 `METHOD_NOT_ALLOWED`.
- Inventory rows `api.invoiceLateFees.create` and `.update` stay red with
  reserved preview tool names; bulk rows stay empty-tool ambiguous.
- Four later tools after freeze then product: create/update preview and execute
  only; opaque `invoiceLateFee` maps; shared ticket protocol; no delete or bulk
  tools.
- Prerequisite Wave-5m product offline ACCEPT remains valid on root.

## Explicit non-accepts

- `wiki/wave_fiven_ticketed_writes_contract.md` was not present at review time.
- No invoice-late-fee product module or registration.
- Live, UI, vision, and bulk remain red.
- `coverage/status.json` remains `complete: false` with 172 offline green rows
  and 0 live/vision.
- HTTP docs ETag/MD5 may change between fetches while plain text is stable; do
  not treat ETag churn alone as a contract change.

## Required product-time fix (after freeze ACCEPT)

When greening create offline, set inventory cleanup for
`api.invoiceLateFees.create` to:

`live non-production cleanup strategy unqualified; singular DELETE is unsupported`

## Full evidence

Authoritative detail lives in the node scratch review file produced with this
verdict (same session): `.fractal/main.billy_complete/tmp/grok-review.md`
(review60). Research package: `.fractal/main.billy_complete/tmp/grok-research.md`
(research60).
