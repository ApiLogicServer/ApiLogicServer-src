"""
Scenario: Shipment at or below the LVS threshold is eligible
  Given a shipment imported by an authorized CLVS courier
  And the shipment has an estimated value for duty not exceeding CAD $3,300
  And the shipment has no prohibited commodity lines (ShipmentCommodity.is_prohibited = 1)
  And the shipment is released at a CBSA-designated customs office
  When the shipment eligibility is evaluated
  Then the shipment shall be eligible for the CLVS Program
  And set the clvs_reason as a comma delimited list of short all reasons why failed (or blank)
"""

from logic_bank.logic_bank import Rule
from database import models


def _reasons(row):
    reasons = []
    if float(row.local_customs_value_amt or 0) > 3300:
        reasons.append("value exceeds CAD $3,300")
    if row.prohibited_commodity_count > 0:
        reasons.append(f"{row.prohibited_commodity_count} prohibited commodity line(s)")
    return reasons


def _clvs_eligible(row, old_row, logic_row):
    return 1 if not _reasons(row) else 0


def _clvs_reason(row, old_row, logic_row):
    return ", ".join(_reasons(row))


def declare_logic():
    # TODO: Review parent-value rules below.
    #   Rule.copy  = snapshot (value frozen at transaction time, no cascade on parent change) ← default
    #   Rule.formula referencing row.parent.attr = live (re-derives if parent changes)
    #   Change Rule.copy → Rule.formula where live propagation is required.
    Rule.count(derive=models.Shipment.prohibited_commodity_count, as_count_of=models.ShipmentCommodity,
               where=lambda row: row.is_prohibited == 1)
    Rule.formula(derive=models.Shipment.clvs_eligible, calling=_clvs_eligible)
    Rule.formula(derive=models.Shipment.clvs_reason, calling=_clvs_reason)
