"""Owner 89DEED22: official docs lock matches the captured 2026-08-19 page."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from types import ModuleType
from typing import Any, Final

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))


def _load_script_module(name: str) -> ModuleType:
    spec = importlib.util.spec_from_file_location(name, SCRIPTS / f"{name}.py")
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


checker = _load_script_module("check_coverage")
generator = _load_script_module("generate_coverage_report")

LIVE_ETAG: Final[str] = "tmhc6wpdc835zt"
LIVE_MD5: Final[str] = "053f755f52e3926b028e29325e3670d4"
LIVE_API: Final[str] = "out_of_scope_by_user"


def _api_manifest() -> dict[str, Any]:
    return checker.load_document(ROOT / "coverage" / "api_v2_manifest.yaml")


def _status() -> dict[str, Any]:
    return checker.load_document(ROOT / "coverage" / "status.json")


def _api_rows() -> list[dict[str, Any]]:
    return list(_api_manifest()["operations"])


def _row(row_id: str) -> dict[str, Any]:
    by_id = {str(row["id"]): row for row in _api_rows()}
    return by_id[row_id]


def test_generator_lock_matches_captured_live_page() -> None:
    """Given the generator constants, When reading the lock, Then it is the live page."""

    assert generator.DOCS_ETAG == LIVE_ETAG
    assert generator.DOCS_MD5 == LIVE_MD5
    assert generator.DOCS_ETAG_OBSERVED == generator.DOCS_ETAG
    assert generator.DOCS_MD5_OBSERVED == generator.DOCS_MD5


def test_generated_official_docs_match_live_lock() -> None:
    """Given generated artifacts, When reading official_docs, Then etag and md5 match."""

    status_docs = dict(_status()["official_docs"])
    manifest_docs = dict(_api_manifest()["official_docs"])
    assert status_docs["etag"] == LIVE_ETAG
    assert status_docs["md5"] == LIVE_MD5
    assert manifest_docs["etag"] == LIVE_ETAG
    assert manifest_docs["md5"] == LIVE_MD5


def test_organizations_list_stays_collection_route() -> None:
    """Given api.organizations.list, When reading the row, Then the collection path stays."""

    row = _row("api.organizations.list")
    assert row["method_or_route"] == "GET /v2/organizations"
    assert row["tool_name"] == "api_organizations_list"


def test_user_organizations_special_is_kept() -> None:
    """Given the special row, When reading it, Then the historical tool path stays."""

    row = _row("api.special.user_organizations")
    assert row["method_or_route"] == "GET /v2/user/organizations"
    assert row["tool_name"] == "api_user_list_organizations"
    evidence = str(row["evidence"])
    assert "GET /v2/organizations" in evidence
    assert "/user/organizations" in evidence


def test_bulk_and_residual_stay_red() -> None:
    """Given bulk and residual honesty rows, When reading them, Then they stay toolless."""

    bulk = [row for row in _api_rows() if row["source_kind"] == "ambiguous_bulk"]
    assert len(bulk) == 92
    for row in bulk:
        assert row["tool_name"] == ""
        assert row["implemented"] is False
    residual_ids = generator.RESIDUAL_CLEAR_HONESTY_IDS
    assert len(residual_ids) == 24
    by_id = {str(row["id"]): row for row in _api_rows()}
    for row_id in residual_ids:
        row = by_id[row_id]
        assert row["tool_name"] == ""
        assert row["implemented"] is False


def test_complete_stays_false_and_api_live_tested_stays_false() -> None:
    """Given generated coverage, When scoring complete, Then it stays false."""

    assert _status()["complete"] is False
    rows = _api_rows()
    assert len(rows) == 305
    for row in rows:
        row_id = str(row["id"])
        assert row["live_tested"] is False, f"{row_id}: live_tested is {row['live_tested']!r}"
        assert generator.api_qualification_live_api(row) == LIVE_API, f"{row_id} missing live_api"
