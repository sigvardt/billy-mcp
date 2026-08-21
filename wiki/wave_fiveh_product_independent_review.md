---
name: wave_fiveh_product_independent_review
title: Wave-5h offline product independent Grok review ACCEPT
desc: Independent Grok acceptance of the offline attachment JSON ticketed-write product at root merge 29cecbe.
tags: [billy, api, attachments, writes, review, coverage]
sources:
  - https://www.billy.dk/api/
  - wiki/wave_fiveh_ticketed_writes_contract.md
  - wiki/wave_fiveh_freeze_independent_review.md
  - wiki/wave_fiveh_product_ready_research_independent_review.md
  - wiki/wave_fiveh_product_implementation_research_independent_review.md
  - coverage/api_v2_manifest.yaml
  - coverage/status.json
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
created: 2026-07-29T23:58:00Z
updated: 2026-07-29T23:58:00Z
---

# Wave-5h offline product independent Grok review ACCEPT

## Verdict and authority

**ACCEPT — the offline product slice only** for root merge **`29cecbe`**
(product leaf commit **`3b6fe4f`**; freeze baseline
`wiki/wave_fiveh_ticketed_writes_contract.md`).

This is the mandatory independent Grok product audit on the root
independent-review route. Child review node
`wave5h_product_review_grok` exited without a durable ACCEPT and does not
replace this page. This ACCEPT does not cover live qualification, UI, vision,
bulk tools, binary `/files` specials, Wave-5i freezes, or overall completeness.

No production code was changed in this review. Official documentation was
re-fetched at ETag `hsisik4g9p3603`, content-length 147934 bytes, MD5
`c2efda0ee4cf9cf200e14910c5fc6996`, matching `coverage/status.json`. Full cited
findings live outside the public repository at
`.fractal/main.billy_complete/tmp/grok-review.md`.

## Accepted product scope

Six ticketed tools for singular create, update, and delete of `attachments`:

| Inventory id | Preview tool | Execute tool | Method and client path |
| --- | --- | --- | --- |
| `api.attachments.create` | `api_attachments_create_preview` | `api_attachments_create_execute` | `POST /attachments` |
| `api.attachments.update` | `api_attachments_update_preview` | `api_attachments_update_execute` | `PUT /attachments/:id` |
| `api.attachments.delete` | `api_attachments_delete_preview` | `api_attachments_delete_execute` | `DELETE /attachments/:id` |

Verified independently:

- Singular request root `attachment`, plural response root `attachments`,
  `additional_plural_roots=()`, partial PUT, bodyless DELETE, locked base
  `https://api.billysbilling.com/v2` without inventing bulk bodies, owner
  encodings, or binary file upload behaviour.
- Typed outer models that forbid undeclared fields while accepting opaque
  attachment JSON.
- One shared `ConfirmationStore` and `WriteProtocolService` on the root server
  (`register_attachment_write_tools` in `src/billy_mcp/server.py`).
- Server-owned `execute_tool_name` binding; `CONFIRMATION_MISMATCH` before
  ticket consumption and before HTTP for wrong-executor misuse (including
  cross-resource via the root service).
- Tamper, expiry, and replay failures without extra writes; no write retries.
- Present `attachments` mapping only; no fabrication of sibling `files` roots.
- Registry asserts exactly **208** `api_*` tools including the six Wave-5h names.
- Coverage honesty: **151** implemented and contract-tested API rows, zero live
  rows, zero vision rows, attachment bulk rows empty-tool red, all UI rows red,
  and `coverage/status.json` `complete: false`. The three attachment CUD rows
  cite real offline suites and remain `live_tested: false`.

## Verification

```text
git rev-parse HEAD
# 29cecbe… merge main.billy_complete.wave5h_attachment_product

uv run pytest -q \
  tests/api/test_attachment_writes.py \
  tests/api/test_attachment_cross_executor.py \
  tests/unit/test_coverage_server.py
# 32 passed

uv run python -c "from billy_mcp.server import create_server; import asyncio; s=create_server(); n=[t.name for t in asyncio.run(s.list_tools()) if t.name.startswith('api_')]; print(len(n))"
# 208
```

Primary implementation files:

- `src/billy_mcp/api/attachment_writes.py`
- `src/billy_mcp/server.py` (shared protocol registration)
- `tests/api/test_attachment_writes.py`
- `tests/api/test_attachment_cross_executor.py`
- `tests/unit/test_coverage_server.py`
- `coverage/api_v2_manifest.yaml` / `coverage/status.json`

## Explicit non-acceptance

Live attachment qualification, UI parity, vision verification, bulk attachment
operations, `api.files.create`, `api.special.files_upload`, Wave-5i work, and
overall completeness remain fail-closed and red or unclaimed.
