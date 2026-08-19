---
name: todo
desc: Open product work for the UI write lane.
tags: [todo]
sources: []
created: 2026-08-16T14:29:47Z
updated: 2026-08-19T18:55:00Z
---

## Open

- Residual five are `out_of_scope_by_user` (`FE6FA4B1`). Do not remake dumps. Do not arm `_ledger_write`. `complete` stays false on bulk92. Do not finish.
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
