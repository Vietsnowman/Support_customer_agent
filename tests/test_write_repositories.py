from __future__ import annotations

from support_agent.repositories import (
    HandoffRepository,
    ReturnRepository,
    TicketRepository,
)
from support_agent.services import make_idempotency_key


def test_ticket_creation_is_idempotent(db_conn):
    repo = TicketRepository(db_conn)
    key = make_idempotency_key(
        action="create_support_ticket",
        conversation_id="CONV-001",
        business_ids=["MD-1052", "ITEM-001"],
    )
    first, first_created = repo.create(
        order_id="MD-1052",
        item_id="ITEM-001",
        issue_description="Sản phẩm bị vỡ khi nhận.",
        damage_type="broken",
        priority="high",
        idempotency_key=key,
    )
    second, second_created = repo.create(
        order_id="MD-1052",
        item_id="ITEM-001",
        issue_description="Sản phẩm bị vỡ khi nhận.",
        damage_type="broken",
        priority="high",
        idempotency_key=key,
    )
    assert first_created is True
    assert second_created is False
    assert first.ticket_id == second.ticket_id


def test_return_request_creation_is_idempotent(db_conn):
    repo = ReturnRepository(db_conn)
    key = make_idempotency_key(
        action="create_return_request",
        conversation_id="CONV-002",
        business_ids=["MD-2001", "ITEM-004"],
    )
    first, first_created = repo.create(
        order_id="MD-2001",
        item_id="ITEM-004",
        reason="Không vừa kích thước",
        eligibility_code="eligible",
        rule_version="return-rules-v1",
        idempotency_key=key,
    )
    second, second_created = repo.create(
        order_id="MD-2001",
        item_id="ITEM-004",
        reason="Không vừa kích thước",
        eligibility_code="eligible",
        rule_version="return-rules-v1",
        idempotency_key=key,
    )
    assert first_created is True
    assert second_created is False
    assert first.return_request_id == second.return_request_id


def test_handoff_creation_is_idempotent(db_conn):
    repo = HandoffRepository(db_conn)
    key = make_idempotency_key(
        action="request_human_handoff",
        conversation_id="CONV-003",
        business_ids=["MD-1052"],
    )
    first, first_created = repo.create(
        conversation_id="CONV-003",
        primary_intent="refund_request",
        reason_code="refund_requires_human",
        priority="normal",
        collected_fields={
            "order_id": "MD-1052",
            "refund_reason": "Sản phẩm lỗi",
        },
        summary="Yêu cầu hoàn tiền cần nhân viên xem xét.",
        idempotency_key=key,
    )
    second, second_created = repo.create(
        conversation_id="CONV-003",
        primary_intent="refund_request",
        reason_code="refund_requires_human",
        priority="normal",
        collected_fields={
            "order_id": "MD-1052",
            "refund_reason": "Sản phẩm lỗi",
        },
        summary="Yêu cầu hoàn tiền cần nhân viên xem xét.",
        idempotency_key=key,
    )
    assert first_created is True
    assert second_created is False
    assert first.handoff_id == second.handoff_id
