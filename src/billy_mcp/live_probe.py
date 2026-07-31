"""Fail-closed live qualification gate for Research88 residual and bulk candidates.

This module deliberately does not expose an MCP tool or a generic HTTP client.
It only makes bounded ``OPTIONS`` observations of the frozen candidate matrix.
Those observations are recorded as non-qualifying evidence: they never prove a
wire contract, safe mutation, coverage status, or cleanup capability.
"""

from __future__ import annotations

import os
import stat
import uuid
from collections.abc import Mapping
from enum import StrEnum
from pathlib import Path
from typing import Final, Literal
from urllib.parse import urlsplit

import httpx
from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    ValidationError,
    field_validator,
    model_validator,
)

API_BASE_URL: Final = "https://api.billysbilling.com/v2"
OBSERVATION_METHOD: Final = "OPTIONS"
OBSERVATION_IDENTIFIER: Final = "__wave5t_observation_target__"
DEFAULT_EVIDENCE_DIRECTORY: Final = Path.home() / ".local" / "state" / "billy-mcp" / "live-probe"
BULK_DELETE_QUERY_NAME: Final[Literal["ids[]"]] = "ids[]"
BULK_DELETE_EMPTY_ERROR_CODE: Final[Literal["INVALID_DELETE_ID_ARRAY"]] = "INVALID_DELETE_ID_ARRAY"


class ProbeStatus(StrEnum):
    """Non-sensitive outcomes emitted by the live gate."""

    SKIPPED_NO_TOKEN = "skipped_no_token"
    BLOCKED_MISSING_TEST_ORGANIZATION = "blocked_missing_test_organization"
    BLOCKED_TEST_ORGANIZATION_MISMATCH = "blocked_test_organization_mismatch"
    BLOCKED_EVIDENCE_DIRECTORY = "blocked_evidence_directory"
    EVIDENCE_WRITE_FAILED = "evidence_write_failed"
    OBSERVED_UNQUALIFIED = "observed_unqualified"


class CandidateKind(StrEnum):
    """The two frozen Research88 candidate classes."""

    RESIDUAL = "residual"
    BULK_SAVE = "bulk_save"
    BULK_DELETE = "bulk_delete"


class CandidateObservationState(StrEnum):
    """Every status remains non-contract evidence until separately qualified."""

    UNQUALIFIED = "unqualified"
    TRANSPORT_UNAVAILABLE = "transport_unavailable"


class BulkDeleteFormKind(StrEnum):
    """Research95's observed unauthenticated bulk-delete input forms."""

    EMPTY_IDS_ARRAY_QUERY = "empty_ids_array_query"
    BARE_IDS_ARRAY_QUERY = "bare_ids_array_query"
    EMPTY_IDS_QUERY = "empty_ids_query"
    EMPTY_JSON_IDS_ARRAY = "empty_json_ids_array"
    EMPTY_JSON_PLURAL_ARRAY = "empty_json_plural_array"
    SYNTHETIC_IDS_ARRAY_QUERY = "synthetic_ids_array_query"


class BulkDeleteFormState(StrEnum):
    """Observed form outcomes that must never qualify a real method."""

    VALIDATION_ERROR = "validation_error"
    METADATA_ONLY_UNQUALIFIED = "metadata_only_unqualified"


class BulkDeleteFormAssessment(BaseModel):
    """Immutable research95 form outcome; no form proves a safe no-op."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    form: BulkDeleteFormKind
    unauthenticated_status_code: Literal[200, 400]
    error_code: Literal["INVALID_DELETE_ID_ARRAY"] | None = None
    state: BulkDeleteFormState
    safe_no_op: Literal[False] = False
    qualifies_live_wire_contract: Literal[False] = False
    permits_real_method_network: Literal[False] = False

    @model_validator(mode="after")
    def _enforce_research95_semantics(self) -> BulkDeleteFormAssessment:
        """Keep validation errors and metadata-only success distinct and unqualified."""

        if self.form is BulkDeleteFormKind.SYNTHETIC_IDS_ARRAY_QUERY:
            if (
                self.unauthenticated_status_code != 200
                or self.error_code is not None
                or self.state is not BulkDeleteFormState.METADATA_ONLY_UNQUALIFIED
            ):
                raise ValueError(
                    "synthetic bulk-delete id is metadata-only unauthenticated evidence"
                )
            return self
        if (
            self.unauthenticated_status_code != 400
            or self.error_code != BULK_DELETE_EMPTY_ERROR_CODE
            or self.state is not BulkDeleteFormState.VALIDATION_ERROR
        ):
            raise ValueError(
                "empty bulk-delete forms are INVALID_DELETE_ID_ARRAY validation errors"
            )
        return self


class ResidualUnauthenticatedClassification(StrEnum):
    """Research96's non-qualifying classifications for residual method gates."""

    PERMANENT_METHOD_NOT_ALLOWED = "permanent_method_not_allowed"
    AUTHENTICATION_GATED = "authentication_gated"
    METADATA_ONLY_UNQUALIFIED = "metadata_only_unqualified"


class ResidualUnauthenticatedOutcome(BaseModel):
    """One immutable unauthenticated outcome that cannot open a product path."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    candidate_id: str = Field(min_length=1)
    unauthenticated_status_code: Literal[200, 401, 405]
    classification: ResidualUnauthenticatedClassification
    permits_real_method_network: Literal[False] = False
    registers_tool: Literal[False] = False
    claims_cleanup: Literal[False] = False
    changes_coverage_state: Literal[False] = False

    @model_validator(mode="after")
    def _enforce_non_qualifying_semantics(self) -> ResidualUnauthenticatedOutcome:
        """Keep each recorded status tied to its only permitted interpretation."""

        expected = {
            ResidualUnauthenticatedClassification.PERMANENT_METHOD_NOT_ALLOWED: 405,
            ResidualUnauthenticatedClassification.AUTHENTICATION_GATED: 401,
            ResidualUnauthenticatedClassification.METADATA_ONLY_UNQUALIFIED: 200,
        }
        if self.unauthenticated_status_code != expected[self.classification]:
            raise ValueError("residual classification does not match its unauthenticated status")
        return self


class ResidualUnauthenticatedOutcomeFixture(BaseModel):
    """The exact Research96 outcome fixture for every frozen residual candidate."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    outcomes: tuple[ResidualUnauthenticatedOutcome, ...]
    permits_real_method_network: Literal[False] = False
    registers_tool: Literal[False] = False
    claims_cleanup: Literal[False] = False
    changes_coverage_state: Literal[False] = False

    @model_validator(mode="after")
    def _enforce_exact_research88_membership(self) -> ResidualUnauthenticatedOutcomeFixture:
        """Reject missing, duplicate, or reclassified residual outcome rows."""

        expected = {
            candidate_id: (status_code, classification)
            for candidate_id, status_code, classification in _RESEARCH96_RESIDUAL_OUTCOMES
        }
        frozen_residual_ids = {
            candidate.id
            for candidate in research88_candidates()
            if candidate.kind is CandidateKind.RESIDUAL
        }
        actual = {
            outcome.candidate_id: (outcome.unauthenticated_status_code, outcome.classification)
            for outcome in self.outcomes
        }
        if len(actual) != len(self.outcomes):
            raise ValueError("residual outcome fixture must not duplicate candidate ids")
        if set(expected) != frozen_residual_ids:
            raise ValueError(
                "residual outcome fixture no longer matches frozen candidate membership"
            )
        if actual != expected:
            raise ValueError(
                "residual outcome fixture must cover each frozen candidate exactly once"
            )
        return self


class BulkDeleteWireClassification(StrEnum):
    """Whether a form is the static query template or a rejected body form."""

    QUERY_ONLY = "query_only"
    REJECTED_NON_PRODUCT_BODY = "rejected_non_product_body"


class CanonicalBulkDeleteForm(BaseModel):
    """A no-input immutable template for Billy's repeated-query bulk delete form."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    permits_real_method_network: Literal[False] = False
    registers_tool: Literal[False] = False
    claims_cleanup: Literal[False] = False
    changes_coverage_state: Literal[False] = False

    @property
    def method(self) -> Literal["DELETE"]:
        """Return the server-stated fixed method without accepting a caller value."""

        return "DELETE"

    @property
    def route_template(self) -> Literal["/{resource}"]:
        """Return the symbolic resource route; no concrete route can be supplied."""

        return "/{resource}"

    @property
    def query_items(self) -> tuple[tuple[str, str], tuple[str, str]]:
        """Return the exact repeated `ids[]` query sequence from the server message."""

        return ((BULK_DELETE_QUERY_NAME, "123"), (BULK_DELETE_QUERY_NAME, "456"))

    @property
    def request_body(self) -> None:
        """Keep the canonical bulk-delete form bodyless."""

        return None

    @property
    def classification(self) -> Literal[BulkDeleteWireClassification.QUERY_ONLY]:
        """Mark the template as the sole recognised input encoding, not a product form."""

        return BulkDeleteWireClassification.QUERY_ONLY

    @property
    def encoded_template(self) -> Literal["/{resource}?ids[]=123&ids[]=456"]:
        """Expose the exact query-only server form without building a request."""

        return "/{resource}?ids[]=123&ids[]=456"


class BulkDeleteRejectedBodyFormKind(StrEnum):
    """Research96 body encodings that the server rejected for bulk delete."""

    JSON_BODY = "json_body"
    FORM_BODY = "form_body"


class BulkDeleteRejectedBodyForm(BaseModel):
    """An immutable rejected body encoding; it is never a product request form."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    form: BulkDeleteRejectedBodyFormKind
    unauthenticated_status_code: Literal[400]
    error_code: Literal["INVALID_DELETE_ID_ARRAY"]
    classification: BulkDeleteWireClassification
    request_body_present: Literal[True] = True
    permits_real_method_network: Literal[False] = False
    registers_tool: Literal[False] = False
    claims_cleanup: Literal[False] = False
    changes_coverage_state: Literal[False] = False

    @model_validator(mode="after")
    def _enforce_rejected_body_semantics(self) -> BulkDeleteRejectedBodyForm:
        """Prevent JSON or form data from being misclassified as the query form."""

        if (
            self.error_code != BULK_DELETE_EMPTY_ERROR_CODE
            or self.classification is not BulkDeleteWireClassification.REJECTED_NON_PRODUCT_BODY
        ):
            raise ValueError("bulk-delete body forms are rejected non-product validation errors")
        return self


class OrganizationPathClassification(StrEnum):
    """Static Research96 classifications that intentionally do not infer a route."""

    UNKNOWN_RESOURCE = "unknown_resource"
    AUTHENTICATION_REQUIRED = "authentication_required"
    AUTH_FIRST_PATH_AGNOSTIC = "auth_first_path_agnostic"


class OrganizationPathNoTokenOutcome(BaseModel):
    """One no-token route observation retained solely as an ambiguity fixture."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    route: Literal["/user/organizations", "/organizations"]
    unauthenticated_status_code: Literal[401, 404]
    error_code: Literal["UNKNOWN_RESOURCE", "AUTHENTICATION_REQUIRED"]
    classification: OrganizationPathClassification

    @model_validator(mode="after")
    def _enforce_no_token_semantics(self) -> OrganizationPathNoTokenOutcome:
        """Keep each no-token path bound to the observed Research96 result."""

        expected = {
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
        if (
            self.unauthenticated_status_code,
            self.error_code,
            self.classification,
        ) != expected[self.route]:
            raise ValueError("no-token organisation path outcome does not match Research96")
        return self


class OrganizationPathInvalidTokenOutcome(BaseModel):
    """The path-agnostic invalid-token result, which proves no route existence."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    status_code: Literal[401]
    error_code: Literal["OAUTH_INVALID_ACCESS_TOKEN"]
    classification: OrganizationPathClassification

    @model_validator(mode="after")
    def _enforce_auth_first_semantics(self) -> OrganizationPathInvalidTokenOutcome:
        """Forbid interpreting invalid-token authentication failure as path evidence."""

        if self.classification is not OrganizationPathClassification.AUTH_FIRST_PATH_AGNOSTIC:
            raise ValueError("invalid-token result must remain auth-first and path-agnostic")
        return self


class OrganizationPathAmbiguityFixture(BaseModel):
    """Static route ambiguity evidence that preserves the documented tool path."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    no_token_outcomes: tuple[OrganizationPathNoTokenOutcome, ...]
    invalid_token_outcome: OrganizationPathInvalidTokenOutcome
    documented_tool_route: Literal["/user/organizations"] = "/user/organizations"
    alternate_route_inferred: Literal[False] = False
    requires_valid_dedicated_non_production_observation: Literal[True] = True
    permits_real_method_network: Literal[False] = False
    registers_tool: Literal[False] = False
    changes_coverage_state: Literal[False] = False

    @model_validator(mode="after")
    def _enforce_exact_no_token_paths(self) -> OrganizationPathAmbiguityFixture:
        """Require both no-token outcomes exactly once while retaining route ambiguity."""

        expected_routes = {"/user/organizations", "/organizations"}
        actual_routes = tuple(outcome.route for outcome in self.no_token_outcomes)
        if len(actual_routes) != len(set(actual_routes)) or set(actual_routes) != expected_routes:
            raise ValueError("organisation path fixture must contain both no-token routes once")
        return self


class RealMethodSafetyGate(BaseModel):
    """Current candidate state: every real residual or bulk method is blocked locally."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    non_persistence_proven: Literal[False] = False
    dual_organization_verified: Literal[False] = False
    owner_only_evidence_verified: Literal[False] = False
    cleanup_verified: Literal[False] = False
    independently_read_back: Literal[False] = False

    @property
    def permits_real_method_network(self) -> Literal[False]:
        """Require a separately reviewed model change before real-method traffic can exist."""

        return False


class LiveProbeCandidate(BaseModel):
    """One statically approved candidate; callers cannot supply routes."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    id: str = Field(min_length=1)
    kind: CandidateKind
    candidate_method: Literal["POST", "PUT", "DELETE"]
    route: str = Field(pattern=r"^/[A-Za-z][A-Za-z0-9]*(?:/(?:bulk|:id))?$")
    query_names: tuple[Literal["ids[]"], ...] = ()
    real_method_gate: RealMethodSafetyGate = Field(default_factory=RealMethodSafetyGate)

    @property
    def observation_route(self) -> str:
        """Return the static non-mutating route used for an OPTIONS observation."""

        return self.route.replace(":id", OBSERVATION_IDENTIFIER)

    @property
    def permits_real_method_network(self) -> Literal[False]:
        """Expose the default-deny invariant without adding a real-method path."""

        return self.real_method_gate.permits_real_method_network


class LiveProbeObservation(BaseModel):
    """Sanitised observation metadata; it intentionally excludes response content."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    candidate_id: str
    candidate_method: Literal["POST", "PUT", "DELETE"]
    route: str
    observation_method: Literal["OPTIONS"] = OBSERVATION_METHOD
    status_code: int | None = Field(default=None, ge=100, le=599)
    state: CandidateObservationState


class LiveProbeResult(BaseModel):
    """Safe CLI result that cannot contain credentials or upstream body data."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    status: ProbeStatus
    candidate_count: int = Field(ge=0)
    observation_count: int = Field(ge=0)
    evidence_written: bool


class LiveProbeEvidence(BaseModel):
    """Owner-only external evidence containing metadata, never raw Billy data."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    run_tag: str = Field(pattern=r"^wave5t-[0-9a-f]{32}$")
    api_base_url: Literal["https://api.billysbilling.com/v2"] = API_BASE_URL
    observations: tuple[LiveProbeObservation, ...]
    contract_qualified: Literal[False] = False
    persistent_data_created: Literal[False] = False


class LiveProbeConfig(BaseModel):
    """Safe configuration only; the API token is intentionally not a field."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    api_base_url: Literal["https://api.billysbilling.com/v2"] = API_BASE_URL
    test_organization_id: str | None = Field(default=None, min_length=1)
    test_organization_guard: str | None = Field(default=None, min_length=1)
    evidence_directory: Path = DEFAULT_EVIDENCE_DIRECTORY
    repository_root: Path

    @field_validator("evidence_directory", "repository_root", mode="after")
    @classmethod
    def _canonical_path(cls, value: Path) -> Path:
        return value.expanduser().resolve(strict=False)

    @classmethod
    def from_environment(
        cls,
        environment: Mapping[str, str] | None = None,
        *,
        repository_root: Path | None = None,
    ) -> LiveProbeConfig:
        """Load only non-secret runner configuration from the environment."""

        source = os.environ if environment is None else environment
        return cls(
            test_organization_id=source.get("BILLY_TEST_ORGANIZATION_ID") or None,
            test_organization_guard=source.get("BILLY_LIVE_PROBE_ORGANIZATION_GUARD") or None,
            evidence_directory=Path(
                source.get("BILLY_LIVE_PROBE_EVIDENCE_DIR", str(DEFAULT_EVIDENCE_DIRECTORY))
            ),
            repository_root=repository_root or Path.cwd(),
        )


class PersistentDataBlocked(RuntimeError):
    """Raised when future code tries to track an unproven persistent resource."""


class CleanupVerificationFailed(RuntimeError):
    """Raised when future cleanup is not proven in reverse dependency order."""


class TrackedDisposableResource(BaseModel):
    """The minimum record a future write path must provide before cleanup."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    resource_id: str = Field(min_length=1)
    test_tag: str = Field(min_length=1)
    safe_disposable_observed: bool
    independently_read_back: bool


class CleanupLedger:
    """Pure in-memory enforcement for any future persistent-data extension.

    This harness has no write operation, so it never instantiates this ledger in
    its runner. Keeping the gate here prevents a future extension from silently
    bypassing tag, read-back, reverse-order, or cleanup-proof requirements.
    """

    def __init__(self, test_tag: str) -> None:
        if not test_tag.strip():
            raise ValueError("test_tag must be non-empty")
        self._test_tag = test_tag
        self._resources: list[TrackedDisposableResource] = []

    def track(self, resource: TrackedDisposableResource) -> None:
        """Accept only uniquely tagged resources proven safe and read back."""

        if resource.test_tag != self._test_tag:
            raise PersistentDataBlocked("resource test tag does not match this run")
        if not resource.safe_disposable_observed:
            raise PersistentDataBlocked("safe disposable operation has not been observed")
        if not resource.independently_read_back:
            raise PersistentDataBlocked("resource lacks independent read-back")
        if any(item.resource_id == resource.resource_id for item in self._resources):
            raise PersistentDataBlocked("resource is already tracked")
        self._resources.append(resource)

    def required_cleanup_order(self) -> tuple[str, ...]:
        """Return reverse creation order, the required reverse dependency order."""

        return tuple(resource.resource_id for resource in reversed(self._resources))

    def verify_cleanup(
        self,
        removed_resource_ids: tuple[str, ...],
        independently_absent_ids: frozenset[str],
    ) -> None:
        """Refuse to hide missing, out-of-order, or unverified cleanup."""

        required = self.required_cleanup_order()
        if removed_resource_ids != required:
            raise CleanupVerificationFailed(
                "resources were not removed in reverse dependency order"
            )
        if independently_absent_ids != frozenset(required):
            raise CleanupVerificationFailed("cleanup lacks independent absence read-back")


_RESIDUAL_CANDIDATES: Final[tuple[tuple[str, Literal["POST", "PUT", "DELETE"], str], ...]] = (
    ("api.accountNatures.create", "POST", "/accountNatures"),
    ("api.accountNatures.update", "PUT", "/accountNatures/:id"),
    ("api.balanceModifiers.create", "POST", "/balanceModifiers"),
    ("api.balanceModifiers.update", "PUT", "/balanceModifiers/:id"),
    ("api.bankPayments.delete", "DELETE", "/bankPayments/:id"),
    ("api.cities.create", "POST", "/cities"),
    ("api.cities.update", "PUT", "/cities/:id"),
    ("api.contactBalancePostings.create", "POST", "/contactBalancePostings"),
    ("api.contactBalancePostings.update", "PUT", "/contactBalancePostings/:id"),
    ("api.countryGroups.create", "POST", "/countryGroups"),
    ("api.countryGroups.update", "PUT", "/countryGroups/:id"),
    ("api.countries.create", "POST", "/countries"),
    ("api.countries.update", "PUT", "/countries/:id"),
    ("api.currencies.create", "POST", "/currencies"),
    ("api.currencies.update", "PUT", "/currencies/:id"),
    ("api.invoiceReminderAssociations.create", "POST", "/invoiceReminderAssociations"),
    ("api.invoiceReminderAssociations.update", "PUT", "/invoiceReminderAssociations/:id"),
    ("api.invoiceReminderAssociations.delete", "DELETE", "/invoiceReminderAssociations/:id"),
    ("api.locales.create", "POST", "/locales"),
    ("api.locales.update", "PUT", "/locales/:id"),
    ("api.postings.create", "POST", "/postings"),
    ("api.postings.update", "PUT", "/postings/:id"),
    ("api.states.create", "POST", "/states"),
    ("api.states.update", "PUT", "/states/:id"),
    ("api.transactions.create", "POST", "/transactions"),
    ("api.transactions.update", "PUT", "/transactions/:id"),
    ("api.transactions.delete", "DELETE", "/transactions/:id"),
    ("api.zipcodes.create", "POST", "/zipcodes"),
    ("api.zipcodes.update", "PUT", "/zipcodes/:id"),
)

_BULK_COLLECTIONS: Final[tuple[str, ...]] = (
    "accountGroups",
    "accountNatures",
    "accounts",
    "attachments",
    "balanceModifiers",
    "bankLineMatches",
    "bankLines",
    "bankLineSubjectAssociations",
    "bankPayments",
    "billLines",
    "bills",
    "cities",
    "contactBalancePayments",
    "contactBalancePostings",
    "contactPersons",
    "contacts",
    "countryGroups",
    "countries",
    "currencies",
    "daybookBalanceAccounts",
    "daybooks",
    "daybookTransactionLines",
    "daybookTransactions",
    "files",
    "invoiceLateFees",
    "invoiceLines",
    "invoiceReminderAssociations",
    "invoiceReminders",
    "invoices",
    "locales",
    "organizations",
    "postings",
    "productPrices",
    "products",
    "salesTaxAccounts",
    "salesTaxMetaFields",
    "salesTaxPayments",
    "salesTaxReturns",
    "salesTaxRules",
    "salesTaxRulesets",
    "states",
    "taxRateDeductionComponents",
    "taxRates",
    "transactions",
    "users",
    "zipcodes",
)


_RESEARCH95_BULK_DELETE_FORM_MATRIX: Final[tuple[BulkDeleteFormAssessment, ...]] = (
    BulkDeleteFormAssessment(
        form=BulkDeleteFormKind.EMPTY_IDS_ARRAY_QUERY,
        unauthenticated_status_code=400,
        error_code=BULK_DELETE_EMPTY_ERROR_CODE,
        state=BulkDeleteFormState.VALIDATION_ERROR,
    ),
    BulkDeleteFormAssessment(
        form=BulkDeleteFormKind.BARE_IDS_ARRAY_QUERY,
        unauthenticated_status_code=400,
        error_code=BULK_DELETE_EMPTY_ERROR_CODE,
        state=BulkDeleteFormState.VALIDATION_ERROR,
    ),
    BulkDeleteFormAssessment(
        form=BulkDeleteFormKind.EMPTY_IDS_QUERY,
        unauthenticated_status_code=400,
        error_code=BULK_DELETE_EMPTY_ERROR_CODE,
        state=BulkDeleteFormState.VALIDATION_ERROR,
    ),
    BulkDeleteFormAssessment(
        form=BulkDeleteFormKind.EMPTY_JSON_IDS_ARRAY,
        unauthenticated_status_code=400,
        error_code=BULK_DELETE_EMPTY_ERROR_CODE,
        state=BulkDeleteFormState.VALIDATION_ERROR,
    ),
    BulkDeleteFormAssessment(
        form=BulkDeleteFormKind.EMPTY_JSON_PLURAL_ARRAY,
        unauthenticated_status_code=400,
        error_code=BULK_DELETE_EMPTY_ERROR_CODE,
        state=BulkDeleteFormState.VALIDATION_ERROR,
    ),
    BulkDeleteFormAssessment(
        form=BulkDeleteFormKind.SYNTHETIC_IDS_ARRAY_QUERY,
        unauthenticated_status_code=200,
        state=BulkDeleteFormState.METADATA_ONLY_UNQUALIFIED,
    ),
)


def research95_bulk_delete_form_matrix() -> tuple[BulkDeleteFormAssessment, ...]:
    """Return the exact observed form matrix without creating a request path."""

    return _RESEARCH95_BULK_DELETE_FORM_MATRIX


def research88_candidates() -> tuple[LiveProbeCandidate, ...]:
    """Construct the exact immutable 29-residual plus 92-bulk candidate matrix."""

    residual = tuple(
        LiveProbeCandidate(
            id=candidate_id,
            kind=CandidateKind.RESIDUAL,
            candidate_method=method,
            route=route,
        )
        for candidate_id, method, route in _RESIDUAL_CANDIDATES
    )
    bulk: list[LiveProbeCandidate] = []
    for collection in _BULK_COLLECTIONS:
        bulk.extend(
            (
                LiveProbeCandidate(
                    id=f"api.{collection}.bulk_save",
                    kind=CandidateKind.BULK_SAVE,
                    candidate_method="PUT",
                    route=f"/{collection}/bulk",
                ),
                LiveProbeCandidate(
                    id=f"api.{collection}.bulk_delete",
                    kind=CandidateKind.BULK_DELETE,
                    candidate_method="DELETE",
                    route=f"/{collection}",
                    query_names=(BULK_DELETE_QUERY_NAME,),
                ),
            )
        )
    return residual + tuple(bulk)


_RESEARCH96_RESIDUAL_OUTCOMES: Final[
    tuple[tuple[str, Literal[200, 401, 405], ResidualUnauthenticatedClassification], ...]
] = (
    (
        "api.accountNatures.create",
        405,
        ResidualUnauthenticatedClassification.PERMANENT_METHOD_NOT_ALLOWED,
    ),
    (
        "api.accountNatures.update",
        405,
        ResidualUnauthenticatedClassification.PERMANENT_METHOD_NOT_ALLOWED,
    ),
    (
        "api.balanceModifiers.create",
        405,
        ResidualUnauthenticatedClassification.PERMANENT_METHOD_NOT_ALLOWED,
    ),
    (
        "api.balanceModifiers.update",
        405,
        ResidualUnauthenticatedClassification.PERMANENT_METHOD_NOT_ALLOWED,
    ),
    (
        "api.bankPayments.delete",
        405,
        ResidualUnauthenticatedClassification.PERMANENT_METHOD_NOT_ALLOWED,
    ),
    (
        "api.cities.create",
        405,
        ResidualUnauthenticatedClassification.PERMANENT_METHOD_NOT_ALLOWED,
    ),
    (
        "api.cities.update",
        405,
        ResidualUnauthenticatedClassification.PERMANENT_METHOD_NOT_ALLOWED,
    ),
    (
        "api.contactBalancePostings.create",
        405,
        ResidualUnauthenticatedClassification.PERMANENT_METHOD_NOT_ALLOWED,
    ),
    (
        "api.contactBalancePostings.update",
        405,
        ResidualUnauthenticatedClassification.PERMANENT_METHOD_NOT_ALLOWED,
    ),
    (
        "api.countryGroups.create",
        405,
        ResidualUnauthenticatedClassification.PERMANENT_METHOD_NOT_ALLOWED,
    ),
    (
        "api.countryGroups.update",
        405,
        ResidualUnauthenticatedClassification.PERMANENT_METHOD_NOT_ALLOWED,
    ),
    (
        "api.countries.create",
        405,
        ResidualUnauthenticatedClassification.PERMANENT_METHOD_NOT_ALLOWED,
    ),
    (
        "api.countries.update",
        405,
        ResidualUnauthenticatedClassification.PERMANENT_METHOD_NOT_ALLOWED,
    ),
    (
        "api.currencies.create",
        405,
        ResidualUnauthenticatedClassification.PERMANENT_METHOD_NOT_ALLOWED,
    ),
    (
        "api.currencies.update",
        405,
        ResidualUnauthenticatedClassification.PERMANENT_METHOD_NOT_ALLOWED,
    ),
    (
        "api.invoiceReminderAssociations.create",
        405,
        ResidualUnauthenticatedClassification.PERMANENT_METHOD_NOT_ALLOWED,
    ),
    (
        "api.invoiceReminderAssociations.update",
        405,
        ResidualUnauthenticatedClassification.PERMANENT_METHOD_NOT_ALLOWED,
    ),
    (
        "api.invoiceReminderAssociations.delete",
        200,
        ResidualUnauthenticatedClassification.METADATA_ONLY_UNQUALIFIED,
    ),
    (
        "api.locales.create",
        405,
        ResidualUnauthenticatedClassification.PERMANENT_METHOD_NOT_ALLOWED,
    ),
    (
        "api.locales.update",
        405,
        ResidualUnauthenticatedClassification.PERMANENT_METHOD_NOT_ALLOWED,
    ),
    (
        "api.postings.create",
        405,
        ResidualUnauthenticatedClassification.PERMANENT_METHOD_NOT_ALLOWED,
    ),
    (
        "api.postings.update",
        405,
        ResidualUnauthenticatedClassification.PERMANENT_METHOD_NOT_ALLOWED,
    ),
    (
        "api.states.create",
        405,
        ResidualUnauthenticatedClassification.PERMANENT_METHOD_NOT_ALLOWED,
    ),
    (
        "api.states.update",
        405,
        ResidualUnauthenticatedClassification.PERMANENT_METHOD_NOT_ALLOWED,
    ),
    (
        "api.transactions.create",
        401,
        ResidualUnauthenticatedClassification.AUTHENTICATION_GATED,
    ),
    (
        "api.transactions.update",
        401,
        ResidualUnauthenticatedClassification.AUTHENTICATION_GATED,
    ),
    (
        "api.transactions.delete",
        200,
        ResidualUnauthenticatedClassification.METADATA_ONLY_UNQUALIFIED,
    ),
    (
        "api.zipcodes.create",
        405,
        ResidualUnauthenticatedClassification.PERMANENT_METHOD_NOT_ALLOWED,
    ),
    (
        "api.zipcodes.update",
        405,
        ResidualUnauthenticatedClassification.PERMANENT_METHOD_NOT_ALLOWED,
    ),
)

_RESEARCH96_RESIDUAL_UNAUTHENTICATED_OUTCOMES: Final[ResidualUnauthenticatedOutcomeFixture] = (
    ResidualUnauthenticatedOutcomeFixture(
        outcomes=tuple(
            ResidualUnauthenticatedOutcome(
                candidate_id=candidate_id,
                unauthenticated_status_code=status_code,
                classification=classification,
            )
            for candidate_id, status_code, classification in _RESEARCH96_RESIDUAL_OUTCOMES
        )
    )
)

_RESEARCH96_CANONICAL_BULK_DELETE_FORM: Final[CanonicalBulkDeleteForm] = CanonicalBulkDeleteForm()

_RESEARCH96_REJECTED_BULK_DELETE_BODY_FORMS: Final[tuple[BulkDeleteRejectedBodyForm, ...]] = (
    BulkDeleteRejectedBodyForm(
        form=BulkDeleteRejectedBodyFormKind.JSON_BODY,
        unauthenticated_status_code=400,
        error_code=BULK_DELETE_EMPTY_ERROR_CODE,
        classification=BulkDeleteWireClassification.REJECTED_NON_PRODUCT_BODY,
    ),
    BulkDeleteRejectedBodyForm(
        form=BulkDeleteRejectedBodyFormKind.FORM_BODY,
        unauthenticated_status_code=400,
        error_code=BULK_DELETE_EMPTY_ERROR_CODE,
        classification=BulkDeleteWireClassification.REJECTED_NON_PRODUCT_BODY,
    ),
)

_RESEARCH96_ORGANIZATION_PATH_AMBIGUITY: Final[OrganizationPathAmbiguityFixture] = (
    OrganizationPathAmbiguityFixture(
        no_token_outcomes=(
            OrganizationPathNoTokenOutcome(
                route="/user/organizations",
                unauthenticated_status_code=404,
                error_code="UNKNOWN_RESOURCE",
                classification=OrganizationPathClassification.UNKNOWN_RESOURCE,
            ),
            OrganizationPathNoTokenOutcome(
                route="/organizations",
                unauthenticated_status_code=401,
                error_code="AUTHENTICATION_REQUIRED",
                classification=OrganizationPathClassification.AUTHENTICATION_REQUIRED,
            ),
        ),
        invalid_token_outcome=OrganizationPathInvalidTokenOutcome(
            status_code=401,
            error_code="OAUTH_INVALID_ACCESS_TOKEN",
            classification=OrganizationPathClassification.AUTH_FIRST_PATH_AGNOSTIC,
        ),
    )
)


def research96_residual_unauthenticated_outcomes() -> ResidualUnauthenticatedOutcomeFixture:
    """Return the static exact-29 residual outcome fixture without issuing a request."""

    return _RESEARCH96_RESIDUAL_UNAUTHENTICATED_OUTCOMES


def research96_canonical_bulk_delete_form() -> CanonicalBulkDeleteForm:
    """Return the no-input query-only bulk-delete fixture without building a request."""

    return _RESEARCH96_CANONICAL_BULK_DELETE_FORM


def research96_rejected_bulk_delete_body_forms() -> tuple[BulkDeleteRejectedBodyForm, ...]:
    """Return the explicit rejected JSON and form-body bulk-delete forms."""

    return _RESEARCH96_REJECTED_BULK_DELETE_BODY_FORMS


def research96_organization_path_ambiguity() -> OrganizationPathAmbiguityFixture:
    """Return static path ambiguity evidence without inferring or probing a route."""

    return _RESEARCH96_ORGANIZATION_PATH_AMBIGUITY


def _fixed_observation_url(candidate: LiveProbeCandidate) -> str:
    """Build a candidate URL without accepting caller-controlled hosts or paths."""

    parsed = urlsplit(candidate.observation_route)
    if parsed.scheme or parsed.netloc or parsed.query or parsed.fragment:
        raise ValueError("candidate route must be a path beneath the fixed Billy API base")
    if not candidate.observation_route.startswith("/"):
        raise ValueError("candidate route must be an absolute-relative path")
    return f"{API_BASE_URL}{candidate.observation_route}"


class LiveProbeRunner:
    """Run bounded, non-mutating observations after all fail-closed gates pass."""

    def __init__(
        self,
        configuration: LiveProbeConfig,
        *,
        transport: httpx.BaseTransport | None = None,
    ) -> None:
        self._configuration = configuration
        self._transport = transport

    def run(self, environment: Mapping[str, str] | None = None) -> LiveProbeResult:
        """Resolve the token locally and run no more than the frozen 121 observations."""

        source = os.environ if environment is None else environment
        token = source.get("BILLY_API_TOKEN")
        candidates = research88_candidates()
        if not token:
            return LiveProbeResult(
                status=ProbeStatus.SKIPPED_NO_TOKEN,
                candidate_count=len(candidates),
                observation_count=0,
                evidence_written=False,
            )
        organization_status = self._organization_status()
        if organization_status is not None:
            return LiveProbeResult(
                status=organization_status,
                candidate_count=len(candidates),
                observation_count=0,
                evidence_written=False,
            )
        try:
            evidence_directory = _ensure_evidence_directory(
                self._configuration.evidence_directory,
                repository_root=self._configuration.repository_root,
            )
        except EvidenceDirectoryError:
            return LiveProbeResult(
                status=ProbeStatus.BLOCKED_EVIDENCE_DIRECTORY,
                candidate_count=len(candidates),
                observation_count=0,
                evidence_written=False,
            )
        observations = self._observe(candidates, token)
        evidence = LiveProbeEvidence(
            run_tag=f"wave5t-{uuid.uuid4().hex}",
            observations=observations,
        )
        try:
            _write_evidence(evidence_directory, evidence)
        except OSError:
            return LiveProbeResult(
                status=ProbeStatus.EVIDENCE_WRITE_FAILED,
                candidate_count=len(candidates),
                observation_count=len(observations),
                evidence_written=False,
            )
        return LiveProbeResult(
            status=ProbeStatus.OBSERVED_UNQUALIFIED,
            candidate_count=len(candidates),
            observation_count=len(observations),
            evidence_written=True,
        )

    def _organization_status(self) -> ProbeStatus | None:
        test_organization = self._configuration.test_organization_id
        guard = self._configuration.test_organization_guard
        if test_organization is None or guard is None:
            return ProbeStatus.BLOCKED_MISSING_TEST_ORGANIZATION
        if test_organization != guard:
            return ProbeStatus.BLOCKED_TEST_ORGANIZATION_MISMATCH
        return None

    def _observe(
        self,
        candidates: tuple[LiveProbeCandidate, ...],
        token: str,
    ) -> tuple[LiveProbeObservation, ...]:
        """Observe only static OPTIONS endpoints and retain no response body or headers."""

        observations: list[LiveProbeObservation] = []
        with httpx.Client(transport=self._transport, timeout=20.0) as client:
            for candidate in candidates:
                try:
                    response = client.request(
                        OBSERVATION_METHOD,
                        _fixed_observation_url(candidate),
                        headers={"X-Access-Token": token, "Accept": "application/json"},
                        params={name: "" for name in candidate.query_names} or None,
                    )
                except httpx.TransportError:
                    observations.append(
                        LiveProbeObservation(
                            candidate_id=candidate.id,
                            candidate_method=candidate.candidate_method,
                            route=candidate.route,
                            state=CandidateObservationState.TRANSPORT_UNAVAILABLE,
                        )
                    )
                    continue
                observations.append(
                    LiveProbeObservation(
                        candidate_id=candidate.id,
                        candidate_method=candidate.candidate_method,
                        route=candidate.route,
                        status_code=response.status_code,
                        state=CandidateObservationState.UNQUALIFIED,
                    )
                )
        return tuple(observations)


class EvidenceDirectoryError(ValueError):
    """Raised before network activity when evidence cannot be kept owner-only."""


def _ensure_evidence_directory(path: Path, *, repository_root: Path) -> Path:
    """Create and validate the one owner-only evidence directory outside the repository."""

    candidate = path.expanduser()
    if not candidate.is_absolute():
        raise EvidenceDirectoryError("evidence directory must be absolute")
    resolved = candidate.resolve(strict=False)
    repository = repository_root.expanduser().resolve(strict=False)
    if resolved.is_relative_to(repository):
        raise EvidenceDirectoryError("evidence directory must be outside the repository")
    resolved.mkdir(parents=True, mode=0o700, exist_ok=True)
    os.chmod(resolved, 0o700)
    details = resolved.stat()
    if not stat.S_ISDIR(details.st_mode):
        raise EvidenceDirectoryError("evidence path is not a directory")
    if details.st_uid != os.getuid():
        raise EvidenceDirectoryError("evidence directory is not owned by this account")
    if stat.S_IMODE(details.st_mode) != 0o700:
        raise EvidenceDirectoryError("evidence directory must have mode 0700")
    return resolved


def _write_evidence(directory: Path, evidence: LiveProbeEvidence) -> Path:
    """Persist only redacted metadata in a unique owner-readable evidence file."""

    target = directory / f"{evidence.run_tag}.json"
    with target.open("x", encoding="utf-8") as handle:
        handle.write(evidence.model_dump_json(indent=2))
        handle.write("\n")
    os.chmod(target, 0o600)
    return target


def load_live_probe_config(
    environment: Mapping[str, str] | None = None,
    *,
    repository_root: Path | None = None,
) -> LiveProbeConfig:
    """Convert invalid external settings to a typed configuration error for the CLI."""

    try:
        return LiveProbeConfig.from_environment(environment, repository_root=repository_root)
    except ValidationError:
        raise
