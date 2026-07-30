---
name: state
desc: Current state of the Wave-5s-B upload containment repair.
created: 2026-07-30T19:14:38Z
updated: 2026-07-30T19:14:38Z
---

# state

Delivered in `54b4579`: execution opens the canonical configured upload root
and each relative directory component by descriptor with no-follow semantics.
The terminal descriptor is verified as the previewed regular-file size and
mtime, then supplies the exact buffer that is SHA-256 checked and sent.

Terminal and intermediate same-digest symlink swaps to outside-root content are
rejected as `FILE_NOT_ALLOWED` before the mock transport. Changed in-root bytes
still return `FILE_CHANGED` without a request. The focused archive test passed
all 38 upload tests. The parent-owned authoritative Grok product audit remains
open; this leaf's Codex fallback review is non-authoritative.
