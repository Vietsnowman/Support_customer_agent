from __future__ import annotations

from support_agent.db import REQUIRED_SCENARIOS, validate_seed_dataset


def _count(db_conn, table: str) -> int:
    return db_conn.execute(f"SELECT COUNT(*) AS n FROM {table}").fetchone()["n"]


def test_seed_has_enough_stage2_records(db_conn):
    assert _count(db_conn, "orders") >= 16
    assert _count(db_conn, "order_items") >= 30
    assert _count(db_conn, "support_tickets") >= 5
    assert _count(db_conn, "return_requests") >= 3
    assert _count(db_conn, "human_handoffs") >= 3


def test_all_foreign_keys_are_valid(db_conn):
    problems = db_conn.execute("PRAGMA foreign_key_check").fetchall()
    assert problems == []


def test_required_stage2_scenarios_exist(db_conn):
    rows = db_conn.execute("SELECT scenario_key FROM orders").fetchall()
    actual = {row["scenario_key"] for row in rows}
    assert REQUIRED_SCENARIOS <= actual


def test_seed_dataset_validation_passes(db_conn):
    assert validate_seed_dataset(db_conn) == []


def test_no_duplicate_scenario_keys(db_conn):
    rows = db_conn.execute(
        """
        SELECT scenario_key, COUNT(*) AS n
        FROM orders
        GROUP BY scenario_key
        HAVING n > 1
        """
    ).fetchall()
    assert rows == []
