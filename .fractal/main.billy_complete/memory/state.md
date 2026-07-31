---
name: state
desc: Current node state, verified review decisions, and open qualification work.
tags: [billy, coverage, review]
sources:
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
  - https://www.billy.dk/api/
created: 2026-07-29T09:56:00Z
updated: 2026-07-31T14:15:00Z
---

# state

## Current state

- Continue mode iter 14 SYNC complete; tip product commit (creditor balances 186.13).
- Coverage: implemented/contract 200; live/vision 16; API live 0; complete false.
- Docs fingerprint ETag `wcw4x9hqvu3603`, MD5 `8b94b0135c91fd15fe54ea33e088a4be`.
- Operator: grok-only; no live API; no running children.
- Branch clean at `ca651f5` vs origin.

## Verification

- Last product: `ui_uploads_list` dual-session + vision purge_verified.
- Offline baseline product: 1400 passed class.
- Live baseline: 16 UI discovery/parity rows green.

## Review decisions (authoritative)

- Product `ui_uploads_list`: **ACCEPT** (IR 186.14; egress ref fix pending).
- Product `ui_creditor_balances_list`: **ACCEPT** (committed 186.13).
- Product `ui_debtor_balances_list`: **ACCEPT** (committed 186.12).
- Product `ui_bills_list`: **ACCEPT** (committed 186.11).
- Prior suppliers/products_import/recurring/quotes/bank/clients/products/invoices/auth: **ACCEPT**.
- Overall completeness: **FAIL**.

## Open coverage work

1. Next UI shell product: `ui_uploads_list` for `ui.discovery.uploads` (research113 freeze ready).
2. Then receipt_inbox, bank/financing/daybooks, settings.
3. Residual/bulk offline API reds only; no live API methods.

## Live UI tools (15 rows)

- list/import shells greened: invoices, products, clients, bank_accounts, quotes,
  recurring_invoices, products_import, suppliers, bills, debtor_balances,
  creditor_balances (+ parity list shells where applicable).

## Evidence boundaries

- No invent API tools for pure UI shells.
- No green balances/uploads from prior products.
- Interface read-back: second browser session only.
- Grok-only children (`--agent=grok`).
- API live_tested stays false with out_of_scope_by_user.

## References

- Plan: `plans/2026-07-31T12:52:41.282Z-186.13-ui_creditor_balances_list.md`
- Wiki: `wiki/ui_creditor_balances_list_shell.md`
- Research seed for next: research112 uploads path note in
  `.fractal/main.billy_complete/tmp/grok-research.md`

## SYNC (iter 14)

- Unread inbox/feed/private: empty. Saved queue: empty.
- No running children; historical only (none need merge this step).
- Parent directives: none.
- Branch clean at `ca651f5` vs origin.
- Material progress: creditor product committed (186.13); live/vision 15.
- Outbox posted: next freeze `ui.discovery.uploads` (0D821979).
- Private note: iter14 next uploads shell (AD9425F1).
- Ready for PREPARE.


## PREPARE (iter 14)

- Parent `main`: already up to date; no merge commit.
- No running children.
- Children with commits ahead: scaffold/init/review stubs only, or product already
  superseded on root (`ui_auth_status` tip is behind root browser/models/server;
  wave5t/wave5u and auth research wiki already on root with equal-or-newer content;
  wave5j bank-line and wave5sb upload branches have no unmerged product delta).
- No child merges this iteration. No integration outbox note.
- Uncommitted: memory/state.md only.
- Ready for RESEARCH freeze: `ui.discovery.uploads`.


## SYNC pre-RESEARCH (iter 14)

- Unread inbox/feed: empty. Saved: empty.
- Private note AD9425F1 read (next: uploads freeze).
- No running children. Parent merge already done.
- Tip still `ca651f5`; dirty: memory/state.md only.
- Ready for RESEARCH freeze: `ui.discovery.uploads`.


## Research (iter 14)

- research113 freeze: `ui_uploads_list` for `ui.discovery.uploads`
  → `/:org_slug/uploads` (query drawerMode/type allowed) h1 `Bilag` CTA
  `Upload filer` (never click; never set file inputs; file_input_count=2 observed).
- Dual session path/h1/title/CTA match; frames purged; api_token_used false.
- Docs fingerprint unchanged ETag `wcw4x9hqvu3603`.
- Aliases (upload, bilag, files, inbox, receipts, …) → empty h1 or `/:org_slug/:id`.
- receipt_inbox still unresolved (separate freeze).
- Do not green files/attachments API parity from shell open.
- Brief: `tmp/grok-research.md`. Do not green coverage in research.
- Ready for PLAN.


## SYNC pre-PLAN (iter 14)

- Unread inbox/feed/private: empty. Saved: empty.
- No running children.
- Outbox: research113 freeze announced; pre-PLAN note posted.
- Ready for PLAN: product `ui_uploads_list`.


## Plan (iter 14)

- Plan: `plans/2026-07-31T13:11:51.928Z-186.14-ui_uploads_list.md`
  — product `ui_uploads_list` for `ui.discovery.uploads` only;
  root-only; dual live+vision; no invent API; no receipt_inbox / files parity green.
- Ready for EXECUTE.


## SYNC pre-EXECUTE (iter 14)

- Unread inbox/feed/private: empty. Saved: empty.
- No running children.
- Plan 186.14 ready; next EXECUTE product `ui_uploads_list`.


## Execute (iter 14)

- Producted `ui_uploads_list` (models/browser/server/tests/coverage/wiki).
- Offline 1400 pass; live dual + vision purge_verified.
- Coverage live/vision 16; complete false.
- Greens only `ui.discovery.uploads`. Ready for REVIEW.


## SYNC pre-REVIEW (iter 14)

- Unread inbox/feed/private: empty. Saved: empty.
- No running children.
- Outbox: EXECUTE complete announced. Ready for independent review.


## Independent review (iter 14)

- Product `ui_uploads_list`: **ACCEPT** (tmp/grok-review.md).
- Required FIX-VERIFY: append live test to browser_egress mit.billy.dk test_references.
- Overall completeness: **FAIL** (expected).
- No product contract blockers; proceed FIX-VERIFY/COMMIT after egress fix.


## SYNC pre-FIX-VERIFY (iter 14)

- Unread inbox/feed/private: empty. Saved: empty.
- No running children.
- IR ACCEPT product; required fix: browser_egress test_references for uploads live test.
- Ready FIX-VERIFY reconfirm.


## FIX-VERIFY (iter 14)

- IR product ACCEPT; required egress test_references fix applied
  (`mit.billy.dk` + `api.billysbilling.com` path-scoped host).
- Lint pass; offline 1400; live uploads reconfirm pass; vision purge_verified.
- Coverage live/vision 16; complete false.
- Plan post-mortem filled. Ready for COMMIT.


## SYNC pre-COMMIT (iter 14)

- Unread inbox/feed/private: empty. Saved: empty.
- No running children.
- FIX-VERIFY clean; commit product next.


## COMMIT (iter 14)

- `fractal commit` product: ui uploads list shell with dual live and vision.
- Not node finish (complete false; bulk + remaining UI still red).
