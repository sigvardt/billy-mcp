---
name: wave_fivem_freeze_codex_fallback_review
title: Wave-5m Codex Power fallback freeze review
desc: Non-authoritative Codex Power fallback ACCEPT of the contact-balance-payment offline contract at fb6bb22; mandatory independent Grok review remains outside this record.
tags: [billy, api, contact_balance_payments, writes, confirmation, fallback, review]
sources:
  - https://www.billy.dk/api/
  - wiki/wave_fivem_ticketed_writes_contract.md
  - wiki/offline_write_probe_rules.md
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
  - coverage/api_v2_manifest.yaml
  - coverage/status.json
  - .fractal/main.billy_complete/tmp/grok-research.md
created: 2026-07-30T07:46:02Z
updated: 2026-07-30T07:46:02Z
---

# Wave-5m Codex Power fallback freeze review

> **Codex Power fallback only.** This is non-authoritative evidence after the
> designated Grok reviewer failed authentication before reviewer actions. It is
> **not** an independent Grok review, final Grok audit, freeze-gate replacement,
> or product approval. It authorises no tools or coverage changes.

## Bounded result

**ACCEPT — offline-contract fidelity only.** The merged Wave-5m contract at
reviewed root commit `fb6bb22`
(`fb6bb226d7ce2457f6fc7773582edf0231855924`)
accurately freezes exactly two singular `contactBalancePayments` operations:
create and update. They have exactly four future preview/execute tools. No
defect was found in the contract's frozen boundary.

The review streamed a clean `git archive fb6bb22`; the archived contract's
SHA-256 was `1878f3fdaa3c773637cef98fb085ac24c810d6ad8f26e4974f362d2ba464e785`,
matching `fb6bb22:wiki/wave_fivem_ticketed_writes_contract.md`. No archive or
raw external evidence was retained.

## Official source and exact frozen surface

The current [Billy API v2 documentation](https://www.billy.dk/api/) still
identifies `https://api.billysbilling.com/v2` as the API endpoint; its generic
conventions use a singular-root `POST /v2/{plural}`, partial
`PUT /v2/{plural}/:id`, require a supplied body id to match the route id, and
return changed records under plural roots. The current page's ETag is
`hsisik4g9p3603`; its body is 147934 bytes with MD5
`c2efda0ee4cf9cf200e14910c5fc6996`. Its
`/v2/contactBalancePayments` entry lists get, list, create, update, bulk save,
and bulk delete — not singular delete.

| Operation | Future preview | Future execute | Client-relative write | Request root | Required response root |
| --- | --- | --- | --- | --- | --- |
| Create | `api_contact_balance_payments_create_preview` | `api_contact_balance_payments_create_execute` | `POST /contactBalancePayments` | `contactBalancePayment` | `contactBalancePayments` |
| Update | `api_contact_balance_payments_update_preview` | `api_contact_balance_payments_update_execute` | `PUT /contactBalancePayments/:id` | `contactBalancePayment` | `contactBalancePayments` |

The contract correctly treats each preview as the sole future inventory
`tool_name`; execute twins do not create inventory rows. No product tool is
registered or authorised by this result.

## Protocol and fail-closed checks

PASS — create accepts exactly `{contactBalancePayment: map}`; update accepts
exactly `{id: non-empty string, contactBalancePayment: map}`. Both outer
objects are strict and the inner map remains opaque. A present inner update id
must equal the route id but is otherwise optional. The page does not invent
relation wire forms, dates, amounts, enum aliases, or a `bankPayment`-derived
payload schema.

PASS — previews are non-mutating. Future execution accepts only a non-empty
`confirmation_ticket`, binds the ticket to the exact operation and executor via
the shared `ConfirmationStore` and `WriteProtocolService`, and rejects an
executor mismatch as `CONFIRMATION_MISMATCH` before ticket consumption or HTTP.
The shared protocol's typed response mapping requires
`contactBalancePayments` for non-delete writes and does not fabricate absent
records. It issues one write request after successful ticket consumption,
discards the prepared request, and has no retry path.

## Authentication, delete, and red boundaries

Research57's unauthenticated `POST` and `PUT` observations are correctly
treated as 401 authentication gates only: they are not accepted-payload,
mutation, cleanup, or live-test evidence. This fallback supplied no
credentials, made no API request, created no record, and used no browser or
browser automation.

Research57 also records 405 `METHOD_NOT_ALLOWED` for singular
`DELETE /contactBalancePayments/:id`; together with the current documentation's
absence of singular delete from Supports, that keeps singular DELETE absent.
There is no delete preview/execute pair or delete inventory row. Bulk save and
bulk delete stay ambiguous with empty tool names because no safe bulk
method/body/partial-failure contract exists.

The reviewed coverage state remains fail-closed: create and update are
discovered but `implemented`, `contract_tested`, and `live_tested` are false;
the two bulk rows remain red; `coverage/status.json` reports 170 offline rows,
zero live-tested rows, zero vision-verified rows, 92 ambiguous-bulk API rows,
339 UI rows, and `complete: false`. The stale create-row cleanup phrase is a
future coverage debt, not authority for delete or cleanup, while that row stays
red.

Accordingly, bulk, live, UI, vision, credentials, browser, webhooks, generic
HTTP/browser controls, persistent test data, cleanup claims, and completeness
remain out of scope and fail-closed.

## Validation and gate status

Non-live root checks passed:

- `uv run python scripts/check_coverage.py` — passed (305 API rows, 339 UI rows).
- `uv run pytest tests/coverage/test_coverage_inventory.py tests/unit/test_coverage_server.py tests/unit/test_write_protocol.py tests/unit/test_confirmations.py` — 56 passed.
- `BILLY_TEST_MODE=commit bash .fractal/main.billy_complete.wave5m_freeze_review_codex_fallback/scripts/test.sh` — passed; the seeded script has no additional command.
- `BILLY_TEST_MODE=commit bash .fractal/main.billy_complete.wave5m_freeze_review_codex_fallback/scripts/lint.sh` — passed.

The mandatory independent Grok freeze review and final Grok audit remain
**outstanding from this fallback record**. This ACCEPT cannot satisfy, replace,
or retrospectively claim either gate; consult separate authoritative Grok
evidence for any gate or product-authorisation decision.
