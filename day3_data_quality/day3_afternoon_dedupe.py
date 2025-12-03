# day3_afternoon_dedupe.py
import sqlite3
from datetime import datetime

conn = sqlite3.connect(':memory:')
cur = conn.cursor()

# Create transactions table WITHOUT unique constraint (simulate broken prod)
cur.execute('''
CREATE TABLE transactions (
    txn_id TEXT,
    user_id INTEGER,
    amount REAL,
    status TEXT,
    created_at INTEGER,
    is_tombstone INTEGER DEFAULT 0
) STRICT
''')

# Simulate duplicate ingestion (API retry)
duplicates = [
    ('txn_123', 101, 100.00, 'completed', 1732869500, 0),  # Original
    ('txn_123', 101, 105.00, 'completed', 1732869510, 0),  # Retry (wrong amount)
    ('txn_124', 102, 50.00, 'completed', 1732869520, 0),   # Good
    ('txn_125', 103, 75.00, 'completed', 1732869530, 0),   # Original
    ('txn_125', 103, 75.00, 'completed', 1732869540, 0),   # Retry (same amount)
]

cur.executemany('INSERT INTO transactions VALUES (?, ?, ?, ?, ?, ?)', duplicates)
conn.commit()

print("=== BEFORE DEDUPLICATION ===")
cur.execute('SELECT * FROM transactions ORDER BY txn_id, created_at')
for row in cur.fetchall():
    print(row)

# Deduplication logic: Keep earliest created_at, mark rest as tombstones
cur.execute('''
WITH ranked AS (
    SELECT
        rowid,
        txn_id,
        ROW_NUMBER() OVER (PARTITION BY txn_id ORDER BY created_at) as rn
    FROM transactions
)
UPDATE transactions
SET is_tombstone = 1
WHERE rowid IN (
    SELECT rowid FROM ranked WHERE rn > 1
)
''')
conn.commit()

print("\n=== AFTER DEDUPLICATION ===")
cur.execute('SELECT * FROM transactions WHERE is_tombstone = 0 ORDER BY txn_id')
print("Live transactions:")
for row in cur.fetchall():
    print(row)

cur.execute('SELECT * FROM transactions WHERE is_tombstone = 1 ORDER BY txn_id')
print("\nTombstoned (duplicate) transactions:")
for row in cur.fetchall():
    print(row)

# Revenue Protection check
cur.execute('''
SELECT
    txn_id,
    COUNT(*) as total_attempts,
    SUM(CASE WHEN is_tombstone = 0 THEN amount ELSE 0 END) as live_amount,
    SUM(CASE WHEN is_tombstone = 1 THEN amount ELSE 0 END) as blocked_amount
FROM transactions
GROUP BY txn_id
HAVING COUNT(*) > 1
''')
print("\n=== REVENUE PROTECTION REPORT ===")
for row in cur.fetchall():
    txn_id, attempts, live, blocked = row
    print(f"{txn_id}: {attempts} attempts, ${live:.2f} kept, ${blocked:.2f} blocked (saved from double-charge)")

conn.close()
