"""
Create a fully functional application and database
 for CBSA Steel Derivative Goods Surtax Order PC Number: 2025-0917
 on 2025-12-11 and annexed Steel Derivative Goods Surtax Order
 under subsection 53(2) and paragraph 79(a) of the
 Customs Tariff program code 25267A to calculate duties and taxes
 including provincial sales tax or HST where applicable when
 hs codes, country of origin, customs value, and province code and ship date >= '2025-12-26'
"""

from logic_bank.logic_bank import Rule
from database import models


def declare_logic():
    Rule.constraint(validate=models.SurtaxLineItem,
        as_condition=lambda row: row.customs_value > 0,
        error_msg="Customs value must be greater than zero (got {row.customs_value})")

    Rule.constraint(validate=models.CustomsEntry,
        as_condition=lambda row: row.ship_date is not None and row.ship_date != '',
        error_msg="Ship date is required on customs entry {row.entry_number}")
