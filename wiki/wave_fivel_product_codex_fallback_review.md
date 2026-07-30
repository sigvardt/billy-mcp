---
name: wave_fivel_product_codex_fallback_review
title: Wave-5l Codex fallback product review ACCEPT
desc: Static Codex Power fallback acceptance of the merged sales-tax-payment write slice at root commit 6bf85ca; the required Grok product gate remains pending.
tags: [billy, api, sales-tax, payments, writes, review, fallback]
sources:
  - https://www.billy.dk/api/
  - wiki/wave_fivel_ticketed_writes_contract.md
  - wiki/wave_fivel_freeze_independent_review.md
  - coverage/api_v2_manifest.yaml
  - coverage/status.json
  - scripts/generate_coverage_report.py
created: 2026-07-30T07:45:00Z
updated: 2026-07-30T07:45:00Z
---

# Wave-5l Codex fallback product review ACCEPT

## Verdict and authority

**ACCEPT — static Codex Power fallback evidence only** for the merged
sales-tax-payment product at root commit **`6bf85ca`** (reviewed against the
prior root baseline `ed5ea8e`). No actionable defect was reproduced in the
permitted Wave-5l product surface.

This is not, and cannot satisfy, the required independent Grok product review.
That Grok gate remains **pending**. This ACCEPT is limited to static
code/contract/test evidence and does not open any later product gate or make a
live, UI, vision, bulk, cleanup, or completeness claim.

The only shared project-wiki changes are this review record and its generated
index entry. The review did not alter production code, tests, coverage
inventory/state, the Wave-5m contract, or any other wiki page. No credentials,
raw documentation body, HAR, trace, browser frame, or persistent test data was
retained.

## Official documentation recheck

The current [Billy API v2 documentation](https://www.billy.dk/api/) names the
fixed `https://api.billysbilling.com/v2` endpoint; its create/update conventions
use a singular request root, require any supplied body ID to match the update
route ID, and return changed records under plural roots. Its
`/v2/salesTaxPayments` entry currently lists get, list, create, update, bulk
save, and bulk delete — not singular delete — and documents the frozen
sales-tax-payment field boundaries.

The review streamed that official page without saving its body. The current
fingerprint matched the freeze evidence: ETag `hsisik4g9p3603`, MD5
`c2efda0ee4cf9cf200e14910c5fc6996`, and 147934 bytes. It did not repeat the
unauthenticated method probes or perform any live call. The accepted freeze
record remains the evidence for POST/PUT 401 and singular DELETE 405; it
therefore continues to exclude singular delete.

## Static contract audit

| Frozen requirement | Static evidence at `6bf85ca` | Result |
| --- | --- | --- |
| Exact four-tool create/update surface | `src/billy_mcp/api/sales_tax_payment_writes.py` registers only `api_sales_tax_payments_create_preview`, `api_sales_tax_payments_create_execute`, `api_sales_tax_payments_update_preview`, and `api_sales_tax_payments_update_execute`. Clean-archive server introspection found 246 `api_*` tools overall and those four write twins; existing get/list reads are separate. | PASS |
| Client-relative writes and roots | The two specifications use `POST`/`PUT`, collection path `/salesTaxPayments`, singular root `salesTaxPayment`, and required plural success root `salesTaxPayments`. `BillyHttpClient` rejects a `/v2` path prefix, so the fixed base cannot be duplicated. | PASS |
| Strict flat outer schemas and opaque map | The registered schemas have `additionalProperties: false`: create preview has only `salesTaxPayment`; update preview only `id` plus `salesTaxPayment`; each execute tool only `confirmation_ticket`. The outer models forbid extras; the inner JSON map remains opaque; update rejects a supplied inner ID that differs from route `id`. | PASS |
| One confirmation protocol with exact binding | `create_server` creates one `ConfirmationStore` and one `WriteProtocolService`, then passes that shared service to this registrar. Preview binds the exact server executor, canonical request, target, and expected effect; a wrong executor returns `CONFIRMATION_MISMATCH` before consumption or HTTP. | PASS |
| One write, typed errors, and response mapping | Execute delegates once to the locked client; write methods have zero retries. The protocol maps only the declared `salesTaxPayments` root and rejects missing or malformed required roots. Focused tests cover tampering, replay, expiry, 401/404 typed errors, empty-token no-network behavior, and one failed 500 write attempt. | PASS |
| No forbidden controls | Clean-archive tool enumeration found no registered tool whose name exposes HTTP or browser control. There are no sales-tax-payment delete or bulk preview/execute tools. | PASS |

The focused suite also directly proves URL encoding for update IDs, exact JSON
envelopes, mutation-free previews, a single write request, and omission of
unreturned related response roots.

## Generated coverage remains fail-closed

`api.salesTaxPayments.create` and `.update` are implemented and
contract-tested offline, but both remain `live_tested: false`. The create row's
cleanup text is exactly: “live non-production cleanup strategy unqualified;
singular DELETE is unsupported.” The two sales-tax-payment bulk rows remain
`ambiguous_bulk`, unimplemented, untested, and have empty tool names. No
singular-delete row or tool was introduced.

Generated `coverage/status.json` reports 170 implemented and contract-tested
API rows, zero live-tested rows, zero vision-verified rows, 92 ambiguous bulk
rows, and `complete: false`. Live, UI, vision, bulk, delete, and overall
completeness therefore remain fail-closed; the frozen acceptance continues to
record the sales-tax-payment UI parity surface as red and unqualified.

## Reproduced clean-archive validation

All review commands ran from a fresh `git archive 6bf85ca` extraction with
`BILLY_API_TOKEN` and organisation variables unset. They created no Billy data
and made no live or browser request.

```text
uv run pytest -q tests/api/test_sales_tax_payment_writes.py \
  tests/coverage/test_coverage_inventory.py \
  tests/unit/test_coverage_server.py
# 32 passed

uv run pytest -q -m 'not live and not vision'
# 1056 passed

BILLY_TEST_MODE=commit bash \
  .fractal/main.billy_complete.wave5l_product_review_grok/scripts/test.sh
# exit 0
```

The disposable clean archive (including its local test environment) was
purged after validation, and the official-document body was streamed only.
