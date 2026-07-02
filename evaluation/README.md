# Behavior Evaluation

Bộ evaluation gồm 64 cases:

- 22 smoke cases cho phát triển hằng ngày.
- 42 regression cases cho release/demo.

## Chạy validator

Từ repository root:

```bash
python evaluation/scripts/validate_behavior_cases.py
```

Validator đọc đường dẫn dựa trên vị trí script, không phụ thuộc current working directory.

## Những gì được kiểm tra

- JSON Schema.
- Vocabulary từ `config/agent-spec.json`.
- Tool authorization.
- Global handoff tool condition.
- Safety block không gọi tool.
- Multi-intent có execution plan.
- `next_action` là atomic.
- Human-handling consistency.
- Coverage report.

Behavior cases mô tả expected decision state, không kiểm tra chain-of-thought.
