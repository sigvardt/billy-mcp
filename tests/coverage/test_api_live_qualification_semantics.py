"""Owner 7C9348E1: API live_tested stays false with live_api out_of_scope_by_user."""

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

LIVE_API: Final[str] = "out_of_scope_by_user"
DEFERRED_KIND: Final[str] = "live_api_deferred"
DEFERRED_SCOPE: Final[str] = "LIVE_API_OWNER_SKIP"


def _api_rows() -> list[dict[str, Any]]:
    document = checker.load_document(ROOT / "coverage" / "api_v2_manifest.yaml")
    return list(document["operations"])


def _toy_api(
    *,
    live_tested: bool,
    live_api: str | None,
    source_kind: str = "clear",
) -> dict[str, Any]:
    row: dict[str, Any] = {
        "id": "api.products.list",
        "source_kind": source_kind,
        "discovered": True,
        "implemented": True,
        "contract_tested": True,
        "live_tested": live_tested,
    }
    if live_api is not None:
        row["qualification"] = {"live_api": live_api, "kind": DEFERRED_KIND}
    return row


def _toy_ui() -> dict[str, Any]:
    return {
        "id": "ui.parity.products.list",
        "workflow_kind": "api_parity",
        "discovered": True,
        "implemented": True,
        "contract_tested": True,
        "live_tested": True,
        "vision_verified": True,
    }


def test_every_api_row_keeps_live_tested_false() -> None:
    """Given the API inventory, When reading each row, Then live_tested is false."""

    rows = _api_rows()
    assert len(rows) == 305
    for row in rows:
        assert row["live_tested"] is False, f"{row['id']}: live_tested is {row['live_tested']!r}"


def test_every_api_row_carries_live_api_out_of_scope() -> None:
    """Given the API inventory, When reading qualification, Then live_api is set."""

    missing = [
        str(row["id"])
        for row in _api_rows()
        if generator.api_qualification_live_api(row) != LIVE_API
    ]
    assert missing == [], f"API rows missing live_api={LIVE_API}: {missing[:12]}"


def test_no_api_row_uses_owner_skip_kind() -> None:
    """Given API rows, When reading kind, Then none are out_of_scope_by_user."""

    bad = [
        str(row["id"])
        for row in _api_rows()
        if isinstance(row.get("qualification"), dict)
        and row["qualification"].get("kind") == "out_of_scope_by_user"
    ]
    assert bad == [], f"API operations classified out of scope: {bad}"


def test_implemented_api_rows_use_live_api_deferred() -> None:
    """Given implemented API rows, When reading qualification, Then they are deferred."""

    implemented = [row for row in _api_rows() if row["implemented"] is True]
    assert len(implemented) == 203
    for row in implemented:
        qual = dict(row.get("qualification") or {})
        assert qual.get("kind") == DEFERRED_KIND, f"{row['id']}: kind={qual.get('kind')!r}"
        assert qual.get("scope_code") == DEFERRED_SCOPE
        assert qual.get("live_api") == LIVE_API
        if row["id"] == "api.files.create":
            assert row["tool_name"] == ""
        else:
            assert row["tool_name"], f"{row['id']}: implemented row lost its tool"
        assert qual.get("tools_allowed") is not False


def test_residual_and_bulk_keep_existing_kinds() -> None:
    """Given residual and bulk rows, When reading qualification, Then kinds stay."""

    by_id = {str(row["id"]): row for row in _api_rows()}
    for row_id in generator.RESIDUAL_METHOD_CLOSED_IDS:
        qual = dict(by_id[row_id].get("qualification") or {})
        assert qual["kind"] == "method_closed_offline"
        assert qual["tools_allowed"] is False
        assert qual["live_api"] == LIVE_API
    for row_id in generator.RESIDUAL_READONLY_MAP_IDS:
        qual = dict(by_id[row_id].get("qualification") or {})
        assert qual["kind"] == "readonly_field_map_insufficient"
        assert qual["tools_allowed"] is False
    for row_id in generator.RESIDUAL_META_DELETE_IDS:
        qual = dict(by_id[row_id].get("qualification") or {})
        assert qual["kind"] == "meta_delete_unqualified"
        assert qual["tools_allowed"] is False
    bulk = [row for row in _api_rows() if row["source_kind"] == "ambiguous_bulk"]
    assert len(bulk) == 92
    for row in bulk:
        qual = dict(row.get("qualification") or {})
        assert qual["kind"] == "external_contract_blocker"
        assert qual["tools_allowed"] is False
        assert qual["live_api"] == LIVE_API


def test_completeness_rejects_api_live_tested_true() -> None:
    """Given an API row with live_tested true, When scoring complete, Then false."""

    assert (
        generator.coverage_is_complete(
            [_toy_api(live_tested=True, live_api=LIVE_API)],
            [_toy_ui()],
        )
        is False
    )


def test_completeness_accepts_deferred_live_api() -> None:
    """Given offline-green API with live_api set, When scoring complete, Then true."""

    assert (
        generator.coverage_is_complete(
            [_toy_api(live_tested=False, live_api=LIVE_API)],
            [_toy_ui()],
        )
        is True
    )


def test_require_complete_uses_live_api_not_live_tested_true() -> None:
    """Given the release gate, When API live_tested is false with live_api, Then it can pass."""

    qualified_api = [_toy_api(live_tested=False, live_api=LIVE_API)]
    qualified_ui = [_toy_ui()]
    complete_status = {"complete": True}
    assert checker.require_complete_errors(qualified_api, qualified_ui, complete_status) == []

    live_true = [_toy_api(live_tested=True, live_api=LIVE_API)]
    live_true_errors = checker.require_complete_errors(live_true, qualified_ui, complete_status)
    assert any("live_tested must stay false" in error for error in live_true_errors)

    missing = [_toy_api(live_tested=False, live_api=None)]
    missing_errors = checker.require_complete_errors(missing, qualified_ui, complete_status)
    assert any("live_api" in error for error in missing_errors)

    bulk = [_toy_api(live_tested=False, live_api=LIVE_API, source_kind="ambiguous_bulk")]
    bulk_errors = checker.require_complete_errors(bulk, qualified_ui, complete_status)
    assert any("no ambiguous_bulk rows" in error for error in bulk_errors)


def test_generated_status_stays_incomplete() -> None:
    """Given generated status, When reading complete, Then it stays false."""

    status = checker.load_document(ROOT / "coverage" / "status.json")
    assert status["complete"] is False
    assert status["qualification"]["live_tested_rows"] == 339
