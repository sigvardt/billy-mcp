# Plan: research79 Wave-5s-B files upload contract

## Goal

Freeze cited offline contract for ticketed binary `POST /files` so Codex Power
can implement `api_files_upload_preview` / `api_files_upload_execute` after
Wave-5s-A product IR, without greening coverage from research alone.

## Done when

1. Official docs re-fetched; body fingerprint recorded.
2. Unauth method matrix for files (+ residual controls) written under `tmp/`.
3. `tmp/grok-research.md` replaced with research79 brief.
4. Durable wiki page `wiki/wave_fivesb_files_upload_research.md` written.
5. Memory state points at Wave-5s-B as next residual product after 5s-A IR.
6. No coverage greening; no headed browser; no disposable records.

## Work

1. Read state, residual ranking, prior research78, inventory dual-row rules.
2. Fetch https://www.billy.dk/api/ and compare MD5/ETag to research78.
3. Extract files Supports table + Creating and using attachments narrative.
4. Probe locked base `https://api.billysbilling.com/v2` without credentials.
5. Cross-check design §8.4, ConfirmationBinding file fields, upload roots.
6. Write brief + wiki + memory; radio status.

## Non-goals

Product implementation, product IR, live tests, UI, bulk resolution.

## Post-Mortem

Completed: the cited binary-upload research handoff was committed at `4c1ce59`,
including the documentation fingerprint, unauthenticated method matrix, and
dual-row ownership boundary. The non-live root checks pass after the later
invoice-log integration.

Deviation: the designated Grok research reviewer failed authentication before
performing any review. Its uncommitted draft was discarded rather than treated
as Grok evidence, and an explicitly labelled Codex Power fallback reviewer was
launched. That fallback cannot satisfy the final mandatory Grok audit.

Cleanup: no upload implementation, live request, browser evidence, credential,
or coverage greening was introduced. The next unresolved coverage slice is the
ticketed files-upload product, after the fallback review is read and integrated.
