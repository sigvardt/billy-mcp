---
name: memory
desc: Node private working state for billy_complete
tags: []
sources: []
created: 2026-07-29T07:56:19Z
updated: 2026-07-29T08:50:00Z
---

# memory

***

## Status

- Independent review: **FAIL**. Report: `.fractal/main.billy_complete/tmp/grok-review.md`.
- Research brief stands: `.fractal/main.billy_complete/tmp/grok-research.md`.
- Worktree still has no `coverage/`, `src/`, `tests/`, or `pyproject.toml`.
- Product-tracked content: design, README, wiki research seed only.
- Branch HEAD: `c60a4f7`. Uncommitted: memory + wiki seed only.

## Review outcomes that stand

- Official docs rechecked: etag `hsisik4g9p3603`; body 147934 bytes; MD5 `c2efda0ee4cf9cf200e14910c5fc6996`; 46 resources; 299 Supports; 207 clear ops; 92 bulk ambiguous; 0 webhooks.
- Paging on live docs: `page` + `pageSize` only (offset is bank-fee prose / historical gist, not paging contract).
- Specials still documented; bulk method body still undocumented on live page.
- Live errors: missing auth → `AUTHENTICATION_REQUIRED`; invalid token → `OAUTH_INVALID_ACCESS_TOKEN`.
- OPTIONS allow-methods include PATCH (CORS only; not bulk contract).
- Sample path ambiguity: `GET /v2/organization` (singular) vs `/v2/organizations` TOC.
- `/v2/documents` is CMS noise, not a Billy resource.
- No false greens (no coverage rows).
- `scripts/test.sh` soft-passes exit 0 without `pyproject.toml` — not qualification.
- Secret scan of tracked files: clean.

## Blockers (must clear via Codex Power)

1. Freeze red `coverage/api_v2_manifest.yaml` (+ UI + browser_egress + status.json complete:false).
2. Shared FastMCP foundation: locked client, tickets, redaction, coverage_* only; zero domain stubs.
3. Dedicated non-production credentials for later live/UI work (not present).

## Contract facts

- Primary: https://www.billy.dk/api/
- Base lock: https://api.billysbilling.com/v2 + X-Access-Token
- Design: docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
- Filter tables only: invoices, bills, daybookTransactions (full lists in research brief §7)
