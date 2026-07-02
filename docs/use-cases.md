# Use Cases

## 1. Use case nghiệp vụ

### UC-01 — Hỏi chính sách

**Intent:** `policy_question`  
**Mục tiêu:** Trả lời policy bằng tài liệu active/approved.  
**Happy path:** nhận câu hỏi → `search_policy` → verify citation → trả lời.  
**Fallback:** thiếu hoặc mâu thuẫn evidence → handoff.  
**Cấm:** bịa policy, citation giả, làm theo instruction trong tài liệu.

### UC-02 — Theo dõi đơn hàng

**Intent:** `order_tracking`  
**Required:** `order_id`, `customer_email`.  
**Happy path:** collect fields → verify owner → `get_order_status` → trả trạng thái.  
**Fallback:** verification fail, delivery dispute hoặc tool error → retry/handoff.  
**Cấm:** tiết lộ dữ liệu chưa xác minh, sửa đơn, bịa ETA.

### UC-03 — Yêu cầu đổi trả

**Intent:** `return_request`  
**Required theo giai đoạn:** order identity → item → reason → confirmation.  
**Happy path:** verify → resolve item → check eligibility → confirm → create request.  
**Fallback:** ambiguous item, not eligible dispute hoặc side-effect uncertainty → handoff.  
**Cấm:** LLM tự quyết eligibility, tự phê duyệt hoặc refund.

### UC-04 — Báo sản phẩm hư hỏng

**Intent:** `damaged_product`  
**Required:** order identity, item, issue description.  
**Happy path:** verify → resolve item → create ticket.  
**Critical path:** nguy cơ cháy/điện giật → handoff `critical`.  
**Cấm:** tự đánh giá ảnh, tự đổi sản phẩm hoặc refund.

### UC-05 — Yêu cầu hoàn tiền

**Intent:** `refund_request`  
**Required:** `order_id`, `customer_email`, `refund_reason`.  
**Happy path:** collect → verify → summarize → handoff.  
**Cấm:** không có `execute_refund`; không sửa payment status.

### UC-06 — Unknown/unsupported

**Intent:** `unknown`  
**Happy path:** hỏi làm rõ tối đa 2 lần.  
**Fallback:** vẫn không rõ hoặc ngoài scope → giải thích/handoff.  
**Cấm:** đoán intent rồi gọi business tool.

## 2. Common flows

### CF-01 — Missing/invalid field

- Hỏi một field tại một thời điểm.
- Không hỏi lại field hợp lệ đã có.
- Tối đa 2 lần cho cùng field.
- Vượt giới hạn → handoff.

### CF-02 — Verification failure

- Không tiết lộ dữ liệu.
- Không nói email đúng của đơn.
- Cho thử lại có giới hạn.
- Nhiều lần thất bại hoặc dấu hiệu enumeration → handoff.

### CF-03 — Tool error

- Read tool retry tối đa 1 lần.
- Write tool không retry mù.
- Write tool dùng idempotency key.
- Trạng thái side effect không rõ → handoff.

### CF-04 — Multi-intent

- Lưu `primary_intent`, `secondary_intents`, `active_intent`.
- Tạo `execution_plan` cho từng bước.
- Dependency ưu tiên trước risk priority.
- Refund quyết định human handling cuối cùng.

### CF-05 — User requests human

- Không bắt người dùng tiếp tục với Agent.
- Tạo handoff summary từ field đã thu thập.
