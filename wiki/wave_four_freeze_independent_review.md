---
name: wave_four_freeze_independent_review
desc: Independent Grok review of the Wave-4 read contract freeze and root offline baseline.
tags: [billy, api, read_only, review, wave4]
sources:
  - https://www.billy.dk/api/
  - wiki/wave_four_remaining_clear_reads_contract.md
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
  - coverage/api_v2_manifest.yaml
  - coverage/status.json
  - src/billy_mcp/server.py
created: 2026-07-29T12:12:38Z
updated: 2026-07-29T12:12:38Z
---

# wave_four_freeze_independent_review

## Verdict

**Accept the root offline baseline and the Wave-4 contract freeze; reject any
product-completeness claim.** The review found no new code defect on root and
no reason to advance coverage state. The in-flight Wave-4 modules were not part
of this root review and remain unimplemented until their tested deliveries are
merged and registered.

## Verified contract and inventory facts

- The official API documentation fingerprint remains ETag `hsisik4g9p3603`,
  MD5 `c2efda0ee4cf9cf200e14910c5fc6996`, and 147934 bytes. The 46 documented
  resources reconcile to 207 clear operations, 92 ambiguous bulk operations,
  and 6 specials (305 API rows total); no webhook row is documented.
- Root has 44 real offline `api_*` tools and two `coverage_*` tools. The 44
  corresponding API rows are implemented and contract-tested, while every live
  and vision flag remains false and `coverage/status.json` remains fail-closed.
- The Wave-4 freeze correctly bounds 50 remaining clear get/list operations.
  `countryId` is required only for cities, states, and zipcodes list inputs,
  based on live unauthenticated validation evidence. It is not an official
  filter-table claim and it does not make those rows live-tested.
- Wave-3's formerly reported list-envelope issues are closed: the relevant
  FastMCP tools have flat inputs and files/attachments preserve
  `meta.paging`.
- The locked API base URL, browser egress allowlist, approval-ticket foundation,
  and logged-value redaction safeguards pass their available offline checks.

## Explicit non-claims and blockers

- No dedicated non-production API token is configured. Live API qualification,
  authenticated UI discovery, and vision review remain blocked and red.
- No `auth_*` product tools, UI tools, or write preview/execute tools are
  registered yet. The ticket store is a tested foundation, not write-tool
  completion.
- The 92 bulk operation bodies remain ambiguous, no file-upload write path is
  implemented, and no coverage row may be marked complete from this review.

## Required follow-up

1. Merge and register only passing Wave-4 leaf deliveries, then add their
   specific test evidence and regenerate coverage without advancing live or UI
   state.
2. Re-run independent Grok review after the Wave-4 root integration. Re-research
   official documentation only if its fingerprint changes or a documented bulk
   request body becomes available.
3. Obtain dedicated non-production API and browser credentials before attempting
   live, UI, bulk, or write qualification.
