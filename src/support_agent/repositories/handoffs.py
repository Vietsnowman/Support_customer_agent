from __future__ import annotations

import json
import sqlite3
from datetime import datetime
from typing import Any

from support_agent.models.domain import HandoffRecord
from support_agent.repositories.base import next_business_id, utc_now_iso


class HandoffRepository:
    def __init__(self, conn: sqlite3.Connection) -> None:
        self.conn = conn

    def get_by_idempotency_key(self, key: str) -> HandoffRecord | None:
        row = self.conn.execute(
            "SELECT * FROM human_handoffs WHERE idempotency_key = ?",
            (key,),
        ).fetchone()
        return _from_row(row) if row else None

    def create(
        self,
        *,
        conversation_id: str,
        primary_intent: str,
        reason_code: str,
        priority: str,
        collected_fields: dict[str, Any],
        summary: str,
        idempotency_key: str,
    ) -> tuple[HandoffRecord, bool]:
        existing = self.get_by_idempotency_key(idempotency_key)
        if existing:
            return existing, False

        with self.conn:
            handoff_id = next_business_id(self.conn, "handoff", "HANDOFF-")
            now = utc_now_iso()
            self.conn.execute(
                """
                INSERT INTO human_handoffs (
                    handoff_id, conversation_id, primary_intent,
                    reason_code, priority, collected_fields_json,
                    summary, status, idempotency_key, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, 'pending_human_review', ?, ?)
                """,
                (
                    handoff_id,
                    conversation_id,
                    primary_intent,
                    reason_code,
                    priority,
                    json.dumps(collected_fields, ensure_ascii=False, sort_keys=True),
                    summary,
                    idempotency_key,
                    now,
                ),
            )
        created = self.get_by_idempotency_key(idempotency_key)
        if created is None:
            raise RuntimeError("Handoff insert succeeded but row was not found")
        return created, True


def _from_row(row: sqlite3.Row) -> HandoffRecord:
    return HandoffRecord(
        handoff_id=row["handoff_id"],
        conversation_id=row["conversation_id"],
        primary_intent=row["primary_intent"],
        reason_code=row["reason_code"],
        priority=row["priority"],
        collected_fields=json.loads(row["collected_fields_json"]),
        summary=row["summary"],
        status=row["status"],
        idempotency_key=row["idempotency_key"],
        created_at=datetime.fromisoformat(row["created_at"]),
    )
