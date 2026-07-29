---
requires_approval: false
agent: codex-power
---

## Independent review

Review the current iteration independently. Do not implement production code.
Write findings to `$NODE_DIR/tmp/grok-review.md`, replacing the prior
iteration's file.

Check:

1. Current official Billy documentation against the maintained API inventory.
2. The tested Billy interface against the interface inventory and API parity
   map.
3. Typed input and output schemas, request construction, response mapping,
   filters, pagination, errors, and writes in the current diff.
4. Approval-token binding, authentication, redaction, host and path
   restrictions, cleanup, and repository secret safety.
5. Headless interface evidence. Review field values before submission, the
   success state, independent read-back, cleanup, and raw-frame purge.
6. Coverage status. Reject any green row based on a stub, mock, skip, untested
   operation, inaccessible screen, ambiguous contract, or vision-only result.

Use current primary sources and include direct citations for every contract
discrepancy. Use the project's headless vision-review harness for any pending
visual evidence. Never open a headed browser or touch desktop windows.

The report must give a pass or fail verdict, exact file and coverage-row
references, reproducible commands or evidence references, and required fixes.
Post high-priority blockers to the parent by radio and continue the step.
