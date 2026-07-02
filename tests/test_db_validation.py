from __future__ import annotations

from support_agent.db.validation import (
    validate_foreign_keys,
    validate_idempotency_keys,
    validate_item_consistency,
    validate_order_consistency,
    validate_required_scenarios,
    validate_unique_scenario_keys,
)


def test_validation_components_pass_for_seed_database(db_conn):
    assert validate_foreign_keys(db_conn) == []
    assert validate_unique_scenario_keys(db_conn) == []
    assert validate_required_scenarios(db_conn) == []
    assert validate_order_consistency(db_conn) == []
    assert validate_item_consistency(db_conn) == []
    assert validate_idempotency_keys(db_conn) == []
