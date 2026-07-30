"""Opt-in live safety checks for the Wave-5t residual/bulk observation gate."""

from __future__ import annotations

import os
from pathlib import Path

import pytest

from billy_mcp.live_probe import LiveProbeConfig, LiveProbeRunner, ProbeStatus

pytestmark = pytest.mark.live


def test_live_probe_skips_without_an_explicit_non_production_opt_in(tmp_path: Path) -> None:
    """Never send traffic merely because a developer happens to have a token set."""

    if os.environ.get("BILLY_LIVE_PROBE_RUN") != "1":
        pytest.skip("set BILLY_LIVE_PROBE_RUN=1 for the dedicated non-production gate")
    token = os.environ.get("BILLY_API_TOKEN")
    organization = os.environ.get("BILLY_TEST_ORGANIZATION_ID")
    guard = os.environ.get("BILLY_LIVE_PROBE_ORGANIZATION_GUARD")
    if not token or not organization or organization != guard:
        pytest.skip("dedicated non-production token and matching organisation guard are required")
    assert guard is not None

    result = LiveProbeRunner(
        LiveProbeConfig(
            test_organization_id=organization,
            test_organization_guard=guard,
            evidence_directory=tmp_path / "owner-only-evidence",
            repository_root=Path.cwd(),
        )
    ).run(
        {
            "BILLY_API_TOKEN": token,
            "BILLY_TEST_ORGANIZATION_ID": organization,
            "BILLY_LIVE_PROBE_ORGANIZATION_GUARD": guard,
        }
    )

    assert result.status is ProbeStatus.OBSERVED_UNQUALIFIED
    assert result.observation_count == 121
    assert result.evidence_written is True
