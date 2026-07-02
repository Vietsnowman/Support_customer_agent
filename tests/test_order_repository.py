from __future__ import annotations

from support_agent.repositories import OrderRepository


def test_verify_owner_is_case_insensitive(db_conn):
    repo = OrderRepository(db_conn)
    assert repo.verify_owner("MD-1052", "USER@EXAMPLE.COM") is True
    assert repo.verify_owner("MD-1052", "wrong@example.com") is False


def test_get_order_status_returns_allowlisted_fields(db_conn):
    repo = OrderRepository(db_conn)
    result = repo.get_order_status("MD-1052")
    assert result == {
        "order_id": "MD-1052",
        "order_status": "processing",
        "fulfillment_status": "shipped",
        "payment_status": "captured",
        "estimated_delivery": result["estimated_delivery"],
    }
    assert result["estimated_delivery"] is not None


def test_find_order_item_can_be_ambiguous(db_conn):
    repo = OrderRepository(db_conn)
    result = repo.find_order_item(
        "MD-1052",
        product_name="áo sơ mi xanh",
    )
    assert result.match_type == "ambiguous"
    assert [x.item_id for x in result.candidates] == ["ITEM-001", "ITEM-002"]


def test_find_order_item_by_item_id_is_single(db_conn):
    repo = OrderRepository(db_conn)
    result = repo.find_order_item("MD-1052", item_id="ITEM-001")
    assert result.match_type == "single"
    assert result.resolved_item is not None
    assert result.resolved_item.item_id == "ITEM-001"


def test_find_order_and_owner_aliases(db_conn):
    repo = OrderRepository(db_conn)

    order = repo.find_order("MD-1052")

    assert order is not None
    assert order.order_id == "MD-1052"
    assert repo.verify_order_owner("MD-1052", "USER@EXAMPLE.COM") is True


def test_owner_safe_order_helpers_block_wrong_email(db_conn):
    repo = OrderRepository(db_conn)

    assert repo.get_order_for_owner("MD-2012", "intruder@example.com") is None
    assert repo.get_order_status_for_owner("MD-2012", "intruder@example.com") is None
    assert repo.list_items_for_owner("MD-2012", "intruder@example.com") == []


def test_owner_safe_order_helpers_return_data_for_owner(db_conn):
    repo = OrderRepository(db_conn)

    order = repo.get_order_for_owner("MD-2012", "OWNER@EXAMPLE.COM")
    status = repo.get_order_status_for_owner("MD-2012", "owner@example.com")
    items = repo.list_items_for_owner("MD-2012", "owner@example.com")

    assert order is not None
    assert order.order_id == "MD-2012"
    assert status is not None
    assert set(status) == {
        "order_id",
        "order_status",
        "fulfillment_status",
        "payment_status",
        "estimated_delivery",
    }
    assert [item.item_id for item in items] == ["ITEM-020", "ITEM-032"]


def test_find_item_by_name_can_return_single_and_none(db_conn):
    repo = OrderRepository(db_conn)

    single = repo.find_item_by_name("MD-2013", "bàn phím cơ")
    missing = repo.find_item_by_name("MD-2013", "áo len")

    assert single.match_type == "single"
    assert single.resolved_item is not None
    assert single.resolved_item.item_id == "ITEM-021"
    assert missing.match_type == "none"


def test_find_order_item_by_id_wrapper(db_conn):
    repo = OrderRepository(db_conn)

    item = repo.find_order_item_by_id("MD-1052", "ITEM-001")

    assert item is not None
    assert item.product_name == "Áo sơ mi xanh size M"
