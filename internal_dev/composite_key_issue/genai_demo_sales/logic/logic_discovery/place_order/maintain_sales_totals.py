"""
On Placing Orders, maintain sales totals
    1. Orders can be assigned to people who are salesreps
    2. Maintain monthly sales totals and order counts for each sales rep
"""

import datetime
from logic_bank.logic_bank import Rule
from logic_bank.exec_row_logic.logic_row import LogicRow
from database import models


def declare_logic():

    def set_order_date_and_month(row: models.Order, old_row: models.Order, logic_row: LogicRow):
        """Order event: sets order_date and year_month before Row Logic runs. year_month is a
        component of the composite FK to SalesRepTotal (sales_rep_id, year_month), so it must be
        set early, like any other FK column - never derived with Rule.formula."""
        if row.order_date is None:
            row.order_date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        row.year_month = row.order_date[:7]

    Rule.early_row_event(on_class=models.Order, calling=set_order_date_and_month)

    Rule.sum(derive=models.SalesRepTotal.total_amount, as_sum_of=models.Order.amount_total,
        insert_parent=True)

    Rule.count(derive=models.SalesRepTotal.order_count, as_count_of=models.Order,
        insert_parent=True)
