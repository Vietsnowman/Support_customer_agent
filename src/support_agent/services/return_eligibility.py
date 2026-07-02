from __future__ import annotations

from datetime import UTC, datetime

from support_agent.models.domain import (
    FulfillmentStatus,
    Order,
    OrderItem,
    ReturnEligibilityResult,
)


class ReturnEligibilityService:
    def __init__(self, return_window_days: int = 7) -> None:
        if return_window_days < 1:
            raise ValueError("return_window_days must be positive")
        self.return_window_days = return_window_days

    def evaluate(
        self,
        order: Order,
        item: OrderItem,
        *,
        as_of: datetime | None = None,
    ) -> ReturnEligibilityResult:
        if item.order_id != order.order_id:
            return ReturnEligibilityResult(
                eligible=False,
                reason_code="item_not_found",
            )

        if order.fulfillment_status != FulfillmentStatus.DELIVERED:
            return ReturnEligibilityResult(
                eligible=False,
                reason_code="order_not_delivered",
            )

        if order.delivered_at is None:
            return ReturnEligibilityResult(
                eligible=False,
                reason_code="invalid_delivery_date",
            )

        if not item.returnable:
            return ReturnEligibilityResult(
                eligible=False,
                reason_code="item_not_returnable",
            )

        if item.condition_status == "used":
            return ReturnEligibilityResult(
                eligible=False,
                reason_code="item_used",
            )

        current = as_of or datetime.now(UTC)
        days = (current.date() - order.delivered_at.date()).days
        if days < 0:
            return ReturnEligibilityResult(
                eligible=False,
                reason_code="invalid_delivery_date",
                days_since_delivery=days,
            )
        if days > self.return_window_days:
            return ReturnEligibilityResult(
                eligible=False,
                reason_code="return_window_expired",
                days_since_delivery=days,
            )

        return ReturnEligibilityResult(
            eligible=True,
            reason_code="eligible",
            days_since_delivery=days,
        )
