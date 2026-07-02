from __future__ import annotations

import hashlib


def make_idempotency_key(
    *,
    action: str,
    conversation_id: str,
    business_ids: list[str],
) -> str:
    normalized = "|".join(
        [action.strip(), conversation_id.strip(), *sorted(x.strip() for x in business_ids)]
    )
    digest = hashlib.sha256(normalized.encode("utf-8")).hexdigest()[:24]
    return f"idem-{action}-{digest}"
