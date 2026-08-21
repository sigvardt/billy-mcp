---
name: wave_fivesc_invoice_email_delivery_research_independent_review
title: Wave-5s-C email and delivery research independent review ACCEPT
desc: Authoritative root Grok acceptance of the cited offline freeze for ticketed invoice email and invoiceDeliveries specials; product and completeness remain open.
tags: [billy, api, specials, invoices, email, e-invoice, delivery, research, review, offline]
sources:
  - https://www.billy.dk/api/
  - https://api.billysbilling.com/v2
  - wiki/wave_fivesc_invoice_email_delivery_research.md
  - wiki/wave_fives_residual_specials_research.md
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
  - coverage/api_v2_manifest.yaml
  - coverage/status.json
  - "parent scratch: .fractal/main.billy_complete/tmp/grok-review.md"
created: 2026-07-30T17:52:00Z
updated: 2026-07-30T17:52:00Z
---

# Wave-5s-C email and delivery research independent review ACCEPT

## Verdict

| Claim | Result |
| --- | --- |
| Wave-5s-C freeze research handoff (research81) | **ACCEPT as research** |
| Official documentation versus maintained inventory | **PASS** (provisional response_fields noted) |
| Unauth method gates versus research matrix | **PASS** |
| Coverage honesty before product | **PASS** |
| Wave-5s-C product implementation | **not accepted** — tools absent; separate product IR after merge |
| Live, UI, vision, bulk, and completeness | **not claimed / fail-closed** |

The authoritative root `INDEPENDENT-REVIEW` Grok step accepted the freeze
research at scratch `.fractal/main.billy_complete/tmp/grok-research.md`
(research81) against freeze page [[wave_fivesc_invoice_email_delivery_research]],
residual ranking [[wave_fives_residual_specials_research]], inventory specials,
and root baseline **`975ed6c`** (product tools still absent). Full cited
findings live outside the public repository at
`.fractal/main.billy_complete/tmp/grok-review.md`.

## Exact reviewed scope

This ACCEPT covers only the cited offline freeze that opens Codex Power product
work **after** Wave-5s-B product merge and product IR:

| Inventory id | Preview tool | Execute tool | HTTP |
| --- | --- | --- | --- |
| `api.special.invoice_email` | `api_invoices_send_email_preview` | `api_invoices_send_email_execute` | `POST /invoices/:invoiceId/emails` |
| `api.special.invoice_delivery` | `api_invoice_deliveries_create_preview` | `api_invoice_deliveries_create_execute` | `POST /invoiceDeliveries` |

Independent re-fetch of [official Billy API documentation](https://www.billy.dk/api/)
returned HTTP 200, ETag `"wcw4x9hqvu3603"`, 147934 bytes, MD5
`8b94b0135c91fd15fe54ea33e088a4be` — matching research81. Unauth probes on
`https://api.billysbilling.com/v2` reconfirmed email POST **401** / empty **400** /
GET-PUT-DELETE **405** POST-only; delivery POST **401**; nested under invoices
**404** `UNKNOWN_RESOURCE`; singular DELETE **405**. Delivery get/list/update
must not be productised from method-open noise alone.

## Provisional inventory response fields

Official samples show **no** success bodies for either special. Inventory lists
email `changed_records[]` and delivery `invoiceDelivery`. Research correctly
flags these as provisional. Product must fail closed offline and revise only
after live proof. This is not a freeze REJECT.

## Non-claims

- Not product ACCEPT.
- Not live, UI, vision, bulk, or completeness.
- No coverage greening from this review.
- Wave-5s-B files upload product remains a separate gate (child active; tools
  still absent on root at review time).

## Coverage honesty

Root offline baseline remains 180 implemented + contract_tested, live 0, vision
0, `complete: false`. Both Wave-5s-C special rows stay red until product
evidence lands.
