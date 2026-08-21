---
name: wave_fivec_ticketed_writes_contract
desc: Cited offline ticketed-write contract for Billy daybook transactions and transaction lines.
tags: [billy, api, writes, coverage]
sources:
  - https://www.billy.dk/api/
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
  - wiki/wave_five_ticketed_writes_contract.md
  - wiki/wave_fiveb_repair_independent_review.md
  - coverage/api_v2_manifest.yaml
created: 2026-07-29T17:34:35Z
updated: 2026-07-29T17:34:35Z
---

# wave_fivec_ticketed_writes_contract

## Scope

This contract freezes the documented offline-only singular CUD cohort for
`daybookTransactions` and `daybookTransactionLines`. It authorizes the six API
operations below, their preview/execute twins, and contract tests. It does not
authorize live qualification, bulk tools, special routes, UI work, browser
work, or a completeness claim.

Grok re-fetched the official Billy API documentation at ETag
`hsisik4g9p3603`, MD5 `c2efda0ee4cf9cf200e14910c5fc6996`, and 147934 bytes.
That document was byte-identical to the existing inventory freeze. The cited
research brief is kept in node scratch; this page is its durable shared
contract.

## Frozen operations

| Inventory id | Preview tool | Execute tool | Method and client path | Request root | Response root |
| --- | --- | --- | --- | --- | --- |
| `api.daybookTransactions.create` | `api_daybook_transactions_create_preview` | `api_daybook_transactions_create_execute` | `POST /daybookTransactions` | `daybookTransaction` | `daybookTransactions` |
| `api.daybookTransactions.update` | `api_daybook_transactions_update_preview` | `api_daybook_transactions_update_execute` | `PUT /daybookTransactions/:id` | `daybookTransaction` | `daybookTransactions` |
| `api.daybookTransactions.delete` | `api_daybook_transactions_delete_preview` | `api_daybook_transactions_delete_execute` | `DELETE /daybookTransactions/:id` | none | `daybookTransactions` |
| `api.daybookTransactionLines.create` | `api_daybook_transaction_lines_create_preview` | `api_daybook_transaction_lines_create_execute` | `POST /daybookTransactionLines` | `daybookTransactionLine` | `daybookTransactionLines` |
| `api.daybookTransactionLines.update` | `api_daybook_transaction_lines_update_preview` | `api_daybook_transaction_lines_update_execute` | `PUT /daybookTransactionLines/:id` | `daybookTransactionLine` | `daybookTransactionLines` |
| `api.daybookTransactionLines.delete` | `api_daybook_transaction_lines_delete_preview` | `api_daybook_transaction_lines_delete_execute` | `DELETE /daybookTransactionLines/:id` | none | `daybookTransactionLines` |

All relative paths omit `/v2`; the locked client alone supplies
`https://api.billysbilling.com/v2`. Create and update bodies contain exactly
one singular root. Update is partial. Delete binds `{"id": "<id>"}` in the
ticket and sends no HTTP body. The response mapper starts with the documented
plural root plus optional `meta.deletedRecords`; it must not claim parent or
line multi-root responses without live evidence.

All six rows are clear, medium-sensitivity CUD operations with no filters or
pagination. The documented error inventory includes
`AUTHENTICATION_REQUIRED` and `OAUTH_INVALID_ACCESS_TOKEN`; the MCP maps the
established missing/invalid-token shape to `AUTH_REQUIRED`. The existing rows'
cleanup contract remains dedicated disposable-record deletion and restoration;
no unauthenticated response is cleanup proof.

## Documented payload boundaries

The typed MCP outer inputs forbid undeclared fields while accepting an opaque
`dict[str, JsonValue]` payload under the documented singular root. This
preserves the official field contract without inventing a separate partial
schema.

`daybookTransaction` documents immutable required `organizationId` and
`entryDate`; optional `daybookId`, `voucherNo`, `description`,
`extendedDescription`, `apiType`, and `priority`; default state `draft`; and
immutable has-many `lines` and `attachments`. At least one line is required
when creating with embedded lines. The embedded-save shape, state transitions,
and parent-plus-line response roots remain live-test questions.

`daybookTransactionLine` documents immutable required
`daybookTransactionId`, account identity (`accountId` or `accountNo`), `amount`,
and `side` (`debit` or `credit`); optional immutable `taxRateId`,
`contraAccountId`, and `currencyId`; plus optional `text` and `priority`. The
apparent update support versus immutable line fields remains a live validation
question, not a reason to omit the documented PUT tool.

## Required ticketed-write protocol

- Reuse the server's one `ConfirmationStore` and `WriteProtocolService`; no
  leaf may create a second store or mutate the shared protocol.
- Preview validates, performs no Billy mutation, and creates an opaque
  short-lived single-use ticket bound to the exact tool, organisation, target,
  canonical request, and expected effect.
- Every `WriteOperationSpec` declares its literal non-empty
  `execute_tool_name`. Every execute handler passes that same server-owned
  literal to `WriteProtocolService.execute` and accepts only
  `confirmation_ticket` with extras forbidden.
- A wrong executor must return `CONFIRMATION_MISMATCH` before consuming the
  ticket or issuing HTTP. The valid bound executor must still be able to use its
  ticket once. Prepared payloads and expired bindings remain subject to the
  accepted P1/P2 pruning behaviour.
- Mutations make one `client.request` call only; no retry policy is allowed.
  Contract tests prove exact method, path, body, zero-write preview,
  tamper/replay/expiry/wrong-binding errors, outer-extra rejection, and both
  same-module and cross-module executor mismatch.

## Offline coverage target

After the six operations are implemented and their contract suites plus server
registration pass, their inventory rows may set `implemented: true` and
`contract_tested: true`. The expected offline totals are 154 `api_*` tools,
124 implemented/contract-tested API rows, zero live rows, zero vision rows, and
`coverage/status.json` with `complete: false`. Evidence references must point
to each focused module suite and the root server-registry test.

## Qualification boundaries

- Current unauthenticated probes give POST/PUT 401, GET-by-id 404, and DELETE
  empty 200 for both collections. The DELETE response is not cleanup or live
  evidence; no `live_tested` flag changes here.
- Bulk save and bulk delete retain empty tool names among the 92 ambiguous rows:
  current documentation gives no request or response-body contract.
- `postings` and `accountNatures` CUD probes return 405 despite Supports flags;
  they stay outside this cohort pending authenticated evidence or authoritative
  clarification.
- Ledger `transactions`, invoices, bills, attachments, files, special routes,
  UI parity, browser authentication, and vision verification are not included.
- No webhook is documented; this contract authorizes no webhook or generic
  network capability.
