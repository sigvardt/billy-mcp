---
name: wave_fived_product_codex_fallback_review
title: Wave-5d Codex Power fallback product review PASS
desc: Secondary offline Codex Power review of the invoice and invoice-line ticketed-write slice at 1108e2f.
tags: [billy, api, invoices, writes, review, fallback]
sources:
  - wiki/wave_fived_ticketed_writes_contract.md
  - wiki/wave_fived_freeze_independent_review.md
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
  - coverage/api_v2_manifest.yaml
  - coverage/status.json
created: 2026-07-29T19:30:00Z
updated: 2026-07-29T19:30:00Z
---

# Wave-5d Codex Power fallback product review PASS

## Verdict and authority

**PASS — secondary offline code-and-test review only** for committed root tip
**`1108e2f`** (the invoice and invoice-line ticketed-write integration).

This is a Codex Power fallback undertaken because the initially mandated Grok
review route failed before review edits. It is **not** the mandatory independent
Grok product acceptance, cannot replace such an acceptance, and does not open
the Wave-5e gate. A separately published
`wiki/wave_fived_product_independent_review.md` is gate context only; this
page makes no Grok or gate verdict.

No production code, tests, coverage artifacts, protocols, or inventory files
were changed by this review. No browser, credential, live Billy data, or raw
browser evidence was used.

## Frozen evidence and limitation

The audit used the frozen offline contract in
`wiki/wave_fived_ticketed_writes_contract.md`, its freeze review in
`wiki/wave_fived_freeze_independent_review.md`, the approved design, the
committed root tree, and the generated coverage artifacts. Those frozen records
identify the cited official-document fingerprint as ETag `hsisik4g9p3603` and
MD5 `c2efda0ee4cf9cf200e14910c5fc6996`.

The cited temporary official-document brief,
`.fractal/main.billy_complete/tmp/grok-research.md`, was absent from its
documented parent location and from this fallback node's `tmp/` directory. This
is an evidence limitation: the fallback did not fetch a replacement, use a
browser, or infer any new documentation claim from its absence.

## Static contract audit

| Frozen requirement | Evidence reviewed | Result |
| --- | --- | --- |
| Exact singular invoice CUD | `src/billy_mcp/api/invoice_writes.py:20`, `:53`, and `:174` define strict outer models, `POST`/`PUT`/`DELETE`, `/invoices`, root `invoice`, and primary root `invoices`; updates reject a conflicting body ID. `tests/api/test_invoice_writes.py` checks strict input, exact request method/path/body, bodyless DELETE, ticket failures, and typed auth/errors. | PASS |
| Exact singular invoice-line CUD | `src/billy_mcp/api/invoice_line_writes.py:20`, `:53`, and `:181` define the equivalent `/invoiceLines`, `invoiceLine`, and `invoiceLines` contract with update-ID binding. `tests/api/test_invoice_line_writes.py` checks the same request and ticket constraints. | PASS |
| Ticket-only exact executor and no retry | `src/billy_mcp/api/write_protocol.py:60` permits only `confirmation_ticket`; `:155-224` binds the server-owned executor name, returns `CONFIRMATION_MISMATCH` before consume/HTTP, and performs one client request. `src/billy_mcp/client.py:99-128` assigns zero retries to write methods; `tests/unit/test_write_protocol.py:211` proves a 503 write makes one attempt. | PASS |
| One shared service and store | `src/billy_mcp/server.py:57-60` creates one `ConfirmationStore` and one `WriteProtocolService`; the same instance reaches both registrars at `:112-113`. | PASS |
| Optional parent mapping | Invoice-line specs declare `additional_plural_roots=("invoices",)` at `src/billy_mcp/api/invoice_line_writes.py:192-203`. `src/billy_mcp/api/write_protocol.py:303-320` maps only returned declared roots, and `tests/api/test_invoice_line_writes.py:285` rejects fabricated parents. | PASS |
| Cross-module ticket preservation | `tests/api/test_invoice_cross_executor.py:30-92` rejects invoice-to-line misuse with no request, then executes the invoice ticket; it rejects line-to-invoice misuse without increasing the request count, then executes the line ticket. | PASS |
| Registry and generated coverage | `tests/unit/test_coverage_server.py:142-156` enumerates twelve Wave-5d tools and asserts 166 `api_*` tools at `:291-305`. `scripts/generate_coverage_report.py:323-325` and `:350-360` carry exactly the six new evidence rows; `tests/coverage/test_coverage_inventory.py:120-136` verifies derived row state. | PASS |

The empty-token regressions in both focused resource suites return
`AUTH_REQUIRED` without network activity. This review therefore did not treat
an unauthenticated DELETE response as success or cleanup evidence.

## Reproduced validation

```text
uv run pytest -q \
  tests/api/test_invoice_writes.py \
  tests/api/test_invoice_line_writes.py \
  tests/api/test_invoice_cross_executor.py \
  tests/unit/test_write_protocol.py \
  tests/unit/test_confirmations.py \
  tests/unit/test_coverage_server.py \
  tests/coverage/test_coverage_inventory.py
# 110 passed

bash .fractal/main.billy_complete.wave5d_product_codex_fallback_review/scripts/test.sh
# 753 passed (non-live suite)

bash .fractal/main.billy_complete.wave5d_product_codex_fallback_review/scripts/lint.sh
# passed: format, Ruff, Pyright, coverage inventory, repository policy
```

## Coverage and explicit non-claims

Generated `coverage/status.json` reports exactly 130 implemented and
contract-tested API rows, zero live-tested rows, zero vision-verified rows, 92
ambiguous bulk rows, and `complete: false`. The review preserves the frozen
fail-closed posture: it does not accept live, UI, vision, bulk, special-route,
or overall-completeness evidence, and it makes no claim about inaccessible UI
or missing credentials.

`BILLY_TEST_MODE=full` ran all 753 tests successfully and then stopped only at
its intended `--require-complete` gate: 92 ambiguous bulk rows remain and live
and UI qualification is incomplete. That failure is expected fail-closed
coverage behaviour, not a defect in this offline product slice.

No concrete defect was reproduced in the reviewed offline slice. The missing
temporary research brief remains the stated limitation of this fallback record.
