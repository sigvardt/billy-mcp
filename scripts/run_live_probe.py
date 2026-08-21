#!/usr/bin/env python3
"""Run the bounded Wave-5t live gate without exposing a generic HTTP interface."""

from __future__ import annotations

import sys
from pathlib import Path

from pydantic import ValidationError

from billy_mcp.live_probe import (
    LiveProbeResult,
    LiveProbeRunner,
    ProbeStatus,
    load_live_probe_config,
)


def main() -> int:
    """Print only the non-sensitive structured gate result."""

    try:
        configuration = load_live_probe_config(repository_root=Path.cwd())
    except ValidationError:
        result = LiveProbeResult(
            status=ProbeStatus.BLOCKED_EVIDENCE_DIRECTORY,
            candidate_count=0,
            observation_count=0,
            evidence_written=False,
        )
        print(result.model_dump_json())
        return 2
    result = LiveProbeRunner(configuration).run()
    print(result.model_dump_json())
    return 0 if result.status == ProbeStatus.SKIPPED_NO_TOKEN else int(not result.evidence_written)


if __name__ == "__main__":
    sys.exit(main())
