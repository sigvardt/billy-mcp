---
name: state
desc: Current node state, verified review decisions, and open qualification work.
tags: [billy, coverage, review]
sources:
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
  - https://www.billy.dk/api/
created: 2026-07-29T09:56:00Z
updated: 2026-07-31T10:40:00Z
---

# state

## Current state

- Research brief (clients product freeze): `.fractal/main.billy_complete/tmp/grok-research.md`
  (research104). Dual evidence: `tmp/discovery103/summary.json` (scrubbed).
- Docs unchanged (ETag `wcw4x9hqvu3603`, MD5 `8b94b0135c91fd15fe54ea33e088a4be`).
- Product `ui_clients_list` ACCEPT (independent review): path `/:org_slug/clients`,
  h1 `Kunder`, CTA `Opret kontakt` presence-only; dual live + vision accept +
  purge_verified. Uncommitted product tree pending COMMIT.
- UI live+vision green: invoices discovery+list, products discovery+list,
  customers discovery + contacts.list parity (6 rows).
- Coverage status: implemented/contract 190; live/vision 6; API live 0
  (`out_of_scope_by_user` at status blocker). Residual bulk 92 + remaining UI red.
  `complete: false`.
- Operator: grok-only; no live API; interface credentials available.
- Residual/bulk real methods remain BLOCK BEFORE NETWORK.
- FIX-VERIFY: no product blockers; offline commit suite 1331 pass; live clients
  reconfirm pass; complete false. COMMIT next.

## Verification

- Docs re-fetch matches prior research fingerprints.
- Dual-session clients path/h1/CTA match A↔B; vision purge verified.
- Coverage honesty: UI 6 live/vision; API live 0; complete false.
- Interface read-back uses second browser session only; no API token.

## Review decisions (authoritative)

- Product `ui_clients_list`: **ACCEPT**; vision **ACCEPT** with purge;
  completeness **FAIL**.
- Product `ui_products_list`: **ACCEPT** (prior).
- Product `ui_invoices_list`: **ACCEPT** (prior).
- Auth remember + dual READY: **ACCEPT** (prior).
- Wave-5m through Wave-5s-C product: **ACCEPT offline only** where previously recorded.
- Research freezes through clients product: **ACCEPT as research** where reviewed.
- Overall completeness: **FAIL**.

## Open coverage work

1. Next UI read-only shell: `ui_bank_accounts_list` (path `/bank-accounts`,
   h1 `Bankkonti`; UI-only; do not invent `api_bank_accounts_*`).
2. Daybooks stays blocked on error shell until recovery research.
3. Residual/bulk product blocked; offline contract only; no live API methods.
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

- Research clients brief: `.fractal/main.billy_complete/tmp/grok-research.md`
- IR clients product: `.fractal/main.billy_complete/tmp/grok-review.md`
- Vision: `.fractal/main.billy_complete/tmp/vision-records/ui_clients_list.json`
- Plan: `plans/2026-07-31T10:27:57.821Z-186.5-ui_clients_list.md`
- Wiki: `wiki/ui_clients_list_shell.md`
- Protocol: `wiki/credentialed_session_discovery_protocol.md`
