---
name: memory
desc: Node private working state for billy_complete
tags: []
sources: []
created: 2026-07-29T07:56:19Z
updated: 2026-07-29T08:28:10Z
---

# memory

***

## Status

- Independent review: **FAIL**. Report: `.fractal/main.billy_complete/tmp/grok-review.md`.
- Worktree still has no `coverage/`, `src/`, `tests/`, or `pyproject.toml`.
- Product-tracked content: design, README, wiki research seed only.
- Research brief stands: `.fractal/main.billy_complete/tmp/grok-research.md`.

## Review outcomes that stand

- Official docs rechecked: etag `hsisik4g9p3603`; 46 resources; 299 Supports; 207 clear ops; 92 bulk ambiguous; 0 webhooks.
- Paging on live docs: `page` + `pageSize` only (offset is fee prose / historical gist, not paging contract).
- Specials still documented; bulk method body still undocumented on live page.
- No false greens (no coverage rows).
- `scripts/test.sh` soft-passes exit 0 without `pyproject.toml` — not qualification.

## Blockers (must clear via Codex Power)

1. Freeze red `coverage/api_v2_manifest.yaml` (+ UI + browser_egress + status.json complete:false).
2. Shared FastMCP foundation: locked client, tickets, redaction, coverage_* only; zero domain stubs.
3. Dedicated non-production credentials for later live/UI work (not present).

## Contract facts

- Primary: https://www.billy.dk/api/
- Base lock: https://api.billysbilling.com/v2 + X-Access-Token
- Design: docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
