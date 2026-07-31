---
name: state
desc: Current node state, verified review decisions, and open qualification work.
tags: [billy, coverage, review]
sources:
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
  - https://www.billy.dk/api/
created: 2026-07-29T09:56:00Z
updated: 2026-07-31T13:05:00Z
---

# state

## Current state

- Continue mode iter 12 product `ui_debtor_balances_list` ready for COMMIT.
- Coverage: implemented/contract 198; live/vision 14; API live 0; complete false.
- Docs fingerprint ETag `wcw4x9hqvu3603`, MD5 `8b94b0135c91fd15fe54ea33e088a4be`.
- Operator: grok-only; no live API; no running children.

## Verification

- Last product: `ui_bills_list` dual-session + vision purge_verified (ACCEPT).
- Offline baseline at tip: 1376 passed class (reconfirm in EXECUTE).
- Live baseline: 13 UI discovery/parity rows green.

## Review decisions (authoritative)

- Product `ui_debtor_balances_list`: **ACCEPT** (committed 186.12).
- Product `ui_bills_list`: **ACCEPT** (committed 186.11).
- Prior suppliers/products_import/recurring/quotes/bank/clients/products/invoices/auth: **ACCEPT**.
- Overall completeness: **FAIL**.

## Open coverage work

1. Next UI shell: `ui.discovery.creditor_balances` (`/:org_slug/creditorbalance`).
2. Then `uploads`, `receipt_inbox`, bank/financing/daybooks, settings.
3. Residual/bulk offline API reds only; no live API methods.

## Live UI tools (13 rows)

- list/import shells greened: invoices, products, clients, bank_accounts, quotes,
  recurring_invoices, products_import, suppliers, bills (+ parity list shells).

## Evidence boundaries

- No invent API tools for pure UI shells.
- No green balances/uploads from bills product.
- Interface read-back: second browser session only.
- Grok-only children (`--agent=grok`).

## References

- Plan: `plans/2026-07-31T12:13:15.985Z-186.11-ui_bills_list.md`
- Wiki: `wiki/ui_bills_list_shell.md`

## SYNC (iter 12)

- Unread inbox/feed/private: empty. Saved queue: empty.
- No running children; historical only.
- Parent directives: none.
- Branch clean at `713f2e8` vs origin (memory dirty only).
- Material progress since last outbox: bills product committed; live/vision 13.

## PREPARE (iter 12)

- Parent `main`: already up to date; no merge commit.
- No running children.
- Children with commits ahead: scaffold/init/review stubs only, or product already
  superseded on root (`ui_auth_status` tip is behind root browser/models/server;
  wave5t/wave5u wiki already on root with equal-or-newer content).
- Missing child wiki only: codex-fallback auth research page — superseded by
  `wiki/auth_credentials_pre_submit_research.md`,
  `wiki/ui_login_surface_contract.md`,
  `wiki/credentialed_session_discovery_protocol.md`. Not merged.
- No child merges this iteration. No integration outbox note.
- Uncommitted: memory/state.md only.

## SYNC pre-RESEARCH (iter 12)

- Unread inbox/feed: empty. Saved: empty.
- Private note 82467776 read (prior SYNC context).
- No running children. Parent merge already done.
- Tip still `713f2e8`; only dirty: memory/state.md.
- Ready for RESEARCH freeze: `ui.discovery.debtor_balances`.

## Research (iter 12)

- research111 freeze: `ui_debtor_balances_list` for `ui.discovery.debtor_balances`
  → `/:org_slug/debtorbalance` h1 `Tilgodehavender` CTA `Opret faktura` (never click).
- Dual session path/h1/title match; frames purged; api_token_used false.
- Docs fingerprint unchanged ETag `wcw4x9hqvu3603`.
- Sibling `creditorbalance` / `Skyldige udgifter` dual-matched for next slice only.
- Brief: `tmp/grok-research.md`. Do not green coverage in research.

## SYNC pre-PLAN (iter 12)

- Unread inbox/feed: empty. Saved: empty. No running children.
- Outbox: research111 freeze announced.
- Ready for PLAN: product `ui_debtor_balances_list`.

## Plan (iter 12)

- Plan: `plans/2026-07-31T12:35:03.218Z-186.12-ui_debtor_balances_list.md`
  — product `ui_debtor_balances_list` for `ui.discovery.debtor_balances` only;
  root-only; dual live+vision; no invent API; no creditor green.

## SYNC pre-EXECUTE (iter 12)

- Unread inbox/feed: empty. Saved: empty. No running children.
- Plan 186.12 ready; next EXECUTE product.

## Execute (iter 12)

- Producted `ui_debtor_balances_list` (models/browser/server/tests/coverage/wiki).
- Offline 1384 pass; live dual + vision purge_verified.
- Coverage live/vision 14; complete false.
- Greens only `ui.discovery.debtor_balances`. Ready for REVIEW.

## SYNC pre-REVIEW (iter 12)

- Unread inbox/feed: empty. Saved: empty. No running children.
- Outbox: EXECUTE complete announced. Ready for independent review.

## Independent review (iter 12)

- Product `ui_debtor_balances_list`: **ACCEPT** (tmp/grok-review.md).
- Overall completeness: **FAIL** (expected).
- No product blockers; proceed FIX-VERIFY/COMMIT.

## SYNC pre-FIX-VERIFY (iter 12)

- Unread inbox/feed: empty. Saved: empty. No running children.
- IR ACCEPT product; no required fixes. Ready FIX-VERIFY reconfirm.

## FIX-VERIFY (iter 12)

- IR product ACCEPT; no required fixes applied.
- Lint pass; offline 1384; live debtor reconfirm pass; vision purge_verified.
- Coverage live/vision 14; complete false.
- Ready for COMMIT.

## SYNC pre-COMMIT (iter 12)

- Unread inbox/feed: empty. Saved: empty. No running children.
- FIX-VERIFY clean; commit product next.
