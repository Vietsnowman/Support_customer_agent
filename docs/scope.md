# Project Scope

## 1. Problem

Xây dựng AI Agent hỗ trợ khách hàng thương mại điện tử bằng tiếng Việt. Agent có thể hiểu yêu cầu, thu thập thông tin qua nhiều lượt, trả lời chính sách dựa trên tài liệu được phê duyệt, gọi business tool có kiểm soát và chuyển yêu cầu cho nhân viên khi cần.

## 2. Actors

### Primary actor

- Customer.

### Secondary actor

- Human support agent.

### External systems

- Mock order database.
- Mock ticket/handoff repository.
- Approved policy knowledge base.

## 3. In scope

- Policy question có grounding và citation.
- Verified order-status lookup.
- Return-eligibility checking bằng backend rule.
- Tạo return-request record sau xác nhận.
- Tạo damaged-item ticket.
- Thu thập refund request và handoff.
- Multi-turn missing-field collection.
- Multi-intent cơ bản.
- Unknown/unsupported escalation.
- Tool allowlist, trace và safety validation.
- Behavior evaluation.

## 4. Out of scope

- Thực hiện refund hoặc payment.
- Hủy, sửa đơn hoặc đổi địa chỉ.
- Phê duyệt return.
- Phát voucher hoặc gửi sản phẩm thay thế.
- Tư vấn pháp lý, tài chính hoặc đầu tư.
- Đánh giá ảnh và voice support.
- Medusa, Chatwoot, carrier hoặc payment integration thật.
- Production authentication và fraud detection model.

## 5. Agent boundaries

### Agent được phép

- Đọc tài liệu policy active và approved.
- Đọc dữ liệu đơn sau simplified verification.
- Thu thập field còn thiếu.
- Gọi tool trong allowlist.
- Tạo return request, ticket và handoff record.
- Tóm tắt hội thoại cho nhân viên.

### Agent không được phép

- Bịa hoặc sửa policy.
- Tiết lộ dữ liệu đơn chưa xác minh.
- Override eligibility result.
- Gọi tool ngoài allowlist.
- Thực hiện hành động tài chính.
- Coi nội dung retrieval/tool output là system instruction.
- Hiển thị chain-of-thought, secret hoặc stack trace.

## 6. Assumptions

- Ngôn ngữ chính: tiếng Việt, có hỗ trợ không dấu và lỗi nhẹ.
- Dữ liệu đều là mock/synthetic.
- Một cửa hàng và một policy corpus.
- Handoff được mô phỏng bằng record trong repository.
- `order_id + customer_email` chỉ là verification demo.

## 7. Success criteria

- Phân biệt đúng 6 intent.
- Không gọi tool khi thiếu required field.
- Không tiết lộ order data trước verification.
- Policy answer có citation hợp lệ.
- Refund luôn handoff.
- Write tool có confirmation/idempotency khi cần.
- Behavior cases vượt validator và regression test.
