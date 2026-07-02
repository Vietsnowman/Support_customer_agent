from __future__ import annotations

import sqlite3
from datetime import datetime


REQUIRED_SCENARIOS: set[str] = {
    "tracking_shipped_with_ambiguous_items",
    "tracking_processing",
    "tracking_cancelled",
    "tracking_payment_failed",
    "delivered_return_eligible_day_3",
    "delivered_return_eligible_day_7",
    "delivered_return_expired_day_8",
    "delivered_non_returnable_item",
    "delivered_used_item",
    "damaged_normal",
    "damaged_critical_safety",
    "ambiguous_product_name",
    "multi_item_non_ambiguous",
    "unauthorized_email_case",
    "payment_refunded_cancelled",
    "payment_partially_refunded",
    "returned_order",
    "return_not_delivered",
}


def validate_seed_dataset(conn: sqlite3.Connection) -> list[str]:
    """Run lightweight consistency checks for the Stage 2 mock database.

    These checks intentionally stay small and deterministic. The goal is not to
    model a production commerce database, but to guarantee that the demo data has
    the edge cases needed by later tool, routing, and evaluation stages.
    """

    errors: list[str] = []
    errors.extend(validate_foreign_keys(conn))
    errors.extend(validate_unique_scenario_keys(conn))
    errors.extend(validate_required_scenarios(conn))
    errors.extend(validate_order_consistency(conn))
    errors.extend(validate_item_consistency(conn))
    errors.extend(validate_idempotency_keys(conn))
    return errors


def validate_foreign_keys(conn: sqlite3.Connection) -> list[str]:
    rows = conn.execute("PRAGMA foreign_key_check").fetchall()
    return [f"foreign_key_check failed: {tuple(row)}" for row in rows]


def validate_unique_scenario_keys(conn: sqlite3.Connection) -> list[str]:
    rows = conn.execute(
        """
        SELECT scenario_key, COUNT(*) AS n
        FROM orders
        GROUP BY scenario_key
        HAVING n > 1
        """
    ).fetchall()
    return [f"duplicate scenario_key: {row['scenario_key']}" for row in rows]


def validate_required_scenarios(conn: sqlite3.Connection) -> list[str]:
    rows = conn.execute("SELECT scenario_key FROM orders").fetchall()
    actual = {row["scenario_key"] for row in rows}
    missing = REQUIRED_SCENARIOS - actual
    return [f"missing scenario_key: {scenario}" for scenario in sorted(missing)]


def validate_order_consistency(conn: sqlite3.Connection) -> list[str]:
    errors: list[str] = []
    rows = conn.execute(
        """
        SELECT order_id, order_status, fulfillment_status, payment_status,
               created_at, shipped_at, delivered_at, estimated_delivery
        FROM orders
        ORDER BY order_id
        """
    ).fetchall()

    for row in rows:
        order_id = row["order_id"]
        created_at = _parse_dt(row["created_at"])
        shipped_at = _parse_dt(row["shipped_at"])
        delivered_at = _parse_dt(row["delivered_at"])
        estimated_delivery = _parse_dt(row["estimated_delivery"])

        fulfillment_status = row["fulfillment_status"]
        order_status = row["order_status"]
        payment_status = row["payment_status"]

        if fulfillment_status in {"shipped", "delivered"} and shipped_at is None:
            errors.append(f"{order_id}: shipped/delivered order must have shipped_at")
        if fulfillment_status == "delivered" and delivered_at is None:
            errors.append(f"{order_id}: delivered order must have delivered_at")
        if fulfillment_status != "delivered" and delivered_at is not None:
            errors.append(f"{order_id}: non-delivered order cannot have delivered_at")

        if shipped_at and created_at > shipped_at:
            errors.append(f"{order_id}: created_at is after shipped_at")
        if delivered_at and shipped_at and shipped_at > delivered_at:
            errors.append(f"{order_id}: shipped_at is after delivered_at")
        if estimated_delivery and created_at > estimated_delivery:
            errors.append(f"{order_id}: created_at is after estimated_delivery")

        if order_status == "cancelled" and fulfillment_status not in {
            "cancelled",
            "not_fulfilled",
        }:
            errors.append(f"{order_id}: cancelled order has inconsistent fulfillment_status")
        if payment_status == "refunded" and order_status in {"pending", "processing"}:
            errors.append(f"{order_id}: refunded payment cannot be pending/processing")
        if payment_status == "failed" and fulfillment_status not in {
            "not_fulfilled",
            "processing",
        }:
            errors.append(f"{order_id}: failed payment should not be fulfilled")

    return errors


def validate_item_consistency(conn: sqlite3.Connection) -> list[str]:
    errors: list[str] = []
    rows = conn.execute(
        """
        SELECT item_id, order_id, quantity, unit_price, returnable, condition_status
        FROM order_items
        ORDER BY item_id
        """
    ).fetchall()
    for row in rows:
        item_id = row["item_id"]
        if row["quantity"] < 1:
            errors.append(f"{item_id}: quantity must be >= 1")
        if row["unit_price"] < 0:
            errors.append(f"{item_id}: unit_price must be >= 0")
        if row["returnable"] not in {0, 1}:
            errors.append(f"{item_id}: returnable must be 0 or 1")
        if row["condition_status"] not in {"new", "opened", "used", "damaged"}:
            errors.append(f"{item_id}: invalid condition_status")
    return errors


def validate_idempotency_keys(conn: sqlite3.Connection) -> list[str]:
    errors: list[str] = []
    checks = (
        ("support_tickets", "idempotency_key"),
        ("return_requests", "idempotency_key"),
        ("human_handoffs", "idempotency_key"),
    )
    for table, column in checks:
        rows = conn.execute(
            f"""
            SELECT {column} AS key, COUNT(*) AS n #Lấy từng idempotency_key và đếm xem nó xuất hiện bao nhiêu lần.
            FROM {table} #chọn ra từng bảng
            GROUP BY {column} #Nhóm các hàng có cùng idempotency_key lại với nhau
            HAVING n > 1 #Lấy những nhóm có số lượng lớn hơn 1
            """
        ).fetchall() 
        for row in rows:
            errors.append(f"{table}: duplicate {column}: {row['key']}")
    return errors


def _parse_dt(value: str | None) -> datetime | None:
    return datetime.fromisoformat(value) if value else None
