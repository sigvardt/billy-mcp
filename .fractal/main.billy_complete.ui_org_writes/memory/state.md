---
name: state
desc: Offline org-update preview/execute is delivered. Live submit is a recorded parent-slot blocker.
tags: [state]
created: 2026-08-16T14:36:03Z
updated: 2026-08-16T14:36:03Z
---

# state

`ui_organizations_update_preview` and `ui_organizations_update_execute` register
from `src/billy_mcp/ui_writes/organizations.py`. Offline ticket tests pass.
Node `scripts/test.sh` runs `tests/unit/test_ui_organizations_writes.py`.

Shared contract: `wiki/ui_organizations_writes.md`. Locked choices: this wiki's
`decisions` page.

Live execute submit is blocked by parent radio `D5136C2E` (contacts holds the
slot). That blocker is recorded on the wiki. No company field has been changed.
Coverage stays red. Parent `complete` stays false.


