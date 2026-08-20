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
  - radio:8EFD0EAD
  - radio:4A5CD1E7
  - radio:F12B607E
  - radio:452E0773
  - radio:07600147
  - radio:E87B6AEF
  - radio:31B0C7A6
  - radio:28C8FBC8
  - radio:C0721A14
  - radio:D326FFB3
  - radio:AD8966F2
  - radio:23709235
  - radio:FD39FFE7
  - radio:113F1E05
  - radio:A337A622
  - radio:D68E402A
  - radio:67CBACB6
  - radio:2683CE6B
  - radio:8EBC19D5
  - radio:EC676F84
  - radio:9310BC17
  - radio:1F1B34F8
  - radio:56354201
  - radio:C6DA7FC8
  - radio:BF91E28F
  - radio:65521475
  - radio:7BA75272
  - radio:59A3A933
  - radio:B9C4FA7C
  - radio:DECEA79B
  - radio:F1A2EFC2
  - radio:3CB4D807
  - radio:3D5A9B9C
  - radio:32662804
  - radio:D859572B
  - radio:70DB45E6
  - radio:4EAEAFFD
  - radio:E8EA9823
  - radio:D2FD1919
  - radio:A0633A17
  - radio:3377FB3C
  - radio:01FCBA13
  - radio:A6A2B60C
  - radio:31BAF1FF
  - radio:D71E5B82
  - radio:A342BBDC
  - radio:94DD65CB
  - radio:48ABEEB7
  - radio:330C5913
  - radio:02CB47D8
  - radio:7C96E1C3
  - radio:58D7D0E1
  - radio:FE6FA4B1
  - radio:7C9348E1
  - radio:89DEED22
  - radio:9B979A05
  - radio:EAB2F91B
  - radio:B54A6BFC
  - radio:2D09964C
  - radio:8C5F08A8
  - radio:AF8E5A1F
  - radio:4DE5EE18
  - radio:47B85E43
  - radio:05F3200D
  - radio:AB6ABE84
  - radio:8FE83270
  - radio:7453B98F
  - radio:4DBD7C3F
  - radio:7B947636
  - radio:A485F530
created: 2026-08-16T13:50:50Z
updated: 2026-08-20T11:21:07Z
---

## Binding now

`A485F530` (saved, P10, honesty remap in working tree): six
create/update rows `contactBalancePostings`, `postings`, and
`transactions` stay toolless/red. Official Supports lists create
and update. Official property tables have no writable field.
First-party bundles GET only. Qualification is
`readonly_field_map_insufficient` /
`READONLY_PROPERTY_TABLE`. No tools. No empty payload. No live
API. `complete` stays false. Unsave after COMMIT.

`7B947636` (unsaved, P10, landed on `bb66a48`): ticketed
`transactions` singular delete. Preview takes a non-empty `id`.
Execute takes `confirmation_ticket` only. Bind DELETE
`/transactions/:id` with an encoded id and no request body.
Official `#v2transactions` Supports delete is the offline
contract. Independent review PASS. No create/update, bulk, UI,
or live API. `complete` stays false.

`4DBD7C3F` (unsaved, P10, landed on `da833d3`): ticketed
`invoiceReminderAssociations` singular delete. Preview takes a
non-empty `id`. Execute takes `confirmation_ticket` only. Bind
DELETE `/invoiceReminderAssociations/:id` with an encoded id and
no request body. Official Supports delete is the offline
contract. Historical unauth missing-id 200 is not cleanup proof.
Independent review PASS. No bulk, UI, or live API. `complete`
stays false.

`7453B98F` (unsaved, P10, landed on `5a1bde8`): ticketed
`balanceModifiers` create and update. Official Supports lists
create and update. Nested `BalanceModifierPayload` of required
non-empty belongs-to-reference strings `modifier` and `subject`
with `extra=forbid`, frozen. Exclude readonly `amount`,
`entryDate`, `realizedCurrencyDifference`, and `isVoided`.
Create preview `POST /balanceModifiers`. Update preview
`PUT /balanceModifiers/:id` with non-empty encoded route id.
Execute `confirmation_ticket` only. Preview makes no HTTP. No
delete. No bulk. No UI. No live API. `live_tested` stays false
with `live_api=out_of_scope_by_user`. Independent review PASS.
No required fixes. `complete` stays false. Residual honesty
remaining 8.

`8FE83270` (unsaved, P10, landed on `b95f96f`): ticketed
`zipcodes` create and update. Official Supports lists create
and update. Nested `ZipcodePayload` of optional string
`zipcode`, belongs-to string `city`, `state`, and `country`,
and float `latitude` and `longitude` with `extra=forbid`,
frozen. Create preview `POST /zipcodes`. Update preview
`PUT /zipcodes/:id` with non-empty encoded route id. Execute
`confirmation_ticket` only. Preview makes no HTTP. No bulk. No
UI. No live API. `live_tested` stays false with
`live_api=out_of_scope_by_user`. Independent review PASS. No
required fixes. `complete` stays false. Residual honesty
remaining 10.

`A485F530` (saved, P10, after transactions delete): research-only
the six readonly-map create/update rows (`contactBalancePostings`,
`postings`, `transactions`). Exhaust official docs and first-party
static assets. No live API. No guessed fields. Keep rows red if
writable schemas stay absent. Do not start until `7B947636`
commits. `complete` stays false.

`AB6ABE84` (unsaved, P10, landed on `850c80a`): ticketed
`states` create and update. Official Supports lists create
and update. Nested `StatePayload` of optional string
`stateCode`, `name`, and belongs-to `country` with
`extra=forbid`, frozen. Create preview `POST /states`. Update
preview `PUT /states/:id` with non-empty encoded route id.
Execute `confirmation_ticket` only. Preview makes no HTTP. No
bulk. No UI. No live API. `live_tested` stays false with
`live_api=out_of_scope_by_user`. Independent review PASS. No
required fixes. `complete` stays false. Residual honesty
remaining 12.

`05F3200D` (unsaved, P10, landed on `113810e`): ticketed
`locales` create and update. Official Supports lists create
and update. Nested `LocalePayload` of optional string `name`
and `icon` with `extra=forbid`, frozen. Create preview
`POST /locales`. Update preview `PUT /locales/:id` with
non-empty encoded route id. Execute `confirmation_ticket` only.
Preview makes no HTTP. No bulk. No UI. No live API.
`live_tested` stays false with `live_api=out_of_scope_by_user`.
Independent review PASS. No required fixes. `complete` stays
false. Residual honesty remaining 14.

`47B85E43` (unsaved, P10, landed on `c412588`): ticketed
`currencies` create and update. Official Supports lists create
and update. Nested `CurrencyPayload` of optional string `name`
and float `exchangeRate` with `extra=forbid`, frozen. Create
preview `POST /currencies`. Update preview
`PUT /currencies/:id` with non-empty encoded route id. Execute
`confirmation_ticket` only. Preview makes no HTTP. No bulk. No
UI. No live API. `live_tested` stays false with
`live_api=out_of_scope_by_user`. Independent review PASS. No
required fixes. `complete` stays false. Residual honesty
remaining 16.

`4DE5EE18` (unsaved, P10, landed on `5e78f1d`): ticketed
`countries` create and update. Official Supports lists create and
update. Nested `CountryPayload` of optional string `name`,
boolean `hasStates`, `hasFiniteStates`, `hasFiniteZipcodes`,
string `icon`, and string `locale` with `extra=forbid`, frozen.
Create preview `POST /countries`. Update preview
`PUT /countries/:id` with non-empty encoded route id. Execute
`confirmation_ticket` only. Preview makes no HTTP. No bulk. No
UI. No live API. `live_tested` stays false with
`live_api=out_of_scope_by_user`. Independent review PASS. No
required fixes. `complete` stays false. Residual honesty
remaining 18.

`AF8E5A1F` (unsaved, P10, landed on `1b037a6`): ticketed
`countryGroups` create and update. Official Supports lists create
and update. Nested `CountryGroupPayload` of optional string
`name`, `icon`, and `memberCountryIds` with `extra=forbid`,
frozen. Create preview `POST /countryGroups`. Update preview
`PUT /countryGroups/:id` with non-empty encoded route id.
Execute `confirmation_ticket` only. Preview makes no HTTP. No
bulk. No UI. No live API. `live_tested` stays false with
`live_api=out_of_scope_by_user`. Independent review PASS.
`complete` stays false. Residual honesty remaining 20.

`8C5F08A8` (unsaved, P10, landed on `9a3a677`): ticketed
`cities` create and update. Nested optional string `name`,
`county`, `state`, and `country` with `extra=forbid`. Create
`POST /cities`. Update `PUT /cities/:id`. Execute
`confirmation_ticket` only. Preview makes no HTTP. Independent
review PASS. Residual honesty remaining 22.

`2D09964C` (unsaved, P10, landed): ticketed
`invoiceReminderAssociations` create and update. Nested required
`reminder` and `invoice` strings, `extra=forbid`. `lateFee`
rejected at the FastMCP boundary. Create
`POST /invoiceReminderAssociations`. Update
`PUT /invoiceReminderAssociations/:id`. Execute
`confirmation_ticket` only. Preview makes no HTTP. Independent
review PASS. Residual honesty remaining 24.

`B54A6BFC` (unsaved, P9, landed): ticketed singular
`api.bankPayments.delete`. Preview `{id}` only. Execute
`DELETE /bankPayments/:id` with no body. Keep
`live_tested=false` with `live_api=out_of_scope_by_user`.

`EAB2F91B` (unsaved, P10, landed): official `#v2accountnatures`
writable fields are exactly `reportType`, `name`, and
`normalBalance`. Ticketed create/update preview payloads use a
nested Pydantic model of those optional strings with
`extra=forbid`. Opaque `dict[str, JsonValue]` is refused for
this resource. Enum members stay opaque strings. Do not infer
required fields or live API.

`9B979A05` (saved, P10, remaining split): split the 121
offline blockers by evidence, not one permanent-red bucket. For
the 25 `method_closed_offline` rows, current official Supports
tables are the primary contract; an unauthenticated 405 must not
silently override current official documentation. Then the two
`readonly_field_map_insufficient` transaction writes and two
`meta_delete_unqualified` rows from official tables/examples and
static official assets only. For bulk92, exhaust the official
page/assets plus static first-party client bundles for exact
request and response schemas. Never infer a common shape. Never
live API. Land the smallest proved cohort with independent Grok
review. Unresolved stay red.

`89DEED22` (saved, P9, lock landed this COMMIT): official lock is
ETag `tmhc6wpdc835zt` / MD5 `053f755f52e3926b028e29325e3670d4`.
Intro `GET /v2/organizations` is prose for
`api.organizations.list`. Special `GET /v2/user/organizations`
(`api_user_list_organizations`) is kept. The 121 remainder is now
owned by `9B979A05`. Never infer bulk schemas. No live API.

`7C9348E1` (saved, P10, landed): API `live_tested` stays false
with `qualification.live_api=out_of_scope_by_user` on every API
row. Completeness is `discovered`, `implemented`, and
`contract_tested`. Do not classify the API operation itself
`kind=out_of_scope_by_user`. Do not green `live_tested`. Live
API tests stay forbidden. Docs lock reconcile moved to
`89DEED22`.

`FE6FA4B1` (unsaved, P10, landed): residual five files and ledger
writes are `out_of_scope_by_user`. Green flags stay false.
`tools_allowed=false`. `not_applicable` rejected. No live write.
No dump. Do not finish.

`58D7D0E1` (saved, P9, landed): honesty-16 is a false-green stop,
not a permanent-red rule. The 11 accepted rows are
`preview_execute`. Residual five moved to `FE6FA4B1`.
No live write. No UI dump. Do not edit `coverage/status.json` by
hand. Do not finish.

`A41C242F` (saved, P10): operator inspected all four product
PNGs for run `29c1b1de26a14976aaa1b98bfe9de46e`. Independent
Grok accept and purge of that exact run are done. Coverage
names `ui_products_create_preview`. Promotion of this row waits
on `58D7D0E1`.

`7C96E1C3` (saved, P10): operator inspected all five PNGs for
run `60b6d620772644f3bca9609c8ae53846`. They match `A342BBDC`.
Independent Grok accept and purge of that exact run are done.
Does not replace `330C5913` empty-org proof.

`02CB47D8` (unsaved, P10, done): `48ABEEB7` is conjunctive. Approved
live-test mode **and** a pytest `/live/` context, or an
equally bounded internal hook that production cannot set.
`PYTEST_CURRENT_TEST` alone must not write frames, even when
the dest is an allowed `run-*` dir. Direct live invocation
must set `BILLY_TEST_MODE=ui-full`. No live CUD rerun.

`48ABEEB7` (saved, P10): pre-submit screenshot path must be the
owner-only `vision-tmp/run-*` directory. Do not write
`Path(BILLY_VISION_FRAME_DIR)` from production. Gate with
`allowed_vision_frame_dir`. Refined by `02CB47D8`.

`330C5913` (saved, P10): five-frame invoice CUD run
`60b6d620772644f3bca9609c8ae53846` restored empty invoices,
products, and contacts. Keep `pending_review` until independent
Grok vision accepts all five frames. Do not remake leftover
reverse-clean.

`A342BBDC` (saved, P10): filled create form before **Gem som
kladde** is now captured as `02_before_submit.png`. Independent
review still required. Do not accept or purge until
`48ABEEB7` lands and review accepts the five-frame set.

`94DD65CB` (done, unsaved, P10): org independently empty after
the earlier four-frame live CUD. Superseded as empty-org proof
by `330C5913`.

`A6A2B60C` (done, unsaved, P10): reverse cleanup is independently
empty. Settled fresh `/invoices`, `/products`, `/clients` show
**Ingen fakturaer**, **Ingen produkter**, **Ingen kontakter**.
No `MCP-UI-INV-*` or `MCP-UI-PRD-*`. Do not remake leftover
reverse-clean.

`31BAF1FF` (done, unsaved, P10): disposable self-contained
invoice CUD restored the same empty lists. Keep that CUD
rerunnable. Do not hard-fail on leftover names.

`D71E5B82` (in force, unsaved, P10): leftover reverse-clean may
be a one-off. Do not commit a delete-only live test as invoice
update qualification. Preserve `ui_invoices_update_preview` /
execute and independent **Enhedspris** `2,00`. After settled
zero, `ui-full` must pass with no `LEFTOVER_*` hard-fail.

`01FCBA13` (done, unsaved, P10): the seven leftover **Kladde**
triples are gone (`A6A2B60C`). Do not rebuild that list.

`3377FB3C` (done, unsaved, P10): the seven leftover products
are gone (`A6A2B60C`). Do not rebuild that list.

`A0633A17` (done, unsaved, P10): product delete watches one
`DELETE /v2/products/:id` 2xx before a fresh settled
`/products` row-absence. No blind retry. Fail closed if no
DELETE or non-2xx. Landed on `657cef5`.

`D2FD1919` (saved, P10): leftover edit Mere then Slet shows heading
**Bekræft**, text **Vil du slette denne kladdefaktura?**, button
**Annuller**, exact active button **Ja, slet faktura**. Generic
**Ja, slet** is wrong. Next: failing fixture for that exact
button after `E8EA9823` capture. Confirm only through FastMCP.
DELETE 2xx, fresh absence, reverse cleanup. No guessed
selectors, force, or evaluate-click.

`E8EA9823` (saved, P10): dump must record each exact `dialog`,
`alertdialog`, and remaining `aria-modal` candidate with `role`,
allowlisted visible label tokens, geometry, computed z-index, and
`active_contained`. Empty `candidates` is valid only after those
locators are counted. No page-wide sweep. No confirm click.
Live recapture: `candidates=[]`, all three counts 0.

`4EAEAFFD` (saved, P10): after the clean commit, do not wait for
**Ja, slet**. One read-only FastMCP reproduction clicks exact
**Mere** then exact **Slet** once, then captures the scoped
dialog or overlay subtree, accessibility roles and text, active
element, sanitized URL and heading, exact visible button and
link labels, geometry and z-index, and whether any navigation or
DELETE response occurred. Derive the normal confirm action from
that evidence. Failing fixture first. Direct browser proves
**Slet** is a SPAN inside `A.link` with `data-ember-action`
under `LI`. That does not prove the confirm label. Never force
or evaluate click, sweep portals, guess labels, or delete
outside FastMCP.

`D859572B` (done, unsaved, P10): PUT prefix `/v2/invoiceLines/`
is removed. `watched=[]` does not name a path. Keep GET prefix
`/v2/invoiceLines` for line render and PUT prefix `/v2/invoices/`
for save.

`70DB45E6` (saved, P9): leftover edit **Mere** button count=1.
One Mere click reveals exact text **Slet** count=1. Do not click
**Slet** in a recapture. `watched=[]` is confirm or persist timing,
not missing chrome. Unique Mere and exact Slet are proved.
`4EAEAFFD` now owns the post-Slet capture. Do not wait for
**Ja, slet** as the next probe.

`32662804` (saved, P10): leftover
`/invoices/03dvBZm9QHuYt8jGMM8TNw/edit` at 1280x720, DPR 1 has
heading `Rediger fakturakladde`, exact main-frame
`input[name=unitPrice][placeholder=Enhedspris]` count=1, input
count=11. Headless `exact_count=0` / `input_count=8` is a stale
or incomplete headless session, not viewport drift. Start a
fresh authenticated runtime and page, then wait for the exact
input. Invoice update cannot qualify until a focused failing
egress test lands, then only PUT prefix `/v2/invoices/` (never
collection PUT). FastMCP, fresh read-back, reverse-clean.
No guessed clicks, frames, APIs, or BrowserRuntime-only proof.

`3D5A9B9C` (saved, P10): remove `reveal_line_editor`. Do not click
the product tag or a guessed row. The leftover edit page already
renders the visible main-frame **Enhedspris** input with no click.
If the headless session still lacks it, return sanitized URL,
heading, exact-input count, product-text count, and input count.
Do not search frames. Do not treat absence as a missing control
until those counts are recorded.

`3CB4D807` (saved, P10): on
`/invoices/03dvBZm9QHuYt8jGMM8TNw/edit` the main frame has
exactly one visible INPUT `name=unitPrice` `placeholder=Enhedspris`
`type=text` `inputmode=numeric` with value `1,00`. No iframe.
Headless zero-input is a session or render miss. Keep the exact
selector. Wait for that visible input after the edit page is
fully rendered, then fill `2,00` once.

`F1A2EFC2` (saved, P10): exact **Enhedspris** is INPUT
`type=text` `inputmode=numeric` `name=unitPrice`
`placeholder=Enhedspris` class `ember-view ember-text-field`.
A normal locator `fill('2,00')` on that input sets value
exactly `2,00`. Reload restored `1,00` because the owner did
not save. `shown_len=3` is a wrong node, not Billy rejecting
`2,00`. Bind that exact selector. Assert `2,00` before
**Gem som kladde**. Then require `PUT /v2/invoiceLines/:id`
2xx and fresh-session `2,00`. No guessed selector. No blind
keys.

`DECEA79B` (saved, P10): fresh authenticated edit of
`MCP-UI-INV-6CDB396B` still shows **Enhedspris** 1,00 and totals
1,00 / 1,25 DKK. The observed PUT did not persist. Keep update
red. Failing fixture for save completion first. Count update
only after a new fresh session shows 2,00. Then reverse-clean
all six triples.

`B9C4FA7C` (saved, P10): a PUT request is not persistence proof.
Do not mark update live-tested from the request event. Fresh
session must open the exact `li[role=row]` and prove
**Enhedspris** 2,00. If it is still 1,00 or absent, record
`UI_CHANGED`. No API qualification. No POST/PUT id as proof.
The persist watcher now drops events with no status. Update
execute must not treat a later POST as the update persist.

`59A3A933` (saved, P10): six leftover invoice drafts persist.
Fresh `/invoices` shows 6 **Kladde** rows at 1,00 DKK. Exact
pairs: `6CDB396B/FB5F7474`, `F1784522/633E97EC`,
`B05A4C85/86AB7365`, `A45B734E/B4A4DD5A`,
`2B8A4FA2/26720BD4`, `DD4158B1/05C906D9`. Persist is proved
by the interface. Do not use POST id as qualification proof.
Row open: exact visible customer text, ancestor
`li[role=row]`, normal click. `MCP-UI-INV-6CDB396B` opened
`/invoices/03dvBZm9QHuYt8jGMM8TNw/edit`. **Mere** exposes
**Slet**. Next: one FastMCP update, then delete all 6 drafts,
6 products, and 6 customers in reverse order. Fresh proof of
empty lists. No owner input.

`7BA75272` (unsaved, P8, superseded as empty-list proof): a
fresh `/products` session then showed **Ingen produkter**.
That empty state is stale after the later leftover drafts.

`65521475` (done, unsaved, P10): leftover cleanup is finished.
`MCP-UI-PRD-8CA457EE` and `MCP-UI-PRD-EA28FA6B` were deleted
through scoped table-item delete. A third fresh `/products`
session shows **Ingen produkter**. Do not remake leftover
cleanup. Next family is invoice draft CUD.

`BF91E28F` (saved, P10): persist is proved. Delete must scope
to the exact tagged `data-cy=table-item` after revealing row
actions, then **Ja, slet**. Page-wide `delete-icon`.first is
unrelated chrome at x=20,y=0. Never use it. The seven leftover
tags named in this message are gone. Keep the scoped-delete
rule for any later disposable product.

`C6DA7FC8` (saved, P10): B777AA82 is our session/search miss,
not Billy persist. Owner sequence on the authenticated browser:
`/:org/products` -> **Opret produkter** -> **Opret produkt**
dialog -> name (placeholder F.eks. webdesign-tjenester / Acme
Red Hammer) -> **Enhedspris**=1 -> leave defaults 1110 Salg,
Normalt salg af varer, DKK -> **Gem produkt**. Modal closed.
Unfiltered Products list showed the tag with Salg and 1,00 DKK.
A fresh invoice **Vælg produkt** showed it. Hard-delete returned
**Ingen produkter**. Binding: compare live org slug before fill;
after Gem require the visible modal to close or capture visible
validation; then hard-navigate a fresh `/products` page and read
the unfiltered list before any search. Hidden Ember dialog nodes
are not failure. Do not call independent `NOT_FOUND` Billy
behavior while this sequence works.

`56354201` (saved, P10): product create and hard-delete work in
the live UI. Owner created `Codex UI Product Probe 20260818T1741Z`
via **Opret produkt** (name + **Enhedspris**=1), saw it on a
fresh `/invoices/new` **Vælg produkt** chevron, then deleted it
with row `data-cy=delete-icon` and **Ja, slet**. Products list
returned to **Ingen produkter**. Do not treat product as
`interface_control_absent` or archive-only. Do not stop on
`67CBACB6`. FastMCP product actors must compare the live URL
slug to the ticket organisation before fill or click. A
still-visible create dialog after **Gem produkt** is
`UI_CHANGED`, not persist. Live FastMCP product create persist
and scoped table-item delete are proved. Next is invoice draft
CUD with a disposable customer + product + positive price.
Cleanup invoice, product, customer. Prove empty. Do not ask
Joakim.

`1F1B34F8` (saved, P9): persist 422 is invalid zero-value fixture
data after the proved Kunde bind, not a Billy UI blocker. Keep the
fresh-page/chevron fix. Failing fixture: draft create must reject
an unpriced line. Then fill one uniquely tagged reversible line
with a positive unit price and the minimum description/product
the live form requires (**Antal**, **Enhedspris**, **Evt.
beskrivelse**, **Vælg produkt**) before **Gem som kladde**. Fresh
session draft read-back, then update/delete and customer cleanup.
If the minimum line is uncertain, inspect the authenticated
browser. Do not escalate to Joakim.

`9310BC17` (saved, P10, owner fact-check): do not wait for `802D71CF`. Owner created `Codex UI Probe 20260818T1541Z` in the normal UI, saw it in Kunder, opened a new `/invoices/new`, opened the customer chevron, and the picker showed that name immediately. Then Mere -> Slet kontakt -> Ja, slet. Invoice Kunde is not `interface_control_absent`. `UI_CHANGED` is load-order or session staleness: the invoice page was open before the customer existed, or was not freshly navigated after create. Recovery: failing fixture for a preloaded invoice state; create and confirm the customer first; only then start a fresh `BrowserRuntime` or hard-navigate `/invoices/new`; open the evidence-derived dropdown-icon/chevron; select the exact visible tag; FastMCP draft CUD. Do not remove required bind helpers as the resolution. Do not ask Joakim to inspect routine UI state.

`EC676F84` (saved, P10): invoice Kunde works when a customer exists. Create a tagged customer through FastMCP and confirm it independently. `9310BC17` now names the stale-page recovery. Delete invoice first, customer second. No live API. No send, approve, or email.

`96908DC6` (saved): complete UI writes and finish the MCP. Interface first. API live testing still deferred. Supersedes `9FD3042F` (read/open-only) and `3F11A9DF` (stop until explicit start).

`728BD2E4` (unsaved, superseded for this slice by `7C9348E1`): no API-doc detour while UI writes were the gap. Live API still deferred. Offline API semantics and official-docs comparison are now in force under `7C9348E1`. No HOLD. No BrowserRuntime-only qualification.

`E004E7D5` (saved): minimum failing-gate set is the 16 false-green parity rows (bills CUD, contacts CUD, daybooks create/delete, daybookTransactions create, files create, invoices CUD, organizations update, products create, transactions create). Still catch any other write row wrongly treated as complete.

`5E1EDFB4` (done, unsaved): opener dump now has every required key. `named_opener` is null. Hit target is the contact `INPUT`.

`51E18E60` (done, unsaved): stop typed-only repeats. Widget dump is complete. Never call the API directly. Do not land another unchanged typed-only red package.

`A3AB03C3` (done, unsaved): right-edge hit is a nameless `DIV`. No click. Do not repeat that same chevron dump.

`9F777B8F` (done, unsaved): DIV ownership recapture is complete. The nameless right-edge DIV shares the smallest wrapper with `input[name=contact]` and the stack includes that input. One position click ran. No visible option. `UI_CHANGED`. Do not repeat that click. Do not remap.

`8EFD0EAD` (done, unsaved): instrumented tagged-Kunde trace is complete. Listeners ran before form open. Typed existing customer `value_len=19`. No `contacts` path_class, no portal insert, no option, no `aria-expanded`. `UI_CHANGED`. Do not repeat that uninstrumented. Do not remap.

`4A5CD1E7` (done, unsaved): event/pageerror dump is complete. Listeners first. Rest pageerror unrelated. After type `input=19` `keydown=19` `change=0`. One change event dispatched. Still no contacts request. `UI_CHANGED`. Do not repeat this dump. Do not guess blur. Do not remap.

`F12B607E` (done, unsaved): five rest bootstraps resolve to `user` / `user` / `user` / `organizations` / unnamed `other_v2`. `contact_dataset_preloaded=false`. `UI_CHANGED`. Field shot and owner templates purged. Tagged customer already deleted. Never issue those routes. Do not repeat route capture.

`452E0773` (done, unsaved): live control contract named `click_open` on the closest `pickerfield` wrapper (`data-cy` name only). Binding `token_class=name_quoted_contact`. One wrapper click ran. `option_role_count=0`. `UI_CHANGED`. That dump is closed.

`07600147` (done, committed on `1936b7c`): one FastMCP tagged customer, fresh confirm, scoped observer, one `pickerfield` click. `changed_node_count=0`. `exact_match_target=false`. `UI_CHANGED`. Customer deleted. Absence proved. Do not repeat that wrapper-center click.

`E87B6AEF` (done, unsaved, on `522105c`): live read-only map has two visible descendants. Contact `INPUT` plus overlay `DIV` at `dx=242`. `unique_target=false`. `wrapper_handler_guard=none`. `UI_CHANGED`. Do not click either target. Do not remake that map.

`31B0C7A6` (done, unsaved, on `1df08a5`): Ember view present via `Ember.View.views`. `lookup_class=view_registry`. `view_constructor_token=pickerfield`. No allowlisted properties or methods. `unique_normal_action=false`. `UI_CHANGED`. No click. Do not remake. Do not invoke.

Fiber inspect (done, unsaved): live dump `fiber_key_class=none` on the contact `INPUT` and `pickerfield`. No named action. `unique_normal_action=false`. `UI_CHANGED`. Do not remake. Do not click.

`28C8FBC8` (done, unsaved, on `c52d1ae`): listener contract is complete. Nine sanitized rows. No named invoke. `unique_normal_action=false`. `UI_CHANGED`. No click. No customer. Do not remake.

Structure compare (done, closed on `8feb636`): Kunde `pickerfield` versus bills `input_wrapper`. `same_family=false`. `transferable_action=none`. `UI_CHANGED`. Do not copy the bills wrapper. Do not remake. Stay red. Do not finish.

`C0721A14` (done, unsaved): customer-detail **Opret faktura** inspect is complete. Path `contacts_customer`. **Ret** 1. Exact **Opret faktura** count 0. `proved_prebind=none`. `UI_CHANGED`. Customer deleted. Absence proved. Route closed. Do not remake.

`D326FFB3` (done, unsaved): freeze invoice CUD as `UI_CHANGED`. Product delete-chrome recapture is complete on `63b2528`. `proved_delete_path=none`. Do not remake. Do not Gem.

`AD8966F2` (done, unsaved): company phone dump is complete. `proved_phone_only=true`. `phone_value_len=0`. Do not remake that dump. Do not read it as a finished product freeze.

`23709235` (done, unsaved, accepted, remapped): empty original is a reversible clear. Live FastMCP tagged set plus empty restore passed. Independent accept `run_id=0937a009bf7e496ca2ce15a8af313868` with purge verified. `ui.parity.organizations.update` names `ui_organizations_update_preview`. Honesty still red.

`8EBC19D5` (done, unsaved, applied): do not recapture with a body-wide MutationObserver or raise the row cap. Helper no longer observes `document.body`. Allowed recapture recorded `unique_action=none`. Next path is a different normal-interface route. Do not broaden to `document.body`.

`2683CE6B` (done, unsaved, dump delivered, refined by `8EBC19D5`): stop page-wide one-off dumps. Live scoped dump: `gem_clicked=true`, `invoice_persisted=false`, two `validation` rows, `unique_action=none`, `proved_bind=none`. Contact-owned roots showed no unique visible option or owned **Opret ny** footer. Do not remake via a body-wide recapture. Next is a different normal-interface path under `FD39FFE7`. Do not freeze. Do not finish.

`FD39FFE7` (saved, still in force): invoice draft CUD and product create are mandatory MCP capabilities. They stay red until live proof. They are not done as `UI_CHANGED`. `EC676F84` now names the invoice path: tagged FastMCP customer, then draft CUD. Do not remake picker dumps. Do not freeze invoice CUD as finished. Product create follows `56354201` / `C6DA7FC8`: persist, hard-delete, then invoice CUD. `67CBACB6` is not a stop.

`113F1E05` (saved, P10, supersedes Tilgodehavender CTA dump): stop enumerating alternate **Opret faktura** entry CTAs. Those entries reach the same empty create form. Do not execute or commit another route-entry diagnostic on assumption. Inspect the loaded create-form customer control locally (scoped DOM/AX plus page-local frontend source or component evidence, no live API). Derive one exact normal existing-customer interaction. Failing fixture first. Then FastMCP draft CUD if that interaction exists. If none, record `UI_CHANGED` and move to product create. Do not accumulate more diagnostic helpers. Stay red. Do not stop the root.

`A337A622` (saved, P10): stop product archive and list-shell enumeration. `/products` and Lagermodul `/inventory` both have named filter counts 0. Independent review failed the Lagermodul helper as a redundant permanent diagnostic. Drop the helper. Keep the wiki fact. Do not persist. Do not remap. Do not treat archive as restored state without an answer to `67CBACB6`. Record product create `UI_CHANGED` / fail-closed. No more product list, dialog, or archive probes unless new read-only evidence names a different normal cleanup control.

`D68E402A` (unsaved, P10, landed): stop read-only classify churn on ledger and files. Do not commit another helper or dump unless it enables a safe write or fixes a production bug. Residual table is in `wiki/ui_write_residual_table.md`. Residual five are now `FE6FA4B1`. Stay red. Keep the root active.

`67CBACB6` (superseded as a stop, not unsaved as a dump ban): live official product dialog proved **Gem produkt** and **Arkiveret (skjul fra lister)**. Archive-list dumps still have named filter counts 0. `56354201` now names the unique cleanup path (row `delete-icon` + **Ja, slet**). Do not remake the form-contract or archive-list dumps. Do not wait on an archive-as-restore answer.

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

Official-docs bulk92 (`BULK_SCHEMA_UNSPECIFIED_OFFICIAL_DOCS`) and residual29 stay red until `9B979A05` proves a cohort. Do not mark them permanently excluded. Do not run live API. An unauthenticated 405 must not silently override current official Supports tables. The current product is the smallest proved offline cohort.

## Agent routing

This node's owner and seed require Grok. The step overlay also allows `codex-power` for local implementation. Parent `96908DC6` wins: Grok only. If a child spawn is needed later, pass `--agent=grok`.
