PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS id_sequences (
    name TEXT PRIMARY KEY,
    next_value INTEGER NOT NULL CHECK (next_value >= 1)
);

CREATE TABLE IF NOT EXISTS orders (
    order_id TEXT PRIMARY KEY,
    customer_email TEXT NOT NULL COLLATE NOCASE,
    scenario_key TEXT NOT NULL UNIQUE,
    order_status TEXT NOT NULL CHECK (
        order_status IN ('pending', 'processing', 'completed', 'cancelled')
    ),
    fulfillment_status TEXT NOT NULL CHECK (
        fulfillment_status IN (
            'not_fulfilled', 'processing', 'shipped',
            'delivered', 'returned', 'cancelled'
        )
    ),
    payment_status TEXT NOT NULL CHECK (
        payment_status IN (
            'pending', 'authorized', 'captured',
            'refunded', 'partially_refunded', 'failed'
        )
    ),
    created_at TEXT NOT NULL,
    shipped_at TEXT,
    delivered_at TEXT,
    estimated_delivery TEXT,
    currency TEXT NOT NULL DEFAULT 'VND',
    total_amount INTEGER NOT NULL CHECK (total_amount >= 0),
    version INTEGER NOT NULL DEFAULT 1 CHECK (version >= 1)
);

CREATE INDEX IF NOT EXISTS idx_orders_email
ON orders(customer_email);

CREATE INDEX IF NOT EXISTS idx_orders_fulfillment
ON orders(fulfillment_status);

CREATE TABLE IF NOT EXISTS order_items (
    item_id TEXT PRIMARY KEY,
    order_id TEXT NOT NULL,
    sku TEXT NOT NULL,
    product_name TEXT NOT NULL,
    category TEXT NOT NULL,
    quantity INTEGER NOT NULL CHECK (quantity >= 1),
    unit_price INTEGER NOT NULL CHECK (unit_price >= 0),
    returnable INTEGER NOT NULL CHECK (returnable IN (0, 1)),
    condition_status TEXT NOT NULL CHECK (
        condition_status IN ('new', 'opened', 'used', 'damaged')
    ),
    FOREIGN KEY (order_id) REFERENCES orders(order_id) ON DELETE CASCADE,
    UNIQUE (order_id, sku)
);

CREATE INDEX IF NOT EXISTS idx_order_items_order_id
ON order_items(order_id);

CREATE INDEX IF NOT EXISTS idx_order_items_product_name
ON order_items(product_name);

CREATE TABLE IF NOT EXISTS support_tickets (
    ticket_id TEXT PRIMARY KEY,
    order_id TEXT NOT NULL,
    item_id TEXT,
    issue_description TEXT NOT NULL,
    damage_type TEXT NOT NULL,
    priority TEXT NOT NULL CHECK (
        priority IN ('low', 'normal', 'high', 'critical')
    ),
    status TEXT NOT NULL CHECK (
        status IN ('open', 'pending', 'resolved', 'closed')
    ),
    idempotency_key TEXT NOT NULL UNIQUE,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    FOREIGN KEY (order_id) REFERENCES orders(order_id),
    FOREIGN KEY (item_id) REFERENCES order_items(item_id)
);

CREATE INDEX IF NOT EXISTS idx_tickets_order_item
ON support_tickets(order_id, item_id);

CREATE TABLE IF NOT EXISTS return_requests (
    return_request_id TEXT PRIMARY KEY,
    order_id TEXT NOT NULL,
    item_id TEXT NOT NULL,
    reason TEXT NOT NULL,
    eligibility_code TEXT NOT NULL,
    rule_version TEXT NOT NULL,
    status TEXT NOT NULL CHECK (
        status IN ('pending_review', 'approved', 'rejected', 'cancelled')
    ),
    idempotency_key TEXT NOT NULL UNIQUE,
    created_at TEXT NOT NULL,
    FOREIGN KEY (order_id) REFERENCES orders(order_id),
    FOREIGN KEY (item_id) REFERENCES order_items(item_id)
);

CREATE INDEX IF NOT EXISTS idx_return_requests_order_item
ON return_requests(order_id, item_id);

CREATE TABLE IF NOT EXISTS human_handoffs (
    handoff_id TEXT PRIMARY KEY,
    conversation_id TEXT NOT NULL,
    primary_intent TEXT NOT NULL,
    reason_code TEXT NOT NULL,
    priority TEXT NOT NULL CHECK (
        priority IN ('low', 'normal', 'high', 'critical')
    ),
    collected_fields_json TEXT NOT NULL,
    summary TEXT NOT NULL,
    status TEXT NOT NULL CHECK (
        status IN ('pending_human_review', 'assigned', 'resolved')
    ),
    idempotency_key TEXT NOT NULL UNIQUE,
    created_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_handoffs_conversation
ON human_handoffs(conversation_id);

CREATE TABLE IF NOT EXISTS tool_audit_log (
    audit_id INTEGER PRIMARY KEY AUTOINCREMENT,
    trace_id TEXT NOT NULL,
    conversation_id TEXT,
    tool_name TEXT NOT NULL,
    input_json TEXT NOT NULL,
    output_json TEXT,
    status TEXT NOT NULL CHECK (
        status IN ('pending', 'success', 'failed', 'timeout', 'unknown')
    ),
    error_code TEXT,
    idempotency_key TEXT,
    created_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_tool_audit_trace
ON tool_audit_log(trace_id);
