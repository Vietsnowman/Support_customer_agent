from __future__ import annotations

import sqlite3
from datetime import datetime

from support_agent.models.domain import SupportTicket
from support_agent.repositories.base import next_business_id, utc_now_iso


class TicketRepository:
    def __init__(self, conn: sqlite3.Connection) -> None:
        self.conn = conn

    def get_by_idempotency_key(self, key: str) -> SupportTicket | None:
        row = self.conn.execute(
            "SELECT * FROM support_tickets WHERE idempotency_key = ?",
            (key,),
        ).fetchone()
        return _from_row(row) if row else None

    def create(
        self,
        *,
        order_id: str,
        item_id: str | None,
        issue_description: str,
        damage_type: str,
        priority: str,
        idempotency_key: str,
    ) -> tuple[SupportTicket, bool]:
        existing = self.get_by_idempotency_key(idempotency_key)
        if existing:
            return existing, False

        with self.conn:
            ticket_id = next_business_id(self.conn, "ticket", "TICKET-")
            now = utc_now_iso()
            self.conn.execute(
                """
                INSERT INTO support_tickets (
                    ticket_id, order_id, item_id, issue_description,
                    damage_type, priority, status, idempotency_key,
                    created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, 'open', ?, ?, ?)
                """,
                (
                    ticket_id,
                    order_id,
                    item_id,
                    issue_description,
                    damage_type,
                    priority,
                    idempotency_key,
                    now,
                    now,
                ),
            )
        created = self.get_by_idempotency_key(idempotency_key)
        if created is None:
            raise RuntimeError("Ticket insert succeeded but row was not found")
        return created, True


def _from_row(row: sqlite3.Row) -> SupportTicket:
    return SupportTicket(
        ticket_id=row["ticket_id"],
        order_id=row["order_id"],
        item_id=row["item_id"],
        issue_description=row["issue_description"],
        damage_type=row["damage_type"],
        priority=row["priority"],
        status=row["status"],
        idempotency_key=row["idempotency_key"],
        created_at=datetime.fromisoformat(row["created_at"]),
        updated_at=datetime.fromisoformat(row["updated_at"]),
    )
