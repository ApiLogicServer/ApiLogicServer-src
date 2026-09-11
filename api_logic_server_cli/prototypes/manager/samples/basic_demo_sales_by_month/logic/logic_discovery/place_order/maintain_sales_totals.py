"""
On Placing Orders, maintain sales totals
    1. Orders can be assigned to people who are salesreps
    2. Maintain monthly sales totals and order counts for each sales rep
"""

from logic_bank.logic_bank import Rule
from database import models


def declare_logic():
    """Order.CreatedOn / Order.CreatedOnYearMonth (a component of the composite FK to
    SalesRepTotal) are set by the generic cross-cutting stamping handler in
    logic/logic_discovery/system/all_classes_stamping.py - no project-specific event needed."""

    Rule.sum(derive=models.SalesRepTotal.total_amount, as_sum_of=models.Order.amount_total,
        insert_parent=True)

    Rule.count(derive=models.SalesRepTotal.order_count, as_count_of=models.Order,
        insert_parent=True)
