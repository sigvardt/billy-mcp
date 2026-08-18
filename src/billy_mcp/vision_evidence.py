"""Non-sensitive vision review records and owner-only frame purge helpers.

Production auth and UI tools never persist screenshots, HAR files, or traces.
Live qualification may capture frames in owner-only temporary storage, write a
redacted review record, and delete the frames after review.
"""

from __future__ import annotations

import json
import shutil
import uuid
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


class VisionEvidenceRecord(BaseModel):
    """Durable non-sensitive vision review record; never embeds frame bytes."""

    model_config = ConfigDict(extra="forbid", strict=True)

    workflow_ref: str = Field(min_length=1)
    run_id: str = Field(min_length=1)
    assertion_refs: list[str] = Field(min_length=1)
    second_interface_ref: str = Field(min_length=1)
    reviewer_verdict: Literal["pending_review", "accept", "reject"]
    timestamp: str = Field(min_length=1)
    purge_verified: bool
    frame_paths_were_outside_repo: bool = True
    author: Literal["live_test", "independent_review"] = "independent_review"


def owner_only_frame_dir(base: Path | None = None) -> Path:
    """Return a fresh owner-only directory for temporary headless frames."""

    root = (base or (Path.home() / ".local" / "share" / "billy-mcp" / "vision-tmp")).expanduser()
    root.mkdir(parents=True, exist_ok=True)
    destination = root / f"run-{uuid.uuid4().hex}"
    destination.mkdir(parents=True, exist_ok=False)
    try:
        destination.chmod(0o700)
    except OSError:
        pass
    return destination


def write_live_pending_unless_accepted(
    destination: Path,
    *,
    workflow_ref: str,
    assertion_refs: list[str],
    second_interface_ref: str,
    run_id: str,
) -> VisionEvidenceRecord:
    """Write a live pending record. Keep an accepted purged review in place."""

    if destination.is_file():
        current = VisionEvidenceRecord.model_validate_json(destination.read_text(encoding="utf-8"))
        if qualifies_for_coverage_vision(current):
            return current
    return write_vision_record(
        destination,
        workflow_ref=workflow_ref,
        assertion_refs=assertion_refs,
        second_interface_ref=second_interface_ref,
        reviewer_verdict="pending_review",
        run_id=run_id,
        author="live_test",
    )


def write_vision_record(
    destination: Path,
    *,
    workflow_ref: str,
    assertion_refs: list[str],
    second_interface_ref: str,
    reviewer_verdict: Literal["pending_review", "accept", "reject"] = "pending_review",
    run_id: str | None = None,
    purge_verified: bool = False,
    author: Literal["live_test", "independent_review"] = "independent_review",
) -> VisionEvidenceRecord:
    """Write one redacted vision record to disk (JSON, no frames)."""

    if author == "live_test" and reviewer_verdict == "accept":
        raise ValueError("independent review must write accept; a live test cannot")
    record = VisionEvidenceRecord(
        workflow_ref=workflow_ref,
        run_id=run_id or uuid.uuid4().hex,
        assertion_refs=list(assertion_refs),
        second_interface_ref=second_interface_ref,
        reviewer_verdict=reviewer_verdict,
        timestamp=datetime.now(UTC).replace(microsecond=0).isoformat(),
        purge_verified=purge_verified,
        frame_paths_were_outside_repo=True,
        author=author,
    )
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(record.model_dump_json(indent=2) + "\n", encoding="utf-8")
    try:
        destination.chmod(0o600)
    except OSError:
        pass
    return record


def purge_frame_dir(frame_dir: Path) -> bool:
    """Delete a temporary frame directory. Return True when no path remains."""

    if frame_dir.exists():
        shutil.rmtree(frame_dir, ignore_errors=True)
    return not frame_dir.exists()


def mark_purge_verified(record_path: Path) -> VisionEvidenceRecord:
    """Set purge_verified on an existing record after frames are deleted."""

    payload: dict[str, Any] = json.loads(record_path.read_text(encoding="utf-8"))
    payload["purge_verified"] = True
    record = VisionEvidenceRecord.model_validate(payload)
    record_path.write_text(record.model_dump_json(indent=2) + "\n", encoding="utf-8")
    return record


def qualifies_for_coverage_vision(record: VisionEvidenceRecord) -> bool:
    """True only after an independent review accepts and purge is verified."""

    return (
        record.author == "independent_review"
        and record.reviewer_verdict == "accept"
        and record.purge_verified is True
    )


def is_outside_repository(path: Path, repository_root: Path) -> bool:
    """Return True when path does not resolve under the git worktree root."""

    try:
        path.resolve().relative_to(repository_root.resolve())
    except ValueError:
        return True
    return False
