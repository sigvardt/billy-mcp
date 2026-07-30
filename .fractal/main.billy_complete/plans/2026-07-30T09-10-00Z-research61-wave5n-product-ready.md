# Research61 — Wave-5n product-ready handoff

## Verdict

Official plain contract unchanged. Freeze page is on root. Product implementation stays gated on freeze independent review ACCEPT. Product-ready package covers singular invoiceLateFees create+update only (four tools).

## Evidence

- Primary: https://www.billy.dk/api/ (ETag wcw4x9hqvu3603, MD5 8b94b0135c91fd15fe54ea33e088a4be, 147934 bytes; access 2026-07-30T09:05:54Z)
- Unauth probes with `{}` body (2026-07-30T09:06:27Z): POST/PUT 401; singular DELETE and bulk DELETE 405
- Freeze page: wiki/wave_fiven_ticketed_writes_contract.md (MD5 93e6d266d1718fa517ff645b3ca213ce)
- Full brief: .fractal/main.billy_complete/tmp/grok-research.md

## Bounded Codex slice (after freeze ACCEPT)

- Module: src/billy_mcp/api/invoice_late_fee_writes.py
- Tests: tests/api/test_invoice_late_fee_writes.py
- Register shared WriteProtocolService
- Green only create+update offline rows after real tests; fix create cleanup wording (no singular delete)
- Target: 254 api_* tools; 174 offline implemented/contract_tested; complete false; live/vision 0

## Out of scope

delete, bulk, UI, live, invoiceReminders product, webhooks, greening before freeze ACCEPT

## No coverage greens in research
