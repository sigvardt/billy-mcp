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
  - radio:B50FBDAD
  - radio:D42EAAA6
  - radio:F3F318A2
  - radio:93D7A063
  - radio:7E7148F6
  - radio:91A2C363
  - radio:A6FB8FC2
  - radio:51E18E60
  - radio:A3AB03C3
  - radio:9F777B8F
created: 2026-08-16T13:50:50Z
updated: 2026-08-17T17:35:00Z
---

## Binding now

`96908DC6` (saved): complete UI writes and finish the MCP. Interface first. API live testing still deferred. Supersedes `9FD3042F` (read/open-only) and `3F11A9DF` (stop until explicit start).

`728BD2E4` (saved): no API-doc detour. Record the new docs fingerprint only. PLAN starts with the failing coverage test, then splits Grok-only children by independent UI write family. No HOLD. No BrowserRuntime-only qualification.

`E004E7D5` (saved): minimum failing-gate set is the 16 false-green parity rows (bills CUD, contacts CUD, daybooks create/delete, daybookTransactions create, files create, invoices CUD, organizations update, products create, transactions create). Still catch any other write row wrongly treated as complete.

`5E1EDFB4` (done, unsaved): opener dump now has every required key. `named_opener` is null. Hit target is the contact `INPUT`.

`51E18E60` (saved; dump delivered at `1275d00`): stop typed-only repeats. Widget dump is complete. Never call the API directly. Do not land another unchanged typed-only red package.

`A3AB03C3` (saved; dump delivered): right-edge hit is a nameless `DIV`. No click. Do not repeat that same chevron dump.

`9F777B8F` (saved): next slice. Failing fixture first. One read-only recapture of the exact right-edge DIV: `elementsFromPoint` stack, box versus the contact input box, `pointer-events`, role/name/testid/allowlisted classes, direct parent and closest owner relation to `input[name=contact]`, whether the hit DIV is contained by or shares the smallest wrapper with that input, and the nearest normally clickable ancestor with accessible role/name. Never store IDs or customer data. One normal Playwright locator or position action only if that evidence proves the DIV belongs to the same Kunde control. Then wait for a visible option before type. If not proved, `UI_CHANGED` and a different read-only capture later. No force, `evaluate` click, guessed selector, blind keyboard, or center-click plus type.

`EE0A0F1B` (in force, not saved): durable TDD invariant is preview+execute twin, not "no ui_* preview/execute exist". Open-only status/tool can never green implemented/live/vision.

`DD80C9A8` (in force, not saved): node `test.sh` must accept `BILLY_TEST_MODE=ui-full` (offline API + live UI/vision, no live API), then require-complete and repository policy.

`4E471870` (done, unsaved): do not green from unarmed execute. `create_server` now passes the shared `BrowserRuntime` and requires `organization_id`.

`5018B3FA` (done, unsaved): start-only execute is a false submit. The default path now performs the family action before `submitted=True`. That is not enough for live qualification.

`D42EAAA6` (done, unsaved): real Playwright `mouse.click` at the save-button box center is proved. The control is visible, enabled, and the hit target. No console errors. After that click there is still no Billy XHR. Isolate is evidence, not a pass. Persist stays the open product work.

`B50FBDAD` (done, unsaved): live update isolate is captured. Name input has the new value. Save is enabled. No visible validation error. Do not repeat the same fill-and-click. The next slice is why Ember does not save after the proved pointer click.

`E613984F` (done, unsaved): execute compares the live URL slug to `prepared.binding.organization_id` and fails closed on mismatch. Contacts no longer use a stored identity file for that compare. Read-back starts a second runtime. A blank `-readback` profile is not a live second session; authenticate it (`E1E454F4`) before live proof. Cleanup still needs a third fresh read-back. Keep coverage red.

`C7DBE974` (done, unsaved): live write tests may write `author=live_test` and `reviewer_verdict=pending_review` only. They must not write `accept` or purge frames. A gate rejects coverage evidence whose reviewer record was created by the test. An independent Grok review writes accept or reject, then purge, then `purge_verified`.

`145EEAB3` (done, unsaved): the nine named idle `billy-live-contacts-*` profiles are gone. After the last live run, zero `billy-live-contacts-*` remain. Do not touch `chrome-profile` or `chrome-profile-readback`. Hardening still applies: login UI_CHANGED, timeouts, and review failures must not leak write, readback, observer, or cleanup profiles.

`F3F318A2` (done, unsaved): failing browser-egress test first. Permit only PUT for `/v2/contacts/:id`. Do not add PATCH unless the live interface request is PATCH. One FastMCP CUD with independent fresh-session read-back after each step and final absence. Browser-originated PUT is interface qualification, not API-token qualification. Keep coverage red.

`31F6E753` (done, unsaved): untagged empty bill drafts are gone. Fresh session list is `/:org_slug/bills/empty`. Pre-submit dump still required before any new bill create. Never book, approve, pay, or email.

`7E7148F6` (done, unsaved): leftover Leverandør portal rule still binds: one named close after role, text, and owning-control proof. No force Save, no generic portal sweep, no Escape.

`A6FB8FC2` (constraint only): do not retry dialog **Gem** plus a second search-toggle close.

`91A2C363` (done, unsaved): existing-option bind plus accept `9920dd9476474b41aef70e6d66d24638`. Bills CUD rows name preview tools. Stay red. If the page differs later, record `UI_CHANGED` and recapture.

`93D7A063` (done, unsaved): accept recorded for `run-3d5b151dfd5342258f8734373597f8c1`, frames gone, then `tool_name` remapped to `ui_clients_{create,update,delete}_preview` in `f47b9d5`. Mapping did not self-approve. Honesty 16 stays red.

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
