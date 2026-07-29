---
name: phase_zero_contract
desc: Frozen Phase 0 implementation boundaries and ownership for Billy MCP.
sources:
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
  - https://www.billy.dk/api/
created: 2026-07-29T09:04:46Z
updated: 2026-07-29T09:04:46Z
---

# phase_zero_contract

The current official API source snapshot contains 207 clear resource operations,
92 ambiguous bulk mentions, and six documented special routes. Every coverage
row remains red until code, contract tests, and dedicated non-production live
tests exist. The ambiguous bulk contract and singular `GET /v2/organization`
sample are not implementable from the public documentation alone.

Phase 0 owns the manifest schemas, generated coverage report, safety foundation,
and typed `coverage_*` tools only. API and UI business tools are not registered
until their concrete workflows are implemented. The API host is fixed to
`https://api.billysbilling.com/v2`; the browser starts headless only and is
deny-by-default outside its reviewed allowlist.

The browser runtime loads `coverage/browser_egress.yaml` at its launch boundary,
before Playwright is called. It does not accept a prebuilt allowlist policy:
normal runtime construction uses the reviewed manifest, while tests may provide
a separate fixture manifest. Missing, malformed, or deny-only manifests abort
the start before a context exists. The persistent profile is derived from the
account running the server, not a hard-coded developer home directory. If route
installation itself fails, the newly launched context and Playwright owner are
closed before the failure is returned.

`BILLY_TEST_MODE=full` is a qualification gate, not a best-effort test mode. It
must fail closed until both the generated `coverage/status.json` and its checker
exist, and then require the checker to enforce row-level completeness. A regular
offline test run can validate only the implemented slice; it is never evidence
that the complete product is qualified.

The coverage status is generated evidence, never an operator-maintained success
switch. A complete report requires every applicable API row to have discovery,
implementation, contract, and dedicated non-production live evidence; every
applicable UI row also requires a headless DOM assertion, an independent
read-back, and a non-sensitive vision-review record confirming purge of raw
frames. Ambiguous bulk documentation and inaccessible authenticated screens
remain red. A full test invocation must reject this state rather than treating a
red manifest as a successful product qualification.

The generated phase labels describe the current evidence slice, never a
qualification shortcut. `phase_1_offline_api_reads` records that a bounded API
read slice has implementation and contract-test evidence; it does not assert
live testing, UI parity, vision verification, or `complete: true`. Future phase
changes must remain generator-owned and be backed by the corresponding
row-level evidence.

The first bounded UI observation is documented in
`wiki/billy_ui_discovery_brief.md`: the allowlisted, forced-headless browser
reached only the unauthenticated login surface. It is evidence about that
surface and its purge procedure, not API-to-UI parity, a `not_applicable`
classification, or any green UI row.

Root owns package metadata, cross-cutting models, CI, scripts, wiki, and
integration wiring. The coverage-inventory child owns manifest data and its
tests. The shared-foundation child owns concrete modules below `src/billy_mcp`
except root-owned `models.py`, plus isolated unit tests. Cross-cutting contract
changes are escalated to root before implementation.
