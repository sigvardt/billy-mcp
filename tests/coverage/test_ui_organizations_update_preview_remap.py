"""Pending org-write vision does not qualify until accept and purge."""

from __future__ import annotations

from pathlib import Path

from billy_mcp.vision_evidence import (
    VisionEvidenceRecord,
    qualifies_for_coverage_vision,
)

ROOT = Path(__file__).resolve().parents[2]
_VISION_RECORD = ROOT / "coverage" / "vision-records" / "ui_organizations_writes.json"
_FRAME_RUN_ID = "0937a009bf7e496ca2ce15a8af313868"
_LIVE_RUN_ID = "affdb4f98390481880e4bcd554ec4fd9"


def test_pending_org_write_record_does_not_qualify_until_accept_and_purge() -> None:
    record = VisionEvidenceRecord.model_validate_json(_VISION_RECORD.read_text(encoding="utf-8"))
    if record.author == "live_test":
        assert record.reviewer_verdict == "pending_review"
        assert record.purge_verified is False
        assert qualifies_for_coverage_vision(record) is False
        return
    assert record.author == "independent_review"
    assert record.reviewer_verdict == "accept"
    assert record.purge_verified is True
    assert record.run_id == _FRAME_RUN_ID
    assert _LIVE_RUN_ID in record.assertion_refs
    assert qualifies_for_coverage_vision(record) is True
