# Design Decisions and Consistency Fixes

## 1. Vocabulary

- `config/agent-spec.json` là nguồn canonical duy nhất.
- Chuẩn hóa còn 6 intent, 11 route và 8 tool.
- Loại bỏ vocabulary cũ: `policy_rag`, `ask_missing_information`, `fallback`.

## 2. Routing state

- Bỏ `final_route` vì gây mâu thuẫn trong multi-intent.
- Dùng `active_intent`, `current_route`, `next_action` và `execution_plan`.
- `next_action` luôn là một hành động nguyên tử.

## 3. Human handling

- Bỏ boolean `requires_human`.
- Thay bằng `human_handling_status`:
  - `not_required`
  - `required_later`
  - `ready_now`
  - `created`

Nhờ đó refund thiếu field không gọi handoff quá sớm.

## 4. Tool policy

- Business tool được authorize theo `active_intent`.
- `request_human_handoff` là global control tool và chỉ được gọi khi trạng thái là `ready_now`.
- Tách tool input khỏi workflow precondition.
- Executor tự sinh idempotency key cho write tool.

## 5. Entity validation

- Tách raw entity khỏi validated entity.
- Email sai format có thể được ghi nhận trong `invalid_fields` mà không làm parse toàn state thất bại.
- Product resolution chỉ diễn ra sau verification.

## 6. Reason codes

- Thu gọn thành 24 decision reason codes trong spec.
- Bộ 64 cases hiện sử dụng 22 code.
- Tool error và business result được tách sang `tool_error_code` và `business_result_code`.

## 7. Evaluation

- Thu gọn từ 147 xuống 64 cases CV-ready.
- 22 smoke cases cho phát triển hằng ngày.
- 42 regression cases cho release/demo.
- Schema nested object được làm chặt.
- Validator không phụ thuộc current working directory.
