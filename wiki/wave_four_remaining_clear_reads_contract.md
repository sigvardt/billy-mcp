---
name: wave_four_remaining_clear_reads_contract
desc: Frozen official + live contract for Wave-4 remaining clear API get/list reads.
tags: [billy, api, read_only, wave4]
sources:
  - https://www.billy.dk/api/
  - .fractal/main.billy_complete/tmp/grok-research.md
created: 2026-07-29T11:55:00Z
updated: 2026-07-29T11:55:00Z
---

# wave_four_remaining_clear_reads_contract

This contract bounds the next read-only API wave after Wave-3. It freezes all
**50** remaining clear get/list operations. It is based on the cited
official-document brief with fingerprint `hsisik4g9p3603` /
`c2efda0ee4cf9cf200e14910c5fc6996` (re-verified 2026-07-29T11:52:46Z) plus
unauthenticated live probes on 2026-07-29T11:53:57Z–11:54:44Z. It is not an
implementation or live-test claim.

## Shared rules

- Use the locked `https://api.billysbilling.com/v2` client and relative paths
  without a `/v2` prefix.
- Each tool has flat Pydantic parameters (no nested `request` object), typed
  success models, and typed `ToolError`. No generic HTTP or browser controls.
- Default list inputs: `page`, `pageSize` (1–1000), optional `include`,
  optional free-form `sortProperty`, optional `sortDirection` in `ASC` | `DESC`.
  Reject `offset` and all unknown fields.
- Geo list inputs (cities, states, zipcodes) also require non-empty
  `countryId`. This is live-proven (HTTP 400 OTHER without it), not an official
  filter table. Do not invent further geo filters offline.
- Get inputs: required `id`, optional `include`.
- Response payloads stay opaque allow-extra objects; map only the documented
  singular/plural root keys and optional `meta.paging` (preserve the paging
  object in structured content).
- Contract tests cover path and query construction, unknown-key rejection,
  response roots, paging, typed 401 mapping, and geo `countryId` requirement.
  `live_tested` stays false without the dedicated non-production organisation
  and token.

## Owned tools and roots

### Geo (8)

| Resource | Tools | Singular root | List root | Paths | List extras |
| --- | --- | --- | --- | --- | --- |
| Country groups | `api_country_groups_get`, `api_country_groups_list` | `countryGroup` | `countryGroups[]` | `/countryGroups` | default |
| Cities | `api_cities_get`, `api_cities_list` | `city` | `cities[]` | `/cities` | require `countryId` |
| States | `api_states_get`, `api_states_list` | `state` | `states[]` | `/states` | require `countryId` |
| Zipcodes | `api_zipcodes_get`, `api_zipcodes_list` | `zipcode` | `zipcodes[]` | `/zipcodes` | require `countryId` |

Live notes: `countryGroups` is publicly readable without a token; cities,
states, and zipcodes validate `countryId` before auth (400 without it; 401 with
a non-empty value and no token).

### Tax (16)

| Resource | Tools | Singular root | List root | Paths |
| --- | --- | --- | --- | --- |
| Tax rates | `api_tax_rates_get`, `api_tax_rates_list` | `taxRate` | `taxRates[]` | `/taxRates` |
| Tax rate deduction components | `api_tax_rate_deduction_components_get`, `api_tax_rate_deduction_components_list` | `taxRateDeductionComponent` | `taxRateDeductionComponents[]` | `/taxRateDeductionComponents` |
| Sales tax rulesets | `api_sales_tax_rulesets_get`, `api_sales_tax_rulesets_list` | `salesTaxRuleset` | `salesTaxRulesets[]` | `/salesTaxRulesets` |
| Sales tax rules | `api_sales_tax_rules_get`, `api_sales_tax_rules_list` | `salesTaxRule` | `salesTaxRules[]` | `/salesTaxRules` |
| Sales tax accounts | `api_sales_tax_accounts_get`, `api_sales_tax_accounts_list` | `salesTaxAccount` | `salesTaxAccounts[]` | `/salesTaxAccounts` |
| Sales tax meta fields | `api_sales_tax_meta_fields_get`, `api_sales_tax_meta_fields_list` | `salesTaxMetaField` | `salesTaxMetaFields[]` | `/salesTaxMetaFields` |
| Sales tax returns | `api_sales_tax_returns_get`, `api_sales_tax_returns_list` | `salesTaxReturn` | `salesTaxReturns[]` | `/salesTaxReturns` |
| Sales tax payments | `api_sales_tax_payments_get`, `api_sales_tax_payments_list` | `salesTaxPayment` | `salesTaxPayments[]` | `/salesTaxPayments` |

### Bank / balance (10)

| Resource | Tools | Singular root | List root | Paths |
| --- | --- | --- | --- | --- |
| Bank payments | `api_bank_payments_get`, `api_bank_payments_list` | `bankPayment` | `bankPayments[]` | `/bankPayments` |
| Bank line matches | `api_bank_line_matches_get`, `api_bank_line_matches_list` | `bankLineMatch` | `bankLineMatches[]` | `/bankLineMatches` |
| Bank lines | `api_bank_lines_get`, `api_bank_lines_list` | `bankLine` | `bankLines[]` | `/bankLines` |
| Bank line subject associations | `api_bank_line_subject_associations_get`, `api_bank_line_subject_associations_list` | `bankLineSubjectAssociation` | `bankLineSubjectAssociations[]` | `/bankLineSubjectAssociations` |
| Balance modifiers | `api_balance_modifiers_get`, `api_balance_modifiers_list` | `balanceModifier` | `balanceModifiers[]` | `/balanceModifiers` |

### Contact balance + invoice extensions (10)

| Resource | Tools | Singular root | List root | Paths |
| --- | --- | --- | --- | --- |
| Contact balance payments | `api_contact_balance_payments_get`, `api_contact_balance_payments_list` | `contactBalancePayment` | `contactBalancePayments[]` | `/contactBalancePayments` |
| Contact balance postings | `api_contact_balance_postings_get`, `api_contact_balance_postings_list` | `contactBalancePosting` | `contactBalancePostings[]` | `/contactBalancePostings` |
| Invoice late fees | `api_invoice_late_fees_get`, `api_invoice_late_fees_list` | `invoiceLateFee` | `invoiceLateFees[]` | `/invoiceLateFees` |
| Invoice reminders | `api_invoice_reminders_get`, `api_invoice_reminders_list` | `invoiceReminder` | `invoiceReminders[]` | `/invoiceReminders` |
| Invoice reminder associations | `api_invoice_reminder_associations_get`, `api_invoice_reminder_associations_list` | `invoiceReminderAssociation` | `invoiceReminderAssociations[]` | `/invoiceReminderAssociations` |

### Ledger + users (6)

| Resource | Tools | Singular root | List root | Paths |
| --- | --- | --- | --- | --- |
| Transactions | `api_transactions_get`, `api_transactions_list` | `transaction` | `transactions[]` | `/transactions` |
| Postings | `api_postings_get`, `api_postings_list` | `posting` | `postings[]` | `/postings` |
| Users | `api_users_get`, `api_users_list` | `user` | `users[]` | `/users` |

`api_users_*` is the `/v2/users` resource. It is distinct from the already-green
specials `api_user_get` (`GET /v2/user`) and `api_user_list_organizations`.

## Sensitivity notes

- Redact user and contact emails; redact phone numbers if they appear in logs.
- Redact token query values on `downloadUrl` (invoice reminders, files).
- Redact bank identifiers if account embeds appear via `include`.

## Supports flags relevant later (not implemented here)

- Several resources omit singular delete or create on the official Supports
  line (e.g. users: no create/delete; salesTaxReturns: no create/delete;
  invoiceReminders: no update/delete). Inventory already encodes clear ops from
  Supports; Wave-4 only implements get/list.
- Writes, bulk, and specials stay red.

## Offline integration evidence

After implementation, the root server must register exactly these 50 tools in
addition to the prior 44 offline-green read tools (**94** `api_*` + 2
`coverage_*`). Each new tool has a focused contract suite and a root registry
assertion. Coverage records only `implemented: true` and `contract_tested: true`
for the matching API rows. Every `live_tested` field stays false, all
interface/vision rows stay red, and generated `complete` remains false.

## Exclusions

This wave excludes every write, preview/execute flow, bulk operation, files
upload, invoice email/delivery/logs specials, invented non-geo filters, browser
authentication, UI workflows, and any live or vision coverage transition.
