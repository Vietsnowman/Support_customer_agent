# Intent Taxonomy

## 1. Taxonomy

```text
customer_support
├── policy_question
├── order_tracking
├── return_request
├── damaged_product
├── refund_request
└── unknown
```

Taxonomy giữ ở dạng phẳng. Policy category, damage type và refund scope là entity, không phải intent mới.

## 2. Intent definitions

| Intent | Khi dùng | Không dùng khi |
|---|---|---|
| `policy_question` | Hỏi quy định chung | Yêu cầu hành động trên đơn cụ thể |
| `order_tracking` | Hỏi trạng thái đơn cụ thể | Hỏi thời gian giao hàng nói chung |
| `return_request` | Muốn kiểm tra/tạo yêu cầu đổi trả | Chỉ hỏi policy hoặc refund |
| `damaged_product` | Báo sản phẩm lỗi/hỏng/sai | Chỉ hỏi policy hàng lỗi |
| `refund_request` | Muốn nhận lại tiền | Chỉ hỏi policy hoàn tiền |
| `unknown` | Mơ hồ hoặc ngoài scope | Chỉ thiếu required field |

## 3. Ví dụ phân biệt

```text
“Chính sách hoàn tiền thế nào?”
→ policy_question

“Tôi muốn hoàn tiền đơn MD-1052.”
→ refund_request

“Giao hàng thường mất bao lâu?”
→ policy_question

“Đơn MD-1052 đang ở đâu?”
→ order_tracking

“Nếu hàng hỏng thì xử lý sao?”
→ policy_question

“Hàng trong đơn MD-1052 bị hỏng.”
→ damaged_product
```

## 4. Multi-intent

State bắt buộc có:

```text
primary_intent
secondary_intents
active_intent
relation_type
execution_plan
```

### Relation types

- `independent`: có thể xử lý lần lượt.
- `sequential`: xử lý theo thứ tự.
- `conditional_dependency`: bước sau phụ thuộc kết quả bước trước.
- `high_risk_combination`: intent rủi ro cao quyết định safety/handoff.

### Priority rule

Nếu không có dependency:

```text
refund_request
> damaged_product
> return_request
> order_tracking
> policy_question
```

`unknown` là fail-safe, không phải intent có risk priority cao nhất.

### Ví dụ dependency

```text
“Kiểm tra đơn và nếu đã giao thì trả lại.”
```

```text
active_intent = order_tracking
step 1: tracking
step 2: return, condition = order_delivered
```

### Ví dụ high risk

```text
“Đơn đang ở đâu và hoàn tiền cho tôi.”
```

Agent có thể đọc trạng thái sau verification, nhưng refund chỉ được ghi nhận và handoff.

## 5. Clarification

Agent hỏi lại khi:

- Thiếu required field.
- Intent mơ hồ.
- Entity invalid, ambiguous hoặc conflicting.
- Không resolve được item.
- Điều kiện multi-intent chưa rõ.

Tối đa 2 lần cho cùng field/intent. Lần hai phải có ví dụ định dạng. Sau giới hạn → handoff.

## 6. LLM output boundary

LLM được tạo:

```text
primary_intent
secondary_intents
relation_type
raw entities
```

Code phải tính lại:

```text
missing/invalid/ambiguous/conflicting fields
active_intent
execution_plan
route
selected_tool
human_handling_status
reason_code
```
