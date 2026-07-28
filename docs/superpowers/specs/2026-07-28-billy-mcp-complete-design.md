# Billy MCP Full-Scope API and Interface Design

Date: 2026-07-28

Repository: `sigvardt/billy-mcp`

Status: Approved design, implementation not started

## 1. Summary

Billy MCP is one Python FastMCP server using stdio transport. It exposes Billy through two explicit lanes:

| Lane | Prefix | Contract |
| --- | --- | --- |
| Official API | `api_*` | Every supported operation in Billy's official API v2 |
| Web interface | `ui_*` | Full parity with API capabilities exposed in Billy's web interface, followed by all additional UI-only capabilities |
| Shared authentication | `auth_*` | API credentials, persistent browser login, reauthentication, MFA, organisation selection, and recovery |
| Coverage | `coverage_*` | Read-only inventory and test status |

The official API base URL is fixed to `https://api.billysbilling.com/v2`. API requests use `X-Access-Token`.

Reads run directly. Writes use an autonomous two-call protocol: preview, then execute with a short-lived, single-use confirmation ticket bound to the exact operation. Human approval is not required for normal writes.

Every browser used by development, tests, and runtime is headless. The interface lane keeps its dedicated persistent profile but never opens, raises, focuses, or manipulates a desktop window.

No completeness claim is allowed until every applicable API and interface coverage row is implemented and tested.

## 2. Goals

1. Inventory every operation in Billy's official API documentation before implementation.
2. Implement every supported official API operation as a typed `api_*` tool.
3. Implement a matching `ui_*` workflow for every API capability Billy exposes through its interface.
4. Add every verified UI-only workflow after the interface lane reaches API parity.
5. Handle API and headless browser authentication completely, including persisted sessions, credentials and TOTP from environment or credential store, expiry, reauthentication, MFA detection, organisation selection, and recovery.
6. Give every tool typed Pydantic input and output models.
7. Use stable, predictable tool names grouped by business area.
8. Track method or route, request fields, response fields, filters, pagination, errors, side effects, cleanup, implementation, and tests in machine-readable coverage manifests.
9. Test request construction, response mapping, errors, pagination, reads, writes, authentication, egress, browser recovery, interface drift, plan restrictions, and cleanup.
10. Verify every interface feature end to end through the headless UI using DOM assertions, independent API or UI read-back, and agent vision.
11. Keep credentials outside the repository.
12. Expose no telemetry, shell execution, dynamic code execution, generic HTTP proxy, or raw browser-control tools.
13. Verify against a Billy test account or dedicated non-production organisation before enabling live use.

## 3. Non-goals

1. No catch-all click, type, selector, browser-navigation, DOM-dump, or arbitrary HTTP tools.
2. No automatic fallback from the API lane to the interface lane.
3. No invented endpoint or webhook support.
4. No caller-provided `confirm: true` boolean.
5. No placeholder or stub tools.
6. No automated test writes against production organisations.
7. No transport other than stdio.
8. No claim that a documentation gap counts as implemented coverage.
9. No headed browser in development, tests, or runtime.
10. No opening, raising, focusing, or manipulating desktop windows.
11. No use of agent vision as the sole verification oracle.

## 4. Terminology

### 4.1 Billy API credential

A long-lived Billy access token sent in `X-Access-Token`. It comes from `BILLY_API_TOKEN` or the operating system credential store. It is never returned to an MCP caller, committed, or logged.

### 4.2 Confirmation ticket

A short-lived, single-use capability returned by a write preview. It is not a Billy credential. It authorises only one exact, already-previewed operation.

### 4.3 API parity baseline

The interface lane must implement the same business capabilities as the API lane wherever Billy's interface exposes them. The interface lane is not merely a gap-filler.

### 4.4 UI-only capability

A verified operation exposed by Billy's interface without an equivalent supported operation in the official API.

### 4.5 Coverage row

One official API operation or one verified interface workflow, with its contract, implementation status, and test evidence.

### 4.6 Headless browser policy

Every Billy browser process launched or controlled by the project is headless. The MCP never controls a desktop window.

### 4.7 Vision verification

A vision-capable agent inspects rendered headless browser frames to verify the intended visible values, submission result, resulting record, and clean restoration. Vision supplements DOM assertions and independent read-back; it never replaces them.

### 4.8 UI write capture set

For a UI write test, the required rendered frames are:

1. Initial state before editing
2. Completed fields immediately before submission
3. Success state and resulting record after submission
4. Restored state after cleanup

## 5. Architecture

```text
MCP host
  |
  | stdio
  v
FastMCP server
  |
  +-- auth_*       shared authentication and organisation context
  +-- api_*        typed Billy API client
  +-- ui_*         typed Playwright workflows
  +-- coverage_*   read-only coverage status
  |
  +-- confirmation ticket store
  +-- stable errors and redacted logging
  +-- network policy and coverage registry
```

### 5.1 Process model

- One Python process and one FastMCP stdio server.
- One managed HTTP client for the official API.
- One MCP-owned persistent Chrome profile for the interface lane.
- One shared authentication and organisation service.
- One in-memory confirmation-ticket store.
- One machine-readable coverage registry.
- Pending confirmation tickets are discarded when the server restarts.

### 5.2 Explicit lanes

Agents select a lane through the tool name. The server never silently changes lanes.

The API lane is preferred for speed and contract stability when an agent chooses it. The interface lane exists both for API parity and for features absent from the official API.

### 5.3 Tool registration

Only implemented tools are registered. Planned names exist in coverage manifests, not as callable stubs.

Every registered tool has:

- A stable name
- A typed input model
- A typed output model
- Stable error codes
- One or more coverage row identifiers
- Tests appropriate to its risk and behaviour

## 6. Tool naming

### 6.1 Pattern

```text
api_<area>_<verb>
ui_<area>_<verb>
auth_<verb>
coverage_<verb>
```

Reads are single-call tools:

```text
api_invoices_list
api_invoices_get
ui_invoices_list
ui_invoices_get
```

Every write has separate preview and execute tools:

```text
api_invoices_create_preview
api_invoices_create_execute
ui_invoices_create_preview
ui_invoices_create_execute
```

Execute tools accept only the confirmation ticket. They do not accept replacement business inputs or a boolean confirmation.

Authentication session transitions such as reauthentication and organisation selection do not modify Billy business data and do not require a confirmation ticket. Creating or revoking an API token, logging out, changing Billy settings, or performing another Billy-side mutation does require preview and execute.

### 6.2 Auth examples

```text
auth_status
auth_login_start
auth_login_wait
auth_reauthenticate
auth_organizations_list
auth_organization_select
auth_api_token_bootstrap_preview
auth_api_token_bootstrap_execute
auth_logout_preview
auth_logout_execute
```

These names are illustrative until the complete inventory freezes the public tool manifest. The naming pattern is fixed.

## 7. Authentication

### 7.1 API credential resolution

The API credential is resolved in this order:

1. `BILLY_API_TOKEN`
2. An organisation-specific token in the operating system credential store
3. Optional bootstrap through the authenticated Billy interface

Interface bootstrap creates an access token through Billy's settings and stores it directly in the credential store. The token value is never returned through MCP.

### 7.2 Browser authentication

The interface lane owns a dedicated Chrome profile outside the repository. It does not attach to the user's everyday browser profile. Chrome always runs headless and never creates or manipulates a desktop window.

The authentication service handles:

- Initial login
- Persistent session recovery
- Login-state detection
- Session expiry
- Reauthentication
- Credential and TOTP resolution from environment variables or the operating system credential store
- MFA, CAPTCHA, passkey, and other challenge detection
- Organisation discovery and selection
- Organisation mismatch detection
- Safe logout
- Browser crash recovery

Authentication first reuses the persisted session. When login is required, the headless browser uses credentials and optional TOTP stored outside the repository. An unautomatable MFA, CAPTCHA, passkey, push approval, or similar challenge returns `AUTH_INTERACTION_REQUIRED` with recovery instructions and never launches a visible browser.

Normal reads and writes are autonomous whenever the session or securely stored authentication material is sufficient.

### 7.3 Authentication states

```text
NO_SESSION
  -> AUTHENTICATING
  -> NEEDS_ORGANISATION
  -> READY
  -> EXPIRED
  -> AUTHENTICATING
```

Failures enter `FAILED` with a stable error and recovery action.

`READY` requires:

- A selected organisation
- A valid API credential for API tools
- A valid browser session for interface tools

An organisation mismatch always fails closed.

### 7.4 Secret handling

The server never logs:

- API tokens
- Passwords
- MFA codes
- Cookies
- Browser storage
- Confirmation tickets

An opaque confirmation ticket is returned only by its preview tool and accepted only by its matching execute tool. It is not written to durable storage.

Logs may contain tool name, coverage row, duration, non-secret organisation identifier, and stable error code.

## 8. Autonomous write protocol

### 8.1 Preview

A write preview:

1. Validates the typed input.
2. Confirms authentication and organisation.
3. Canonicalises all business inputs.
4. Reads current state when required.
5. Validates files and destinations when present.
6. Builds a human-readable summary for the agent.
7. Creates a short-lived, single-use confirmation ticket.
8. Returns the summary, canonical inputs, expected-state summary, ticket, and expiry.

Preview performs no write.

### 8.2 Execute

An execute tool:

1. Accepts only the confirmation ticket.
2. Rejects missing, invalid, expired, consumed, or mismatched tickets.
3. Restores the exact operation and inputs from the ticket record.
4. Revalidates authentication and organisation.
5. Rechecks expected current state.
6. Revalidates file identity or destination when present.
7. Executes the exact operation once.
8. Consumes the ticket.
9. Returns the typed result and verified post-state.

Any changed input or state requires a new preview.

For interface writes under test, the workflow captures the four required rendered states: initial state before editing, completed fields immediately before submission, success state and resulting record after submission, and restored state after cleanup. The result is accepted only when DOM assertions, independent read-back, and vision verification agree at every applicable state.

### 8.3 Ticket binding

Every ticket binds:

- Lane
- Tool
- Billy organisation
- Canonical inputs
- Expected current state
- Expiry
- Single-use identifier
- File identity when uploading
- Normalised destination when configuring an integration or webhook

Tickets contain at least 256 bits of cryptographic randomness and expire no later than five minutes after preview. Tickets are server-side opaque identifiers so they can be revoked and consumed reliably.

### 8.4 Files

Preview resolves and validates the exact local file:

- Canonical real path
- Configured allowed root
- Regular-file check
- Size
- Modification time
- SHA-256
- Intended Billy destination

Execute repeats these checks and rejects a changed file or symlink escape.

Allowed upload roots are explicitly configured outside the repository.

### 8.5 Destinations

Integration and webhook destinations bind the normalised scheme, host, port, path, and relevant query values.

No documented Billy webhook was found during initial research. The server will not invent a webhook tool. Webhooks remain a red discovery row until an official or verified interface contract exists.

## 9. Official API lane

### 9.1 Contract

Billy's official API documentation is the source of truth.

Base URL:

```text
https://api.billysbilling.com/v2
```

Authentication header:

```text
X-Access-Token
```

### 9.2 Initial research snapshot

Initial documentation research found:

| Item | Count |
| --- | ---: |
| Resources | 46 |
| Operation flags | 299 |
| Additional special routes | 6 |
| Total operation mentions | 305 |
| Clear method and path entries | 213 |
| Bulk save/delete entries needing contract clarification | 92 |
| Documented webhooks found | 0 |

These counts are a starting point, not a completeness claim.

The 92 ambiguous bulk operations must be clarified through updated official documentation, Billy support, or controlled testing against the dedicated non-production organisation. They remain red until their complete contract is known, implemented, and tested.

### 9.3 API implementation order

1. Freeze the official endpoint inventory.
2. Implement typed read operations.
3. Implement pagination, filtering, response mapping, and errors.
4. Implement writes through preview and execute.
5. Implement bulk and special operations only after their contracts are clear.
6. Run contract and live non-production tests.

No documentation ambiguity may be waived into a green completeness status.

## 10. Interface lane

### 10.1 Automation contract

The interface lane uses Playwright with the dedicated persistent Chrome profile in headless mode only. Development, CI, live verification, and runtime use the same no-window rule.

Each business area has typed page objects and workflow state machines. Selectors prefer accessible roles, labels, and stable route or data markers. Fragile styling selectors are avoided.

The MCP exposes business operations, not browser primitives.

### 10.2 API parity first

For every official API business operation:

1. Determine whether Billy exposes an equivalent interface workflow.
2. Record the mapping and evidence.
3. Implement the typed `ui_*` workflow when applicable.
4. Test it independently of the API tool through the headless UI.
5. Verify it with DOM assertions, independent API or UI read-back, and agent vision.

If Billy has no equivalent interface workflow, the UI row is marked not applicable with evidence. No stub tool is registered.

### 10.3 UI-only second

After the parity baseline, implement all additional verified interface capabilities.

The initial read-only discovery probed 107 routes and found 31 real route families plus settings.

The following route families were discovered at read or navigation depth. None is green until `discovered`, `implemented`, `contract_tested`, `live_tested`, and `vision_verified` are all true:

- Invoices
- Quotes
- Recurring invoices
- Products and product import
- Customers
- Debtor and creditor balances
- Uploads and receipt inbox
- Purchases and suppliers
- Bank accounts and reconciliation
- Financing
- Daybooks and transactions
- Reports
- VAT declarations
- Annual reports
- Exports, including SAF-T
- Add-ons and integrations
- Inventory
- Company, user, accounting, VAT, invoicing, users, subscription, access-token, and beta settings

Still red:

- Field-level write flows
- Authentication transitions
- Account menu and organisation switching
- Full daybook editor
- Plan-gated workflows
- Some settings workflows

### 10.4 Headless vision verification

Every interface coverage row requires end-to-end execution through headless Chrome.

Read workflows require:

- DOM assertions for the expected values and controls
- A rendered headless frame inspected by a vision-capable agent
- Independent API or second UI read-back

If no independent read-back path exists, the row remains red until one is established.

Write workflows require:

1. Initial-state frame
2. Completed-form frame before submission
3. DOM assertions that the exact intended values are present
4. Submission through the real Billy UI
5. Success-state and resulting-record frame
6. Independent API or UI read-back of the submitted result
7. Cleanup through the supported API or UI path
8. Restored-state frame and final read-back

The vision-capable agent must confirm the intended visible values, the correct submission result, the resulting record, and clean restoration. Vision is additive evidence and never the sole oracle.

After review, raw frames are purged. The durable `vision_evidence` record contains only the coverage row, test-run identifier, assertion and read-back references, reviewer verdict, timestamp, and `purge_verified: true`. It contains no screenshot, rendered frame, credential, or Billy business value.

### 10.5 Interface drift

Every workflow defines an expected page signature using route, stable controls, and critical labels.

If the signature changes, the tool returns `UI_CHANGED`. It does not guess, use coordinates, or click a visually similar control.

### 10.6 Browser recovery

The browser manager:

- Launches only a headless browser using the MCP-owned profile
- Never opens, raises, focuses, or manipulates a desktop window
- Serialises stateful UI writes
- Closes extra tabs after workflows
- Restores a known safe route
- Detects crashes and stale sessions
- Recreates the page without discarding the profile
- Never resumes a pending write automatically after a crash

## 11. Network policy

### 11.1 API client

The API client can contact only:

```text
https://api.billysbilling.com
```

The base URL is never caller-configurable. Tests inject a mock HTTP transport instead of changing the destination.

### 11.2 Browser

The browser:

- Allows only exact Billy application and asset hosts recorded in the reviewed browser-egress manifest
- Blocks surveys, analytics, telemetry, and unrelated third parties
- Has no general-purpose browsing tool
- Denies unrecognised destinations by default

Some explicit Billy workflows require another company's site, such as Google authentication, a bank login, Stripe, MobilePay, or Froda.

For those workflows only:

1. The exact partner host is verified during discovery.
2. The matching typed tool temporarily allows only the required hosts.
3. The destination is included in the write preview when it affects configuration or disclosure.
4. The temporary allowance ends with the workflow.

The repository contains a reviewed browser-egress manifest with exact Billy and partner hosts, owning workflow, purpose, and test evidence. Unknown hosts remain denied. The allowlist is built from verified flows, never guesses.

## 12. Coverage model

### 12.1 Manifests

The repository contains:

```text
coverage/api_v2_manifest.yaml
coverage/ui_workflows_manifest.yaml
```

Each row tracks:

| Field | Meaning |
| --- | --- |
| `id` | Stable row identifier |
| `lane` | `api` or `ui` |
| `area` | Business area |
| `operation` | Stable verb |
| `method_or_route` | API method/path or UI route/workflow |
| `request_fields` | Typed inputs |
| `response_fields` | Typed outputs |
| `filters` | Supported filters |
| `pagination` | Pagination contract |
| `errors` | Known error shapes |
| `side_effects` | External changes |
| `cleanup` | Test cleanup procedure |
| `tool_name` | Registered MCP tool |
| `discovered` | Contract exists |
| `implemented` | Real implementation exists |
| `contract_tested` | Unit or contract tests pass |
| `live_tested` | Dedicated non-production verification passes |
| `vision_verified` | Vision-capable agent verified rendered headless UI evidence; required for UI rows only |
| `vision_evidence` | Durable non-sensitive review record that references the run, assertions, read-back, reviewer, and verified purge; never a raw frame |
| `evidence` | Documentation or test reference |

### 12.2 Completeness rule

An API row is green only when all four required statuses are true:

- `discovered`
- `implemented`
- `contract_tested`
- `live_tested`

An interface row requires those four statuses plus:

- `vision_verified`

`vision_verified` is not applicable to API rows. It is mandatory for every interface parity and UI-only row.

An operation that cannot yet be safely tested remains red. `not_applicable` is allowed only for a UI parity row when evidence shows Billy exposes no equivalent UI workflow. It is not allowed for an official API operation.

The project may claim feature completeness only when:

- Every supported official API operation is green.
- Every applicable interface parity row is green.
- Every verified UI-only operation is green.
- No unresolved documentation or discovery gap is being counted as complete.

Plan-gated or irreversible operations require a Billy-supported test path or resettable dedicated organisation. If that is unavailable, the row remains incomplete.

### 12.3 Generated report

CI generates a human-readable coverage table and a single machine-readable `coverage/status.json`. The generated `complete` field is the only source for README and release completeness status.

CI fails if:

- A registered tool lacks a coverage row.
- An implemented row lacks required tests.
- An interface row is green without `vision_verified` and a durable `vision_evidence` review record.
- A vision review record lacks DOM assertions, independent read-back, reviewer result, or `purge_verified: true`.
- Raw rendered frames are present in the repository or remain after the review retention window.
- The report is stale.
- `coverage/status.json` says `complete: true` while any applicable row remains red.
- README or release metadata claims completeness without generated `complete: true`.

## 13. Errors

Public errors are stable and machine-readable.

| Code | Meaning |
| --- | --- |
| `AUTH_REQUIRED` | Authentication is missing |
| `AUTH_EXPIRED` | Credential or browser session expired |
| `AUTH_INTERACTION_REQUIRED` | An unautomatable MFA, CAPTCHA, passkey, push approval, or similar challenge requires out-of-band resolution; no browser window is launched |
| `ORGANIZATION_REQUIRED` | No organisation selected |
| `ORGANIZATION_MISMATCH` | Current organisation differs from the request or ticket |
| `VALIDATION_ERROR` | Typed or business validation failed |
| `NOT_FOUND` | Billy resource or interface object is missing |
| `CONFLICT` | Current state changed |
| `CONFIRMATION_INVALID` | Ticket is invalid |
| `CONFIRMATION_EXPIRED` | Ticket expired |
| `CONFIRMATION_CONSUMED` | Ticket was already used |
| `CONFIRMATION_MISMATCH` | Operation, state, file, or destination changed |
| `FILE_NOT_ALLOWED` | Path is outside configured roots |
| `FILE_CHANGED` | File changed after preview |
| `PLAN_UNAVAILABLE` | Billy plan does not expose the feature |
| `UI_CHANGED` | Interface signature changed |
| `EGRESS_DENIED` | Destination is not allowed |
| `RATE_LIMITED` | Billy rate limit was reached |
| `BILLY_ERROR` | Billy returned an upstream error |
| `CLEANUP_FAILED` | Test data could not be fully removed |

There is no production `NOT_IMPLEMENTED` error because stub tools are not registered.

## 14. Testing

### 14.1 Test layers

| Layer | Coverage |
| --- | --- |
| Unit | Canonicalisation, request construction, response mapping, errors, tickets, file identity, URL normalisation, redaction |
| Contract | Pydantic schemas against documentation and sanitised fixtures |
| API integration | Filters, pagination, errors, reads, and writes against the dedicated organisation |
| Interface workflow | Headless selectors, state machines, reads, writes, plan gates, typed mapping, rendered-frame capture, and vision verification |
| Authentication | Headless login states, persisted sessions, credential and TOTP resolution, expiry, reauthentication, challenge errors without a window, organisation selection, credential bootstrap |
| Egress | Allowed and denied destinations for both lanes |
| Recovery | Browser crash, stale session, restart, and discarded tickets |
| Cleanup | Reverse-order deletion and leftover reporting |

### 14.2 Live test safety

Automated live tests run only against a dedicated non-production organisation or a Billy-supported sandbox. The test runner has no production-write mode.

Runtime use against a production organisation is permitted only after the non-production qualification suite passes. Production runtime writes additionally require:

- An explicit live-write enablement setting
- An explicit organisation allowlist

Neither setting is committed with an enabled value. Runtime production enablement is not a testing mechanism.

### 14.3 Write-test lifecycle

1. Generate a unique test-run identifier.
2. Create clearly tagged temporary resources.
3. Capture the initial rendered state for an interface write.
4. Exercise preview, fill the form, and capture the completed fields before submission.
5. Execute through the real headless UI and capture the success state and resulting record.
6. Verify DOM state and independently read back the result through the API or a second UI path.
7. Have a vision-capable agent verify the intended values, submission, and resulting record.
8. Track every created or changed object.
9. Restore or delete in reverse dependency order.
10. Capture the restored state, assert it through the DOM, independently read it back, and have the vision-capable agent verify clean restoration.
11. Write a non-sensitive vision-review record, purge the raw frames, and record `purge_verified: true`.
12. Run a final search for the test tag where supported.
13. Fail with `CLEANUP_FAILED` and report exact leftovers if cleanup is incomplete.

The test suite never hides orphaned data.

### 14.4 Irreversible actions

Tax submission, external financing, subscription purchase, and similar actions are not tested against production.

They require a Billy-supported sandbox, a resettable dedicated organisation, or an explicit documented test mode. Until verified safely, they remain red and prevent a completeness claim.

## 15. Security requirements

1. No secrets in source control, fixtures, test recordings, or examples.
2. Credentials come only from environment variables or the operating system credential store.
3. The browser profile, downloads, and test-org rendered-frame evidence stay outside the repository with owner-only permissions.
4. Confirmation tickets are high-entropy, short-lived, single-use, and never logged.
5. File uploads are restricted to configured roots.
6. API and browser egress policies are enforced in code.
7. No telemetry from Billy MCP.
8. The MCP server exposes no shell or dynamic-code operation.
9. Dependencies are minimal, locked, audited, and updated through reviewed changes.
10. Every browser is headless and the project never opens, raises, focuses, or manipulates a desktop window.
11. Production runtime never persists screenshots, rendered frames, HAR files, or browser traces.
12. Non-production test rendered frames are ephemeral, stored outside the repository with owner-only permissions, and purged after vision review. Synthetic and sanitised fixtures may be committed.
13. Public releases are scanned for credentials and dependency advisories.
14. The MCP host is trusted to call tools. Tickets protect against accidental or stale writes, not a fully malicious local host.

## 16. Repository structure

```text
billy-mcp/
  README.md
  LICENSE
  pyproject.toml
  src/billy_mcp/
    server.py
    config.py
    errors.py
    logging.py
    auth/
    api/
    ui/
    confirmations/
    coverage/
  coverage/
    api_v2_manifest.yaml
    ui_workflows_manifest.yaml
    browser_egress.yaml
    status.json
    vision_reviews/
  tests/
    unit/
    contract/
    live/
    fixtures/
  scripts/
    generate_coverage_report.py
  docs/
    superpowers/specs/
    authentication.md
    security.md
  .github/workflows/
```

The repository excludes:

- `.env` and credentials
- Browser profiles and cookies
- Downloads containing company data
- HAR files, traces, screenshots, and rendered-frame evidence
- Test-account exports

## 17. Delivery plan

### Phase 0: Inventory and shared foundation

1. Create the public repository and CI.
2. Freeze the official API inventory before API implementation.
3. Create the interface workflow inventory and API-parity cross-map.
4. Create coverage manifest schemas and generated reports.
5. Implement FastMCP stdio shell, typed errors, config, and redacted logging.
6. Implement headless-only authentication, organisation context, credential and TOTP storage, and persistent browser lifecycle without desktop-window control.
7. Implement autonomous confirmation tickets.
8. Implement API and browser egress policies.

### Lane A: Official API

1. Implement every clear read operation.
2. Implement typed response mapping, filters, pagination, and errors.
3. Clarify every ambiguous bulk and special operation.
4. Implement every write through preview and execute.
5. Run unit, contract, and dedicated-organisation tests.
6. Keep ambiguous or untested rows red.

### Lane B: Interface API parity

1. Cross-map every API business operation to Billy's interface.
2. Implement every applicable read workflow.
3. Map every write form field and validation rule.
4. Implement every applicable write through preview and execute.
5. Implement the rendered-frame capture and agent-vision verification pipeline.
6. Test authentication transitions, organisation switching, plan gates, drift, recovery, vision evidence, and cleanup through headless Chrome.
7. Require all applicable parity rows to be green before moving the lane beyond parity.

### Lane B: UI-only coverage

1. Complete the remaining verified interface inventory.
2. Implement inventory, Copilot, financing, annual reports, bulk exports, partner integrations, settings, and other verified UI-only workflows.
3. Verify external partner destinations and scope their temporary allowlists.
4. Test every claimed UI-only workflow headlessly against the dedicated organisation or supported sandbox, including required vision evidence.

### Final reconciliation

1. Cross-link API and interface coverage.
2. Run the complete test suite.
3. Run credential, telemetry, network, dependency, and public-artifact audits.
4. Verify every UI row has vision evidence and that ephemeral frames were purged.
5. Verify the test organisation is clean.
6. Publish a completeness claim only when every applicable row is green.

## 18. Implementation roles

- Grok CLI performs implementation grunt work.
- Codex orchestrates, reviews, verifies evidence, and decides what is accepted.
- A vision-capable agent verifies every headless UI workflow using rendered-frame evidence in addition to DOM assertions and independent read-back.
- Humans may place credentials or TOTP material in the environment or operating system credential store and resolve unavoidable authentication challenges out of band. The MCP never launches a visible browser.

Codex subagents are not used for this project unless the user changes that instruction.

## 19. Acceptance criteria

The project is complete only when all of these are true:

1. One FastMCP stdio server lists only real, typed tools.
2. Every supported official API operation is implemented and tested.
3. Every API capability exposed by Billy's interface has a headless end-to-end tested and vision-verified UI equivalent.
4. Every verified UI-only operation is implemented, headless end-to-end tested, and vision verified.
5. Authentication covers API tokens, headless persistent login, credential and TOTP resolution, expiry, reauthentication, MFA detection, organisation selection, bootstrap, recovery, and no-window challenge errors.
6. Every write uses preview and execute with an exact, one-use confirmation ticket.
7. File and destination bindings are revalidated at execution.
8. No generic browser, HTTP, shell, or dynamic-code tool exists.
9. Egress controls and telemetry blocking are enforced.
10. Every browser is headless and no project process opens, raises, focuses, or manipulates a desktop window.
11. Coverage reports are generated from manifests, every API row satisfies the four-status rule, every UI row additionally has `vision_verified`, and generated `coverage/status.json` says `complete: true`.
12. Request construction, response mapping, filters, pagination, errors, writes, authentication, recovery, plan gates, rendered-frame vision, and cleanup are tested.
13. Automated live verification uses only a dedicated non-production organisation or Billy-supported sandbox.
14. Test data is removed or restored, cleanup failures are visible, and ephemeral rendered frames are purged after review.
15. Production runtime persists no screenshot, rendered frame, HAR, or browser trace.
16. The public repository contains no credential or private company artifact.
17. No unresolved documentation gap is counted as complete.

## 20. Known gaps at design approval

| Gap | Required resolution |
| --- | --- |
| 92 ambiguous bulk save/delete operation mentions | Obtain the complete official contract or verify with Billy in the dedicated organisation |
| No documented webhook found | Continue official and interface discovery; do not invent a tool |
| Field-level write forms | Map and test every field and validation |
| Authentication transitions | Test headless login, persisted session, credential and TOTP resolution, expiry, reauthentication, challenge errors, switching, and logout |
| Account menu | Complete live discovery |
| Daybook editor | Complete live discovery and write tests |
| Plan-gated workflows | Obtain suitable test access or Billy-supported sandbox |
| Some settings | Complete field-level discovery and tests |
| Irreversible actions | Obtain a safe supported test path |
| Vision evidence pipeline | Implement rendered-frame capture, vision review, evidence indexing, and purge verification |

Every unresolved gap remains visible and blocks the relevant completeness claim.

## 21. Approved decisions

1. One Python FastMCP stdio server.
2. Explicit `api_*` and `ui_*` lanes with shared `auth_*`.
3. The interface lane must reach full API parity before adding UI-only features.
4. Dedicated persistent Chrome profile owned by the MCP.
5. Every browser is headless; the project never opens, raises, focuses, or manipulates a desktop window.
6. Autonomous preview and execute for writes, with no mandatory human approval.
7. Exact file and destination binding.
8. Official documentation is the API contract.
9. Playwright headless page objects and workflow state machines with no native desktop automation.
10. Fail closed on interface drift.
11. Billy-only API egress and restricted browser egress.
12. Exact partner hosts temporarily allowed only for explicitly requested Billy workflows.
13. No telemetry, shell execution, dynamic code, secret logging, generic browser controls, or stubs.
14. Dedicated non-production verification before live use.
15. Manifest-driven completeness with no early completeness claim.
16. Grok CLI performs implementation grunt work under Codex orchestration and review.
17. Every UI workflow requires DOM assertions, independent read-back, and agent vision; no UI row is green without `vision_verified`.
18. UI write tests capture initial, completed-form, submitted-result, and cleaned-up frames.
19. Non-production frames are ephemeral and purged; production runtime persists no visual or browser trace artifact.

## 22. Document control

This document is the implementation contract. A code change that contradicts it requires an explicit design revision.

The next required artifact is the detailed implementation plan. Implementation starts only after that plan is reviewed.
