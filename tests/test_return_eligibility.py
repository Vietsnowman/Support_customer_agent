from __future__ import annotations

from datetime import UTC, datetime

from support_agent.repositories import OrderRepository
from support_agent.services import ReturnEligibilityService


AS_OF = datetime(2026, 7, 1, 12, 0, tzinfo=UTC)


def _evaluate(db_conn, order_id: str, item_id: str):
    repo = OrderRepository(db_conn)
    order = repo.get_order(order_id)
    item = repo.get_item(order_id, item_id)
    assert order is not None and item is not None
    return ReturnEligibilityService(return_window_days=7).evaluate(
        order,
        item,
        as_of=AS_OF,
    )


def test_not_delivered_order_is_not_eligible(db_conn):
    result = _evaluate(db_conn, "MD-1052", "ITEM-001")
    assert result.eligible is False
    assert result.reason_code == "order_not_delivered"


def test_expired_order_is_not_eligible(db_conn):
    result = _evaluate(db_conn, "MD-1053", "ITEM-003")
    assert result.eligible is False
    assert result.reason_code == "return_window_expired"
    assert result.days_since_delivery == 20


def test_recent_delivered_order_is_eligible(db_conn):
    result = _evaluate(db_conn, "MD-2001", "ITEM-004")
    assert result.eligible is True
    assert result.reason_code == "eligible"
    assert result.days_since_delivery == 3


def test_non_returnable_item_is_not_eligible(db_conn):
    result = _evaluate(db_conn, "MD-2002", "ITEM-005")
    assert result.eligible is False
    assert result.reason_code == "item_not_returnable"


def test_day_7_order_is_still_eligible(db_conn):
    result = _evaluate(db_conn, "MD-2007", "ITEM-012")
    assert result.eligible is True
    assert result.reason_code == "eligible"
    assert result.days_since_delivery == 7


def test_day_8_order_is_expired(db_conn):
    result = _evaluate(db_conn, "MD-2008", "ITEM-013")
    assert result.eligible is False
    assert result.reason_code == "return_window_expired"
    assert result.days_since_delivery == 8


def test_used_item_is_not_eligible(db_conn):
    result = _evaluate(db_conn, "MD-2009", "ITEM-014")
    assert result.eligible is False
    assert result.reason_code == "item_used"
