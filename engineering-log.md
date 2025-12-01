# Engineering Log

## [2025-11-29] Day 1: Repo Setup & Scaffolding

- **Time Spent:** 1 hour
- **Shipped:** Initial repo skeleton, Makefile, directory structure (src/tests/docs).
- **Tests:** Ran `make ready` (Success).
- **What Broke:** Nothing yet (setup phase).
- **Lesson:** Learned the basics of GitHub Actions syntax (YAML).
- **Reflection (Which KPI?):** This repo will prove the KPI: "Raw → clean latency < 2 minutes for 95% of 1k synthetic transactions."

## Dec 2 2025;

## Day 2: Schema Design & Constraint Enforcement (December 1, 2025)

### Objective
Design a type-safe, idempotent transactions schema with explicit error handling.

### What I Built
1. **Transactions schema** with 7 columns:
   - `pk` (AUTOINCREMENT primary key)
   - `txn_id` (external idempotency key, UNIQUE)
   - `user_id`, `amount`, `currency`, `status`, `created_at`
2. **Type enforcement** via STRICT mode + INTEGER timestamps
3. **Business rules** via CHECK constraint (amount > 0)
4. **Error logging** via manual try/catch (replaced INSERT OR IGNORE)

### Failure Modes Debugged
| Scenario | Symptom | Root Cause | Fix |
|----------|---------|------------|-----|
| Type coercion | Wrong SUM results | Dynamic typing | STRICT mode |
| Bad timestamps | Incorrect sorting | TEXT allows garbage | INTEGER + STRICT |
| Duplicates | 20 rows instead of 10 | No unique constraint | txn_id UNIQUE |
| Silent failures | Negative amount skipped | INSERT OR IGNORE | Explicit try/catch |
| Gap confusion | MAX(pk) ≠ COUNT(*) | Autoincrement reserves pk | Expected behavior |

### Key Learnings (Teach-Backs)

**1. Why external txn_id?**
Idempotency must be guaranteed before the database is touched. API clients need a stable, replay-safe identifier that isn't tied to internal storage.

**2. When is INSERT OR IGNORE safe?**
Only for non-critical duplicates (idempotency checks). For validation failures (negative amounts, invalid currency), explicit error handling is required because silent skips hide business-critical bugs.

**3. What do pk gaps mean?**
Gaps where `MAX(pk) > COUNT(*)` indicate rejected inserts or deletes. This is normal behavior; autoincrement is for internal ordering, not auditing. Use `txn_id` for financial reconciliation.

### FinTech Anchors (Business Impact)
- **Compliance**: INTEGER timestamps enable provable transaction ordering for audits
- **Revenue Protection**: STRICT mode prevents $50M gaps from silent type coercion
- **Fraud Prevention**: CHECK constraints reject malformed data at write-time
- **Operational Efficiency**: Explicit error logs enable root-cause debugging during incidents

### Artifacts Shipped
- `schema.sql` — Reusable DDL with inline rationale
- `day2_txn.py` — Working insert script with error logging
- `sample_data.csv` — 10 test transactions
- `failure_scenarios.md` — 5 break/fix scenarios documented
- `lessons_learned.md` — Teach-backs and decision rules

### Time Spent
- Morning Block (schema + type safety): 2.5 hours
- Afternoon Block (idempotency + error handling): 2 hours
- Documentation + commit prep: 1 hour
- **Total**: 5.5 hours

### Spaced Recall Plan
- **48 hours (Dec 2)**: From memory, write the 3 bugs fixed + root causes
- **10 days (Dec 10)**: Rebuild schema + insert script from scratch (45 min limit)

### Retrieval Anchor
> "In FinTech: enforce types with STRICT, enforce rules with CHECK, enforce identity with txn_id. Log every failure explicitly. Gaps in pk are normal; silence in error logs is catastrophic."

### What's Next (Day 3)
Define 6 data quality rules (positive amount, valid currency set, no future dates, status domain, no duplicate txn_ids, user exists) and implement a validation runner.

### Open Questions (for deeper learning)
1. How do distributed systems avoid txn_id collisions? (UUIDs vs timestamp-based?)
2. What's the production-grade approach to refunds? (Separate table vs signed amounts?)
3. How long should idempotency keys be cached? (Redis TTL? Postgres partitioning?)


