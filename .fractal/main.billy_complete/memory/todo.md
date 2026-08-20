---
name: todo
desc: Open product work after official docs lock promote.
tags: [todo]
sources: []
created: 2026-08-16T14:29:47Z
updated: 2026-08-20T13:55:05Z
---

## Open

- Binding `3DA6FB8E` done: independent review PASS on `df2f475`; owner-input outbox posted; unsaved. Residual still bulk92 plus six `READONLY_PROPERTY_TABLE` rows and six UI owner-scope rows. `complete` stays false. Wait for owner scope.
- Binding `88C4B0A9`: residual audit committed. Official lock now `pi4s9u10j037qn` / `d805f3d2bb8e339f7635d6834b4011bd` after bankLines list-filter relock. Owner input still required on bulk92 plus six readonly-map rows. Do not implement guessed tools. `complete` stays false.
- Typed `api_bank_lines_list` filters landed. `accountId` required. Shared `BankListRequest` unchanged. Independent review PASS.
- Binding `9B979A05`: remaining residual honesty is 6 readonly-map. Method-closed remaining is 0. Bulk92 stay unspecified. Never infer a common bulk shape. Unresolved stay red. No live API. Do not finish.
- Residual five are `out_of_scope_by_user` (`FE6FA4B1`). Do not remake dumps. Do not arm `_ledger_write`. `complete` stays false on bulk92.
- Owner `D71E5B82` still binds: reusable invoice CUD must pass `ui-full` after settled zero with no `LEFTOVER_*` hard-fail.
- `A337A622` still forbids more product list, dialog, or archive probes.
- Daybook persist is not unique. Files have no UI delete. **Godkend** stays prohibited.
- `1F1B34F8`: offline preview rejects an unpriced line. Live **Enhedspris** fill proved. Leftover reverse-clean is done. Do not remake leftover lists.
- Residual invoice create is no longer a stop on `67CBACB6`. Product hard-delete is owner-proved. Daybook and files still wait. Do not add classify helpers.
- Invoice draft CUD is mandatory (`FD39FFE7`). Prior `UI_CHANGED` bind dumps are unverified against the owner-visible session. `113F1E05` still forbids another entry-CTA dump. Never send, approve, or email.
- Product create is mandatory (`FD39FFE7`) and live-proved. `56354201` / `BF91E28F` cleanup is scoped table-item `delete-icon` then **Ja, slet**. `A337A622` still forbids more product list, dialog, or archive probes. Do not remake form-contract, delete-chrome, leftover-cleanup, or either archive dump.
- Daybook create persist is not unique (`opret_ny_kassekladde_count=1` and `indstillinger_count=1`). Helper dropped after review. Do not remake that dump. Do not arm `_ledger_write`. Stay red.
- After live MCP proof: point remaining CUD parity rows at preview tools. Invoice and product remaps are done. Do not green from stubs. Files stay fail-closed (research185 **Slet** 0).

## Done

- Binding `88C4B0A9` residual audit: unimplemented API set is exactly bulk92 plus six readonly-map rows. Census tests and evidence ref `research-88c4b0a9-residual-audit` landed. Independent review PASS. Owner input required. Unsaved after the owner-input report.
- Binding `A485F530` honesty remap committed on `e995411`. Six create/update rows stay toolless/red (`readonly_field_map_insufficient` / `READONLY_PROPERTY_TABLE`). Independent review PASS. Unsaved.
- Binding `A485F530` research: official property tables for `contactBalancePostings`, `postings`, and `transactions` create/update are all readonly or immutable. First-party bundles GET only. No writable field map. Honesty remap: six rows `readonly_field_map_insufficient`. No tools.
- Binding `7B947636`: ticketed offline `api.transactions.delete` in `src/billy_mcp/api/transaction_writes.py` landed on `bb66a48`. Preview `{id}` only. Execute `DELETE /transactions/:id` with no body. Residual honesty remaining 6. Independent review PASS. Unsaved.
- Binding `4DBD7C3F`: ticketed offline `api.invoiceReminderAssociations.delete` in `src/billy_mcp/api/invoice_reminder_association_writes.py` landed on `da833d3`. Preview `{id}` only. Execute `DELETE /invoiceReminderAssociations/:id` with no body. Residual honesty remaining 7. Independent review PASS. Unsaved.
- Binding `7453B98F`: ticketed offline `api.balanceModifiers.create` and `.update` in `src/billy_mcp/api/balance_modifier_writes.py` landed on `5a1bde8`. Nested required `modifier` and `subject` strings, `extra=forbid`. Readonly `amount`/`entryDate`/`realizedCurrencyDifference`/`isVoided` and `modifierId`/`subjectId` rejected. Residual honesty remaining 8. Independent review PASS. Unsaved.
- Binding `8FE83270`: ticketed offline `api.zipcodes.create` and `.update` in `src/billy_mcp/api/zipcode_writes.py` landed on `b95f96f`. Nested optional `zipcode`, belongs-to `city`/`state`/`country`, and float `latitude`/`longitude`, `extra=forbid`. `zipcodeId`/`cityId`/`stateId`/`countryId` rejected. Residual honesty remaining 10. Independent review PASS. Unsaved.
- Binding `AB6ABE84`: ticketed offline `api.states.create` and `.update` in `src/billy_mcp/api/state_writes.py` landed on `850c80a`. Nested optional `stateCode`, `name`, and belongs-to `country` strings, `extra=forbid`. `stateId`/`countryId` rejected. Residual honesty remaining 12. Independent review PASS. Unsaved.
- Binding `05F3200D`: ticketed offline `api.locales.create` and `.update` in `src/billy_mcp/api/locale_writes.py` landed on `113810e`. Nested optional `name` and `icon` strings, `extra=forbid`. `localeId` rejected. Residual honesty remaining 14. Independent review PASS. Unsaved.
- Binding `47B85E43`: ticketed offline `api.currencies.create` and `.update` in `src/billy_mcp/api/currency_writes.py`. Nested optional `name` string and `exchangeRate` float, `extra=forbid`. `currencyId` rejected. Residual honesty remaining 16. Independent review PASS. Committed.
- Binding `4DE5EE18`: ticketed offline `api.countries.create` and `.update` committed on `5e78f1d`. Nested optional string `name`, boolean `hasStates`, `hasFiniteStates`, `hasFiniteZipcodes`, string `icon`, and string `locale`, `extra=forbid`. `localeId` rejected. Official `#v2countries` Supports create and update; unauth 405 must not override that table. Residual honesty remaining 18. Independent review PASS. Unsaved.
- Binding `AF8E5A1F`: ticketed offline `api.countryGroups.create` and `.update` committed on `1b037a6`. Nested optional string `name`, `icon`, and `memberCountryIds`, `extra=forbid`. Arrays and `memberCountries` rejected. Residual honesty remaining 20. Independent review PASS. Unsaved.
- Binding `8C5F08A8`: ticketed offline `api.cities.create` and `.update`. Nested optional string `name`, `county`, `state`, and `country`, `extra=forbid`. `stateId`/`countryId` rejected. Residual honesty remaining 22. Independent review PASS.
- Binding `2D09964C`: ticketed offline `api.invoiceReminderAssociations.create` and `.update`. Nested required `reminder` and `invoice` strings, `extra=forbid`, `lateFee` rejected. Residual honesty remaining 24. Independent review PASS.
- Binding `B54A6BFC`: ticketed offline `api.bankPayments.delete`. Preview `{id}` only. Execute DELETE `/bankPayments/:id` with no body. Residual honesty remaining 26.
- Binding `EAB2F91B`: nested `AccountNaturePayload` is only `reportType`, `name`, `normalBalance` with `extra=forbid`. FastMCP preview schema is typed. `customField` and undocumented nested keys fail at the tool boundary. Enum members stay opaque strings. Empty payload is allowed because docs list no required fields.
- Binding `9B979A05` smallest cohort: ticketed offline `api.accountNatures.create` and `.update`. Residual honesty remaining 27. Independent review PASS on the cohort; typed payload is the FIX-VERIFY lock.
- Binding `89DEED22` lock: official fingerprint is `tmhc6wpdc835zt` / `053f755f52e3926b028e29325e3670d4`. Intro `GET /v2/organizations` is prose for `api.organizations.list`. Special `api_user_list_organizations` kept. Independent review PASS.
- Binding `7C9348E1`: every API row has `live_tested=false` and `live_api=out_of_scope_by_user`. Implemented rows are `live_api_deferred`. Completeness no longer requires API `live_tested=true`. Independent review PASS.
- Binding `FE6FA4B1`: five residual writes are `out_of_scope_by_user`. Flags stay false. Not `not_applicable`.
- Binding `58D7D0E1`: 11 accepted CUD rows are `preview_execute`. Independent review passed. `complete` stays false.
- Independent accept and purge of product CUD run `29c1b1de26a14976aaa1b98bfe9de46e`. Coverage names `ui_products_create_preview`.
- Independent accept and purge of invoice CUD run `60b6d620772644f3bca9609c8ae53846`. Coverage names `ui_invoices_{create,update,delete}_preview`. Live CUD uses `write_live_pending_unless_accepted`. Honesty-16 still red.
- 16-row gate, honesty, shared protocol, durable preview/execute invariant, `ui-full` mode.
- Seven family children landed offline preview/execute tools and are merged.
- `create_server` requires `organization_id` and reaches a shared `BrowserRuntime` actor. Commit-mode suite and lint pass. No greening.
- Ticket org is compared to the live URL slug before fill or click. Contacts no longer read a stored identity file for that compare. Read-back starts a second runtime. Shared fake records are gone.
- READY returns `organization_id`. DualSessionLogin READYs write then `-readback`.
- Live write tests cannot self-approve vision or purge frames (`C7DBE974` gate).
- Exact-text Ret and Slet-kontakt-as-link helpers, with unit tests. Substring Ret is documented as Opret.
- Five leftover `MCP-UI-C-*` contacts deleted through FastMCP. Fresh session empty.
- Exact-name read-back: `{tag}` is not present inside `{tag}-U`.
- Delete confirm label is **Ja, slet**.
- Browser egress PUT `/v2/contacts/:id` only. Live FastMCP contacts CUD passed. Success execute keeps redacted PUT persist fields.
- Durable contacts CUD vision record is accept with purge verified. Frame folder `run-3d5b151dfd5342258f8734373597f8c1` is gone.
- Contacts CUD `tool_name` values are `ui_clients_{create,update,delete}_preview`. Honesty 16 stays red. `ui_clients_update_open` and `ui_clients_delete_open` stay registered via `RETAINED_OPEN_SHELL_TOOLS`.
- Page-wide vendor tag click removed. `evaluate` removed. Six-selector walk removed. Unit inspect dumps isolated. Scoped wrapper dump exists.
- Portal create-footer picker skips decoy lists and huge ancestors. Live vendor bind is `scoped:portal_footer`.
- Date fill works without a prior click (`value_len` 10). Amount fill without a prior click reaches **Gem som kladde**. A leftover-footer count error is not a bind.
- Draft save `force=True` is gone. Offline owner save-dump overwrite is closed.
- Existing-option bind wins over create footer. Dropzone wrapper is not leftover. Live FastMCP draft-bill CUD passed with `vendor_bind=scoped:existing_option`.
- Bills CUD `tool_name` values are `ui_bills_{create,update,delete}_preview`. Honesty 16 stays red. `ui_bills_update_open` and `ui_bills_delete_open` stay registered via `RETAINED_OPEN_SHELL_TOOLS`.
- Invoice Kunde opener dump records the `5E1EDFB4` ownership fields. Live recapture has every key. `named_opener` is still null. Hit target is the contact `INPUT`.
- Dummy 15-char `after_type` is not an existing-customer observation. Helper `after_type_is_existing_customer_observation` requires `MCP-UI-INV-` + 8 hex and matching `value_len`. Typed-only stays unbound.
- Live FastMCP created that 19-char customer and typed it into the proved `INPUT`. Still no visible option. `UI_CHANGED`. Contact deleted.
- DIV ownership dump delivered. Overlay click ran. No option. `UI_CHANGED`. Do not repeat that click.
- Instrumented tagged-Kunde trace delivered (`8EFD0EAD`). Listeners first. Typed existing customer `value_len=19`. No contacts request, no portal, no option. `UI_CHANGED`. Contact deleted. Do not repeat that uninstrumented flow.
- Event/pageerror dump delivered (`4A5CD1E7`). Rest pageerror marked unrelated. After type: `input=19` `keydown=19` `change=0`. One change event dispatched. Still `UI_CHANGED`.
- `F12B607E` route-key dump delivered. Five rest bootstraps are `user` x3, `organizations` x1, unnamed `other_v2` x1. No contact-adjacent preload. Field shot and owner templates purged. Tagged customer deleted.
- Control-contract helper and failing fixture landed (`452E0773`). Live dump named `click_open` on the `pickerfield` wrapper. One wrapper click. `option_role_count=0`. `UI_CHANGED`. No customer created. Binding unsaved.
- Post-click helper and failing fixture landed (`07600147`). Live dump: hidden subtree 2, one `pickerfield` click, `changed_node_count=0`, `exact_match_target=false`, `UI_CHANGED`. Tagged customer deleted. Absence proved. Dump is committed on `1936b7c`.
- Descendant helper and failing fixture landed (`E87B6AEF`). Live dump: two visible descendants, overlay suffix excluded, `unique_target=false`, `wrapper_handler_guard=none`, `UI_CHANGED`. No customer. No click.
- Ember inspect helper and failing fixture landed (`31B0C7A6`). Live dump: `lookup_class=view_registry`, `view_constructor_token=pickerfield`, no allowlisted selection, collection, open state, or methods, `unique_normal_action=false`, `UI_CHANGED`. No click. No customer. Do not remake.
- Fiber inspect helper and failing fixture landed. Live dump: `fiber_key_class=none`, `wrapper_fiber_key_class=none`, no named action, `unique_fiber_host=false`, `unique_normal_action=false`, `UI_CHANGED`. No click. No customer. Do not remake.
- Listener-contract helper and failing fixture landed. Live dump: nine rows, empty property categories, no accepted key, no named invoke, `unique_normal_action=false`, `UI_CHANGED`. No click. No customer. Do not remake.
- Structure compare closed on `8feb636`. Kunde `pickerfield` versus bills `input_wrapper`. `same_family=false`. `transferable_action=none`. `UI_CHANGED`. Do not remake. Do not copy the bills wrapper.
- Customer-detail **Opret faktura** inspect closed. Path `contacts_customer`, **Ret** 1, **Opret faktura** 0, `proved_prebind=none`, `UI_CHANGED`. Customer deleted. Absence proved. Do not remake.
- Product delete-chrome recapture closed. **Mere** opened. **Slet** counts 0. Create form open. Save token `other`. `proved_delete_path=none`. No product created. Do not remake.
- Organizations update accepted and purged. `tool_name` is `ui_organizations_update_preview`. Honesty still red.
- Draft-save validation-open dump delivered. `gem_clicked=true`, `invoice_persisted=false`, `opret_ny_count=1`, `option_role_count=0`, `proved_bind=none`. Page-wide **Opret ny** is not a proved list open. Leftover tagged customer deleted. Absence 0.
- Scoped post-validation dump delivered. Contact input and pickerfield present. Two `validation` rows above the input. `unique_action=none`. `proved_bind=none`. Tagged customer deleted. Absence proved. Do not remake.
- Official invoice-list **Opret faktura** landing delivered. Empty list, one button click, destination `invoices_new`, contact empty, `proved_bind=none`. Tagged customer deleted. Do not remake.
- Official product dialog contract delivered. Live dump: `proved_submit=gem_produkt`, `unique_cleanup_path=archive_checkbox`. No product created. Persist fail-closed. Do not remake.
- Product list archive-filter classify delivered. Live dump: named filter counts 0, `unique_restore_readback=none`. No product created. Do not remake.
