"""Typed loading of generated coverage data without completeness invention."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Literal, cast

import yaml
from pydantic import BaseModel, ConfigDict, Field

from billy_mcp.errors import unavailable_coverage_error
from billy_mcp.models import CoverageStatus, StableErrorCode, ToolError

_REQUIRED_FILES = (
    "api_v2_manifest.yaml",
    "ui_workflows_manifest.yaml",
    "browser_egress.yaml",
    "status.json",
)


class CoverageRow(BaseModel):
    """The shared coverage-row core that Phase 0 manifests expose."""

    model_config = ConfigDict(extra="allow")

    id: str
    lane: Literal["api", "ui"]
    area: str
    operation: str
    method_or_route: str
    request_fields: list[str] = Field(default_factory=list)
    response_fields: list[str] = Field(default_factory=list)
    filters: list[str] | dict[str, object] = Field(default_factory=list)
    pagination: str | dict[str, object] | None = None
    errors: list[str] | str = Field(default_factory=list)
    side_effects: str = "unknown"
    cleanup: str = "unknown"
    tool_name: str = ""
    evidence: str = ""
    vision_evidence: object = None
    qualification: dict[str, object] = Field(default_factory=dict)
    status: CoverageStatus = Field(default_factory=CoverageStatus)

    @classmethod
    def from_manifest(cls, raw: dict[str, object]) -> CoverageRow:
        status_fields = {
            key: raw.pop(key)
            for key in (
                "discovered",
                "implemented",
                "contract_tested",
                "live_tested",
                "vision_verified",
            )
            if key in raw
        }
        return cls.model_validate({**raw, "status": status_fields})


class GeneratedCoverageStatus(BaseModel):
    """Generated machine status; it is authoritative and never inferred by this loader."""

    model_config = ConfigDict(extra="allow")

    complete: bool
    phase: str | None = None
    source_counts: dict[str, int] = Field(default_factory=dict)
    qualification: dict[str, object] = Field(default_factory=dict)


class CoverageReport(BaseModel):
    """Typed report assembled from the sibling coverage inventory artifacts."""

    model_config = ConfigDict(extra="forbid")

    status: GeneratedCoverageStatus
    api_rows: list[CoverageRow]
    ui_rows: list[CoverageRow]
    browser_egress_entries: int


class CoverageLoadError(Exception):
    """Typed failure instead of a fabricated empty or green report."""

    def __init__(self, error: ToolError) -> None:
        self.error = error
        super().__init__(error.message)


def load_coverage_report(repository_root: Path) -> CoverageReport:
    """Load all required sibling inventory artifacts or report their exact absence."""

    coverage_root = repository_root / "coverage"
    missing = [name for name in _REQUIRED_FILES if not (coverage_root / name).is_file()]
    if missing:
        raise CoverageLoadError(unavailable_coverage_error(missing))
    api_rows = _load_rows(coverage_root / "api_v2_manifest.yaml", "operations")
    ui_rows = _load_rows(coverage_root / "ui_workflows_manifest.yaml", "workflows")
    browser_entries = _load_entries(coverage_root / "browser_egress.yaml", "hosts")
    with (coverage_root / "status.json").open(encoding="utf-8") as status_file:
        status = GeneratedCoverageStatus.model_validate(json.load(status_file))
    if status.complete and any(not _is_complete_eligible(row) for row in [*api_rows, *ui_rows]):
        raise CoverageLoadError(
            ToolError(
                code=StableErrorCode.VALIDATION_ERROR,
                message="Generated coverage status conflicts with red manifest rows.",
            )
        )
    return CoverageReport(
        status=status,
        api_rows=api_rows,
        ui_rows=ui_rows,
        browser_egress_entries=len(browser_entries),
    )


def _load_rows(path: Path, records_key: str) -> list[CoverageRow]:
    raw = _load_yaml(path)
    records = _records_from(raw, records_key)
    if not isinstance(records, list):
        raise CoverageLoadError(
            ToolError(
                code=StableErrorCode.VALIDATION_ERROR,
                message=f"Invalid coverage rows in {path.name}.",
            )
        )
    rows: list[CoverageRow] = []
    for record in cast(list[object], records):
        if not isinstance(record, dict):
            raise CoverageLoadError(
                ToolError(
                    code=StableErrorCode.VALIDATION_ERROR, message=f"Invalid row in {path.name}."
                )
            )
        rows.append(CoverageRow.from_manifest(dict(cast(dict[str, object], record))))
    return rows


def _load_entries(path: Path, records_key: str) -> list[object]:
    raw = _load_yaml(path)
    records = _records_from(raw, records_key)
    if not isinstance(records, list):
        raise CoverageLoadError(
            ToolError(
                code=StableErrorCode.VALIDATION_ERROR,
                message=f"Invalid egress entries in {path.name}.",
            )
        )
    return cast(list[object], records)


def _load_yaml(path: Path) -> object:
    with path.open(encoding="utf-8") as manifest_file:
        return cast(object, yaml.safe_load(manifest_file) or [])


def _records_from(raw: object, key: str) -> object:
    if not isinstance(raw, dict):
        return raw
    mapping = cast(dict[str, object], raw)
    return mapping[key] if key in mapping else cast(object, mapping)


def _is_green(row: CoverageRow) -> bool:
    status = row.status
    if row.lane == "api":
        return (
            status.discovered
            and status.implemented
            and status.contract_tested
            and status.live_tested is False
        )
    return (
        status.discovered
        and status.implemented
        and status.contract_tested
        and status.live_tested
        and status.vision_verified is True
    )


def _is_complete_eligible(row: CoverageRow) -> bool:
    """Match generated-status semantics without treating owner-scoped rows as green."""

    return row.qualification.get("kind") == "out_of_scope_by_user" or _is_green(row)
