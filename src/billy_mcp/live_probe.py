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
