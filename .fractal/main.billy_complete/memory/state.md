---
name: state
desc: Current node state, verified review decisions, and open qualification work.
tags: [billy, coverage, review]
sources:
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
  - https://www.billy.dk/api/
created: 2026-07-30T06:20:59Z
updated: 2026-07-30T09:43:18Z
---

# state

## Current state

- Wave-5c through Wave-5m write modules are merged into root; one shared confirmation store and write protocol.
- Root registry **254** `api_*` tools. Offline coverage **174** implemented + contract_tested. Live/vision **0**. `complete: false`.
- Wave-5m freeze ACCEPT and product ACCEPT offline remain valid.
- Wave-5n freeze page on root: `wiki/wave_fiven_ticketed_writes_contract.md` (MD5 `93e6d266d1718fa517ff645b3ca213ce`).
- Wave-5n freeze independent review: **ACCEPT**.
- Wave-5n product-ready research: **ACCEPT as research**.
- Wave-5n product-implementation research (research62): **ACCEPT as research** (review62).
- Wave-5n product source is merged on root: four invoice-late-fee create/update ticketed tools, their 19-test contract suite, corrected create cleanup wording, and generated coverage evidence. Root verification passed; independent product review is still required before acceptance.
- Wave-5o freeze-ready research (research63): **drafted** — singular `invoiceReminders` create only; freeze authoring gated on Wave-5n product ACCEPT.
- Official plain API contract stable (research63 HTML byte-identical to research62; ETag `wcw4x9hqvu3603`, MD5 `8b94b0135c91fd15fe54ea33e088a4be`).
- UI all red; bulk 92 empty-tool red; no live token; no UI credentials.

## Verification

- Docs research63: ETag `wcw4x9hqvu3603`, MD5 `8b94b0135c91fd15fe54ea33e088a4be`, body 147934; HTML equals research62.
- Unauth probes with `{}` body: invoiceReminders POST 401; PUT/DELETE 405; bulk DELETE 405. invoiceLateFees POST/PUT 401; singular/bulk DELETE 405. associations POST/PUT 405; DELETE 200 meta-only; DELETE without ids 400 `INVALID_DELETE_ID_ARRAY`.
- `invoice_late_fee_writes.py` is registered on root with create/update preview/execute tools; no delete or bulk tool was added.
- Root verification: clean-clone focused suite 33 passed; root non-live suite 1,094 passed; formatting, Ruff, Pyright, coverage, and repository-policy checks passed.
- Coverage honesty on root: 174/174/0/0; both invoiceLateFees bulk rows remain empty-tool red; complete false.
- Freeze MD5 match; freeze ACCEPT still valid.

## Review decisions (authoritative)

- Wave-5m freeze/product: **ACCEPT** offline.
- Wave-5n freeze: **ACCEPT**.
- Wave-5n product-ready research: **ACCEPT as research**.
- Wave-5n product-implementation research: **ACCEPT as research** (review62).
- Wave-5n product: **not accepted**; root integration is verified but awaits an independent product review.
- Wave-5o freeze-ready research: **drafted this pass** (not independently reviewed yet).
- Overall completeness: **FAIL**.

## Open coverage work

1. Obtain an independent product review of the verified root Wave-5n invoice-late-fee create/update merge.
3. After product ACCEPT: author Wave-5o freeze for invoiceReminders create-only (research63 package); then freeze review; then two-tool product.
4. Later: organizations create+update; users update-only; salesTaxReturns update-only (opaque/cautious); associations delete-only candidate.
5. Bulk 92, UI/auth/vision, live CUD still open.

## Evidence boundaries

- Plain contract is stable; HTML identity with research62 is the durable reconfirm.
- Research and root non-live verification are not product acceptance; live, UI, vision, bulk, and completeness remain red.
- Offline 401 opens freeze; 405 excludes methods offline.
- POST/PUT probes require a JSON object body (`{}` minimum) to reach the auth gate.

## References

- Research: `.fractal/main.billy_complete/tmp/grok-research.md` (research63)
- Prior product research: research62 + `wiki/wave_fiven_product_implementation_research_independent_review.md`
- Freeze ACCEPT: `wiki/wave_fiven_freeze_independent_review.md`
- Freeze page: `wiki/wave_fiven_ticketed_writes_contract.md`
- Probe rules: `wiki/offline_write_probe_rules.md`
