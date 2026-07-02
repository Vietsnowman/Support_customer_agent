# Stage 1 Validation Report

## Result

Stage 1 — Python environment and SQLite mock data is implemented.

## Implemented

- Python package using `src/` layout.
- Python 3.11 setup scripts for Windows and Unix.
- SQLite schema with foreign keys, checks, indexes and transactions.
- Tables: orders, items, support tickets, return requests, human handoffs, audit logs and ID sequences.
- Relative-date seed loader to keep eligible/expired scenarios stable.
- Six order scenarios and seven items.
- Pydantic domain models.
- Parameterized repository queries.
- Vietnamese-safe item matching using Python `casefold()`.
- Deterministic return eligibility rules.
- Idempotent ticket, return and handoff creation.
- Database CLI.
- Generated demo database.
- Unit tests.

## Validation

```text
Behavior specification validator: 64/64 passed
Smoke cases:                     22
Unit tests:                      14 passed
SQLite foreign_key_check:        no errors
Editable package install:        passed
Console command:                 passed
```

## Mock scenarios

| Order | Scenario |
|---|---|
| MD-1052 | shipped order with two similar products |
| MD-1053 | return window expired |
| MD-2001 | return eligible |
| MD-2002 | non-returnable product |
| MD-2003 | critical product safety incident |
| MD-2004 | cancelled order |

## Next milestone

Milestone 2 should wrap these repositories and services with the eight deterministic tool contracts defined in `docs/tool-policy.md`.
