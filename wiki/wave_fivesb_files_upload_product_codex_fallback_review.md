---
name: wave_fivesb_files_upload_product_codex_fallback_review
title: Wave-5s-B files upload product Codex fallback review
desc: Non-authoritative static Codex Power review of the Wave-5s-B files-upload product at root baseline 98484f3; fails on an exact-byte and symlink TOCTOU before the mandatory Grok audit.
tags: [billy, api, files, upload, review, codex, fallback, static, security]
sources:
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
  - wiki/wave_fivesb_files_upload_research.md
  - wiki/wave_fivesb_files_upload_product_ready_research.md
  - wiki/review_provenance_rules.md
  - src/billy_mcp/api/file_upload_writes.py
  - src/billy_mcp/client.py
  - src/billy_mcp/config.py
  - src/billy_mcp/confirmations.py
  - src/billy_mcp/redaction.py
  - src/billy_mcp/server.py
  - tests/api/test_file_upload_writes.py
  - tests/unit/test_client.py
  - tests/unit/test_confirmations.py
  - tests/unit/test_coverage_server.py
  - git commit 98484f3
  - git commit f3ef8dc
created: 2026-07-30T18:40:25Z
updated: 2026-07-30T18:40:25Z
---

# Wave-5s-B files upload product Codex fallback review

## Scope, authority, and provenance

**Fallback verdict: FAIL.** This is an offline, static Codex Power fallback
review of the Wave-5s-B files-upload product at root baseline `98484f3`. It
found a time-of-check/time-of-use (TOCTOU) defect: the bytes posted after an
execute-time identity check are not proved to match the ticket digest, and the
same gap permits a symlink escape after containment validation. The defect
violates the approved design's file-identity and repeat-containment requirements
(design §§8.3–8.4).

This record is deliberately non-authoritative. It cannot replace the mandatory
Grok product audit, does not grant Grok acceptance, and makes no claim about
live API behaviour, UI, vision, bulk operations, coverage completeness, or
overall product completion. Its evidence is limited to committed source and
tests plus local, temporary-directory `httpx.MockTransport` checks; it used no
credential, browser, API traffic, persistent test data, or external research.

The designated Grok route failed authentication before it could edit or review
product material. Commit `f3ef8dc` records that the attempt stopped during its
research step before subsequent product-review steps; its name-status contains
only node-orchestration material, not `src/`, `tests/`, `coverage/`, inventory,
or wiki product changes. That verifies the pre-edit failure required by
[[review_provenance_rules]]. This fallback therefore reports only its own
committed static evidence and leaves the Grok gate open.

`98484f3` is an ancestor of this review branch. `git diff --name-only
98484f3..HEAD` showed only this node's orchestration seed before this report was
written, so the reviewed product source, focused tests, registry, and contract
records are the root-baseline material rather than review-branch product edits.

## Contract reviewed

The cited files-upload research freezes a raw-binary `POST /v2/files` special
with a `files.create` inventory alias, two tools only, documented allowlisted
headers, and a preview/execute ticket carrying the canonical path and SHA-256
digest (wiki/wave_fivesb_files_upload_research.md:48-79). The product-ready
handoff adds repeat regular-file, size, mtime, and digest validation at execute
(wiki/wave_fivesb_files_upload_product_ready_research.md:74-102). These agree
with the approved design: every ticket binds a file identity (§8.3), while
preview and execute must both resolve the canonical real path under a configured
root, validate a regular file, size, mtime, and SHA-256, and reject a changed
file or symlink escape (§8.4).

## Static findings

| ID | Severity | Finding and evidence | Disposition |
| --- | --- | --- | --- |
| F-01 | **blocker** | `execute()` computes and compares a fresh `_FileIdentity` at `file_upload_writes.py:253-262`, then separately calls `prepared.identity.path.read_bytes()` at :263-269 and posts those unchecked bytes at :270-278. The digest helper hashes a different file read (`_identity_for_path`, :358-380). A local temporary-directory reproduction replaced the regular file *after* `_identity_beneath_roots()` returned and *before* `read_bytes()`; execution succeeded and the one mocked POST carried the replacement bytes rather than the ticketed bytes. A second reproduction made that post-check replacement a symlink to a file outside the configured root; execution again succeeded and posted the outside-root bytes. No live request was made. | Fails exact bytes-versus-ticket-digest binding and execute-time configured-root/symlink containment. This is a product blocker. |
| F-02 | none | The preview and execute models are strict (`extra="forbid"`, `strict=True`) and the FastMCP signatures use `StrictStr`/`StrictBool`; execute accepts only `confirmation_ticket` (`file_upload_writes.py:34-94,305-345`). The focused registry test requires exactly the two named tools, `additionalProperties: false`, and the expected input fields; invalid types, unknown fields, and CR/LF header values fail before HTTP (`tests/api/test_file_upload_writes.py:104-160`). | Static input boundary passes. |
| F-03 | superseded by F-01 | In the non-racing case, preview accepts only relative paths, resolves them under configured canonical roots, rejects non-regular files, and hashes the resolved file (`file_upload_writes.py:71-78,348-389`; `config.py:37-60`). Focused tests cover missing, outside, non-regular, and pre-execute symlink-escape paths without an HTTP request (`tests/api/test_file_upload_writes.py:225-253,324-392`). Those checks do not protect the post-check replacement window demonstrated in F-01. | The normal-path logic is present, but the required execute-time containment property does not hold. |
| F-04 | none | Preview binds the execute tool, organisation, canonical request, expected effect, canonical path, and digest (`file_upload_writes.py:181-210`). `ConfirmationStore` uses 32 random bytes, a five-minute maximum TTL, and one lock to atomically expire, compare, and consume a ticket (`confirmations.py:19-21,115-183`). The executor consumes the binding before file or HTTP work and drops prepared metadata (`file_upload_writes.py:230-251`). Focused tests cover tampering, expiry, cross-executor use, replay, and no resulting write (`tests/api/test_file_upload_writes.py:395-473`; `tests/unit/test_confirmations.py:75-114`). | Ticket binding, expiry, and replay closure pass statically. |
| F-05 | none | `post_file()` accepts bytes plus named header arguments only, validates caller-controlled header values, constructs only documented headers, and uses a single `POST` to the fixed `/files` path without a retry loop (`client.py:130-188,221-227`). The URL builder fixes the official v2 base and rejects absolute, query-bearing, traversal, and duplicate-prefix paths (`client.py:190-199`); configuration restricts the base URL to that value (`config.py:13,29-37`). Unit tests assert raw body, documented headers, omission of optional headers, one attempt on 503, and CR/LF rejection before a request (`tests/unit/test_client.py:90-173`). | Header injection, base-URL lock, raw-body construction, and one-upload attempt pass statically. |
| F-06 | none | Preview itself only resolves and records metadata; it does not call the client (`file_upload_writes.py:172-220`), and the focused tests assert no request for preview and validation failures (`tests/api/test_file_upload_writes.py:138-160,205-253`). The ticket is consumed before revalidation and HTTP work, so failures close the prepared operation. A local mock-503 check verified that a response failure returns the typed error, consumes the ticket, and prevents a second request on replay. Successful response roots are validated and recursively redacted, including `downloadUrl` (`file_upload_writes.py:415-458`; `redaction.py:48-75`); the focused test asserts that redaction (`tests/api/test_file_upload_writes.py:256-297`). | No-preview HTTP, response-failure closure, and response redaction pass statically. |
| F-07 | medium | The committed identity-change tests mutate the file or symlink **before** `execute()` starts (`tests/api/test_file_upload_writes.py:324-392`). They do not force a replacement after the execute-time identity calculation and before `read_bytes()`, so the F-01 defect passed the focused suite. | Add a deterministic regression test for both byte replacement and symlink replacement in that exact interval as part of the repair. |
| F-08 | none | The production server imports and calls `register_file_upload_tools()` (`server.py:40,106-120`). The focused server registry suite includes exactly `api_files_upload_preview` and `api_files_upload_execute` in the Wave-5s-B set (`tests/unit/test_coverage_server.py:329-334,407-504`), while the inventory checks preserve the one special family and forbid a separate `api_files_create*` tool (`tests/coverage/test_coverage_inventory.py:124-143,270-294`). | Tool registration and alias boundary pass statically. |

## Replacement-window test method

The two F-01 checks were deliberately local and non-live. Each used a temporary
configured root, a synthetic in-process client, and `httpx.MockTransport`. A
test hook changed the file only after the production execute function had
obtained its current identity, then allowed the unchanged production
`read_bytes()` and client call to run. The regular-file variant posted the new
contents; the symlink variant posted bytes reached outside the root. Both
returned the normal mapped success result and made exactly one mock request.

This is not merely a test-order concern. The current implementation's hash is
over the pre-read file while the request body is from a later pathname read.
The repair must obtain a no-follow descriptor through the configured root,
validate regular-file metadata, read and hash from that same descriptor, compare
the resulting digest to the ticket, and send that exact in-memory byte buffer.
It also needs the deterministic regression checks described in F-07. The parent
owns that repair; this review made no source or test change.

## Focused offline verification

The focused non-live suite passed: `58 passed` for
`tests/api/test_file_upload_writes.py`, `tests/unit/test_client.py`,
`tests/unit/test_confirmations.py`, and `tests/unit/test_coverage_server.py`
with `-m 'not live and not vision'`. Those tests use local mock transports and
temporary paths. Their passing status does not negate F-01 because the
post-identity replacement interval was not a committed regression case.

## Fallback verdict and required gate

**FAIL — do not accept the Wave-5s-B product on this fallback review.** The
ticketed upload can send bytes that differ from its ticket digest and can read
outside a configured root if replacement occurs in the execute-time gap. The
remaining static safety boundaries above are positively evidenced, but they do
not compensate for that blocker.

The required next product gate is a source repair plus focused regression tests,
followed by the mandatory Grok audit. This document remains supplemental only:
it supplies neither Grok acceptance nor any live, UI, vision, bulk,
coverage-completeness, or overall-completion assertion.
