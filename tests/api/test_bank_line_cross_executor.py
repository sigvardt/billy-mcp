"""Integration tests for root-shared bank-line write tickets."""

from __future__ import annotations

import asyncio
from collections.abc import Mapping
from typing import cast

from fastmcp import FastMCP
from pytest import MonkeyPatch

from billy_mcp.client import BillyHttpClient, BillyResponse
from billy_mcp.models import StableErrorCode
from billy_mcp.server import create_server


def call_tool(server: FastMCP, tool_name: str, arguments: dict[str, object]) -> dict[str, object]:
    """Call one typed root-server tool and return its structured payload."""

    result = asyncio.run(server.call_tool(tool_name, arguments))
    structured_content = result.structured_content
    assert isinstance(structured_content, dict)
    payload = structured_content.get("result", structured_content)
    assert isinstance(payload, dict)
    return cast(dict[str, object], payload)


def test_root_shared_service_rejects_wrong_executors_before_consume_and_http(
    monkeypatch: MonkeyPatch,
) -> None:
    """Wrong same- and cross-resource executors leave exact tickets usable."""

    requests: list[tuple[str, str, object | None]] = []

    def fake_request(
        self: BillyHttpClient,
        method: str,
        path: str,
        *,
        params: Mapping[str, str | int | float | bool] | None = None,
        json_body: object | None = None,
    ) -> BillyResponse:
        del self, params
        requests.append((method, path, json_body))
        if path == "/bankLineMatches":
            return BillyResponse(
                200,
                {
                    "bankLineMatches": [{"id": "match-1"}],
                    "bankLines": [{"id": "line-1"}],
                },
            )
        if path == "/bankLines":
            return BillyResponse(200, {"bankLines": [{"id": "line-1"}]})
        if path == "/bankLineSubjectAssociations":
            return BillyResponse(
                200,
                {"bankLineSubjectAssociations": [{"id": "association-1"}]},
            )
        raise AssertionError(f"unexpected request: {method} {path}")

    monkeypatch.setattr(BillyHttpClient, "request", fake_request)
    server = create_server()

    match_preview = call_tool(
        server,
        "api_bank_line_matches_create_preview",
        {"bankLineMatch": {"opaque": "match"}},
    )
    for wrong_executor in (
        "api_bank_line_matches_delete_execute",
        "api_bank_lines_create_execute",
        "api_bank_line_subject_associations_create_execute",
    ):
        mismatch = call_tool(
            server,
            wrong_executor,
            {"confirmation_ticket": match_preview["confirmation_ticket"]},
        )
        assert mismatch["code"] == StableErrorCode.CONFIRMATION_MISMATCH
        assert requests == []

    match_execution = call_tool(
        server,
        "api_bank_line_matches_create_execute",
        {"confirmation_ticket": match_preview["confirmation_ticket"]},
    )
    assert match_execution["changed_records"] == {
        "bankLineMatches": [{"id": "match-1"}],
        "bankLines": [{"id": "line-1"}],
    }
    assert requests == [("POST", "/bankLineMatches", {"bankLineMatch": {"opaque": "match"}})]

    line_preview = call_tool(
        server,
        "api_bank_lines_create_preview",
        {"bankLine": {"opaque": "line"}},
    )
    line_mismatch = call_tool(
        server,
        "api_bank_line_subject_associations_create_execute",
        {"confirmation_ticket": line_preview["confirmation_ticket"]},
    )
    assert line_mismatch["code"] == StableErrorCode.CONFIRMATION_MISMATCH
    assert len(requests) == 1

    line_execution = call_tool(
        server,
        "api_bank_lines_create_execute",
        {"confirmation_ticket": line_preview["confirmation_ticket"]},
    )
    assert line_execution["changed_records"] == {"bankLines": [{"id": "line-1"}]}
    assert requests[-1] == ("POST", "/bankLines", {"bankLine": {"opaque": "line"}})

    association_preview = call_tool(
        server,
        "api_bank_line_subject_associations_create_preview",
        {"bankLineSubjectAssociation": {"opaque": "association"}},
    )
    association_mismatch = call_tool(
        server,
        "api_bank_line_matches_create_execute",
        {"confirmation_ticket": association_preview["confirmation_ticket"]},
    )
    assert association_mismatch["code"] == StableErrorCode.CONFIRMATION_MISMATCH
    assert len(requests) == 2

    association_execution = call_tool(
        server,
        "api_bank_line_subject_associations_create_execute",
        {"confirmation_ticket": association_preview["confirmation_ticket"]},
    )
    assert association_execution["changed_records"] == {
        "bankLineSubjectAssociations": [{"id": "association-1"}]
    }
    assert requests[-1] == (
        "POST",
        "/bankLineSubjectAssociations",
        {"bankLineSubjectAssociation": {"opaque": "association"}},
    )
