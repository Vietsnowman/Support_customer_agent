from __future__ import annotations

import json
import re
import sqlite3
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

from pydantic import BaseModel, ConfigDict, EmailStr, Field


ORDER_ID_RE = re.compile(r"^MD-\d{4,10}$")
ITEM_ID_RE = re.compile(r"^ITEM-\d{3,10}$")


class SeedModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class SeedOrder(SeedModel):
    order_id: str
    customer_email: EmailStr
    scenario_key: str
    order_status: str
    fulfillment_status: str
    payment_status: str
    created_days_ago: int = Field(ge=0)
    shipped_days_ago: int | None = Field(default=None, ge=0)
    delivered_days_ago: int | None = Field(default=None, ge=0)
    estimated_delivery_days_from_now: int | None = None
    currency: str = "VND"
    total_amount: int = Field(ge=0)


class SeedItem(SeedModel):
    item_id: str
    order_id: str
    sku: str
    product_name: str
    category: str
    quantity: int = Field(ge=1)
    unit_price: int = Field(ge=0)
    returnable: bool
    condition_status: str


class SeedTicket(SeedModel):
    ticket_id: str
    order_id: str
    item_id: str | None = None
    issue_description: str
    damage_type: str
    priority: str
    status: str
    idempotency_key: str
    created_days_ago: int = Field(ge=0)


class SeedReturnRequest(SeedModel):
    return_request_id: str
    order_id: str
    item_id: str
    reason: str
    eligibility_code: str
    rule_version: str = "return-rules-v1"
    status: str
    idempotency_key: str
    created_days_ago: int = Field(ge=0)


class SeedHandoff(SeedModel):
    handoff_id: str
    conversation_id: str
    primary_intent: str
    reason_code: str
    priority: str
    collected_fields: dict[str, Any]
    summary: str
    status: str
    idempotency_key: str
    created_days_ago: int = Field(ge=0)


def _read_json(path: Path) -> list[dict[str, Any]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise ValueError(f"Seed file must contain a JSON array: {path}")
    return data


def load_seed_bundle(seed_dir: Path) -> dict[str, list[SeedModel]]:
    return {
        "orders": [SeedOrder.model_validate(x) for x in _read_json(seed_dir / "orders.json")],
        "items": [SeedItem.model_validate(x) for x in _read_json(seed_dir / "order_items.json")],
        "tickets": [SeedTicket.model_validate(x) for x in _read_json(seed_dir / "support_tickets.json")],
        "returns": [SeedReturnRequest.model_validate(x) for x in _read_json(seed_dir / "return_requests.json")],
        "handoffs": [SeedHandoff.model_validate(x) for x in _read_json(seed_dir / "handoffs.json")],
    }


def _ensure_unique(values: list[str], label: str) -> None:
    if len(values) != len(set(values)):
        raise ValueError(f"Duplicate {label} in seed data")


def _validate_order_relative_dates(order: SeedOrder) -> None:
    if order.fulfillment_status in {"shipped", "delivered"} and order.shipped_days_ago is None:
        raise ValueError(f"{order.order_id}: shipped/delivered order must have shipped_days_ago")
    if order.fulfillment_status == "delivered" and order.delivered_days_ago is None:
        raise ValueError(f"Delivered order {order.order_id} must have delivered_days_ago")
    if order.fulfillment_status != "delivered" and order.delivered_days_ago is not None:
        raise ValueError(f"Non-delivered order {order.order_id} cannot have delivered_days_ago")
    if order.shipped_days_ago is not None and order.created_days_ago < order.shipped_days_ago:
        raise ValueError(f"{order.order_id}: created_days_ago must be >= shipped_days_ago")
    if (
        order.shipped_days_ago is not None
        and order.delivered_days_ago is not None
        and order.shipped_days_ago < order.delivered_days_ago
    ):
        raise ValueError(f"{order.order_id}: shipped_days_ago must be >= delivered_days_ago")
    if order.order_status == "cancelled" and order.fulfillment_status not in {"cancelled", "not_fulfilled"}:
        raise ValueError(f"{order.order_id}: cancelled order has inconsistent fulfillment_status")
    if order.payment_status == "refunded" and order.order_status in {"pending", "processing"}:
        raise ValueError(f"{order.order_id}: refunded payment cannot belong to pending/processing order")


def validate_seed_bundle(bundle: dict[str, list[SeedModel]]) -> None:
    orders = bundle["orders"]
    items = bundle["items"]
    tickets = bundle["tickets"]
    returns = bundle["returns"]
    handoffs = bundle["handoffs"]

    order_ids = [x.order_id for x in orders]
    item_ids = [x.item_id for x in items]

    _ensure_unique(order_ids, "order_id")
    _ensure_unique([x.scenario_key for x in orders], "scenario_key")
    _ensure_unique(item_ids, "item_id")
    _ensure_unique([x.ticket_id for x in tickets], "ticket_id")
    _ensure_unique([x.return_request_id for x in returns], "return_request_id")
    _ensure_unique([x.handoff_id for x in handoffs], "handoff_id")
    _ensure_unique([x.idempotency_key for x in tickets], "ticket idempotency_key")
    _ensure_unique([x.idempotency_key for x in returns], "return idempotency_key")
    _ensure_unique([x.idempotency_key for x in handoffs], "handoff idempotency_key")

    for order in orders:
        if not ORDER_ID_RE.fullmatch(order.order_id):
            raise ValueError(f"Invalid order_id: {order.order_id}")
        _validate_order_relative_dates(order)

    order_id_set = set(order_ids)
    item_id_set = set(item_ids)
    item_to_order = {x.item_id: x.order_id for x in items}

    for item in items:
        if not ITEM_ID_RE.fullmatch(item.item_id):
            raise ValueError(f"Invalid item_id: {item.item_id}")
        if item.order_id not in order_id_set:
            raise ValueError(f"Item {item.item_id} references unknown order")

    for ticket in tickets:
        if ticket.order_id not in order_id_set:
            raise ValueError(f"Ticket {ticket.ticket_id} references unknown order")
        if ticket.item_id is not None:
            if ticket.item_id not in item_id_set:
                raise ValueError(f"Ticket {ticket.ticket_id} references unknown item")
            if item_to_order[ticket.item_id] != ticket.order_id:
                raise ValueError(f"Ticket {ticket.ticket_id} item belongs to another order")

    for request in returns:
        if request.order_id not in order_id_set or request.item_id not in item_id_set:
            raise ValueError(
                f"Return {request.return_request_id} references unknown order/item"
            )
        if item_to_order[request.item_id] != request.order_id:
            raise ValueError(
                f"Return {request.return_request_id} item belongs to another order"
            )


def _iso(value: datetime | None) -> str | None:
    return value.isoformat() if value is not None else None


def _next_from_ids(values: list[str], prefix: str) -> int:
    numbers: list[int] = []
    for value in values:
        if value.startswith(prefix):
            try:
                numbers.append(int(value.removeprefix(prefix)))
            except ValueError:
                pass
    return max(numbers, default=0) + 1


def seed_database(
    conn: sqlite3.Connection,
    seed_dir: Path,
    *,
    now: datetime | None = None,
) -> None:
    anchor = now or datetime.now(UTC)
    bundle = load_seed_bundle(seed_dir)
    validate_seed_bundle(bundle)

    with conn:
        for order in bundle["orders"]:
            created = anchor - timedelta(days=order.created_days_ago)
            shipped = (
                anchor - timedelta(days=order.shipped_days_ago)
                if order.shipped_days_ago is not None
                else None
            )
            delivered = (
                anchor - timedelta(days=order.delivered_days_ago)
                if order.delivered_days_ago is not None
                else None
            )
            eta = (
                anchor + timedelta(days=order.estimated_delivery_days_from_now)
                if order.estimated_delivery_days_from_now is not None
                else None
            )
            conn.execute(
                """
                INSERT INTO orders (
                    order_id, customer_email, scenario_key,
                    order_status, fulfillment_status, payment_status,
                    created_at, shipped_at, delivered_at, estimated_delivery,
                    currency, total_amount
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    order.order_id,
                    str(order.customer_email).lower(),
                    order.scenario_key,
                    order.order_status,
                    order.fulfillment_status,
                    order.payment_status,
                    _iso(created),
                    _iso(shipped),
                    _iso(delivered),
                    _iso(eta),
                    order.currency,
                    order.total_amount,
                ),
            )

        for item in bundle["items"]:
            conn.execute(
                """
                INSERT INTO order_items (
                    item_id, order_id, sku, product_name, category,
                    quantity, unit_price, returnable, condition_status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    item.item_id,
                    item.order_id,
                    item.sku,
                    item.product_name,
                    item.category,
                    item.quantity,
                    item.unit_price,
                    int(item.returnable),
                    item.condition_status,
                ),
            )

        for ticket in bundle["tickets"]:
            created = anchor - timedelta(days=ticket.created_days_ago)
            conn.execute(
                """
                INSERT INTO support_tickets (
                    ticket_id, order_id, item_id, issue_description,
                    damage_type, priority, status, idempotency_key,
                    created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    ticket.ticket_id,
                    ticket.order_id,
                    ticket.item_id,
                    ticket.issue_description,
                    ticket.damage_type,
                    ticket.priority,
                    ticket.status,
                    ticket.idempotency_key,
                    _iso(created),
                    _iso(created),
                ),
            )

        for request in bundle["returns"]:
            created = anchor - timedelta(days=request.created_days_ago)
            conn.execute(
                """
                INSERT INTO return_requests (
                    return_request_id, order_id, item_id, reason,
                    eligibility_code, rule_version, status,
                    idempotency_key, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    request.return_request_id,
                    request.order_id,
                    request.item_id,
                    request.reason,
                    request.eligibility_code,
                    request.rule_version,
                    request.status,
                    request.idempotency_key,
                    _iso(created),
                ),
            )

        for handoff in bundle["handoffs"]:
            created = anchor - timedelta(days=handoff.created_days_ago)
            conn.execute(
                """
                INSERT INTO human_handoffs (
                    handoff_id, conversation_id, primary_intent,
                    reason_code, priority, collected_fields_json,
                    summary, status, idempotency_key, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    handoff.handoff_id,
                    handoff.conversation_id,
                    handoff.primary_intent,
                    handoff.reason_code,
                    handoff.priority,
                    json.dumps(handoff.collected_fields, ensure_ascii=False),
                    handoff.summary,
                    handoff.status,
                    handoff.idempotency_key,
                    _iso(created),
                ),
            )

        sequence_rows = {
            "ticket": _next_from_ids(
                [x.ticket_id for x in bundle["tickets"]], "TICKET-"
            ),
            "return": _next_from_ids(
                [x.return_request_id for x in bundle["returns"]], "RET-"
            ),
            "handoff": _next_from_ids(
                [x.handoff_id for x in bundle["handoffs"]], "HANDOFF-"
            ),
        }
        for name, next_value in sequence_rows.items():
            conn.execute(
                "INSERT INTO id_sequences(name, next_value) VALUES (?, ?)",
                (name, next_value),
            )
