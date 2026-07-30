---
name: wave_fivek_product_ready_research_codex_fallback_review
title: Wave-5k product-ready research Codex Power fallback review
desc: Non-authoritative offline Codex Power fallback ACCEPT of implementation readiness for two bankPayments ticketed-write rows; not a Grok gate, freeze acceptance, or product approval.
tags: [billy, api, bank, payments, writes, review, fallback]
sources:
  - wiki/wave_fivek_freeze_authoring_authority_research_independent_review.md
  - wiki/wave_fivek_freeze_ready_research_independent_review.md
  - wiki/wave_fivek_freeze_implementation_research_independent_review.md
  - wiki/wave_fivek_freeze_authoring_readiness_research_independent_review.md
  - wiki/wave_fivek_freeze_page_authoring_package_research_independent_review.md
  - wiki/offline_write_probe_rules.md
  - coverage/api_v2_manifest.yaml
  - coverage/status.json
  - .fractal/main.billy_complete/plans/2026-07-30T03-46-00Z-2.49-wave5k_product_ready_research.md
  - .fractal/main.billy_complete/plans/2026-07-30T03:52:10.107Z-2.49-wave5k_freeze_and_reviews.md
  - src/billy_mcp/api/write_protocol.py
  - src/billy_mcp/client.py
  - tests/unit/test_coverage_server.py
  - tests/api/test_bank_line_writes.py
created: 2026-07-30T04:04:00Z
updated: 2026-07-30T04:07:00Z
---

# Wave-5k product-ready research Codex Power fallback review

> **Codex Power fallback — non-authoritative.** The assigned Grok invocation
> could not start because its environment was unauthenticated, so this is a
> repository-side offline fallback review of the Wave-5k research49 handoff. It is **not** an
> independent Grok research review, does **not** satisfy or replace a mandatory
> Grok gate, is **not** freeze-page acceptance, and is **not** approval of a
> bankPayments product implementation. The cited Grok research records remain
> the authority for their own findings.

## Verdict

**ACCEPT — offline implementation readiness of the handoff only.** The cited
research, current inventory, and existing shared write infrastructure support a
future, separately gated implementation of exactly two rows and four ticketed
tools, provided it preserves every constraint below. This ACCEPT neither
implements nor registers a tool, and it changes no coverage state.

The result is deliberately conditional: neither
`wiki/wave_fivek_ticketed_writes_contract.md` nor
`src/billy_mcp/api/bank_payment_writes.py` exists at review time. A future
freeze page and its independent review remain prerequisites for product work.

## Exact permitted boundary

| Inventory row | Preview | Execute | Client-relative request | Required input / response roots |
| --- | --- | --- | --- | --- |
| `api.bankPayments.create` | `api_bank_payments_create_preview` | `api_bank_payments_create_execute` | `POST /bankPayments` | opaque `bankPayment` map; primary `bankPayments` response root |
| `api.bankPayments.update` | `api_bank_payments_update_preview` | `api_bank_payments_update_execute` | `PUT /bankPayments/{id}` | non-empty route `id` plus opaque `bankPayment` map; primary `bankPayments` response root |

The inventory confirms the two clear, documented rows and their preview names
at `coverage/api_v2_manifest.yaml`; it records full API routes under `/v2`.
The implementation boundary is intentionally client-relative: the shared
`WriteOperationSpec` and `BillyHttpClient` reject paths that include `/v2`,
hosts, queries, fragments, or traversal, while the locked client supplies the
fixed Billy v2 base. The current read surface independently uses singular
`bankPayment` and plural `bankPayments` roots in
`src/billy_mcp/api/bank_reads.py`.

The package and authority research records name the same four tools and routes.
They also require opaque inner maps rather than a speculative field schema. The
outer preview model must still forbid undeclared fields. For partial update, if
the opaque `bankPayment` map includes `id`, it must equal the route `id`; this
is an explicit handoff constraint and the established singular-write pattern
(`src/billy_mcp/api/bank_line_writes.py`) enforces the same equality before a
ticket is issued. This fallback does not claim that a nonexistent bank-payment
module has already passed that test.

## Ticket and request-safety check

The future four tools can use the existing server-owned protocol without
expanding its authority:

- `WriteProtocolService.preview` canonicalizes and retains the request on the
  server, and each execute tool accepts only `confirmation_ticket`.
- `WriteProtocolService.execute` compares the stored binding's exact executor
  name with the invoked executor before consuming the ticket or issuing HTTP.
  The binding includes the exact canonical request and update target.
- Its POST/PUT construction wraps the opaque map under the singular root and
  constructs the update path from the server-held route id. Successful create
  and update responses require the declared primary plural root.
- `BillyHttpClient` retries only `GET` and `HEAD`; POST and PUT receive zero
  retries. The protocol consumes and discards the prepared ticket before the
  one outbound request. Existing bank-line contract tests demonstrate wrong
  executors make no request and a replay leaves the observed request count at
  one (`tests/api/test_bank_line_writes.py`).

Accordingly, the handoff must bind
`api_bank_payments_create_execute` only to the create preview and
`api_bank_payments_update_execute` only to the update preview. An execute API
that accepts a caller-supplied body, accepts a different executor, retries a
write, permits an inner/route id mismatch, or treats an undeclared response
root as primary would fall outside this ACCEPT.

## Exclusions verified

`api.bankPayments.delete` remains a red inventory row and must not gain either
preview or execute tool. The cited independent research chain and
`wiki/offline_write_probe_rules.md` document unauthenticated singular DELETE
as **405** `METHOD_NOT_ALLOWED`: “Resource at `bankPayments` does not support
deleting a single record.” That observed 405 overrides the optimistic Supports
listing for offline work.

`api.bankPayments.bulk_save` and `.bulk_delete` remain tool-less,
`ambiguous_bulk`, unimplemented, and untested in the manifest. The probe rules
require a request/response body contract before any bulk tool can leave red.
Neither bulk operation is part of this handoff.

## Arithmetic and fail-closed state

The current server test asserts **238** registered `api_*` tools, while
`coverage/status.json` records **166** implemented and contract-tested offline
API rows. Adding the two preview/execute pairs is therefore a four-tool
registry delta (**238 → 242**) but only a two-row coverage delta
(**166 → 168**), after real implementation and contract tests only. The
research49 plan and accepted Wave-5k research records state the same target;
this review made no coverage edit.

The current manifest keeps create, update, and delete unimplemented and
uncontract-tested. `coverage/status.json` remains `complete: false`, with zero
live-tested and vision-verified rows, an unavailable-token blocker for live or
UI qualification, and 92 ambiguous bulk API rows. Thus live, UI, vision, bulk,
and overall-completion qualification all remain fail-closed.

## What this ACCEPT does not authorize

- authoring or accepting the Wave-5k freeze contract;
- adding `bank_payment_writes.py`, server registration, tests, or coverage
  evidence;
- changing the current red bankPayments CUD or bulk rows;
- live calls, UI or browser qualification, vision evidence, credentials, or
  persistent test data; or
- any claim that the product is complete or ready for production use.

The next product-capable decision belongs to the separately required freeze
page and its independent review, followed by implementation and its own
independent product review. This fallback remains supplemental evidence only.
