# Failing Data Quality Tests – Day 3

## positive_amount
- txn_004: amount = -10 → violates positive amount requirement

## valid_currency
- txn_005: currency = BTC → not in allowed currencies (USD, EUR, GBP, JPY)

## no_future_dates
- txn_006: created_at = 9999999999 → timestamp exceeds current system time

## valid_status
- txn_007: status = unknown → not in allowed statuses (pending, posted, failed, completed)

## unique_txn_id
- txn_008 appears twice → duplicate txn_id

## user_exists
- txn_009: user_id = 999 → no matching user in users table

## amount_below_threshold
- txn_010: amount = 25000 → exceeds $10,000 threshold (potential money laundering)

## tombstones (duplicates)
- txn_123 second attempt: 105 → blocked, saved as tombstone
- txn_125 second attempt: 75 → blocked, saved as tombstone
