---
name: wave_three_unfiltered_reads_contract
desc: Frozen official contract for Wave-3 unfiltered clear API get/list reads.
tags: [billy, api, read_only, unfiltered]
sources:
  - https://www.billy.dk/api/
  - .fractal/main.billy_complete/tmp/grok-research.md
created: 2026-07-29T11:05:00Z
updated: 2026-07-30T17:37:00Z
---

# wave_three_unfiltered_reads_contract

This contract bounds the next read-only API wave after Wave-2 filtered reads.
It is based on the cited official-document brief with fingerprint
`hsisik4g9p3603` / `c2efda0ee4cf9cf200e14910c5fc6996` (re-verified
2026-07-29T11:02:40Z). It is not an implementation or live-test claim.

## Shared rules

- Use the locked `https://api.billysbilling.com/v2` client and relative paths
  without a `/v2` prefix.
- Each tool has Pydantic input and success models and returns typed
  `ToolError`; no generic HTTP or browser controls are allowed.
- Every list accepts only `page`, `pageSize` (1–1000), optional `include`,
  optional free-form `sortProperty`, and optional `sortDirection` in
  `ASC` | `DESC`. Offset paging is not permitted.
- No resource-specific list filters are documented for these resources. Do not
  invent parent-id filters such as `invoiceId` or `contactId` offline.
- Response payloads stay opaque allow-extra objects; map only the documented
  singular/plural root keys and optional `meta.paging`.
- Contract tests cover path and query construction, local unknown-filter
  rejection, response roots, paging, typed 401 mapping, and redaction for bank
  fields and file `downloadUrl` tokens. `live_tested` stays false without the
  dedicated non-production organisation and token.

## Owned tools and roots

| Resource | Tools | Singular root | List root | Paths |
| --- | --- | --- | --- | --- |
| Invoice lines | `api_invoice_lines_get`, `api_invoice_lines_list` | `invoiceLine` | `invoiceLines[]` | `/invoiceLines` |
| Bill lines | `api_bill_lines_get`, `api_bill_lines_list` | `billLine` | `billLines[]` | `/billLines` |
| Daybook transaction lines | `api_daybook_transaction_lines_get`, `api_daybook_transaction_lines_list` | `daybookTransactionLine` | `daybookTransactionLines[]` | `/daybookTransactionLines` |
| Contact persons | `api_contact_persons_get`, `api_contact_persons_list` | `contactPerson` | `contactPersons[]` | `/contactPersons` |
| Daybooks | `api_daybooks_get`, `api_daybooks_list` | `daybook` | `daybooks[]` | `/daybooks` |
| Daybook balance accounts | `api_daybook_balance_accounts_get`, `api_daybook_balance_accounts_list` | `daybookBalanceAccount` | `daybookBalanceAccounts[]` | `/daybookBalanceAccounts` |
| Accounts | `api_accounts_get`, `api_accounts_list` | `account` | `accounts[]` | `/accounts` |
| Account groups | `api_account_groups_get`, `api_account_groups_list` | `accountGroup` | `accountGroups[]` | `/accountGroups` |
| Account natures | `api_account_natures_get`, `api_account_natures_list` | `accountNature` | `accountNatures[]` | `/accountNatures` |
| Files | `api_files_get`, `api_files_list` | `file` | `files[]` | `/files` |
| Attachments | `api_attachments_get`, `api_attachments_list` | `attachment` | `attachments[]` | `/attachments` |

## Sensitivity notes

- Accounts expose readonly bank identifiers (`bankName`, `bankRoutingNo`,
  `bankAccountNo`, `bankSwift`, `bankIban`). Redact them in logs even when the
  inventory sensitivity field remains low.
- Files expose `downloadUrl` values that may include download tokens on
  `download.billy.dk`. Redact tokens; do not treat download as a generic fetch.
- Contact persons expose email addresses; apply existing redaction rules.

## Supports flags relevant to later waves (not implemented here)

- Account natures: no singular delete in Supports (inventory already omits it).
- Files: Supports list create but no update and no singular delete; the only
  documented create path is raw-binary `POST /v2/files` with
  `X-Filename` and optional `x-create-attachment`, `x-create-variants`,
  `x-organizationid`, `x-should-scan`. Never call the sample host
  `api.billy.dk`. Inventory currently has both `api.files.create` and
  `api.special.files_upload`; resolve to one raw-binary tool in the write wave.
- Attachment linking via parent `attachmentIds` arrays is write-wave only.

## Offline integration evidence

The root server must register exactly these 22 tools in addition to the prior
22 offline-green read tools. Each has a focused contract suite and a root
registry assertion. The coverage generator records only `implemented: true` and
`contract_tested: true` for the matching API rows. Every `live_tested` field
stays false, all interface/vision rows stay red, and generated `complete`
remains false.

## Exclusions

This wave excludes every write, preview/execute flow, bulk operation, files
upload, invoice email/delivery/logs specials, invented parent filters, browser
authentication, UI workflows, and any live or vision coverage transition.
