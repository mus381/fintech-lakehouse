-- Day 2: FinTech Transactions Schema
-- Purpose: Type-safe, idempotent ledger with explicit error handling
-- Key Constraints: STRICT mode, CHECK for positive amounts, UNIQUE txn_id

CREATE TABLE IF NOT EXISTS transactions (
    pk INTEGER PRIMARY KEY AUTOINCREMENT,
    txn_id TEXT NOT NULL UNIQUE,           -- External idempotency key
    user_id INTEGER NOT NULL,
    amount REAL NOT NULL CHECK(amount > 0), -- No negative amounts
    currency TEXT NOT NULL,
    status TEXT NOT NULL,
    created_at INTEGER NOT NULL             -- Unix timestamp (UTC)
) STRICT;

-- Why STRICT? Prevents silent type coercion (e.g., '50.00' stored as TEXT)
-- Why txn_id? Enables idempotent retries; pk alone is insufficient
-- Why INTEGER timestamps? Immune to timezone bugs and string formatting issues
