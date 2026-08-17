"""Given live other_v2 rows, When checking route keys, Then F12B607E fields are missing."""

from __future__ import annotations

from pathlib import Path
from typing import Final

_LIVE_OTHER_V2_ROWS: Final[list[dict[str, object]]] = [
    {"method": "GET", "path_class": "other_v2", "status": 200, "timing_ms": 51},
    {"method": "GET", "path_class": "other_v2", "status": 200, "timing_ms": 71},
    {"method": "GET", "path_class": "other_v2", "status": 200, "timing_ms": 90},
    {"method": "GET", "path_class": "other_v2", "status": 200, "timing_ms": 71},
    {"method": "GET", "path_class": "other_v2", "status": 200, "timing_ms": 489},
]
_REQUIRED: Final[list[str]] = ["route_class", "timing_bucket", "phase"]


def test_live_other_v2_rows_miss_f12b607e_route_keys() -> None:
    """Given the five live other_v2 rows, When checking route keys, Then they are missing."""

    from billy_mcp.ui_writes.invoices_kunde_routes import (
        REQUIRED_KUNDE_ROUTE_KEYS,
        kunde_route_missing_keys,
    )

    missing = kunde_route_missing_keys(_LIVE_OTHER_V2_ROWS)
    assert missing == _REQUIRED
    assert set(_REQUIRED).issubset(REQUIRED_KUNDE_ROUTE_KEYS)
    for row in _LIVE_OTHER_V2_ROWS:
        assert "route_class" not in row
        assert "timing_bucket" not in row
        assert "phase" not in row


def test_complete_route_row_has_no_missing_keys() -> None:
    """Given a filled other_v2 row, When checking keys, Then none are missing."""

    from billy_mcp.ui_writes.invoices_kunde_routes import (
        contact_dataset_preloaded,
        empty_kunde_route_row,
        kunde_route_missing_keys,
        route_class_for,
        sanitize_v2_route_template,
        timing_bucket_for,
    )

    row = empty_kunde_route_row()
    assert kunde_route_missing_keys([row]) == []
    assert sanitize_v2_route_template("/v2/products?q=secret") == "/v2/products"
    assert (
        sanitize_v2_route_template("/v2/contactPersons/aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee")
        == "/v2/contactPersons/:uuid"
    )
    assert sanitize_v2_route_template("/v2/users/0123456789abcdef0123456789abcdef") == (
        "/v2/users/:id"
    )
    assert sanitize_v2_route_template("/v2/taxRates/12") == "/v2/taxRates/:n"
    assert (
        sanitize_v2_route_template("/v2/organizations/example-org-slug/bootstrap")
        == "/v2/organizations/:id/bootstrap"
    )
    assert (
        sanitize_v2_route_template("/v2/organizations/AbCdEfGhIjKlMnOpQrStUv/campaign")
        == "/v2/organizations/:id/campaign"
    )
    assert route_class_for("/v2/products") == "products"
    assert route_class_for("/v2/contacts") == "contacts"
    assert route_class_for("/v2/unknownThing") == "other_v2"
    assert timing_bucket_for(51) == "50_99"
    assert timing_bucket_for(71) == "50_99"
    assert timing_bucket_for(90) == "50_99"
    assert timing_bucket_for(489) == "250_499"
    assert contact_dataset_preloaded([row]) is False
    adjacent = empty_kunde_route_row()
    adjacent["route_class"] = "contactPersons"
    adjacent["phase"] = "at_rest"
    assert contact_dataset_preloaded([adjacent]) is True
    later = empty_kunde_route_row()
    later["route_class"] = "contactPersons"
    later["phase"] = "after_type"
    assert contact_dataset_preloaded([later]) is False


def test_redact_route_request_omits_url_and_template() -> None:
    """Given a raw URL, When redacting, Then committed keys omit path and query."""

    from billy_mcp.ui_writes.invoices_kunde_routes import redact_route_request

    row = redact_route_request(
        method="get",
        path_class="other_v2",
        status=200,
        timing_ms=71,
        url="https://api.billysbilling.com/v2/products?q=MCP-UI-INV-DEADBEEF",
        phase="at_rest",
    )
    encoded = str(row)
    assert "products" in {row["route_class"]}
    assert row["timing_bucket"] == "50_99"
    assert row["phase"] == "at_rest"
    assert "MCP-UI" not in encoded
    assert "q=" not in encoded
    assert "billysbilling" not in encoded
    assert "route_template" not in row


def test_sink_records_route_keys_without_url() -> None:
    """Given a /v2/products response, When the sink stores it, Then route keys exist."""

    from billy_mcp.ui_writes.invoices_form_observe import KundeTraceSink

    sink = KundeTraceSink()
    sink.current_phase = "at_rest"
    sink.note_request(1, "GET", "https://api.billysbilling.com/v2/products?q=secret")
    sink.note_response(1, "GET", "https://api.billysbilling.com/v2/products?q=secret", 200)
    row = sink.requests[0]
    assert row["route_class"] == "products"
    assert row["timing_bucket"] in {"0_49", "50_99", "100_249", "250_499", "500_plus"}
    assert row["phase"] == "at_rest"
    encoded = str(sink.requests) + str(sink.route_templates)
    assert "secret" not in encoded
    assert "q=" not in encoded
    assert sink.route_templates == ["/v2/products"]


def test_apply_route_dump_writes_isolated_templates(tmp_path: Path) -> None:
    """Given templates, When applying the dump, Then owner file is isolated."""

    from billy_mcp.ui_writes.invoices_kunde_routes import apply_kunde_route_dump

    target = tmp_path / "routes.json"
    result = apply_kunde_route_dump(
        {
            "at_rest": {
                "requests": [
                    {
                        "method": "GET",
                        "path_class": "other_v2",
                        "status": 200,
                        "timing_ms": 51,
                        "route_class": "products",
                        "timing_bucket": "50_99",
                        "phase": "at_rest",
                    }
                ]
            }
        },
        ["/v2/products"],
        template_path=target,
    )
    assert result["kunde_route_missing_keys"] == []
    assert result["contact_dataset_preloaded"] is False
    assert target.is_file()
    assert "products" in target.read_text(encoding="utf-8")
    assert "secret" not in target.read_text(encoding="utf-8")
