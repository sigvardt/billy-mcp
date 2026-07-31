---
name: state
desc: Current node state, verified review decisions, and open qualification work.
tags: [billy, coverage, review]
sources:
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
  - https://www.billy.dk/api/
created: 2026-07-29T09:56:00Z
updated: 2026-07-31T10:55:00Z
---

# state

## Current state

- Product `ui_bank_accounts_list` ACCEPT (IR 186.6). FIX-VERIFY clean: no product fixes;
  lint + 1338 offline + live reconfirm. Uncommitted product ready for COMMIT.
- Coverage: implemented/contract 191; live/vision 7; API live 0; complete false.
- Docs fingerprint ETag `wcw4x9hqvu3603`, MD5 `8b94b0135c91fd15fe54ea33e088a4be`.
- Operator: grok-only; no live API.

## Verification

- Dual-session bank-accounts path/h1/CTA; vision purge_verified.
- UI-only discovery greened; no api_bank_accounts_*; no bankLines parity green.

## Review decisions (authoritative)

- Product `ui_bank_accounts_list`: **ACCEPT**.
- Prior invoices/products/clients/auth: **ACCEPT**.
- Overall completeness: **FAIL**.

## Open coverage work

1. COMMIT ui_bank_accounts_list product.
2. Next UI shell after commit (quotes/financing/daybooks recovery research).
3. Residual/bulk offline red only; no live API methods.

## Evidence boundaries

- No invent `api_bank_accounts_*`.
- No green bankLines parity from bank-accounts shell alone.
- Interface read-back: second browser session only.
- Grok-only children (`--agent=grok`).

## References

- Plan: `plans/2026-07-31T10:43:41.114Z-186.6-ui_bank_accounts_list.md`
- IR: `tmp/grok-review.md`
- Vision: `tmp/vision-records/ui_bank_accounts_list.json`
- Wiki: `wiki/ui_bank_accounts_list_shell.md`
