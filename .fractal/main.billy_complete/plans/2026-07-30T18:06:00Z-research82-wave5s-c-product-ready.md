# Research82 — Wave-5s-C product-ready email + delivery

## Goal

Produce a cited product-ready handoff for Codex Power on ticketed
`api_invoices_send_email_*` and `api_invoice_deliveries_create_*` without
greening coverage, while Wave-5s-B product remains the active implementation
child.

## Done

- Re-fetched https://www.billy.dk/api/ — MD5 `8b94b0135c91fd15fe54ea33e088a4be`,
  ETag `"wcw4x9hqvu3603"`, byte-identical to research81.
- Unauth probes on locked base reconfirmed email/delivery method matrix and
  residual 405 false friends.
- Mapped codebase gaps: generic WriteProtocolService POST target=None, nested
  email path, provisional singular/plural response roots; prefer custom
  ConfirmationStore services (upload-special pattern).
- Wrote scratch `tmp/grok-research.md` (research82) and wiki
  `wave_fivesc_invoice_email_delivery_product_ready_research.md`.
- Updated residual specials wiki pointer and node memory.
- Acknowledged Wave-5s-B child radio on StrictBool/CR-LF fixes; 5s-C product
  remains gated on 5s-B merge + Grok product IR.

## Non-claims

No coverage greening, no product ACCEPT, no live/UI/vision work, no disposable
records, no headed browser.

## Post-Mortem

Research82 deepens the accepted Wave-5s-C freeze into an implementable offline
recipe. Official docs did not drift. The decisive product-ready finding is that
the generic singular write helper cannot bind nested email `target=invoiceId`
or map provisional special response envelopes safely, so Codex Power must ship
custom special services after Wave-5s-B clears its merge gates.

Independent Grok review accepted the handoff as research only. It reproduced
the official fingerprint and method gates, retained all response-shape and
side-effect boundaries, and found no defect requiring a change to the handoff.
