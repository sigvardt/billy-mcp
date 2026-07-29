---
name: wave_five_write_protocol_independent_review
desc: Independent Grok audit accepting the scoped Wave-5 shared ticketed-write protocol for root merge.
tags: [billy, api, writes, review, confirmation]
sources:
  - https://www.billy.dk/api/
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
  - wiki/wave_five_ticketed_writes_contract.md
  - coverage/api_v2_manifest.yaml
  - coverage/status.json
created: 2026-07-29T13:39:00Z
updated: 2026-07-29T13:39:00Z
---

# wave_five_write_protocol_independent_review

## Verdict

Grok independently accepted the scoped Wave-5 shared ticketed-write protocol
for root merge. The accepted delivery is the two-file foundation from
`main.billy_complete.wave5_write_foundation` commit `2f6736d`, integrated by
the labelled root merge `1e25dc2`. This is not a product-completeness verdict:
the server still exposes only the 94 read `api_*` tools and two coverage tools,
and every write, live, interface, vision, bulk, special-route, and completion
claim remains red.

The child-local review could not authenticate to Grok after the product edit.
The parent Grok audit reviewed the committed product diff afterwards and is the
required independent review; no implementation agent was switched mid-edit.

## Evidence checked

- Official documentation matched the inventory fingerprint: ETag
  `hsisik4g9p3603`, MD5 `c2efda0ee4cf9cf200e14910c5fc6996`.
- The product diff contains only
  `src/billy_mcp/api/write_protocol.py` and
  `tests/unit/test_write_protocol.py`; it does not register tools or alter
  coverage, client, browser, auth, UI, bulk, or special routes.
- The audit verified mutation-free preview, ticket-only execution input,
  relative locked-client paths, escaped identifiers, exact write bodies,
  no write retry, typed 401/404 mapping, ticket mismatch/replay/expiry and
  concurrent-consume coverage, redaction, and optional rather than fabricated
  `meta.deletedRecords`.
- Focused protocol and confirmation tests passed (32 tests), and the root
  non-live suite passed after integration (510 tests). The coverage status
  remains `complete: false` with no write evidence greened.

## Required boundaries

- Resource leaves must register paired preview and ticket-only execute tools
  against one process-volatile `ConfirmationStore`; their inventory rows remain
  red until both tools and focused contract evidence exist.
- Never infer a bulk contract, authenticated cleanup, live result, or a
  `deletedRecords` array from unauthenticated delete responses.
- Keep the current clear-write property ambiguities (including contact
  `paymentTermsDays`) out of strict offline validation until non-production
  observation resolves them.

## Advisories

- Before any product embed create is exposed, preserve every documented changed
  plural root instead of returning only the primary resource root.
- Prune consumed or expired prepared-ticket records to bound process memory.

## Sources

1. Official API documentation: https://www.billy.dk/api/.
2. Frozen Wave-5 contract: [[wave_five_ticketed_writes_contract]].
3. Approved design: `docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md`.
4. Machine inventory and status: `coverage/api_v2_manifest.yaml` and
   `coverage/status.json`.
