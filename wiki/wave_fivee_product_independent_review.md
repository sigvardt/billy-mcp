---
name: wave_fivee_product_independent_review
title: Wave-5e offline product independent Grok review ACCEPT
desc: Independent Grok acceptance of the offline bill and bill-line ticketed-write product at tip 15d0bde.
tags: [billy, api, writes, review, coverage, bills]
sources:
  - https://www.billy.dk/api/
  - wiki/wave_fivee_ticketed_writes_contract.md
  - wiki/wave_fivee_freeze_independent_review.md
  - coverage/api_v2_manifest.yaml
  - coverage/status.json
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
created: 2026-07-29T20:30:00Z
updated: 2026-07-29T20:30:00Z
---

# Wave-5e offline product independent Grok review ACCEPT

## Verdict and authority

**ACCEPT — the offline product slice only** for exact tip **`15d0bde`**
(product integration of bill and bill-line ticketed writes; freeze baseline
**`fc8118e`**).

This is the mandatory independent Grok product audit performed on the root
independent-review route. A Codex Power fallback review, if present, cannot
replace this ACCEPT for gate purposes. This page does not accept live
qualification, UI, vision, bulk tools, specials, Wave-5f, or overall
completeness.

No production code was changed in this review. Official documentation was
re-fetched at ETag `hsisik4g9p3603`, content-length 147934 bytes, matching
inventory MD5 `c2efda0ee4cf9cf200e14910c5fc6996`. Documentation is unchanged
from the inventory freeze and the Wave-5e contract.

## Accepted product scope

The review accepts the twelve ticketed tools for singular create, update, and
delete of `bills` and `billLines`:

| Inventory id | Preview tool | Execute tool | Method and client path |
| --- | --- | --- | --- |
| `api.bills.create` | `api_bills_create_preview` | `api_bills_create_execute` | `POST /bills` |
| `api.bills.update` | `api_bills_update_preview` | `api_bills_update_execute` | `PUT /bills/:id` |
| `api.bills.delete` | `api_bills_delete_preview` | `api_bills_delete_execute` | `DELETE /bills/:id` |
| `api.billLines.create` | `api_bill_lines_create_preview` | `api_bill_lines_create_execute` | `POST /billLines` |
| `api.billLines.update` | `api_bill_lines_update_preview` | `api_bill_lines_update_execute` | `PUT /billLines/:id` |
| `api.billLines.delete` | `api_bill_lines_delete_preview` | `api_bill_lines_delete_execute` | `DELETE /billLines/:id` |

Verified independently:

- Singular request roots, partial PUT, bodyless DELETE, and locked base URL
  without a duplicate `/v2` client path prefix on relative paths.
- Typed outer models that forbid undeclared fields while accepting opaque
  singular-root payloads (no invoice-line `productId` / `unitPrice` fields).
- One shared `ConfirmationStore` and `WriteProtocolService` on the root server.
- Server-owned `execute_tool_name` binding; `CONFIRMATION_MISMATCH` before
  ticket consumption and before HTTP for same-module and cross-module misuse.
- Tamper, expiry, and replay failures without extra writes; no write retries on
  the shared protocol path.
- Bill-line `additional_plural_roots=("bills",)` with optional parent mapping;
  primary-only responses do not fabricate `bills`. Parent bill writes use no
  additional response root.
- Generator-owned offline evidence for all six CUD rows; registry asserts
  exactly 178 `api_*` tools and the twelve Wave-5e write names.
- Coverage remains fail-closed: 136 implemented and contract-tested API rows,
  zero live rows, zero vision rows, 92 empty-tool bulk rows, all UI rows red,
  and `coverage/status.json` `complete: false`.

## Verification

```text
git rev-parse HEAD
# 15d0bde7fca1a202339c1a6f2790571f78e78e5a

.venv/bin/python -m pytest -q \
  tests/api/test_bill_writes.py \
  tests/api/test_bill_line_writes.py \
  tests/api/test_bill_cross_executor.py \
  tests/unit/test_coverage_server.py
# 58 passed

.venv/bin/python -c "from billy_mcp.server import create_server; import asyncio; s=create_server(); n=[t.name for t in asyncio.run(s.list_tools()) if t.name.startswith('api_')]; print(len(n))"
# 178
```

Docs fingerprint re-fetch: ETag `hsisik4g9p3603`, MD5
`c2efda0ee4cf9cf200e14910c5fc6996`, 147934 bytes.

## Explicit non-claims

- No live non-production qualification.
- No UI, vision, or browser evidence.
- No bulk save/delete tools or bodies.
- No attachment CUD, file binary upload, invoice specials, transactions,
  postings, or tax/bank writes.
- No overall `complete: true`.

## Scratch detail

Full reviewer notes (scratch, not durable authority):  
`.fractal/main.billy_complete/tmp/grok-review.md`
