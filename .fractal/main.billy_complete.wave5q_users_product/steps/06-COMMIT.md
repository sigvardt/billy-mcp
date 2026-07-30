---
requires_approval: false
---

## Commit

1. Commit: `fractal commit "<short lowercase summary>"` -- this checks scope,
   lints, stages, commits, and pushes (unless `--local` was passed to
   initialization). Fix and retry on lint failure. Hook reformats of project
   files are auto-retried once -- review what they changed (`git diff HEAD~`).
   Hook rewrites of wiki pages (`wiki/` and your memory wiki) are auto-retried
   too when they preserve wiki structure (a breaking rewrite fails with the fix
   in the error); any hook rewrite of other `.fractal/` pages is refused -- and
   never run project format hooks over those paths yourself: damage applied
   before staging bypasses the commit-time guard.

   The summary is wrapped as `<branch>: iteration <run>.<iter> (<summary>)` --
   pass only the bare summary. A message containing the branch name or the word
   "iteration" is rejected; re-commit with a plain summary.

   If it rejects **out-of-scope changes** (e.g. ancestor `_index.md` files
   touched by `wiki update`), revert them and retry:

   ```bash
   git checkout HEAD -- <out-of-scope files listed in the error>
   fractal commit "<summary>"
   ```

   When the out-of-scope changes are genuinely intentional, commit them with
   `--ignore-scope` (it still lints):

   ```bash
   fractal commit "<summary>" --ignore-scope
   ```

   Reserve `--force` for a true last resort -- it bypasses the scope check *and*
   lint.

2. Only after the commit succeeds and the worktree is clean, if every
   Completion Requirement is met, signal completion:
   `fractal node finish --reason="Wave-5q users update offline product delivered"`.
   Do not claim the separate Grok product independent review, live/UI/vision,
   bulk, or overall completeness. Post the resulting offline handoff to the
   parent through the node outbox; do not wait for a reply.
