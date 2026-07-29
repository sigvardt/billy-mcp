---
requires_approval: false
agent: codex-power
---

## Codex Power fallback review

The designated Grok route is unavailable before product edits because its
device/API authentication is absent. Perform a separate-context Codex Power
fallback review of this leaf only; it cannot be labelled a Grok review or close
the parent's mandatory Grok product-review gate. Write the explicit fallback
verdict and the authentication limitation to `$NODE_DIR/tmp/grok-review.md`.

Review the owned diff against `wiki/wave_fived_ticketed_writes_contract.md` and
the accepted Wave-5c pattern. Check typed schemas, exact routes and roots,
preview non-mutation, ticket/executor binding before consume or HTTP, single-use
failure paths, no write retries, error mapping, focused evidence, secrets, and
unchanged non-Wave-5d coverage. Give PASS or FAIL with exact locations and
reproducible commands; post blockers to the parent. Do not browse, use a
browser, or claim live/UI/vision evidence.
