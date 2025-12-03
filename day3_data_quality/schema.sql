-- schema.sql

CREATE TABLE users (
    user_id INTEGER PRIMARY KEY
) STRICT;

CREATE TABLE transactions (
    txn_id TEXT PRIMARY KEY,
    user_id INTEGER NOT NULL,
    amount REAL NOT NULL,
    currency TEXT NOT NULL,
    status TEXT NOT NULL,
    created_at INTEGER NOT NULL
) STRICT;

CREATE TABLE data_quality_rules (
    rule_id TEXT PRIMARY KEY,
    sql_check TEXT NOT NULL,
    severity TEXT NOT NULL
) STRICT;
