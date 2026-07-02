from __future__ import annotations

import json
import sqlite3
from datetime import UTC, datetime
from typing import Any


def utc_now_iso() -> str:
    return datetime.now(UTC).isoformat()


def json_text(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True)


def next_business_id(
    conn: sqlite3.Connection,
    sequence_name: str,
    prefix: str,
) -> str:
    row = conn.execute(
        "SELECT next_value FROM id_sequences WHERE name = ?",
        (sequence_name,),
    ).fetchone()
    if row is None:
        raise RuntimeError(f"Missing ID sequence: {sequence_name}")

    value = int(row["next_value"])
    conn.execute(
        "UPDATE id_sequences SET next_value = ? WHERE name = ?",
        (value + 1, sequence_name),
    )
    return f"{prefix}{value:04d}"
