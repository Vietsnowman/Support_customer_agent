from __future__ import annotations

import sqlite3
from typing import Any

from support_agent.repositories.base import json_text, utc_now_iso


class AuditRepository:
    def __init__(self, conn: sqlite3.Connection) -> None:
        self.conn = conn

    def record(
        self,
        *,
        trace_id: str,
        conversation_id: str | None,
        tool_name: str,
        tool_input: dict[str, Any],
        status: str,
        tool_output: dict[str, Any] | None = None,
        error_code: str | None = None,
        idempotency_key: str | None = None,
    ) -> int:
        with self.conn:
            cursor = self.conn.execute(
                """
                INSERT INTO tool_audit_log (
                    trace_id, conversation_id, tool_name,
                    input_json, output_json, status,
                    error_code, idempotency_key, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    trace_id,
                    conversation_id,
                    tool_name,
                    json_text(tool_input),
                    json_text(tool_output) if tool_output is not None else None,
                    status,
                    error_code,
                    idempotency_key,
                    utc_now_iso(),
                ),
            )
        return int(cursor.lastrowid)
