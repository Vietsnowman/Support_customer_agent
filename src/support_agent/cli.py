from __future__ import annotations

import argparse
import json
from pathlib import Path

from support_agent.config import settings
from support_agent.db import (
    REQUIRED_SCENARIOS,
    connect,
    initialize_schema,
    reset_database,
    seed_database,
    validate_seed_dataset,
)


TABLES = (
    "orders",
    "order_items",
    "support_tickets",
    "return_requests",
    "human_handoffs",
    "tool_audit_log",
)


def _resolve(value: str | None, default: Path) -> Path:
    return Path(value).resolve() if value else default


def command_init(db_path: Path) -> None:
    with connect(db_path) as conn:
        initialize_schema(conn)
    print(f"Initialized database: {db_path}")


def command_seed(db_path: Path, seed_dir: Path) -> None:
    with connect(db_path) as conn:
        initialize_schema(conn)
        seed_database(conn, seed_dir)
    print(f"Seeded database: {db_path}")


def command_reset(db_path: Path, seed_dir: Path) -> None:
    conn = reset_database(db_path)
    try:
        seed_database(conn, seed_dir)
    finally:
        conn.close()
    print(f"Reset and seeded database: {db_path}")


def command_inspect(db_path: Path) -> None:
    with connect(db_path) as conn:
        counts = {
            table: conn.execute(f"SELECT COUNT(*) AS n FROM {table}").fetchone()["n"]
            for table in TABLES
        }
        scenarios = [
            dict(row)
            for row in conn.execute(
                """
                SELECT order_id, scenario_key, customer_email,
                       order_status, fulfillment_status, payment_status
                FROM orders ORDER BY order_id
                """
            ).fetchall()
        ]
    print(json.dumps({"counts": counts, "orders": scenarios}, ensure_ascii=False, indent=2))


def command_check(db_path: Path) -> None:
    with connect(db_path) as conn:
        counts = {
            table: conn.execute(f"SELECT COUNT(*) AS n FROM {table}").fetchone()["n"]
            for table in TABLES
        }
        errors = validate_seed_dataset(conn)
        scenarios = {
            row["scenario_key"]
            for row in conn.execute("SELECT scenario_key FROM orders").fetchall()
        }
        missing_scenarios = sorted(REQUIRED_SCENARIOS - scenarios)

    report = {
        "counts": counts,
        "foreign_key_check": "passed" if not any(
            error.startswith("foreign_key_check") for error in errors
        ) else "failed",
        "seed_validation": "passed" if not errors else "failed",
        "scenario_coverage": "passed" if not missing_scenarios else "failed",
        "missing_scenarios": missing_scenarios,
        "errors": errors,
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="SQLite mock-data utilities")
    parser.add_argument("--db", help="Override database path")
    parser.add_argument("--seeds", help="Override seed directory")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("init-db")
    sub.add_parser("seed-db")
    sub.add_parser("reset-db")
    sub.add_parser("inspect-db")
    sub.add_parser("check-db")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    db_path = _resolve(args.db, settings.db_path)
    seed_dir = _resolve(args.seeds, settings.seed_dir)

    if args.command == "init-db":
        command_init(db_path)
    elif args.command == "seed-db":
        command_seed(db_path, seed_dir)
    elif args.command == "reset-db":
        command_reset(db_path, seed_dir)
    elif args.command == "inspect-db":
        command_inspect(db_path)
    elif args.command == "check-db":
        command_check(db_path)


if __name__ == "__main__":
    main()
