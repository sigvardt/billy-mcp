---
name: wave_fivek_freeze_codex_fallback_review
title: Wave-5k Codex Power fallback freeze review
desc: Non-authoritative Codex Power fallback ACCEPT of the Wave-5k bank-payment offline contract; independent Grok acceptance and product work remain blocked.
tags: [billy, api, bank_payments, writes, confirmation, fallback, review]
sources:
  - https://www.billy.dk/api/
  - wiki/wave_fivek_ticketed_writes_contract.md
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
  - coverage/api_v2_manifest.yaml
  - coverage/status.json
  - tests/unit/test_coverage_server.py
created: 2026-07-30T04:46:00Z
updated: 2026-07-30T04:46:00Z
---

# Wave-5k Codex Power fallback freeze review

> **Codex Power fallback only.** This review was performed because the Grok
> route failed authentication before making any reviewer edit. It is **not** an
> independent Grok review, **not** a freeze acceptance, and **not** a product
> approval. It cannot replace the mandatory independent Grok freeze gate or
> authorise Wave-5k implementation.

## Bounded result

**ACCEPT — bounded to offline-contract fidelity.** The committed Wave-5k page
faithfully freezes the documented create/update boundary for singular
`bankPayments` and keeps every unresolved or non-qualified surface fail-closed.
This result says nothing about a future implementation, live qualification,
browser/UI parity, vision, bulk operations, or project completeness.

The reviewed root commit is
`4775256d73e6dee533b3513156723ecedb8f5b0c`
(`main.billy_complete: iteration 2.51 (record wave5k review gate)`). Its
`wiki/wave_fivek_ticketed_writes_contract.md` bytes match the committed contract
reviewed here; that page was originally added at
`0e1ac72e09db3d0269a9ed00aea2c985819dfca8`.

## Official API and contract fidelity

The current [Billy API v2 documentation](https://www.billy.dk/api/) locks the
base to `https://api.billysbilling.com/v2`, defines create as a singular-root
`POST`, and defines update as `PUT /v2/<resource>/:id`: its body may omit the
id, but a supplied body id must equal the route id; omitted properties are not
changed. Its create/update response convention returns changed records under
plural resource roots. The `bankPayments` resource is documented for create and
update, and its field table confirms the immutable/readonly boundaries retained
by the frozen page. The documentation's payment example specifically uses
`POST /bankPayments` with a `bankPayment` root.

| Reviewed requirement | Result |
| --- | --- |
| Create twins | PASS — exactly `api_bank_payments_create_preview` then `api_bank_payments_create_execute`; the only HTTP write is `POST /bankPayments`. |
| Update twins | PASS — exactly `api_bank_payments_update_preview` then `api_bank_payments_update_execute`; the only HTTP write is partial `PUT /bankPayments/:id`. |
| Request and response roots | PASS — both previews accept the singular `bankPayment` map; successful non-delete mapping requires `bankPayments`, while any additional root is mapped only if actually returned. |
| Input boundary | PASS — outer inputs are strict: create is exactly `{bankPayment}` and update is exactly `{id, bankPayment}`. The inner map remains intentionally opaque rather than inventing a relation, amount, date, or enum wire schema. |
| Partial-update identity | PASS — a supplied `bankPayment.id` must equal the route `id`, but is not otherwise required. |

This is a correct conservative application of the [official generic resource
conventions](https://www.billy.dk/api/) to the explicitly documented
`/v2/bankPayments` resource. In particular, the page preserves documented
immutable and readonly field information without claiming it as a new typed
request schema.

## Ticket and execution boundary

PASS — the page matches the approved design's autonomous-write protocol:
preview is non-mutating and creates a short-lived, single-use ticket bound to
the exact server tool, organisation, target, canonical request, and expected
effect. Execute accepts only `confirmation_ticket`; an executor-name mismatch
fails before ticket consumption and before HTTP. The shared confirmation store
and write-protocol service are required to make that binding shared across the
four tools.

The page also retains the design's exact-operation safety boundary: execution
performs one write request only, discards prepared writes, and has no write
retry. Changed business data or expected state requires a new preview. These
requirements accord with the approved design's ticket binding and its execute
sequence, and do not create a generic HTTP or browser capability.

## Authentication, delete, bulk, and exclusion checks

Credential-free probes against the locked base used only empty synthetic
`bankPayment` bodies and returned `401 AUTHENTICATION_REQUIRED` for both
`POST /bankPayments` and `PUT /bankPayments/not-a-real-id`. The `DELETE` probe
against that same nonexistent identifier returned `405 METHOD_NOT_ALLOWED` with
the service message that `bankPayments` does not support deleting a single
record. No credential, production data, persistent write, browser/UI session,
screenshot, HAR, or trace was used.

The official resource table still names create, update, delete, bulk save, and
bulk delete. The observed singular-delete 405 correctly overrides that broad
Supports listing for this contract: no delete preview or execute tool is
authorised. The bulk entries remain ambiguous because the documentation supplies
neither a complete bulk request/response shape nor a partial-failure contract;
no bulk tool follows from the listing.

Accordingly, the page correctly excludes delete, bulk, generic HTTP/browser
tools, webhooks, invented cleanup or restoration, live claims, UI parity, and
vision claims. It does not treat an unauthenticated response as a successful
write, delete, cleanup, or live test.

## Fail-closed baseline

PASS — the current generated `coverage/status.json` reports 166 implemented
and contract-tested offline API rows, zero live-tested rows, zero
vision-verified rows, 92 ambiguous-bulk API rows, and `complete: false`.
The registry assertion in `tests/unit/test_coverage_server.py` remains 238
`api_*` tools. The two bank-payment create/update inventory rows remain
unimplemented, untested, and not live-tested; their future execute twins do not
create additional coverage rows. The delete and bulk rows stay red.

This preserves the approved design's rule that an API row is not green without
implemented, contract-tested, and live-tested evidence; vision remains required
for interface rows. It also preserves the design's prohibition on treating
ambiguous bulk documentation or another unresolved gap as completeness.

## Gate remaining closed

This bounded ACCEPT is a review of the offline page only. The mandatory
independent Grok freeze review remains required before any Wave-5k product leaf.
Until that separate gate and subsequent real implementation/testing occur,
`api.bankPayments.create` and `api.bankPayments.update` remain red, singular
delete remains excluded, bulk remains ambiguous, and the repository remains
incomplete.
