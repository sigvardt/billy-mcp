---
name: wave_fiveg_product_independent_review
title: Wave-5g offline product independent Grok review ACCEPT
desc: Independent Grok acceptance of the offline sales-tax ruleset and rule ticketed-write product at root merge 55faa02.
tags: [billy, api, writes, review, coverage, sales-tax]
sources:
  - https://www.billy.dk/api/
  - wiki/wave_fiveg_ticketed_writes_contract.md
  - wiki/wave_fiveg_freeze_independent_review.md
  - coverage/api_v2_manifest.yaml
  - coverage/status.json
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
created: 2026-07-29T22:33:00Z
updated: 2026-07-29T22:33:00Z
---

# Wave-5g offline product independent Grok review ACCEPT

## Verdict and authority

**ACCEPT — the offline product slice only** for root merge **`55faa02`**
(product commit **`e6f96e7`**; freeze baseline **`5612aa8`**).

This is the mandatory independent Grok product audit performed on the root
independent-review route. A Codex Power fallback review, if present, cannot
replace this ACCEPT for gate purposes. This page does not accept live
qualification, UI, vision, bulk tools, specials, Wave-5h freezes, or overall
completeness.

No production code was changed in this review. Official documentation was
re-fetched at ETag `hsisik4g9p3603`, content-length 147934 bytes, matching
inventory MD5 `c2efda0ee4cf9cf200e14910c5fc6996`. Documentation is unchanged
from the inventory freeze and the Wave-5g contract.

## Accepted product scope

The review accepts the twelve ticketed tools for singular create, update, and
delete of `salesTaxRulesets` and `salesTaxRules`:

| Inventory id | Preview tool | Execute tool | Method and client path |
| --- | --- | --- | --- |
| `api.salesTaxRulesets.create` | `api_sales_tax_rulesets_create_preview` | `api_sales_tax_rulesets_create_execute` | `POST /salesTaxRulesets` |
| `api.salesTaxRulesets.update` | `api_sales_tax_rulesets_update_preview` | `api_sales_tax_rulesets_update_execute` | `PUT /salesTaxRulesets/:id` |
| `api.salesTaxRulesets.delete` | `api_sales_tax_rulesets_delete_preview` | `api_sales_tax_rulesets_delete_execute` | `DELETE /salesTaxRulesets/:id` |
| `api.salesTaxRules.create` | `api_sales_tax_rules_create_preview` | `api_sales_tax_rules_create_execute` | `POST /salesTaxRules` |
| `api.salesTaxRules.update` | `api_sales_tax_rules_update_preview` | `api_sales_tax_rules_update_execute` | `PUT /salesTaxRules/:id` |
| `api.salesTaxRules.delete` | `api_sales_tax_rules_delete_preview` | `api_sales_tax_rules_delete_execute` | `DELETE /salesTaxRules/:id` |

Verified independently:

- Singular request roots, partial PUT, bodyless DELETE, and locked base URL
  without inventing bulk bodies or webhooks.
- Typed outer models that forbid undeclared fields while accepting opaque
  singular-root payloads (including undocumented future fields offline).
- One shared `ConfirmationStore` and `WriteProtocolService` on the root server.
- Server-owned `execute_tool_name` binding; `CONFIRMATION_MISMATCH` before
  ticket consumption and before HTTP for wrong-executor misuse.
- Tamper, expiry, and replay failures without extra writes; no write retries.
- Parent `additional_plural_roots=("salesTaxRules",)` with optional mapping when
  present; child responses do not fabricate `salesTaxRulesets`.
- Registry asserts exactly 202 `api_*` tools and the twelve Wave-5g write names.
- Coverage remains fail-closed: 148 implemented and contract-tested API rows,
  zero live rows, zero vision rows, 92 empty-tool bulk rows, all UI rows red,
  and `coverage/status.json` `complete: false`.
- Host lock remains `https://api.billysbilling.com/v2`; sample host
  `api.billy.dk` must not become the client base.

## Verification

```text
git rev-parse HEAD
# 55faa02… merge main.billy_complete.wave5g_sales_tax_product

uv run pytest -q \
  tests/api/test_sales_tax_writes.py \
  tests/api/test_sales_tax_cross_executor.py \
  tests/unit/test_coverage_server.py
# 44 passed

uv run python -c "from billy_mcp.server import create_server; import asyncio; s=create_server(); n=[t.name for t in asyncio.run(s.list_tools()) if t.name.startswith('api_')]; print(len(n))"
# 202
```

Primary implementation files:

- `src/billy_mcp/api/sales_tax_writes.py`
- `src/billy_mcp/server.py` (shared protocol registration)
- `tests/api/test_sales_tax_writes.py`
- `tests/api/test_sales_tax_cross_executor.py`
- `tests/unit/test_coverage_server.py`
- Coverage row evidence on the six CUD ids in `coverage/api_v2_manifest.yaml`

## Explicit non-acceptance

- Live non-production qualification of the six rows
- UI parity, headless E2E, and vision review
- Bulk save/delete for either resource
- Attachments, sales-tax accounts/meta-fields/payments/returns, specials
- Overall project completeness

## Next gate

After this ACCEPT, the next offline freeze track is Wave-5h singular
`attachments` CUD, cited in node scratch
`.fractal/main.billy_complete/tmp/grok-research.md` (research only until a freeze
wiki page is written and independently accepted).
