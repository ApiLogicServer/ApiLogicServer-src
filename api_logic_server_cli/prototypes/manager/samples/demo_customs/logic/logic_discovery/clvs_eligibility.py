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


def _clvs_reasons(row, old_row, logic_row):
    reasons = []
    if float(row.local_customs_value_amt or 0) > 3300:
        reasons.append("value exceeds CAD $3,300")
    if row.prohibited_commodity_count and row.prohibited_commodity_count > 0:
        reasons.append(f"{row.prohibited_commodity_count} prohibited commodity line(s)")
    if row.service_type_cd != '04':
        reasons.append("not a CLVS-authorized courier (service_type_cd != 04)")
    if row.dest_loc_cntry_cd != 'CA':
        reasons.append("destination is not Canada")
    return ", ".join(reasons)


def _clvs_eligible(row, old_row, logic_row):
    return 0 if _clvs_reasons(row, old_row, logic_row) else 1


def _clvs_reason_str(row, old_row, logic_row):
    return _clvs_reasons(row, old_row, logic_row)


def declare_logic():
    Rule.count(derive=models.Shipment.prohibited_commodity_count,
               as_count_of=models.ShipmentCommodity,
               where=lambda row: row.is_prohibited == 1)
    Rule.formula(derive=models.Shipment.clvs_eligible, calling=_clvs_eligible)
    Rule.formula(derive=models.Shipment.clvs_reason,   calling=_clvs_reason_str)
