from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class OrderStatus(StrEnum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class FulfillmentStatus(StrEnum):
    NOT_FULFILLED = "not_fulfilled"
    PROCESSING = "processing"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    RETURNED = "returned"
    CANCELLED = "cancelled"


class PaymentStatus(StrEnum):
    PENDING = "pending"
    AUTHORIZED = "authorized"
    CAPTURED = "captured"
    REFUNDED = "refunded"
    PARTIALLY_REFUNDED = "partially_refunded"
    FAILED = "failed"


class Priority(StrEnum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"


class TicketStatus(StrEnum):
    OPEN = "open"
    PENDING = "pending"
    RESOLVED = "resolved"
    CLOSED = "closed"


class ReturnRequestStatus(StrEnum):
    PENDING_REVIEW = "pending_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    CANCELLED = "cancelled"


class HandoffStatus(StrEnum):
    PENDING_HUMAN_REVIEW = "pending_human_review"
    ASSIGNED = "assigned"
    RESOLVED = "resolved"


class Order(StrictModel):
    order_id: str
    customer_email: EmailStr
    scenario_key: str
    order_status: OrderStatus
    fulfillment_status: FulfillmentStatus
    payment_status: PaymentStatus
    created_at: datetime
    shipped_at: datetime | None = None
    delivered_at: datetime | None = None
    estimated_delivery: datetime | None = None
    currency: str = "VND"
    total_amount: int = Field(ge=0)


class OrderItem(StrictModel):
    item_id: str
    order_id: str
    sku: str
    product_name: str
    category: str
    quantity: int = Field(ge=1)
    unit_price: int = Field(ge=0)
    returnable: bool
    condition_status: str


class SupportTicket(StrictModel):
    ticket_id: str
    order_id: str
    item_id: str | None
    issue_description: str
    damage_type: str
    priority: Priority
    status: TicketStatus
    idempotency_key: str
    created_at: datetime
    updated_at: datetime


class ReturnRequest(StrictModel):
    return_request_id: str
    order_id: str
    item_id: str
    reason: str
    eligibility_code: str
    rule_version: str
    status: ReturnRequestStatus
    idempotency_key: str
    created_at: datetime


class HandoffRecord(StrictModel):
    handoff_id: str
    conversation_id: str
    primary_intent: str
    reason_code: str
    priority: Priority
    collected_fields: dict[str, Any]
    summary: str
    status: HandoffStatus
    idempotency_key: str
    created_at: datetime


class ReturnEligibilityResult(StrictModel):
    eligible: bool
    reason_code: str
    rule_version: str = "return-rules-v1"
    days_since_delivery: int | None = None
