from __future__ import annotations

from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest

from billy_mcp.confirmations import (
    MAX_TICKET_TTL,
    ConfirmationBinding,
    ConfirmationFailure,
    ConfirmationStore,
)
from billy_mcp.models import StableErrorCode


class Clock:
    def __init__(self) -> None:
        self.now = datetime(2026, 7, 29, tzinfo=UTC)

    def __call__(self) -> datetime:
        return self.now


def binding(**changes: object) -> ConfirmationBinding:
    values: dict[str, object] = {
        "tool": "api_files_upload_execute",
        "organization_id": "org-1",
        "target": {"id": "target-1"},
        "request": {"metadata": {"b": 2, "a": 1}},
        "expected_effect_state": {"state": "draft"},
        "file_path": Path("/tmp/upload.pdf"),
        "file_digest": "a" * 64,
        "destination_url": "https://Example.test:443/submit?x=1",
    }
    values.update(changes)
    return ConfirmationBinding.model_validate(values)


def test_ticket_has_256_bit_entropy_and_canonical_binding() -> None:
    store = ConfirmationStore()
    first = store.issue(binding())
    second = store.issue(binding())

    assert len(first.value) >= 43
    assert first.value != second.value
    equivalent = binding(request={"metadata": {"a": 1, "b": 2}})
    assert store.consume(first.value, equivalent) == binding()


@pytest.mark.parametrize(
    ("changes", "expected"),
    [
        ({"tool": "api_other_execute"}, StableErrorCode.CONFIRMATION_MISMATCH),
        ({"target": {"id": "other"}}, StableErrorCode.CONFIRMATION_MISMATCH),
        ({"request": {"changed": True}}, StableErrorCode.CONFIRMATION_MISMATCH),
        ({"expected_effect_state": {"state": "approved"}}, StableErrorCode.CONFIRMATION_MISMATCH),
        ({"file_digest": "b" * 64}, StableErrorCode.CONFIRMATION_MISMATCH),
        ({"file_path": Path("/tmp/other.pdf")}, StableErrorCode.CONFIRMATION_MISMATCH),
        ({"destination_url": "https://example.test/other"}, StableErrorCode.CONFIRMATION_MISMATCH),
    ],
)
def test_ticket_rejects_any_binding_change(
    changes: dict[str, object], expected: StableErrorCode
) -> None:
    store = ConfirmationStore()
    ticket = store.issue(binding())

    with pytest.raises(ConfirmationFailure) as failure:
        store.consume(ticket.value, binding(**changes))

    assert failure.value.error.code is expected


def test_ticket_rejects_tampering_replay_and_expiry() -> None:
    clock = Clock()
    store = ConfirmationStore(clock)
    ticket = store.issue(binding())

    with pytest.raises(ConfirmationFailure) as tampered:
        store.consume(f"{ticket.value}x", binding())
    assert tampered.value.error.code is StableErrorCode.CONFIRMATION_INVALID

    store.consume(ticket.value, binding())
    with pytest.raises(ConfirmationFailure) as replay:
        store.consume(ticket.value, binding())
    assert replay.value.error.code is StableErrorCode.CONFIRMATION_CONSUMED

    expired_ticket = store.issue(binding(), ttl=MAX_TICKET_TTL)
    clock.now += timedelta(minutes=5)
    with pytest.raises(ConfirmationFailure) as expired:
        store.consume(expired_ticket.value, binding())
    assert expired.value.error.code is StableErrorCode.CONFIRMATION_EXPIRED


def test_expired_bindings_and_replay_markers_are_pruned_without_losing_live_errors() -> None:
    clock = Clock()
    store = ConfirmationStore(clock)
    consumed_ticket = store.issue(binding())
    expired_ticket = store.issue(binding(tool="api_contacts_create_execute"))

    store.consume(consumed_ticket.value, binding())
    consumed = store.terminal_failure(consumed_ticket.value)
    assert consumed is not None
    assert consumed.code is StableErrorCode.CONFIRMATION_CONSUMED

    clock.now += MAX_TICKET_TTL
    expired = store.terminal_failure(expired_ticket.value)
    assert expired is not None
    assert expired.code is StableErrorCode.CONFIRMATION_EXPIRED

    fresh_ticket = store.issue(binding(tool="api_accounts_create_execute"))
    assert store.terminal_failure(consumed_ticket.value) is None
    assert store.terminal_failure(expired_ticket.value) is None
    assert (
        store.consume(
            fresh_ticket.value,
            binding(tool="api_accounts_create_execute"),
        ).tool
        == "api_accounts_create_execute"
    )
