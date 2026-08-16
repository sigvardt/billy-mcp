---
name: decisions
desc: Binding owner scope and qualification decisions for this node.
tags: [owner, scope]
sources:
  - radio:96908DC6
  - radio:DC3B8E96
created: 2026-08-16T13:50:50Z
updated: 2026-08-16T13:50:50Z
---

## Binding now

`96908DC6` (saved): complete UI writes and finish the MCP. Interface first. API live testing still deferred. Supersedes `9FD3042F` (read/open-only) and `3F11A9DF` (stop until explicit start).

`728BD2E4` (saved): no API-doc detour. Record the new docs fingerprint only. PLAN starts with the failing coverage test, then splits Grok-only children by independent UI write family. No HOLD. No BrowserRuntime-only qualification.

`E004E7D5` (saved): minimum failing-gate set is the 16 false-green parity rows (bills CUD, contacts CUD, daybooks create/delete, daybookTransactions create, files create, invoices CUD, organizations update, products create, transactions create). Still catch any other write row wrongly treated as complete.

`EE0A0F1B` (saved): durable TDD invariant is preview+execute twin, not "no ui_* preview/execute exist". Open-only status/tool can never green implemented/live/vision.

`DD80C9A8` (saved): node `test.sh` must accept `BILLY_TEST_MODE=ui-full` (offline API + live UI/vision, no live API), then require-complete and repository policy.

Use only the Grok CLI for this node and any child (`--agent=grok`). Qualify UI tools through the real MCP boundary, not direct BrowserRuntime as proof.

## Still in force

- No live Billy API tests. No credentialed API qualification calls. Each API row keeps `live_tested` false with `out_of_scope_by_user`.
- Annual reports stay `out_of_scope_by_user` (`scope_code=ANNUAL_REPORTS_OWNER_SKIP`, owner radio `DC3B8E96`). Do not invent `ui_annual_*` or `api_annual_*`. Do not mark the row UI `not_applicable` only because the plan skips it.
- Interface credentials live at `/Users/user/Desktop/billy_login.txt`. Never read them into memory, logs, commits, or radio.
- Do not send invoices or emails, make payments, submit VAT or filings, change users/access/tokens/subscription, or cause other external effects unless a separately safe non-production fixture proves no external consequence, or Joakim gives explicit authority.

## Not a completion wall by themselves

Official-docs bulk92 (`BULK_SCHEMA_UNSPECIFIED_OFFICIAL_DOCS`) and residual29 method-closed honesty stay red and deferred. Do not mark them permanently excluded. Do not run live API to green them. UI writes are the current product.

## Agent routing

This node's owner and seed require Grok. The step overlay also allows `codex-power` for local implementation. Parent `96908DC6` wins: Grok only. If a child spawn is needed later, pass `--agent=grok`.
