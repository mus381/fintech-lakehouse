# Day 3 Lessons Learned

## Key Takeaways
1. **Data quality rules prevent errors early:** Negative amounts, invalid currencies, future dates, unknown statuses, duplicates, missing users, and high-value transactions can all cause revenue loss or compliance issues.
2. **Tombstones enable revenue protection:** Instead of deleting duplicates, we mark them so we can audit, report, and reconcile without losing data.
3. **Deduplication order matters:** Using `ORDER BY created_at` ensures the earliest transaction is kept, preventing inconsistent or incorrect financial records.

## Provocative Questions & Answers
- Why tombstones instead of deletes? Keeps an auditable record for revenue protection and compliance.
- ORDER BY created_at importance? Ensures the first transaction survives; later duplicates are tombstoned.
- False positives vs false negatives? Blocking valid transactions annoys users, but allowing fraud is costlier.
- Handling large transactions? Transactions over $10K are flagged to monitor potential money laundering.
