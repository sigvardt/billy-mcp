# research63 — Wave-5o invoiceReminders freeze-ready

## Finding

Official API HTML body is byte-identical to research62 (ETag `wcw4x9hqvu3603`,
MD5 `8b94b0135c91fd15fe54ea33e088a4be`). Wave-5n product is advanced on child
`wave5n_invoice_late_fee_product` (174 offline there) but not on root (still
172). Next freeze after Wave-5n product ACCEPT: singular `invoiceReminders`
create only.

## Probe summary

- invoiceReminders POST 401; PUT/DELETE 405; bulk DELETE 405
- invoiceReminderAssociations POST/PUT 405; DELETE 200 meta-only
- invoiceLateFees POST/PUT 401; DELETE 405 (Wave-5n still valid)

## Slice for Codex Power (after Wave-5n product ACCEPT)

Author freeze wiki only for two tools:

- `api_invoice_reminders_create_preview` / `_execute`
- Path `POST /invoiceReminders`; root `invoiceReminder` → `invoiceReminders`
- No update, delete, bulk, associations create/update, greening, or product

## Evidence

`.fractal/main.billy_complete/tmp/grok-research.md` (research63),
`tmp/write-probes-research63.json`, section extracts, freeze MD5
`93e6d266d1718fa517ff645b3ca213ce` still valid for Wave-5n.
