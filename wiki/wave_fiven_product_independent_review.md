---
name: wave_fiven_product_independent_review
title: Wave-5n invoice-late-fee product independent review ACCEPT
desc: Authoritative offline Grok ACCEPT for singular invoiceLateFees create and update ticketed write tools on root a3ad538; live, UI, vision, bulk, singular delete, and completeness remain fail-closed.
tags: [billy, api, invoice-late-fees, writes, review, product]
sources:
  - https://www.billy.dk/api/
  - wiki/wave_fiven_ticketed_writes_contract.md
  - wiki/wave_fiven_freeze_independent_review.md
  - wiki/offline_write_probe_rules.md
  - coverage/api_v2_manifest.yaml
  - coverage/status.json
  - src/billy_mcp/api/invoice_late_fee_writes.py
  - src/billy_mcp/api/write_protocol.py
  - src/billy_mcp/server.py
  - src/billy_mcp/config.py
  - tests/api/test_invoice_late_fee_writes.py
  - tests/unit/test_coverage_server.py
  - tests/coverage/test_coverage_inventory.py
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
created: 2026-07-30T10:00:00Z
updated: 2026-07-30T10:00:00Z
---

# Wave-5n invoice-late-fee product independent review ACCEPT

## Verdict

| Claim | Result |
| --- | --- |
| Wave-5n offline product (singular create + update ticketed writes) | **ACCEPT** |
| Official documentation versus create/update product surface | **PASS** |
| Four write tools versus freeze contract | **PASS** |
| Ticket binding, path escape, response-root mapping, no-retry | **PASS** |
| Coverage honesty (`complete: false`; live 0; vision 0; bulk red; no singular delete) | **PASS** |
| Live, UI, vision, bulk, singular delete, webhook, completeness | **not claimed / fail-closed** |

**Verdict: ACCEPT**

This authoritative root Grok product review accepts only the offline Wave-5n
invoice-late-fee ticketed-write product slice at parent baseline **`a3ad538`**
(`a3ad538cc2612207a0fa5544c7740f43f24a7259`), which contains product merge
`8c21d03` and the four tools added by `8fab311`.

This ACCEPT is not live testing, UI/vision acceptance, bulk resolution,
singular-delete authorisation, webhook support, or overall product completeness.

No production source, tests, coverage rows, status values, or prior contract
pages were modified by this review.

## Reviewed baseline

| Item | Value |
| --- | --- |
| Root product baseline | `a3ad538` (`a3ad538cc2612207a0fa5544c7740f43f24a7259`) |
| Product merge | `8c21d03` (`merge main.billy_complete.wave5n_invoice_late_fee_product`) |
| Product implementation commit | `8fab311` (adds `invoice_late_fee_writes.py` + tests + inventory greening) |
| Freeze page | `wiki/wave_fiven_ticketed_writes_contract.md` (full-file MD5 `93e6d266d1718fa517ff645b3ca213ce`) |
| Freeze independent review | **ACCEPT** at `wiki/wave_fiven_freeze_independent_review.md` |

## Evidence classes (keep separate)

| Class | What it proves | What it does not prove |
| --- | --- | --- |
| Current official docs (`https://www.billy.dk/api/`) | Supports create/update; omits singular delete; property notes for opaque-map treatment | Authenticated success, cleanup, live qualification |
| Historical / this-review unauth probes (`https://api.billysbilling.com/v2`) | Method gates: POST/PUT 401; singular DELETE 405; bulk DELETE 405 | Live mutation, accepted payloads, response extensions |
| Offline contract tests | Schema, tickets, paths, mapping, no-retry, registry/coverage honesty | Live org behaviour, UI parity, vision |
| Live / UI / vision | Not performed | Not claimed |

## Official documentation (this review)

Fetched `https://www.billy.dk/api/` during this review:

| Fingerprint field | Observed value |
| --- | --- |
| HTTP ETag | `wcw4x9hqvu3603` |
| Body MD5 | `8b94b0135c91fd15fe54ea33e088a4be` |
| Body size | 147934 bytes |

Direct citation for `/v2/invoiceLateFees` (plain text from the official HTML):

> Supports: get by id, list, create, update, bulk save, bulk delete

Property notes observed on the same page:

| Property | Official notes | Product treatment check |
| --- | --- | --- |
| `invoice` | immutable, required | Opaque inner map only — **PASS** |
| `entryDate` | immutable, required | Opaque; no date encoding invented — **PASS** |
| `flatFee` | immutable, required | Opaque; no number encoding invented — **PASS** |
| `percentageFee` | immutable, required | Opaque; no number encoding invented — **PASS** |
| `createdTime` | readonly | Not a mutable outer field — **PASS** |
| `amount` | readonly | Not a mutable outer field — **PASS** |
| `isVoided` | (empty notes) | Unproven; no void/cleanup promise — **PASS** |

Singular delete is omitted from Supports. That omission, together with the
DELETE 405 probe below, keeps singular delete out of this product ACCEPT.

Access ETag/MD5 differ from the inventory lock string
(`hsisik4g9p3603` / `c2efda0ee4cf9cf200e14910c5fc6996`) while size stays
147934 bytes and the plain Supports + property table for this resource match
the freeze. Access-metadata churn alone is not a contract change (same reading
as the freeze independent review and `wiki/offline_write_probe_rules.md`).

## Unauthenticated probes (evidence only, not live qualification)

Against locked base `https://api.billysbilling.com/v2` with JSON object body,
no credentials:

| Call | Result |
| --- | --- |
| `POST /invoiceLateFees` body `{}` | **401** `AUTHENTICATION_REQUIRED` |
| `PUT /invoiceLateFees/nonexistent-probe-id` body `{}` | **401** `AUTHENTICATION_REQUIRED` |
| `DELETE /invoiceLateFees/nonexistent-probe-id` | **405** `METHOD_NOT_ALLOWED` — resource does not support deleting a single record |
| `DELETE /invoiceLateFees?ids[]=nonexistent` | **405** `METHOD_NOT_ALLOWED` — resource does not support bulk deleting records |

These reconfirm the freeze gates. They are not authenticated live tests and do
not green `live_tested`.

## Accepted product surface

Exactly four ticketed write tools (plus the pre-existing read tools
`api_invoice_late_fees_get` / `api_invoice_late_fees_list`, which are not part of
this write product ACCEPT):

| Inventory id | Preview tool | Execute tool | Method and client path | Singular request root | Required success root |
| --- | --- | --- | --- | --- | --- |
| `api.invoiceLateFees.create` | `api_invoice_late_fees_create_preview` | `api_invoice_late_fees_create_execute` | `POST /invoiceLateFees` | `invoiceLateFee` | `invoiceLateFees` |
| `api.invoiceLateFees.update` | `api_invoice_late_fees_update_preview` | `api_invoice_late_fees_update_execute` | `PUT /invoiceLateFees/:id` | `invoiceLateFee` | `invoiceLateFees` |

Implementation: `src/billy_mcp/api/invoice_late_fee_writes.py`, registered from
`src/billy_mcp/server.py` via `register_invoice_late_fee_write_tools` on the
shared root `WriteProtocolService` and `ConfirmationStore`. Client base remains
locked to `https://api.billysbilling.com/v2` in `src/billy_mcp/config.py`.

No invoiceLateFees delete, bulk, webhook, generic HTTP, or browser write tool is
registered.

## Assertions checked

| # | Assertion | Result | Evidence |
| --- | --- | --- | --- |
| 1 | Exactly four create/update preview+execute tools; no delete/bulk/webhook/generic HTTP/browser write tools for this product | **PASS** | `invoice_late_fee_writes.py` registers four `server.tool` names; product module list is create/update only; tests assert set equality and no delete/bulk names in the write server under test |
| 2 | POST `/invoiceLateFees` maps singular `invoiceLateFee` → plural `invoiceLateFees`; PUT uses escaped `/:id`; optional inner id must match route | **PASS** | Spec uses `collection_path="/invoiceLateFees"`, `singular_root="invoiceLateFee"`, `plural_root="invoiceLateFees"`; `execution_path_for` uses `quote(resource_id, safe="")`; update validator rejects mismatched inner id; path-escape test uses `late fee /?` → `/v2/invoiceLateFees/late%20fee%20%2F%3F` |
| 3 | Preview rejects unknown outer fields and preserves opaque JSON inner maps; execute is ticket-only | **PASS** | Pydantic `extra="forbid"` on preview/execute inputs; opaque `dict[str, JsonValue]`; execute tools take only `confirmation_ticket`; validation tests reject extras and replacement business fields on execute input |
| 4 | Shared confirmation tickets bind executor, payload, target, expected effect, organisation, expiry; single-use; one non-retried write | **PASS** | Shared `WriteProtocolService` + `ConfirmationStore`; binding via `confirmation_binding_for`; consume-before-request; failed 500 test asserts exactly one HTTP call |
| 5 | Response mapping accepts only required plural root; typed errors for malformed/missing roots and HTTP/auth failures | **PASS** | Success maps only `invoiceLateFees` (related `invoices` root dropped); missing/malformed root → `VALIDATION_ERROR`; 401/404/500 mapped; empty token → `AUTH_REQUIRED` with zero network |
| 6 | Product tests cover frozen schema, no-mutation preview, canonical binding, path escaping, tamper/wrong-executor/expiry/replay, no retry | **PASS** | `tests/api/test_invoice_late_fee_writes.py` (focused suite green) |
| 7 | Create/update inventory rows `implemented` + `contract_tested`; create cleanup states singular DELETE unsupported; update restoration-only | **PASS** | `coverage/api_v2_manifest.yaml`: create cleanup `live non-production cleanup strategy unqualified; singular DELETE is unsupported`; update cleanup `restore prior test state`; both `implemented: true`, `contract_tested: true`, `live_tested: false` |
| 8 | Root 254 `api_*` tools; 174 implemented/contract-tested; live 0; vision 0; `complete: false` | **PASS** | `coverage/status.json`; `tests/unit/test_coverage_server.py` asserts `len(api_tool_names) == 254` |
| 9 | invoiceLateFees bulk save/delete remain empty-tool, ambiguous, red | **PASS** | Both rows `source_kind`/`contract_status` `ambiguous_bulk`, `implemented: false`, `contract_tested: false`, `tool_name: ""` |
| 10 | Current docs support create/update and do not justify singular delete; 401/405 evidence accurate and not claimed as live testing | **PASS** | Official Supports quote above; probes table above; explicit non-live wording |
| 11 | No sensitive material, raw browser evidence, live mutation, or UI/vision claim | **PASS** | This page and the review method use only public docs, unauth status codes, offline tests, and committed source; no tokens, frames, HAR, or customer data |
| 12 | Focused invoice-late-fee/coverage/registry checks and non-live suite pass | **PASS** | Commands/results below |

## Commands and results

```text
# Official docs
curl -sS -D headers -o billy-api-docs.html https://www.billy.dk/api/
# HTTP/2 200; etag "wcw4x9hqvu3603"; content-length 147934;
# MD5 8b94b0135c91fd15fe54ea33e088a4be

# Unauth method gates (no token; JSON object body)
POST /v2/invoiceLateFees {}                         -> 401 AUTHENTICATION_REQUIRED
PUT  /v2/invoiceLateFees/nonexistent-probe-id {}    -> 401 AUTHENTICATION_REQUIRED
DELETE /v2/invoiceLateFees/nonexistent-probe-id     -> 405 METHOD_NOT_ALLOWED
DELETE /v2/invoiceLateFees?ids[]=nonexistent        -> 405 METHOD_NOT_ALLOWED

# Focused offline product + coverage + registry
uv run pytest tests/api/test_invoice_late_fee_writes.py \
  tests/unit/test_coverage_server.py \
  tests/coverage/test_coverage_inventory.py -q
# 33 passed in 5.38s

# Root non-live suite
uv run pytest -q -m "not live"
# 1094 passed in 11.03s

# Node test.sh (orchestrator no-op; exit 0)
bash .fractal/main.billy_complete.wave5n_product_review_grok/scripts/test.sh
# exit 0
```

## Coverage and fail-closed boundaries

| Metric | Value at `a3ad538` product surface |
| --- | --- |
| `api_*` tools | **254** |
| `implemented_rows` | **174** |
| `contract_tested_rows` | **174** |
| `live_tested_rows` | **0** |
| `vision_verified_rows` | **0** |
| `complete` | **false** |
| `api.invoiceLateFees.create` / `.update` | offline green (`implemented` + `contract_tested`) |
| `api.invoiceLateFees.bulk_save` / `.bulk_delete` | empty-tool red (`ambiguous_bulk`) |
| Singular delete inventory row | **absent** (correct; not greened) |
| All UI / vision rows for this resource | remain red / unqualified |

## Explicit non-accepts

- Live API qualification (`live_tested` remains false; `BILLY_API_TOKEN` still unavailable per status blocker).
- All UI parity and vision verification.
- Ambiguous bulk save/delete tools and greening.
- Singular delete tools (Supports omit; DELETE 405).
- Webhooks, generic HTTP escape hatches, headed browser controls.
- Overall project completeness (`complete` remains false).
- Any claim that unauth 401/405 probes are live testing.

## Protocol alignment

Shared design ticket protocol in
`docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md` (preview then
ticket-only execute; short-lived single-use tickets; no silent retries) matches
the product implementation through `WriteProtocolService` and
`ConfirmationStore`.

## Authorisation opened by this ACCEPT

With this offline product ACCEPT on root, parent orchestration may treat
Wave-5n singular invoiceLateFees create/update as product-gated offline and may
proceed to the next researched offline freeze/product slice (for example
Wave-5o invoiceReminders create-only research already noted on parent). That
later work requires its own freeze and independent reviews. This page does not
authorise live greening, bulk tools, or singular delete.

## Scratch evidence (not for git)

Node-local only under
`.fractal/main.billy_complete.wave5n_product_review_grok/tmp/`:

- `billy-api-docs.html` / headers
- unauth probe JSON snippets
- `focused-tests.log`, `offline-suite.log`

## Verdict line

**ACCEPT**
