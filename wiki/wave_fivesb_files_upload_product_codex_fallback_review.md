---
name: wave_fivesb_files_upload_product_codex_fallback_review
title: Wave-5s-B files upload product Codex fallback review
desc: Non-authoritative static Codex Power re-review of Wave-5s-B files upload from root baseline 98484f3 through repair 86ecb89; fails on an identical-byte symlink containment TOCTOU.
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
  - git commit 86ecb89
  - git commit f3ef8dc
created: 2026-07-30T18:40:25Z
updated: 2026-07-30T18:49:41Z
---

# Wave-5s-B files upload product Codex fallback review

## Scope, authority, and provenance

**Fallback verdict: FAIL.** This is an offline, static Codex Power re-review
of the Wave-5s-B files-upload product from root baseline `98484f3`, including
the exact-byte repair merged as `86ecb89`. The repair correctly prevents an
ordinary post-check replacement from sending bytes whose SHA-256 differs from
the ticket digest. It does not close the same-window replacement of the checked
path with a symlink to an outside-root file whose bytes have that same digest.
That path succeeds and makes one mocked POST, contrary to the approved design's
execute-time configured-root and symlink-containment requirement (§8.4).

This is deliberately a non-authoritative fallback. It cannot replace the
mandatory Grok product audit, does not grant Grok acceptance, and makes no claim
about live API behaviour, UI, vision, bulk operations, coverage completeness,
or overall product completion. Evidence is restricted to committed source and
focused tests plus one temporary-directory `httpx.MockTransport` reproduction.
No credential, browser, API traffic, persistent test data, external research,
or retained raw test material was used.

The designated Grok route failed authentication before it edited or reviewed
product material. Commit `f3ef8dc` records `Not signed in` during its research
step and says the later product-review steps did not run. Its name-status has
node-orchestration material only: it contains no `src/`, `tests/`, coverage,
inventory, or wiki product edit. This verifies the required pre-edit failure
under [[review_provenance_rules]]. The fallback is therefore attributed only to
Codex Power and leaves the mandatory Grok gate open.

The original product baseline is `98484f3`; `86ecb89` adds only the current
digest comparison in `file_upload_writes.py` and its focused regression test to
that reviewed upload slice. This page was updated after merging that repair; it
does not present this branch's documentation as product evidence.

## Contract reviewed

The files-upload contract freezes a raw-binary `POST /v2/files`, one
`files.create` inventory alias, exactly two tools, documented allowlisted
headers, and a preview/execute ticket carrying canonical path and SHA-256
digest (wiki/wave_fivesb_files_upload_research.md:48-79). The product-ready
handoff additionally requires repeat regular-file, size, mtime, and digest
validation at execute (wiki/wave_fivesb_files_upload_product_ready_research.md:74-102).
Approved design §§8.3–8.4 requires file identity in every upload ticket, then
repeat canonical-path, configured-root, regular-file, size, mtime, and SHA-256
validation at execute, rejecting both a changed file and a symlink escape.

## Static findings

| ID | Severity | Finding and evidence | Disposition |
| --- | --- | --- | --- |
| F-01 | **blocker** | `execute()` obtains and compares a fresh root-contained identity at `file_upload_writes.py:253-262`, then separately follows `prepared.identity.path` with `read_bytes()` at :263-264. The repair checks the later buffer's SHA-256 at :270-274, so a different-byte substitution is rejected. It cannot show that a same-digest buffer came from the checked root-contained file. A temporary-directory, in-process `FileUploadService` reproduction replaced the regular file only from the `read_bytes()` hook, after the identity check, with a symlink to an outside-root regular file containing the same synthetic bytes. The call returned `FileUploadExecuteSuccess` and made exactly one `httpx.MockTransport` POST. | Exact bytes-versus-ticket-digest semantics now pass for this case, but execute-time configured-root and symlink containment still fail. The design requires rejection of any symlink escape, including one with matching bytes. |
| F-02 | none | The preview and execute models forbid extra fields and use strict validation; FastMCP signatures use `StrictStr`/`StrictBool`, while execute accepts only `confirmation_ticket` (`file_upload_writes.py:34-94,300-350`). The focused registry test requires exactly the two named tools, `additionalProperties: false`, and the expected fields; invalid types, unknown fields, and CR/LF header values fail before HTTP (`tests/api/test_file_upload_writes.py:104-160`). | Static strict-input boundary passes. |
| F-03 | superseded by F-01 | Preview accepts only relative paths, resolves under canonical configured roots, rejects non-regular files, and hashes the resolved file (`file_upload_writes.py:71-78,353-394`; `config.py:37-60`). Focused tests reject missing, outside, non-regular, and pre-execute symlink-escape paths without HTTP (`tests/api/test_file_upload_writes.py:225-253,324-419`). Those checks do not protect the post-check identical-byte symlink replacement in F-01. | Normal-path containment is present; the required execute-time containment property is not. |
| F-04 | none | Preview binds execute tool, organisation, canonical request, expected effect, canonical path, and digest (`file_upload_writes.py:181-210`). `ConfirmationStore` uses 32 random bytes, a five-minute maximum TTL, and one lock to atomically expire, compare, and consume tickets (`confirmations.py:19-21,115-183`). Execute consumes and discards prepared metadata before local or HTTP work (`file_upload_writes.py:230-251`). Focused tests cover tampering, expiry, cross-executor use, replay, and no resulting write (`tests/api/test_file_upload_writes.py:422-500`; `tests/unit/test_confirmations.py:40-120`). | Ticket binding, expiry, and replay closure pass statically. |
| F-05 | none | `post_file()` accepts bytes and named header arguments only, validates caller-controlled values, constructs only documented headers, and performs one `POST` with no retry loop (`client.py:130-188,221-227`). The URL builder fixes the official v2 base and rejects absolute, query-bearing, traversal, and duplicate-prefix paths (`client.py:190-199`); configuration restricts the base URL to that value (`config.py:13,29-37`). Unit tests assert raw body, headers, optional-header omission, one 503 attempt, and CR/LF rejection before a request (`tests/unit/test_client.py:90-173`). | Header injection, base-URL lock, raw-body construction, and one-upload attempt pass statically. |
| F-06 | none | Preview only resolves and records metadata; it does not call the client, and tests assert no request for preview and validation failures (`file_upload_writes.py:172-220`; `tests/api/test_file_upload_writes.py:138-160,205-253`). Ticket consumption and prepared-metadata discard happen before every revalidation and before the single post, so an identity or response failure closes that operation (`file_upload_writes.py:245-284`). Successful response roots are validated and recursively redacted, including `downloadUrl` (`file_upload_writes.py:420-463`; `redaction.py:48-75`); the focused success test asserts that redaction (`tests/api/test_file_upload_writes.py:256-297`). | No-preview HTTP, response-failure closure, and response redaction pass statically. |
| F-07 | medium | The repair's new race test changes the file contents from the `read_bytes()` hook and asserts `FILE_CHANGED` with zero HTTP (`tests/api/test_file_upload_writes.py:355-379`). The existing symlink test changes the path before execute begins (`:401-419`). Neither replaces the checked pathname with an outside-root symlink containing identical ticketed bytes in the exact identity-to-read interval. | The focused suite misses F-01. Add a deterministic same-digest symlink-race regression that asserts `FILE_NOT_ALLOWED` and zero HTTP. |
| F-08 | none | The production server imports and calls `register_file_upload_tools()` (`server.py:40,106-120`). The focused registry suite includes exactly `api_files_upload_preview` and `api_files_upload_execute` in the Wave-5s-B set (`tests/unit/test_coverage_server.py:329-334,407-514`). | Tool registration and the two-tool boundary pass statically. |

## Replacement-window test method

The F-01 check was wholly local and non-live. A synthetic regular file under a
temporary configured root was previewed. The test hook ran only when the
unchanged production code reached `Path.read_bytes()`, after the successful
execute-time identity calculation. It atomically replaced the checked pathname
with a symlink to an outside-root synthetic regular file containing the same
pre-preview bytes. The subsequent pathname read followed that symlink; its
digest equalled the ticket digest, so the current repair permitted one mocked
POST and mapped the normal success response.

No evidence bytes, ticket, path, or response data was retained. This test does
not make a network request or use a credential. It establishes the code-path
property: hashing an in-memory buffer can prove its ticket digest, but cannot
prove that the buffer was read from a path that remained inside a configured
root after the preceding identity check.

The repair must acquire the file via a configured-root-aware, no-follow
descriptor traversal; validate regular-file metadata from that descriptor; read
and hash the exact buffer from the same descriptor; compare it to the ticket;
and send that buffer. It also needs the deterministic regression described in
F-07. This review makes no source or test change.

## Focused offline verification

The focused non-live upload set passed: **59 passed** for
`tests/api/test_file_upload_writes.py`, `tests/unit/test_client.py`,
`tests/unit/test_confirmations.py`, and `tests/unit/test_coverage_server.py`
with `-m 'not live and not vision'`. The node-required non-live suite also
passed: **1,221 passed**. Both runs use local transports and temporary test
paths; neither result negates F-01 because the committed race test covers a
different-byte swap, not the same-digest symlink escape reproduced here.

## Fallback verdict and required gate

**FAIL — do not accept the Wave-5s-B product on this fallback review.** The
digest repair closes the changed-bytes race, but an identical-byte symlink can
still escape a configured root in the interval between the current identity
calculation and `read_bytes()`. The other listed static safety boundaries are
positively evidenced, but they do not compensate for this §8.4 blocker.

The required product gate is a containment repair plus a focused same-digest
symlink-window regression, followed by the mandatory Grok audit. This document
remains supplemental only: it supplies neither Grok acceptance nor a live, UI,
vision, bulk, coverage-completeness, or overall-completion assertion.
