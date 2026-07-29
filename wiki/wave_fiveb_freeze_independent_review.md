---
name: wave_fiveb_freeze_independent_review
desc: Independent Grok ACCEPT of the Wave-5b offline ticketed-write contract freeze; product not yet shipped.
tags: [billy, review, writes, coverage]
sources:
  - https://www.billy.dk/api/
  - wiki/wave_fiveb_ticketed_writes_contract.md
  - coverage/status.json
created: 2026-07-29T16:22:40Z
updated: 2026-07-29T16:22:40Z
---

# wave_fiveb_freeze_independent_review

## Verdict

| Claim | Result |
| --- | --- |
| Wave-5b cited contract freeze | **ACCEPT** |
| Wave-5b product implementation | **not on root** (separate review required after merge) |
| Wave-5a offline product (recheck) | **ACCEPT** |
| Overall product completeness | **FAIL** (expected) |
| Coverage honesty / fail-closed bulk-UI-live | **PASS** |

Root HEAD at review: `8144448`. Official docs fingerprint unchanged: ETag
`hsisik4g9p3603`, MD5 `c2efda0ee4cf9cf200e14910c5fc6996`.

## What was accepted

`wiki/wave_fiveb_ticketed_writes_contract.md` freezes exactly nine clear
singular CUD inventory rows (account groups, accounts, daybook balance
accounts) for offline ticketed preview/execute tools. Paths, singular roots,
shared protocol reuse, ticket binding, and exclusions (bulk, account natures,
postings, specials, UI, live green) match current official documentation and
the maintained inventory tool names.

## Follow-up

The review's optional wording finding was corrected in
`scripts/generate_coverage_report.py`: the generated report now calls the
current phase offline API read-and-write coverage. Regeneration left the
manifest counts and `complete: false` unchanged; this is a prose-alignment fix,
not a qualification change.

## What remains red

- All nine Wave-5b rows: discovered only; not implemented or contract-tested.
- Runtime still 124 `api_*` tools (no Wave-5b write tools registered).
- Live 0; UI 0 vision; bulk 92 empty-tool; four specials red; 100 clear CUD red.
- Unauthenticated DELETE 200 is not cleanup proof. Unauthenticated natures and
  postings CUD return 405 despite some documentation Supports flags.

## Next product gate

After Codex Power leaves land and the root registers the eighteen tools and
regenerates coverage to 118 offline rows with 142 `api_*` tools, run a separate
independent product review before expanding scope.

Full scratch report: node `tmp/grok-review.md` (not durable; this wiki page is
the shared summary).
