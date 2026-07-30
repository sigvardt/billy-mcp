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
