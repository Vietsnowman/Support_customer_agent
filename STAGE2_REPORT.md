# Stage 2 Report — Mock Data + SQLite

## Summary

Stage 2 has been expanded directly in the project while keeping the scope suitable for a personal/student project. The implementation focuses on high-value edge cases instead of production-scale data volume.

## Added/changed

### Seed data

- Expanded orders from 6 to 19.
- Expanded order items from 7 to 36.
- Expanded support tickets from 1 to 6.
- Expanded return requests from 1 to 4.
- Expanded human handoffs from 1 to 4.

Required scenario coverage now includes:

- tracking shipped, processing, cancelled, payment failed
- return eligible day 3 and day 7
- return expired day 8 and day 20
- return not delivered
- non-returnable item
- used item
- normal damaged product
- critical safety damaged product
- ambiguous product name
- multi-item non-ambiguous order
- unauthorized email case
- refunded cancelled order
- partially refunded order
- returned order

### Validation

Added:

```text
src/support_agent/db/validation.py
```

The validator checks:

- foreign keys
- unique scenario keys
- required scenario coverage
- order date consistency
- item consistency
- idempotency key uniqueness

### Repository helpers

Added owner-safe helpers in `OrderRepository`:

```python
get_order_for_owner(order_id, email)
get_order_status_for_owner(order_id, email)
list_items_for_owner(order_id, email)
```

These helpers return no data when the supplied email does not match the order owner.

Added Stage 2/3-friendly aliases:

```python
find_order(order_id)
verify_order_owner(order_id, email)
find_order_item_by_id(order_id, item_id)
find_item_by_name(order_id, product_name)
```

### CLI

Added:

```bash
python -m support_agent.cli check-db
```

The command reports table counts, foreign key status, seed validation, scenario coverage, missing scenarios, and validation errors.

### Tests

Expanded tests from 14 to 26. New checks cover:

- minimum Stage 2 record counts
- required scenario coverage
- seed dataset validation
- validation components
- owner-safe helper blocking behavior
- item resolution single/ambiguous/none
- day 7/day 8 return eligibility boundaries
- used item return rejection

## Verification results

```text
pytest: 26 passed
behavior validator: 64 behavior cases passed
smoke cases: 22
check-db: passed
```

Current `check-db` counts:

```json
{
  "orders": 19,
  "order_items": 36,
  "support_tickets": 6,
  "return_requests": 4,
  "human_handoffs": 4,
  "tool_audit_log": 0
}
```

## Scope decision

The project intentionally does not add `customers`, `addresses`, `payment_transactions`, or shipment-history tables in Stage 2. `customer_email` remains a mock verification field for demo purposes only.
