---
name: wave_fiveb_ticketed_writes_contract
desc: Cited offline ticketed-write contract for Billy account groups, accounts, and daybook balance accounts.
tags: [billy, api, writes, coverage]
sources:
  - https://www.billy.dk/api/
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
  - wiki/wave_five_ticketed_writes_contract.md
  - coverage/api_v2_manifest.yaml
created: 2026-07-29T16:12:51Z
updated: 2026-07-29T16:12:51Z
---

# wave_fiveb_ticketed_writes_contract

## Scope

This contract freezes the next offline-only singular CUD cohort after the
accepted Wave-5a registration: account groups, accounts, and daybook balance
accounts. It authorizes implementation and contract tests only. It does not
authorize live qualification, bulk tools, special routes, interface work, or a
completeness claim.

The official Billy API documentation fingerprint is ETag `hsisik4g9p3603`, MD5
`c2efda0ee4cf9cf200e14910c5fc6996`, and 147934 bytes. It matches the existing
inventory freeze.

## Frozen operations

| Inventory id | Preview tool | Execute tool | Method and client path | Request root | Response root |
| --- | --- | --- | --- | --- | --- |
| `api.accountGroups.create` | `api_account_groups_create_preview` | `api_account_groups_create_execute` | `POST /accountGroups` | `accountGroup` | `accountGroups` |
| `api.accountGroups.update` | `api_account_groups_update_preview` | `api_account_groups_update_execute` | `PUT /accountGroups/:id` | `accountGroup` | `accountGroups` |
| `api.accountGroups.delete` | `api_account_groups_delete_preview` | `api_account_groups_delete_execute` | `DELETE /accountGroups/:id` | none | `accountGroups` |
| `api.accounts.create` | `api_accounts_create_preview` | `api_accounts_create_execute` | `POST /accounts` | `account` | `accounts` |
| `api.accounts.update` | `api_accounts_update_preview` | `api_accounts_update_execute` | `PUT /accounts/:id` | `account` | `accounts` |
| `api.accounts.delete` | `api_accounts_delete_preview` | `api_accounts_delete_execute` | `DELETE /accounts/:id` | none | `accounts` |
| `api.daybookBalanceAccounts.create` | `api_daybook_balance_accounts_create_preview` | `api_daybook_balance_accounts_create_execute` | `POST /daybookBalanceAccounts` | `daybookBalanceAccount` | `daybookBalanceAccounts` |
| `api.daybookBalanceAccounts.update` | `api_daybook_balance_accounts_update_preview` | `api_daybook_balance_accounts_update_execute` | `PUT /daybookBalanceAccounts/:id` | `daybookBalanceAccount` | `daybookBalanceAccounts` |
| `api.daybookBalanceAccounts.delete` | `api_daybook_balance_accounts_delete_preview` | `api_daybook_balance_accounts_delete_execute` | `DELETE /daybookBalanceAccounts/:id` | none | `daybookBalanceAccounts` |

All relative paths omit `/v2`; the client alone locks the API base to
`https://api.billysbilling.com/v2`. Create and update bodies contain exactly
one singular root. Delete binds `{"id": "<id>"}` in the ticket and sends no
HTTP body. The server maps documented changed records and optional
`meta.deletedRecords` without inventing missing roots.

## Required protocol

- Reuse the root's single `ConfirmationStore` and `WriteProtocolService`.
- Preview validates a typed outer input with forbidden extras, performs no
  write, and returns an opaque ticket with at least 256 bits of entropy and a
  lifetime no longer than five minutes.
- Execute accepts only `confirmation_ticket`, consumes it once, and restores
  the exact stored tool, organisation, target, canonical request, and expected
  effect.
- The payload remains an opaque `dict[str, JsonValue]` inside the typed outer
  model. Do not create a second protocol or retry a mutation.
- Contract tests prove preview makes no HTTP request; execute sends the exact
  method, path, and body; ticket tamper, replay, expiry, and binding mismatches
  fail closed; and outer extra fields are rejected.

## Qualification boundaries

- The nine inventory rows may become implemented and contract-tested after
  passing offline implementation tests, but remain `live_tested: false`.
- Unauthenticated POST returns 401. The account-groups PUT and GET-by-id 404
  quirk still maps through the stable 404 path; it is not a success case.
- An unauthenticated DELETE's empty 200 response is not cleanup or live-test
  evidence and never authorizes a green row.
- The 92 bulk rows remain ambiguous and have no tools.
- `accountNatures` and `postings` CUD operations remain out of this cohort:
  current unauthenticated POST, PUT, and DELETE probes return 405 despite some
  documentation support flags. They need authenticated non-production evidence
  or authoritative clarification before implementation.
- Files, invoice email or delivery, invoice logs, browser authentication, UI
  parity, and vision evidence remain outside this contract.
