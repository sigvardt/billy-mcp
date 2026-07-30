---
name: state
desc: Verified terminal state of the scoped Wave-5j offline bank-line product leaf.
created: 2026-07-30T02:42:04Z
updated: 2026-07-30T02:42:04Z
---
# state

The scoped product implements the nine accepted singular CUD inventory rows
for `bankLineMatches`, `bankLines`, and `bankLineSubjectAssociations` as
eighteen strict typed preview/execute tools. The root server registers them
through its existing shared `WriteProtocolService` and `ConfirmationStore`.

The implementation preserves the accepted contract:

- fixed client-relative collection paths, singular request roots, partial
  update id equality, and bodyless deletes;
- opaque inner JSON payloads with strict flat outer inputs;
- exact, non-empty server-owned executor binding with single-use, no-retry
  execution;
- optional related roots only for match operations and only when returned;
  line and association operations declare no additional roots; and
- typed error paths with expiry, tamper, replay, organisation, target, payload,
  expected-effect, and cross-executor mismatch evidence.

Verification passes for 71 focused tests and 1,020 non-live/non-vision tests,
the repository formatter, Ruff, Pyright, coverage false-completeness checks,
and repository policy. The live server exposes 238 unique `api_*` tools.
Generated coverage reports 166 implemented and contract-tested offline rows,
zero live-tested and vision-verified rows, and `complete: false`.

The coverage generator contains exactly nine new source-controlled evidence
entries, each referring only to the two real bank-line suites and the root
registry assertion. No bulk, live/UI/vision, `bankPayments`,
`balanceModifiers`, credential, or browser artifact is part of this leaf.
This leaf makes no independent product-acceptance or overall-completion claim.
