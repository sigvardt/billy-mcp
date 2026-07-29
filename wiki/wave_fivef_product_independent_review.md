---
name: wave_fivef_product_independent_review
title: Wave-5f offline product independent Grok review ACCEPT
desc: Independent Grok acceptance of the offline tax-rate and deduction-component ticketed-write product at root merge 353449d.
tags: [billy, api, writes, review, coverage, tax]
sources:
  - https://www.billy.dk/api/
  - wiki/wave_fivef_ticketed_writes_contract.md
  - wiki/wave_fivef_freeze_independent_review.md
  - coverage/api_v2_manifest.yaml
  - coverage/status.json
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
created: 2026-07-29T21:32:00Z
updated: 2026-07-29T21:32:00Z
---

# Wave-5f offline product independent Grok review ACCEPT

## Verdict and authority

**ACCEPT — the offline product slice only** for root merge **`353449d`**
(product commit **`8c1cdf6`**; freeze baseline **`d412e8c`**).

This is the mandatory independent Grok product audit performed on the root
independent-review route. A Codex Power fallback review, if present, cannot
replace this ACCEPT for gate purposes. This page does not accept live
qualification, UI, vision, bulk tools, specials, Wave-5g, or overall
completeness.

No production code was changed in this review. Official documentation was
re-fetched at ETag `hsisik4g9p3603`, content-length 147934 bytes, matching
inventory MD5 `c2efda0ee4cf9cf200e14910c5fc6996`. Documentation is unchanged
from the inventory freeze and the Wave-5f contract.

## Accepted product scope

The review accepts the twelve ticketed tools for singular create, update, and
delete of `taxRates` and `taxRateDeductionComponents`:

| Inventory id | Preview tool | Execute tool | Method and client path |
| --- | --- | --- | --- |
| `api.taxRates.create` | `api_tax_rates_create_preview` | `api_tax_rates_create_execute` | `POST /taxRates` |
| `api.taxRates.update` | `api_tax_rates_update_preview` | `api_tax_rates_update_execute` | `PUT /taxRates/:id` |
| `api.taxRates.delete` | `api_tax_rates_delete_preview` | `api_tax_rates_delete_execute` | `DELETE /taxRates/:id` |
| `api.taxRateDeductionComponents.create` | `api_tax_rate_deduction_components_create_preview` | `api_tax_rate_deduction_components_create_execute` | `POST /taxRateDeductionComponents` |
| `api.taxRateDeductionComponents.update` | `api_tax_rate_deduction_components_update_preview` | `api_tax_rate_deduction_components_update_execute` | `PUT /taxRateDeductionComponents/:id` |
| `api.taxRateDeductionComponents.delete` | `api_tax_rate_deduction_components_delete_preview` | `api_tax_rate_deduction_components_delete_execute` | `DELETE /taxRateDeductionComponents/:id` |

Verified independently:

- Singular request roots, partial PUT, bodyless DELETE, and locked base URL
  without inventing bulk bodies or webhooks.
- Typed outer models that forbid undeclared fields while accepting opaque
  singular-root payloads (including undocumented future fields offline).
- One shared `ConfirmationStore` and `WriteProtocolService` on the root server.
- Server-owned `execute_tool_name` binding; `CONFIRMATION_MISMATCH` before
  ticket consumption and before HTTP for wrong-executor misuse.
- Tamper, expiry, and replay failures without extra writes; no write retries.
- Parent `additional_plural_roots=("taxRateDeductionComponents",)` with optional
  mapping when present; child responses do not fabricate `taxRates`.
- Registry asserts exactly 190 `api_*` tools and the twelve Wave-5f write names.
- Coverage remains fail-closed: 142 implemented and contract-tested API rows,
  zero live rows, zero vision rows, 92 empty-tool bulk rows, all UI rows red,
  and `coverage/status.json` `complete: false`.
- Host lock remains `https://api.billysbilling.com/v2`; sample host
  `api.billy.dk` is denied by config and client tests.

## Verification

```text
git rev-parse HEAD
# 353449d4f098ecfada142ce1a5379af60268b01c

uv run pytest -q \
  tests/api/test_tax_writes.py \
  tests/unit/test_coverage_server.py
# 43 passed

uv run python -c "from billy_mcp.server import create_server; import asyncio; s=create_server(); n=[t.name for t in asyncio.run(s.list_tools()) if t.name.startswith('api_')]; print(len(n))"
# 190
```

Docs fingerprint re-fetch: ETag `hsisik4g9p3603`, MD5
`c2efda0ee4cf9cf200e14910c5fc6996`, 147934 bytes.

## Explicit non-claims

- No live non-production qualification.
- No UI, vision, or browser evidence.
- No bulk save/delete tools or bodies.
- No files binary upload, invoice specials, sales-tax ruleset/rule writes,
  transactions, postings, bank payments, or platform geo writes.
- No Wave-5g freeze or product authorisation.
- No overall `complete: true`.

## Scratch detail

Full citation tables and checklists:
`.fractal/main.billy_complete/tmp/grok-review.md` (iteration-local; not the
durable gate record).
