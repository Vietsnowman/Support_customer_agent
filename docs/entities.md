# Entities and Required Fields

## 1. Entity schema

| Entity | Kiểu | Ví dụ |
|---|---|---|
| `order_id` | string | `MD-1052` |
| `customer_email` | string/email | `user@example.com` |
| `item_id` | string | `ITEM-001` |
| `product_name` | string | `Áo sơ mi xanh` |
| `resolved_item_id` | string | `ITEM-001` |
| `policy_category` | enum | `return` |
| `issue_description` | string | `Sản phẩm bị vỡ` |
| `damage_type` | enum | `broken` |
| `return_reason` | string | `Không vừa` |
| `refund_reason` | string | `Không đúng mô tả` |
| `refund_scope` | enum | `specific_item` |
| `user_confirmation` | boolean | `true` |

## 2. Enum

```text
policy_category:
shipping | return | refund | warranty | payment | damaged_item | other

damage_type:
broken | defective | missing_part | wrong_item | unsafe | other

refund_scope:
full_order | partial_order | specific_item | unknown
```

## 3. Validation

### Order ID

```regex
^MD-\d{4,10}$
```

Trim và uppercase trước validation.

### Item ID

```regex
^ITEM-\d{3,10}$
```

### Email

Tách raw và validated entity:

```text
raw_entities.customer_email: string | null
entities.customer_email: valid email | null
```

Nhờ đó email sai format vẫn được lưu trong `invalid_fields` thay vì làm Pydantic parse thất bại ngay.

## 4. Required fields by intent

```python
REQUIRED_FIELDS_BY_INTENT = {
    "policy_question": [],
    "order_tracking": ["order_id", "customer_email"],
    "return_request": ["order_id", "customer_email", "item_reference"],
    "damaged_product": [
        "order_id", "customer_email", "item_reference", "issue_description"
    ],
    "refund_request": ["order_id", "customer_email", "refund_reason"],
    "unknown": [],
}
```

`item_reference = item_id hoặc product_name`.

## 5. Tool input vs workflow precondition

Không trộn hai khái niệm:

```python
TOOL_INPUT_FIELDS = {
    "get_order_status": ["order_id"],
    "check_return_eligibility": ["order_id", "resolved_item_id"],
    "create_return_request": [
        "order_id", "resolved_item_id", "return_reason", "user_confirmation"
    ],
}

WORKFLOW_PRECONDITIONS = {
    "get_order_status": ["verification_status == verified"],
    "create_return_request": [
        "verification_status == verified",
        "eligibility == true",
        "user_confirmation == true",
    ],
}
```

## 6. Field collection order

```text
1. order_id
2. customer_email
3. verification
4. item reference nếu cần
5. reason/description
6. optional fields
7. confirmation trước write action
```

Chỉ hỏi field đầu tiên còn thiếu tại gate hiện tại. Giữ mọi field hợp lệ người dùng đã cung cấp.

## 7. Entity quality state

```text
missing_fields
invalid_fields
ambiguous_fields
conflicting_fields
```

- `null` không ghi đè giá trị hợp lệ.
- Giá trị mới khác giá trị cũ phải được xác nhận trước khi ghi đè.
- Product name chỉ resolve trong đơn đã xác minh.
