---
name: wave_fivei_product_independent_review
title: Wave-5i offline product independent Grok review ACCEPT
desc: Independent Grok acceptance of the offline sales-tax account and meta-field ticketed-write product at root merge 084ad77.
tags: [billy, api, sales-tax, writes, review, coverage]
sources:
  - https://www.billy.dk/api/
  - wiki/wave_fivei_ticketed_writes_contract.md
  - wiki/wave_fivei_freeze_independent_review.md
  - wiki/wave_fivei_product_ready_research_independent_review.md
  - coverage/api_v2_manifest.yaml
  - coverage/status.json
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
created: 2026-07-30T01:08:00Z
updated: 2026-07-30T01:08:00Z
---

# Wave-5i offline product independent Grok review ACCEPT

## Verdict and authority

**ACCEPT — the offline product slice only** for root merge **`084ad77`**
(product leaf commit **`7784901`**; integration record **`a0b55c2`**; freeze
baseline `wiki/wave_fivei_ticketed_writes_contract.md`).

This is the mandatory independent Grok product audit on the root
independent-review route. Child review node `wave5i_product_grok_review`
exited without a durable ACCEPT and does not replace this page. This ACCEPT
does not cover live qualification, UI, vision, bulk tools, Wave-5j bank work,
or overall completeness.

No production code was changed in this review. Official documentation was
re-fetched at ETag `hsisik4g9p3603`, content-length 147934 bytes, MD5
`c2efda0ee4cf9cf200e14910c5fc6996`, matching `coverage/status.json`. Full cited
findings live outside the public repository at
`.fractal/main.billy_complete/tmp/grok-review.md`.

## Accepted product scope

Twelve ticketed tools for singular create, update, and delete of
`salesTaxAccounts` and `salesTaxMetaFields`:

| Inventory id | Preview tool | Execute tool | Method and client path |
| --- | --- | --- | --- |
| `api.salesTaxAccounts.create` | `api_sales_tax_accounts_create_preview` | `api_sales_tax_accounts_create_execute` | `POST /salesTaxAccounts` |
| `api.salesTaxAccounts.update` | `api_sales_tax_accounts_update_preview` | `api_sales_tax_accounts_update_execute` | `PUT /salesTaxAccounts/:id` |
| `api.salesTaxAccounts.delete` | `api_sales_tax_accounts_delete_preview` | `api_sales_tax_accounts_delete_execute` | `DELETE /salesTaxAccounts/:id` |
| `api.salesTaxMetaFields.create` | `api_sales_tax_meta_fields_create_preview` | `api_sales_tax_meta_fields_create_execute` | `POST /salesTaxMetaFields` |
| `api.salesTaxMetaFields.update` | `api_sales_tax_meta_fields_update_preview` | `api_sales_tax_meta_fields_update_execute` | `PUT /salesTaxMetaFields/:id` |
| `api.salesTaxMetaFields.delete` | `api_sales_tax_meta_fields_delete_preview` | `api_sales_tax_meta_fields_delete_execute` | `DELETE /salesTaxMetaFields/:id` |

Verified independently:

- Singular request roots `salesTaxAccount` / `salesTaxMetaField`, primary plural
  response roots, `additional_plural_roots=()`, partial PUT, bodyless DELETE,
  locked base `https://api.billysbilling.com/v2`, no bulk tools, no invented
  enum values.
- Typed outer models that forbid undeclared fields while accepting opaque inner
  JSON.
- New module `src/billy_mcp/api/sales_tax_account_meta_writes.py`; Wave-5g
  `sales_tax_writes.py` not expanded.
- One shared `ConfirmationStore` and `WriteProtocolService` on the root server.
- Server-owned `execute_tool_name` binding; `CONFIRMATION_MISMATCH` before
  ticket consumption and before HTTP for wrong-executor misuse (same-resource
  and cross-resource via the root service).
- Tamper, expiry, and replay failures without extra writes; no write retries.
- Primary-root mapping only; sibling roots not fabricated; optional deleted
  metadata only when present.
- Registry asserts exactly **220** `api_*` tools including the twelve Wave-5i
  names.
- Coverage honesty: **157** implemented and contract-tested API rows, zero live
  rows, zero vision rows, related bulk rows empty-tool red, all UI rows red,
  and `coverage/status.json` `complete: false`. The six CUD rows cite real
  offline suites and remain `live_tested: false`.

## Verification

```text
git rev-parse HEAD
# a0b55c2… (contains merge 084ad77)

uv run pytest -q \
  tests/api/test_sales_tax_account_meta_writes.py \
  tests/api/test_sales_tax_account_meta_cross_executor.py \
  tests/unit/test_coverage_server.py
# 43 passed

uv run python -c "from billy_mcp.server import create_server; import asyncio; s=create_server(); n=[t.name for t in asyncio.run(s.list_tools()) if t.name.startswith('api_')]; print(len(n))"
# 220
```

Primary implementation files:

- `src/billy_mcp/api/sales_tax_account_meta_writes.py`
- `src/billy_mcp/server.py` (shared protocol registration)
- `tests/api/test_sales_tax_account_meta_writes.py`
- `tests/api/test_sales_tax_account_meta_cross_executor.py`
- `tests/unit/test_coverage_server.py`
- `coverage/api_v2_manifest.yaml` / `coverage/status.json`

## Explicit non-acceptance

Live sales-tax account and meta-field qualification, UI parity, vision
verification, bulk operations, binary files specials, Wave-5j bank-line
product tools, and overall completeness remain fail-closed and red or
unclaimed.
