"""Live UI write tests must not self-approve vision or purge frames first."""

from __future__ import annotations

from pathlib import Path

import pytest

from billy_mcp.vision_evidence import (
    VisionEvidenceRecord,
    mark_purge_verified,
    qualifies_for_coverage_vision,
    write_vision_record,
)

_REPO = Path(__file__).resolve().parents[2]
_CONTACTS_VISION_RECORD = (
    _REPO / "coverage" / "vision-records" / "ui_contacts_writes.json"
)
_CONTACTS_FRAME_RUN_ID = "3d5b151dfd5342258f8734373597f8c1"
_WRITE_LIVE_TESTS = (
    _REPO / "tests/live/test_ui_contacts_writes.py",
    _REPO / "tests/live/test_ui_bills_writes.py",
    _REPO / "tests/live/test_ui_files_writes.py",
    _REPO / "tests/live/test_ui_organizations_writes.py",
    _REPO / "tests/live/test_ui_invoices_writes.py",
    _REPO / "tests/live/test_ui_products_writes.py",
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


def test_contacts_write_record_does_not_qualify_while_live_test_pending() -> None:
    record = VisionEvidenceRecord.model_validate_json(
        _CONTACTS_VISION_RECORD.read_text(encoding="utf-8")
    )
    if record.author == "live_test":
        assert record.reviewer_verdict == "pending_review"
        assert record.purge_verified is False
        assert qualifies_for_coverage_vision(record) is False
        return
    assert record.author == "independent_review"
    assert record.reviewer_verdict == "accept"
    assert record.purge_verified is True
    assert record.run_id == _CONTACTS_FRAME_RUN_ID
    assert qualifies_for_coverage_vision(record) is True


def test_independent_accept_and_purge_qualifies_for_coverage_vision(tmp_path: Path) -> None:
    destination = tmp_path / "ui_contacts_writes.json"
    write_vision_record(
        destination,
        workflow_ref="ui.parity.contacts.create",
        assertion_refs=[
            "tests/live/test_ui_contacts_writes.py::"
            "test_ui_contacts_create_update_delete_via_call_tool"
        ],
        second_interface_ref="create_server_readback_plus_third_profile",
        reviewer_verdict="accept",
        run_id=_CONTACTS_FRAME_RUN_ID,
        purge_verified=False,
        author="independent_review",
    )
    pending = VisionEvidenceRecord.model_validate_json(destination.read_text(encoding="utf-8"))
    assert qualifies_for_coverage_vision(pending) is False
    verified = mark_purge_verified(destination)
    assert qualifies_for_coverage_vision(verified) is True
