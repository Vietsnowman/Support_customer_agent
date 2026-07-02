# Implementation Plan

## Milestone 1 — Schemas and mock data

- Pydantic schemas từ `agent-spec.json`.
- SQLite mock orders, items, tickets, returns, handoffs.
- Entity normalizer và validator.

## Milestone 2 — Deterministic tools

- Implement 8 tools.
- Unit test precondition, output schema, retry và idempotency.

## Milestone 3 — Policy RAG

- Approved policy corpus.
- BM25 + dense retrieval.
- Citation verifier.

## Milestone 4 — Intent and entity understanding

- Structured LLM output.
- Regex cho order/email/item ID.
- Missing/invalid/ambiguous/conflicting detection.

## Milestone 5 — LangGraph workflow

- 11 canonical routes.
- Multi-turn state.
- Basic multi-intent execution plan.

## Milestone 6 — Safety and handoff

- Authorization middleware.
- Safety validator.
- Mock handoff repository.

## Milestone 7 — Evaluation

- Chạy 22 smoke cases thường xuyên.
- Chạy đủ 64 cases trước release/demo.
- Báo cáo intent, route, tool và safety metrics.

## Milestone 8 — Streamlit demo

- Chat UI.
- Structured execution trace, không hiển thị chain-of-thought.
- Evaluation summary.

## Không bắt buộc cho CV-ready

- FastAPI/Docker.
- Local LLM comparison.
- Real integrations.
- Advanced fraud model.
- Image damage model.
