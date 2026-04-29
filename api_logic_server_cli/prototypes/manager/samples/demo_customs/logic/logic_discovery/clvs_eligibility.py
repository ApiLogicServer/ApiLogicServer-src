"""
CLVS Eligibility Rules.
Scenario: Shipment at or below the LVS threshold is eligible for the CLVS Program.

Conditions (all must be true):
  1. Imported by an authorised CLVS courier (entry_category_type_cd == 'CLV')
  2. Estimated value for duty <= CAD $3,300  (cad_value_amt)
  3. Does not contain prohibited/controlled/regulated goods (dang_goods_cd is null/empty)
  4. Released at a CBSA-designated customs office (portofentry is not null)

Derived flag: clvs_eligible_flg (1=eligible, 0=not eligible)
"""
from logic_bank.logic_bank import Rule
from database import models

_CLVS_THRESHOLD = 3300.0
_CLVS_COURIER_CD = "CLV"


def declare_logic():
    Rule.formula(
        derive=models.Shipment.clvs_eligible_flg,
        as_expression=lambda row: (
            "Y"
            if (
                row.entry_category_type_cd == _CLVS_COURIER_CD
                and (row.cad_value_amt is None or float(row.cad_value_amt) <= _CLVS_THRESHOLD)
                and not row.dang_goods_cd
                and row.portofentry
            )
            else "N"
        ),
    )
