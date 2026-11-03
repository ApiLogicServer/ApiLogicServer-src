# Ad-Libs — check_credit

Decisions made beyond the literal prompt text.

## 🟡 FYI — Customer.balance formula: sum of ALL orders, not just unshipped

The prompt says only "Add the order total to the customer's balance" — it does not mention
shipping status at all. This was implemented literally:

```python
Rule.sum(derive=models.Customer.balance, as_sum_of=models.Order.amount_total)
```

No `where=` clause. This differs from the classic basic_demo tutorial pattern (which sums
only unshipped orders, treating shipping as "settled"). If the intent was actually "unpaid
orders count toward the limit, shipped ones don't," add
`where=lambda row: row.date_shipped is None` to this rule.

## 🔴 Review Required — pre-existing `customer.balance` values did not match this rule

`basic_demo.sqlite`'s seed data has non-zero balances for customers with orders, but those
values were computed under the classic unshipped-only formula, not this project's
sum-of-all-orders formula. Two customers (Bob, Diana) had all their orders already shipped,
so their seeded balance was `0` even though `sum(order.amount_total)` for them is `300`.

Per the CE guidance on initializing derived columns for pre-existing rows (LogicBank does
not retroactively recompute a sum on rows it hasn't touched), this was fixed with a one-time
SQL backfill immediately after writing the rule:

```sql
UPDATE customer SET balance = (SELECT COALESCE(SUM(amount_total),0) FROM "order" WHERE customer_id = customer.id);
```

This was necessary before any live testing — otherwise a customer could be silently
under-tracked (looks like they have credit room they don't) or a valid order could be
wrongly rejected against a stale balance. Flagging as Review Required only because it's a
direct data change outside the rule engine, not because of any doubt in the correctness of
the recomputation (it matches the rule's own definition exactly).
