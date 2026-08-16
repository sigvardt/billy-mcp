---
name: decisions
desc: Binding owner scope and qualification decisions for this node.
tags: [owner, scope]
sources:
  - radio:96908DC6
  - radio:DC3B8E96
  - radio:E1E454F4
  - radio:4E471870
  - radio:E613984F
created: 2026-08-16T13:50:50Z
updated: 2026-08-16T13:50:50Z
---

## Binding now

`96908DC6` (saved): complete UI writes and finish the MCP. Interface first. API live testing still deferred. Supersedes `9FD3042F` (read/open-only) and `3F11A9DF` (stop until explicit start).

`728BD2E4` (saved): no API-doc detour. Record the new docs fingerprint only. PLAN starts with the failing coverage test, then splits Grok-only children by independent UI write family. No HOLD. No BrowserRuntime-only qualification.

`E004E7D5` (saved): minimum failing-gate set is the 16 false-green parity rows (bills CUD, contacts CUD, daybooks create/delete, daybookTransactions create, files create, invoices CUD, organizations update, products create, transactions create). Still catch any other write row wrongly treated as complete.

`EE0A0F1B` (saved): durable TDD invariant is preview+execute twin, not "no ui_* preview/execute exist". Open-only status/tool can never green implemented/live/vision.

`DD80C9A8` (saved): node `test.sh` must accept `BILLY_TEST_MODE=ui-full` (offline API + live UI/vision, no live API), then require-complete and repository policy.

`4E471870` (done, unsaved): do not green from unarmed execute. `create_server` now passes the shared `BrowserRuntime` and requires `organization_id`.

`5018B3FA` (done, unsaved): start-only execute is a false submit. The default path now performs the family action before `submitted=True`. That is not enough for live qualification.

`E613984F` (saved): execute compares the live URL slug to `prepared.binding.organization_id` and fails closed on mismatch. Contacts no longer use a stored identity file for that compare. Read-back starts a second runtime. A blank `-readback` profile is not a live second session; authenticate it (`E1E454F4`) before live proof. Cleanup still needs a third fresh read-back. Keep coverage red.

`C7DBE974` (done, unsaved): live write tests may write `author=live_test` and `reviewer_verdict=pending_review` only. They must not write `accept` or purge frames. A gate rejects coverage evidence whose reviewer record was created by the test. An independent Grok review writes accept or reject, then purge, then `purge_verified`.

`145EEAB3` (saved): the nine named idle `billy-live-contacts-*` profiles are gone. Zero `billy-live-contacts-*` remain. Do not touch `chrome-profile`. Keep this saved until a live run also leaves zero leftover write, readback, observer, and cleanup profiles.

Use only the Grok CLI for this node and any child (`--agent=grok`). Qualify UI tools through the real MCP boundary, not direct BrowserRuntime as proof.

## Still in force

- No live Billy API tests. No credentialed API qualification calls. Each API row keeps `live_tested` false with `out_of_scope_by_user`.
- Annual reports stay `out_of_scope_by_user` (`scope_code=ANNUAL_REPORTS_OWNER_SKIP`, owner radio `DC3B8E96`). Do not invent `ui_annual_*` or `api_annual_*`. Do not mark the row UI `not_applicable` only because the plan skips it.
- Live UI refs (`E1E454F4`): `BILLY_BROWSER_PRIMARY_REFERENCE=billy-ui-primary` and `BILLY_BROWSER_SECONDARY_REFERENCE=billy-ui-secondary` in keyring service `billy-mcp`. Never log values. Never read `/Users/user/Desktop/billy_login.txt` into memory, logs, commits, or radio. `BILLY_ORGANIZATION_ID` stays unset until the dedicated non-production org is proved in the interface.
- Do not send invoices or emails, make payments, submit VAT or filings, change users/access/tokens/subscription, or cause other external effects unless a separately safe non-production fixture proves no external consequence, or Joakim gives explicit authority.

## Not a completion wall by themselves

Official-docs bulk92 (`BULK_SCHEMA_UNSPECIFIED_OFFICIAL_DOCS`) and residual29 method-closed honesty stay red and deferred. Do not mark them permanently excluded. Do not run live API to green them. UI writes are the current product.

## Agent routing

This node's owner and seed require Grok. The step overlay also allows `codex-power` for local implementation. Parent `96908DC6` wins: Grok only. If a child spawn is needed later, pass `--agent=grok`.
