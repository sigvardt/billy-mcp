---
name: wave_fiven_product_ready_research_independent_review
title: Wave-5n invoice-late-fee product-ready research independent review
desc: Independent Grok ACCEPT as research for the Wave-5n invoiceLateFees product-ready package; freeze ACCEPT and product remain separate gates.
tags: [billy, api, invoice-late-fees, writes, review, research]
sources:
  - https://www.billy.dk/api/
  - wiki/wave_fiven_ticketed_writes_contract.md
  - wiki/offline_write_probe_rules.md
  - wiki/wave_fivem_product_independent_review.md
  - coverage/api_v2_manifest.yaml
  - coverage/status.json
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
created: 2026-07-30T09:18:00Z
updated: 2026-07-30T09:18:00Z
---

# Wave-5n invoice-late-fee product-ready research independent review

## Verdict

**ACCEPT as research** for the Wave-5n offline product-ready package covering
singular `invoiceLateFees` create and update only (four ticketed tools after a
separate freeze ACCEPT).

This is not freeze-page ACCEPT, product ACCEPT, live ACCEPT, UI ACCEPT, vision
ACCEPT, bulk resolution, or overall completeness.

## Scope accepted

- Official plain API contract for `/v2/invoiceLateFees` permits create and
  update; Supports omits singular delete.
- Unauthenticated probes against `https://api.billysbilling.com/v2` with a JSON
  object body: POST/PUT return 401 `AUTHENTICATION_REQUIRED`; singular DELETE
  and bulk DELETE with `ids[]` return 405 `METHOD_NOT_ALLOWED`.
- Product handoff correctly requires freeze independent review ACCEPT of
  [[wave_fiven_ticketed_writes_contract]] before any implementation.
- Four later tools after freeze then product: create/update preview and execute
  only; opaque `invoiceLateFee` maps; shared ticket protocol; no delete or bulk
  tools.
- Create cleanup must be corrected at greening to:
  `live non-production cleanup strategy unqualified; singular DELETE is unsupported`
- Target offline arithmetic after real product tests only: 254 `api_*` tools,
  174 implemented and contract-tested rows, live and vision still zero,
  `complete: false`.

## Explicit non-accepts

- Freeze independent review ACCEPT is not issued here (dedicated freeze review
  remains the freeze gate).
- No invoice-late-fee product module or write registration on root.
- Live, UI, vision, and bulk remain red.
- `coverage/status.json` remains `complete: false` with 172 offline green rows
  and 0 live/vision.
- HTTP docs ETag/MD5 may change between fetches while plain text is stable; do
  not treat ETag churn alone as a contract change.

## Freeze page concordance (not freeze ACCEPT)

`wiki/wave_fiven_ticketed_writes_contract.md` (content MD5
`93e6d266d1718fa517ff645b3ca213ce`) matches the official create/update surface,
delete exclusion, bulk exclusion, ticketed protocol, and opaque field
boundaries revalidated in this review. That concordance supports the
product-ready research package; it is not a freeze ACCEPT.

## Revalidation boundary

Root verification reconfirms 250 registered `api_*` tools, only get/list late-fee
tools, no `invoice_late_fee_writes.py`, create/update inventory rows still red,
all 92 ambiguous bulk rows empty-tool, and 19 passing focused
contact-balance-payment contract tests for the prior Wave-5m product. These
checks confirm the fail-closed boundary only.

## Full evidence

Authoritative detail lives in the node scratch review file produced with this
verdict: `.fractal/main.billy_complete/tmp/grok-review.md` (review61). Research
package: `.fractal/main.billy_complete/tmp/grok-research.md` (research61).
