"""Offline contracts for non-sensitive vision evidence helpers."""

from __future__ import annotations

import json
from pathlib import Path

from billy_mcp.vision_evidence import (
    is_outside_repository,
    mark_purge_verified,
    owner_only_frame_dir,
    purge_frame_dir,
    qualifies_for_coverage_vision,
    write_live_pending_unless_accepted,
    write_vision_record,
)


def test_write_vision_record_has_no_frame_bytes(tmp_path: Path) -> None:
    destination = tmp_path / "record.json"
    record = write_vision_record(
        destination,
        workflow_ref="auth.login.ready",
        assertion_refs=["assert_ready"],
        second_interface_ref="profile_b",
        reviewer_verdict="pending_review",
    )
    payload = json.loads(destination.read_text(encoding="utf-8"))
    assert record.purge_verified is False
    assert "screenshot" not in payload
    assert "png" not in payload
    assert payload["frame_paths_were_outside_repo"] is True
    assert payload["workflow_ref"] == "auth.login.ready"
    assert payload["second_interface_ref"] == "profile_b"


def test_purge_frame_dir_and_mark_verified(tmp_path: Path) -> None:
    frames = owner_only_frame_dir(base=tmp_path / "vision-tmp")
    (frames / "a.png").write_bytes(b"fake-png")
    assert frames.exists()
    assert purge_frame_dir(frames) is True
    record_path = tmp_path / "record.json"
    write_vision_record(
        record_path,
        workflow_ref="auth.login.ready",
        assertion_refs=["a"],
        second_interface_ref="b",
        purge_verified=False,
    )
    verified = mark_purge_verified(record_path)
    assert verified.purge_verified is True
    assert json.loads(record_path.read_text(encoding="utf-8"))["purge_verified"] is True


def test_live_pending_binds_run_id_and_does_not_overwrite_accept(tmp_path: Path) -> None:
    destination = tmp_path / "ui_organizations_writes.json"
    accepted = write_vision_record(
        destination,
        workflow_ref="ui.parity.organizations.update",
        assertion_refs=["live"],
        second_interface_ref="fresh-session-input-name-phone",
        reviewer_verdict="accept",
        run_id="0937a009bf7e496ca2ce15a8af313868",
        purge_verified=True,
        author="independent_review",
    )
    assert qualifies_for_coverage_vision(accepted) is True
    kept = write_live_pending_unless_accepted(
        destination,
        workflow_ref="ui.parity.organizations.update",
        assertion_refs=["new-live"],
        second_interface_ref="fresh-session-input-name-phone",
        run_id="ffffffffffffffffffffffffffffffff",
    )
    assert kept.run_id == "0937a009bf7e496ca2ce15a8af313868"
    assert kept.author == "independent_review"
    assert kept.reviewer_verdict == "accept"
    pending_path = tmp_path / "pending.json"
    pending = write_live_pending_unless_accepted(
        pending_path,
        workflow_ref="ui.parity.organizations.update",
        assertion_refs=["live"],
        second_interface_ref="fresh-session-input-name-phone",
        run_id="aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
    )
    assert pending.author == "live_test"
    assert pending.reviewer_verdict == "pending_review"
    assert pending.run_id == "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
    assert qualifies_for_coverage_vision(pending) is False


def test_is_outside_repository(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    outside = tmp_path / "outside" / "frame.png"
    outside.parent.mkdir()
    outside.write_bytes(b"x")
    assert is_outside_repository(outside, repo) is True
    inside = repo / "tracked.png"
    inside.write_bytes(b"y")
    assert is_outside_repository(inside, repo) is False
