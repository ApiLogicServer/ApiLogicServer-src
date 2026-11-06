"""
Encourage customers to purchase 'green' products with an item discount using a configurable flat percentage.

    Product.green is a flag (yes/no).
    sys_config.green_discount_pct is a global flat percentage, editable in the Admin UI.
    Item.discount_amount is the quantity * unit_price * green_discount_pct when the item's product is green, otherwise 0.
    The Item amount is the quantity * unit_price less the Item discount_amount (rule 4 of Check Credit, extended; see check_credit.py).
"""

from decimal import Decimal
from logic_bank.logic_bank import Rule
from logic_bank.exec_row_logic.logic_row import LogicRow
from database import models


def declare_logic():
    """Business logic rules for the green-product discount."""

    Rule.copy(derive=models.Item.green, from_parent=models.Product.green)

    def _discount_amount(row: models.Item, old_row: models.Item, logic_row: LogicRow):
        """Derive discount_amount: quantity * unit_price * the sys_config green_discount_pct for green items, else 0."""
        green = row.green
        quantity = row.quantity
        unit_price = row.unit_price
        if green != "yes":
            return Decimal(0)
        pct = models.SysConfig.current(logic_row.session).green_discount_pct
        return (quantity * unit_price * pct).quantize(Decimal("0.01"))

    Rule.formula(derive=models.Item.discount_amount, calling=_discount_amount)
