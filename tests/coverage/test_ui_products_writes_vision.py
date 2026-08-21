"""Pending product-write vision does not qualify until accept and purge."""

from __future__ import annotations

from pathlib import Path

from billy_mcp.vision_evidence import (
    VisionEvidenceRecord,
    qualifies_for_coverage_vision,
)

ROOT = Path(__file__).resolve().parents[2]
_VISION_RECORD = ROOT / "tmp" / "vision-records" / "ui_products_writes.json"
_FRAME_NAMES = (
    "01_before.png",
    "02_before_submit.png",
    "03_after_create.png",
    "04_after_delete.png",
)
_GROK_REVIEW = ".fractal/main.billy_complete/tmp/grok-review.md"


def test_pending_product_write_record_does_not_qualify_until_accept_and_purge() -> None:
    record = VisionEvidenceRecord.model_validate_json(_VISION_RECORD.read_text(encoding="utf-8"))
    frame_dir = (
        Path.home() / ".local" / "share" / "billy-mcp" / "vision-tmp" / f"run-{record.run_id}"
    )
    if record.author == "live_test":
        assert record.reviewer_verdict == "pending_review"
        assert record.purge_verified is False
        assert qualifies_for_coverage_vision(record) is False
        assert frame_dir.is_dir()
        for name in _FRAME_NAMES:
            assert (frame_dir / name).is_file()
        return
    assert record.author == "independent_review"
    assert record.reviewer_verdict == "accept"
    assert record.purge_verified is True
    assert _GROK_REVIEW in record.assertion_refs
    assert qualifies_for_coverage_vision(record) is True
    assert frame_dir.exists() is False
