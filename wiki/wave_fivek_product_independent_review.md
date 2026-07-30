---
name: wave_fivek_product_independent_review
title: Wave-5k offline product independent review ACCEPT
desc: Authoritative root Grok acceptance of the offline bankPayments create and update ticketed-write product (delete excluded on 405) at root integration ee40a40.
tags: [billy, api, bank, payments, writes, review, coverage]
sources:
  - https://www.billy.dk/api/
  - wiki/wave_fivek_ticketed_writes_contract.md
  - wiki/wave_fivek_freeze_independent_review.md
  - wiki/offline_write_probe_rules.md
  - src/billy_mcp/api/bank_payment_writes.py
  - src/billy_mcp/api/write_protocol.py
  - src/billy_mcp/client.py
  - src/billy_mcp/server.py
  - tests/api/test_bank_payment_writes.py
  - tests/unit/test_coverage_server.py
  - coverage/api_v2_manifest.yaml
  - coverage/ui_workflows_manifest.yaml
  - coverage/status.json
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
created: 2026-07-30T05:25:00Z
updated: 2026-07-30T05:25:00Z
---

# Wave-5k offline product independent review ACCEPT

## Verdict

| Claim | Result |
| --- | --- |
| Wave-5k offline product | **ACCEPT** |
| Official documentation versus create/update inventory greens | **PASS** |
| Four-tool surface versus freeze contract | **PASS** |
| Ticket binding, auth empty-token, path lock, no delete tools | **PASS** |
| Coverage honesty (`complete: false`; live 0; delete/bulk red) | **PASS** |
| Live, UI, vision, bulk, singular delete, completeness | **not claimed / fail-closed** |

This is the authoritative root Grok product ACCEPT for the offline Wave-5k slice
at parent HEAD **`ee40a40`** (product merge `7e02ff8` from child
`main.billy_complete.wave5k_bank_payment_product` @ `2cdbffa`). This page
retains the complete non-sensitive decision evidence needed for the product
gate; ephemeral working notes are not part of the project record.

No production code, coverage flags, or tool surface was changed by this review.

## Accepted surface

Exactly four ticketed tools:

| Inventory id | Preview | Execute | Client path | Request root | Required success root |
| --- | --- | --- | --- | --- | --- |
| `api.bankPayments.create` | `api_bank_payments_create_preview` | `api_bank_payments_create_execute` | `POST /bankPayments` | opaque `bankPayment` | `bankPayments` |
| `api.bankPayments.update` | `api_bank_payments_update_preview` | `api_bank_payments_update_execute` | `PUT /bankPayments/:id` | opaque `bankPayment` + non-empty route `id` | `bankPayments` |

Implementation: `src/billy_mcp/api/bank_payment_writes.py` registered from
`src/billy_mcp/server.py` on the shared root `WriteProtocolService` /
`ConfirmationStore`. Outer inputs forbid extras; update enforces optional inner
`bankPayment.id` equality with the route id; execute accepts only
`confirmation_ticket`; one write with no retry; undeclared related roots are not
fabricated.

## Evidence

- Official docs: https://www.billy.dk/api/ — ETag `hsisik4g9p3603`, MD5
  `c2efda0ee4cf9cf200e14910c5fc6996`, body 147934 bytes (reconfirmed at review).
- Unauth gates: POST/PUT **401** `AUTHENTICATION_REQUIRED`; DELETE **405**
  singular-delete refusal (research53 probes).
- Freeze gate already **ACCEPT** in `wiki/wave_fivek_freeze_independent_review.md`.
- Offline tests: `uv run pytest tests/api/test_bank_payment_writes.py
  tests/unit/test_coverage_server.py -q` → **20 passed** at review time.
- Root arithmetic: **242** `api_*` tools; **168** implemented and
  contract-tested offline rows; live **0**; vision **0**; `complete: false`.
- Delete inventory row remains red and unregistered; bulk rows remain
  `ambiguous_bulk` with empty tools; all UI bankPayments rows remain red.

## Explicit exclusions

Singular delete tools; bulk save/delete; live qualification; browser/UI parity;
vision verification; webhooks; generic HTTP; Wave-5l freezes; overall
completeness.

## Authorisation opened by this ACCEPT

Codex Power may proceed to Wave-5l offline freeze authoring for
`api.salesTaxPayments.create` and `.update` only (four tools; no singular delete;
void cleanup via documented `isVoided` when live), under a new freeze page and
independent freeze review. This product ACCEPT does not itself freeze or
implement sales-tax payments.

## Non-blocking notes

- Shared auth mapping already treats `OAUTH_INVALID_ACCESS_TOKEN`; product tests
  explicitly cover empty token and 401 `AUTHENTICATION_REQUIRED` only.
- Inventory cleanup wording debt on later resources is out of this product
  scope.
