from __future__ import annotations

import json
import stat
from collections.abc import Callable
from pathlib import Path

import httpx
import pytest
from pydantic import ValidationError

from billy_mcp.live_probe import (
    API_BASE_URL,
    CandidateKind,
    CandidateObservationState,
    CleanupLedger,
    CleanupVerificationFailed,
    LiveProbeConfig,
    LiveProbeRunner,
    PersistentDataBlocked,
    ProbeStatus,
    TrackedDisposableResource,
    research88_candidates,
)


def _config(tmp_path: Path, **overrides: object) -> LiveProbeConfig:
    repository_root = tmp_path / "repository"
    settings: dict[str, object] = {
        "repository_root": repository_root,
        "evidence_directory": tmp_path / "evidence",
    }
    settings.update(overrides)
    return LiveProbeConfig.model_validate(settings)


def _forbid_network(_: httpx.Request) -> httpx.Response:
    pytest.fail("live gate attempted an HTTP request before its safety gates passed")


def _runner(
    tmp_path: Path,
    handler: Callable[[httpx.Request], httpx.Response] = _forbid_network,
    **overrides: object,
) -> LiveProbeRunner:
    return LiveProbeRunner(_config(tmp_path, **overrides), transport=httpx.MockTransport(handler))


def _guarded_environment() -> dict[str, str]:
    return {
        "BILLY_API_TOKEN": "unit-only-token",
        "BILLY_TEST_ORGANIZATION_ID": "dedicated-non-production-org",
        "BILLY_LIVE_PROBE_ORGANIZATION_GUARD": "dedicated-non-production-org",
    }


def test_missing_token_skips_without_network_or_evidence(tmp_path: Path) -> None:
    result = _runner(tmp_path).run({})

    assert result.model_dump() == {
        "status": ProbeStatus.SKIPPED_NO_TOKEN,
        "candidate_count": 121,
        "observation_count": 0,
        "evidence_written": False,
    }
    assert not (tmp_path / "evidence").exists()


@pytest.mark.parametrize(
    ("environment", "expected_status"),
    [
        (
            {"BILLY_API_TOKEN": "unit-only-token"},
            ProbeStatus.BLOCKED_MISSING_TEST_ORGANIZATION,
        ),
        (
            {
                "BILLY_API_TOKEN": "unit-only-token",
                "BILLY_TEST_ORGANIZATION_ID": "dedicated-non-production-org",
            },
            ProbeStatus.BLOCKED_MISSING_TEST_ORGANIZATION,
        ),
        (
            {
                "BILLY_API_TOKEN": "unit-only-token",
                "BILLY_TEST_ORGANIZATION_ID": "dedicated-non-production-org",
                "BILLY_LIVE_PROBE_ORGANIZATION_GUARD": "other-org",
            },
            ProbeStatus.BLOCKED_TEST_ORGANIZATION_MISMATCH,
        ),
    ],
)
def test_missing_or_mismatched_test_organization_blocks_before_network(
    tmp_path: Path,
    environment: dict[str, str],
    expected_status: ProbeStatus,
) -> None:
    config = _config(
        tmp_path,
        test_organization_id=environment.get("BILLY_TEST_ORGANIZATION_ID"),
        test_organization_guard=environment.get("BILLY_LIVE_PROBE_ORGANIZATION_GUARD"),
    )

    result = LiveProbeRunner(config, transport=httpx.MockTransport(_forbid_network)).run(
        environment
    )

    assert result.status is expected_status
    assert result.observation_count == 0
    assert result.evidence_written is False
    assert not (tmp_path / "evidence").exists()


def test_fixed_base_is_literal_and_every_candidate_stays_beneath_it(tmp_path: Path) -> None:
    with pytest.raises(ValidationError):
        _config(tmp_path, api_base_url="https://api.billy.dk/v2")

    candidates = research88_candidates()

    assert API_BASE_URL == "https://api.billysbilling.com/v2"
    assert all(candidate.route.startswith("/") for candidate in candidates)
    assert all("//" not in candidate.route for candidate in candidates)
    assert all(
        f"{API_BASE_URL}{candidate.observation_route}".startswith(f"{API_BASE_URL}/")
        for candidate in candidates
    )


def test_research88_candidate_construction_is_exact_and_deterministic() -> None:
    candidates = research88_candidates()
    residual = tuple(
        candidate for candidate in candidates if candidate.kind is CandidateKind.RESIDUAL
    )
    bulk = tuple(
        candidate for candidate in candidates if candidate.kind is not CandidateKind.RESIDUAL
    )

    assert len(candidates) == 121
    assert len(residual) == 29
    assert len(bulk) == 92
    assert tuple(candidate.id for candidate in residual) == (
        "api.accountNatures.create",
        "api.accountNatures.update",
        "api.balanceModifiers.create",
        "api.balanceModifiers.update",
        "api.bankPayments.delete",
        "api.cities.create",
        "api.cities.update",
        "api.contactBalancePostings.create",
        "api.contactBalancePostings.update",
        "api.countryGroups.create",
        "api.countryGroups.update",
        "api.countries.create",
        "api.countries.update",
        "api.currencies.create",
        "api.currencies.update",
        "api.invoiceReminderAssociations.create",
        "api.invoiceReminderAssociations.update",
        "api.invoiceReminderAssociations.delete",
        "api.locales.create",
        "api.locales.update",
        "api.postings.create",
        "api.postings.update",
        "api.states.create",
        "api.states.update",
        "api.transactions.create",
        "api.transactions.update",
        "api.transactions.delete",
        "api.zipcodes.create",
        "api.zipcodes.update",
    )
    assert tuple(candidate.id for candidate in bulk[:4]) == (
        "api.accountGroups.bulk_save",
        "api.accountGroups.bulk_delete",
        "api.accountNatures.bulk_save",
        "api.accountNatures.bulk_delete",
    )
    assert tuple(candidate.id for candidate in bulk[-2:]) == (
        "api.zipcodes.bulk_save",
        "api.zipcodes.bulk_delete",
    )
    assert all(candidate.candidate_method == "PUT" for candidate in bulk[::2])
    assert all(candidate.candidate_method == "DELETE" for candidate in bulk[1::2])
    assert all(candidate.query_names == ("ids[]",) for candidate in bulk[1::2])


def test_invalid_evidence_path_blocks_before_network(tmp_path: Path) -> None:
    repository_root = tmp_path / "repository"
    result = _runner(
        tmp_path,
        evidence_directory=repository_root / "evidence",
        repository_root=repository_root,
        test_organization_id="dedicated-non-production-org",
        test_organization_guard="dedicated-non-production-org",
    ).run(_guarded_environment())

    assert result.status is ProbeStatus.BLOCKED_EVIDENCE_DIRECTORY
    assert result.observation_count == 0
    assert result.evidence_written is False
    assert not (repository_root / "evidence").exists()


def test_observations_are_options_only_redacted_and_evidence_is_owner_only(tmp_path: Path) -> None:
    requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return httpx.Response(
            401,
            json={
                "errorCode": "AUTHENTICATION_REQUIRED",
                "errorMessage": "customer@example.test must never be persisted",
                "accessToken": "upstream-secret",
            },
        )

    result = _runner(
        tmp_path,
        handler,
        test_organization_id="dedicated-non-production-org",
        test_organization_guard="dedicated-non-production-org",
    ).run(_guarded_environment())

    evidence_directory = tmp_path / "evidence"
    evidence_files = tuple(evidence_directory.glob("wave5t-*.json"))
    assert result.status is ProbeStatus.OBSERVED_UNQUALIFIED
    assert result.observation_count == 121
    assert result.evidence_written is True
    assert len(requests) == 121
    assert all(request.method == "OPTIONS" for request in requests)
    assert all(str(request.url).startswith(f"{API_BASE_URL}/") for request in requests)
    assert all(request.content == b"" for request in requests)
    assert stat.S_IMODE(evidence_directory.stat().st_mode) == 0o700
    assert len(evidence_files) == 1
    assert stat.S_IMODE(evidence_files[0].stat().st_mode) == 0o600

    evidence_text = evidence_files[0].read_text(encoding="utf-8")
    evidence = json.loads(evidence_text)
    assert "unit-only-token" not in result.model_dump_json()
    assert "unit-only-token" not in evidence_text
    assert "customer@example.test" not in evidence_text
    assert "upstream-secret" not in evidence_text
    assert evidence["contract_qualified"] is False
    assert evidence["persistent_data_created"] is False
    assert {item["state"] for item in evidence["observations"]} == {
        CandidateObservationState.UNQUALIFIED
    }


def test_transport_and_meta_success_never_become_contract_evidence(tmp_path: Path) -> None:
    responses = iter((200, 401, 405))

    def handler(_: httpx.Request) -> httpx.Response:
        return httpx.Response(next(responses, 200), json={"meta": {"success": True}})

    result = _runner(
        tmp_path,
        handler,
        test_organization_id="dedicated-non-production-org",
        test_organization_guard="dedicated-non-production-org",
    ).run(_guarded_environment())

    evidence_file = next((tmp_path / "evidence").glob("wave5t-*.json"))
    evidence = json.loads(evidence_file.read_text(encoding="utf-8"))
    assert result.status is ProbeStatus.OBSERVED_UNQUALIFIED
    assert evidence["contract_qualified"] is False
    assert {item["state"] for item in evidence["observations"]} == {
        CandidateObservationState.UNQUALIFIED
    }
    assert {item["status_code"] for item in evidence["observations"]} == {200, 401, 405}


def test_cleanup_ledger_requires_tagged_safe_read_back_and_reverse_cleanup() -> None:
    ledger = CleanupLedger("wave5t-test-tag")
    unsafe = TrackedDisposableResource(
        resource_id="unsafe",
        test_tag="wave5t-test-tag",
        safe_disposable_observed=False,
        independently_read_back=True,
    )
    with pytest.raises(PersistentDataBlocked):
        ledger.track(unsafe)

    first = TrackedDisposableResource(
        resource_id="parent",
        test_tag="wave5t-test-tag",
        safe_disposable_observed=True,
        independently_read_back=True,
    )
    second = TrackedDisposableResource(
        resource_id="child",
        test_tag="wave5t-test-tag",
        safe_disposable_observed=True,
        independently_read_back=True,
    )
    ledger.track(first)
    ledger.track(second)

    assert ledger.required_cleanup_order() == ("child", "parent")
    with pytest.raises(CleanupVerificationFailed):
        ledger.verify_cleanup(("parent", "child"), frozenset({"parent", "child"}))
    ledger.verify_cleanup(("child", "parent"), frozenset({"parent", "child"}))
