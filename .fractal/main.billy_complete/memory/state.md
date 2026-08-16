---
name: state
desc: Current node state for the Billy MCP complete run.
tags: [billy, coverage, ui_writes]
sources:
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
  - https://www.billy.dk/api/
created: 2026-08-16T14:29:47Z
updated: 2026-08-16T14:29:47Z
---

## Now

Owner `96908DC6` is binding. Interface writes first. API live stays deferred.

HEAD has CUD honesty and `ui_writes` stubs. This commit adds the durable CUD
gate (`EE0A0F1B`) and `ui-full` mode (`DD80C9A8`). Node complete is false.

Coverage: complete false; implemented 512; contract 528; UI live/vision 328.
Sixteen CUD parity rows are open-only and not implemented/live/vision. No
`ui_*_preview` / `ui_*_execute` tools yet.

## Children

Seven Grok write children are active and offline-first. Contacts holds the live
slot. Do not merge until they land preview/execute plus offline proof.

## Review

`.fractal/main.billy_complete/tmp/grok-review.md`: package PASS with R1 commit;
N1 discovery create greens left in place; N2 file-digest tests are the files
child; N3 consume-before-submit is the same as the API ticket protocol.

See `decisions.md` and `todo.md`.
