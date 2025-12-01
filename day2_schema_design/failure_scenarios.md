# Day 2: Failure Scenarios & Fixes

## Scenario 1: Type Coercion Bug
**Symptom:** Changed `amount REAL` to `amount TEXT`; inserts succeeded but `SUM(amount)` returned wrong results
**Root Cause:** SQLite's dynamic typing allows TEXT in REAL columns (default mode)
**Fix:** Added `STRICT` mode to enforce type constraints at write-time
**FinTech Impact:** Prevents $50M revenue calculation errors from silent type mismatches

## Scenario 2: Garbage Timestamp Accepted
**Symptom:** Inserted `created_at = 'not-a-date'`; no error, but `MIN/MAX` queries sorted incorrectly
**Root Cause:** TEXT columns accept any string; SQLite sorts lexicographically
**Fix:** Changed to `INTEGER` timestamps (Unix epoch) + `STRICT` mode
**FinTech Impact:** Ensures audit logs can prove transaction order in disputes

## Scenario 3: Duplicate Inserts (No Idempotency)
**Symptom:** Running script twice created 20 rows instead of 10
**Root Cause:** No unique constraint on transaction identity
**Fix:** Added `txn_id TEXT NOT NULL UNIQUE` + `INSERT OR IGNORE`
**FinTech Impact:** Prevents double-billing when API retries occur

## Scenario 4: Silent Constraint Failures
**Symptom:** Negative amount inserted with `INSERT OR IGNORE`; no error logged
**Root Cause:** `OR IGNORE` swallows all errors (duplicates + validation failures)
**Fix:** Replaced `executemany()` with manual loop + explicit try/catch
**FinTech Impact:** Distinguishes safe duplicates from critical data corruption

## Scenario 5: Autoincrement Gaps
**Symptom:** `MAX(pk) = 30` but `COUNT(*) = 10`; feared data loss
**Root Cause:** Rejected inserts increment sequence before constraint checks
**Fix:** No fix needed — gaps are normal; use `txn_id` for auditing, not `pk`
**FinTech Impact:** Prevents false alarms during incident response
