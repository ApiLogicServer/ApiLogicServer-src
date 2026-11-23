"""
On Moving Orders to a different Customer, Check Credit
    1. Recompute the customers balances as the sum of the unhipped order totals
    2. The Customer's balance must not exceed the credit limit

version: 1.0
created: 2026-11-22T08:55:00
created_by: claude-opus-5-5 (valjhuber@gmail.com)
"""


def declare_logic():
    """No rules of its own: covered by existing rules, which run on every write path.
    Uses: Customer.balance (Check Credit), Customer.credit_limit_check (Check Credit)"""
