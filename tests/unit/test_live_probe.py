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
    BULK_DELETE_EMPTY_ERROR_CODE,
    BULK_DELETE_QUERY_NAME,
    BulkDeleteFormAssessment,
    BulkDeleteFormKind,
    BulkDeleteFormState,
    BulkDeleteRejectedBodyForm,
    BulkDeleteRejectedBodyFormKind,
    BulkDeleteWireClassification,
    CandidateKind,
    CandidateObservationState,
    CanonicalBulkDeleteForm,
    CleanupLedger,
    CleanupVerificationFailed,
    LiveProbeConfig,
    LiveProbeRunner,
    OrganizationPathAmbiguityFixture,
    OrganizationPathClassification,
    OrganizationPathInvalidTokenOutcome,
    OrganizationPathNoTokenOutcome,
    PersistentDataBlocked,
    ProbeStatus,
    RealMethodSafetyGate,
    ResidualUnauthenticatedClassification,
    ResidualUnauthenticatedOutcome,
    ResidualUnauthenticatedOutcomeFixture,
    TrackedDisposableResource,
    research88_candidates,
    research95_bulk_delete_form_matrix,
    research96_canonical_bulk_delete_form,
    research96_organization_path_ambiguity,
    research96_rejected_bulk_delete_body_forms,
    research96_residual_unauthenticated_outcomes,
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
    assert BULK_DELETE_QUERY_NAME == "ids[]"
    assert all(candidate.query_names == (BULK_DELETE_QUERY_NAME,) for candidate in bulk[1::2])


def test_research95_empty_bulk_delete_forms_are_validation_errors_not_safe_no_ops() -> None:
    matrix = research95_bulk_delete_form_matrix()
    empty_forms = matrix[:-1]

    assert tuple(form.form for form in empty_forms) == (
        BulkDeleteFormKind.EMPTY_IDS_ARRAY_QUERY,
        BulkDeleteFormKind.BARE_IDS_ARRAY_QUERY,
        BulkDeleteFormKind.EMPTY_IDS_QUERY,
        BulkDeleteFormKind.EMPTY_JSON_IDS_ARRAY,
        BulkDeleteFormKind.EMPTY_JSON_PLURAL_ARRAY,
    )
    assert all(form.unauthenticated_status_code == 400 for form in empty_forms)
    assert all(form.error_code == BULK_DELETE_EMPTY_ERROR_CODE for form in empty_forms)
    assert all(form.state is BulkDeleteFormState.VALIDATION_ERROR for form in empty_forms)
    assert all(form.safe_no_op is False for form in empty_forms)
    assert all(form.qualifies_live_wire_contract is False for form in empty_forms)
    assert all(form.permits_real_method_network is False for form in empty_forms)

    with pytest.raises(ValidationError):
        BulkDeleteFormAssessment(
            form=BulkDeleteFormKind.EMPTY_IDS_ARRAY_QUERY,
            unauthenticated_status_code=200,
            state=BulkDeleteFormState.METADATA_ONLY_UNQUALIFIED,
        )
    with pytest.raises(ValidationError):
        BulkDeleteFormAssessment.model_validate(
            {
                "form": BulkDeleteFormKind.SYNTHETIC_IDS_ARRAY_QUERY,
                "unauthenticated_status_code": 200,
                "state": BulkDeleteFormState.METADATA_ONLY_UNQUALIFIED,
                "permits_real_method_network": True,
            }
        )


def test_research95_metadata_only_success_cannot_open_a_real_method_network_path() -> None:
    matrix = research95_bulk_delete_form_matrix()
    synthetic_form = matrix[-1]

    assert synthetic_form.form is BulkDeleteFormKind.SYNTHETIC_IDS_ARRAY_QUERY
    assert synthetic_form.unauthenticated_status_code == 200
    assert synthetic_form.error_code is None
    assert synthetic_form.state is BulkDeleteFormState.METADATA_ONLY_UNQUALIFIED
    assert synthetic_form.safe_no_op is False
    assert synthetic_form.qualifies_live_wire_contract is False
    assert synthetic_form.permits_real_method_network is False

    candidates = research88_candidates()
    assert all(candidate.permits_real_method_network is False for candidate in candidates)
    assert all(
        candidate.real_method_gate.non_persistence_proven is False for candidate in candidates
    )
    assert all(
        candidate.real_method_gate.dual_organization_verified is False for candidate in candidates
    )
    assert all(
        candidate.real_method_gate.owner_only_evidence_verified is False for candidate in candidates
    )
    assert all(candidate.real_method_gate.cleanup_verified is False for candidate in candidates)
    assert all(
        candidate.real_method_gate.independently_read_back is False for candidate in candidates
    )
    with pytest.raises(ValidationError):
        RealMethodSafetyGate.model_validate({"non_persistence_proven": True})


def test_research96_residual_outcomes_cover_each_frozen_residual_once() -> None:
    fixture = research96_residual_unauthenticated_outcomes()
    residual_ids = tuple(
        candidate.id
        for candidate in research88_candidates()
        if candidate.kind is CandidateKind.RESIDUAL
    )

    assert tuple(outcome.candidate_id for outcome in fixture.outcomes) == residual_ids
    assert len(fixture.outcomes) == 29
    assert len({outcome.candidate_id for outcome in fixture.outcomes}) == 29
    assert {
        (outcome.unauthenticated_status_code, outcome.classification)
        for outcome in fixture.outcomes
    } == {
        (405, ResidualUnauthenticatedClassification.PERMANENT_METHOD_NOT_ALLOWED),
        (401, ResidualUnauthenticatedClassification.AUTHENTICATION_GATED),
        (200, ResidualUnauthenticatedClassification.METADATA_ONLY_UNQUALIFIED),
    }
    assert sum(outcome.unauthenticated_status_code == 405 for outcome in fixture.outcomes) == 25
    assert sum(outcome.unauthenticated_status_code == 401 for outcome in fixture.outcomes) == 2
    assert sum(outcome.unauthenticated_status_code == 200 for outcome in fixture.outcomes) == 2
    outcomes_by_id = {
        outcome.candidate_id: (outcome.unauthenticated_status_code, outcome.classification)
        for outcome in fixture.outcomes
    }
    assert {
        candidate_id: outcomes_by_id[candidate_id]
        for candidate_id in (
            "api.transactions.create",
            "api.transactions.update",
        )
    } == {
        "api.transactions.create": (
            401,
            ResidualUnauthenticatedClassification.AUTHENTICATION_GATED,
        ),
        "api.transactions.update": (
            401,
            ResidualUnauthenticatedClassification.AUTHENTICATION_GATED,
        ),
    }
    assert {
        candidate_id: outcomes_by_id[candidate_id]
        for candidate_id in (
            "api.transactions.delete",
            "api.invoiceReminderAssociations.delete",
        )
    } == {
        "api.transactions.delete": (
            200,
            ResidualUnauthenticatedClassification.METADATA_ONLY_UNQUALIFIED,
        ),
        "api.invoiceReminderAssociations.delete": (
            200,
            ResidualUnauthenticatedClassification.METADATA_ONLY_UNQUALIFIED,
        ),
    }
    assert all(
        outcome == (405, ResidualUnauthenticatedClassification.PERMANENT_METHOD_NOT_ALLOWED)
        for candidate_id, outcome in outcomes_by_id.items()
        if candidate_id
        not in {
            "api.transactions.create",
            "api.transactions.update",
            "api.transactions.delete",
            "api.invoiceReminderAssociations.delete",
        }
    )
    assert all(outcome.permits_real_method_network is False for outcome in fixture.outcomes)
    assert all(outcome.registers_tool is False for outcome in fixture.outcomes)
    assert all(outcome.claims_cleanup is False for outcome in fixture.outcomes)
    assert all(outcome.changes_coverage_state is False for outcome in fixture.outcomes)
    assert fixture.permits_real_method_network is False
    assert fixture.registers_tool is False
    assert fixture.claims_cleanup is False
    assert fixture.changes_coverage_state is False


def test_research96_residual_outcome_fixture_rejects_status_and_membership_drift() -> None:
    fixture = research96_residual_unauthenticated_outcomes()
    outcomes = [outcome.model_dump(mode="json") for outcome in fixture.outcomes]

    with pytest.raises(ValidationError):
        ResidualUnauthenticatedOutcome(
            candidate_id="api.transactions.create",
            unauthenticated_status_code=200,
            classification=ResidualUnauthenticatedClassification.AUTHENTICATION_GATED,
        )
    with pytest.raises(ValidationError):
        ResidualUnauthenticatedOutcomeFixture.model_validate({"outcomes": outcomes[:-1]})
    with pytest.raises(ValidationError):
        ResidualUnauthenticatedOutcomeFixture.model_validate({"outcomes": [*outcomes, outcomes[0]]})

    outcomes[24]["unauthenticated_status_code"] = 405
    outcomes[24]["classification"] = "permanent_method_not_allowed"
    with pytest.raises(ValidationError):
        ResidualUnauthenticatedOutcomeFixture.model_validate({"outcomes": outcomes})
    with pytest.raises(ValidationError):
        ResidualUnauthenticatedOutcome.model_validate(
            {
                "candidate_id": "api.bankPayments.delete",
                "unauthenticated_status_code": 405,
                "classification": "permanent_method_not_allowed",
                "permits_real_method_network": True,
            }
        )


def test_research96_bulk_delete_fixture_is_query_only_and_rejects_body_variants() -> None:
    canonical = research96_canonical_bulk_delete_form()
    rejected_body_forms = research96_rejected_bulk_delete_body_forms()

    assert canonical.method == "DELETE"
    assert canonical.route_template == "/{resource}"
    assert canonical.query_items == (("ids[]", "123"), ("ids[]", "456"))
    assert canonical.request_body is None
    assert canonical.classification is BulkDeleteWireClassification.QUERY_ONLY
    assert canonical.encoded_template == "/{resource}?ids[]=123&ids[]=456"
    assert canonical.permits_real_method_network is False
    assert canonical.registers_tool is False
    assert canonical.claims_cleanup is False
    assert canonical.changes_coverage_state is False
    assert canonical.model_dump() == {
        "permits_real_method_network": False,
        "registers_tool": False,
        "claims_cleanup": False,
        "changes_coverage_state": False,
    }

    for supplied_field in (
        {"route": "/accounts"},
        {"body": {"ids": ["123", "456"]}},
        {"request_body": {"ids": ["123", "456"]}},
        {"query_name": "ids"},
        {"query_parameter_name": "ids"},
    ):
        with pytest.raises(ValidationError):
            CanonicalBulkDeleteForm.model_validate(supplied_field)

    assert tuple(form.form for form in rejected_body_forms) == (
        BulkDeleteRejectedBodyFormKind.JSON_BODY,
        BulkDeleteRejectedBodyFormKind.FORM_BODY,
    )
    assert all(form.unauthenticated_status_code == 400 for form in rejected_body_forms)
    assert all(form.error_code == BULK_DELETE_EMPTY_ERROR_CODE for form in rejected_body_forms)
    assert all(
        form.classification is BulkDeleteWireClassification.REJECTED_NON_PRODUCT_BODY
        for form in rejected_body_forms
    )
    assert all(form.request_body_present is True for form in rejected_body_forms)
    assert all(form.permits_real_method_network is False for form in rejected_body_forms)
    assert all(form.registers_tool is False for form in rejected_body_forms)
    with pytest.raises(ValidationError):
        BulkDeleteRejectedBodyForm.model_validate(
            {
                "form": BulkDeleteRejectedBodyFormKind.JSON_BODY,
                "unauthenticated_status_code": 400,
                "error_code": BULK_DELETE_EMPTY_ERROR_CODE,
                "classification": BulkDeleteWireClassification.QUERY_ONLY,
            }
        )


def test_research96_organization_path_fixture_preserves_documented_route_ambiguity() -> None:
    fixture = research96_organization_path_ambiguity()

    assert {
        outcome.route: (
            outcome.unauthenticated_status_code,
            outcome.error_code,
            outcome.classification,
        )
        for outcome in fixture.no_token_outcomes
    } == {
        "/user/organizations": (
            404,
            "UNKNOWN_RESOURCE",
            OrganizationPathClassification.UNKNOWN_RESOURCE,
        ),
        "/organizations": (
            401,
            "AUTHENTICATION_REQUIRED",
            OrganizationPathClassification.AUTHENTICATION_REQUIRED,
        ),
    }
    assert fixture.invalid_token_outcome.status_code == 401
    assert fixture.invalid_token_outcome.error_code == "OAUTH_INVALID_ACCESS_TOKEN"
    assert (
        fixture.invalid_token_outcome.classification
        is OrganizationPathClassification.AUTH_FIRST_PATH_AGNOSTIC
    )
    assert fixture.documented_tool_route == "/user/organizations"
    assert fixture.alternate_route_inferred is False
    assert fixture.requires_valid_dedicated_non_production_observation is True
    assert fixture.permits_real_method_network is False
    assert fixture.registers_tool is False
    assert fixture.changes_coverage_state is False


def test_research96_organization_path_fixture_rejects_inference_and_wrong_outcomes() -> None:
    fixture = research96_organization_path_ambiguity()

    with pytest.raises(ValidationError):
        OrganizationPathNoTokenOutcome(
            route="/user/organizations",
            unauthenticated_status_code=401,
            error_code="AUTHENTICATION_REQUIRED",
            classification=OrganizationPathClassification.AUTHENTICATION_REQUIRED,
        )
    with pytest.raises(ValidationError):
        OrganizationPathInvalidTokenOutcome(
            status_code=401,
            error_code="OAUTH_INVALID_ACCESS_TOKEN",
            classification=OrganizationPathClassification.AUTHENTICATION_REQUIRED,
        )
    with pytest.raises(ValidationError):
        OrganizationPathAmbiguityFixture.model_validate(
            {
                "no_token_outcomes": fixture.no_token_outcomes[:1],
                "invalid_token_outcome": fixture.invalid_token_outcome,
            }
        )
    with pytest.raises(ValidationError):
        OrganizationPathAmbiguityFixture.model_validate(
            {
                "no_token_outcomes": (
                    fixture.no_token_outcomes[0],
                    fixture.no_token_outcomes[0],
                ),
                "invalid_token_outcome": fixture.invalid_token_outcome,
            }
        )
    with pytest.raises(ValidationError):
        OrganizationPathAmbiguityFixture.model_validate(
            {
                "no_token_outcomes": fixture.no_token_outcomes,
                "invalid_token_outcome": fixture.invalid_token_outcome,
                "alternate_route_inferred": True,
            }
        )


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
