---
name: wave_fivek_freeze_independent_review
title: Wave-5k contract freeze independent review ACCEPT
desc: Authoritative root Grok acceptance of the cited offline contract for singular bankPayments create and update ticketed writes (delete excluded on 405).
tags: [billy, api, bank, payments, writes, review, coverage]
sources:
  - https://www.billy.dk/api/
  - wiki/wave_fivek_ticketed_writes_contract.md
  - wiki/wave_fivek_freeze_authoring_authority_research_independent_review.md
  - wiki/wave_fivek_freeze_ready_research_independent_review.md
  - wiki/wave_fivek_freeze_implementation_research_independent_review.md
  - wiki/wave_fivek_freeze_codex_fallback_review.md
  - wiki/offline_write_probe_rules.md
  - coverage/api_v2_manifest.yaml
  - coverage/status.json
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
created: 2026-07-30T04:58:00Z
updated: 2026-07-30T04:58:00Z
---

# Wave-5k contract freeze independent review ACCEPT

## Verdict

| Claim | Result |
| --- | --- |
| Wave-5k cited contract freeze | **ACCEPT** |
| Official documentation versus maintained inventory | **PASS** |
| Unauth method gates (POST/PUT 401, DELETE 405) | **PASS** |
| Freeze versus exact two-row / four-tool map | **PASS** |
| Coverage honesty before product integration | **PASS** |
| Wave-5k product implementation | **not accepted** — separate product leaf and product review required |
| Live, UI, vision, bulk, and completeness | **not claimed / fail-closed** |

The authoritative root `INDEPENDENT-REVIEW` Grok step accepted the freeze page at
root HEAD **`4535c01`** (`wiki/wave_fivek_ticketed_writes_contract.md`, content
MD5 `b854527d6b91af47847ff2eb3a586752`). Full cited findings live outside the
public repository at `.fractal/main.billy_complete/tmp/grok-review.md`.

A prior Codex Power fallback page
(`wiki/wave_fivek_freeze_codex_fallback_review.md`) recorded non-authoritative
contract-fidelity ACCEPT only and explicitly refused to open product. That page
does not replace this Grok freeze ACCEPT. This root review is the authoritative
freeze gate for Wave-5k.

## Exact reviewed scope

The accepted contract freezes exactly two singular API v2 JSON CUD operations
(four ticketed tools: two preview + two execute):

| Inventory id | Preview tool | Execute tool | Method and client path | Singular request root | Required success root |
| --- | --- | --- | --- | --- | --- |
| `api.bankPayments.create` | `api_bank_payments_create_preview` | `api_bank_payments_create_execute` | `POST /bankPayments` | `bankPayment` | `bankPayments` |
| `api.bankPayments.update` | `api_bank_payments_update_preview` | `api_bank_payments_update_execute` | `PUT /bankPayments/:id` | `bankPayment` | `bankPayments` |

The accepted contract preserves:

- Locked base `https://api.billysbilling.com/v2` and client-relative paths
  without a duplicated `/v2`.
- Opaque inner `bankPayment` maps with strict outer inputs (create exactly
  `{bankPayment}`; update exactly `{id, bankPayment}`).
- Partial update id equality when an inner `id` is supplied.
- Shared root `ConfirmationStore` and `WriteProtocolService`.
- Short-lived single-use confirmation tickets; execute input is only
  `{confirmation_ticket}`; executor binding mismatch fails before ticket
  consumption and before HTTP.
- Exactly one write request on execute; no write retry.
- Related plural response roots mapped only when actually returned.
- Official field boundaries as constraints (immutable create fields, readonly
  `createdTime` / `contactBalancePostings`, documented `cashSide` debit/credit,
  irreversible `isVoided` void path) without inventing a typed wire schema.

## Explicit exclusions (still red / not authorised)

| Surface | Gate evidence | Offline decision |
| --- | --- | --- |
| Singular delete tools | Unauthenticated `DELETE /bankPayments/:id` → **405** `METHOD_NOT_ALLOWED` with message that singular delete is unsupported; overrides Supports delete flag | **No** delete preview/execute tools |
| Bulk save / bulk delete | Supports flags only; no bulk request/response/partial-failure contract; inventory `ambiguous_bulk` with empty `tool_name` | **No** bulk tools |
| Live qualification | `BILLY_API_TOKEN` unavailable; live_tested 0 | Not authorised by freeze |
| UI / vision | UI implemented 0; vision_verified 0 | Not authorised by freeze |
| Webhooks | 0 official mentions | Do not invent |
| Completeness | `coverage/status.json` `complete: false` | Unchanged |

Inventory may still record `api.bankPayments.delete` with a `tool_name`; that
row stays red and unregistered.

## Official evidence reconfirmed at review time

- Docs: https://www.billy.dk/api/ — ETag `hsisik4g9p3603`, MD5
  `c2efda0ee4cf9cf200e14910c5fc6996`, body 147934 bytes.
- bankPayments Supports include create and update (and list delete flags that
  offline product must not over-claim for singular delete).
- Unauth POST/PUT → 401 `AUTHENTICATION_REQUIRED`.
- Unauth DELETE → 405 with singular-delete refusal.
- Inventory create/update rows remain `implemented: false`,
  `contract_tested: false`, `live_tested: false` until product lands.

## Product authorisation opened by this ACCEPT

Codex Power may implement exactly the four frozen tools in
`src/billy_mcp/api/bank_payment_writes.py`, register them through the shared
write protocol in `src/billy_mcp/server.py`, and add offline contract tests.
Target arithmetic after real implementation and tests only: **242** `api_*`
tools and **168** implemented + contract_tested offline API rows. Delete, bulk,
live, UI, vision, and completeness remain fail-closed.

This page is **not** product ACCEPT. Product requires its own independent
review after merge.
