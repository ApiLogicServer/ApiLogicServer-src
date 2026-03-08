"""
CBSA Steel Derivative Goods Surtax Order — PC 2025-0917
Program Code: 25267A | Effective: 2025-12-26

Entry-Level Calculations
=========================
Copies system constants and province tax rate onto the CustomsEntry,
derives the surtax_active flag, and rolls up aggregates from line items.

SysConfig → CustomsEntry (copies):
  - surtax_effective_date  (regulatory date threshold)

Province → CustomsEntry (copies):
  - province_tax_rate     (combined GST/HST/PST rate)

CustomsEntry derived:
  - surtax_active  = 1 when ship_date >= surtax_effective_date

CustomsEntry aggregates (sum of SurtaxLineItem):
  - total_customs_value
  - total_base_duty
  - total_surtax
  - total_provincial_tax
  - grand_total_duties
"""
from decimal import Decimal
import database.models as models
from logic_bank.logic_bank import Rule


def declare_logic():
    """Entry-level aggregation rules — CBSA Steel Surtax PC 2025-0917"""

    # -----------------------------------------------------------------------
    # Copy SysConfig constants to the entry header
    # (FK: customs_entry.sys_config_id → sys_config.id, default = 1)
    # -----------------------------------------------------------------------
    Rule.copy(derive=models.CustomsEntry.surtax_effective_date, from_parent=models.SysConfig.surtax_effective_date)

    # -----------------------------------------------------------------------
    # Copy province tax rate to the entry header
    # (FK: customs_entry.province_id → province.id)
    # -----------------------------------------------------------------------
    Rule.copy(derive=models.CustomsEntry.province_tax_rate, from_parent=models.Province.tax_rate)

    # -----------------------------------------------------------------------
    # surtax_active flag — True when ship_date >= 2025-12-26
    # String ISO date comparison works correctly for YYYY-MM-DD format
    # -----------------------------------------------------------------------
    Rule.formula(derive=models.CustomsEntry.surtax_active,
                 as_expression=lambda row: 1 if row.ship_date and row.surtax_effective_date and row.ship_date >= row.surtax_effective_date else 0)

    # -----------------------------------------------------------------------
    # Roll-up aggregates from line items
    # -----------------------------------------------------------------------
    Rule.sum(derive=models.CustomsEntry.total_customs_value, as_sum_of=models.SurtaxLineItem.customs_value)
    Rule.sum(derive=models.CustomsEntry.total_base_duty, as_sum_of=models.SurtaxLineItem.base_duty_amount)
    Rule.sum(derive=models.CustomsEntry.total_surtax, as_sum_of=models.SurtaxLineItem.surtax_amount)
    Rule.sum(derive=models.CustomsEntry.total_provincial_tax, as_sum_of=models.SurtaxLineItem.provincial_tax_amount)
    Rule.sum(derive=models.CustomsEntry.grand_total_duties, as_sum_of=models.SurtaxLineItem.line_total)
