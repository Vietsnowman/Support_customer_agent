# Routing Policy

## 1. Canonical routes

```text
clarify
collect_fields
verify_customer
retrieve_policy
execute_order
execute_return
execute_ticket
request_confirmation
human_handoff
respond
safety_block
```

Không dùng `final_route`. State chỉ lưu:

```text
current_route
next_action
active_intent
execution_plan
```

Điều này tránh mâu thuẫn giữa primary intent và route của bước đang chạy.

## 2. Decision order

```text
1. Safety gate
2. User-requested/immediate handoff
3. Intent ambiguity
4. Invalid/ambiguous/conflicting entity
5. Missing required field
6. Multi-intent execution plan
7. Verification
8. Confirmation
9. Tool authorization
10. Tool execution
11. Result verification
12. Respond hoặc handoff
```

## 3. Human handling state

Thay `requires_human` bằng:

```text
not_required
required_later
ready_now
created
```

- `required_later`: refund còn thiếu field hoặc chưa verify.
- `ready_now`: đủ payload để gọi `request_human_handoff`.
- `created`: handoff tool đã thành công.

## 4. Route by intent

```text
policy_question:
retrieve_policy → respond | human_handoff

order_tracking:
collect_fields → verify_customer → execute_order → respond

return_request:
collect_fields → verify_customer → execute_return
→ request_confirmation → execute_return → respond

damaged_product:
collect_fields → verify_customer → execute_ticket → respond/human_handoff

refund_request:
collect_fields → verify_customer → human_handoff

unknown:
clarify → respond/human_handoff
```

## 5. Multi-intent execution plan

`next_action` phải là một hành động nguyên tử. Không dùng:

```text
search_policy_then_collect_fields
retry_tool_or_handoff
ask_email_and_clarify_other_part
```

Dùng:

```json
{
  "active_intent": "policy_question",
  "next_action": "search_policy",
  "execution_plan": [
    {
      "step_id": "step-1",
      "intent": "policy_question",
      "route": "retrieve_policy",
      "status": "active"
    },
    {
      "step_id": "step-2",
      "intent": "order_tracking",
      "route": "collect_fields",
      "status": "queued"
    }
  ]
}
```

## 6. Simplified resolver

```python
def resolve_route(state):
    if state.safety_status == "blocked":
        return "safety_block"

    if state.human_handling_status == "ready_now":
        return "human_handoff"

    if state.workflow_status == "clarification_required":
        return "clarify"

    if state.invalid_fields or state.ambiguous_fields or state.conflicting_fields:
        return "collect_fields"

    if state.missing_fields:
        return "collect_fields"

    if state.verification_required and state.verification_status == "not_started":
        return "verify_customer"

    return state.execution_plan.active_step.route
```
