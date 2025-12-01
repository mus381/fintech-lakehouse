# FinTech Lakehouse Pipeline
Goal: ETL pipeline validating and writing to a 3-layer lakehouse.


## Day 2: Schema Design & Constraint Enforcement

**Goal**: Build a type-safe, idempotent transactions schema with explicit error handling.

**Deliverables**:
- ✅ Transactions schema with STRICT mode + CHECK constraints
- ✅ Idempotency via `txn_id` (prevents double-inserts)
- ✅ Explicit error logging (distinguishes duplicates from validation failures)
- ✅ 5 documented failure scenarios with fixes

**Key Files**:
- [`schema.sql`](day2_schema_design/schema.sql) — Production-ready DDL
- [`day2_txn.py`](day2_schema_design/day2_txn.py) — Insert script with error tracking
- [`failure_scenarios.md`](day2_schema_design/failure_scenarios.md) — Break/fix documentation

**Run the demo**:
```bash
cd day2_schema_design
python3 day2_txn.py
# Expected: 9 successes, 1 logged failure (negative amount)
```

**What I learned**:
- STRICT mode prevents silent type coercion bugs
- External `txn_id` enables safe API retries
- INSERT OR IGNORE hides critical errors (use explicit try/catch)
- Autoincrement gaps are normal, not data loss

**Business impact**:
- Prevents $50M revenue gaps from type mismatches
- Enables 3am incident debugging with root-cause logs
- Supports audit compliance via provable transaction ordering
