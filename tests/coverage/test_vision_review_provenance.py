"""Live UI write tests must not self-approve vision or purge frames first."""

from __future__ import annotations

from pathlib import Path

import pytest

from billy_mcp.vision_evidence import (
    VisionEvidenceRecord,
    qualifies_for_coverage_vision,
    write_vision_record,
)

_REPO = Path(__file__).resolve().parents[2]
_WRITE_LIVE_TESTS = (
    _REPO / "tests/live/test_ui_contacts_writes.py",
    _REPO / "tests/live/test_ui_bills_writes.py",
    _REPO / "tests/live/test_ui_files_writes.py",
)


def test_ui_write_live_tests_do_not_self_approve_or_purge() -> None:
    for path in _WRITE_LIVE_TESTS:
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        assert 'reviewer_verdict="accept"' not in text
        assert "reviewer_verdict='accept'" not in text
        assert "purge_frame_dir(" not in text
        assert "mark_purge_verified(" not in text


def test_live_test_cannot_write_an_accept_vision_record(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="independent review"):
        write_vision_record(
            tmp_path / "record.json",
            workflow_ref="ui.parity.contacts.create",
            assertion_refs=["test"],
            second_interface_ref="readback",
            reviewer_verdict="accept",
            author="live_test",
        )


def test_accept_from_live_test_does_not_qualify_coverage() -> None:
    record = VisionEvidenceRecord(
        workflow_ref="ui.parity.contacts.create",
        run_id="abc",
        assertion_refs=["test"],
        second_interface_ref="readback",
        reviewer_verdict="accept",
        timestamp="2026-08-16T00:00:00+00:00",
        purge_verified=True,
        author="live_test",
    )
    assert qualifies_for_coverage_vision(record) is False
