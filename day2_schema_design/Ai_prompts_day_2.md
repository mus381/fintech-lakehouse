AI PROMPTS TO DEEPEN UNDERSTANDING

Use these prompts in ChatGPT/Claude when you want to explore edge cases or stress-test your mental models:

### **Morning Block (Type Safety & Constraints)**

**Prompt 1: Schema Design Trade-offs**
```
I have a payments table with columns: pk, txn_id, user_id, amount, currency, status, created_at.

I'm debating between:
- Option A: Store created_at as INTEGER (Unix timestamp)
- Option B: Store created_at as TEXT (ISO 8601 string like '2025-11-30T08:15:00Z')

Walk me through the trade-offs for:
1. Query performance (sorting, filtering by date range)
2. Timezone handling (if users are global)
3. Audit compliance (human readability vs machine precision)
4. Storage size

Which would you recommend for a FinTech ledger and why?
```

---

**Prompt 2: Constraint Failure Modes**
```
I added this CHECK constraint to prevent negative amounts:

CREATE TABLE transactions (
    amount REAL NOT NULL CHECK(amount > 0),
    ...
) STRICT;

But now I need to support refunds, which are conceptually "negative transactions."

Give me 3 different architectural approaches to handle refunds without allowing negative amounts in the main transactions table. For each approach, explain:
1. Schema changes required
2. Query complexity impact
3. Audit trail implications
4. Which approach Stripe/Square likely uses and why
```

---

**Prompt 3: STRICT Mode Edge Cases**
```
I'm using SQLite STRICT mode to enforce types. Give me 5 edge cases where STRICT mode might cause unexpected failures in production, and how to handle each one. Focus on:
- Currency conversions (float precision)
- Timezone migrations (changing from TEXT to INTEGER timestamps)
- Backwards compatibility (reading old data before STRICT was added)
- Null handling in STRICT vs non-STRICT
- Performance implications of type enforcement
```

---

### **Afternoon Block (Idempotency & Error Handling)**

**Prompt 4: Idempotency Key Design**
```
I'm building a payment API where clients submit transactions with a txn_id for idempotency.

Challenge me with 5 tricky scenarios:
1. Client retries with same txn_id but different amount (is this fraud or a bug?)
2. Two clients accidentally generate the same txn_id (collision)
3. Client wants to "cancel and resubmit" — should I allow same txn_id with status='cancelled' then status='completed'?
4. How long should I remember txn_ids? (30 days? Forever?)
5. What if txn_id is valid but references a deleted user?

For each scenario, tell me:
- What Stripe's API does
- What I should do as a beginner (simplest safe approach)
- What production-grade systems do (with Redis/distributed locks)
```

---

**Prompt 5: Batch Insert Failure Patterns**
```
I'm inserting 1,000 payment transactions in a batch using a loop with try/catch.

Give me 5 realistic failure scenarios and how to handle each:
1. Rows 1-500 succeed, row 501 fails due to negative amount, should I continue or rollback?
2. Database connection drops at row 750 — how do I resume without duplicates?
3. Row 234 has a duplicate txn_id (safe to ignore) but row 456 has a CHECK violation (critical error) — how do I log these differently?
4. The batch takes 10 minutes and times out — should I use smaller batches or optimize the schema?
5. A network partition causes 2 servers to process the same batch — how do I prevent double-inserts?

Focus on: transaction boundaries, retry logic, and error classification.
```

---

**Prompt 6: Autoincrement Gap Forensics**
```
I'm debugging a production issue. My transactions table has:
- MAX(pk) = 15,234
- COUNT(*) = 12,890
- Gap of 2,344 missing primary keys

Give me a step-by-step investigation plan:
1. What queries do I run to find patterns? (Are gaps clustered by date? By user_id?)
2. What log entries do I search for? (Failed inserts? Deletes? Schema changes?)
3. How do I distinguish between "normal constraint rejections" vs "data loss bug"?
4. If I find 2,000 gaps are from CHECK constraint failures, is this a problem or expected?
5. How do I explain this to non-technical stakeholders without causing panic?

Frame this like a real incident response with a timeline.
