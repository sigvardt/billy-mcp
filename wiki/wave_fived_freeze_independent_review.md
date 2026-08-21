---
name: wave_fived_freeze_independent_review
title: Wave-5d contract freeze independent review ACCEPT
desc: Independent Grok acceptance of the cited offline contract for invoice and invoice-line singular ticketed writes.
tags: [billy, api, writes, review, coverage]
sources:
  - https://www.billy.dk/api/
  - wiki/wave_fived_ticketed_writes_contract.md
  - wiki/wave_fivec_product_independent_review.md
  - coverage/api_v2_manifest.yaml
  - coverage/status.json
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
created: 2026-07-29T18:52:00Z
updated: 2026-07-29T18:52:00Z
---

# Wave-5d contract freeze independent review ACCEPT

## Verdict

| Claim | Result |
| --- | --- |
| Wave-5d cited contract freeze | **ACCEPT** |
| Official documentation versus maintained inventory | **PASS** |
| Freeze versus exact six-row tool/path/root map | **PASS** |
| Coverage honesty before product integration | **PASS** |
| Wave-5d product implementation | **not accepted** — separate review required after root integration |
| Live, UI, vision, bulk, and completeness | **not claimed / fail-closed** |

The independent Grok review checked root tip `5c376de`. Official documentation
matched inventory freeze fingerprint ETag `hsisik4g9p3603`, MD5
`c2efda0ee4cf9cf200e14910c5fc6996`, body 147934 bytes. The freeze page
`wiki/wave_fived_ticketed_writes_contract.md` matches the documented Supports
create/update/delete surface for `/v2/invoices` and `/v2/invoiceLines`, the
pre-seeded inventory preview tool names, singular request roots, bodyless
deletes, locked API base, shared ticket protocol with required
`execute_tool_name`, and line multi-root declaration
`additional_plural_roots=("invoices",)`.

## Accepted frozen scope

Offline contract only for singular create, update, and delete of `invoices` and
`invoiceLines` (six inventory rows, twelve tools after product lands):

- exact preview/execute name pairs and POST/PUT/DELETE client paths;
- singular roots `invoice` / `invoiceLine`; primary response roots
  `invoices` / `invoiceLines`;
- optional parent `invoices` root on line writes when Billy returns it;
- opaque payloads, no invented embedded-line schema offline;
- exclusions: bills, bulk, invoice email/delivery/logs specials, files,
  attachments, reminder/late-fee family, UI, live qualification.

At freeze time all six rows remain red (`implemented` and `contract_tested`
false). Coverage stays at 124 offline implemented/contract-tested rows, live 0,
`complete: false`. Root has no invoice write modules yet.

## Required product gate

This is not a product acceptance. After root registration of both write
modules, independent Grok product review must verify 166 `api_*` tools, 130
offline implemented/contract-tested rows, six evidence mappings, multi-root line
mapping, and same- and cross-module executor-mismatch regressions. Reject any
live, UI, vision, bulk, or completeness claim without its own evidence.

No browser was launched, no credential or customer data was used, and no raw
browser evidence was retained. The full temporary reviewer note remains outside
the public repository path at
`.fractal/main.billy_complete/tmp/grok-review.md`; this page is the durable,
non-sensitive summary.
