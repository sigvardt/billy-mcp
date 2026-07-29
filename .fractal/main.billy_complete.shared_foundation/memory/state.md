---
name: state
desc: Current shared-foundation delivery state and inventory integration contract.
created: 2026-07-29T09:24:10Z
updated: 2026-07-29T09:24:10Z
---

# state

The shared foundation supplies safe configuration and credential resolution,
structured redaction, stable upstream errors, opaque confirmation bindings, a
locked HTTP client, headless-only browser runtime, typed coverage loading, and
a FastMCP shell that registers only `coverage_status` and `coverage_report`.

Coverage integration reads `coverage/api_v2_manifest.yaml` under `operations`,
`coverage/ui_workflows_manifest.yaml` under `workflows`,
`coverage/browser_egress.yaml` under `hosts`, and `coverage/status.json`.
Absent artifacts return typed `NOT_FOUND`; red rows cannot produce a complete
report.
