# Updated day3_checks.py with tombstones

import sqlite3
import csv

conn = sqlite3.connect(':memory:')
cur = conn.cursor()
cur.execute('PRAGMA foreign_keys = ON')

# Create tables
cur.executescript("""
CREATE TABLE users (
    user_id INTEGER PRIMARY KEY
) STRICT;

CREATE TABLE transactions (
    txn_id TEXT,
    user_id INTEGER,
    amount REAL,
    currency TEXT,
    status TEXT,
    created_at INTEGER,
    is_tombstone INTEGER DEFAULT 0
) STRICT;

CREATE TABLE data_quality_rules (
    rule_id TEXT PRIMARY KEY,
    sql_check TEXT NOT NULL,
    severity TEXT NOT NULL
) STRICT;
""")

# Insert users
cur.executemany('INSERT INTO users VALUES (?)', [(101,), (102,), (103,)])

# Insert rules
rules = [
    ('positive_amount', 'amount > 0', 'high'),
    ('valid_currency', "currency IN ('USD','EUR','GBP','JPY')", 'high'),
    ('no_future_dates', 'created_at <= strftime("%s","now")', 'high'),
    ('valid_status', "status IN ('pending','posted','failed','completed')", 'medium'),
    ('unique_txn_id', 'COUNT(txn_id) = 1', 'high'),
    ('user_exists', 'user_id IN (SELECT user_id FROM users)', 'high'),
    ('amount_below_threshold', 'amount <= 10000', 'high')
]
cur.executemany('INSERT INTO data_quality_rules VALUES (?, ?, ?)', rules)

# Load CSV
with open('sample_data_with_bad_rows.csv', newline='') as f:
    reader = csv.reader(f)
    next(reader)
    for row in reader:
        try:
            cur.execute('INSERT INTO transactions VALUES (?, ?, ?, ?, ?, ?, 0)',
                        (row[0], int(row[1]), float(row[2]), row[3], row[4], int(row[5])))
        except sqlite3.IntegrityError:
            pass

conn.commit()

# Deduplication: tombstone duplicates keeping earliest created_at
cur.execute("""
WITH ranked AS (
    SELECT rowid, txn_id, ROW_NUMBER() OVER (PARTITION BY txn_id ORDER BY created_at) AS rn
    FROM transactions
)
UPDATE transactions
SET is_tombstone = 1
WHERE rowid IN (SELECT rowid FROM ranked WHERE rn > 1)
""")
conn.commit()

# Run checks
print("\n=== DATA QUALITY CHECK RESULTS ===\n")
for rule_id, sql_check, severity in rules:
    if rule_id == 'unique_txn_id':
        cur.execute("""
            SELECT txn_id, COUNT(*) as cnt
            FROM transactions
            WHERE is_tombstone = 0
            GROUP BY txn_id
            HAVING cnt > 1
        """)
    else:
        cur.execute(f"""
            SELECT txn_id, user_id, amount, currency, status, created_at
            FROM transactions
            WHERE NOT ({sql_check})
        """)
    failures = cur.fetchall()
    if failures:
        print(f"RULE FAILED: {rule_id} (severity: {severity})")
        for row in failures:
            print(f"  {row}")
        print()

# Revenue protection report
cur.execute("""
SELECT txn_id,
       COUNT(*) as total_attempts,
       SUM(CASE WHEN is_tombstone=0 THEN amount ELSE 0 END) as live_amount,
       SUM(CASE WHEN is_tombstone=1 THEN amount ELSE 0 END) as blocked_amount
FROM transactions
GROUP BY txn_id
HAVING COUNT(*) > 1
""")
print("\n=== REVENUE PROTECTION REPORT ===")
for row in cur.fetchall():
    txn_id, attempts, live, blocked = row
    print(f"{txn_id}: {attempts} attempts, ${live:.2f} kept, ${blocked:.2f} blocked (saved from double-charge)")

conn.close()
