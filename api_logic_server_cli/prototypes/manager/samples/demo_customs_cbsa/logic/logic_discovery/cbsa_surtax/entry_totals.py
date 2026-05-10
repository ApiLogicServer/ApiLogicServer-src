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
    # Aggregate line item values to entry header
    Rule.sum(derive=models.CustomsEntry.total_customs_value, as_sum_of=models.SurtaxLineItem.customs_value)
    Rule.sum(derive=models.CustomsEntry.total_duty_amount,   as_sum_of=models.SurtaxLineItem.base_duty_amount)
    Rule.sum(derive=models.CustomsEntry.total_surtax_amount, as_sum_of=models.SurtaxLineItem.surtax_amount)

    # duty_paid_value = customs value + all duties (base for sales tax)
    Rule.formula(derive=models.CustomsEntry.duty_paid_value,
        as_expression=lambda row: (row.total_customs_value or Decimal(0))
            + (row.total_duty_amount or Decimal(0))
            + (row.total_surtax_amount or Decimal(0)))

    # sales_tax_amount = duty_paid_value * province combined tax rate
    Rule.formula(derive=models.CustomsEntry.sales_tax_amount,
        as_expression=lambda row: (row.duty_paid_value or Decimal(0)) * (row.province_tax_rate or Decimal(0)))

    # total_tax_due = all duties + sales tax
    # Expressed as duty_paid_value - customs_value + sales_tax to avoid sum-column prune ordering issue
    Rule.formula(derive=models.CustomsEntry.total_tax_due,
        as_expression=lambda row: (row.duty_paid_value or Decimal(0))
            - (row.total_customs_value or Decimal(0))
            + (row.sales_tax_amount or Decimal(0)))
