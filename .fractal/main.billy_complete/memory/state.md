---
name: state
desc: Current node state, verified review decisions, and open qualification work.
tags: [billy, coverage, review]
sources:
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
  - https://www.billy.dk/api/
created: 2026-07-29T09:56:00Z
updated: 2026-07-31T10:25:00Z
---

# state

## Current state

- RESEARCH103 done: products/clients/bank-accounts dual-session freeze. Brief:
  `.fractal/main.billy_complete/tmp/grok-research.md`. Artifacts:
  `tmp/discovery103/summary.json` (scrubbed; frames purged).
- Docs unchanged (ETag `wcw4x9hqvu3603`, MD5 `8b94b0135c91fd15fe54ea33e088a4be`).
- Product 186.4 `ui_products_list` ACCEPT (IR): path `/:org_slug/products`,
  h1 `Produkter`, `search_control_visible` via `data-cy=search-button`; dual
  live + vision accept + purge_verified.
- UI live+vision green: invoices discovery+list, products discovery+list (4).
- API offline implemented+contract ~184 (+ UI shells in status 188 totals);
  API live 0 (`out_of_scope_by_user` at status blocker). Residual 29 + bulk 92
  red. `complete: false`.
- Operator: grok-only; no live API; interface credentials available.
- Wave-5u residual/bulk real methods remain BLOCK BEFORE NETWORK.
- FIX-VERIFY 186.4: no IR product blockers; offline commit suite + live products
  reconfirm; complete:false. COMMIT next.

## Verification

- Research103 docs re-fetch identical to research99–102.
- Research103 dual-session: bank-accounts, products, clients path/h1 match A↔B;
  daybooks still error shell (not re-probed as product).
- Coverage honesty: UI 4 live/vision; API live 0; complete false.
- Credentialed discovery uses second interface only; no API token.

## Review decisions (authoritative)

- Slice 186.4 product (`ui_products_list`): **ACCEPT**; vision **ACCEPT** with
  purge; completeness **FAIL**.
- Slice 186.3 product (`ui_invoices_list`): **ACCEPT** (prior).
- Slice 186.2 auth remember + dual READY: **ACCEPT** (prior).
- Wave-5m through Wave-5s-C product: **ACCEPT offline only** where previously recorded.
- Research88–103: **ACCEPT as research** (where reviewed).
- Overall completeness: **FAIL**.

## Open coverage work

1. Next UI read-only shells from research103 secondary freezes: `ui_clients_list`
   (`/clients` / `Kunder` / `Opret kontakt` ↔ contacts.list) or UI-only
   `ui_bank_accounts_list` (no `api_bank_accounts_*`).
2. Daybooks stays blocked on error shell until recovery research.
3. Residual/bulk product blocked; no live methods; offline contract only.
4. Full UI parity + vision under dedicated non-production org.
5. `auth_status` remains login-signature-only; use `auth_login_wait` for READY.

## Evidence boundaries

- Do not implement residual or bulk tools from unauth fixtures alone.
- Empty bulk `ids[]` is an error (`INVALID_DELETE_ID_ARRAY`), not a no-op.
- No greening from research alone; no invent `api_bank_accounts_*`.
- Interface read-back: second browser session only; no live API.
- Grok-only children (`--agent=grok`).
- No webhooks (official 0 mentions).
- Shell-open UI rows: empty request_fields, pagination null, list_shell_open_only.

## References

- Research103 brief: `.fractal/main.billy_complete/tmp/grok-research.md`
- IR 186.4: `.fractal/main.billy_complete/tmp/grok-review.md`
- Vision: `.fractal/main.billy_complete/tmp/vision-records/ui_products_list.json`
- Plan: `plans/2026-07-31T10:12:54.977Z-186.4-ui_products_list.md`
- Protocol: `wiki/credentialed_session_discovery_protocol.md`
- Invoices shell wiki: `wiki/ui_invoices_list_shell.md`
