from __future__ import annotations

import sqlite3
from datetime import datetime

from support_agent.models.domain import ReturnRequest
from support_agent.repositories.base import next_business_id, utc_now_iso


class ReturnRepository:
    def __init__(self, conn: sqlite3.Connection) -> None:
        self.conn = conn

    def get_by_idempotency_key(self, key: str) -> ReturnRequest | None:
        row = self.conn.execute(
            "SELECT * FROM return_requests WHERE idempotency_key = ?",
            (key,),
        ).fetchone()
        return _from_row(row) if row else None

    def create(
        self,
        *,
        order_id: str,
        item_id: str,
        reason: str,
        eligibility_code: str,
        rule_version: str,
        idempotency_key: str,
    ) -> tuple[ReturnRequest, bool]:
        existing = self.get_by_idempotency_key(idempotency_key)
        if existing:
            return existing, False

        with self.conn:
            request_id = next_business_id(self.conn, "return", "RET-")
            now = utc_now_iso()
            self.conn.execute(
                """
                INSERT INTO return_requests (
                    return_request_id, order_id, item_id, reason,
                    eligibility_code, rule_version, status,
                    idempotency_key, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, 'pending_review', ?, ?)
                """,
                (
                    request_id,
                    order_id,
                    item_id,
                    reason,
                    eligibility_code,
                    rule_version,
                    idempotency_key,
                    now,
                ),
            )
        created = self.get_by_idempotency_key(idempotency_key)
        if created is None:
            raise RuntimeError("Return insert succeeded but row was not found")
        return created, True


def _from_row(row: sqlite3.Row) -> ReturnRequest:
    return ReturnRequest(
        return_request_id=row["return_request_id"],
        order_id=row["order_id"],
        item_id=row["item_id"],
        reason=row["reason"],
        eligibility_code=row["eligibility_code"],
        rule_version=row["rule_version"],
        status=row["status"],
        idempotency_key=row["idempotency_key"],
        created_at=datetime.fromisoformat(row["created_at"]),
    )
