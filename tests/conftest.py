from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

import pytest

from support_agent.db import reset_database, seed_database


@pytest.fixture()
def db_conn(tmp_path: Path):
    db_path = tmp_path / "test.db"
    conn = reset_database(db_path)
    seed_dir = Path(__file__).resolve().parents[1] / "data" / "seeds"
    seed_database(
        conn,
        seed_dir,
        now=datetime(2026, 7, 1, 12, 0, tzinfo=UTC),
    )
    try:
        yield conn
    finally:
        conn.close()
