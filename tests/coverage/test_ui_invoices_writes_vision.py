"""Pending invoice-write vision does not qualify until accept and purge."""

from __future__ import annotations

from pathlib import Path

from billy_mcp.vision_evidence import (
    VisionEvidenceRecord,
    qualifies_for_coverage_vision,
)

ROOT = Path(__file__).resolve().parents[2]
_VISION_RECORD = ROOT / "coverage" / "vision-records" / "ui_invoices_writes.json"
_FRAME_RUN_ID = "60b6d620772644f3bca9609c8ae53846"
_FRAME_DIR = Path.home() / ".local" / "share" / "billy-mcp" / "vision-tmp" / f"run-{_FRAME_RUN_ID}"
_FRAME_NAMES = (
    "01_before.png",
    "02_before_submit.png",
    "03_after_create.png",
    "04_after_update.png",
    "05_after_delete.png",
)
_GROK_REVIEW = ".fractal/main.billy_complete/tmp/grok-review.md"


def test_pending_invoice_write_record_does_not_qualify_until_accept_and_purge() -> None:
    record = VisionEvidenceRecord.model_validate_json(_VISION_RECORD.read_text(encoding="utf-8"))
    if record.author == "live_test":
        assert record.reviewer_verdict == "pending_review"
        assert record.purge_verified is False
        assert record.run_id == _FRAME_RUN_ID
        assert qualifies_for_coverage_vision(record) is False
        assert _FRAME_DIR.is_dir()
        for name in _FRAME_NAMES:
            assert (_FRAME_DIR / name).is_file()
        return
    assert record.author == "independent_review"
    assert record.reviewer_verdict == "accept"
    assert record.purge_verified is True
    assert record.run_id == _FRAME_RUN_ID
    assert _GROK_REVIEW in record.assertion_refs
    assert qualifies_for_coverage_vision(record) is True
    assert _FRAME_DIR.exists() is False
