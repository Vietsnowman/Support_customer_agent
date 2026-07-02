# Tool Policy

## 1. Tool registry

| Tool | Loại | Side effect |
|---|---|---|
| `search_policy` | read | Không |
| `verify_order_owner` | read | Không |
| `get_order_status` | read | Không |
| `find_order_item` | read | Không |
| `check_return_eligibility` | deterministic read | Không |
| `create_return_request` | write | Có |
| `create_support_ticket` | write | Có |
| `request_human_handoff` | control write | Có |

## 2. Business allowlist

```python
BUSINESS_TOOL_ALLOWLIST = {
    "policy_question": {"search_policy"},
    "order_tracking": {"verify_order_owner", "get_order_status"},
    "return_request": {
        "verify_order_owner", "find_order_item",
        "check_return_eligibility", "create_return_request",
    },
    "damaged_product": {
        "verify_order_owner", "find_order_item", "create_support_ticket",
    },
    "refund_request": {"verify_order_owner"},
    "unknown": set(),
}
```

`request_human_handoff` là global control tool, chỉ được gọi khi:

```text
human_handling_status == ready_now
```

## 3. Preconditions chung

Trước tool call:

- Tool tồn tại trong registry.
- Tool được authorize cho `active_intent` hoặc là global control tool hợp lệ.
- Input đúng schema.
- Workflow precondition đã đạt.
- Safety không blocked.
- Verification/confirmation đã đạt nếu cần.

## 4. Tool contracts rút gọn

### `search_policy`

Input: `query`, optional `policy_category`, `top_k`.  
Output: active/approved chunks kèm `document_id`, `chunk_id`, score.  
Không evidence hoặc evidence mâu thuẫn → handoff.

### `verify_order_owner`

Input: `order_id`, `customer_email`.  
Output: `authorized: bool`.  
Không được tiết lộ email đúng hoặc cho biết đơn thuộc người khác.

### `get_order_status`

Input: `order_id`.  
Precondition: verified.  
Output allowlist: order, fulfillment, payment status và ETA nếu backend có.

### `find_order_item`

Input: `order_id`, `item_id | product_name`.  
Precondition: verified.  
Nếu nhiều candidate → hỏi người dùng, không tự chọn.

### `check_return_eligibility`

Input: `order_id`, `resolved_item_id`.  
Output: `eligible`, `reason_code`, `rule_version`.  
LLM không được override.

### `create_return_request`

Precondition: verified, item resolved, eligible, reason, confirmation.  
Output: `return_request_id`, status `pending_review`.

### `create_support_ticket`

Precondition: verified, item resolved, issue description.  
Output: `ticket_id`, status.

### `request_human_handoff`

Input: reason, collected fields, summary, priority.  
Không chứa chain-of-thought, secret hoặc dữ liệu không cần thiết.

## 5. Retry and idempotency

- Read tool: retry tối đa 1 lần cho lỗi tạm thời.
- Write tool: không retry mù.
- Executor tự sinh idempotency key trước write tool từ conversation/action/business identifiers.
- Sau timeout, lookup bằng key trước khi retry.
- Không rõ side effect → handoff.

## 6. Forbidden tools

```text
execute_refund
cancel_order
modify_order
change_address
update_payment
approve_return
issue_voucher
replace_product
```
