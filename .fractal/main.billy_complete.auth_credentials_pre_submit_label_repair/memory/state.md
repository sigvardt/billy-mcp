---
name: state
desc: Verified current state of the scoped auth submit-label repair.
created: 2026-07-30T22:45:29Z
updated: 2026-07-30T22:45:29Z
---

# state

The pre-submit login signature accepts only trimmed `Log in` and `Log ind`.
The fake default and happy-path coverage use those labels. The legacy page title
`Login` returns `UI_CHANGED` before credential resolution, fill, or click.

Focused browser tests, node lint and test scripts, Ruff, and Pyright pass. The
shared auth pre-submit research page remains the canonical project-wide contract;
this repair adds no new shared knowledge.
