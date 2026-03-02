def make_idempotency_key(*parts: str) -> str:
    return ":".join(parts)
