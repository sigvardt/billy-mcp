# research64 — Wave-5o invoiceReminders freeze authoring package

## Finding

Official API HTML body is byte-identical to research63 (ETag `wcw4x9hqvu3603`,
MD5 `8b94b0135c91fd15fe54ea33e088a4be`, body 147934). Wave-5n product ACCEPT is
on root. Unauthenticated probes reconfirm invoiceReminders create-only
offline: POST 401; PUT/DELETE 405; bulk DELETE 405. Wave-5o freeze page is
still absent.

## Slice for Codex Power (now unblocked)

Author freeze wiki only:

- Path: `wiki/wave_fiveo_ticketed_writes_contract.md`
- Tools: `api_invoice_reminders_create_preview` / `_execute`
- Path `POST /invoiceReminders`; root `invoiceReminder` → `invoiceReminders`
- No update, delete, bulk, associations create/update, greening, or product

## Evidence

`.fractal/main.billy_complete/tmp/grok-research.md` (research64),
`tmp/write-probes-research64.json`, section extracts, Wave-5n product ACCEPT
MD5 `2ebc31c6223de5ce5e21d599f92b1a74`, Wave-5n freeze MD5
`93e6d266d1718fa517ff645b3ca213ce`.

## Post-Mortem

- Completed: reconfirmed docs and method gates after Wave-5n product ACCEPT;
  packaged exact freeze-page authoring requirements for create-only
  invoiceReminders.
- Review and verification: no coverage greening; no product code; no live or
  browser work.
- Cleanup: scratch HTML/probe files only under node tmp; no credentials or
  disposable records.
- Next unresolved slice: Codex Power freeze page, then independent freeze
  review, then two-tool product.
