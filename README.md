# E-commerce Support Agent Mini — CV-ready Specification

Dự án mô phỏng một AI Agent hỗ trợ khách hàng thương mại điện tử bằng tiếng Việt. Phiên bản này được thu gọn để phù hợp với dự án cá nhân nhưng vẫn thể hiện các năng lực quan trọng trên CV:

- Phân loại 6 intent và trích xuất entity có cấu trúc.
- Hội thoại nhiều lượt để thu thập field còn thiếu.
- Hybrid RAG cho policy có citation.
- Tool calling có allowlist và precondition.
- Xác minh đơn hàng trước khi đọc dữ liệu.
- Return eligibility bằng rule backend.
- Human handoff cho refund và tình huống rủi ro.
- Multi-intent cơ bản với execution plan.
- Safety validation và behavior evaluation.

## Phạm vi CV-ready

Phiên bản triển khai mục tiêu gồm:

```text
6 intents
11 routes
8 tools
24 decision reason codes
64 behavior cases
22 smoke cases
SQLite mock database
Streamlit demo
```

Không triển khai payment/refund thực, Medusa, Chatwoot, image assessment hoặc production authentication.

## Cấu trúc

```text
support_agent_cv_ready_final/
├── README.md
├── config/
│   └── agent-spec.json
├── docs/
│   ├── scope.md
│   ├── use-cases.md
│   ├── intents.md
│   ├── entities.md
│   ├── routing-policy.md
│   ├── tool-policy.md
│   ├── safety-policy.md
│   └── implementation-plan.md
├── schemas/
│   └── agent-state.schema.json
├── evaluation/
│   ├── README.md
│   ├── datasets/
│   │   ├── behavior_cases.jsonl
│   │   └── smoke_cases.jsonl
│   ├── schemas/
│   │   └── behavior-case.schema.json
│   ├── scripts/
│   │   └── validate_behavior_cases.py
│   └── reports/
│       └── behavior_cases_coverage.json
├── requirements-dev.txt
└── .gitignore
```

## Nguồn chân lý duy nhất

`config/agent-spec.json` là nguồn canonical cho:

- Intent.
- Route.
- Workflow status.
- Tool.
- Reason code.
- Allowlist.
- Required field.

Các tài liệu và validator phải dùng cùng vocabulary này.

## Kiểm tra bộ đặc tả

```bash
python -m pip install -r requirements-dev.txt
python evaluation/scripts/validate_behavior_cases.py
```

Validator kiểm tra:

- JSON Schema.
- Case ID trùng.
- Enum và vocabulary.
- Tool authorization.
- Human handoff consistency.
- Multi-intent execution plan.
- Atomic `next_action`.
- Coverage report.

## Mục tiêu đánh giá đề xuất

Đây là mục tiêu triển khai, không phải kết quả đã đạt:

```text
Primary intent accuracy       >= 90%
Route accuracy                >= 90%
Tool-selection accuracy       >= 95%
Task success rate             >= 85%
Unauthorized tool-call rate   = 0%
Unauthorized data disclosure  = 0%
```

## Lưu ý an toàn

Cơ chế xác minh `order_id + customer_email` chỉ là giả lập cho demo. Không được coi đây là cơ chế xác thực production.

---

## Giai đoạn 1–2 — Python environment và SQLite mock data

Bản này đã bổ sung triển khai nền Stage 1 và bản Stage 2 vừa sức cho dự án cá nhân:

- Python package theo `src/` layout.
- SQLite schema cho orders, items, tickets, returns, handoffs và audit log.
- Seed data mở rộng theo edge case nghiệp vụ: 19 orders, 36 order items, 6 tickets, 4 return requests và 4 handoffs.
- Required scenario coverage cho tracking, return, damaged, refund/handoff, unauthorized và ambiguous product name.
- Pydantic domain models và seed validation.
- `validate_seed_dataset(conn)` để kiểm tra foreign key, scenario coverage, date consistency, item consistency và idempotency key.
- Repository layer dùng parameterized SQL.
- Owner-safe repository helpers: `get_order_for_owner`, `get_order_status_for_owner`, `list_items_for_owner`.
- Deterministic return eligibility.
- Idempotency cho write operations.
- CLI khởi tạo/reset/inspect/check database.
- Unit tests cho schema, seed validation, repository, return eligibility, idempotency và audit log.

### Khởi tạo nhanh trên Windows

```powershell
Set-ExecutionPolicy -Scope Process Bypass
.\scripts\setup.ps1
```

### Chạy thủ công

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
Copy-Item .env.example .env
python -m support_agent.cli reset-db
python -m support_agent.cli inspect-db
python -m support_agent.cli check-db
pytest
```

Tài liệu chi tiết: `docs/stage1-mock-data.md` và `docs/stage2-mock-data.md`.
