---
name: wave_fiveb_product_fallback_review
title: Wave-5b product fallback review
desc: Codex Power fallback review of Wave-5b root product at 920ceab; REJECT pending ticket-to-executor binding.
tags: [billy, review, writes, fallback]
sources:
  - wiki/wave_fiveb_ticketed_writes_contract.md
  - wiki/wave_fiveb_freeze_independent_review.md
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
  - coverage/status.json
created: 2026-07-29T16:43:08Z
updated: 2026-07-29T16:43:08Z
---

# Wave-5b product fallback review

## Verdict

**REJECT** for the Wave-5b ticketed-write product at root commit `920ceab` on
`main.billy_complete`, compared with root baseline `85820b9`.

This is a read-only Codex Power fallback because the planned Grok review failed
at Grok authentication before doing any review work. It improves the product
gate, but it is **not** the mandatory independent Grok audit. That final Grok
audit remains pending after the defects below are fixed and the root is
re-reviewed.

The rejection is limited to the offline ticketed-write product gate. It makes
no live, UI, vision, bulk, special-route, or overall-completeness acceptance
claim.

## Scope and sources inspected

The complete `85820b9..920ceab` diff was inspected. Product changes comprised
the two new write registrars, their focused tests, root server registration,
the coverage generator and generated API/status artifacts, and the root
registry test. Root `.fractal/` planning and memory changes were excluded from
product findings.

The review compared these committed surfaces with the cited contract and
design:

- `src/billy_mcp/api/account_writes.py` and
  `tests/api/test_account_writes.py`;
- `src/billy_mcp/api/daybook_balance_account_writes.py` and
  `tests/api/test_daybook_balance_account_writes.py`;
- shared `src/billy_mcp/api/write_protocol.py`,
  `src/billy_mcp/confirmations.py`, and their focused unit tests;
- `src/billy_mcp/server.py` and `tests/unit/test_coverage_server.py`;
- `scripts/generate_coverage_report.py`, `scripts/check_coverage.py`,
  `coverage/api_v2_manifest.yaml`, `coverage/status.json`, and
  `coverage/report.md`;
- `wiki/wave_fiveb_ticketed_writes_contract.md`,
  `wiki/wave_fiveb_freeze_independent_review.md`, and the approved design at
  `docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md`, especially
  its shared-store, matching-executor, preview/execute, and generated-coverage
  requirements.

## Clean-archive evidence

A disposable clean archive was created directly from `920ceab` with `git
archive`; all commands below ran in that archive. No Billy API call, browser,
credential, or live test was used.

| Check | Result |
| --- | --- |
| `git diff --check 85820b9 920ceab` | Pass |
| Focused pytest: both Wave-5b write suites, confirmation store, write protocol, root registry, and coverage inventory | **103 passed** |
| Coverage checker with `--reject-false-completeness` | Pass: 305 API rows and 339 UI rows |
| Coverage checker with `--require-complete` | Correctly failed: `complete=false`, 92 ambiguous bulk rows, 305 API rows without live evidence, and 339 UI rows without full/vision evidence |
| Ruff over changed product/tests | Pass |
| Pyright over changed modules and server | Pass: 0 errors, warnings, or information items |

The tests prove the expected request roots, HTTP methods, percent-encoded IDs,
zero-write previews, replay/expiry/tamper handling, mapped responses, 18
Wave-5b registered tools, and nine offline evidence rows. They do not prove
that a ticket reaches only its matching execute tool; the reproduction below
shows the opposite.

## Actionable findings

### P1 — a ticket is accepted by an unrelated execute tool

`src/billy_mcp/api/write_protocol.py:183-202` takes only a ticket. It looks up
the prepared operation and consumes that operation's stored binding, but never
receives or compares the name of the invoked execute tool with
`prepared.binding.tool`. Every Wave-5b execute wrapper delegates in that form:
`src/billy_mcp/api/account_writes.py:92-248` and
`src/billy_mcp/api/daybook_balance_account_writes.py:76-141`.

The clean-archive reproduction registered both Wave-5b modules on one local
FastMCP server with an `httpx.MockTransport`, previewed
`api_accounts_create_preview`, then submitted the returned ticket to
`api_daybook_balance_accounts_delete_execute`. Instead of returning
`CONFIRMATION_MISMATCH`, it successfully issued the stored `POST /v2/accounts`
request and returned the account-create response. This violates the approved
design's requirement that a confirmation ticket is accepted only by its
matching execute tool and the Wave-5b contract's exact tool binding.

Fix the shared protocol to require the invoked execute-tool name, compare it
to the prepared binding before consuming or sending a request, and return the
stable mismatch error on a cross-executor attempt. Have every wrapper pass its
literal execute name. Add integration tests that preview each Wave-5b family
and call a different executor, asserting no HTTP request; the present focused
tests at `tests/api/test_account_writes.py:289-418` and
`tests/api/test_daybook_balance_account_writes.py:225-330` cover matching
execution and synthetic binding changes, but not this public-handler boundary.

### P2 — ticket state has no expiry cleanup path

`src/billy_mcp/confirmations.py:118-169` retains unredeemed `_records` until a
caller later tries to consume that exact ticket, and grows `_consumed` forever.
`src/billy_mcp/api/write_protocol.py:151-202` likewise never removes a
prepared request after successful or terminal execution. Consequently,
unredeemed previews retain their opaque request payloads after the five-minute
validity window and normal successful writes grow process memory for the life
of the server. This shared-protocol residual predates the Wave-5b leaf modules
but is exercised by all 18 newly registered executors.

Prune expired pending and consumed ticket state under the existing locks on
issue/consume, remove prepared requests on every terminal ticket outcome, and
bound any replay markers to the ticket expiry. Add clock-driven unit tests that
verify both state cleanup and preservation of the required single-use errors.

## Coverage and qualification state observed

The generated artifacts at `920ceab` are internally consistent and remain
fail-closed:

- The nine Wave-5b rows (`accountGroups`, `accounts`, and
  `daybookBalanceAccounts` create/update/delete) show
  `implemented=true` and `contract_tested=true`, but all nine retain
  `live_tested=false`. This review does not accept those offline claims because
  of P1 and does not alter the generated state.
- `coverage/status.json` reports 644 total rows: 305 API (207 clear, 92
  ambiguous bulk, six documented special routes) and 339 UI (305 API-parity,
  34 discovery). It reports 118 implemented and contract-tested rows, zero
  live-tested rows, zero vision-verified rows, and `complete=false`.
- All 92 bulk rows remain red with no bulk tools. All 339 UI and vision rows
  remain red. The four unimplemented special-route rows remain red; the two
  existing user special routes remain offline-only with `live_tested=false`.
  No special-route, live, UI, vision, bulk, or completeness qualification is
  accepted here.

## Required next gate

Correct P1 in the shared protocol and its public-handler tests, address the P2
retention issue, regenerate and verify coverage only if the corrected evidence
requires it, then request the still-mandatory independent Grok product audit.
Until that audit accepts a corrected root, Wave-5b must not be promoted as an
accepted product slice or as complete/live/UI/vision/bulk-qualified work.
