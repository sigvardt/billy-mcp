---
name: wave_fivel_freeze_independent_review
title: Wave-5l contract freeze independent review ACCEPT
desc: Authoritative root Grok acceptance of the cited offline contract for singular salesTaxPayments create and update ticketed writes (singular delete excluded on 405).
tags: [billy, api, sales-tax, payments, writes, review, coverage]
sources:
  - https://www.billy.dk/api/
  - wiki/wave_fivel_ticketed_writes_contract.md
  - wiki/wave_fivek_product_independent_review.md
  - wiki/offline_write_probe_rules.md
  - coverage/api_v2_manifest.yaml
  - coverage/status.json
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
created: 2026-07-30T05:44:00Z
updated: 2026-07-30T05:44:00Z
---

# Wave-5l contract freeze independent review ACCEPT

## Verdict

| Claim | Result |
| --- | --- |
| Wave-5l cited contract freeze | **ACCEPT** |
| Official documentation versus maintained inventory | **PASS** |
| Unauth method gates (POST/PUT 401, DELETE 405) | **PASS** |
| Freeze versus exact two-row / four-tool map | **PASS** |
| Coverage honesty before product integration | **PASS** |
| Wave-5l product implementation | **not accepted** — separate product leaf and product review required |
| Live, UI, vision, bulk, and completeness | **not claimed / fail-closed** |

The authoritative root independent review accepts the freeze page
`wiki/wave_fivel_ticketed_writes_contract.md` (content MD5
`3c49c4f41f3d9485a177a6ee643db412`). Full cited findings live outside the public
repository at `.fractal/main.billy_complete/tmp/grok-review.md`.

This page is the freeze gate for Wave-5l. It is not product acceptance.

## Exact reviewed scope

The accepted contract freezes exactly two singular API v2 JSON CUD operations
(four ticketed tools: two preview + two execute):

| Inventory id | Preview tool | Execute tool | Method and client path | Singular request root | Required success root |
| --- | --- | --- | --- | --- | --- |
| `api.salesTaxPayments.create` | `api_sales_tax_payments_create_preview` | `api_sales_tax_payments_create_execute` | `POST /salesTaxPayments` | `salesTaxPayment` | `salesTaxPayments` |
| `api.salesTaxPayments.update` | `api_sales_tax_payments_update_preview` | `api_sales_tax_payments_update_execute` | `PUT /salesTaxPayments/:id` | `salesTaxPayment` | `salesTaxPayments` |

The accepted contract preserves:

- Locked base `https://api.billysbilling.com/v2` and client-relative paths
  without a duplicated `/v2`.
- Opaque inner `salesTaxPayment` maps with strict outer inputs (create exactly
  `{salesTaxPayment}`; update exactly `{id, salesTaxPayment}`).
- Partial update id equality when an inner `id` is supplied.
- Shared root `ConfirmationStore` and `WriteProtocolService`.
- Short-lived single-use confirmation tickets; execute input is only
  `{confirmation_ticket}`; executor binding mismatch fails before ticket
  consumption and before HTTP.
- Exactly one write request on execute; no write retry.
- Related plural response roots mapped only when actually returned.
- Official field boundaries as constraints (`salesTaxReturn`, `entryDate`,
  `account` immutable required; `amount` and `side` readonly; `isVoided` only
  as a documented mutable candidate without invented unvoid or cleanup proof)
  without inventing a typed wire schema or public create sample that does not
  exist for this resource.

## Explicit exclusions (still red / not authorised)

| Surface | Gate evidence | Offline decision |
| --- | --- | --- |
| Singular delete tools | Supports omits singular delete; unauthenticated `DELETE /salesTaxPayments/:id` → **405** `METHOD_NOT_ALLOWED` with singular-delete refusal | **No** delete preview/execute tools; no delete inventory row |
| Bulk save / bulk delete | Supports flags only; inventory `ambiguous_bulk` with empty `tool_name` | **No** bulk tools |
| Live qualification | `BILLY_API_TOKEN` unavailable; live_tested 0 | Not authorised by freeze |
| UI / vision | All UI salesTaxPayments parity rows red; vision_verified 0 | Not authorised by freeze |
| Webhooks | 0 official mentions | Do not invent |
| Completeness | `coverage/status.json` `complete: false` | Unchanged |

Inventory create cleanup still says “delete dedicated test resource”. That text
is debt only; this freeze forbids reading it as singular-delete authorisation.

## Official evidence reconfirmed at review time

- Docs: https://www.billy.dk/api/ — ETag `hsisik4g9p3603`, MD5
  `c2efda0ee4cf9cf200e14910c5fc6996`, body 147934 bytes.
- salesTaxPayments Supports: get by id, list, create, update, bulk save, bulk
  delete (no singular delete).
- Unauth POST/PUT → 401 `AUTHENTICATION_REQUIRED`.
- Unauth DELETE → 405 with singular-delete refusal.
- Inventory create/update rows remain `implemented: false`,
  `contract_tested: false`, `live_tested: false` until product lands.
- Root arithmetic at freeze: **242** `api_*` tools / **168** offline green;
  product module `sales_tax_payment_writes.py` absent.

## Product authorisation opened by this ACCEPT

Codex Power may implement exactly the four frozen tools in
`src/billy_mcp/api/sales_tax_payment_writes.py` with focused tests and server
registration through the shared write protocol. Target after real tests:
**246** tools / **170** offline implemented+contract_tested; live and vision
remain 0; bulk stays red; `complete: false`.

Do not fold payment writes into `sales_tax_writes.py` (rulesets/rules).

Independent product review is still required after product merge. This freeze
ACCEPT does not green coverage and does not authorise bulk, delete, live, UI,
vision, or completeness claims.
