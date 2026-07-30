---
name: state
desc: Current delivered state of the offline invoiceLogs product leaf.
created: 2026-07-30T16:43:41Z
updated: 2026-07-30T16:43:41Z
---

# state

The leaf owns a single offline API surface: `api_invoice_logs_list` for the
documented `GET /invoiceLogs` query. Its strict input requires `invoiceId` and
`organizationId`, freezes `eventTime`/`DESC` sorting, and excludes paging and
all other controls. The response maps the exact `invoiceLogs` array to opaque,
extra-preserving entries and returns typed `BILLY_ERROR` values for malformed
roots or elements while preserving typed authentication errors.

The real server registers 265 API tools. Generated coverage marks only
`api.special.invoice_logs` implemented and contract-tested, producing 180
offline rows with live and vision at zero and `complete: false`.
