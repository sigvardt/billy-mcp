# Research69 — Wave-5p organizations product handoff

## Goal

Reconfirm official Billy API contract for organizations create/update after
freeze independent ACCEPT, and package the exact offline product surface for
Codex Power.

## Findings

- Docs body MD5 `8b94b0135c91fd15fe54ea33e088a4be`, ETag `wcw4x9hqvu3603`, 147934 bytes (byte-identical to research68).
- Unauth: organizations POST/PUT 401; DELETE 405. No gate drift.
- Freeze ACCEPT on root; product module still absent.
- Four tools only: create/update preview+execute. Opaque `organization` map. Required root `organizations`.
- Create cleanup must use fail-closed non-delete wording when greening.

## Deliverable

`.fractal/main.billy_complete/tmp/grok-research.md` (research69 product handoff).

## Next (not this research step)

Codex Power implements `organization_writes.py` + tests + coverage to 177 offline green, then independent product review.

## Post-Mortem

- Completed: current official-doc evidence and unauthenticated 401/405 method gates were recorded in the owner-only research handoff; the separate research review accepted that handoff without treating it as product or live evidence.
- Deviation: the first product-leaf launch failed before agent work because its cost cap lacked an explicit priced model. The child seed was corrected to `gpt-5.6-terra` and the same Codex Power leaf was restarted; no fallback was authorized or used.
- Review: the independent reviewer found one stale historical freeze-status note in the product-ready research review. It now links to the separately accepted freeze verdict while preserving that review's original non-acceptance scope.
- Verification and cleanup: non-live repository checks had passed before the handoff; scratch research remains owner-only and is not tracked.
- Unresolved coverage slice: the active organizations create/update product leaf must deliver four ticketed API tools and contract tests before coverage can move from 175 to the expected 177 offline-green rows.
