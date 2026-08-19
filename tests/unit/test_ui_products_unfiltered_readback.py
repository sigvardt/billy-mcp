"""Offline source contract: product persist reads unfiltered /products first."""

from __future__ import annotations

from pathlib import Path


def _prove_text_paths(body: str) -> list[str]:
    """Return path= values from prove_text_on_fresh_page calls, in order."""

    paths: list[str] = []
    needle = "prove_text_on_fresh_page("
    start = 0
    while True:
        index = body.find(needle, start)
        if index < 0:
            break
        chunk = body[index : index + 280]
        if 'path="products"' in chunk:
            paths.append("products")
        elif 'path="inventory"' in chunk:
            paths.append("inventory")
        start = index + len(needle)
    return paths


def test_create_form_opens_from_products_list() -> None:
    """Owner C6DA7FC8: create starts on /products, not Lagermodul inventory."""

    from billy_mcp.ui_writes import products_submit

    body = Path(products_submit.__file__).read_text(encoding="utf-8")
    assert 'require_matching_org_slug(page, organization_id, "products")' in body
    assert 'f"{BILLY_ORIGIN}/{slug}/products"' in body


def test_create_readback_uses_products_path_before_inventory() -> None:
    """Owner C6DA7FC8: persist proof starts on /products, not /inventory."""

    from billy_mcp.ui_writes import products_submit

    body = Path(products_submit.__file__).read_text(encoding="utf-8")
    paths = _prove_text_paths(body)
    assert paths, "create execute must prove persist on a fresh page"
    assert paths[0] == "products"


def test_product_unfiltered_readback_does_not_search_first() -> None:
    """Owner C6DA7FC8: unfiltered exact-text count before any search fill."""

    from billy_mcp.ui_writes import products_delete, products_delete_row, products_submit

    submit = Path(products_submit.__file__).read_text(encoding="utf-8")
    delete = Path(products_delete.__file__).read_text(encoding="utf-8") + Path(
        products_delete_row.__file__
    ).read_text(encoding="utf-8")
    live = Path(__file__).resolve().parents[1] / "live" / "test_ui_products_writes.py"
    live_body = live.read_text(encoding="utf-8")

    assert submit.count("allow_search=False") >= 1
    assert submit.count("visible_body=True") >= 1
    text_at = delete.find("get_by_text(tag, exact=True)")
    search_at = delete.find("search.first.fill")
    assert text_at >= 0
    assert search_at == -1 or text_at < search_at
    live_text = live_body.find("get_by_text")
    if live_text < 0:
        live_text = live_body.find("exact_name_in_text")
    live_search = live_body.find("search.first.fill")
    assert live_text >= 0
    assert live_search == -1 or live_text < live_search
    assert "[data-cy='table-item']" in delete
    assert "force=True" not in delete
    assert "page.locator(_DELETE_ICON)" not in delete


def test_product_delete_absence_uses_table_item_not_body() -> None:
    """Owner C6DA7FC8 / IR 198.46: leftover absence is an unfiltered row, not body text."""

    from billy_mcp.ui_writes import products_delete, products_delete_row

    delete = Path(products_delete.__file__).read_text(encoding="utf-8") + Path(
        products_delete_row.__file__
    ).read_text(encoding="utf-8")
    prove = delete[delete.index("if not clicked") :]
    assert "visible_body=True" not in prove
    assert "prove_text_on_fresh_page" not in prove
    assert "prove_unfiltered_row_absent" in prove
    assert "TABLE_ITEM" in prove
    assert 'path="products"' in prove or "/products" in prove
    assert "_wait_row_gone" in delete


def test_hidden_ember_dialog_wrapper_is_not_leftover() -> None:
    """Owner C6DA7FC8: leftover heading/name without validation is not UI_CHANGED."""

    from billy_mcp.ui_writes.products_submit import leftover_create_dialog_message

    assert leftover_create_dialog_message(form_visible=False, validation="") is None
    assert leftover_create_dialog_message(form_visible=True, validation="") is None
    assert leftover_create_dialog_message(form_visible=True, validation="Påkrævet") == "Påkrævet"
