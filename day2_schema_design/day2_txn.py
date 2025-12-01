import sqlite3
# Connect to persistent DB
conn = sqlite3.connect('txn.db')
cur = conn.cursor()
# Create transactions table if missing
cur.execute("""
CREATE TABLE IF NOT EXISTS transactions (
    pk INTEGER PRIMARY KEY AUTOINCREMENT,
    txn_id TEXT NOT NULL UNIQUE,
    user_id INTEGER NOT NULL,
    amount REAL NOT NULL CHECK(amount > 0),
    currency TEXT NOT NULL,
    status TEXT NOT NULL,
    created_at INTEGER NOT NULL
) STRICT
""")
# Insert 10 rows with unique txn_id
rows = [
    ('txn_001', 101, 50.00, 'USD', 'completed', 1732869300),
    ('txn_002', 102, 75.50, 'USD', 'completed', 1732869390),
    ('txn_003', 101, 120.00, 'EUR', 'pending', 1732869525),
    ('txn_004', 103, 200.00, 'USD', 'completed', 1732869612),
    ('txn_005', 102, -9999.00, 'GBP', 'failed', 1732869720),
    ('txn_006', 104, 500.00, 'USD', 'completed', 1732869930),
    ('txn_007', 101, 80.00, 'USD', 'completed', 1732870035),
    ('txn_008', 103, 150.00, 'EUR', 'pending', 1732870200),
    ('txn_009', 105, 60.00, 'USD', 'completed', 1732870365),
    ('txn_010', 104, 90.00, 'GBP', 'completed', 1732870500)
]
# Insert rows, skipping duplicates based on txn_id
successes = []
failures = []

for row in rows:
    try:
        cur.execute("""
            INSERT INTO transactions
            (txn_id, user_id, amount, currency, status, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, row)
        successes.append(row[0])  # Log the txn_id
    except sqlite3.IntegrityError as e:
        failures.append((row[0], str(e)))  # Log txn_id + error

conn.commit()

print(f"✅ Successes: {len(successes)}")
print(f"❌ Failures: {len(failures)}")
for txn_id, error in failures:
    print(f"   - {txn_id}: {error}")
# Query min and max created_at and total rows
cur.execute("SELECT MIN(created_at), MAX(created_at), COUNT(*) FROM transactions")
earliest, latest, total = cur.fetchone()
print(f"Earliest: {earliest}, Latest: {latest}, Total rows: {total}")
conn.close()
