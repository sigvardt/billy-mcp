---
name: wave_fiven_product_implementation_research_independent_review
title: Wave-5n invoice-late-fee product-implementation research independent review
desc: Independent Grok ACCEPT as research for the Wave-5n product-implementation gate after freeze ACCEPT; product remains a separate Codex Power leaf.
tags: [billy, api, invoice-late-fees, writes, review, research]
sources:
  - https://www.billy.dk/api/
  - wiki/wave_fiven_ticketed_writes_contract.md
  - wiki/wave_fiven_freeze_independent_review.md
  - wiki/offline_write_probe_rules.md
  - coverage/api_v2_manifest.yaml
  - coverage/status.json
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
created: 2026-07-30T09:34:00Z
updated: 2026-07-30T09:34:00Z
---

# Wave-5n invoice-late-fee product-implementation research independent review

## Verdict

**ACCEPT as research** for the Wave-5n offline product-implementation package
(research62). Freeze independent review **ACCEPT** remains valid. Product
implementation is not accepted here.

| Claim | Result |
| --- | --- |
| Research62 product-implementation package | **ACCEPT as research** |
| Freeze page + freeze ACCEPT vs official contract | **PASS** |
| Unauth POST/PUT 401 (JSON body) and DELETE 405 (singular + bulk) | **PASS** |
| Coverage honesty before product merge | **PASS** (172 offline; create/update still red) |
| Wave-5n product on root | **Not present** — separate Codex Power leaf |
| Live, UI, vision, bulk, completeness | **Not claimed / fail-closed** |

This page is not product acceptance.

## Reviewed baseline

| Item | Value |
| --- | --- |
| Root commit | `2cf3e6a` |
| Freeze page | [[wave_fiven_ticketed_writes_contract]] (file MD5 `93e6d266d1718fa517ff645b3ca213ce`) |
| Freeze ACCEPT | [[wave_fiven_freeze_independent_review]] |
| Research brief | `.fractal/main.billy_complete/tmp/grok-research.md` (research62) |
| Full review record | `.fractal/main.billy_complete/tmp/grok-review.md` (review62) |

## Official and probe evidence (this review)

- Docs: https://www.billy.dk/api/ — ETag `wcw4x9hqvu3603`, body MD5
  `8b94b0135c91fd15fe54ea33e088a4be`, 147934 bytes. Plain contract matches
  research62. Inventory pin may differ on access fingerprint only.
- `/v2/invoiceLateFees` Supports: get by id, list, create, update, bulk save,
  bulk delete. Singular delete omitted.
- Unauth base `https://api.billysbilling.com/v2` with `{}` body: POST/PUT → 401
  `AUTHENTICATION_REQUIRED`; singular DELETE and bulk DELETE with `ids[]` → 405
  `METHOD_NOT_ALLOWED`. No token. Not live qualification.

## Exact product surface still authorised (not implemented on root)

| Inventory id | Preview | Execute | Method / path | Roots |
| --- | --- | --- | --- | --- |
| `api.invoiceLateFees.create` | `api_invoice_late_fees_create_preview` | `api_invoice_late_fees_create_execute` | `POST /invoiceLateFees` | `invoiceLateFee` / `invoiceLateFees` |
| `api.invoiceLateFees.update` | `api_invoice_late_fees_update_preview` | `api_invoice_late_fees_update_execute` | `PUT /invoiceLateFees/:id` | `invoiceLateFee` / `invoiceLateFees` |

Bulk rows stay empty-tool red. No singular delete tools. No webhooks.

## Root honesty

- `coverage/status.json`: implemented 172, contract_tested 172, live 0, vision 0,
  `complete: false`. Independent recount matches. Zero false greens.
- No `src/billy_mcp/api/invoice_late_fee_writes.py` on root.
- Registry still expects 250 `api_*` tools until product lands (+4 → 254).
- Create inventory cleanup still says `delete dedicated test resource`; product
  greening must rewrite it to exclude singular DELETE.

## Product gate

Codex Power product leaf may implement and contract-test the four tools. Target
after honest greening: 174 offline implemented/contract_tested, 254 `api_*`
tools, live and vision still 0, `complete: false`. Independent **product**
review is a later step after merge.

## Exclusions

Not product ACCEPT, live qualification, UI/vision acceptance, bulk resolution,
singular delete authorisation, coverage greening, or overall completeness.

## Verdict line

**ACCEPT as research**
