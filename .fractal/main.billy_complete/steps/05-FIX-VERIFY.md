---
requires_approval: false
agent: grok
---

## Fix and verify

Read `$NODE_DIR/tmp/grok-review.md`. Reproduce every reported problem. Fix each
confirmed problem and record why any rejected finding is incorrect with direct
evidence.

Review the complete diff for missed edge cases and rule violations. Run:

```bash
bash "$NODE_DIR/scripts/lint.sh"
bash "$NODE_DIR/scripts/test.sh"
```

When all completion requirements may now be true, also run:

```bash
BILLY_TEST_MODE=full bash "$NODE_DIR/scripts/test.sh"
```

Do not set `coverage/status.json` to `complete: true` by hand. The coverage
generator may set it only from passing row-level evidence.

Update memory per the memory skill. Put project-wide architecture, conventions,
and evidence rules in the shared project wiki. Run `wiki lint` on both stores
and fix actionable problems.

Append a `## Post-Mortem` section to each plan used this iteration. Record work
completed, deviations, review findings, test results, cleanup state, and the
next unresolved coverage slice. If every completion requirement passes, record
the final evidence instead of a next slice.
