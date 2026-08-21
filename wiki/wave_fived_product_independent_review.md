---
name: wave_fived_product_independent_review
title: Wave-5d offline product independent Grok review ACCEPT
desc: Independent Grok acceptance of the offline invoice and invoice-line ticketed-write product at tip 1108e2f.
tags: [billy, api, writes, review, coverage, invoices]
sources:
  - https://www.billy.dk/api/
  - wiki/wave_fived_ticketed_writes_contract.md
  - wiki/wave_fived_freeze_independent_review.md
  - coverage/api_v2_manifest.yaml
  - coverage/status.json
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
created: 2026-07-29T19:20:00Z
updated: 2026-07-29T19:20:00Z
---

# Wave-5d offline product independent Grok review ACCEPT

## Verdict and authority

**ACCEPT — the offline product slice only** for exact tip **`1108e2f`**
(product integration of invoice and invoice-line ticketed writes; freeze baseline
**`5c376de`**).

This is the mandatory independent Grok product audit performed on the
authenticated root independent-review route. A Codex Power fallback review, if
present, cannot replace this ACCEPT for gate purposes. This page does not accept
live qualification, UI, vision, bulk tools, specials, or overall completeness.

No production code was changed in this review. Official documentation was
re-fetched at ETag `hsisik4g9p3603`, content-length 147934 bytes, matching
inventory MD5 `c2efda0ee4cf9cf200e14910c5fc6996`. Documentation is unchanged
from the inventory freeze and the Wave-5d contract.

## Accepted product scope

The review accepts the twelve ticketed tools for singular create, update, and
delete of `invoices` and `invoiceLines`:

| Inventory id | Preview tool | Execute tool | Method and client path |
| --- | --- | --- | --- |
| `api.invoices.create` | `api_invoices_create_preview` | `api_invoices_create_execute` | `POST /invoices` |
| `api.invoices.update` | `api_invoices_update_preview` | `api_invoices_update_execute` | `PUT /invoices/:id` |
| `api.invoices.delete` | `api_invoices_delete_preview` | `api_invoices_delete_execute` | `DELETE /invoices/:id` |
| `api.invoiceLines.create` | `api_invoice_lines_create_preview` | `api_invoice_lines_create_execute` | `POST /invoiceLines` |
| `api.invoiceLines.update` | `api_invoice_lines_update_preview` | `api_invoice_lines_update_execute` | `PUT /invoiceLines/:id` |
| `api.invoiceLines.delete` | `api_invoice_lines_delete_preview` | `api_invoice_lines_delete_execute` | `DELETE /invoiceLines/:id` |

Verified independently:

- Singular request roots, partial PUT, bodyless DELETE, and locked base URL
  without a duplicate `/v2` client path prefix.
- Typed outer models that forbid undeclared fields while accepting opaque
  singular-root payloads.
- One shared `ConfirmationStore` and `WriteProtocolService` on the root server.
- Server-owned `execute_tool_name` binding; `CONFIRMATION_MISMATCH` before
  ticket consumption and before HTTP for same-module and cross-module misuse.
- Tamper, expiry, and replay failures without extra writes; no write retries on
  the shared protocol path.
- Invoice-line `additional_plural_roots=("invoices",)` with optional parent
  mapping; primary-only responses do not fabricate `invoices`.
- Generator-owned offline evidence for all six CUD rows; registry asserts
  exactly 166 `api_*` tools and the twelve Wave-5d names.
- Coverage remains fail-closed: 130 implemented and contract-tested API rows,
  zero live rows, zero vision rows, 92 empty-tool bulk rows, all UI rows red,
  and `coverage/status.json` `complete: false`.

## Verification

```text
git rev-parse HEAD
# 1108e2f…

uv run pytest -q \
  tests/api/test_invoice_writes.py \
  tests/api/test_invoice_line_writes.py \
  tests/api/test_invoice_cross_executor.py \
  tests/unit/test_write_protocol.py \
  tests/unit/test_confirmations.py \
  tests/unit/test_coverage_server.py \
  tests/coverage/test_coverage_inventory.py
# 110 passed
```

Official docs re-check: ETag `hsisik4g9p3603`, content-length 147934.

## Findings

No actionable product defects. Non-blocking notes: invoice-line tests omit an
explicit HTTP-500 non-retry twin (parent module covers it; protocol issues a
single request). Live-only questions remain for embedded line minimum/replace
rules, approved-state irreversibility, and multi-root presence on every live
line write. Unauthenticated empty DELETE responses are still not cleanup proof.

## Explicit non-claims

This ACCEPT does not green live, UI, vision, bulk, special-route, webhook, or
overall-completeness claims. It authorises the Wave-5e bills offline cohort only
after a cited freeze promoted from current research and its own freeze ACCEPT.

The temporary full reviewer note lives outside the repository at
`.fractal/main.billy_complete/tmp/grok-review.md`; this page is the durable,
scrubbed gate record.
