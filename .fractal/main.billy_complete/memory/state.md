---
name: state
desc: Current node state, verified review decisions, and open qualification work.
tags: [billy, coverage, review]
sources:
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
  - https://www.billy.dk/api/
created: 2026-07-29T09:56:00Z
updated: 2026-07-31T15:50:16Z
---

# state

## Current state

- Continue mode iter 20 COMMIT done. Product tip reports 186.20 (`6a6b94f`).
- Coverage: implemented/contract 206; live/vision 22; API live 0; complete false.
- Docs fingerprint ETag `wcw4x9hqvu3603`, MD5 `8b94b0135c91fd15fe54ea33e088a4be` (unchanged).
- Operator: grok-only; no live API; no running children.
- Next: RESEARCH freeze `ui.discovery.vat_declarations`.

## Verification

- Last product: `ui_reports_open` dual-session + vision purge_verified (COMMIT 186.20).
- Offline baseline product: 1448 passed non-live.
- Live baseline: 22 UI discovery/parity rows green.

## Review decisions (authoritative)

- Product `ui_reports_open`: **ACCEPT** (IR 186.20; no required fixes; egress retains prior lives).
- Product `ui_transactions_list`: **ACCEPT** (IR 186.19; no required fixes; egress retains prior lives).
- Product `ui_daybooks_open`: **ACCEPT** (IR 186.18; no required fixes; egress retains prior lives).
- Product `ui_financing_open`: **ACCEPT** (IR 186.17; no required fixes; egress retains prior lives).
- Product `ui_bank_reconciliation_open`: **ACCEPT** (IR 186.16; egress generator retains prior lives).
- Product `ui_receipt_inbox_list`: **ACCEPT** (committed 186.15).
- Product `ui_uploads_list`: **ACCEPT** (committed 186.14).
- Product `ui_creditor_balances_list`: **ACCEPT** (committed 186.13).
- Product `ui_debtor_balances_list`: **ACCEPT** (committed 186.12).
- Product `ui_bills_list`: **ACCEPT** (committed 186.11).
- Prior suppliers/products_import/recurring/quotes/bank/clients/products/invoices/auth: **ACCEPT**.
- Overall completeness: **FAIL**.

## Open coverage work

1. Next UI discovery freeze after COMMIT: `ui.discovery.vat_declarations`.
2. Then annual_reports, exports, saft_exports, addons, integrations, inventory,
   settings_*.
3. Residual/bulk offline API reds only; no live API methods.
4. UI parity rows still largely red after discovery shells.

## Live UI tools (22 rows)

- discovery greened (18): invoices, quotes, recurring_invoices, products, product_import,
  customers, debtor_balances, creditor_balances, uploads, receipt_inbox, purchases,
  suppliers, bank_accounts, bank_reconciliation, financing, daybooks, transactions,
  reports.
- parity greened (list shells): bills.list, contacts.list, invoices.list, products.list.
- discovery still red (16): vat_declarations, annual_reports,
  exports, saft_exports, addons, integrations, inventory, settings_*.

## Evidence boundaries

- No invent API tools for pure UI shells.
- Reports path is `/:org_slug/reports-all` h1 `Rapporter`; bare `/reports`
  rejected; never click Eksport; no invent api_reports_*.
- Transactions path is `/:org_slug/transactions` h1 `Posteringer`; nested create
  shell `Postering:` rejected; never click Ny postering.
- Daybooks path is `/:org_slug/daybooks/new` (editor shell); bare `/daybooks` rejected.
- Bank recon is `/:org_slug/bank_accounts/:id/sync` (Afstemning), distinct from
  bank-accounts Bankkonti; empty content shell valid in test org.
- Interface read-back: second browser session only.
- Grok-only children (`--agent=grok`).
- API live_tested stays false with out_of_scope_by_user.

## References

- Plan transactions: `plans/2026-07-31T15:28:53.633Z-186.19-ui_transactions_list.md`
- Wiki: `wiki/ui_transactions_list_shell.md`
- Plan daybooks: look up 186.18 in plans/; wiki `wiki/ui_daybooks_open_shell.md`
- Next: RESEARCH freeze `ui.discovery.reports`

## SYNC (iter 20)

- Unread inbox/feed: empty. Saved queue: empty.
- Private D637D92D read/reacted (next reports freeze); refreshed private 62844996.
- No running children; historical only (none need merge this step).
- Parent directives: none (scope override: no live API; grok-only).
- Branch clean at product tip transactions 186.19 (`c4206ef`) vs origin.
- Coverage: implemented/contract 205; live/vision 21; complete false.
- Outbox posted: iter20 progress (59DA1FC0).
- Ready for PREPARE then RESEARCH freeze: `ui.discovery.reports`.

## PREPARE (iter 20)

- Parent `main`: already up to date; no merge commit.
- No running children.
- Children with commits ahead: scaffold/init/review stubs only, or product already
  superseded on root (`auth_status` present and evolved; wave5t/wave5u research
  wiki already on root or fractal-only; wave5j bank-line fractal-only; optional
  unmerged wiki-only
  `ui_auth_credentials_login_organization_research_codex_fallback.md` — skip,
  superseded auth research already on root product path).
- No child merges this iteration. No integration outbox note.
- Uncommitted: memory/state.md only.
- Ready for RESEARCH freeze: `ui.discovery.reports`.

## SYNC pre-RESEARCH (iter 20)

- Unread inbox/feed: empty. Saved: empty.
- Private 62844996 read/reacted (next: reports freeze).
- No running children. Parent merge already done (no-op).
- Tip transactions product `c4206ef`; dirty: memory/state.md only.
- Outbox: pre-research reports freeze announced.
- Ready for RESEARCH freeze: `ui.discovery.reports`.

## Research (iter 20)

- research119 freeze: `ui_reports_open` for `ui.discovery.reports`
  → path class `/:org_slug/reports-all` (default tab profit-and-loss; also
  balance, trial-balance) h1 `Rapporter`.
- Dual session path/h1/title/markers match on hub + three tabs; bare `/reports`
  is soft empty chrome (reject); exports/vat/annual are sibling families.
- No `/v2/reports` API — do not invent api_reports_*; never click Eksport.
- Frames purged; api_token_used false; writes/clicks false.
- Docs fingerprint unchanged ETag `wcw4x9hqvu3603`.
- Brief: `tmp/grok-research.md`. Do not green coverage in research.
- Ready for PLAN.

## SYNC pre-PLAN (iter 20)

- Unread inbox/feed/private: empty. Saved: empty.
- No running children.
- Outbox: research119 freeze already announced (86C69C3C); ready PLAN product
  `ui_reports_open`.
- Tip transactions product; dirty memory/state.md only (+ tmp research artifacts).
- Ready for PLAN: product `ui_reports_open`.

## Plan (iter 20)

- Plan: `plans/2026-07-31T16:00:58.156Z-186.20-ui_reports_open.md`
  — product `ui_reports_open` for `ui.discovery.reports` only;
  root-only; dual live+vision; path `/:org_slug/reports-all` (+ optional tab)
  h1 `Rapporter`; Eksport observe-only; bare /reports reject; no invent API
  reports; no vat/annual/exports re-green; egress append without drop.
- Ready for EXECUTE.

## SYNC pre-EXECUTE (iter 20)

- Unread inbox/feed/private: empty. Saved: empty.
- No running children.
- Plan 186.20 ready; next EXECUTE product `ui_reports_open`.
- Dirty: memory + untracked plan/tmp research.

## Execute (iter 20)

- Producted `ui_reports_open` (models/browser/server/tests/coverage/wiki).
- Offline non-live 1448 passed; live dual + vision purge_verified.
- Coverage live/vision 22; complete false.
- Greens only `ui.discovery.reports`. Ready for REVIEW.

## SYNC pre-REVIEW (iter 20)

- Unread inbox/feed/private: empty. Saved: empty.
- No running children.
- Outbox: EXECUTE complete announced (E04F9097). Ready for independent review of
  `ui_reports_open` (186.20).

## Independent review (iter 20)

- Product `ui_reports_open`: **ACCEPT** (tmp/grok-review.md).
- No required product fixes. Egress refs intact (transactions + prior lives + reports).
- Overall completeness: **FAIL** (expected).
- Proceed FIX-VERIFY then COMMIT.

## SYNC pre-FIX-VERIFY (iter 20)

- Unread inbox/feed/private: empty. Saved: empty.
- No running children.
- IR ACCEPT product; no required product fixes.
- Ready FIX-VERIFY reconfirm.

## FIX-VERIFY (iter 20)

- IR product ACCEPT; optional N1/N2 no-op (left as-is).
- lint pass; offline 1448; live reports reconfirm pass; vision purge_verified.
- Egress refs intact (uploads + receipt_inbox + bank_recon + bank_accounts +
  financing + daybooks + transactions + reports).
- Coverage live/vision 22; complete false.
- Plan post-mortem filled. Ready for COMMIT.

## SYNC pre-COMMIT (iter 20)

- Unread inbox/feed: empty. Saved: empty.
- Private 0B2A374F read/reacted (next vat_declarations freeze).
- No running children.
- FIX-VERIFY clean; commit product next.

## COMMIT (iter 20)

- `fractal commit` product: ui reports open shell with dual live and vision (`6a6b94f`).
- Not node finish (complete false; bulk + remaining UI still red).

## SYNC (iter 19)

- Unread inbox/feed: empty. Saved queue: empty.
- Private 02AD1B86 read/reacted (next transactions freeze); refreshed private 16FA6AE4.
- No running children; historical only (none need merge this step).
- Parent directives: none (scope override already applied: no live API; grok-only).
- Branch clean at product tip daybooks 186.18 (`0b6176d`) vs origin.
- Coverage: implemented/contract 204; live/vision 20; complete false.
- Outbox posted: iter19 progress (E16BA800).
- Ready for PREPARE then RESEARCH freeze: `ui.discovery.transactions`.

## PREPARE (iter 19)

- Parent `main`: already up to date; no merge commit.
- No running children.
- Children with commits ahead: scaffold/init/review stubs only, or product already
  superseded on root (`auth_status` present on root and evolved; wave5t/wave5u
  research wiki already on root; wave5j bank-line fractal-only delta; optional
  unmerged wiki-only
  `ui_auth_credentials_login_organization_research_codex_fallback.md` — skip,
  superseded auth research already on root product path).
- No child merges this iteration. No integration outbox note.
- Uncommitted: memory/state.md only.
- Ready for RESEARCH freeze: `ui.discovery.transactions`.

## SYNC pre-RESEARCH (iter 19)

- Unread inbox/feed: empty. Saved: empty.
- Private 16FA6AE4 read/reacted (next: transactions freeze).
- No running children. Parent merge already done (no-op).
- Tip daybooks product `0b6176d`; dirty: memory/state.md only.
- Ready for RESEARCH freeze: `ui.discovery.transactions`.

## Research (iter 19)

- research118 freeze: `ui_transactions_list` for `ui.discovery.transactions`
  → `/:org_slug/transactions` h1 `Posteringer` (CTA `Ny postering` observe-only).
- Dual session path/h1/title/markers match; Billy may append `?period=…`;
  nested `/transactions/:segment` is create shell h1 `Postering:` (not list);
  soft aliases empty; daybooks contrast Upsedasse vs daybooks/new editor.
- Frames purged; api_token_used false; writes/clicks false.
- Docs fingerprint unchanged ETag `wcw4x9hqvu3603`.
- Do not invent api write tools; do not green daybooks or parity rows.
- Brief: `tmp/grok-research.md`. Do not green coverage in research.
- Ready for PLAN.

## SYNC pre-PLAN (iter 19)

- Unread inbox/feed/private: empty. Saved: empty.
- No running children.
- Outbox: research118 freeze already announced (C686DB1B); ready PLAN product
  `ui_transactions_list`.
- Tip daybooks product; dirty memory/state.md only (+ tmp research artifacts).
- Ready for PLAN: product `ui_transactions_list`.

## Plan (iter 19)

- Plan: `plans/2026-07-31T15:28:53.633Z-186.19-ui_transactions_list.md`
  — product `ui_transactions_list` for `ui.discovery.transactions` only;
  root-only; dual live+vision; path `/:org_slug/transactions` h1 `Posteringer`;
  CTA Ny postering observe-only; nested create shell not list; no invent API
  writes; no daybooks/parity re-green; egress append without drop.
- Ready for EXECUTE.

## SYNC pre-EXECUTE (iter 19)

- Unread inbox/feed/private: empty. Saved: empty.
- No running children.
- Plan 186.19 ready; next EXECUTE product `ui_transactions_list`.
- Dirty: memory + untracked plan/tmp research.

## Execute (iter 19)

- Producted `ui_transactions_list` (models/browser/server/tests/coverage/wiki).
- Offline 1439; live dual + vision purge_verified.
- Coverage live/vision 21; complete false.
- Greens only `ui.discovery.transactions`. Ready for REVIEW.

## SYNC pre-REVIEW (iter 19)

- Unread inbox/feed/private: empty. Saved: empty.
- No running children.
- Outbox: EXECUTE complete announced (E6D4D26D). Ready for independent review of
  `ui_transactions_list` (186.19).

## Independent review (iter 19)

- Product `ui_transactions_list`: **ACCEPT** (tmp/grok-review.md).
- No required product fixes. Egress refs intact (daybooks + prior lives + transactions).
- Overall completeness: **FAIL** (expected).
- Proceed FIX-VERIFY then COMMIT.

## SYNC pre-FIX-VERIFY (iter 19)

- Unread inbox/feed/private: empty. Saved: empty.
- No running children.
- IR ACCEPT product; no required product fixes.
- Ready FIX-VERIFY reconfirm.

## FIX-VERIFY (iter 19)

- IR product ACCEPT; optional N1 no-op API-token assert removed (comment only).
- lint pass; offline 1439; live transactions reconfirm pass (one transient login
  UI_CHANGED then pass); vision purge_verified.
- Egress refs intact (uploads + receipt_inbox + bank_recon + bank_accounts +
  financing + daybooks + transactions).
- Coverage live/vision 21; complete false.
- Plan post-mortem filled. Ready for COMMIT.

## SYNC pre-COMMIT (iter 19)

- Unread inbox/feed/private: empty. Saved: empty.
- No running children.
- FIX-VERIFY clean; commit product next.

## COMMIT (iter 19)

- `fractal commit` product: ui transactions list shell with dual live and vision (`c4206ef`).
- Not node finish (complete false; bulk + remaining UI still red).

## SYNC (iter 17)

- Unread inbox/feed/private: empty. Saved queue: empty.
- No running children; historical only (none need merge this step).
- Parent directives: none (scope override already applied: no live API; grok-only).
- Branch clean at `c5b054c` vs origin (product tip bank recon 186.16 at `ffe1b46`).
- Coverage: implemented/contract 202; live/vision 18; complete false.
- Outbox posted: iter17 progress (D9AA3D84).
- Private note: next financing freeze (A25545DD).
- Ready for PREPARE.

## PREPARE (iter 17)

- Parent `main`: already up to date; no merge commit.
- No running children.
- Children with commits ahead: scaffold/init/review stubs only, or product already
  superseded on root (`ui_auth_status` code present on root; wave5t/wave5u research
  wiki already on root; wave5j bank-line and wave5sb upload branches have no
  unmerged product delta outside `.fractal`). Optional unmerged wiki-only:
  `ui_auth_credentials_login_organization_research_codex_fallback.md` — skip
  (superseded auth research already applied on root product path).
- No child merges this iteration. No integration outbox note.
- Uncommitted: memory/state.md only.
- Ready for RESEARCH freeze: `ui.discovery.financing`.

## SYNC pre-RESEARCH (iter 17)

- Unread inbox/feed: empty. Saved: empty.
- Private note A25545DD read (next: financing freeze).
- No running children. Parent merge already done (no-op).
- Tip still `c5b054c`; dirty: memory/state.md only.
- Ready for RESEARCH freeze: `ui.discovery.financing`.

## Research (iter 17)

- research116 freeze: `ui_financing_open` for `ui.discovery.financing`
  → `/:org_slug/financing` h1 `Ansøg om erhvervslån` (Bank nav `Ansøg om lån`).
- Dual session path/h1/title match; apply CTA observe-only
  (`Få et uforpligtende tilbud`); frames purged; api_token_used false; writes false.
- Docs fingerprint unchanged ETag `wcw4x9hqvu3603`.
- Design §14.4: external financing writes not tested — product is read-only open.
- Aliases/subpaths empty or false-positive; query variants stay financing landing.
- Do not invent api_financing_*/api_loans_*; no bank_* re-green.
- Brief: `tmp/grok-research.md`. Do not green coverage in research.
- Ready for PLAN.

## SYNC pre-PLAN (iter 17)

- Unread inbox/feed/private: empty. Saved: empty.
- No running children.
- Outbox: research116 freeze already announced (9BE5071A); ready PLAN product
  `ui_financing_open`.
- Tip `c5b054c`; dirty memory/state.md only (+ tmp research artifacts untracked).
- Ready for PLAN: product `ui_financing_open`.

## Plan (iter 17)

- Plan: `plans/2026-07-31T14:31:32.054Z-186.17-ui_financing_open.md`
  — product `ui_financing_open` for `ui.discovery.financing` only;
  root-only; dual live+vision; path `/:org_slug/financing` h1 `Ansøg om erhvervslån`;
  no invent API; no apply/offer/submit click (§14.4); no bank_* re-green;
  egress append without drop.
- Ready for EXECUTE.

## SYNC pre-EXECUTE (iter 17)

- Unread inbox/feed/private: empty. Saved: empty.
- No running children.
- Plan 186.17 ready; next EXECUTE product `ui_financing_open`.
- Tip `c5b054c`; dirty: memory + untracked plan.

## Execute (iter 17)

- Producted `ui_financing_open` (models/browser/server/tests/coverage/wiki).
- Offline 1422; live dual + vision purge_verified.
- Coverage live/vision 19; complete false.
- Greens only `ui.discovery.financing`. Ready for REVIEW.

## SYNC pre-REVIEW (iter 17)

- Unread inbox/feed/private: empty. Saved: empty.
- No running children.
- Outbox: EXECUTE complete announced (B38E2018). Ready for independent review of
  `ui_financing_open` (186.17).

## Independent review (iter 17)

- Product `ui_financing_open`: **ACCEPT** (tmp/grok-review.md).
- No required product fixes. Egress refs intact (uploads + receipt + recon + financing).
- Overall completeness: **FAIL** (expected).
- Proceed FIX-VERIFY then COMMIT.

## SYNC pre-FIX-VERIFY (iter 17)

- Unread inbox/feed/private: empty. Saved: empty.
- No running children.
- IR ACCEPT product; no required product fixes.
- Ready FIX-VERIFY reconfirm.

## FIX-VERIFY (iter 17)

- IR product ACCEPT; no product code fixes required.
- lint pass; offline 1422; live financing reconfirm pass; vision purge_verified.
- Egress refs intact (uploads + receipt_inbox + bank_recon + bank_accounts + financing).
- Coverage live/vision 19; complete false.
- Plan post-mortem filled. Ready for COMMIT.

## SYNC pre-COMMIT (iter 17)

- Unread inbox/feed/private: empty. Saved: empty.
- No running children.
- FIX-VERIFY clean; commit product next.

## COMMIT (iter 17)

- `fractal commit` product: ui financing open shell with dual live and vision (`8ad1215`).
- Not node finish (complete false; bulk + remaining UI still red).

## SYNC (iter 15)

- Unread inbox/feed/private: empty. Saved queue: empty.
- No running children; historical only (none need merge this step).
- Parent directives: none.
- Branch clean at `9f09728` vs origin (product tip uploads 186.14).
- Material progress already on branch: uploads list shell live/vision 16; complete false.
- Outbox posted: iter15 progress (6F16EFA6).
- Private note: next receipt_inbox freeze (E9600E9B).
- Ready for PREPARE.

## PREPARE (iter 15)

- Parent `main`: already up to date; no merge commit.
- No running children.
- Children with commits ahead: scaffold/init/review stubs only, or product already
  superseded on root (`ui_auth_status` code present on root; wave5t/wave5u and auth
  research wiki already on root; wave5j bank-line and wave5sb upload branches have
  no unmerged product delta outside `.fractal`).
- No child merges this iteration. No integration outbox note.
- Uncommitted: memory/state.md only.
- Ready for RESEARCH freeze: `ui.discovery.receipt_inbox`.

## SYNC pre-RESEARCH (iter 15)

- Unread inbox/feed: empty. Saved: empty.
- Private note E9600E9B read (next: receipt_inbox freeze).
- No running children. Parent merge already done (no-op).
- Tip still `9f09728`; dirty: memory/state.md only.
- Ready for RESEARCH freeze: `ui.discovery.receipt_inbox`.

## Research (iter 15)

- research114 freeze: `ui_receipt_inbox_list` for `ui.discovery.receipt_inbox`
  → `/:org_slug/vouchers` h1 `Bilagsindbakke` (distinct from uploads Bilag).
- Dual session path/h1/title match; file_input_count=1 observe-only; frames purged;
  api_token_used false; writes false.
- Docs fingerprint unchanged ETag `wcw4x9hqvu3603`.
- Aliases (inbox, receipts, kvittering, indbakke, …) empty h1 or `/:org_slug/:id`.
- Uploads query variants still Bilag — not receipt inbox.
- Do not invent api_vouchers_*/api_receipt_inbox_*; no files/attachments parity green.
- Brief: `tmp/grok-research.md`. Do not green coverage in research.
- Ready for PLAN.

## SYNC pre-PLAN (iter 15)

- Unread inbox/feed/private: empty. Saved: empty.
- No running children.
- Outbox: research114 freeze already announced; ready PLAN product ui_receipt_inbox_list.
- Tip `9f09728`; dirty memory/state.md only (+ tmp research artifacts untracked).
- Ready for PLAN: product `ui_receipt_inbox_list`.

## Plan (iter 15)

- Plan: `plans/2026-07-31T13:38:05.270Z-186.15-ui_receipt_inbox_list.md`
  — product `ui_receipt_inbox_list` for `ui.discovery.receipt_inbox` only;
  root-only; dual live+vision; path `/:org_slug/vouchers` h1 `Bilagsindbakke`;
  no invent API; no uploads re-green; no file pick / Ret click.
- Ready for EXECUTE.

## SYNC pre-EXECUTE (iter 15)

- Unread inbox/feed/private: empty. Saved: empty.
- No running children.
- Plan 186.15 ready; next EXECUTE product `ui_receipt_inbox_list`.

## Execute (iter 15)

- Producted `ui_receipt_inbox_list` (models/browser/server/tests/coverage/wiki).
- Offline focused pass; live dual + vision purge_verified.
- Coverage live/vision 17; complete false.
- Greens only `ui.discovery.receipt_inbox`. Ready for REVIEW.

## SYNC pre-REVIEW (iter 15)

- Unread inbox/feed/private: empty. Saved: empty.
- No running children.
- Outbox: EXECUTE complete announced. Ready for independent review of
  `ui_receipt_inbox_list` (186.15).

## Independent review (iter 15)

- Product `ui_receipt_inbox_list`: **ACCEPT** (tmp/grok-review.md).
- Required FIX-VERIFY: browser_egress test_references must restore
  `test_ui_uploads_list.py` and append `test_ui_receipt_inbox_list.py` on
  mit.billy.dk + path-scoped api.billysbilling.com (current tree dropped uploads).
- Overall completeness: **FAIL** (expected).
- No product contract blockers; proceed FIX-VERIFY after egress fix.

## SYNC pre-FIX-VERIFY (iter 15)

- Unread inbox/feed/private: empty. Saved: empty.
- No running children.
- IR ACCEPT product; required fix: browser_egress test_references restore
  uploads + append receipt_inbox live tests.
- Ready FIX-VERIFY reconfirm.

## FIX-VERIFY (iter 15)

- IR product ACCEPT; required egress test_references fix applied
  (restore `test_ui_uploads_list.py` + append `test_ui_receipt_inbox_list.py`
  on mit.billy.dk and api.billysbilling.com path-scoped host).
- lint pass; offline 1408; live receipt_inbox reconfirm pass; vision purge_verified.
- Coverage live/vision 17; complete false.
- Plan post-mortem filled. Ready for COMMIT.

## SYNC pre-COMMIT (iter 15)

- Unread inbox/feed/private: empty. Saved: empty.
- No running children.
- FIX-VERIFY clean; commit product next.

## COMMIT (iter 15)

- `fractal commit` product: ui receipt inbox list shell with dual live and vision.
- Not node finish (complete false; bulk + remaining UI still red).

## SYNC (iter 16)

- Unread inbox/feed/private: empty. Saved queue: empty.
- No running children; historical only (none need merge this step).
- Parent directives: none (scope override already applied: no live API; grok-only).
- Branch clean at `7d86a0c` vs origin (product tip receipt_inbox 186.15).
- Coverage: implemented/contract 201; live/vision 17; complete false.
- Outbox posted: iter16 progress (8592CBC1).
- Private note: next bank_reconciliation freeze (3E8FB7AD).
- Ready for PREPARE.

## PREPARE (iter 16)

- Parent `main`: already up to date; no merge commit.
- No running children.
- Children with commits ahead: scaffold/init/review stubs only, or product already
  superseded on root (`ui_auth_status` code present on root; wave5t/wave5u research
  wiki already on root; wave5j bank-line has no unmerged product delta outside
  `.fractal`). Optional unmerged wiki-only:
  `ui_auth_credentials_login_organization_research_codex_fallback.md` — skip
  (superseded auth research already applied on root product path).
- No child merges this iteration. No integration outbox note.
- Uncommitted: memory/state.md only.
- Ready for RESEARCH freeze: `ui.discovery.bank_reconciliation`.

## SYNC pre-RESEARCH (iter 16)

- Unread inbox/feed: empty. Saved: empty.
- Private note 3E8FB7AD read (next: bank_reconciliation freeze).
- No running children. Parent merge already done (no-op).
- Tip still `7d86a0c`; dirty: memory/state.md only.
- Ready for RESEARCH freeze: `ui.discovery.bank_reconciliation`.

## Research (iter 16)

- research115 freeze: `ui_bank_reconciliation_open` for `ui.discovery.bank_reconciliation`
  → path class `/:org_slug/bank_accounts/:id/sync` (underscore), nav label `Afstemning`.
- Distinct from list shell `/:org_slug/bank-accounts` h1 `Bankkonti`.
- Dual session path/h1/title/structure match; empty content shell (no h1/table) in
  test org; not plan-paywall; frames purged; api_token_used false; writes false.
- Docs fingerprint unchanged ETag `wcw4x9hqvu3603`.
- Alias seeds (bank-reconciliation, afstemning, …) empty soft shells; query
  variants on bank-accounts stay Bankkonti.
- Do not invent api_bank_accounts_*/api_reconciliation_*; do not green bankLines
  parity from this shell; do not re-green bank_accounts discovery.
- Brief: `tmp/grok-research.md`. Do not green coverage in research.
- Ready for PLAN.

## SYNC pre-PLAN (iter 16)

- Unread inbox/feed/private: empty after reading BF1898B1. Saved: empty.
- No running children.
- Outbox: research115 freeze already announced (FA60692F).
- Tip `7d86a0c`; dirty memory/state.md only (+ tmp research artifacts untracked).
- Ready for PLAN: product `ui_bank_reconciliation_open`.

## Plan (iter 16)

- Plan: `plans/2026-07-31T14:06:12.186Z-186.16-ui_bank_reconciliation_open.md`
  — product `ui_bank_reconciliation_open` for `ui.discovery.bank_reconciliation`
  only; root-only; dual live+vision; path `/:org_slug/bank_accounts/:id/sync`
  via Afstemning href harvest; empty content shell valid; no invent API; no
  bank_accounts re-green; no connect/import/match; egress append without drop.
- Ready for EXECUTE.

## SYNC pre-EXECUTE (iter 16)

- Unread inbox/feed/private: empty. Saved: empty.
- No running children.
- Plan 186.16 ready; next EXECUTE product `ui_bank_reconciliation_open`.
- Tip `7d86a0c`; dirty: memory + untracked plan.

## Execute (iter 16)

- Producted `ui_bank_reconciliation_open` (models/browser/server/tests/coverage/wiki).
- Offline 1414; live dual + vision purge_verified.
- Coverage live/vision 18; complete false.
- Greens only `ui.discovery.bank_reconciliation`. Ready for REVIEW.
- Egress generator fixed to retain uploads + receipt_inbox + bank_recon refs.

## SYNC pre-REVIEW (iter 16)

- Unread inbox/feed/private: empty. Saved: empty.
- No running children.
- Outbox: EXECUTE complete announced. Ready for independent review of
  `ui_bank_reconciliation_open` (186.16).

## Independent review (iter 16)

- Product `ui_bank_reconciliation_open`: **ACCEPT** (tmp/grok-review.md).
- No required product fixes. Egress refs intact (uploads + receipt + recon).
- Overall completeness: **FAIL** (expected).
- Proceed FIX-VERIFY then COMMIT.

## SYNC pre-FIX-VERIFY (iter 16)

- Unread inbox/feed/private: empty. Saved: empty.
- No running children.
- IR ACCEPT product; no required product fixes.
- Ready FIX-VERIFY reconfirm.

## FIX-VERIFY (iter 16)

- IR product ACCEPT; no product code fixes required.
- lint pass; offline 1414; live recon reconfirm pass (one transient login
  UI_CHANGED then pass); vision purge_verified.
- Egress refs intact (uploads + receipt_inbox + bank_recon + bank_accounts).
- Coverage live/vision 18; complete false.
- Plan post-mortem filled. Ready for COMMIT.

## SYNC pre-COMMIT (iter 16)

- Unread inbox/feed/private: empty. Saved: empty.
- No running children.
- FIX-VERIFY clean; commit product next.

## COMMIT (iter 16)

- `fractal commit` product: ui bank reconciliation open shell with dual live and vision (`ffe1b46`).
- Not node finish (complete false; bulk + remaining UI still red).
