---
name: state
desc: Current node state, verified review decisions, and open qualification work.
tags: [billy, coverage, review]
sources:
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
  - https://www.billy.dk/api/
created: 2026-07-29T12:12:38Z
updated: 2026-07-29T13:41:04Z
---

# state

## Current state

- Root product surface: **94** real `api_*` tools + 2 `coverage_*` (clear get/list offline complete).
- Clear resource get/list offline: **92/92** implemented and contract_tested.
- Specials offline-green: `api.special.user_get`, `api.special.user_organizations` only (4 specials remain red).
- Coverage: implemented 94, contract_tested 94, live_tested 0, vision 0, `complete: false`.
- Official docs fingerprint unchanged (etag `hsisik4g9p3603`, MD5 `c2efda0ee4cf9cf200e14910c5fc6996`).
- UI discovery still unauthenticated login only; all 339 UI rows red.
- `BILLY_API_TOKEN` unavailable; no live qualification claimed.
- Wave-5 **contract freeze** committed (`wiki/wave_five_ticketed_writes_contract.md` @ `9624d26`). The shared unregistered write protocol is merged at `1e25dc2`; no write tools or coverage evidence are registered yet.
- The `wave5_write_foundation` child is intentionally closed after the parent Grok audit accepted its two-file product diff. Child-local Grok authentication failed, but the subsequent parent Grok audit supplied the required independent review.
- Current verification: repository lint passed, the root non-live suite passed **510** tests, and the protocol-plus-confirmation focused suite passed **32** tests.

## Evidence boundaries

- Official API: https://www.billy.dk/api/ fingerprint above.
- 46 resources, 207 clear ops, 92 bulk ambiguous, 6 specials; 0 webhooks.
- Write probes (unauth): POST/PUT → 401; DELETE → empty 200 (not cleanup proof). Bulk unproven.
- Remaining red API work: 115 clear writes, 92 bulk, four specials.

## Review decisions

- Wave-4 offline integration: **ACCEPT** slice; **FAIL** product completeness.
- Wave-5 contract freeze @ `9624d26`: **ACCEPT** freeze honesty and alignment; **no** write greening; product completeness still **FAIL**.
- Parent Grok IR @ root baseline `1f259c2`: **ACCEPT** fail-closed baseline; product completeness **FAIL**. Docs fingerprint still matches inventory.
- Foundation leaf `wave5_write_foundation` product @ `2f6736d`: **ACCEPT for merge** and integrated at `1e25dc2` (`write_protocol.py` + unit tests). Advisories: map all changed plural roots before embed creates; prune the prepared-ticket map after consume.
- No REQUIRED rewrite of Wave-4 read modules or freeze wiki for false-green.
- Before greening any Wave-5a row: both preview+execute, preview no mutation, ticket matrix, exact body capture, evidence map; live stays false.

## Next implementation slice (for Codex Power)

1. Spawn/merge catalog/contact/contact_person/daybook write leaves (30 tools) using opaque singular-root bodies and `…Id` belongs-to wire form. Product embeds must preserve all documented changed plural roots.
2. Root wires one process-volatile `ConfirmationStore`, registers all 30 tools, and adds server registration coverage.
3. Root register → 124 `api_*` + 2 coverage; offline-green only 15 write inventory rows.
4. Independent Grok product review of integrated Wave-5a.
5. Later: live token (resolve contact `paymentTermsDays` requiredness, DELETE `meta.deletedRecords`, bulk), specials, auth, UI/vision.

## Research notes (durable)

- Official docs fingerprint still `hsisik4g9p3603` / `c2efda0ee4cf9cf200e14910c5fc6996`.
- Unauth DELETE still returns empty 200 success (products and daybooks re-probed); not cleanup proof.
- Contact property table marks `paymentTermsDays` required; live probe needed before strict offline validation.
- Product create sample embeds `prices[]` with `unitPrice` + `currencyId` (clear embed, not bulk).

## References

- Research: `.fractal/main.billy_complete/tmp/grok-research.md`
- Review: `.fractal/main.billy_complete/tmp/grok-review.md`
- Wiki: `wiki/wave_five_ticketed_writes_contract.md`, `wiki/wave_five_write_protocol_independent_review.md`, `wiki/wave_four_root_integration_independent_review.md`
