"""
Create a fully functional application and database
 for CBSA Steel Derivative Goods Surtax Order PC Number: 2025-0917
 on 2025-12-11 and annexed Steel Derivative Goods Surtax Order
 under subsection 53(2) and paragraph 79(a) of the
 Customs Tariff program code 25267A to calculate duties and taxes
 including provincial sales tax or HST where applicable when
 hs codes, country of origin, customs value, and province code and ship date >= '2025-12-26'
Transactions are received as a CustomsEntry with multiple
SurtaxLineItems, one per imported product HS code.
"""

from decimal import Decimal
from logic_bank.logic_bank import Rule
from database import models


def declare_logic():
    # surtax_applicable: 1 when ship_date >= effective_date (ISO string comparison is correct)
    Rule.formula(derive=models.CustomsEntry.surtax_applicable,
        as_expression=lambda row: 1 if (row.ship_date and row.effective_date and row.ship_date >= row.effective_date) else 0)

    # base_duty_amount = customs_value * base_duty_rate
    Rule.formula(derive=models.SurtaxLineItem.base_duty_amount,
        as_expression=lambda row: (row.customs_value or Decimal(0)) * (row.base_duty_rate or Decimal(0)))

    # surtax_amount = customs_value * country_surtax_rate (only when surtax_applicable)
    Rule.formula(derive=models.SurtaxLineItem.surtax_amount,
        as_expression=lambda row: (row.customs_value or Decimal(0)) * (row.country_surtax_rate or Decimal(0))
            if row.surtax_applicable else Decimal(0))
