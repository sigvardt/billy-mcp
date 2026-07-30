# Research87 — Wave-5s-C product in-flight reconfirm

## Objective

Reconfirm the official Billy API v2 contract for the active Wave-5s-C product
leaf without greening coverage and without opening residual freezes.

## Findings

- Official docs body MD5 `8b94b0135c91fd15fe54ea33e088a4be` is byte-identical
  to research81–research86 (ETag `"wcw4x9hqvu3603"`, 147934 bytes).
- Email and delivery method gates still open offline on POST only; refined
  probe: empty-body PUT/PATCH on emails returns 400 before 405; body-present
  PUT returns 405 POST-only.
- Residual clear 29 remains offline-blocked (405 false friends, transactions
  readonly property table, bankPayments delete 405, reminder-association
  missing-id 200 is not cleanup proof).
- Product leaf `wave5sc_email_delivery_product` is active with WIP matching
  freeze paths; root specials still red (182/182/0/0).

## Codex Power slice

Finish the active leaf only: four ticketed tools, two special rows, offline
implemented + contract_tested, live false. Custom ConfirmationStore services.
No residual/bulk/UI work. After merge: Grok product independent review.

## Artifacts

- `.fractal/main.billy_complete/tmp/grok-research.md`
- `wiki/wave_fivesc_research87_product_in_flight_reconfirm.md`
- scratch: `tmp/write-probes-research87.json`, `tmp/billy-api-docs-research87.html`

## Post-Mortem

- The cited reconfirmation remained accurate through the product merge: the
  official document fingerprint and the documented email/delivery wire did not
  change.
- The bounded child product was merged at `0efceae`; Review87 subsequently
  accepted it offline. Research itself did not green coverage; the product's
  real contract tests moved only the two special rows to implemented and
  contract-tested.
- Residual clear 29, bulk 92, UI 339, live qualification, and completeness
  remain red. No residual or interface work was inferred from this research.
