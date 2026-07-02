# Giai đoạn 2 — Mock data và SQLite, bản phù hợp dự án cá nhân

## Mục tiêu

Giai đoạn 2 tạo một SQLite mock database đủ sạch và đủ edge case để phục vụ các business tools ở giai đoạn sau. Phạm vi được giữ gọn để phù hợp với dự án cá nhân: không mô phỏng toàn bộ hệ thống thương mại điện tử production, chỉ tập trung vào dữ liệu cần cho support agent.

## Phạm vi đã triển khai

- Giữ schema hiện tại: `orders`, `order_items`, `support_tickets`, `return_requests`, `human_handoffs`, `tool_audit_log`, `id_sequences`.
- Không thêm bảng `customers` ở giai đoạn này.
- Dùng `customer_email` trong `orders` làm mock ownership verification.
- Seed data mở rộng có chủ đích: 19 orders, 36 order items, 6 support tickets, 4 return requests, 4 human handoffs.
- Mỗi order phục vụ một scenario cụ thể thay vì sinh dữ liệu ngẫu nhiên nhiều nhưng ít giá trị test.

## Required scenarios

Các scenario bắt buộc nằm trong `support_agent.db.validation.REQUIRED_SCENARIOS`:

```text
tracking_shipped_with_ambiguous_items
tracking_processing
tracking_cancelled
tracking_payment_failed
delivered_return_eligible_day_3
delivered_return_eligible_day_7
delivered_return_expired_day_8
delivered_non_returnable_item
delivered_used_item
damaged_normal
damaged_critical_safety
ambiguous_product_name
multi_item_non_ambiguous
unauthorized_email_case
payment_refunded_cancelled
payment_partially_refunded
returned_order
return_not_delivered
```

## Validation

File chính:

```text
src/support_agent/db/validation.py
```

Các nhóm kiểm tra:

- `PRAGMA foreign_key_check` phải pass.
- `scenario_key` không trùng.
- Có đủ required scenarios.
- Order date consistency:
  - shipped/delivered order phải có `shipped_at`.
  - delivered order phải có `delivered_at`.
  - non-delivered order không được có `delivered_at`.
  - `created_at <= shipped_at <= delivered_at` nếu các mốc tồn tại.
- Item consistency:
  - quantity >= 1.
  - unit_price >= 0.
  - returnable thuộc 0/1.
  - condition_status hợp lệ.
- Idempotency key không trùng trong tickets, returns và handoffs.

Chạy kiểm tra:

```bash
python -m support_agent.cli reset-db
python -m support_agent.cli check-db
```

Output kỳ vọng:

```json
{
  "counts": {
    "orders": 19,
    "order_items": 36,
    "support_tickets": 6,
    "return_requests": 4,
    "human_handoffs": 4,
    "tool_audit_log": 0
  },
  "foreign_key_check": "passed",
  "seed_validation": "passed",
  "scenario_coverage": "passed",
  "missing_scenarios": [],
  "errors": []
}
```

## Repository helpers bổ sung

`OrderRepository` có thêm các wrapper và owner-safe helper để chuẩn bị cho Stage 3:

```python
def find_order(order_id: str) -> Order | None: ...
def verify_order_owner(order_id: str, email: str) -> bool: ...
def find_order_item_by_id(order_id: str, item_id: str) -> OrderItem | None: ...
def find_item_by_name(order_id: str, product_name: str) -> ItemMatch: ...
def get_order_for_owner(order_id: str, email: str) -> Order | None: ...
def get_order_status_for_owner(order_id: str, email: str) -> dict[str, object] | None: ...
def list_items_for_owner(order_id: str, email: str) -> list[OrderItem]: ...
```

Các helper `*_for_owner` trả `None` hoặc danh sách rỗng khi email không khớp, giúp Stage 3 tool layer tránh leak dữ liệu đơn hàng.

## Definition of Done

Stage 2 được xem là hoàn thành đủ tốt cho dự án cá nhân khi:

- `pytest` pass toàn bộ.
- Database reset được nhiều lần không lỗi.
- `check-db` trả `foreign_key_check`, `seed_validation`, `scenario_coverage` đều passed.
- Có ít nhất 16 orders và 30 order items.
- Có đủ required scenario keys.
- Repository tìm order/item đúng.
- Item resolution có đủ `single`, `ambiguous`, `none`.
- Wrong email không lấy được order data qua owner-safe helper.
- Write repositories vẫn idempotent.
- README ghi rõ `customer_email` chỉ là mock verification, không phải production authentication.
