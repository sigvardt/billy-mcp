---
name: todo
desc: Open product work for the UI write lane.
tags: [todo]
sources: []
created: 2026-08-16T14:29:47Z
updated: 2026-08-16T14:29:47Z
---

## Open

- Finish live FastMCP draft-bills CUD: bind the vendor typeahead (existing contact or **Opret** + **Opret leverandør** **Gem**), then date/amount, pre-submit dump, POST create, **Opdater** PUT, tagged **Slet**. Keep honesty 16 red. Do not remap bills yet.
- Parent `31F6E753` dump is implemented offline. Live still fails before click because vendor select does not stick.
- After bills accept+purge: point only the three bills CUD rows at preview tools.
- After live MCP proof: point the remaining 10 CUD parity rows at preview tools. Do not green from stubs. Keep a retained-open allowlist for any open-shell tool that still has live form-open tests.
- Ledger last. Files bind path+digest. Org update restores company fields only.

## Done

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
