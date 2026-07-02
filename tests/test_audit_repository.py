from __future__ import annotations

from support_agent.repositories import AuditRepository


def test_audit_log_stores_structured_event(db_conn):
    audit_id = AuditRepository(db_conn).record(
        trace_id="TRACE-001",
        conversation_id="CONV-001",
        tool_name="get_order_status",
        tool_input={"order_id": "MD-1052"},
        status="success",
        tool_output={"fulfillment_status": "shipped"},
    )
    row = db_conn.execute(
        "SELECT * FROM tool_audit_log WHERE audit_id = ?",
        (audit_id,),
    ).fetchone()
    assert row is not None
    assert row["tool_name"] == "get_order_status"
    assert "MD-1052" in row["input_json"]
