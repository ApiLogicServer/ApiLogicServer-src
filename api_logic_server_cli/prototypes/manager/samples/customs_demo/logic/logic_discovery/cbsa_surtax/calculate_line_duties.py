"""
CBSA Steel Derivative Goods Surtax Order — PC 2025-0917
Program Code: 25267A | Effective: 2025-12-26

Line Item Duty Calculations
============================
Calculates base customs duty, surtax, duty-paid value, and provincial tax
for each SurtaxLineItem.  All amounts are in CAD.

Calculation chain (per line item):
  1. Copy base_duty_rate from HsCodeRate (parent)
  2. Copy surtax_rate from CountryOrigin (parent)
  3. Derive surtax_applicable flag from entry.surtax_active + surtax_rate
  4. base_duty_amount = customs_value * base_duty_rate
  5. surtax_amount    = customs_value * surtax_rate  (if surtax_applicable else 0)
  6. duty_paid_value  = customs_value + base_duty_amount + surtax_amount
  7. provincial_tax_amount = duty_paid_value * customs_entry.province_tax_rate
  8. line_total       = base_duty_amount + surtax_amount + provincial_tax_amount

Constraints:
  - customs_value must be > 0
  - quantity must be > 0
"""
from decimal import Decimal
import database.models as models
from logic_bank.rule_bank.rule_bank import RuleBank
from logic_bank.logic_bank import Rule


def declare_logic():
    """Line-item duty and tax calculation rules — CBSA Steel Surtax PC 2025-0917"""

    # -----------------------------------------------------------------------
    # Copy lookup rates onto the line item (LB tracks FK-parent dependencies)
    # -----------------------------------------------------------------------
    Rule.copy(derive=models.SurtaxLineItem.base_duty_rate, from_parent=models.HsCodeRate.base_duty_rate)
    Rule.copy(derive=models.SurtaxLineItem.surtax_rate, from_parent=models.CountryOrigin.surtax_rate)

    # -----------------------------------------------------------------------
    # Surtax applicable flag:
    #   True when the parent entry is within the surtax window (surtax_active=1)
    #   AND the country of origin is subject to the surtax (surtax_rate > 0)
    # -----------------------------------------------------------------------
    Rule.formula(derive=models.SurtaxLineItem.surtax_applicable,
                 as_expression=lambda row: 1 if row.customs_entry.surtax_active and row.surtax_rate and row.surtax_rate > 0 else 0)

    # -----------------------------------------------------------------------
    # Base customs duty = customs value × MFN/preferential duty rate
    # -----------------------------------------------------------------------
    Rule.formula(derive=models.SurtaxLineItem.base_duty_amount,
                 as_expression=lambda row: (row.customs_value or Decimal(0)) * (row.base_duty_rate or Decimal(0)))

    # -----------------------------------------------------------------------
    # Surtax = customs value × 25% (when applicable)
    # Note: surtax is levied on customs value only, not on base duty
    # -----------------------------------------------------------------------
    Rule.formula(derive=models.SurtaxLineItem.surtax_amount,
                 as_expression=lambda row: (row.customs_value or Decimal(0)) * (row.surtax_rate or Decimal(0)) if row.surtax_applicable else Decimal(0))

    # -----------------------------------------------------------------------
    # Duty-paid value = customs value + base duty + surtax
    # This is the base for GST/HST/PST assessment
    # -----------------------------------------------------------------------
    Rule.formula(derive=models.SurtaxLineItem.duty_paid_value,
                 as_expression=lambda row: (row.customs_value or Decimal(0)) + (row.base_duty_amount or Decimal(0)) + (row.surtax_amount or Decimal(0)))

    # -----------------------------------------------------------------------
    # Provincial tax (GST/HST/PST) = duty-paid value × combined provincial rate
    # Rate is set at the entry level (copied from Province lookup)
    # -----------------------------------------------------------------------
    Rule.formula(derive=models.SurtaxLineItem.provincial_tax_amount,
                 as_expression=lambda row: (row.duty_paid_value or Decimal(0)) * (row.customs_entry.province_tax_rate or Decimal(0)))

    # -----------------------------------------------------------------------
    # Line total = base duty + surtax + provincial tax
    # -----------------------------------------------------------------------
    Rule.formula(derive=models.SurtaxLineItem.line_total,
                 as_expression=lambda row: (row.base_duty_amount or Decimal(0)) + (row.surtax_amount or Decimal(0)) + (row.provincial_tax_amount or Decimal(0)))

    # -----------------------------------------------------------------------
    # Constraints
    # -----------------------------------------------------------------------
    Rule.constraint(validate=models.SurtaxLineItem,
                    as_condition=lambda row: row.customs_value > 0,
                    error_msg="customs_value must be greater than zero (got {row.customs_value})")
    Rule.constraint(validate=models.SurtaxLineItem,
                    as_condition=lambda row: row.quantity > 0,
                    error_msg="quantity must be greater than zero (got {row.quantity})")
