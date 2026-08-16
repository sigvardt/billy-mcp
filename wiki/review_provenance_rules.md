---
name: review_provenance_rules
title: Review evidence provenance rules
desc: Shared evidence rules for independent-review identity, fallback reviews, and failed-agent drafts.
tags: [review, evidence, provenance, safety]
sources:
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
  - coverage/status.json
created: 2026-07-30T17:06:27Z
updated: 2026-07-30T17:06:27Z
---

# Review evidence provenance rules

## Identity and scope

- A review may name its reviewer only when that reviewer completed the review
  after authenticating and produced the recorded evidence.
- A Grok audit, current-document review, or vision verdict cannot be supplied
  by a different agent under a Grok label.
- A fallback review must name its actual reviewer and its limited purpose. It
  can improve repository confidence, but it does not satisfy a mandatory Grok,
  vision, live, or completeness gate.

## Failed-agent handling

- When a designated agent fails before edits because of authentication, quota,
  or rate limiting, rerun the complete bounded review with the other permitted
  route, as required by the routing policy.
- Before accepting a fallback result, verify the failure occurred before edits.
  Record the observed failure mode and retain the missing mandatory gate as a
  blocker where applicable.
- An uncommitted draft from a failed reviewer has no review provenance. Do not
  merge or cite it as an authoritative verdict; remove it when its ownership or
  authorship cannot be validated.

## Coverage boundary

Review pages do not green inventory rows. Only implementation plus the required
row-level test evidence can update generated coverage, and `complete: true`
still requires all live, UI, vision, and independent-review obligations in the
approved design.

A live test may write a vision record with `author=live_test` and
`reviewer_verdict=pending_review` only. It must not write `accept` or purge
frames. `qualifies_for_coverage_vision` is true only when
`author=independent_review`, `reviewer_verdict=accept`, and `purge_verified`.
Owner radio `C7DBE974`.
