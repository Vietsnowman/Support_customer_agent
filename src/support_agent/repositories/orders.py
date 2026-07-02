from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from datetime import datetime

from support_agent.models.domain import Order, OrderItem


@dataclass(frozen=True, slots=True)
class ItemMatch:
    match_type: str
    candidates: tuple[OrderItem, ...]

    @property
    def resolved_item(self) -> OrderItem | None:
        return self.candidates[0] if self.match_type == "single" else None


class OrderRepository:
    def __init__(self, conn: sqlite3.Connection) -> None:
        self.conn = conn

    def verify_owner(self, order_id: str, customer_email: str) -> bool:
        row = self.conn.execute(
            """
            SELECT 1
            FROM orders
            WHERE order_id = ? AND lower(customer_email) = lower(?)
            """,
            (order_id, customer_email.strip()),
        ).fetchone()
        return row is not None

    def get_order(self, order_id: str) -> Order | None:
        row = self.conn.execute(
            "SELECT * FROM orders WHERE order_id = ?",
            (order_id,),
        ).fetchone()
        return _order_from_row(row) if row else None

    def find_order(self, order_id: str) -> Order | None:
        """Alias used by the Stage 2/3 public repository contract."""
        return self.get_order(order_id)

    def verify_order_owner(self, order_id: str, email: str) -> bool:
        """Alias with business-facing wording for later tool code."""
        return self.verify_owner(order_id, email)

    def get_order_for_owner(self, order_id: str, email: str) -> Order | None:
        if not self.verify_owner(order_id, email):
            return None
        return self.get_order(order_id)

    def get_order_status(self, order_id: str) -> dict[str, object] | None:
        row = self.conn.execute(
            """
            SELECT order_id, order_status, fulfillment_status,
                   payment_status, estimated_delivery
            FROM orders
            WHERE order_id = ?
            """,
            (order_id,),
        ).fetchone()
        return dict(row) if row else None

    def get_order_status_for_owner(
        self,
        order_id: str,
        email: str,
    ) -> dict[str, object] | None:
        if not self.verify_owner(order_id, email):
            return None
        return self.get_order_status(order_id)

    def list_items(self, order_id: str) -> list[OrderItem]:
        rows = self.conn.execute(
            "SELECT * FROM order_items WHERE order_id = ? ORDER BY item_id",
            (order_id,),
        ).fetchall()
        return [_item_from_row(row) for row in rows]

    def list_items_for_owner(self, order_id: str, email: str) -> list[OrderItem]:
        if not self.verify_owner(order_id, email):
            return []
        return self.list_items(order_id)

    def get_item(self, order_id: str, item_id: str) -> OrderItem | None:
        row = self.conn.execute(
            """
            SELECT * FROM order_items
            WHERE order_id = ? AND item_id = ?
            """,
            (order_id, item_id),
        ).fetchone()
        return _item_from_row(row) if row else None

    def find_order_item_by_id(self, order_id: str, item_id: str) -> OrderItem | None:
        return self.get_item(order_id, item_id)

    def find_item_by_name(self, order_id: str, product_name: str) -> ItemMatch:
        return self.find_order_item(order_id, product_name=product_name)

    def find_order_item(
        self,
        order_id: str,
        *,
        item_id: str | None = None,
        product_name: str | None = None,
    ) -> ItemMatch:
        if item_id:
            item = self.get_item(order_id, item_id)
            return ItemMatch("single", (item,)) if item else ItemMatch("none", ())

        if not product_name or not product_name.strip():
            return ItemMatch("none", ())

        query = product_name.strip().casefold()
        rows = self.conn.execute(
            "SELECT * FROM order_items WHERE order_id = ? ORDER BY item_id",
            (order_id,),
        ).fetchall()
        candidates = tuple(
            _item_from_row(row)
            for row in rows
            if query in str(row["product_name"]).casefold()
        )
        if len(candidates) == 1:
            return ItemMatch("single", candidates)
        if len(candidates) > 1:
            return ItemMatch("ambiguous", candidates)
        return ItemMatch("none", ())


def _dt(value: str | None) -> datetime | None:
    return datetime.fromisoformat(value) if value else None


def _order_from_row(row: sqlite3.Row) -> Order:
    return Order(
        order_id=row["order_id"],
        customer_email=row["customer_email"],
        scenario_key=row["scenario_key"],
        order_status=row["order_status"],
        fulfillment_status=row["fulfillment_status"],
        payment_status=row["payment_status"],
        created_at=_dt(row["created_at"]),
        shipped_at=_dt(row["shipped_at"]),
        delivered_at=_dt(row["delivered_at"]),
        estimated_delivery=_dt(row["estimated_delivery"]),
        currency=row["currency"],
        total_amount=row["total_amount"],
    )


def _item_from_row(row: sqlite3.Row) -> OrderItem:
    return OrderItem(
        item_id=row["item_id"],
        order_id=row["order_id"],
        sku=row["sku"],
        product_name=row["product_name"],
        category=row["category"],
        quantity=row["quantity"],
        unit_price=row["unit_price"],
        returnable=bool(row["returnable"]),
        condition_status=row["condition_status"],
    )
