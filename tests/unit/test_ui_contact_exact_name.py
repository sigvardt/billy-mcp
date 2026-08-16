"""Exact contact-name match. Substring `{tag}` must not hit `{tag}-U`."""

from billy_mcp.ui_writes.page_flow import exact_name_in_text


def test_updated_tag_is_not_a_hit_for_the_original() -> None:
    # Given: a list body that only shows the renamed customer
    body = "Kontakter\nMCP-UI-C-AAAA-U\nMere"

    # When: the observer looks for the original tag
    found = exact_name_in_text(body, "MCP-UI-C-AAAA")

    # Then: the original tag is absent
    assert found is False


def test_updated_tag_is_a_hit_for_itself() -> None:
    body = "Kontakter\nMCP-UI-C-AAAA-U\nMere"

    found = exact_name_in_text(body, "MCP-UI-C-AAAA-U")

    assert found is True


def test_empty_list_is_not_a_hit() -> None:
    found = exact_name_in_text("Kontakter\nIngen kunder", "MCP-UI-C-AAAA")

    assert found is False
